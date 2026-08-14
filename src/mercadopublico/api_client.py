"""Cliente HTTP mínimo para la API de Mercado Público.

Centraliza la lógica de red (reintentos con backoff, User-Agent, timeout) para
que los scripts de ingesta no la repitan. El ticket se inyecta como parámetro
pero NUNCA se incluye en la URL "segura" que se usa para logs.
"""

from __future__ import annotations

import sys
import time
from typing import Any

import requests

from .config import API_BASE

USER_AGENT = "mercado-publico-cl-ingesta/0.0 (fase0; inspeccion de shape)"
TIMEOUT_S = 60
MAX_RETRIES = 4
RETRIABLE_STATUS = (429, 500, 502, 503, 504)


def fetch_json(
    endpoint: str, ticket: str, params: dict[str, str] | None = None
) -> tuple[Any, str]:
    """GET a `{API_BASE}/{endpoint}` devolviendo (json, url_sin_ticket).

    Reintenta con backoff exponencial (2, 4, 8, 16 s) ante errores de red,
    5xx o 429. La URL segura (para logs) nunca incluye el ticket.
    """
    params = dict(params or {})
    url = f"{API_BASE}/{endpoint}"
    url_safe = url + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")

    request_params = {**params, "ticket": ticket}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = requests.get(
                url, params=request_params, headers=headers, timeout=TIMEOUT_S
            )
            if resp.status_code in RETRIABLE_STATUS:
                raise requests.HTTPError(f"HTTP {resp.status_code}", response=resp)
            resp.raise_for_status()
            return resp.json(), url_safe
        except (requests.RequestException, ValueError) as err:
            last_err = err
            if attempt == MAX_RETRIES:
                break
            wait = 2**attempt
            print(
                f"  intento {attempt} falló ({err}); reintentando en {wait}s...",
                file=sys.stderr,
            )
            time.sleep(wait)

    raise RuntimeError(
        f"No se pudo obtener la data tras {MAX_RETRIES} intentos: {last_err}"
    )
