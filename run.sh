python -m pyserini.index.lucene \
  --collection JsonCollection \
  --input data/jsonl \
  --index indexes/sample_collection_jsonl \
  --generator DefaultLuceneDocumentGenerator \
  --threads 1 \
  --storePositions --storeDocvectors --storeRaw