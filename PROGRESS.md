# 폴더별 프로젝트 진행 현황

- **완료**: 핵심 구현 완료, 로컬/운영 사용 가능  
- **진행중**: 동작하나 TODO·보완 필요  
- **미착수**: 스켈레톤/placeholder만 있음  

---

## 루트

| 항목 | 진행도 | 비고 |
|------|--------|------ |
| pyproject.toml / uv | 완료 | 의존성·스크립트 정리 |
| docker-compose (인프라) | 완료 | MySQL, Kafka, Redis만 기동 |
| Makefile / scripts | 진행중 | db_migrate는 placeholder |

---

## app/

### app/domain
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| Job, JobStatus | 완료 | create/restore, 상태 전이 |
| events (JobCreated, InferenceCompleted) | 완료 | |
| errors (NotFound, InvalidState 등) | 완료 | |
| model.py | 완료 | 도메인 모델 |

### app/ports
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| JobRepository, EventBus, IdempotencyGate | 완료 | Protocol, async 일치 |
| ModelRunner, BlobStore | 완료 | 인터페이스 정의 |

### app/application
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| commands/create_job | 완료 | Job 생성 + 이벤트 발행 |
| commands/get_job_status (queries) | 완료 | |
| commands/process_job | 진행중 | sync repo 호출, Worker와 미연동 |
| commands/write_result | 진행중 | sync repo 호출, Writer 미연동 |
| dto, errors | 완료 | |
| policies (idempotency, processing_mode) | 완료 | |

### app/api
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| v1/jobs (POST, GET) | 완료 | CreateJob / GetJobStatus 연동 |
| v1/health, metrics | 완료 | |
| deps (REPO/EVENT_BUS/IDEM 백엔드 선택) | 완료 | BACKEND=infra, .env 로드 |
| errors, middleware | 완료 | 500 메시지 노출, 로깅 |

### app/adapters
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| inmemory (repo, event_bus, idem_gate) | 완료 | 테스트용 |
| mysql (repository, models, errors) | 완료 | from_env MYSQL_* 지원, save_result TODO |
| kafka (event_bus, consumer, serializer, topics) | 완료 | DLQ 훅 TODO |
| redis (idem_gate) | 완료 | from_env REDIS_HOST/PORT 지원 |
| nfs | 미착수 | .gitkeep |
| runtime (model_runner_stub) | 진행중 | 스텁만 |

### app/worker
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| main (Kafka consume, REPO/EVENT_BUS 옵션) | 완료 | |
| handler (JobCreated 처리) | 진행중 | OCR/Inference placeholder, status 업데이트 TODO |
| tasks | 미착수 | 비어 있음 |

### app/core
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| logging (환경별 aiokafka 레벨) | 완료 | |
| id_generator, metrics, retry, timeouts, tracing | 완료 | |
| config | 미착수 | Pydantic Settings 등 미적용 |

### app/observability
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| slo_sli.md | 완료 | 문서 |
| alerts/, dashboards/ | 미착수 | .gitkeep |

---

## tests/
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| test_api_jobs (create, get, 404, 409) | 완료 | |
| application/test_create_job, test_get_job_status | 완료 | |
| domain/test_job | 완료 | |
| adapters/ | 미착수 | .gitkeep, MySQL/Kafka 등 통합 테스트 없음 |

---

## deploy/
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| k8s/base (api, mysql, kafka, redis, worker-ocr, writer, pdb, monitoring, networkpolicy) | 완료 | 매니페스트 존재 |
| k8s/overlays (arch-async-standard/batched/writer, dev/prod) | 완료 | Kustomize 패치 |

---

## docker/
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| docker-compose.yml | 완료 | 인프라만, api/worker 주석 |
| mysql/init/001_init.sql | 완료 | jobs 테이블, 인덱스 길이 보정 |
| api.Dockerfile, worker-ocr.Dockerfile | 완료 | |

---

## scripts/
| 항목 | 진행도 | 비고 |
|------|--------|------ |
| local_up.sh, db_init.sh | 완료 | 인프라 기동·테이블 생성 |
| db_migrate.sh | 미착수 | placeholder (alembic 미도입) |
| lint.sh, test.sh, smoke_test.sh | 완료 | |

---

## 요약

| 구역 | 완료 | 진행중 | 미착수 |
|------|------|--------|--------|
| app/domain, ports | ● | - | - |
| app/application | 대부분 | process_job, write_result | - |
| app/api, adapters (inmemory,mysql,kafka,redis) | ● | mysql save_result, kafka DLQ | nfs |
| app/worker | main | handler (OCR placeholder) | tasks |
| app/core | logging 등 | - | config |
| tests | API·UseCase·domain | - | adapters 통합 |
| deploy, docker, scripts | 대부분 | - | db_migrate |

**다음 권장 작업**: Worker handler 실제 OCR/추론 연동, config 정리, db_migrate(alembic) 도입, adapters 단위/통합 테스트 보강.
