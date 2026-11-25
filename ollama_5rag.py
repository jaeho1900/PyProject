from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from ddgs import DDGS
import os
import json

# 설정 경로 및 모델명
HISTORY_FILE = "./langdata/chat_history.json"
PERSIST_DIRECTORY = "./my_vector_db"
MODEL_NAME = "./ko-sroberta-multitask"   # "jhgan/ko-sroberta-multitask"

# ==========================================
# [1] 대화 기록 관리 함수
# ==========================================
def load_chat_history():
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
    try:
        raw_data = []
        for msg in chat_history:
            role = "user" if isinstance(msg, HumanMessage) else "assistant"
            raw_data.append({"role": role, "content": msg.content})

        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(raw_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"[경고] 대화 기록 저장 중 오류가 발생했습니다: {e}")

# ==========================================
# [2] 인터넷 웹 서칭 함수 (DuckDuckGo)
# ==========================================
def fetch_web_search_data(query, max_results=5):
    print(f"=== [인터넷 서칭 중] 키워드: '{query}' ===")
    search_snippets = []
    try:
        # region을 'kr-kr'로 지정해 한국어 검색 결과 우선 확보
        with DDGS(verify=False, timeout=20) as ddgs:
            results = list(ddgs.text(query, region="kr-kr", max_results=max_results))

        if not results:
            print("[알림] 검색 결과가 없습니다.")
            return "- 웹 검색 결과가 없습니다. 내부 문서 및 법리를 기반으로 작성합니다."

        for r in results:
            title = r.get("title", "")
            body = r.get("body", "")
            url = r.get("href", "")
            search_snippets.append(f"- **제목:** {title}\n  **요약:** {body}\n  **출처:** {url}")

        print("[성공] 최신 웹 데이터를 성공적으로 수집했습니다.")
    except Exception as e:
        print(f"[경고] 웹 검색 중 오류가 발생했습니다: {e}")
        search_snippets.append("- 웹 검색 데이터를 가져오지 못했습니다. 내부 문서 및 법리를 기반으로 작성합니다.")

    return "\n\n".join(search_snippets)

# ==========================================
# [3] 메인 실행부
# ==========================================
if __name__ == "__main__":
    print("=== 빌딩관리 법률 및 트렌드 AI 어시스턴트 초기화 중 ===")

    # 1. 벡터 DB 존재 여부 확인
    if not os.path.exists(PERSIST_DIRECTORY):
        print(f"[오류] '{PERSIST_DIRECTORY}' 벡터 DB가 존재하지 않습니다.")
        print("먼저 'build_vector_db.py'를 실행하여 벡터 DB를 생성해 주세요!")
        exit(1)

    # 2. 임베딩 모델 및 벡터 DB 로드
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},     # GPU가 있다면 "cuda"로 변경 가능
        encode_kwargs={"normalize_embeddings": True}
    )
    vectorstore = Chroma(
        persist_directory=PERSIST_DIRECTORY,
        embedding_function=embeddings
    )
    print("[알림] 로컬 벡터 DB를 성공적으로 불러왔습니다.")

    # 3. llm 객체 생성
    llm = ChatOllama(
        model="qwen2.5:3b",
        temperature=0.4,
    )

    # 4. 템플릿 정의
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", """당신은 대한민국 최고 권위의 건물관리 및 공사도급 계약 분쟁 전문 '빌딩관리 법률가'입니다.
제공된 [내부 판례 데이터(PDF)]와 [실시간 웹 검색 자료]를 종합하여 사용자의 질문에 정확하고 전문적인 법적 분석과 실무적 조언을 제공하세요.

[내부 판례 데이터(PDF)]
{vector_context}

[실시간 웹 검색 참고 자료]
{web_context}"""),
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ]
    )

    chain = prompt | llm
    chat_history = load_chat_history()

    print("\n=== 빌딩관리 법률 상담을 시작합니다. ===")
    print("💡 [안내]")
    print(" - 일반 질문: 내부 판례(PDF) 기반으로 답변합니다.")
    print(" - 인터넷 검색 포함: 질문 앞에 **'!웹 '** 또는 **'!w '**를 붙여서 입력하세요. (예: '!웹 최근 대법원 판례 동향')")
    print(" - 종료하려면 '종료' 또는 'quit'를 입력하세요.\n")

    # 5. 인터랙티브 루프
    while True:
        user_input = input("\n사용자: ").strip()

        if user_input.lower() in ["종료", "quit", "exit"]:
            save_chat_history(chat_history)
            print("대화를 종료합니다. 다음에 뵙겠습니다!")
            break

        if not user_input:
            continue

        # 사용자가 인터넷 검색을 원했는지 확인 (!웹 또는 !w 로 시작하는지 체크)
        use_web_search = False
        if user_input.startswith("!웹 ") or user_input.startswith("!w "):
            use_web_search = True
            # 명령어 접두사 제거하고 실제 검색어/질문만 추출
            actual_query = user_input[3:].strip()
        else:
            actual_query = user_input

        try:
            # Step A: 벡터 DB에서 관련 판례 문서 검색 (상위 2개)[cite: 6]
            retrieved_docs = vectorstore.similarity_search(actual_query, k=2)
            vector_context = "\n".join([f"- {doc.page_content} (출처 페이지: {doc.metadata.get('page', 'N/A')})" for doc in retrieved_docs])

            # Step B: 사용자가 선택한 경우에만 인터넷 웹 검색 수행
            if use_web_search:
                print(f"[선택 기능 활성화] 인터넷 검색을 수행합니다.")
                web_context = fetch_web_search_data(actual_query, max_results=2)
            else:
                web_context = "사용자가 인터넷 검색을 요청하지 않았습니다. 내부 판례 및 법리 데이터를 기반으로 답변하세요."

            # Step C: LLM 체인 실행
            response = chain.invoke({
                "vector_context": vector_context,
                "web_context": web_context,
                "chat_history": chat_history,
                "input": actual_query
            })

            ai_response = response.content
            print(f"\n빌딩관리 법률가: {ai_response}")

            # Step D: 대화 기록 업데이트 및 저장 (실제 질문 내용 기준으로 저장)
            chat_history.append(HumanMessage(content=actual_query))
            chat_history.append(AIMessage(content=ai_response))
            save_chat_history(chat_history)

        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
