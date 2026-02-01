# Runbook – OCR Model Serving Platform

## 목적
본 문서는 운영 중 발생 가능한 장애 상황에 대해
신속한 진단과 대응을 위한 가이드를 제공한다.

---

## Case 1. OCR Queue Backlog 급증

### 증상
- OCR 처리 지연
- Redis queue length 지속 증가
- API 응답은 정상이나 완료 지연

### 확인 지표
- queue_backlog metric
- worker 처리량 감소
- worker CPU 사용률

### 즉시 조치
1. Worker replica 수 증가
kubectl scale deploy worker-ocr --replicas=N

2. HPA 설정 확인

### 원인 분석
- 트래픽 급증
- OCR 처리 시간 증가
- Worker 리소스 부족

### 재발 방지
- backlog 기반 HPA 적용
- OCR timeout/리트라이 정책 개선

---

## Case 2. OCR Worker CrashLoop / OOM

### 증상
- worker pod 재시작 반복
- 처리 실패 증가

### 확인 지표
- pod 상태 (CrashLoopBackOff)
- OOMKilled 이벤트
- 메모리 사용량

### 즉시 조치
1. worker 리소스 limit 상향
2. 문제 워커 로그 확인
3. 필요 시 이전 이미지로 롤백

### 원인 분석
- OCR 모델 메모리 과다 사용
- 잘못된 입력 이미지

### 재발 방지
- 입력 크기 제한
- 메모리 request/limit 재조정

---

## Case 3. DB Connection Saturation

### 증상
- API 5xx 증가
- Job 조회/저장 실패

### 확인 지표
- DB connection count
- API 에러율

### 즉시 조치
1. API replica 증가
2. DB connection pool 제한 확인

### 원인 분석
- 트래픽 증가 대비 pool 설정 미흡

### 재발 방지
- 커넥션 풀 설정 표준화
- 캐시/조회 분리 고려
