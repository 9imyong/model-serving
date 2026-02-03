"""Jobs API 엔드포인트 테스트."""
from __future__ import annotations


def test_create_job_returns_201(client):
    resp = client.post(
        "/api/v1/jobs",
        json={"model_name": "default", "input_uri": ""},
    )
    assert resp.status_code == 201
    data = resp.json()
    assert "job_id" in data
    assert data["status"] == "PENDING"
    assert "created_at" in data


def test_create_job_with_input_uri(client):
    resp = client.post(
        "/api/v1/jobs",
        json={"model_name": "ocr", "input_uri": "s3://bucket/key"},
    )
    assert resp.status_code == 201
    data = resp.json()
    job_id = data["job_id"]
    assert job_id
    get_resp = client.get(f"/api/v1/jobs/{job_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["job_id"] == job_id
    assert get_data["input_uri"] == "s3://bucket/key"
    assert get_data["status"] == "PENDING"


def test_get_job_not_found_returns_404(client):
    resp = client.get("/api/v1/jobs/nonexistent-id-12345")
    assert resp.status_code == 404


def test_duplicate_input_uri_returns_409(client):
    payload = {"model_name": "m", "input_uri": "same-uri"}
    client.post("/api/v1/jobs", json=payload)
    resp = client.post("/api/v1/jobs", json=payload)
    assert resp.status_code == 409
