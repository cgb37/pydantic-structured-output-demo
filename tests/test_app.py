import pytest
from quart import Quart


@pytest.mark.asyncio
async def test_health_returns_ok():
    from webapp import create_app

    app = create_app()

    test_client = app.test_client()
    resp = await test_client.get("/health")
    assert resp.status_code == 200
    json_data = await resp.get_json()
    assert json_data["status"] == "ok"


@pytest.mark.asyncio
async def test_home_returns_html():
    from webapp import create_app

    app = create_app()

    test_client = app.test_client()
    resp = await test_client.get("/")
    assert resp.status_code == 200
    text = await resp.get_data(as_text=True)
    assert "Pydantic Structured Output Demo" in text
