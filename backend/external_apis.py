import httpx

async def get_mxn_to_usd_rate() -> float:
    """Consulta en tiempo real el tipo de cambio MXN -> USD usando Frankfurter API."""
    url = "https://api.frankfurter.app/latest?from=USD&to=MXN"
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            return float(data["rates"]["MXN"])
    except Exception:
        # Valor de respaldo en caso de caída de red externa
        return 19.85