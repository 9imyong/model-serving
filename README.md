# Model Serving Platform

OCR 기반 모델 서빙 플랫폼.

# Model Serving Platform (OCR)

> FastAPI 기반 모델 서빙 플랫폼 템플릿
>
> **Usecase 중심 · Light DDD · Ports/Adapters · Kubernetes 대응 구조**

본 프로젝트는 OCR 모델 서빙을 위한 **실서비스 전제 플랫폼 스켈레톤**이다.
API, Worker, Domain 로직을 명확히 분리하고 장애 예측·대응·복구가 가능한 구조를 목표로 설계되었다.

---

## 핵심 목표

* FastAPI와 핵심 비즈니스 로직 분리
* Usecase 중심 설계로 변경 영향 최소화
* 비동기 Worker / Event 기반 확장 가능 구조
* Local ↔ Kubernetes 환경 간 실행 방식 일관성
* 과도한 DDD를 지양한 실무 친화적 아키텍처

본 프로젝트는 내부 **Coding Convention Guide**를 기준으로 설계되었다.

---

## 전체 구조 요약

```
.
├── app/
│   ├── api/            # HTTP API (FastAPI)
│   ├── application/    # Usecase (Command / Query)
│   ├── domain/         # 핵심 규칙 / 상태
│   ├── ports/          # 외부 의존 인터페이스
│   ├── adapters/       # DB / Kafka / Runtime 구현
│   ├── core/           # 공통 인프라 (logging, metrics 등)
│   └── worker/         # 비동기 처리 Worker
│
├── docker/             # Dockerfile / Compose
├── deploy/k8s/         # Kubernetes manifests (base / overlays)
├── scripts/            # 로컬 실행 및 유틸 스크립트
├── observability/      # 대시보드 / 알림 / SLO-SLI
├── tests/              # domain → application → adapter 테스트
└── README.md
```

---

## 실행 방법 (Quick Start)

### 1️⃣ Local 실행 (uv)

```bash
uv sync
uv run uvicorn app.main:app --reload
```

* 기본 health check: `GET /health`
* FastAPI 개발 서버 기반 로컬 테스트용

---

### 2️⃣ Local 실행 (Docker Compose)

```bash
./scripts/local_up.sh
```

* API + Worker + Redis + MySQL 구성
* Kubernetes 없이 전체 플로우 검증 가능

중지:

```bash
docker compose down
```

---

### 3️⃣ Kubernetes 실행

#### kind / dev 환경

```bash
kubectl apply -k deploy/k8s/overlays/arch-async-standard/dev
```

#### 실서비스 환경

```bash
kubectl apply -k deploy/k8s/overlays/arch-async-batched/prod
```

* base + overlay(kustomize) 구조
* 코드 동일, 처리 전략과 운영 정책만 분리

---

## 아키텍처 시나리오

Kubernetes 환경에서 다음 3가지 아키텍처를 제공한다.

| 시나리오                    | 설명                       |
| ----------------------- | ------------------------ |
| **arch-async-standard** | Kafka 기반 단건 처리 비동기 구조    |
| **arch-async-batched**  | GPU 마이크로배치 기반 처리량 최적화 구조 |

자세한 내용은 `ARCHITECTURE.md` 참고.

---

## Coding Convention

본 프로젝트는 다음 원칙을 따른다.

* API는 요청 검증과 응답 변환만 담당
* 비즈니스 로직은 **Application Usecase**에 위치
* Domain은 외부 시스템을 모른다
* DB / Queue / Runtime은 Ports & Adapters로 추상화
* Worker는 Usecase를 호출하는 어댑터 역할

자세한 규칙은 **Coding Convention Guide** 문서를 참고한다.

---

## 테스트 전략

```
tests/
 ├── domain/        # 순수 규칙 테스트
 ├── application/   # usecase 테스트 (우선)
 └── adapters/      # 외부 시스템 연동 테스트
```

* Domain → Application → Adapter 순서로 테스트
* API 테스트는 smoke 수준으로 최소화

---

## Smoke Test

배포 직후 최소 기능 확인을 위해 다음 스크립트를 제공한다.

```bash
./scripts/smoke_test.sh
```

* health check
* 핵심 API 호출
* 외부 의존성 연결 확인

---

## 운영 및 관측성

* 로그: 구조화 로그 + request_id / job_id 포함
* 메트릭: Prometheus 기준
* 대시보드 / 알림 정의: `observability/`

장애 대응 및 복구 시나리오는 `RUNBOOK.md` 참고.

---

## 변경 이력

* v0.1.0: Initial platform skeleton

---

## 대상 독자

* AI 모델 서빙 백엔드 개발자
* 플랫폼 / 인프라 엔지니어
* Kubernetes 기반 서비스 운영 담당자

> 이 프로젝트는 **예제 코드가 아닌, 운영 가능한 구조**를 목표로 한다.

## 로컬 실행

```bash
./scripts/local_up.sh
```

## 문서

- [ARCHITECTURE.md](ARCHITECTURE.md) – 아키텍처 개요
- [RUNBOOK.md](RUNBOOK.md) – 운영 런북
- [CHANGELOG.md](CHANGELOG.md) – 변경 이력
