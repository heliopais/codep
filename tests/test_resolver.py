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
            os.path.join(self.test_dir, "repos", "benefits"),
            os.path.join(self.test_dir, "repos", "benefits", "benefits-model-training"),
            os.path.join(self.test_dir, "repos", "benefits", "benefits-compensation-partner"),
            os.path.join(self.test_dir, "repos", "exo", "exo-inference"),
            os.path.join(self.test_dir, "repos", "exo", "exo-training"),
            os.path.join(self.test_dir, "repos", "docs", "okrs-helio"),
            os.path.join(self.test_dir, "repos", "docs", "okrs-nandani"),
            os.path.join(self.test_dir, "Documents", "CW"),
            os.path.join(self.test_dir, "Documents", "hNotes"),
        ]
        for p in self.candidates:
            os.makedirs(p, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_multi_token_benefits_training(self):
        mode, paths = resolve(
            "benefits training",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("benefits-model-training"))

    def test_multi_token_exo_inference(self):
        mode, paths = resolve(
            "exo inference",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("exo-inference"))

    def test_multi_token_okrs_helio(self):
        mode, paths = resolve(
            "okrs helio",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "SINGLE")
        self.assertTrue(paths[0].endswith("okrs-helio"))

    def test_disambiguation_okrs(self):
        mode, paths = resolve(
            "okrs",
            candidate_override=self.candidates
        )
        self.assertEqual(mode, "MULTIPLE")
        self.assertGreaterEqual(len(paths), 2)

    def test_approximate_match_on_typos(self):
        mode, paths = resolve(
            "benifits train",
            candidate_override=self.candidates
        )
        # Should be APPROX or SINGLE pointing to benefits-model-training
        self.assertIn(mode, ("APPROX", "SINGLE"))
        best = paths[0]
        self.assertTrue("benefits-model-training" in best or "benefits" in best)

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
