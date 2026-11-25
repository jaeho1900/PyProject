from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import os

# 설정 경로 및 모델명
PDF_FILE_PATH = "./langdata/sample.pdf"
PERSIST_DIRECTORY = "./my_vector_db"
MODEL_NAME = "./ko-sroberta-multitask"   # "jhgan/ko-sroberta-multitask"

def build_vector_database():
    if not os.path.exists(PDF_FILE_PATH):
        print(f"[오류] '{PDF_FILE_PATH}' 파일을 찾을 수 없습니다. 경로를 확인해주세요.")
        return

    print(f"=== [1단계] '{PDF_FILE_PATH}' 파일 로딩 및 텍스트 추출 중 ===")
    loader = PyPDFLoader(PDF_FILE_PATH)
    raw_documents = loader.load()

    # 텍스트 청크 분할 설정
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    docs = text_splitter.split_documents(raw_documents)
    print(f"[알림] PDF가 총 {len(docs)}개의 청크(조각)로 분할되었습니다.")

    print("=== [2단계] 임베딩 모델 로드 및 벡터 DB 저장 중 ===")
    embeddings = HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},   # GPU가 있다면 "cuda"로 변경 가능
        encode_kwargs={"normalize_embeddings": True}
    )

    # 기존 DB가 있다면 덮어쓰거나 추가됨
    vectorstore = Chroma.from_documents(
        documents=docs,
        embedding=embeddings,
        persist_directory=PERSIST_DIRECTORY
    )

    print(f"[성공] 벡터 DB 구축이 완료되었습니다. (저장 경로: '{PERSIST_DIRECTORY}')")

if __name__ == "__main__":
    build_vector_database()
