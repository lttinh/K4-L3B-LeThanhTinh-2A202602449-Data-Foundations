"""Reproducible offline benchmark: python -m scripts.benchmark_personal."""
import json
from pathlib import Path
from src import Document, FixedSizeChunker, ChunkingStrategyComparator, EmbeddingStore, KnowledgeBaseAgent, _mock_embed, compute_similarity

ROOT = Path(__file__).resolve().parents[1]


def load_corpus():
    docs = []
    for path in sorted((ROOT / 'data/shopee-returns').glob('*.md')):
        raw = path.read_text(encoding='utf-8-sig')
        front, body = raw.split('---', 2)[1:]
        # This corpus uses flat string fields, not general YAML.
        metadata = {}
        for line in front.strip().splitlines():
            key, value = line.split(':', 1)
            value = value.strip()
            metadata[key] = json.loads(value) if value.startswith('"') else value
        for key in ('doc_id', 'title', 'source_url', 'retrieved_at', 'document_version', 'audience', 'category'):
            if not metadata.get(key):
                raise ValueError(f'{path}: missing {key}')
        docs.append(Document(metadata['doc_id'], body.strip(), metadata))
    if not 5 <= len(docs) <= 10 or len({d.id for d in docs}) != len(docs):
        raise ValueError('Expected 5–10 documents with unique IDs')
    return docs


def run():
    queries = json.loads((ROOT / 'report/benchmark_queries.json').read_text(encoding='utf-8-sig'))
    if len(queries) != 5:
        raise ValueError('Checkpoint 5 requires exactly five benchmark queries')
    docs = load_corpus()
    chunker = FixedSizeChunker(chunk_size=500, overlap=50)
    chunks = [Document(f'{d.id}::chunk-{i:03d}', text, {**d.metadata, 'chunk_index': i})
              for d in docs for i, text in enumerate(chunker.chunk(d.content))]
    store = EmbeddingStore(embedding_fn=_mock_embed)
    store.add_documents(chunks)
    # Deliberately expose context instead of pretending a mock generates answers.
    agent = KnowledgeBaseAgent(store, lambda prompt: '[MOCK: ngữ cảnh truy xuất, không phải câu trả lời LLM]\n' + prompt.split('CONTEXT:\n', 1)[1].split('\n\nQUESTION:', 1)[0])
    results = []
    for q in queries:
        hits = store.search_with_filter(q['query'], 3, q.get('metadata_filter'))
        gold_doc = next(d for d in docs if d.id == q['gold_doc_id'])
        evidence = q.get('evidence_all', [q['evidence']])
        if not all(part in gold_doc.content for part in evidence):
            raise ValueError(f"Gold evidence missing from {gold_doc.id}")
        gold_chunks = [c for c in chunks if c.metadata['doc_id'] == gold_doc.id
                       and any(part in c.content for part in evidence)]
        for hit in hits:
            hit['relevant'] = hit['metadata']['doc_id'] == q['gold_doc_id'] and any(part in hit['content'] for part in evidence)
        retrieved_gold = '\n'.join(h['content'] for h in hits if h['metadata']['doc_id'] == gold_doc.id)
        results.append({**q, 'top3': hits, 'hit_at_3': any(h['relevant'] for h in hits),
                        'gold_chunk_ids': [c.id for c in gold_chunks],
                        'evidence_covered_at_3': all(part in retrieved_gold for part in evidence),
                        'unfiltered_top3': store.search(q['query'], 3),
                        'agent_answer': agent.answer(q['query'], metadata_filter=q.get('metadata_filter'))})
    pairs = [
        ('Tôi muốn trả hàng.', 'Tôi muốn trả hàng.', 'cao'),
        ('Tôi muốn trả hàng.', 'Tôi muốn gửi lại sản phẩm.', 'cao'),
        ('Người bán chịu phí vận chuyển.', 'Shop thanh toán phí gửi hàng.', 'cao'),
        ('Tôi muốn hoàn tiền.', 'Mặt trăng quay quanh Trái Đất.', 'thấp'),
        ('Đơn hàng bị hư hỏng.', 'Hôm nay tôi học lập trình Python.', 'thấp'),
    ]
    output = {'backend': 'MockEmbedder (64 dimensions, MD5; no semantic meaning)',
              'strategy': 'fixed_size', 'chunk_size': 500, 'overlap': 50,
              'document_count': len(docs), 'chunk_count': len(chunks),
              'baseline': {d.id: ChunkingStrategyComparator().compare(d.content, 500) for d in docs[:3]},
              'similarity': [{'a': a, 'b': b, 'hypothesis': p, 'score': compute_similarity(_mock_embed(a), _mock_embed(b))} for a, b, p in pairs],
              'results': results}
    path = ROOT / 'report/benchmark_results.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'{len(docs)} documents; {len(chunks)} chunks; Hit@3={sum(r["hit_at_3"] for r in results)}/5; {path}')
    for index, result in enumerate(results, 1):
        print(f"\nQuery {index}: {result['query']}")
        print(f"Filter: {result.get('metadata_filter', {})}")
        print(f"Gold: {result['gold_answer']}")
        for rank, hit in enumerate(result['top3'], 1):
            print(f"  {rank}. score={hit['score']:.6f} doc_id={hit['metadata']['doc_id']} chunk_id={hit['id']}")
            print('     ' + hit['content'].replace('\n', ' ')[:180])


if __name__ == '__main__':
    run()
