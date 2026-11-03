import asyncio
import json
import os
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("COPILOT_ENV", "development")

import app  # noqa: E402
from fastapi.exceptions import RequestValidationError  # noqa: E402


def run_handler(errors):
    exc = RequestValidationError(errors)
    response = asyncio.run(app.request_validation_handler(None, exc))
    return response.status_code, response.body.decode("utf-8")


class ValidationErrorHandlerTests(unittest.TestCase):
    def test_nan_and_infinity_inputs_produce_422_not_a_crash(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            status, body = run_handler([{
                "type": "int_type",
                "loc": ("body", "lines", 0, "unit_price_piasters"),
                "msg": "Input should be a valid integer",
                "input": bad,
            }])
            self.assertEqual(status, 422)
            json.loads(body, parse_constant=lambda c: self.fail(
                f"non-JSON constant {c} in response"
            ))

    def test_submitted_values_are_never_echoed(self):
        secret = "SuperSecret-Passw0rd-Value"
        status, body = run_handler([{
            "type": "value_error",
            "loc": ("body", "new_password"),
            "msg": "Value error, choose a less predictable password",
            "input": secret,
            "ctx": {"error": ValueError(secret)},
        }])
        self.assertEqual(status, 422)
        self.assertNotIn(secret, body)
        detail = json.loads(body)["detail"]
        self.assertEqual(set(detail[0]), {"type", "loc", "msg"})
        self.assertEqual(detail[0]["loc"], ["body", "new_password"])

    def test_message_that_interpolates_rejected_value_is_sanitized(self):
        secret = "private-client-name"
        status, body = run_handler([{
            "type": "value_error",
            "loc": ("body", "client"),
            "msg": f"Invalid client: {secret}",
            "input": secret,
        }])
        self.assertEqual(status, 422)
        self.assertNotIn(secret, body)
        self.assertEqual(json.loads(body)["detail"][0]["msg"], "Invalid value")

    def test_location_parts_stay_json_safe(self):
        status, body = run_handler([{
            "type": "missing",
            "loc": ("body", 3, object()),
            "msg": "Field required",
        }])
        self.assertEqual(status, 422)
        self.assertEqual(json.loads(body)["detail"][0]["loc"][:2], ["body", 3])


if __name__ == "__main__":
    unittest.main()
