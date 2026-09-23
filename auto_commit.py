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

EXTRA_FILES = [
    "notes/quick_tips.md",
    "notes/snippets.md",
    "notes/todo.md",
    "notes/resources.md",
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


def generate_til(topic: str) -> str:
    client = Anthropic()

    system_prompt = (
        "너는 개발을 공부하면서 메모하는 평범한 개발자야. "
        "너무 완벽한 블로그 글처럼 쓰지 마. "
        "실제 공부 노트처럼 약간 거칠고 솔직하게 써. "
        "분량은 공백 포함 한글 기준 160\~320자 사이로 들쭉날쭉하게. "
        "제목은 ## 로 시작해도 되고 안 해도 됨. "
        "불릿은 1\~3개 정도만 쓰고, 코드는 정말 필요할 때만 아주 짧게. "
        "가끔은 '이거 헷갈림', '다음에 다시 볼 것', '아직 잘 모르겠음' 같은 말을 자연스럽게 넣어. "
        "인사말이나 '오늘은' 같은 시작 문구는 절대 넣지 마."
    )

    user_prompt = f"주제: {topic}\n이 내용으로 짧은 공부 메모 하나 적어줘."

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=450,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    return message.content[0].text.strip()


def get_backdated_date() -> datetime.date:
    days_ago = random.randint(0, 4)
    return datetime.date.today() - datetime.timedelta(days=days_ago)


def append_to_file(content: str, target_date: datetime.date, filepath: str = "daily_til.md") -> None:
    date_str = target_date.strftime("%Y-%m-%d")
    entry = f"\n\n---\n\n### {date_str}\n\n{content}\n"

    file_exists = os.path.exists(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("# Daily TIL Log\n")
        f.write(entry)
    print(f"[OK] {date_str} → {filepath}")


def write_individual_til(content: str, target_date: datetime.date) -> None:
    if random.random() > 0.60:
        return
    os.makedirs("til", exist_ok=True)
    date_str = target_date.strftime("%Y-%m-%d")
    filepath = f"til/{date_str}.md"
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"# {date_str}\n\n{content}\n")
    print(f"[OK] 개별 파일: {filepath}")


def update_topics_index(topic: str, target_date: datetime.date) -> None:
    if random.random() > 0.50:
        return
    os.makedirs("notes", exist_ok=True)
    filepath = "notes/topics.md"
    date_str = target_date.strftime("%Y-%m-%d")
    line = f"- {date_str} · {topic}\n"
    file_exists = os.path.exists(filepath)
    with open(filepath, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("# Topics\n\n")
        f.write(line)
    print(f"[OK] topics 업데이트")


def make_extra_fake_changes(target_date: datetime.date) -> None:
    if random.random() > 0.35:
        return

    os.makedirs("notes", exist_ok=True)
    selected = random.sample(EXTRA_FILES, k=random.randint(1, 2))

    for filepath in selected:
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# {os.path.basename(filepath)}\n\n")

        note = random.choice([
            f"- {target_date}: 복습함\n",
            f"- {target_date}: 나중에 다시 볼 것\n",
            f"- {target_date}: 관련 링크 저장\n",
            f"- {target_date}: 좀 더 파봐야 할 듯\n",
        ])
        with open(filepath, "a", encoding="utf-8") as f:
            f.write(note)
        print(f"[OK] 추가 변경: {filepath}")


def light_day(target_date: datetime.date) -> None:
    """Claude 호출 없이 아주 짧은 메모만 남기는 가벼운 날"""
    content = random.choice(LIGHT_NOTES)
    append_to_file(content, target_date)

    # 가끔 다른 파일도 아주 살짝 건드림
    if random.random() < 0.4:
        make_extra_fake_changes(target_date)

    print("[INFO] 가벼운 날로 처리했습니다.")


def main() -> None:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("[ERROR] ANTHROPIC_API_KEY 없음", file=sys.stderr)
        sys.exit(1)

    target_date = get_backdated_date()
    print(f"[INFO] 날짜: {target_date}")

    # 약 22% 확률로 가벼운 날
    if random.random() < 0.22:
        light_day(target_date)
        return

    # 일반 날
    topic = random.choice(TOPICS)
    print(f"[INFO] 주제: {topic}")

    try:
        content = generate_til(topic)
    except Exception as e:
        print(f"[ERROR] API 실패: {e}", file=sys.stderr)
        sys.exit(1)

    append_to_file(content, target_date)
    write_individual_til(content, target_date)
    update_topics_index(topic, target_date)
    make_extra_fake_changes(target_date)


if __name__ == "__main__":
    main()
