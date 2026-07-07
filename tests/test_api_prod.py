import asyncio
import pytest
from httpx import AsyncClient

from garutvon.api_prod.main import create_app


@pytest.mark.asyncio
async def test_health():
    app = create_app()
    async with AsyncClient(app=app, base_url="http://test") as ac:
        r = await ac.get("/api/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"
