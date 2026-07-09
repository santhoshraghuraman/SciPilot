"""
SciPilot — IBM watsonx.ai Full Connection Test
Run: python scripts/test_connection.py
"""
import sys, os
sys.path.insert(0, ".")

from dotenv import load_dotenv
load_dotenv(".env", override=True)

key = os.getenv("WATSONX_API_KEY", "")
pid = os.getenv("WATSONX_PROJECT_ID", "")
url = os.getenv("WATSONX_URL", "")

print("=" * 55)
print("SciPilot — IBM watsonx.ai Connection Test")
print("=" * 55)
print(f"Project ID : {pid}")
print(f"URL        : {url}")
print(f"API Key    : {key[:12]}...{key[-4:]}  (len={len(key)})")
print()

from ibm_watsonx_ai import Credentials
from ibm_watsonx_ai.foundation_models import Embeddings, ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as Params

creds = Credentials(url=url, api_key=key)

# ── Test 1: Embeddings ────────────────────────────────────────────────────────
print("[1/2] IBM Slate Embeddings ...")
try:
    emb = Embeddings(
        model_id="ibm/slate-125m-english-rtrvr",
        credentials=creds,
        project_id=pid,
    )
    result = emb.embed_documents(texts=["SciPilot connection test"])
    dim = len(result[0])
    print(f"      OK — embedding dimension = {dim}")
    assert dim > 0, "Empty embedding returned"
except Exception as e:
    print(f"      FAIL — {e}")

# ── Test 2: Granite text generation ──────────────────────────────────────────
print("[2/2] IBM Granite-13b-instruct-v2 ...")
try:
    model = ModelInference(
        model_id="ibm/granite-13b-instruct-v2",
        credentials=creds,
        project_id=pid,
        params={
            Params.MAX_NEW_TOKENS: 40,
            Params.TEMPERATURE: 0.1,
        },
    )
    prompt = (
        "<|system|>\nYou are a helpful assistant.\n"
        "<|user|>\nSay 'SciPilot is ready' in one sentence.\n"
        "<|assistant|>\n"
    )
    resp = model.generate(prompt=prompt)
    text = resp["results"][0]["generated_text"].strip()
    print(f"      OK — response: {text!r}")
except Exception as e:
    print(f"      FAIL — {e}")

print()
print("=" * 55)
print("Done. Fix any FAIL items above before running the app.")
print("=" * 55)
