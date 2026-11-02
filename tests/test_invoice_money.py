import unittest

from tools.invoice_money import InvoiceMoneyError, egp_to_piasters, piasters_to_egp


class InvoiceMoneyTests(unittest.TestCase):
    def test_exact_decimal_egp_conversion(self):
        self.assertEqual(egp_to_piasters("12"), 1200)
        self.assertEqual(egp_to_piasters("12.3"), 1230)
        self.assertEqual(egp_to_piasters("12.34"), 1234)
        self.assertEqual(piasters_to_egp(1234), "12.34")

    def test_rejects_float_and_invalid_decimal_forms(self):
        for value in (12.34, "1.234", "-1", "1e3", "01", "1,000", ""):
            with self.subTest(value=value), self.assertRaises(InvoiceMoneyError):
                egp_to_piasters(value)


if __name__ == "__main__":
    unittest.main()
