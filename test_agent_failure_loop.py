import unittest
from unittest.mock import patch

from requests import ReadTimeout

from agent_failure_loop import enrich_transaction


class AgentFailureLoopTest(unittest.TestCase):
    @patch("agent_failure_loop.infrai.capture")
    def test_capture_keeps_pipeline_exception(self, capture):
        def lookup(**_: object) -> dict[str, object]:
            raise ValueError("merchant response had no category")

        with self.assertRaises(ValueError):
            enrich_transaction("txn-7", lookup)
        capture.assert_called_once()
        self.assertEqual(capture.call_args.kwargs["fingerprint"], ["transaction-agent", "merchant-lookup"])

    @patch("agent_failure_loop.infrai.capture", side_effect=ReadTimeout("capture timed out"))
    def test_capture_failure_keeps_pipeline_exception(self, capture):
        def lookup(**_: object) -> dict[str, object]:
            raise ValueError("merchant response had no category")

        with self.assertRaisesRegex(ValueError, "merchant response had no category"):
            enrich_transaction("txn-7", lookup)
        capture.assert_called_once()


if __name__ == "__main__":
    unittest.main()
