# Runbook – OCR Model Serving Platform

## 목적
본 문서는 OCR 모델 서빙 플랫폼 운영 중 발생 가능한 주요 장애 시나리오에 대해
신속한 진단, 즉각적인 대응, 재발 방지 기준을 제공한다.

본 플랫폼은 Kafka 기반 비동기 처리 구조를 기본으로 하며,
GPU 병목과 장애를 전제로 한 운영을 목표로 한다.

---

## Case 1. Kafka OCR Job Lag 급증

### 증상
- OCR 처리 완료 지연
- Kafka consumer lag 지속 증가
- API 응답은 정상(202)이나 Job 완료까지 지연

### 확인 지표
- kafka_consumer_lag
- OCR processing latency (p95/p99)
- GPU Util / Memory
- Worker 처리량(TPS)

### 즉시 조치
1. GPU 상태 확인
GPU Util < 50%: 단건 처리 또는 배치 미적용 가능성
GPU OOM 발생 여부 확인

2. Worker 상태 점검
Pod 상태 확인 (CrashLoopBackOff 여부)
최근 배포 또는 설정 변경 여부 확인

3. Consumer 재시작
kubectl rollout restart deploy worker-ocr

### 원인 분석
- 트래픽 급증으로 Kafka backlog 증가
- 단건 처리로 인한 GPU Util 저조
- OCR 처리 시간 증가 (모델 또는 입력 이미지 영향)

### 재발 방지
- arch-async-standard → arch-async-batched 전환 검토
- 마이크로배치 설정(max_batch_size / max_wait_ms) 튜닝
- Kafka lag 기반 알람 임계치 재조정

---

## Case 2. OCR Worker CrashLoop / OOM

### 증상

- Worker Pod 재시작 반복
- OCR 처리 실패율 증가
- Kafka lag 동반 증가

### 확인 지표

- Pod 상태 (CrashLoopBackOff)
- OOMKilled 이벤트
- GPU Memory 사용량
- Worker 로그 (CUDA / inference error)

### 즉시 조치

- Worker 재시작
- kubectl rollout restart deploy worker-ocr
- GPU 메모리 설정 확인
  batch size 과도 여부
  입력 이미지 크기 확인
- 필요 시 이전 이미지로 롤백
  kubectl rollout undo deploy worker-ocr

### 원인 분석

- 배치 크기 과다로 인한 GPU OOM
- 비정상 입력 이미지 (초대형 해상도 등)
- 모델 메모리 릭 또는 설정 오류

### 재발 방지

- 입력 이미지 크기 제한
- batch size 상한 설정
- GPU memory usage 알람 추가
- OOM 발생 Job에 대한 DLQ 또는 격리 처리 (선택)

Case 3. API 5xx 증가 / 응답 지연

### 증상
- API 5xx 오류 증가
- API p95 latency 급증
- Job 생성 실패

### 확인 지표
- API error rate (5xx)
- API p95 latency
- Pod CPU / Memory 사용량
- DB connection 사용량

### 즉시 조치

- API replica 증가
  kubectl scale deploy api --replicas=N

- Readiness 상태 확인
- 비정상 Pod로 트래픽 전달 여부 점검

### 원인 분석

- 트래픽 급증 대비 API 처리 부족
- DB connection pool 고갈
- 외부 의존성(DB / Kafka) 지연 전파

### 재발 방지
- API HPA 기준(p95 latency / CPU) 재조정
- DB connection pool 설정 표준화
- API ↔ Worker 책임 분리 유지 (동기 처리 금지)

Case 4. 배포 중 서비스 영향 발생
### 증상
- 배포 중 API 오류 발생
- 일시적 트래픽 실패

### 확인 지표
- 배포 이벤트 타임라인
- Readiness / Liveness 실패 여부
- PodDisruptionBudget(PDB) 충족 여부

### 즉시 조치

- 배포 중단 또는 롤백
- 잔존 Pod 상태 확인

### 원인 분석
- PDB 미설정
- Replica 수 부족
- Readiness Probe 설정 미흡

### 재발 방지
- PDB / Anti-Affinity 적용
- 최소 replica ≥ 2 유지
- 무중단 배포 전략 유지

## 공통 운영 원칙
- Kafka는 유실 방지 및 오프셋 기반 재시작 수단으로 사용한다.
- 중복 처리는 DB 멱등성으로 최종 보장한다.
- GPU 병목은 scale-out이 아닌 제어 및 배치 전략으로 해결한다.
- 고가용성(HA)은 구조 변경이 아닌 운영 성숙도 강화로 적용한다.