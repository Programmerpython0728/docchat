"""Umumiy HTTP client — connection pool bilan"""
import httpx

_client: httpx.AsyncClient | None = None


def init_http_client() -> httpx.AsyncClient:
    global _client
    if _client is None:
        _client = httpx.AsyncClient(
            # LLM streaming uchun read timeout cheksiz (token-token sekin keladi).
            # Connect/write/pool — qisqa.
            timeout=httpx.Timeout(connect=10.0, read=None, write=30.0, pool=10.0),
            limits=httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
        )
    return _client


async def close_http_client():
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None


def get_http_client() -> httpx.AsyncClient:
    if _client is None:
        return init_http_client()
    return _client
