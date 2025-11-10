import time
from typing import Dict, List, Tuple
import httpx
from .models import Message
from .config import settings

_CACHE: Dict[str, Tuple[float, List[Message]]] = {}

def _normalize_upstream_item(item: dict) -> Message:
    return Message(
        id=str(item.get("id") or item.get("_id") or item.get("message_id") or ""),
        member_name=str(
            item.get("member_name")
            or item.get("member")
            or item.get("name")
            or item.get("user_name")
            or ""
        ),
        text=str(
            item.get("text")
            or item.get("message")
            or item.get("body")
            or ""
        ),
        timestamp=item.get("timestamp"),
    )

async def _get_messages_json(url: str):
    # Try the given URL, then toggle trailing slash, then toggle scheme if needed
    candidates = [url]
    if url.endswith("/"):
        candidates.append(url.rstrip("/"))
    else:
        candidates.append(url + "/")

    # scheme toggle
    if url.startswith("https://"):
        base = url.replace("https://", "http://", 1)
    elif url.startswith("http://"):
        base = url.replace("http://", "https://", 1)
    else:
        base = "https://" + url
    if base not in candidates:
        candidates.append(base)
        candidates.append(base.rstrip("/") if base.endswith("/") else base + "/")

    async with httpx.AsyncClient(timeout=20, follow_redirects=True) as client:
        last_exc = None
        for u in candidates:
            try:
                r = await client.get(u, headers={"Accept": "application/json"})
                if r.status_code == 200:
                    return r.json()
            except Exception as e:
                last_exc = e
        if last_exc:
            raise last_exc
        raise RuntimeError("Failed to fetch messages from any candidate URL")

async def fetch_messages() -> List[Message]:
    now = time.time()
    ttl = settings.CACHE_TTL_SECONDS

    if "messages" in _CACHE:
        ts, cached = _CACHE["messages"]
        if now - ts < ttl:
            return cached

    data = await _get_messages_json(settings.MESSAGES_API_URL)
    items = data if isinstance(data, list) else data.get("items") or data.get("data") or []
    msgs = [_normalize_upstream_item(it) for it in items]
    _CACHE["messages"] = (now, msgs)
    return msgs

def invalidate_cache():
    _CACHE.pop("messages", None)
