"""Cliente HTTP mínimo para la API de Mercado Público.

Centraliza la lógica de red (reintentos con backoff, User-Agent, timeout) para
que los scripts de ingesta no la repitan. El ticket se inyecta como parámetro
pero NUNCA se incluye en la URL "segura" que se usa para logs.

Sobre el rate limit (ver docs/mercado-publico-referencia.md §4.3): además del
límite diario de 10.000 req/ticket, la API aplica un límite de RÁFAGA (por
ventana corta) y devuelve HTTP 429 si se la golpea muy rápido. Por eso el 429
tiene un backoff propio, más largo, y respeta el header `Retry-After` si viene.
"""

from __future__ import annotations

import sys
import time
from typing import Any

import requests

from .config import API_BASE

USER_AGENT = "mercado-publico-cl-ingesta/0.1 (analisis compras publicas)"
TIMEOUT_S = 90
MAX_RETRIES = 6
RETRIABLE_STATUS = (429, 500, 502, 503, 504)
MAX_WAIT_S = 90  # techo para cualquier espera individual


def _retry_after_segundos(resp: requests.Response | None) -> float | None:
    """Lee el header Retry-After (en segundos) si viene; None si no."""
    if resp is None:
        return None
    val = resp.headers.get("Retry-After")
    if not val:
        return None
    try:
        return min(float(val), MAX_WAIT_S)
    except (TypeError, ValueError):
        return None


def _espera(attempt: int, status: int | None, resp: requests.Response | None) -> float:
    """Calcula cuántos segundos esperar antes del próximo intento."""
    if status == 429:
        # 429: respetar Retry-After si viene; si no, backoff más generoso.
        ra = _retry_after_segundos(resp)
        if ra is not None:
            return ra
        return min(MAX_WAIT_S, 3 * (2 ** (attempt - 1)))  # 3, 6, 12, 24, 48, 90
    return min(MAX_WAIT_S, 2**attempt)  # otros: 2, 4, 8, 16, 32, 64


def fetch_url(url: str, stats: dict[str, int] | None = None) -> Any:
    """GET de una URL COMPLETA (para la API OCDS paginada, otra base y sin ticket).

    Mismos reintentos/backoff/429 que fetch_json. Devuelve el JSON parseado.
    """
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        if stats is not None:
            stats["intentos"] = stats.get("intentos", 0) + 1
        status: int | None = None
        resp: requests.Response | None = None
        try:
            resp = requests.get(url, headers=headers, timeout=TIMEOUT_S)
            status = resp.status_code
            if status == 429 and stats is not None:
                stats["n429"] = stats.get("n429", 0) + 1
            if status in RETRIABLE_STATUS:
                raise requests.HTTPError(f"HTTP {status}", response=resp)
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as err:
            last_err = err
            if attempt == MAX_RETRIES:
                break
            wait = _espera(attempt, status, resp)
            if status != 429 or attempt >= 2:
                motivo = f"HTTP {status}" if status else type(err).__name__
                print(f"  reintentando ({motivo}, intento {attempt}) en {wait:.0f}s...", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"No se pudo obtener {url} tras {MAX_RETRIES} intentos: {last_err}")


def fetch_json(
    endpoint: str,
    ticket: str,
    params: dict[str, str] | None = None,
    stats: dict[str, int] | None = None,
) -> tuple[Any, str]:
    """GET a `{API_BASE}/{endpoint}` devolviendo (json, url_sin_ticket).

    Reintenta ante errores de red, 5xx y 429 (este último con espera más larga y
    respetando Retry-After). La URL segura (para logs) nunca incluye el ticket.

    Si se pasa `stats` (dict), acumula: `n429` (nº de respuestas 429 vistas) e
    `intentos` (nº total de intentos). El descargador lo usa para adaptar su ritmo.
    """
    params = dict(params or {})
    url = f"{API_BASE}/{endpoint}"
    url_safe = url + ("?" + "&".join(f"{k}={v}" for k, v in params.items()) if params else "")

    request_params = {**params, "ticket": ticket}
    headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    last_err: Exception | None = None
    for attempt in range(1, MAX_RETRIES + 1):
        if stats is not None:
            stats["intentos"] = stats.get("intentos", 0) + 1
        status: int | None = None
        resp: requests.Response | None = None
        try:
            resp = requests.get(
                url, params=request_params, headers=headers, timeout=TIMEOUT_S
            )
            status = resp.status_code
            if status == 429 and stats is not None:
                stats["n429"] = stats.get("n429", 0) + 1
            if status in RETRIABLE_STATUS:
                raise requests.HTTPError(f"HTTP {status}", response=resp)
            resp.raise_for_status()
            return resp.json(), url_safe
        except (requests.RequestException, ValueError) as err:
            last_err = err
            if attempt == MAX_RETRIES:
                break
            wait = _espera(attempt, status, resp)
            # Ruido mínimo: el 429 es esperable, solo avisamos desde el 2º intento.
            if status != 429 or attempt >= 2:
                motivo = f"HTTP {status}" if status else type(err).__name__
                print(
                    f"  reintentando ({motivo}, intento {attempt}) en {wait:.0f}s...",
                    file=sys.stderr,
                )
            time.sleep(wait)

    raise RuntimeError(
        f"No se pudo obtener la data tras {MAX_RETRIES} intentos: {last_err}"
    )
