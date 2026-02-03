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
- REDIS
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

### C. arch-async-writer (Downstream 병목 분리형)

**목표**  
- GPU 추론 이후 단계(DB / IO / 내부 네트워크) 병목 격리  
- GPU 처리 파이프라인 보호 및 불필요한 GPU 증설 방지  

**설계 배경**  
GPU 추론 자체는 병목이 아니지만,  
추론 결과 저장(DB), 파일 IO, 내부 서비스 호출, 네트워크 지연 등  
다운스트림 처리 단계에서 지연이 발생하는 경우가 있다.

이 경우 GPU Util은 낮거나 안정적임에도 불구하고,
- Kafka lag 지속 증가  
- End-to-End latency 증가  
- 처리 완료 지연  
이 동시에 발생한다.

**arch-async-writer는 이러한 다운스트림 병목을 GPU 처리 경로로부터 분리하는 것을 목표로 한다.**

---

**구성**  
- API  
- Kafka (OCR Job Topic)  
- OCR Worker (GPU Inference 전담)  
- Kafka (Result Topic)  
- Writer Worker (DB / IO / Network 처리 전담)  
- MySQL  

---

**핵심 설계**  
- GPU Worker는 **추론만 수행**하고 결과를 `result-topic`에 이벤트로 발행  
- Writer Worker는 결과 이벤트를 소비하여  
  - DB 저장  
  - 파일 업로드  
  - 내부 RPC 호출  
  을 전담 처리  
- GPU ↔ Writer 사이에 Kafka를 완충 계층으로 두어  
  다운스트림 지연이 GPU 처리 흐름으로 전파되지 않도록 설계  

---

**특징**  
- GPU Util 안정화 (GPU 병목 오인 방지)  
- Writer Worker 독립적 scale-out 가능  
- DB / Network 장애 시 GPU 추론 지속 가능  
- 재시도 / DLQ 기반 장애 복구 용이  

---

**트레이드오프**  
- 파이프라인 단계 증가로 운영 복잡도 상승  
- 데이터 정합성(멱등성, 중복 처리) 설계 필요  
- 토픽 및 컨슈머 관리 비용 증가  

---

**사용 시점**  
- GPU Util < 60% 상태에서 Kafka lag 지속 증가  
- Trace 상 DB / Network span 비중이 가장 큰 경우  
- GPU 증설이나 배치 처리로도 지연 해소가 되지 않는 경우  
- 다운스트림 안정성이 SLA에 중요한 서비스 단계  

---

## 4. 아키텍처 전환 기준

아키텍처는 고정된 형태가 아니라,  
**관측 지표 기반으로 단계적으로 전환 가능하도록 설계**한다.

| 상황 | 판단 기준(예시 지표) | 전환 전략 |
|-----|------------------|---------|
| **비동기 처리 필요** | API p95 latency 증가, 동기 처리 타임아웃 | **arch-async-standard 도입** |
| **GPU 병목 발생** | GPU Util ≥ 80%, Kafka lag 지속 증가 | **arch-async-standard → arch-async-batched** |
| **GPU Util 낮음 + Lag 증가** | GPU Util < 60%, DB/Network latency p95 증가 | **arch-async-batched → arch-async-writer** |
| **가용성 요구 증가** | 무중단 배포 필요, 장애 허용치 감소 | **PDB / Anti-Affinity / HPA 적용** |

> ※ HA(PDB, Anti-Affinity, HPA, 알림 강화)는  
> 아키텍처 유형 변경이 아닌 **운영 정책으로 단계적 적용**한다.

---

## 5. 설계 요약

본 플랫폼은 입력 폭주, GPU 처리 병목, 다운스트림 병목을 구분하여  
각 상황에 적합한 아키텍처를 선택적으로 적용한다.

- **arch-async-standard**: 입력 변동성 흡수 및 기본 안정성 확보  
- **arch-async-batched**: GPU 처리량 극대화  
- **arch-async-writer**: 다운스트림 병목 격리 및 운영 안정성 강화  

이를 통해 단일 해법이 아닌,  
**병목 위치 기반의 점진적 확장과 장애 대응이 가능한 구조**를 제공한다.
