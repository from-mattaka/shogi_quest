"""判定ロジックのテスト（エンジン・cshogi 不要）。 python -m unittest discover -s tests"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from analysis.evaluator import Score, Thresholds, classify, is_candidate, parse_info, to_mine  # noqa: E402

TH = Thresholds()


class WinrateTest(unittest.TestCase):
    def test_sigmoid(self):
        self.assertAlmostEqual(Score(cp=0).winrate(), 0.5)
        self.assertAlmostEqual(Score(cp=600).winrate(), 0.7310585786, places=6)
        self.assertEqual(Score(mate=3, mate_win=True).winrate(), 1.0)
        self.assertEqual(Score(mate=3, mate_win=False).winrate(), 0.0)
        self.assertEqual(Score.mated().winrate(), 0.0)

    def test_flip_and_perspective(self):
        self.assertEqual(Score(cp=120).flip(), Score(cp=-120))
        self.assertTrue(Score(mate=5, mate_win=True).flip().is_mate_loss)
        self.assertEqual(to_mine(Score(cp=200), "GOTE", "SENTE"), Score(cp=-200))
        self.assertEqual(to_mine(Score(cp=200), "SENTE", "SENTE"), Score(cp=200))

    def test_fmt(self):
        self.assertEqual(Score(cp=35).fmt(), "+35")
        self.assertEqual(Score(cp=-80).fmt(), "-80")
        self.assertEqual(Score(mate=5, mate_win=True).fmt(), "#+5")
        self.assertEqual(Score.mated().fmt(), "#-")


class ClassifyTest(unittest.TestCase):
    def test_categories(self):
        b = Score(cp=0)  # 50%
        self.assertEqual(classify(b, Score(cp=-1000), "a", "b", 600, TH), "大悪手")   # 50→15.9%
        self.assertEqual(classify(b, Score(cp=-300), "a", "b", 600, TH), "悪手")      # 50→37.8%
        self.assertEqual(classify(b, Score(cp=-150), "a", "b", 600, TH), "疑問手")    # 50→43.8%
        self.assertIsNone(classify(b, Score(cp=-50), "a", "b", 600, TH))

    def test_same_as_best_is_not_mistake(self):
        self.assertIsNone(classify(Score(cp=0), Score(cp=-1000), "a", "a", 600, TH))

    def test_missed_mate(self):
        self.assertEqual(classify(Score(mate=7, mate_win=True), Score(cp=3000), "a", "b", 600, TH), "詰み逃し")
        # 詰みを維持していれば詰み逃しではない
        self.assertIsNone(classify(Score(mate=7, mate_win=True), Score(mate=9, mate_win=True), "a", "b", 600, TH))

    def test_endgame_noise_is_small(self):
        # 勝勢で評価値が 3000→2000 に下がっても勝率はほぼ変わらない
        self.assertIsNone(classify(Score(cp=3000), Score(cp=2000), "a", "b", 600, TH))

    def test_candidate(self):
        self.assertTrue(is_candidate(Score(cp=0), Score(cp=-200), "a", "b", 600, TH))
        self.assertFalse(is_candidate(Score(cp=0), Score(cp=-200), "a", "a", 600, TH))
        self.assertTrue(is_candidate(Score(mate=3, mate_win=True), Score(cp=900), "a", "b", 600, TH))

    def test_thresholds_validation(self):
        with self.assertRaises(ValueError):
            Thresholds.from_config({"dubious": 0.2, "mistake": 0.1})


class ParseInfoTest(unittest.TestCase):
    def test_cp(self):
        pl, bound = parse_info("info depth 12 seldepth 18 score cp -35 multipv 2 nodes 1 nps 1 time 1 pv 7g7f 3c3d 2g2f")
        self.assertEqual((pl.multipv, pl.score, pl.pv, bound), (2, Score(cp=-35), ["7g7f", "3c3d", "2g2f"], False))

    def test_mate_and_bound(self):
        pl, bound = parse_info("info depth 20 score mate -5 lowerbound pv 5e5d")
        self.assertTrue(pl.score.is_mate_loss)
        self.assertEqual(pl.score.mate, 5)
        self.assertTrue(bound)
        pl, _ = parse_info("info depth 3 score mate + pv 1a1b")
        self.assertTrue(pl.score.is_mate_win)

    def test_ignored(self):
        self.assertIsNone(parse_info("info string EvalDirectory = eval"))
        self.assertIsNone(parse_info("info depth 1 nodes 100"))


if __name__ == "__main__":
    unittest.main()
