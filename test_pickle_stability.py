import unittest
import pickle
import hashlib
import sys
import os


class TestPickleStability(unittest.TestCase):

    def get_pickle_hash(self, obj, protocol=pickle.HIGHEST_PROTOCOL) -> str:
        try:
            p_data = pickle.dumps(obj, protocol=protocol)
            return hashlib.sha256(p_data).hexdigest()
        except Exception as e:
            self.fail(f"Error: {e}")

    def test_equivalence_partitions(self):
        data_samples = [
            "Test String",
            42,
            [1, 2, 3, 4],
            {"key": "value", "status": True}
        ]
        for obj in data_samples:
            hash1 = self.get_pickle_hash(obj)
            hash2 = self.get_pickle_hash(obj)
            self.assertEqual(hash1, hash2)

    def test_boundary_values(self):
        boundary_samples = [
            0,
            sys.maxsize,
            -sys.maxsize - 1,
            "",
            [],
            {}
        ]
        for obj in boundary_samples:
            hash1 = self.get_pickle_hash(obj)
            hash2 = self.get_pickle_hash(obj)
            self.assertEqual(hash1, hash2)

    def test_recursive_structures(self):
        nested_json_like = {
            "id": 101,
            "metadata": {
                "tags": ["python", "pickle", "test"],
                "version": {"major": 3, "minor": 10}
            },
            "active": True
        }
        hash1 = self.get_pickle_hash(nested_json_like)
        hash2 = self.get_pickle_hash(nested_json_like)
        self.assertEqual(hash1, hash2)

    def test_environment_dump(self):
        sample_data = {"test_key": [1, 2, 3]}
        current_hash = self.get_pickle_hash(sample_data)
        output_file = "pickle_hashes_report.txt"
        with open(output_file, "a", encoding="utf-8") as f:
            f.write(
                f"OS: {sys.platform} | "
                f"Python: {sys.version.split()[0]} | "
                f"Hash: {current_hash}\n"
            )
        self.assertTrue(os.path.exists(output_file))


if __name__ == "__main__":
    unittest.main()
