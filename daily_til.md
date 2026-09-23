# Daily TIL Log


---

### 2026-09-20

## 인덱스 vs 트랜잭션 헷갈리는 거 정리

인덱스는 조회 빠르게 해주는 대신 쓰기 느려짐. 무조건 많이 걸면 좋은 줄 알았는데 아니었음.

- 트랜잭션 ACID에서 I(격리성) 부분이 아직 잘 모르겠음. 격리 수준 4단계 다음에 다시 볼 것
- 정규화는 3NF까지는 이해했는데 BCNF부터 머리 아픔

실무에서 정규화 너무 깊이 하면 조인이 많아져서 오히려 성능 떨어질 수도 있다고 함. 이거 트레이드오프 감이 아직 없음.


---

### 2026-09-20

오늘 좀 피곤해서 짧게만.


---

### 2026-09-20

## 단위 테스트와 모킹, 이것만 지키자

- 테스트 하나에는 검증 하나만 둔다. 이름은 `결제_잔액부족시_예외발생`처럼 조건과 결과를 담는다.
- Given-When-Then 구조로 읽히게 작성한다.
- 모킹은 D


---

### 2026-09-23




---

### 2026-09-22

## CI/CD 파이프라인, 빠르고 믿을 수 있게

- 느린 파이프라인은 결국 우회된다. PR 기준 10분 이내를 목표로 삼고, 의존성 캐시와 잡 병렬화부터 챙기자.
- 단계는 lint → unit → integration 순서로 두어 빠르게 실패하게 만든다.
- 빌드는 한 번만 한다. 같은 아티팩트를 스테이징에서 프로덕션으로 승격하고, 환경별 재빌드는 금지한다.


---

### 2026-09-22

## 네트워크 장애는 구간별로 쪼개서 본다

"API가 느려요"의 원인은 대부분 DNS, TCP, TLS, HTTP 중 한 구간에 있다. 추측


---

### 2026-09-21

## 쉘 스크립트는 "실패 시 멈춤"을 기본값으로

운영 사고의 상당수는 에러를 무시하고 계속 돈 스크립트에서 나온다. 첫 줄 템플릿을 고정하자.

```bash
#!/usr/bin/env bash
set -euo pipefail
tmp=$(mktemp -d)
trap 'rm -rf "$


---

### 2026-09-22




---

### 2026-09-20

## 느린 API, 네트워크는 아래 계층부터 의심하라

원인은 코드보다 계층 어딘가에 있는 경우가 많다. 아래 순서로 좁힌다.

1. **DNS**: 해석 지연이나 오래


---

### 2026-09-19

나중에 다시 볼 예정.


---

### 2026-09-21

## 단위 테스트와 모킹, 이것만 지키자

- 테스트 하나에 검증 하나. 이름은 `결제_잔액부족시_예외발생`처럼 행동 중심으로 짓는다.
- Given-When-Then 구조로 쓰면 리뷰


---

### 2026-09-20




---

### 2026-09-21

오늘은 이 정도만.


---

### 2026-09-20

## DB 실무 메모: 인덱스·트랜잭션·정규화

- **인덱스**: 복합 인덱스는 "등치 조건 → 범위 조건 → 정렬" 순서로 설계한다. 추가 전후로 반드시 EXPLAIN을 확인한다.
- **트랜잭션**: 최대한 짧게 유지한다. 외부 API 호출을 트랜잭션 안에 넣으면 락 대기가 쌓여 장애로 번진다.
- **정규화**: 3NF로 시작하고, 병목이 측정됐을 때만 반정규화한다. 중복 데이터를 두면 동기화 책임도 함께 생긴다.

```sql
EXPLAIN SELECT * FROM orders
WHERE user_id = 1 AND created_at > '2024-01-01'
ORDER BY created_at;
```


---

### 2026-09-23

## 컨텍스트 매니저 직접 만들기: 환경 변수 임시 변경

```python
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
```

`__enter__`/`__exit__` 클래스 대신 `@contextmanager`로 설정 → `yield` → 정리 흐름을 한눈에 보이게 했습니다. `try/finally`를 써서 블록 안에서 예외가 나도 환경이 반드시 복원되므로, 테스트끼리 상태가 새는 문제를 막을 수 있습니다.


---

### 2026-09-23

```python
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
```

**변경 사항**

1. **덮어쓰기를 `try` 블록 안으로 이동**
   기존 코드는 `os.environ.update()`가 `try` 밖에 있었습니다. 문자열이 아닌 값이 섞여 들어오면 `TypeError`가 납니다. 이때 앞 키들은 이미 바뀐 상태인데 `finally`가 실행되지 않아 환경이 오염된 채로 남습니다. 이제는 적용 도중 실패해도 항상 원복됩니다.

2. **`None` 값으로 키 제거 지원**
   설정 관련 테스트에서는 "이 환경 변수가 없을 때" 동작을 검증하는 경우가 많습니다. `temp_env(DB_URL=None)`처럼 쓸 수 있게 타입 힌트를 `str | None`으로 넓혔습니다. 기존 호출 방식은 그대로 동작합니다.

3. **스레드 안전성 주의사항을 docstring에 명시**
   `os.environ`은 프로세스 전역 상태입니다. 멀티스레드나 병렬 테스트에서 예기치 않게 간섭할 수 있으므로 사용자가 알 수 있게 적었습니다.

4. **예제 코드를 `if __name__ == "__main__":`으로 감쌈**
   모듈을 import할 때 예제가 실행되어 출력이나 부작용이 생기지 않도록 했습니다.
