"""Configuración y carga del entorno.

Lee variables desde el `.env` de la raíz del repo. Usa `python-dotenv` si está
instalado; si no, cae a un parser mínimo propio para no depender del paquete.
El ticket NUNCA se hardcodea: siempre viene del entorno.
"""

from __future__ import annotations

import os
from pathlib import Path

# Raíz del repo = dos niveles arriba de este archivo (src/mercadopublico/config.py)
REPO_ROOT = Path(__file__).resolve().parents[2]
ENV_PATH = REPO_ROOT / ".env"

# Capa raw: JSON crudo tal cual lo devuelve la API (reproducibilidad, re-parseo).
RAW_DIR = REPO_ROOT / "data" / "raw"

API_BASE = "https://api.mercadopublico.cl/servicios/v1/publico"


def _load_dotenv(path: Path = ENV_PATH) -> None:
    """Carga variables de un archivo .env al os.environ (sin sobrescribir las ya definidas)."""
    try:
        from dotenv import load_dotenv  # type: ignore

        load_dotenv(path, override=False)
        return
    except ModuleNotFoundError:
        pass

    # Fallback: parser mínimo (KEY=VALUE, ignora comentarios y líneas vacías).
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def get_ticket() -> str:
    """Devuelve el ticket de la API desde el entorno, o falla con un mensaje claro."""
    _load_dotenv()
    ticket = os.environ.get("MERCADO_PUBLICO_TICKET", "").strip()
    if not ticket:
        raise RuntimeError(
            "Falta MERCADO_PUBLICO_TICKET. Copia .env.example a .env y completa el "
            "ticket, o expórtalo en el entorno."
        )
    return ticket
