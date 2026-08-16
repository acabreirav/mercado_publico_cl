"""Contador de cuota diaria de la API (persistente en disco).

La API v1 permite 10.000 solicitudes por día calendario por ticket (ver
docs/mercado-publico-referencia.md §4.3). Este contador se guarda en disco para
que el tope se respete AUNQUE se corra el descargador varias veces en el día o en
sesiones distintas. El archivo vive junto a la data cruda y se resetea por fecha.
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

from .config import RAW_DIR

LIMITE_DIARIO = 10_000


class CuotaDiaria:
    def __init__(self, limite: int = LIMITE_DIARIO, dir_: Path = RAW_DIR):
        self.limite = limite
        self.hoy = dt.date.today().isoformat()
        self.path = dir_ / f".cuota-{self.hoy}.json"
        self.usadas = 0
        if self.path.exists():
            try:
                self.usadas = int(json.loads(self.path.read_text()).get("usadas", 0))
            except (ValueError, OSError):
                self.usadas = 0

    @property
    def restantes(self) -> int:
        return max(0, self.limite - self.usadas)

    def puede_gastar(self, n: int = 1) -> bool:
        return self.usadas + n <= self.limite

    def gastar(self, n: int = 1) -> None:
        self.usadas += n
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            self.path.write_text(
                json.dumps({"fecha": self.hoy, "usadas": self.usadas}), encoding="utf-8"
            )
        except OSError:
            pass  # el contador en memoria sigue válido para esta corrida
