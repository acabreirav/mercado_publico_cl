"""Puntajes de confiabilidad e interés para el comparador de precios.

Dos preguntas distintas sobre cada producto:

  - CONFIABILIDAD: ¿cuánto podemos fiarnos de esta comparación? Sube con el número
    de organismos distintos y de compras. Poca gente comprando = anécdota; muchos
    organismos comprando lo mismo = patrón.

  - INTERÉS (vale investigar): combina la DISPERSIÓN de precio (qué tan desigual se
    paga) con la CONFIABILIDAD (qué tan sólida es la evidencia). Un producto con
    dispersión enorme pero 2 compras es ruido; dispersión alta con 20 organismos es
    una historia. El orden por defecto del dashboard usa este puntaje.

Son heurísticas transparentes, no un modelo estadístico. Documentado a propósito
para que un futuro explorador pueda discutir y ajustar los umbrales.
"""

from __future__ import annotations

import math


def confiabilidad(n_organismos: int, n_items: int) -> tuple[str, float]:
    """Devuelve (tier, score 0-1). Tier: 'alta' | 'media' | 'baja'."""
    # Saturaciones suaves: 8 organismos y 15 compras ya dan señal fuerte.
    s_org = min(1.0, n_organismos / 8)
    s_items = min(1.0, n_items / 15)
    score = round(0.65 * s_org + 0.35 * s_items, 3)  # los organismos pesan más
    if n_organismos >= 8 and n_items >= 12:
        tier = "alta"
    elif n_organismos >= 5 and n_items >= 6:
        tier = "media"
    else:
        tier = "baja"
    return tier, score


def interes(ratio_p75_p25: float, n_organismos: int, n_items: int) -> float:
    """Puntaje 'vale investigar' = dispersión robusta ponderada por amplitud.

    log2(organismos) premia que muchos compradores distintos estén en el patrón,
    sin dejar que un producto con cientos de compras de un solo organismo domine.
    """
    amplitud = math.log2(max(2, n_organismos))  # >=1
    volumen = math.log10(max(10, n_items)) / math.log10(10)  # ~1 en 10 compras, crece suave
    return round((ratio_p75_p25 - 1) * amplitud * volumen, 3)
