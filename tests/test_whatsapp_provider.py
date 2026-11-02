import unittest
from urllib.parse import parse_qs, urlsplit

from tools.whatsapp_provider import (
    FakeWhatsAppProvider, build_wa_me_url, normalize_international_phone,
)


class WhatsAppProviderTests(unittest.TestCase):
    def test_wa_me_link_normalizes_international_phone_and_encodes_message(self):
        url = build_wa_me_url("+20 10-1234-5678", "تذكير بموعد القضية")
        parsed = urlsplit(url)
        self.assertEqual(parsed.netloc, "wa.me")
        self.assertEqual(parsed.path, "/201012345678")
        self.assertEqual(parse_qs(parsed.query)["text"], ["تذكير بموعد القضية"])

    def test_rejects_local_or_invalid_phone_numbers(self):
        for phone in ("01012345678", "123", "1234567890123456", "", None):
            with self.subTest(phone=phone), self.assertRaises(ValueError):
                normalize_international_phone(phone)

    def test_fake_provider_records_without_network_access(self):
        provider = FakeWhatsAppProvider()
        result = provider.send_text("+20 10 1234 5678", "موعد غداً")
        self.assertEqual(result["status"], "accepted_by_fake_provider")
        self.assertEqual(provider.messages, [{
            "phone": "201012345678", "message": "موعد غداً",
        }])

    def test_rejects_empty_or_oversized_message(self):
        with self.assertRaises(ValueError):
            build_wa_me_url("+201012345678", " ")
        with self.assertRaises(ValueError):
            build_wa_me_url("+201012345678", "x" * 2001)


if __name__ == "__main__":
    unittest.main()
