"""Measure chunk structure: python -m scripts.compare_chunk_structure."""
import json

from scripts.benchmark_personal import ROOT, load_corpus
from src import FixedSizeChunker, RecursiveChunker, SentenceChunker


def run():
    docs = load_corpus()
    strategies = {
        'fixed_500_overlap_50': FixedSizeChunker(500, 50),
        'recursive_500': RecursiveChunker(chunk_size=500),
        'sentence_3': SentenceChunker(3),
    }
    output = {'personal_strategy': 'fixed_size', 'document_count': len(docs),
              'source_characters': sum(len(d.content) for d in docs),
              'strategies': {}, 'example': {}}
    example = next(d for d in docs if d.id == 'shopee-instant-refund')
    output['example_doc_id'] = example.id
    for name, chunker in strategies.items():
        chunks = [c for d in docs for c in chunker.chunk(d.content)]
        output['strategies'][name] = {
            'count': len(chunks), 'max_length': max(map(len, chunks)),
            'over_500': sum(len(c) > 500 for c in chunks),
            'total_characters': sum(map(len, chunks)),
        }
        output['example'][name] = chunker.chunk(example.content)
    path = ROOT / 'report/chunk_structure_results.json'
    path.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
    print(path)


if __name__ == '__main__':
    run()
