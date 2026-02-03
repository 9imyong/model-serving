# app/adapters/mysql/errors.py
from __future__ import annotations

from sqlalchemy.exc import IntegrityError

from app.application.errors import ConflictError


def raise_if_duplicate_input_uri(err: IntegrityError) -> None:
    """
    MySQL duplicate key(1062) 또는 메시지 패턴을 기반으로
    input_uri UNIQUE 충돌이면 ConflictError로 변환한다.
    """
    # MySQL / aiomysql / pymysql 계열은 orig.args[0]에 1062가 오는 경우가 많음
    orig = getattr(err, "orig", None)
    code = None
    if orig is not None:
        args = getattr(orig, "args", None)
        if args and isinstance(args, (tuple, list)) and args:
            if isinstance(args[0], int):
                code = args[0]

    msg = str(err).lower()

    # 1062: Duplicate entry (MySQL)
    is_duplicate = (code == 1062) or ("duplicate" in msg and "uq_jobs_input_uri" in msg) or ("duplicate entry" in msg)

    if is_duplicate:
        raise ConflictError("job already exists for this input_uri") from err
