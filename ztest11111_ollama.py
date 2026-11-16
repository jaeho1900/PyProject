from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.documents import Document
import os

# 1. 허깅페이스 임베딩 모델 설정
# (한국어 텍스트 벡터화 성능이 우수한 오픈소스 모델 사용)
local_model_path = "./ko-sroberta-multitask"
embeddings = HuggingFaceEmbeddings(
    model_name=local_model_path,
    model_kwargs={"device": "cpu"},  # GPU가 있다면 "cuda"로 변경 가능
    encode_kwargs={"normalize_embeddings": True}
)

# 벡터 DB가 로컬에 저장될 디렉토리 경로
persist_directory = "./my_vector_db"

# ==========================================
# [STEP 1] 데이터를 벡터로 변환하여 DB에 저장하기
# ==========================================
def save_documents_to_db():
    # 저장할 샘플 문서 (예: 빌딩 관리 매뉴얼 데이터)
    raw_texts = [
        "건물관리에서 대리석 바닥은 주기적인 광택 작업과 중성 세정제 사용이 필수적입니다.",
        "공조 시스템(HVAC) 필터는 분기별로 점검하고 교체해야 에너지 효율을 유지할 수 있습니다.",
        "주차유도 시스템의 오류 발생 시 즉시 통합 관제 센터에 로그를 전달하고 재부팅해야 합니다.",
        "소방시설 자탐설비의 수신기 오작동 시 즉시 담당 관리소에 연락하여 현장을 확인해야 합니다."
    ]

    # LangChain Document 형식으로 변환 (메타데이터 포함 가능)
    docs = [
        Document(page_content=text, metadata={"id": i, "category": "building_management"})
        for i, text in enumerate(raw_texts)
    ]

    print("=== 벡터 DB에 문서 임베딩 및 저장 중 ===")
    # Chroma 벡터스토어 생성 및 로컬 파일 시스템 저장 (persist_directory 지정 시 자동 저장)
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=persist_directory
    )
    print(f"[성공] 총 {len(docs)}개의 문서가 벡터 DB에 저장되었습니다.")
    return vectorstore

# ==========================================
# [STEP 2] 저장된 벡터 DB를 불러와서 유사도 검색하기
# ==========================================
def load_and_search_db(query):
    print(f"\n=== 벡터 DB 불러오기 및 검색 수행 (검색어: '{query}') ===")

    if not os.path.exists(persist_directory):
        print("[알림] 저장된 벡터 DB가 없습니다. 먼저 데이터를 저장합니다.")
        save_documents_to_db()

    # 이미 저장된 로컬 벡터 DB 불러오기
    vectorstore = Chroma(
        persist_directory=persist_directory,
        embedding_function=embeddings
    )

    # 유사도가 높은 상위 2개의 문서 검색
    results = vectorstore.similarity_search(query, k=2)

    print("\n--- [검색 결과] ---")
    for i, doc in enumerate(results):
        print(f"{i+1}. 내용: {doc.page_content}")
        print(f"   메타데이터: {doc.metadata}")

    return results

if __name__ == "__main__":
    # 1. 최초 실행 시 또는 데이터 갱신 시 저장 (이미 있다면 불러와서 검색만 수행 가능)
    if not os.path.exists(persist_directory):
        save_documents_to_db()
    else:
        print("[알림] 기존에 저장된 벡터 DB를 감지했습니다.")

    # 2. 질문/검색 테스트 실행
    user_query = "대리석 관리 방법을 알려줘"
    load_and_search_db(user_query)
