from __future__ import annotations

import sys
from pathlib import Path

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.main import app
from app.search import SearchHit
import app.main as main_module


class FakeSearcher:
    size = 2

    def search(self, query: str, mode: str = "hybrid", top_k: int = 10, rrf_k: int = 60):
        return [
            SearchHit(
                doc_id="cloud_001",
                title="Cloud doc",
                text=f"query={query} mode={mode} top_k={top_k} rrf_k={rrf_k}",
                score=0.99,
            )
        ]


def test_root_lists_endpoints():
    client = TestClient(app)
    res = client.get("/")
    client.close()

    assert res.status_code == 200
    assert res.json()["endpoints"] == ["/search", "/healthz", "/docs"]


def test_healthz_reports_not_ready(monkeypatch):
    monkeypatch.setattr(main_module, "_searcher", None)
    client = TestClient(app)
    res = client.get("/healthz")
    client.close()

    assert res.status_code == 200
    assert res.json() == {"ready": False, "n_docs": 0}


def test_search_requires_ready_searcher(monkeypatch):
    monkeypatch.setattr(main_module, "_searcher", None)
    client = TestClient(app)
    res = client.get("/search", params={"q": "cloud", "mode": "hybrid"})
    client.close()

    assert res.status_code == 503
    assert res.json()["detail"] == "Searcher not yet ready"


def test_search_validates_query_and_returns_shape(monkeypatch):
    monkeypatch.setattr(main_module, "_searcher", FakeSearcher())
    client = TestClient(app)
    ok = client.get("/search", params={"q": "cloud", "mode": "hybrid", "top_k": 5, "rrf_k": 61})
    bad = client.get("/search", params={"q": "", "mode": "hybrid"})
    client.close()

    assert ok.status_code == 200
    body = ok.json()
    assert body["query"] == "cloud"
    assert body["mode"] == "hybrid"
    assert body["top_k"] == 5
    assert isinstance(body["latency_ms"], float)
    assert body["hits"][0]["doc_id"] == "cloud_001"
    assert "rrf_k=61" in body["hits"][0]["text"]
    assert bad.status_code == 422


def test_search_rejects_invalid_mode(monkeypatch):
    monkeypatch.setattr(main_module, "_searcher", FakeSearcher())
    client = TestClient(app)
    res = client.get("/search", params={"q": "cloud", "mode": "bogus"})
    client.close()

    assert res.status_code == 422
