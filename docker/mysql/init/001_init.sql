-- docker/mysql/init/001_init.sql
-- NOTE: 컨테이너 최초 부팅 시 1회 실행됨

CREATE TABLE IF NOT EXISTS jobs (
    job_id     CHAR(32)      NOT NULL,
    input_uri  VARCHAR(1024) NOT NULL,
    model_name VARCHAR(64)   NOT NULL,
    status     VARCHAR(32)   NOT NULL,
    created_at DATETIME(6)   NOT NULL DEFAULT CURRENT_TIMESTAMP(6),

    PRIMARY KEY (job_id),
    UNIQUE KEY uq_jobs_input_uri (input_uri),
    KEY ix_jobs_status_created_at (status, created_at)
) ENGINE=InnoDB
  DEFAULT CHARSET=utf8mb4
  COLLATE=utf8mb4_unicode_ci;
