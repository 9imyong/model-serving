## OCR Model Serving Platform – Coding Conventions

## 1. 문서 목적

본 문서는 OCR 기반 모델 서빙 플랫폼의 코딩 규칙 및 설계 기준을 정의합니다.  
본 컨벤션은 다음을 목표로 합니다.

- 비즈니스 로직과 프레임워크(API)의 분리
- 장애 대응·확장·운영을 고려한 구조
- 로컬(kind)과 실서비스(Kubernetes) 환경 간 일관성
- 과도한 DDD를 지양한 Light DDD 적용

---

## 2. 레이어 구조와 책임

- api          : HTTP 인터페이스 (FastAPI)
- application  : 유스케이스 (행동/흐름)
- domain       : 핵심 규칙 / 상태 머신
- ports        : 외부 의존 인터페이스
- adapters     : 외부 시스템 구현
- core         : 공통 관심사

### 2.1 의존성 규칙 (중요)

- api → application → domain
- application → ports
- adapters → ports

domain은 외부 시스템과 프레임워크를 알지 못합니다.

금지:
- domain에서 DB, Redis, HTTP, FastAPI import
- application에서 ORM 직접 사용

---

## 3. 타입 모델 컨벤션 (Pydantic vs Dataclass)

### 3.1 Pydantic 사용 기준 (경계)

사용 위치:
- API 요청/응답 모델
- 설정 모델(core/config.py)
- 외부 입력 파싱(adapters)

예시:

    class CreateJobRequest(BaseModel):
        image_url: str

원칙:
- 검증/직렬화는 경계에서만 수행
- 내부 로직으로 Pydantic 전달 금지

---

### 3.2 Dataclass 사용 기준 (내부)

사용 위치:
- Domain 엔티티
- Application DTO

예시:

    @dataclass(frozen=True, slots=True)
    class CreateJobDTO:
        image_url: str

원칙:
- 내부 데이터 모델은 dataclass 기본
- 불변 DTO는 frozen=True 권장

---

## 4. Domain 컨벤션 (Light DDD)

### 4.1 Domain의 역할
- 상태 전이
- 불변 조건
- 핵심 규칙

예시:

    @dataclass(slots=True)
    class Job:
        id: str
        status: JobStatus

        def start(self) -> None:
            if self.status != JobStatus.PENDING:
                raise InvalidStateError()
            self.status = JobStatus.RUNNING

### 4.2 금지 사항
- ORM 모델 사용
- DB / Redis / Kafka 접근
- HTTP 개념

Domain은 “규칙”만 가진다.

---

## 5. Application (Usecase) 컨벤션

### 5.1 책임
- 시스템의 행동 단위
- 여러 Domain / Port 조합
- 트랜잭션 흐름 제어

### 5.2 Command / Query 분리
- commands/ : 상태 변경
- queries/  : 조회

예시:

    class CreateJobUseCase:
        def __init__(self, repo: JobRepository, bus: EventBus):
            self.repo = repo
            self.bus = bus

        def execute(self, dto: CreateJobDTO) -> Job:
            job = Job.create(dto)
            self.repo.save(job)
            self.bus.publish(JobCreated(job.id))
            return job

규칙:
- usecase는 HTTP / ORM을 모른다
- 외부 의존성은 생성자로 주입

---

## 6. API 컨벤션

### 6.1 API의 역할
- 요청 검증
- DTO 변환
- usecase 호출
- 응답 변환

예시:

    @router.post("/jobs")
    def create_job(req: CreateJobRequest):
        job = create_job_uc.execute(req.to_dto())
        return JobResponse.from_domain(job)

규칙:
- 비즈니스 로직 금지
- Domain 객체 직접 반환 금지

---

## 7. Ports / Adapters 컨벤션

### 7.1 Port 정의 기준

다음은 반드시 Port로 추상화한다.
- Repository (DB)
- Queue / Event Bus
- OCR Engine
- Blob Storage (NFS / S3)

예시:

    class JobRepository(Protocol):
        def save(self, job: Job) -> None: ...
        def get(self, job_id: str) -> Job: ...

### 7.2 Adapter 규칙
- 외부 라이브러리는 adapter에만 위치
- adapter → domain 직접 참조 금지

---

## 8. Worker (비동기) 컨벤션

### 8.1 Worker의 정체성

Worker는 Usecase를 호출하는 어댑터 역할을 수행한다.

- 메시지 수신
- DTO 변환
- usecase 호출
- 결과 저장

비즈니스 규칙 금지

### 8.2 Idempotency
- job_id 기준 중복 처리 방지
- 재시도 / 중복 소비 고려

---

## 9. 예외 처리 컨벤션

### 9.1 계층별 예외
- domain : DomainError 계열
- core   : ExternalServiceError, TimeoutError
- api    : HTTP 예외로 매핑

### 9.2 금지

    except Exception:
        pass

---

## 10. 로깅 & 메트릭 컨벤션

### 10.1 로깅
- print() 금지
- 구조화 로그 사용
- 필수 필드
  - request_id
  - job_id

### 10.2 메트릭
- API   : 요청 수, 에러율, p95 지연
- Worker: 처리량, 실패율, 처리 시간
- Queue : backlog

---

## 11. 네이밍 규칙

파일        : snake_case  
클래스      : PascalCase  
Usecase     : CreateJobUseCase  
Port        : JobRepository  
Adapter     : MySQLJobRepository  

---

## 12. 테스트 컨벤션

    tests/
     ├── domain/
     ├── application/
     └── adapters/

- Domain → Application → Adapter 순서로 테스트
- API 테스트는 스모크 수준으로 유지

---

## 13. 로컬 / 실서비스 공통 원칙
- 코드는 하나
- 배포 설정만 분리
- dev  : kind + colima
- prod : Kubernetes

---

## 14. 최종 원칙 요약

본 프로젝트는 Usecase 중심 + Ports/Adapters + Light DDD 구조를 기반으로  
프레임워크와 비즈니스 로직을 분리하고,  
운영·확장·장애 대응에 최적화된 코딩 컨벤션을 적용한다.
