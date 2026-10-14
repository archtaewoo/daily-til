import os
from dataclasses import dataclass, fields


@dataclass(frozen=True, slots=True)
class Settings:
    db_url: str = "sqlite:///local.db"
    debug: bool = False
    max_workers: int = 4
    timeout: float = 5.0

    @classmethod
    def from_env(cls, prefix: str = "APP_") -> "Settings":
        def cast(raw: str, typ: type):
            if typ is bool:
                return raw.lower() in {"1", "true", "yes", "on"}
            return typ(raw)

        overrides = {
            f.name: cast(raw, f.type)
            for f in fields(cls)
            if (raw := os.getenv(f"{prefix}{f.name.upper()}")) is not None
        }
        return cls(**overrides)


settings = Settings.from_env()  # 예: APP_DEBUG=true, APP_MAX_WORKERS=8
