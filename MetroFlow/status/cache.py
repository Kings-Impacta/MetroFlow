"""Uma reserva persistente impede chamadas por usuário ou processo."""
from contextlib import closing
import json
import logging
from pathlib import Path
import sqlite3
import time
from .domain import LineCondition
from .providers import ProviderFailure

logger = logging.getLogger(__name__)


class SharedStatusCache:
    def __init__(self, path, clock=time.time):
        self.path, self.clock = Path(path), clock

    def read(self, key, provider):
        now, cached, leader, failed = self.clock(), [], False, False
        fresh_until = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(self.path, timeout=0.1)) as db, db:
                db.execute("CREATE TABLE IF NOT EXISTS status_cache (key TEXT PRIMARY KEY, payload TEXT, next_call REAL, attempts TEXT, failed INTEGER)")
                db.execute("CREATE TABLE IF NOT EXISTS status_cache_policy (key TEXT PRIMARY KEY, fresh_until REAL)")
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT payload,next_call,attempts,failed FROM status_cache WHERE key=?",(key,)).fetchone()
                payload, next_call, attempts, failed = row if row else ("[]",0,"[]",False)
                cached = [LineCondition.model_validate(x) for x in json.loads(payload)]
                policy = db.execute("SELECT fresh_until FROM status_cache_policy WHERE key=?", (key,)).fetchone()
                fresh_until = policy[0] if policy else None
                recent = [t for t in json.loads(attempts) if t>now-3600]
                if now>=next_call and len(recent)<12:
                    recent.append(now)
                    db.execute("INSERT OR REPLACE INTO status_cache VALUES (?,?,?,?,?)",
                               (key,payload,now+300,json.dumps(recent),int(failed)))
                    leader = True
            if leader:
                backoff, failed = 300, False
                stored = cached
                stored_fresh_until = fresh_until
                try:
                    fetched = provider.fetch(now)
                    if not fetched or any(not isinstance(r,LineCondition) or r.validity != "current"
                            or r.aged(now).validity == "unavailable" for r in fetched):
                        raise ProviderFailure()
                    if len({r.line_code for r in fetched}) != len(fetched):
                        raise ProviderFailure()
                    by_code = {r.line_code:r.model_copy(update={"validity":"stale"}) for r in cached}
                    by_code.update({r.line_code:r for r in fetched})
                    cached = list(by_code.values())
                    backoff = max(300, getattr(fetched, "refresh_after", 300))
                    fresh_until = now + getattr(fetched, "fresh_for", 600)
                    if getattr(fetched,"cacheable",True):
                        stored, stored_fresh_until = cached, fresh_until
                    else:
                        stored = [r.model_copy(update={"validity":"stale"}) for r in stored]
                except ProviderFailure as error:
                    backoff, failed = max(300,error.backoff), True
                    source = key if key in {"metro-board-v1","motiva-board-v1","cptm-v1"} else "fonte configurada"
                    logger.warning("Falha ao atualizar status de %s (%s); último retorno preservado.",source,error.kind)
                except (ValueError,TypeError,AttributeError):
                    failed = True
                with closing(sqlite3.connect(self.path, timeout=0.1)) as db, db:
                    db.execute("UPDATE status_cache SET payload=?,next_call=?,failed=? WHERE key=?",
                        (json.dumps([r.model_dump() for r in stored]),now+backoff,int(failed),key))
                    if stored_fresh_until is not None:
                        db.execute("INSERT OR REPLACE INTO status_cache_policy VALUES (?,?)",(key,stored_fresh_until))
        except (OSError, sqlite3.Error, ValueError, TypeError):
            # Sem reserva confiável, não consultar a origem para contornar o limite.
            failed = True
        return [row.aged(now,bool(failed) or (fresh_until is not None and now>=fresh_until),keep_last=True) for row in cached]
