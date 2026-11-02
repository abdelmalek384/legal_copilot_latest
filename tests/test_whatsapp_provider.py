import unittest

from tools.whatsapp_provider import (
    FakeWhatsAppProvider, WhatsAppProviderError, normalize_whatsapp_recipient,
)


class WhatsAppProviderTests(unittest.TestCase):
    def test_fake_provider_records_message_without_network_delivery(self):
        provider = FakeWhatsAppProvider()
        result = provider.send_text("01012345678", "موعد المكتب يوم 2026-11-05")
        self.assertEqual(result["status"], "accepted_by_fake_provider")
        self.assertEqual(provider.messages, [{
            "recipient": "+201012345678",
            "message": "موعد المكتب يوم 2026-11-05",
        }])

    def test_normalizes_international_and_egyptian_phone_formats(self):
        self.assertEqual(normalize_whatsapp_recipient("+20 10 1234 5678"), "+201012345678")
        self.assertEqual(normalize_whatsapp_recipient("00201012345678"), "+201012345678")

    def test_rejects_invalid_recipient_and_empty_or_oversized_message(self):
        provider = FakeWhatsAppProvider()
        with self.assertRaises(WhatsAppProviderError):
            provider.send_text("123", "Reminder")
        with self.assertRaises(WhatsAppProviderError):
            provider.send_text("+201012345678", " ")
        with self.assertRaises(WhatsAppProviderError):
            provider.send_text("+201012345678", "x" * 4097)


if __name__ == "__main__":
    unittest.main()
