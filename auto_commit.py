import ast
import os
import random
import datetime
import sys
from anthropic import Anthropic

TOPICS = [
    "Python 심화 문법 (데코레이터, 제너레이터, 컨텍스트 매니저)",
    "Git/GitHub 실무 팁 (rebase, cherry-pick, hooks)",
    "Docker & 컨테이너 기초",
    "자료구조와 알고리즘 (해시맵, 트리, 그래프)",
    "운영체제 기본기 (프로세스, 스레드, 메모리 관리)",
    "네트워크 기초 (TCP/IP, HTTP, DNS)",
    "데이터베이스 (인덱스, 트랜잭션, 정규화)",
    "리눅스/쉘 스크립팅",
    "디자인 패턴",
    "CI/CD 파이프라인",
    "테스트 코드 작성법 (단위 테스트, 모킹)",
    "클린 코드 원칙",
]

CODE_TOPICS = [
    "실용적인 데코레이터 예제",
    "컨텍스트 매니저 직접 만들기",
    "간단한 재시도(retry) 유틸",
    "파일 처리 헬퍼 함수",
    "간단한 캐시 데코레이터",
    "로깅 유틸리티",
    "설정값 관리 클래스",
    "간단한 데이터 검증 함수",
]

LIGHT_NOTES = [
    "오늘 좀 피곤해서 짧게만.",
    "복습만 대충 함.",
    "나중에 다시 볼 예정.",
    "간단한 정리만.",
    "오늘은 이 정도만.",
    "다음에 더 파봐야지.",
    "메모만 남김.",
]

MODEL = "claude-opus-5-5"
MAX_ATTEMPTS = 2  # 잘림/코드 오류 시 생성 재시도 횟수


class GenerationError(Exception):
    """응답이 잘렸거나 코드가 유효하지 않을 때 발생."""


def get_client():
    # SDK는 429/5xx/연결 오류를 기본 2회 재시도한다. 여유 있게 5회로 상향.
    return Anthropic(max_retries=5)


def extract_text(message) -> str:
    """응답의 텍스트 블록을 합친다. 토큰 한도로 잘렸으면 실패 처리."""
    print(f"[DEBUG] stop_reason={message.stop_reason}, usage={message.usage}")
    if message.stop_reason == "max_tokens":
        raise GenerationError("max_tokens에 도달해 응답이 잘림")
    text_parts = [block.text for block in message.content if hasattr(block, "text")]
    return "\n".join(text_parts).strip()


def extract_code(content: str) -> str:
    """첫 번째 코드 블록의 내용을 반환. 코드 블록이 없으면 빈 문자열."""
    for fence in ("```python", "```py", "```"):
        if fence in content:
            return content.split(fence, 1)[1].split("```", 1)[0].strip()
    return ""


def validate_python(content: str) -> str:
    """응답에서 코드를 꺼내 문법을 검사하고, 유효한 코드를 반환."""
    code = extract_code(content)
    if not code:
        raise GenerationError("응답에 코드 블록이 없음")
    try:
        ast.parse(code)
    except SyntaxError as exc:
        raise GenerationError(f"코드 문법 오류: {exc}") from exc
    return code


def run_with_attempts(generate, attempts: int = MAX_ATTEMPTS):
    """generate()가 GenerationError를 내면 재시도. 끝까지 실패하면 None."""
    for attempt in range(1, attempts + 1):
        try:
            return generate()
        except GenerationError as exc:
            print(f"[WARN] 생성 실패({attempt}/{attempts}): {exc}", file=sys.stderr)
    return None


def generate_memo(topic: str) -> str:
    client = get_client()
    system_prompt = (
        "너는 5년차 이상 시니어 개발자야. "
        "실무에서 바로 써먹을 수 있는 짧은 메모를 작성해. "
        "분량은 220~350자 정도. "
        "제목은 ## 로 시작. "
        "필요할 때만 짧은 코드 스니펫을 포함해. "
        "인사말은 넣지 마."
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=2000,
        system=system_prompt,
        messages=[{"role": "user", "content": f"주제: {topic}\n시니어 관점의 짧은 실무 메모를 작성해줘."}],
    )
    return extract_text(message)


def generate_code_main(topic: str) -> str:
    client = get_client()
    system_prompt = (
        "너는 시니어 개발자야. "
        "코드를 메인으로 작성하고, 설명은 짧게 보조로 붙여. "
        "코드는 현대적이고 깔끔한 스타일로 10~25줄 이내로 작성해. "
        "제목은 ## 로 시작. "
        "코드 블록을 사용하고, 왜 이렇게 짰는지 한두 문장 정도만 설명해. "
        "인사말은 넣지 마."
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=3000,
        system=system_prompt,
        messages=[{"role": "user", "content": f"주제: {topic}\n코드를 메인으로 한 짧은 실무 예제를 작성해줘."}],
    )
    content = extract_text(message)
    validate_python(content)  # 저장 전에 미리 검증
    return content


def generate_code_edit(existing_code: str, topic: str) -> str:
    client = get_client()
    system_prompt = (
        "너는 시니어 개발자야. "
        "주어진 코드를 더 나은 방향으로 살짝 수정해. "
        "큰 변경은 하지 말고, 가독성·안정성·실무 관점에서 개선해. "
        "수정된 전체 코드를 보여주고, 무엇을 왜 바꿨는지 짧게 설명해. "
        "인사말은 넣지 마."
    )
    message = client.messages.create(
        model=MODEL,
        max_tokens=3500,
        system=system_prompt,
        messages=[{
            "role": "user",
            "content": f"주제: {topic}\n\n기존 코드:\n```python\n{existing_code}\n```\n이 코드를 시니어 관점에서 개선해줘."
        }],
    )
    content = extract_text(message)
    validate_python(content)
    return content


def get_today() -> datetime.date:
    return datetime.date.today()


def export_date_to_workflow(target_date: datetime.date):
    """워크플로의 커밋 스텝이 같은 날짜를 쓰도록 GITHUB_ENV에 기록한다."""
    env_file = os.environ.get("GITHUB_ENV")
    if not env_file:
        return
    with open(env_file, "a", encoding="utf-8") as f:
        f.write(f"TIL_DATE={target_date.strftime('%Y-%m-%d')}\n")


def append_to_daily(content: str, target_date: datetime.date):
    date_str = target_date.strftime("%Y-%m-%d")
    entry = f"\n\n---\n\n### {date_str}\n\n{content}\n"
    filepath = "daily_til.md"
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("# Daily TIL Log\n")
        f.write(entry)
    print("[OK] daily_til.md 업데이트")


def next_code_path(target_date: datetime.date) -> str:
    """같은 날짜 파일이 있으면 -2, -3 ... 접미사를 붙여 덮어쓰기를 막는다."""
    date_str = target_date.strftime("%Y-%m-%d")
    path = f"code/{date_str}.py"
    n = 2
    while os.path.exists(path):
        path = f"code/{date_str}-{n}.py"
        n += 1
    return path


def save_code_file(content: str, target_date: datetime.date) -> str:
    os.makedirs("code", exist_ok=True)
    filename = next_code_path(target_date)
    code = validate_python(content)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code + "\n")
    print(f"[OK] 코드 파일 생성: {filename}")
    return filename


def get_recent_code_files(limit: int = 5) -> list:
    """파일명이 날짜 형식이므로 내림차순 정렬하면 최근 파일이 앞에 온다."""
    if not os.path.exists("code"):
        return []
    files = sorted((f for f in os.listdir("code") if f.endswith(".py")), reverse=True)
    return files[:limit]


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY 없음", file=sys.stderr)
        sys.exit(1)

    target_date = get_today()
    export_date_to_workflow(target_date)
    print(f"[INFO] 날짜: {target_date}")

    mode_roll = random.random()

    # 1. 가벼운 날 (20%)
    if mode_roll < 0.20:
        append_to_daily(random.choice(LIGHT_NOTES), target_date)
        print("[INFO] 모드: 가벼운 날")
        return

    # 2. 코드 수정 날 (10%) - 기존 코드가 있을 때만, 최근 파일 중에서 선택
    recent_files = get_recent_code_files()
    if mode_roll < 0.30 and recent_files:
        chosen = random.choice(recent_files)
        with open(f"code/{chosen}", "r", encoding="utf-8") as f:
            existing_code = f.read()
        topic = random.choice(CODE_TOPICS)
        content = run_with_attempts(lambda: generate_code_edit(existing_code, topic))
        if content is None:
            print("[INFO] 생성 실패로 이번 실행은 변경 없이 종료")
            return
        append_to_daily(content, target_date)
        with open(f"code/{chosen}", "w", encoding="utf-8") as f:
            f.write(validate_python(content) + "\n")
        print(f"[OK] 코드 수정: code/{chosen}")
        print("[INFO] 모드: 코드 수정")
        return

    # 3. 코드 메인 날 (25%)
    if mode_roll < 0.55:
        topic = random.choice(CODE_TOPICS)
        content = run_with_attempts(lambda: generate_code_main(topic))
        if content is None:
            print("[INFO] 생성 실패로 이번 실행은 변경 없이 종료")
            return
        append_to_daily(content, target_date)
        save_code_file(content, target_date)
        print("[INFO] 모드: 코드 메인")
        return

    # 4. 일반 메모 날 (나머지)
    topic = random.choice(TOPICS)
    content = run_with_attempts(lambda: generate_memo(topic))
    if content is None:
        print("[INFO] 생성 실패로 이번 실행은 변경 없이 종료")
        return
    append_to_daily(content, target_date)
    print("[INFO] 모드: 일반 메모")


if __name__ == "__main__":
    main()
