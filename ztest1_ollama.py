from langchain_ollama import ChatOllama
import textwrap
from langchain_core.prompts import ChatPromptTemplate

llm = ChatOllama(
    model="qwen2.5:14b",
    # model="exaone3.5:7.8b",
    temperature=0.7,  # 창의성 조절 (0.0 ~ 1.0)
)

# ==================
# 1안)즉문즉답
response = llm.invoke("건물관리와 빌딩관리의 가장 큰 차이점을 설명해줘.")

# # ------------------
# # 2안)역할부여 및 질의응답
# prompt = ChatPromptTemplate.from_messages(
#     [
#       ("system", "당신은 빌딩관리 30년차 전문가입니다. 사용자의 질문에 재치 있게 답변해 주세요."),
#       ("user", "{ingredient}를 관리하기 위한 가성비 높은 방법 2가지를 추천해 주세요."),
#     ]
# )
# chain = prompt | llm
# response = chain.invoke({"ingredient": "대리석"})
# ==================

wrapped_text = textwrap.fill(response.content, width=40)
print(wrapped_text)
