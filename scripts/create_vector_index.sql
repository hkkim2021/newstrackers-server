-- pgvector IVFFlat 인덱스 생성
-- Supabase SQL Editor에서 실행

-- 1. vector 확장 활성화 (이미 되어 있을 수 있음)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. embedding 컬럼 추가 (이미 있으면 무시)
ALTER TABLE news_articles ADD COLUMN IF NOT EXISTS embedding vector(768);

-- 3. IVFFlat 인덱스 생성 (cosine distance)
-- lists 값은 데이터 행 수의 제곱근 정도로 설정 (약 10,000행 기준 100)
-- 데이터가 많아지면 lists 값을 늘릴 것
CREATE INDEX IF NOT EXISTS idx_news_articles_embedding
ON news_articles
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
