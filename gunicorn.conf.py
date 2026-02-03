# gunicorn.conf.py
#
# FastAPI 실행용 Gunicorn 설정 (uvicorn worker)
# - API는 CPU/IO 중심이므로 worker 수는 CPU 기준
# - GPU와 무관 (GPU 워커는 worker-ocr에서만 사용)

import multiprocessing
import os

# ---- 기본 ----
bind = os.getenv("GUNICORN_BIND", "0.0.0.0:8000")
worker_class = "uvicorn.workers.UvicornWorker"

# ---- 워커/스레드 ----
# 권장: CPU 코어 기반 (기본: (2*CPU)+1)
# 컨테이너에서 CPU quota를 정확히 반영하려면 K8s limits와 함께 조정
default_workers = multiprocessing.cpu_count() * 2 + 1
workers = int(os.getenv("GUNICORN_WORKERS", str(default_workers)))

# UvicornWorker는 async이므로 threads는 보통 1로 둔다.
threads = int(os.getenv("GUNICORN_THREADS", "1"))

# ---- 타임아웃 ----
# 업로드/외부 I/O가 길어질 수 있으면 timeout을 약간 넉넉히
timeout = int(os.getenv("GUNICORN_TIMEOUT", "60"))
graceful_timeout = int(os.getenv("GUNICORN_GRACEFUL_TIMEOUT", "30"))
keepalive = int(os.getenv("GUNICORN_KEEPALIVE", "5"))

# ---- 로깅 ----
loglevel = os.getenv("GUNICORN_LOG_LEVEL", "info")
accesslog = "-"   # stdout
errorlog = "-"    # stderr
capture_output = True

# 프록시(Nginx/Ingress) 뒤에서 클라이언트 IP/스킴 복원
# (단, 신뢰할 수 있는 프록시만 설정)
forwarded_allow_ips = os.getenv("FORWARDED_ALLOW_IPS", "*")
proxy_protocol = os.getenv("PROXY_PROTOCOL", "false").lower() == "true"

# ---- 기타 ----
preload_app = os.getenv("GUNICORN_PRELOAD", "false").lower() == "true"
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "0"))  # 0이면 비활성
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "0"))
