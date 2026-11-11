"""Condições informativas sem dependência do motor de rotas."""
from datetime import datetime
import re
import unicodedata
from typing import Literal
from pydantic import BaseModel, ConfigDict

LINE_CODES = tuple(f"L{n}" for n in (1,2,3,4,5,6,7,8,9,10,11,12,13,15,17))
SERVICE_CODES = ("EXP-AER", "EXP-L10")
DELEGATED = frozenset(("L4","L5","L6","L7","L8","L9","L17"))


def line_code(value: object) -> str | None:
    if isinstance(value, bool):
        return None
    match = re.fullmatch(r"(?:L|LINHA\s*)?0*(\d{1,2})", str(value).strip().upper())
    code = f"L{int(match[1])}" if match else None
    return code if code in LINE_CODES else None


def timestamp(value: object) -> float | None:
    if not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.timestamp() if parsed.tzinfo is not None else None
    except (ValueError, OverflowError):
        return None


def situation(label: str) -> str:
    value = "".join(c for c in unicodedata.normalize("NFKD", label.casefold()) if not unicodedata.combining(c))
    return {"operacao normal":"normal", "velocidade reduzida":"restricted",
            "operacao parcial":"restricted", "operacao especial":"restricted",
            "atividade programada":"restricted", "paralisada":"interrupted",
            "operacao interrompida":"interrupted", "operacao encerrada":"closed"}.get(value, "unknown")


class LineCondition(BaseModel):
    model_config = ConfigDict(extra="forbid")
    line_code: str
    situation: Literal["normal","restricted","interrupted","closed","unknown"] = "unknown"
    label: str = "Informação indisponível"
    description: str = ""
    source: str = ""
    source_url: str = ""
    collected_at: float | None = None
    updated_at: float | None = None
    verified_at: float | None = None
    validity: Literal["current","stale","unavailable"] = "unavailable"
    attribution: str = ""

    def aged(self, now: float, failed: bool = False, *, keep_last: bool = False) -> "LineCondition":
        if self.collected_at is None:
            return self
        verified = self.verified_at if self.verified_at is not None else self.collected_at
        age = max(now-self.collected_at, now-verified)
        if self.collected_at > now+60 or verified > now+60 or (age > 3600 and not keep_last):
            return LineCondition(line_code=self.line_code)
        return self.model_copy(update={"validity":"stale" if failed or age>600 or self.validity == "stale" else "current"})
