import unittest
from src import RecursiveChunker, EmbeddingStore, Document, KnowledgeBaseAgent, compute_similarity


class TestPersonalEdgeCases(unittest.TestCase):
    def test_recursive_preserves_every_character_and_size(self):
        text = 'Điều kiện. Ngoại lệ!\n\n' + 'x' * 99 + '\nKết thúc.'
        for separators in (None, [], ['\n\n'], ['']):
            chunks = RecursiveChunker(separators, 17).chunk(text)
            self.assertEqual(''.join(chunks), text)
            self.assertTrue(all(0 < len(c) <= 17 for c in chunks))

    def test_recursive_invalid_size(self):
        with self.assertRaises(ValueError):
            RecursiveChunker(chunk_size=0).chunk('abc')

    def test_cosine_dimension_mismatch(self):
        with self.assertRaises(ValueError):
            compute_similarity([1], [1, 2])

    def test_filter_before_ranking_and_delete_parent(self):
        vectors = {'q': [1., 0.], 'buyer': [0., 1.], 'seller': [1., 0.]}
        store = EmbeddingStore(embedding_fn=vectors.__getitem__)
        store.add_documents([Document('a0', 'buyer', {'doc_id': 'a', 'audience': 'buyer'}),
                             Document('a1', 'buyer', {'doc_id': 'a', 'audience': 'buyer'}),
                             Document('b0', 'seller', {'doc_id': 'b', 'audience': 'seller'})])
        self.assertEqual(store.search('q', 1)[0]['id'], 'b0')
        self.assertEqual(store.search_with_filter('q', 1, {'audience': 'buyer'})[0]['id'], 'a0')
        self.assertEqual(store.search('q', 0), [])
        self.assertTrue(store.delete_document('a'))
        self.assertEqual(store.get_collection_size(), 1)
        self.assertFalse(store.delete_document('a'))

    def test_agent_passes_filtered_context_and_question(self):
        store = EmbeddingStore()
        store.add_documents([Document('b', 'buyer evidence', {'audience': 'buyer', 'source_url': 'source'}),
                             Document('s', 'seller evidence', {'audience': 'seller'})])
        prompts = []
        agent = KnowledgeBaseAgent(store, lambda p: prompts.append(p) or 'answer')
        self.assertEqual(agent.answer('my question', metadata_filter={'audience': 'buyer'}), 'answer')
        self.assertIn('buyer evidence', prompts[0])
        self.assertIn('my question', prompts[0])
        self.assertNotIn('seller evidence', prompts[0])
        agent.answer('missing', metadata_filter={'audience': 'none'})
        self.assertEqual(len(prompts), 1)
