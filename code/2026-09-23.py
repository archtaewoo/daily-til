import os
from collections.abc import Iterator, Mapping
from contextlib import contextmanager


def _apply(key: str, value: str | None) -> None:
    """value가 None이면 키를 제거하고, 아니면 설정한다."""
    if value is None:
        os.environ.pop(key, None)
    else:
        os.environ[key] = value


@contextmanager
def temp_env(
    overrides: Mapping[str, str | None] | None = None,
    /,
    **kwargs: str | None,
) -> Iterator[None]:
    """블록 안에서만 환경 변수를 덮어쓰고, 끝나면 원래 값으로 복원한다.

    - 값으로 None을 주면 블록 안에서 해당 키를 제거한다.
    - 식별자로 쓸 수 없는 키(예: "MY-VAR")는 첫 번째 인자에 dict로 전달한다.
    - os.environ은 프로세스 전역 상태이므로 스레드 안전하지 않다.
      병렬 테스트 환경에서는 주의해서 사용한다.
    """
    changes: dict[str, str | None] = {**(overrides or {}), **kwargs}

    # 환경을 건드리기 전에 타입을 검증해서 빠르게 실패시킨다.
    for key, value in changes.items():
        if value is not None and not isinstance(value, str):
            raise TypeError(
                f"환경 변수 {key!r}의 값은 str 또는 None이어야 합니다 "
                f"(받은 타입: {type(value).__name__})"
            )

    original = {key: os.environ.get(key) for key in changes}
    try:
        for key, value in changes.items():
            _apply(key, value)
        yield
    finally:
        for key, value in original.items():
            _apply(key, value)  # 원래 없던 키(None)는 삭제된다


if __name__ == "__main__":
    before = os.environ.get("LOG_LEVEL")

    with temp_env(LOG_LEVEL="DEBUG", APP_ENV="test"):
        assert os.environ["LOG_LEVEL"] == "DEBUG"

    with temp_env({"LOG-FORMAT": "json"}, LOG_LEVEL=None):
        assert "LOG_LEVEL" not in os.environ
        assert os.environ["LOG-FORMAT"] == "json"

    assert os.environ.get("LOG_LEVEL") == before
    assert "LOG-FORMAT" not in os.environ
    print("OK: 환경 변수가 원래 상태로 복원되었습니다.")
