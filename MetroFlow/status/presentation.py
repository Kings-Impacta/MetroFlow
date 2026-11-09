"""Informação operacional carregada separadamente do trajeto e de seu registro."""
from datetime import datetime, timedelta, timezone
import reflex as rx
from pydantic import TypeAdapter, ValidationError
from MetroFlow.planning.presentation.state import PlanningState, request_script
from .domain import LineCondition


class LineStatusState(rx.State):
    rows: list[dict[str,str]] = []
    message: str = "As condições operacionais ainda não foram consultadas."
    _request_id: int = 0

    @rx.event
    def refresh(self):
        self._request_id += 1
        self.rows = []
        self.message = "Consultando condições operacionais…"
        return rx.call_script(request_script("/api/planning/line-status",self._request_id),callback=LineStatusState.receive)

    @rx.event
    def receive(self, result: dict):
        if result.get("request_id") != self._request_id:
            return
        self.rows = []
        if result.get("status") != 200:
            self.message = "Status indisponível. Você pode continuar buscando trajetos."
            return
        try:
            conditions = TypeAdapter(list[LineCondition]).validate_python(result.get("data"))
        except ValidationError:
            self.message = "Status indisponível. Você pode continuar buscando trajetos."
            return
        def date(value):
            return datetime.fromtimestamp(value,timezone(timedelta(hours=-3))).strftime("%d/%m %H:%M") if value is not None else "Não informada"
        self.rows = [dict(code=r.line_code,label=r.label,description=r.description,
            source=r.source,source_url=r.source_url,attribution=r.attribution,
            validity={"current":"Atual na consulta","stale":"Desatualizado","unavailable":"Indisponível"}[r.validity],
            collected="Coleta: "+date(r.collected_at),updated="Última mudança: "+date(r.updated_at),
            verified="Verificação da fonte: "+date(r.verified_at)) for r in conditions]
        self.message = "Informação complementar: não altera o trajeto nem representa lotação dos trens. Consulte novamente antes de viajar."


def condition_card(row):
    return rx.card(rx.vstack(
        rx.hstack(rx.text(row["code"],weight="bold"),rx.badge(row["validity"])),
        rx.text(row["label"]),rx.text(row["description"]),
        rx.text(row["collected"],size="1"),rx.text(row["updated"],size="1"),rx.text(row["verified"],size="1"),
        rx.cond(row["source"]!="",rx.link(row["source"],href=row["source_url"],is_external=True)),
        rx.text(row["attribution"],size="1"),align="start"),width="100%")


def status_panel(for_route: bool = False):
    def card(row):
        if for_route:
            return rx.cond(PlanningState.route_line_codes.contains(row["code"]),condition_card(row))
        return condition_card(row)
    return rx.vstack(rx.heading("Condições operacionais das linhas",size="5"),
        rx.text(LineStatusState.message),
        rx.button("Atualizar condições",on_click=LineStatusState.refresh),
        rx.foreach(LineStatusState.rows,card),align="start",width="100%",on_mount=LineStatusState.refresh)
