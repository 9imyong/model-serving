# Architecture Overview

본 문서는 OCR 기반 모델 서빙 플랫폼의 아키텍처 설계 의도와
아키텍처 유형별 구성 및 트레이드오프를 설명한다.

## 1. 설계 목표
- API와 비즈니스 로직의 분리
- 장애 예측·대응·복구가 가능한 구조
- 로컬(kind)과 실서비스(Kubernetes) 환경 간 일관성 유지
- Scale-out 및 고가용성(HA) 대응

---

## 2. 공통 구조 (Logical Architecture)

- API: FastAPI 기반 요청 수신 및 Job 생성
- Application: Usecase 기반 처리 흐름 제어
- Domain: Job 상태 머신 및 핵심 규칙
- Worker: OCR 처리 전담
- Storage: MySQL (Job 상태), Kafka: 비동기 트리거(Topic), Redis (비동기 큐)
- Observability: Metrics / Logs / Health Probe

코드 구조(app/)는 모든 아키텍처에서 동일하게 유지한다.

---

## 3. 아키텍처 유형

### A. arch-simple (단순형)
**구성**
- API
- MySQL
- OCR 처리: API 내부 동기 실행

**특징**
- 구성 단순
- 배포/운영 비용 최소
- 처리량 증가 시 확장 한계 존재

**사용 시점**
- PoC
- 트래픽이 매우 적은 초기 단계

---

### B. arch-async (비동기형, EDA)
**구성**
- API
- Redis (Queue)
- OCR Worker
- MySQL

**특징**
- API는 Job enqueue만 수행
- Worker 수평 확장 가능 (HPA)
- 처리량/지연 시간 안정화

**사용 시점**
- OCR 요청 증가
- API 응답 지연 발생 시

---

### C. arch-ha (고가용/확장형)
**구성**
- arch-async 구성 + HA 요소
- API/Worker replicas ≥ 2
- PDB / Anti-Affinity
- 강화된 관측/알림

**특징**
- 노드/파드 장애에도 서비스 지속
- 무중단 배포 가능

**사용 시점**
- SLA 요구
- 장애 허용치가 낮은 운영 환경

---

## 4. 아키텍처 전환 기준

| 상황 | 전환 |
|----|----|
| OCR 처리 지연, CPU 포화 | simple → async |
| 워커 장애 영향 큼 | async → ha |
| SLA/무중단 요구 | ha 유지 |

---

## 5. 요약
- 코드 구조는 단일 유지
- 배포 설정(Kustomize overlay)으로 아키텍처 분기
- 운영 복잡도 증가에 따라 점진적 확장