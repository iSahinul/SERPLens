import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from serplens.prompt_scan import (aggregate, prompt_like, proven_demand,
                                  verdict)


def row(query, page, clicks, imps, pos):
    return {"query": query, "page": page, "clicks": clicks,
            "impressions": imps, "position": pos}


ROWS = [
    # 9-word question, two pages: weighted pos = (100*10 + 50*4)/150 = 8.0
    row("how do i fix a leaking tap at home", "/a", 2, 100, 10.0),
    row("how do i fix a leaking tap at home", "/b", 0, 50, 4.0),
    # 8-word query at pos 2.0, zero clicks -> WATCH
    row("what is the best way to descale kettles", "/c", 0, 40, 2.0),
    # 8-word query deep -> CONTENT GAP
    row("why does my washing machine smell so bad lately", "/d", 0, 10, 25.0),
    # short query: never prompt-like, but proven demand if question word
    row("how to descale kettle", "/c", 5, 200, 6.0),
    # long but too few impressions
    row("a very long query that nobody really searches for ever", "/e", 0, 2, 9.0),
]


class TestVerdict(unittest.TestCase):
    def test_gap(self):
        self.assertEqual(verdict(21, 3), "CONTENT GAP")

    def test_watch(self):
        self.assertEqual(verdict(3.5, 0), "WATCH")

    def test_watch_needs_zero_clicks(self):
        self.assertEqual(verdict(2.0, 1), "EDIT CANDIDATE")

    def test_edit(self):
        self.assertEqual(verdict(12, 0), "EDIT CANDIDATE")


class TestAggregate(unittest.TestCase):
    def setUp(self):
        self.q = aggregate(ROWS)

    def test_weighted_position(self):
        self.assertAlmostEqual(
            self.q["how do i fix a leaking tap at home"]["position"], 8.0)

    def test_top_page_by_impressions(self):
        self.assertEqual(
            self.q["how do i fix a leaking tap at home"]["top_page"], "/a")

    def test_totals(self):
        q = self.q["how do i fix a leaking tap at home"]
        self.assertEqual((q["clicks"], q["impressions"]), (2, 150))


class TestFilters(unittest.TestCase):
    def setUp(self):
        self.q = aggregate(ROWS)

    def test_prompt_like(self):
        items = prompt_like(self.q)
        by_query = {i["query"]: i for i in items}
        self.assertIn("how do i fix a leaking tap at home", by_query)
        self.assertEqual(by_query["how do i fix a leaking tap at home"]
                         ["verdict"], "EDIT CANDIDATE")
        self.assertEqual(by_query["what is the best way to descale kettles"]
                         ["verdict"], "WATCH")
        self.assertEqual(
            by_query["why does my washing machine smell so bad lately"]
            ["verdict"], "CONTENT GAP")
        self.assertNotIn("how to descale kettle", by_query)
        self.assertNotIn(
            "a very long query that nobody really searches for ever",
            by_query)

    def test_proven_demand_includes_short_question(self):
        items = proven_demand(self.q)
        self.assertIn("how to descale kettle",
                      {i["query"] for i in items})


if __name__ == "__main__":
    unittest.main()
