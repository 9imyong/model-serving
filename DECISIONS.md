# Architecture & Design Decisions

## 1. 왜 API / Application / Domain을 분리했는가
- API 프레임워크 변경 대비
- 테스트 용이성
- 장애 원인 구분 명확화

---

## 2. 왜 Light DDD인가
- 도메인 복잡도보다 운영 복잡도가 큼
- 과도한 Aggregate/Factory는 생산성 저하
- 상태 머신/규칙 수준만 적용

---

## 3. 왜 Ports/Adapters 구조인가
- DB / Queue / OCR 엔진 교체 대비
- 인프라 의존성 격리
- 로컬/실서비스 환경 차이 최소화

---

## 4. 왜 kind + colima인가
- 로컬에서도 Kubernetes 동일 경험
- 실서비스와 배포 구조 일관성 유지

---

## 5. 왜 아키텍처를 3단계로 나눴는가
- 단순 → 비동기 → 고가용
- 트래픽/운영 요구에 따른 점진적 확장
- 과제 요구사항(2종 이상 아키텍처) 충족
