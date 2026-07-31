"""Unit tests for FastAPI cloud REST API."""

import cv2
import httpx
import numpy as np
import pytest

from threatvision.api.app import app

@pytest.mark.anyio
async def test_health_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"

@pytest.mark.anyio
async def test_statistics_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/statistics")
        assert response.status_code == 200
        data = response.json()
        assert "fps" in data
        assert "system" in data

@pytest.mark.anyio
async def test_history_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        response = await client.get("/history")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

@pytest.mark.anyio
async def test_detect_endpoint():
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        _, encoded = cv2.imencode(".jpg", img)

        response = await client.post(
            "/detect", files={"file": ("test.jpg", encoded.tobytes(), "image/jpeg")}
        )
        assert response.status_code == 200
        data = response.json()
        assert "threat_score" in data
        assert "threat_level" in data
