from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
import os
import json

# 대화 기록을 저장할 파일명
HISTORY_FILE = "chat_history.json"

def load_chat_history():
    """저장된 파일이 있다면 이전 대화 기록을 불러옵니다."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                raw_data = json.load(f)
                history = []
                for item in raw_data:
                    if item["role"] == "user":
                        history.append(HumanMessage(content=item["content"]))
                    elif item["role"] == "assistant":
                        history.append(AIMessage(content=item["content"]))
                print(f"[알림] 이전 대화 기록을 성공적으로 불러왔습니다! (총 대화 쌍: {len(history) // 2}개)")
                return history
        except Exception as e:
            print(f"[경고] 대화 기록을 불러오는 중 오류가 발생했습니다: {e}")
    return []

def save_chat_history(chat_history):
    """현재 대화 기록을 JSON 파일로 저장합니다."""
    try:
        raw_data = []
        for msg in chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            raw_data.append({"role": role, "content": msg.content})

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)
        print("[알림] 대화 기록이 파일에 안전하게 저장되었습니다.")
    except Exception as e:
        print(f"[경고] 대화 기록 저장 중 오류가 발생했습니다: {e}")

# 1. llm 객체 생성
llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0.7,
)

# 2. 템플릿 정의
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "당신은 친절하고 유능한 AI 어시스턴트입니다. 이전 대화 맥락을 기억하고 자연스럽게 이어가세요."),
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
    ]
)

# 3. 체인(Chain) 구성
chain = prompt | llm

# 4. 프로그램 시작 시 이전 대화 기록 불러오기
chat_history = load_chat_history()

print("\n=== AI와 대화를 시작합니다. (종료하려면 '종료' 또는 'quit' 입력) ===")
print("💡 팁: 대화를 종료하면 기록이 자동 저장되어 며칠 뒤에 이어서 할 수 있습니다.")

# 5. 체인 실행(chain.invoke)
while True:
    user_input = input("\n사용자: ")

    if user_input.lower() in ["종료", "quit", "exit"]:
        # 종료하기 전 대화 기록 저장
        save_chat_history(chat_history)
        print("대화를 종료합니다. 다음에 뵙겠습니다!")
        break

    try:
        # 모델 실행
        response = chain.invoke({
            "chat_history": chat_history,
            "input": user_input
        })

        ai_response = response.content
        print(f"AI: {ai_response}")

        # 대화 기록 리스트에 추가
        chat_history.append(HumanMessage(content=user_input))
        chat_history.append(AIMessage(content=ai_response))

        # (선택사항) 대화가 오갈 때마다 실시간으로 파일에 백업하려면 아래 주석 해제
        save_chat_history(chat_history)

    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
