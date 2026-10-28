#!/usr/bin/env python3
"""
Unit tests for codep resolver
"""

import os
import sys
import unittest
import tempfile
import shutil

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))
from resolver import resolve, score_candidate, load_config, to_user_path

class TestCodepResolver(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        # Create simulated directory hierarchy
        self.candidates = [
            os.path.join(self.test_dir, "repos", "api"),
            os.path.join(self.test_dir, "repos", "api", "api-backend-v2"),
            os.path.join(self.test_dir, "repos", "api", "api-client-sdk"),
            os.path.join(self.test_dir, "repos", "web", "web-frontend"),
            os.path.join(self.test_dir, "repos", "web", "web-dashboard"),
            os.path.join(self.test_dir, "repos", "docs", "docs-internal"),
            os.path.join(self.test_dir, "repos", "docs", "docs-public"),
            os.path.join(self.test_dir, "Documents", "Projects"),
            os.path.join(self.test_dir, "Documents", "Notes"),
        ]
        for p in self.candidates:
            os.makedirs(p, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_multi_token_api_backend(self):
        mode, paths = resolve(
            "api backend",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("api-backend-v2"))

    def test_multi_token_web_frontend(self):
        mode, paths = resolve(
            "web frontend",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("web-frontend"))

    def test_multi_token_docs_internal(self):
        mode, paths = resolve(
            "docs internal",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("docs-internal"))

    def test_disambiguation_docs(self):
        mode, paths = resolve(
            "docs",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "MULTIPLE")
        self.assertGreaterEqual(len(paths), 2)

    def test_approximate_match_on_typos(self):
        mode, paths = resolve(
            "bakcend api",
            candidate_override=self.candidates
        )
        self.assertIn(mode, ("APPROX", "SINGLE"))
        best = paths[0]
        self.assertTrue("api-backend" in best or "api" in best)

    def test_direct_path(self):
        mode, paths = resolve(self.test_dir)
        self.assertEqual(mode, "SINGLE")
        self.assertEqual(paths[0], os.path.abspath(self.test_dir))

    def test_empty_query(self):
        mode, paths = resolve("   ", candidate_override=self.candidates)
        self.assertEqual(mode, "NONE")
        self.assertEqual(paths, [])

    def test_to_user_path(self):
        home = os.path.expanduser("~")
        sample = os.path.join(home, "repos", "myproject")
        self.assertEqual(to_user_path(sample), "~/repos/myproject")

if __name__ == "__main__":
    unittest.main()
