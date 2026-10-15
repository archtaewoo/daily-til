import os
from dataclasses import dataclass, fields
from typing import Any, get_type_hints

_TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
_FALSE_VALUES = frozenset({"0", "false", "no", "off", ""})


def _cast(raw: str, typ: type, env_key: str) -> Any:
    """환경 변수 문자열을 필드 타입으로 변환한다. 실패 시 어떤 변수인지 명시해 예외를 던진다."""
    value = raw.strip()

    if typ is bool:
        lowered = value.lower()
        if lowered in _TRUE_VALUES:
            return True
        if lowered in _FALSE_VALUES:
            return False
        raise ValueError(f"{env_key}: bool로 해석할 수 없는 값입니다: {raw!r}")

    try:
        return typ(value)
    except (TypeError, ValueError) as e:
        raise ValueError(
            f"{env_key}: {typ.__name__}(으)로 변환할 수 없는 값입니다: {raw!r}"
        ) from e


@dataclass(frozen=True, slots=True)
class Settings:
    db_url: str = "sqlite:///local.db"
    debug: bool = False
    max_workers: int = 4
    timeout: float = 5.0

    @classmethod
    def from_env(cls, prefix: str = "APP_") -> "Settings":
        hints = get_type_hints(cls)
        overrides: dict[str, Any] = {}

        for f in fields(cls):
            env_key = f"{prefix}{f.name.upper()}"
            raw = os.getenv(env_key)
            if raw is not None:
                overrides[f.name] = _cast(raw, hints[f.name], env_key)

        return cls(**overrides)


settings = Settings.from_env()  # 예: APP_DEBUG=true, APP_MAX_WORKERS=8
