# Architecture Overview

본 문서는 OCR 기반 모델 서빙 플랫폼의 아키텍처 설계 의도와,  
비동기 처리 구조를 중심으로 한 아키텍처 유형별 구성 및 트레이드오프를 설명합니다.  

## 1. 설계 목표

- API와 비즈니스 로직(OCR 추론)의 명확한 분리  
- GPU 병목을 고려한 안정적인 비동기 처리  
- 장애 예측·대응·복구가 가능한 운영 중심 구조  
- 로컬(kind) ↔ 실서비스(Kubernetes) 환경 간 일관성 유지  
- 트래픽 증가에 따른 점진적 확장 전략 제공  

## 2. 공통 구조 (Logical Architecture)

모든 아키텍처 유형은 동일한 코드 구조(`app/`)를 공유하며, 배포 및 운영 설정에 따라 처리 방식만 달라집니다.  

- **API**: FastAPI 기반 요청 수신 및 Job 생성  
- **Application**: Usecase 기반 처리 흐름 제어  
- **Domain**: Job 상태 머신 및 핵심 규칙 (멱등성 보장)  
- **Worker**: OCR 처리 전담 (GPU 연산)  
- **Messaging**: Kafka (OCR 작업 이벤트/큐)  
- **Storage**: MySQL (Job 상태 및 결과의 Source of Truth)  
- **Redis (Optional)**: 중복 제거, 속도 제한 등 보조 제어  
- **Observability**: Metrics / Logs / Tracing / Health Probe  

## 3. 아키텍처 유형

### A. arch-async-standard (기본 비동기형, EDA)

**목표**  
- GPU 병목을 API로부터 분리  
- 최소한의 운영 복잡도로 안정적인 비동기 처리 제공  

**구성**  
- API  
- Kafka (OCR Job Topic)  
- OCR Worker (GPU concurrency = 1)  
- MySQL  

**특징**  
- API는 Job 생성 후 즉시 응답(비동기)  
- Worker는 Kafka 메시지를 단건 단위 처리  
- DB 상태 전이를 통한 멱등성 보장  
- 오프셋 기반 재시작으로 장애 복구 용이  

**장점**  
- 구조 단순, 구현·운영 부담 낮음  
- 중소 규모 트래픽에 안정적인 처리  

**한계**  
- GPU Util 낮게 유지될 수 있음  
- 대량 트래픽 상황에서 처리량 한계 존재  

**사용 시점**  
- 초기 운영 단계  
- 트래픽 예측이 어려운 서비스 시작 구간  

---

### B. arch-async-batched (GPU 배치 최적화형)

**목표**  
- GPU 자원 최대 활용  
- 대량 트래픽 환경에서도 처리량(Throughput)과 지연 안정성 확보  

**구성**  
- arch-async-standard 구성 기반  
- Worker 내부에 Micro-Batch 처리 로직 추가  

**핵심 설계**  
- Kafka에서 수신한 메시지를 즉시 처리하지 않고,  
- 최대 배치 크기 (예: N건) 또는 최대 대기 시간 (예: 10~30ms) 조건 만족 시까지 임시 큐에 적재  
- 배치 단위로 GPU inference 수행  
- 결과는 Job 단위로 분리하여 저장  

**특징**  
- GPU Util 상승  
- 초당 처리량(TPS) 증가  
- Kafka lag 회복 속도 향상  

**트레이드오프**  
- 소량 트래픽에서는 지연이 소폭 증가할 수 있음  
- 구현 복잡도 상승 (배치 큐, 실패 분리 처리)  

**사용 시점**  
- 대량 OCR 요청 발생  
- GPU가 명확한 병목 지점 환경  
- 처리량 최적화가 중요한 서비스 단계  

## 4. 아키텍처 전환 기준

| 상황                             | 판단 기준(예시 지표)                     | 전환 전략                            |
|---------------------------------|----------------------------------------|-----------------------------------|
| **비동기 처리 필요**                 | API p95 latency 증가, 동기 처리로 인한 타임아웃 | **arch-async-standard 도입**       |
| **GPU Util 낮음, Kafka lag 회복 지연** | GPU Util < 50%, lag 감소 속도 느림          | **arch-async-standard → arch-async-batched** |
| **SLA / 장애 대응 요구 증가**         | 무중단 배포, 장애 허용치 감소                | **arch-async-batched + HA 운영 정책 적용** |

> ※ HA(PDB, Anti-Affinity, 알림 강화)는 운영 정책으로 단계적으로 적용하며,  
> 아키텍처 타입 자체를 변경하지 않습니다.  