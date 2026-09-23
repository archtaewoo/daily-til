import os
from collections.abc import Iterator
from contextlib import contextmanager

@contextmanager
def temp_env(**overrides: str) -> Iterator[None]:
    """블록 안에서만 환경 변수를 덮어쓰고, 끝나면 원래 값으로 복원한다."""
    original = {key: os.environ.get(key) for key in overrides}
    os.environ.update(overrides)
    try:
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)  # 원래 없던 키는 삭제
            else:
                os.environ[key] = value

with temp_env(APP_ENV="test", DB_URL="sqlite:///:memory:"):
    print(os.environ["APP_ENV"])  # test

print(os.environ.get("APP_ENV"))  # 원래 값 또는 None
