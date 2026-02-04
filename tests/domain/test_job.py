"""Domain Job / JobStatus 테스트."""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from app.domain.errors import InvalidJobState
from app.domain.job import Job, JobStatus


class TestJobCreate:
    def test_create_minimal(self):
        job = Job.create("job-1")
        assert job.id == "job-1"
        assert job.status == JobStatus.PENDING
        assert job.input_uri == ""
        assert job.model_name == "default"
        assert job.created_at is not None

    def test_create_with_input_uri_and_model(self):
        job = Job.create("j2", input_uri="s3://bucket/key", model_name="ocr-v1")
        assert job.id == "j2"
        assert job.input_uri == "s3://bucket/key"
        assert job.model_name == "ocr-v1"

    def test_create_with_none_input_uri_normalized_to_empty(self):
        job = Job.create("j3", input_uri=None)
        assert job.input_uri == ""


class TestJobRestore:
    def test_restore_from_string_status(self):
        job = Job.restore("r1", status="RUNNING", input_uri="uri")
        assert job.id == "r1"
        assert job.status == JobStatus.RUNNING
        assert job.input_uri == "uri"

    def test_restore_from_enum_status(self):
        job = Job.restore("r2", status=JobStatus.SUCCEEDED)
        assert job.status == JobStatus.SUCCEEDED

    def test_restore_with_created_at(self):
        now = datetime.now(timezone.utc)
        job = Job.restore("r3", created_at=now)
        assert job.created_at == now


class TestJobStateTransitions:
    def test_pending_to_running(self):
        job = Job.create("t1")
        job.mark_running()
        assert job.status == JobStatus.RUNNING

    def test_running_to_succeeded(self):
        job = Job.create("t2")
        job.mark_running()
        job.mark_succeeded()
        assert job.status == JobStatus.SUCCEEDED

    def test_running_to_inferred(self):
        job = Job.create("t3")
        job.mark_running()
        job.mark_inferred()
        assert job.status == JobStatus.INFERRED

    def test_pending_to_failed(self):
        job = Job.create("t4")
        job.mark_failed()
        assert job.status == JobStatus.FAILED

    def test_running_to_failed(self):
        job = Job.create("t5")
        job.mark_running()
        job.mark_failed()
        assert job.status == JobStatus.FAILED

    def test_cannot_start_from_non_pending(self):
        job = Job.create("t6")
        job.mark_running()
        with pytest.raises(InvalidJobState):
            job.mark_running()

    def test_cannot_succeed_from_pending(self):
        job = Job.create("t7")
        with pytest.raises(InvalidJobState):
            job.mark_succeeded()

    def test_aliases_start_complete_fail(self):
        job = Job.create("t8")
        job.start()
        assert job.status == JobStatus.RUNNING
        job.complete()
        assert job.status == JobStatus.SUCCEEDED
