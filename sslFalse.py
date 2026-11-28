# huggingface.co 등에서 HTTPS로 모델을 내려받으며 정상적으로 인증서 검증을 통과시키려면,
# 번들 파일을 만들어 SSL_CERT_FILE과 REQUESTS_CA_BUNDLE에 그 경로를 지정해 두는 것이 가장 안정적이다.
# (한 번 생성해 두면 재사용할 수 있다.)

# 1. 번들 파일 만들기
#  : Python의 requests·urllib3 계열은 기본적으로 certifi의 cacert.pem 파일 경로를 신뢰 저장소로 사용한다.
#    certifi 기본 파일에 TLS용 Root CA가 포함된 PEM 번들 파일을 만들어 SSL_CERT_FILE과 REQUESTS_CA_BUNDLE에 지정한다.

# 2. SSL 인증서 검증 임시 끄기 (verify=False 등)
#  : 임시 테스트로 오류를 피할 수는 있으나 transformers/huggingface_hub 전체에
#    일관되게 적용하기가 번거롭다.

# 3. 로컬 모델 캐시/폴더 직접 지정
#  : 외부 허깅페이스 접속 자체를 하지 않고, 미리 받은 모델 폴더 경로(model="C:/models/...")로
#    pipeline을 실행하면 TLS 검증이 일어나지 않는다.

# 4. 시스템/런타임별 별도 설정
#  : 예를 들어 httpx를 직접 쓸 때는 httpx.Client(verify=...)처럼 인자를 줄 수 있지만,
#    transformers·huggingface_hub·requests는 환경변수(SSL_CERT_FILE, REQUESTS_CA_BUNDLE)에
#    파일 경로를 받는 구조이다.


# ==========================================
# [step 1] 현재 TLA 인증서 추출
# ==========================================
import socket
import ssl
from pathlib import Path

HOST = "huggingface.co"
PORT = 443
OUT_PEM = Path("D:/PyProject/PyResource/captured_chain.pem")
OUT_PEM.parent.mkdir(parents=True, exist_ok=True)

# 진단용: 실제 서버/프록시가 건네는 인증서 체인을 보기 위해 검증을 끈 컨텍스트 생성
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

pem_parts = []

with socket.create_connection((HOST, PORT), timeout=10) as sock:
    with ctx.wrap_socket(sock, server_hostname=HOST) as ssock:
        # Peer 인증서(DER) 추출
        der_cert = ssock.getpeercert(binary_form=True)
        if der_cert:
            pem_parts.append(ssl.DER_cert_to_PEM_cert(der_cert))

        # Python 3.10+ 에서 전체 인증서 체인(DER 리스트) 확인 시도
        get_chain = getattr(ssock, "get_verified_chain", None) or getattr(
            ssock, "get_unverified_chain", None
        )
        chain = get_chain() if callable(get_chain) else None

        if chain:
            for idx, c in enumerate(chain):
                c_der = c.public_bytes(encoding=__import__("cryptography.hazmat.primitives.serialization", fromlist=["Encoding"]).Encoding.DER) if hasattr(c, "public_bytes") else c
                print(f"[Chain #{idx}]")
                pem_parts.append(ssl.DER_cert_to_PEM_cert(c_der))

# 중복 제거 후 PEM 저장
unique_pems = list(dict.fromkeys(pem_parts))
OUT_PEM.write_text("\n".join(unique_pems), encoding="utf-8")
print(f"저장 완료: {OUT_PEM} (인증서 {len(unique_pems)}개)")  # 1개 파일에 내부용 외부용 2개 추출


# ==========================================
# [step 2] 현재 TLA 인증서 확인
# ==========================================
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.backends import default_backend

pem_bytes = Path("D:/PyProject/PyResource/captured_chain.pem").read_bytes()
# 여러 개의 PEM 블록 분리
chunks = [
    (block + "-----END CERTIFICATE-----").encode("utf-8")
    for block in pem_bytes.decode("utf-8").split("-----END CERTIFICATE-----")
    if "-----BEGIN CERTIFICATE-----" in block
]

for i, raw in enumerate(chunks):
    cert = x509.load_pem_x509_certificate(raw, default_backend())
    print("", sep="\n")
    print(f"=== 인증서 #{i} ===")
    print("Subject :", cert.subject.rfc4514_string())
    print("Issuer  :", cert.issuer.rfc4514_string())
    print("NotAfter:", cert.not_valid_after_utc)

# ==========================================
# [step 3] 터미널에서 직접 번들 파일 만들기
# ==========================================
# 확인된 루트CA인증서 추출(Win+R, certlm.msc, 신뢰할수있는루트인증기관, 해당인증서, 모든작업, 내보내기, Base64fh..., 다음, somansa_bundle.pem)

# python -c "from pathlib import Path; import certifi; out = Path('D:/PyProject/PyResource/somansa_bundle.pem'); out.parent.mkdir(parents=True, exist_ok=True); out.write_text(Path(certifi.where()).read_text(encoding='utf-8') + '\n' + Path('D:/PyProject/PyResource/captured_chain.pem').read_text(encoding='utf-8'), encoding='utf-8'); print('Saved:', out)"
# $env:SSL_CERT_FILE="D:\PyProject\PyResource\somansa_bundle.pem"
# $env:REQUESTS_CA_BUNDLE="D:\PyProject\PyResource\somansa_bundle.pem"
# python 1.py (파일 실행)

# ==========================================
# [step 3-1] 파이썬 코드에서 실행
# ==========================================
import os
from pathlib import Path
import certifi

bundle_path = Path("D:/PyProject/PyResource/somansa_bundle.pem")
bundle_path.parent.mkdir(parents=True, exist_ok=True)
bundle_path.write_text(
    Path(certifi.where()).read_text(encoding="utf-8")
    + "\n"
    + Path("D:/PyProject/PyResource/captured_chain.pem").read_text(encoding="utf-8"),
    encoding="utf-8",
)

os.environ["SSL_CERT_FILE"] = str(bundle_path)
os.environ["REQUESTS_CA_BUNDLE"] = str(bundle_path)
os.environ["CURL_CA_BUNDLE"] = str(bundle_path)

from transformers import pipeline

sentiment_agent = pipeline(
    task="text-classification",
    model="distilbert-base-uncased-finetuned-sst-2-english",
)
review = "The service was fast and the staff was friendly."
print(sentiment_agent(review))
