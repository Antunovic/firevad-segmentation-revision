from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from reference_segments import Reference, ReferenceAnnotations, compare


def reference(starts, length=500):
    return Reference(tuple(zip([0, *starts], [s - 1 for s in starts] + [length - 1])))


class ComparisonTests(unittest.TestCase):
    def test_inclusive_tolerance(self):
        original = reference([100, 200])
        self.assertFalse(compare(original, reference([90, 210])).needs_revision)
        self.assertTrue(compare(original, reference([100, 211])).needs_revision)
        self.assertTrue(compare(original, reference([89, 200])).needs_revision)
        self.assertFalse(compare(reference([]), reference([])).needs_revision)

    def test_count_disagreements(self):
        original = reference([100, 200])
        self.assertIn("Segment counts differ", compare(original, reference([100])).issues)
        self.assertIn("Reference frame counts differ",
                      compare(original, reference([100, 200], length=499)).issues)
        self.assertIn("RGB/IR frame counts differ", compare(original, original, 500, 499).issues)
        self.assertIn("Dataset length differs from reference",
                      compare(original, original, 400, 400).issues)

    def test_missing_is_not_agreement(self):
        original = reference([100, 200])
        self.assertEqual(compare(original, None).status, "Reference missing")
        self.assertEqual(compare(None, None).status, "No references")

    def test_malformed_annotation_is_not_silently_accepted(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "Antonio/environment_1/1.json"
            path.parent.mkdir(parents=True)
            path.write_text('{"environment": 1, "video_id": 1, "segments": []}', encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no segments"):
                ReferenceAnnotations(tmp)

    def test_bundle_matches_comparison_report(self):
        refs = ReferenceAnnotations(Path(__file__).parent / "reference_annotations")
        antonio, mislav = refs.by_annotator
        self.assertEqual(len(antonio), 183)
        self.assertEqual(antonio.keys(), mislav.keys())
        # Scene IDs independently counted from the original annotators' files.
        expected = {
            1: [7, 8, 21, 29],
            2: [2, 3, 4, 10, 12, 13, 14, 17],
            3: [2, 3, 6],
            4: [6, 20],
            5: [3, 4, 5, 13],
            6: [15, 34],
        }
        self.assertEqual({key for key in antonio if refs.for_scene(*key).needs_revision},
                         {(env, vid) for env, vids in expected.items() for vid in vids})


if __name__ == "__main__":
    unittest.main()
