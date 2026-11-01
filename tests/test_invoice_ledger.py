import unittest
from datetime import date, timedelta

from tools.invoice_ledger import (
    InvoiceLine,
    format_document_number,
    invoice_payment_status,
    invoice_total_piasters,
    outstanding_piasters,
    receivables_aging_bucket,
)


class IntegerPiasterInvoiceLedgerTests(unittest.TestCase):
    def test_line_and_invoice_totals_use_integer_minor_units(self):
        lines = [
            InvoiceLine("Consultation", 2, 12550),
            InvoiceLine("Court filing", 1, 5000),
        ]
        self.assertEqual(invoice_total_piasters(lines), 30100)

    def test_rejects_empty_lines_invalid_quantities_and_overflow(self):
        with self.assertRaises(ValueError):
            invoice_total_piasters([])
        for quantity in (0, -1):
            with self.assertRaises(ValueError):
                InvoiceLine("Work", quantity, 100).total_piasters()
        with self.assertRaises(TypeError):
            InvoiceLine("Work", True, 100).total_piasters()
        with self.assertRaises(ValueError):
            InvoiceLine("Work", 2, 9_000_000_000_000_000).total_piasters()

    def test_balance_and_payment_status(self):
        self.assertEqual(outstanding_piasters(10000, [2500, 1250]), 6250)
        self.assertEqual(invoice_payment_status(10000, []), "unpaid")
        self.assertEqual(invoice_payment_status(10000, [9999]), "partially_paid")
        self.assertEqual(invoice_payment_status(10000, [4000, 6000]), "paid")
        with self.assertRaises(ValueError):
            outstanding_piasters(10000, [10001])

    def test_aging_buckets_use_calendar_days(self):
        as_of = date(2026, 11, 2)
        self.assertEqual(receivables_aging_bucket(as_of.isoformat(), as_of.isoformat()), "current")
        self.assertEqual(receivables_aging_bucket((as_of-timedelta(days=30)).isoformat(), as_of.isoformat()), "1_30")
        self.assertEqual(receivables_aging_bucket((as_of-timedelta(days=31)).isoformat(), as_of.isoformat()), "31_60")
        self.assertEqual(receivables_aging_bucket((as_of-timedelta(days=61)).isoformat(), as_of.isoformat()), "61_plus")
        self.assertEqual(receivables_aging_bucket((as_of+timedelta(days=4)).isoformat(), as_of.isoformat()), "current")

    def test_invoice_and_receipt_number_formats(self):
        self.assertEqual(format_document_number("invoice", 2026, 1), "INV-2026-000001")
        self.assertEqual(format_document_number("receipt", 2026, 12), "RCT-2026-000012")
        with self.assertRaises(ValueError):
            format_document_number("credit_note", 2026, 1)
        with self.assertRaises(ValueError):
            format_document_number("invoice", 2026, 0)


if __name__ == "__main__":
    unittest.main()
