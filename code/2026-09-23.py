import os
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def temp_env(**overrides: str | None) -> Iterator[None]:
    """블록 안에서만 환경 변수를 덮어쓰고, 끝나면 원래 값으로 복원한다.

    - 값으로 None을 주면 블록 안에서 해당 키를 제거한다.
    - os.environ은 프로세스 전역 상태이므로 스레드 안전하지 않다.
      병렬 테스트 환경에서는 주의해서 사용한다.
    """
    original = {key: os.environ.get(key) for key in overrides}
    try:
        for key, value in overrides.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value
        yield
    finally:
        for key, value in original.items():
            if value is None:
                os.environ.pop(key, None)  # 원래 없던 키는 삭제
            else:
                os.environ[key] = value


if __name__ == "__main__":
    with temp_env(APP_ENV="test", DB_URL="sqlite:///:memory:"):
        print(os.environ["APP_ENV"])  # test

    print(os.environ.get("APP_ENV"))  # 원래 값 또는 None
