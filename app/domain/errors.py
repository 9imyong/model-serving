# app/domain/errors.py

class DomainError(Exception):
    code: str = "DOMAIN_ERROR"
    message: str = "domain error"

    def __init__(self, message: str | None = None):
        super().__init__(message or self.message)


# 범용(추상) 에러
class NotFoundError(DomainError):
    code = "NOT_FOUND"
    message = "resource not found"


class InvalidStateError(DomainError):
    code = "INVALID_STATE"
    message = "invalid resource state"


# 구체(케이스별) 에러
class JobNotFound(NotFoundError):
    code = "JOB_NOT_FOUND"
    message = "job not found"


class InvalidJobState(InvalidStateError):
    code = "INVALID_JOB_STATE"
    message = "invalid job state"
