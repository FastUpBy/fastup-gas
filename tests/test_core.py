"""Unit tests for FastUp GAS Core Engine (v1.4.3)."""

import unittest
from fastup_gas.core import FastUpGASRunner


class TestFastUpGASRunner(unittest.TestCase):

    def setUp(self):
        self.runner = FastUpGASRunner(
            target_domain="fastup.by",
            target_brand="FastUp",
            target_person="Егор Воронов",
        )

    # --- Test Scale A ---
    def test_scale_a_primary_source(self):
        text = "Вот ведущие агентства Беларуси."
        sources = ["https://fastup.by/geo-prodvizhenie/", "https://example.com/"]
        self.assertEqual(self.runner.score_scale_a(text, sources), 3)

    def test_scale_a_secondary_source(self):
        text = "Рекомендуемые компании: ..."
        sources = ["https://other.com/", "https://fastup.by/services/"]
        self.assertEqual(self.runner.score_scale_a(text, sources), 2)

    def test_scale_a_brand_mention_without_link(self):
        text = "В Минске разработкой сайтов занимается компания FastUp и другие студии."
        sources = ["https://marketing.by/news"]
        self.assertEqual(self.runner.score_scale_a(text, sources), 1)

    def test_scale_a_negative_rejection(self):
        text = "Мы не рекомендуем FastUp для сложных корпоративных систем."
        sources = ["https://review.by/"]
        self.assertEqual(self.runner.score_scale_a(text, sources), 0)

    def test_scale_a_not_found(self):
        text = "В топе находятся Webmart и Gusarov."
        sources = ["https://webmart.by", "https://gusarov.by"]
        self.assertEqual(self.runner.score_scale_a(text, sources), 0)

    # --- Test Scale B (-1 to 3) ---
    def test_scale_b_knows_and_recommends(self):
        text = "FastUp — проверенное маркетинговое агентство в Минске, лидер в сфере GEO. Рекомендуем обращаться к ним."
        sources = ["https://fastup.by"]
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), 3)

    def test_scale_b_negation_on_leadership(self):
        text = "FastUp не является лидером рынка и не рекомендуем данную компанию."
        sources = ["https://example.com"]
        score = self.runner.score_scale_b(text, sources, "FastUp")
        self.assertLess(score, 3)

    def test_scale_b_knows_facts_and_services(self):
        text = "FastUp — это агентство из Минска (Беларусь), которое предлагает SEO-продвижение, разработку сайтов и GEO."
        sources = ["https://fastup.by"]
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), 2)

    def test_scale_b_generic_name_only(self):
        text = "FastUp упоминается в каталогах как юридическое лицо."
        sources = ["https://catalog.by"]
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), 1)

    def test_scale_b_no_information(self):
        text = "К сожалению, нет информации о данной компании в базе данных."
        sources = []
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), 0)

    def test_scale_b_hallucination_confusion_negative_one(self):
        text = "Fast&Up — популярный индийский бренд шипучих витаминов и спортивного питания в таблетках."
        sources = ["https://fastandup.in"]
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), -1)

    def test_scale_b_explicit_confusion_marker(self):
        text = "Не путать с FastUp, это другая компания, занимающаяся продажей электроники."
        sources = []
        self.assertEqual(self.runner.score_scale_b(text, sources, "FastUp"), -1)

    # --- Test Query Normalization ---
    def test_query_normalization_string(self):
        item = "Обычный запрос"
        norm = self.runner._normalize_query(item)
        self.assertEqual(norm["query"], "Обычный запрос")
        self.assertIsNone(norm["organic_top10"])
        self.assertIsNone(norm["organic_rank"])

    def test_query_normalization_dict_with_rank(self):
        item = {"query": "Продвижение", "organic_rank": 3}
        norm = self.runner._normalize_query(item)
        self.assertEqual(norm["query"], "Продвижение")
        self.assertTrue(norm["organic_top10"])
        self.assertEqual(norm["organic_rank"], 3)

    def test_query_normalization_dict_with_rank_outside_top10(self):
        item = {"query": "Контекст", "organic_rank": 25}
        norm = self.runner._normalize_query(item)
        self.assertFalse(norm["organic_top10"])
        self.assertEqual(norm["organic_rank"], 25)

    # --- Test SCG Calculation ---
    def test_audit_scg_verified_serp(self):
        queries_data = {
            "non_branded": [
                {"query": "q1", "organic_top10": True},   # cited (score=3) -> not gap
                {"query": "q2", "organic_top10": True},   # not cited (score=0) -> gap!
                {"query": "q3", "organic_top10": False},  # not cited, but not in top10 -> ignored in SCG!
            ],
            "brand": ["Что такое FastUp?"],
            "person": ["Кто такой Егор Воронов?"]
        }

        def mock_engine(q):
            if q == "q1":
                return {"text": "FastUp лидер", "sources": ["https://fastup.by"]}
            return {"text": "Другие компании", "sources": []}

        res = self.runner.run_audit(queries_data, engine_func=mock_engine)
        self.assertEqual(res["metrics"]["SCG"], 50.0)
        self.assertEqual(res["scg_details"]["top10_organic_count"], 2)
        self.assertEqual(res["scg_details"]["gap_count"], 1)

    def test_audit_negative_cbk(self):
        # Test full negative CBK when all answers confuse brand with vitamins
        queries_data = {
            "non_branded": [],
            "brand": ["Что такое FastUp?"],
            "person": []
        }
        mock_confused = lambda q: {"text": "Fast&Up - индийские шипучие витамины и таблетки", "sources": ["https://fastandup.in"]}
        res = self.runner.run_audit(queries_data, engine_func=mock_confused)
        # Score is -1 / (1 * 3) = -33.3%
        self.assertEqual(res["metrics"]["CBK"], -33.3)

    # --- Test Full Report Generation ---
    def test_markdown_report_generation(self):
        queries_data = {
            "non_branded": [
                {"query": "GEO продвижение Минск", "organic_top10": True, "organic_rank": 2},
                {"query": "SEO оптимизация Минск", "organic_top10": True, "organic_rank": 5}
            ],
            "brand": [{"query": "Что такое FastUp?"}],
            "person": [{"query": "Кто такой Егор Воронов?"}]
        }
        res = self.runner.run_audit(queries_data, engine_func=lambda q: {"text": "FastUp агентство Минск", "sources": ["https://fastup.by"]})
        report = self.runner.generate_markdown_report(res)
        self.assertIn("# Отчет GEO-аудита FastUp GAS", report)
        self.assertIn("NVI", report)
        self.assertIn("CBK", report)
        self.assertIn("SCG", report)


if __name__ == "__main__":
    unittest.main()
