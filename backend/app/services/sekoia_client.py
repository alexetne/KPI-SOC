from typing import Any

import httpx


async def fetch_sekoia_alerts(
    base_url: str,
    api_key: str,
    limit: int,
    query_params: dict[str, str],
) -> tuple[str, list[dict[str, Any]]]:
    endpoint = f"{base_url.rstrip('/')}/v1/sic/alerts"
    params = {"limit": str(limit), **query_params}
    headers = {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.get(endpoint, headers=headers, params=params)
        response.raise_for_status()
        payload = response.json()

    return endpoint, extract_alerts(payload)


def extract_alerts(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if not isinstance(payload, dict):
        return []
    for key in ("items", "data", "alerts", "results"):
        value = payload.get(key)
        if isinstance(value, list):
            return [item for item in value if isinstance(item, dict)]
        if isinstance(value, dict):
            nested = extract_alerts(value)
            if nested:
                return nested
    return []
