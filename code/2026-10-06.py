import re
from typing import Any

EMAIL_RE = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")

def validate_user(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []

    name = data.get("name")
    if not isinstance(name, str) or not name.strip():
        errors.append("name: 비어 있지 않은 문자열이어야 합니다")

    age = data.get("age")
    if not isinstance(age, int) or isinstance(age, bool) or not 0 <= age <= 150:
        errors.append("age: 0~150 사이의 정수여야 합니다")

    email = data.get("email")
    if not isinstance(email, str) or not EMAIL_RE.fullmatch(email):
        errors.append("email: 올바른 이메일 형식이 아닙니다")

    return errors


if errors := validate_user({"name": "Kim", "age": 200, "email": "kim@"}):
    print("\n".join(errors))
