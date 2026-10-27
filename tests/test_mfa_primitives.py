import base64
import hashlib
import hmac
import struct
import unittest
from urllib.parse import parse_qs, urlparse

from tools.mfa_primitives import (
    MFAPrimitivesError, build_totp_uri, generate_recovery_codes,
    generate_totp_secret, hash_recovery_code, verify_recovery_code, verify_totp,
)


def totp_for(secret, timestamp):
    key = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
    step = int(timestamp) // 30
    digest = hmac.new(key, struct.pack(">Q", step), hashlib.sha1).digest()
    offset = digest[-1] & 15
    binary = struct.unpack(">I", digest[offset:offset + 4])[0] & 0x7fffffff
    return f"{binary % 1_000_000:06d}"


class MFAPrimitivesTests(unittest.TestCase):
    def test_secret_is_base32_and_uri_has_standard_totp_parameters(self):
        secret = generate_totp_secret()
        decoded = base64.b32decode(secret + "=" * ((8 - len(secret) % 8) % 8))
        self.assertEqual(len(decoded), 20)
        uri = build_totp_uri(secret, "lawyer@example.test")
        parsed = urlparse(uri)
        query = parse_qs(parsed.query)
        self.assertEqual(parsed.scheme, "otpauth")
        self.assertEqual(parsed.netloc, "totp")
        self.assertEqual(query["digits"], ["6"])
        self.assertEqual(query["period"], ["30"])
        self.assertEqual(query["algorithm"], ["SHA1"])

    def test_totp_matches_rfc6238_sha1_reference_vector(self):
        # RFC 6238's 20-byte SHA-1 secret, encoded as Base32; six-digit truncation of 94287082.
        secret = "GEZDGNBVGY3TQOJQGEZDGNBVGY3TQOJQ"
        self.assertEqual(verify_totp(secret, "287082", now=59, window=0), 1)

    def test_totp_accepts_current_step_and_rejects_replay_step(self):
        secret = generate_totp_secret()
        now = 1_800_000_000
        code = totp_for(secret, now)
        accepted_step = verify_totp(secret, code, now=now, window=0)
        self.assertEqual(accepted_step, now // 30)
        self.assertIsNone(verify_totp(secret, code, now=now, window=0,
                                      last_accepted_step=accepted_step))

    def test_totp_skew_window_and_bad_codes(self):
        secret = generate_totp_secret()
        now = 1_800_000_000
        prior_code = totp_for(secret, now - 30)
        self.assertEqual(verify_totp(secret, prior_code, now=now, window=1), now // 30 - 1)
        for code in ("", "123", "1234567", "12a456", " 12345 "):
            self.assertIsNone(verify_totp(secret, code, now=now))
        self.assertIsNone(verify_totp(secret, prior_code, now=now, window=0))

    def test_totp_rejects_bad_secret_and_bad_parameters(self):
        with self.assertRaises(MFAPrimitivesError):
            verify_totp("not base32!", "123456", now=100)
        with self.assertRaises(MFAPrimitivesError):
            verify_totp("MY", "123456", now=100)
        secret = generate_totp_secret()
        for window in (-1, 3, True):
            with self.subTest(window=window), self.assertRaises(MFAPrimitivesError):
                verify_totp(secret, "123456", now=100, window=window)
        for now in (-1, float("inf"), True, "100"):
            with self.subTest(now=now), self.assertRaises(MFAPrimitivesError):
                verify_totp(secret, "123456", now=now)

    def test_totp_uri_rejects_control_characters(self):
        secret = generate_totp_secret()
        with self.assertRaises(MFAPrimitivesError):
            build_totp_uri(secret, "lawyer\nBcc: bad@example.test")

    def test_recovery_codes_are_hashed_and_only_match_their_code(self):
        code = "A1B2C3D4E5"
        encoded = hash_recovery_code(code)
        self.assertNotIn(code, encoded)
        self.assertTrue(verify_recovery_code(code, encoded))
        self.assertTrue(verify_recovery_code("A1B2-C3D4-E5", encoded))
        self.assertFalse(verify_recovery_code("0000000000", encoded))
        self.assertFalse(verify_recovery_code(code, "not-a-hash"))

    def test_generated_recovery_codes_are_unique_and_hashes_match(self):
        result = generate_recovery_codes(8)
        self.assertEqual(len(result["codes"]), 8)
        self.assertEqual(len(set(result["codes"])), 8)
        self.assertEqual(len(result["hashes"]), 8)
        self.assertTrue(all(verify_recovery_code(code, encoded)
                            for code, encoded in zip(result["codes"], result["hashes"])))
        self.assertTrue(all(code not in encoded for code, encoded in zip(result["codes"], result["hashes"])))

    def test_recovery_code_generation_and_hash_validation(self):
        for count in (0, 21, True):
            with self.subTest(count=count), self.assertRaises(MFAPrimitivesError):
                generate_recovery_codes(count)
        with self.assertRaises(MFAPrimitivesError):
            hash_recovery_code("too-short")
        self.assertFalse(verify_recovery_code("bad", hash_recovery_code("A1B2C3D4E5")))
        self.assertFalse(verify_recovery_code("A1B2C3D4E5", "scrypt$999999999$8$1$bad$bad"))


if __name__ == "__main__":
    unittest.main()
