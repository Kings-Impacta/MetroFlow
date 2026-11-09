"""Uma reserva persistente impede chamadas por usuário ou processo."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import time
from .domain import LineCondition
from .providers import ProviderFailure


class SharedStatusCache:
    def __init__(self, path, clock=time.time):
        self.path, self.clock = Path(path), clock

    def read(self, key, provider):
        now, cached, leader, failed = self.clock(), [], False, False
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with closing(sqlite3.connect(self.path, timeout=0.1)) as db, db:
                db.execute("CREATE TABLE IF NOT EXISTS status_cache (key TEXT PRIMARY KEY, payload TEXT, next_call REAL, attempts TEXT, failed INTEGER)")
                db.execute("BEGIN IMMEDIATE")
                row = db.execute("SELECT payload,next_call,attempts,failed FROM status_cache WHERE key=?",(key,)).fetchone()
                payload, next_call, attempts, failed = row if row else ("[]",0,"[]",False)
                cached = [LineCondition.model_validate(x) for x in json.loads(payload)]
                recent = [t for t in json.loads(attempts) if t>now-3600]
                if now>=next_call and len(recent)<12:
                    recent.append(now)
                    db.execute("INSERT OR REPLACE INTO status_cache VALUES (?,?,?,?,?)",
                               (key,payload,now+300,json.dumps(recent),int(failed)))
                    leader = True
            if leader:
                backoff, failed = 300, False
                try:
                    cached = provider.fetch(now)
                except ProviderFailure as error:
                    backoff, failed = max(300,error.backoff), True
                with closing(sqlite3.connect(self.path, timeout=0.1)) as db, db:
                    db.execute("UPDATE status_cache SET payload=?,next_call=?,failed=? WHERE key=?",
                        (json.dumps([r.model_dump() for r in cached]),now+backoff,int(failed),key))
        except (OSError, sqlite3.Error, ValueError, TypeError):
            # Sem reserva confiável, não consultar a origem para contornar o limite.
            return []
        return [row.aged(now,bool(failed)) for row in cached]
