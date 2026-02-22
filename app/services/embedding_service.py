# --- Gemini 임베딩 (주석 처리) ---
# import asyncio
# import logging
# import time
#
# from google import genai
#
# from app.core.config import settings
#
# logger = logging.getLogger(__name__)
#
# _client = None
#
# def _get_client() -> genai.Client:
#     global _client
#     if _client is None:
#         _client = genai.Client(api_key=settings.GOOGLE_API_KEY)
#     return _client
#
# MODEL = "models/gemini-embedding-001"
# DIMENSION = 768
# MAX_RETRIES = 3
#
# def _build_embedding_text(title: str, description: str | None) -> str:
#     parts = [title]
#     if description:
#         parts.append(description)
#     return " ".join(parts).strip()
#
# def generate_embedding(text: str) -> list[float] | None:
#     ...
#
# def generate_embeddings_batch(texts: list[str], batch_size: int = 100) -> list[list[float] | None]:
#     ...

# --- OpenAI 임베딩 ---
import logging
import time

from openai import OpenAI

from app.core.config import settings

logger = logging.getLogger(__name__)

_client = None

MODEL = "text-embedding-ada-002"
DIMENSION = 1536
MAX_RETRIES = 3


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return _client


def _build_embedding_text(title: str, description: str | None) -> str:
    """제목+설명을 결합하여 임베딩 입력 텍스트를 만든다."""
    parts = [title]
    if description:
        parts.append(description)
    return " ".join(parts).strip()


def generate_embedding(text: str) -> list[float] | None:
    """단일 텍스트의 임베딩 벡터를 생성한다. 실패 시 None 반환."""
    if not text or not text.strip():
        return None

    client = _get_client()
    for attempt in range(MAX_RETRIES):
        try:
            result = client.embeddings.create(
                model=MODEL,
                input=text,
            )
            return result.data[0].embedding
        except Exception as e:
            logger.warning(f"임베딩 생성 실패 (시도 {attempt + 1}/{MAX_RETRIES}): {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)

    logger.error(f"임베딩 생성 최종 실패: {text[:80]}...")
    return None


def generate_embeddings_batch(texts: list[str], batch_size: int = 100) -> list[list[float] | None]:
    """여러 텍스트를 배치로 임베딩한다. 각 결과는 벡터 또는 None."""
    results: list[list[float] | None] = [None] * len(texts)
    client = _get_client()

    for i in range(0, len(texts), batch_size):
        batch = texts[i: i + batch_size]
        valid_indices = [j for j, t in enumerate(batch) if t and t.strip()]
        valid_texts = [batch[j] for j in valid_indices]

        if not valid_texts:
            continue

        for attempt in range(MAX_RETRIES):
            try:
                result = client.embeddings.create(
                    model=MODEL,
                    input=valid_texts,
                )
                for idx, embedding_obj in zip(valid_indices, result.data):
                    results[i + idx] = embedding_obj.embedding
                break
            except Exception as e:
                logger.warning(
                    f"배치 임베딩 실패 (시도 {attempt + 1}/{MAX_RETRIES}, "
                    f"배치 {i // batch_size}): {e}"
                )
                if attempt < MAX_RETRIES - 1:
                    time.sleep(2 ** attempt)
                else:
                    logger.error(f"배치 임베딩 최종 실패 (배치 {i // batch_size})")

    return results
