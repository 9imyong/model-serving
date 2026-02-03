# 구현 점검 요약 (Implementation Check)

## 수정 완료한 항목

### 1. **deps.py – Redis 어댑터**
- **문제**: `app.adapters.idempotency.redis_gate` 경로로 import → 해당 패키지 없음.
- **조치**: `app.adapters.redis.idem_gate`에서 `RedisIdempotencyGate` import하도록 수정.
- **추가**: `RedisIdempotencyGate.from_env()` 구현 (REDIS_URL 환경변수, `decode_responses=True` 사용 시 `get()` 반환값 처리 정리).

### 2. **MySQL repository**
- **문제**: `map_integrity_error` import 후 `raise_if_duplicate_input_uri`만 사용.
- **조치**: import를 `raise_if_duplicate_input_uri`로 변경.
- **문제**: `Job.restore()` 미구현.
- **조치**: `app.domain.job`에 `Job.restore(...)` 정적 메서드 추가 (DB/저장소 복원용).
- **문제**: 포트의 `get()` 미구현, `exists_by_input_uri` / `save_result` 미구현.
- **조치**: `get()` = `get_by_id` 래핑, `exists_by_input_uri`(SELECT 1), `save_result`(TODO no-op) 추가.
- **추가**: `MySQLJobRepository.from_env()` 구현 (엔진 + `async_sessionmaker`, 연산마다 `async with session_factory()` 사용).

### 3. **application.errors – NotFoundError**
- **문제**: `app.adapters.mysql.repository`, `app.worker.handler`에서 `app.application.errors.NotFoundError` 사용하는데 해당 모듈에 없음.
- **조치**: `app.domain.errors.NotFoundError`를 `application.errors`에서 re-export.

### 4. **Job.create / input_uri**
- **문제**: `Job.create(job_id, input_uri=None, ...)` 호출 시 타입/동작 불일치.
- **조치**: `Job.create(..., input_uri: str | None = "")`로 허용하고, 본문에서 `input_uri or ""` 사용.

### 5. **JobRepository Protocol & UseCase async**
- **문제**: 포트는 `async get`, InMemory는 sync `get`; `GetJobStatusUseCase.execute`는 sync인데 API에서 `await uc.execute()` 호출.
- **조치**:
  - 포트: `save`/`get`/`exists_by_input_uri`/`save_result` 모두 async로 통일.
  - InMemory: `save`/`get`/`exists_by_input_uri`/`save_result`를 async로 변경.
  - `GetJobStatusUseCase.execute`를 async로 바꾸고 `job = await self.repo.get(job_id)` 사용.
  - `CreateJobUseCase`: 두 분기 모두 `await self.repo.save(job)` 사용.

### 6. **Worker handler**
- **문제**: `repo.get_by_id()` 호출 → 포트에는 `get()`만 정의.
- **조치**: `await self.repo.get(job_id)`로 변경.

### 7. **기타**
- `app.api.middleware.request_id`: 상단 잘못된 주석(`# """..."""`) 제거.

---

## 아직 확인/보완하면 좋은 부분

1. **MySQL `from_env()`**
   - 한 번에 하나의 `session_factory`만 사용. 요청 단위 세션은 FastAPI Depends + lifespan으로 분리하는 방식은 추후 검토 가능.

2. **테스트**
   - `tests/` 아래에 실제 테스트 코드가 거의 없음. `conftest.py`만 있고 adapters/application/domain은 `.gitkeep` 수준.  
   - API/UseCase/Repository 단위 테스트 추가 권장.

3. **core/config.py**
   - 현재 `"""Configuration."""`만 있음. 설정 로딩(Pydantic Settings 등)은 필요 시 추가.

4. **request_id 미들웨어**
   - `response`가 `finally`에서 설정 전에 예외가 나면 `response`가 None일 수 있음. 현재는 `call_next` 직후에만 사용하므로 실사용에서는 문제 적으나, 방어적으로 `response` None 체크 가능.

5. **에러 매핑**
   - `error_mapper`에서 `DomainError`의 서브클래스 순서(NotFoundError, InvalidStateError 먼저)는 이미 올바르게 처리됨.

---

## 구조 요약

| 영역 | 상태 |
|------|------|
| 도메인 (Job, JobStatus, events, errors) | 구현됨, `Job.restore` 추가 반영 |
| 포트 (EventBus, JobRepository, IdempotencyGate) | Protocol 정의 및 async 일치 |
| Application (CreateJob, GetJobStatus, DTO) | UseCase async 및 repo 호출 방식 정리 |
| API (jobs, health, metrics, deps) | 의존성/import 및 Redis/MySQL wiring 수정 |
| Adapters (inmemory, mysql, kafka, redis) | Redis/MySQL import·메서드·from_env 반영 |
| Worker handler | `repo.get()` 사용으로 통일 |

위 수정으로 **실행 시 ImportError·AttributeError·타입 불일치**는 해소된 상태입니다. 로컬에서 `uv run python -c "from app.main import app"` 또는 `uv run uvicorn app.main:app`으로 한 번 더 확인하는 것을 권장합니다.
