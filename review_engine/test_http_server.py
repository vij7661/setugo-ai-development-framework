from __future__ import annotations

import unittest

from review_engine.http_server import static_asset


class DashboardServingTests(unittest.TestCase):
    def test_dashboard_assets_are_allowlisted_and_loadable(self):
        index = static_asset("/")
        css = static_asset("/styles.css")
        js = static_asset("/app.js")
        self.assertIsNotNone(index)
        self.assertIsNotNone(css)
        self.assertIsNotNone(js)
        self.assertEqual(index[0], "text/html; charset=utf-8")
        self.assertEqual(css[0], "text/css; charset=utf-8")
        self.assertEqual(js[0], "text/javascript; charset=utf-8")
        self.assertIn(b'<script src="/app.js"></script>', index[1])
        self.assertIn(b'fetch(path', js[1])
        self.assertIn(b'Asia/Kolkata', js[1])

    def test_arbitrary_and_traversal_paths_are_not_served(self):
        self.assertIsNone(static_asset("/../configuration.py"))
        self.assertIsNone(static_asset("/review_engine/config.example.json"))
        self.assertIsNone(static_asset("/.git/config"))

    def test_frontend_does_not_embed_raw_credentials(self):
        for path in ("/", "/app.js", "/styles.css"):
            asset = static_asset(path)
            self.assertIsNotNone(asset)
            lowered = asset[1].lower()
            self.assertNotIn(b"bearer ", lowered)
            self.assertNotIn(b"api_key=", lowered)
            self.assertNotIn(b"apikey=", lowered)


if __name__ == "__main__":
    unittest.main()
