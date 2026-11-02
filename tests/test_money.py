import unittest

from tools.money import egp_to_piasters, piasters_to_egp, require_piasters


class PiasterMoneyTests(unittest.TestCase):
    def test_decimal_strings_convert_without_float_arithmetic(self):
        self.assertEqual(egp_to_piasters("125.75"), 12575)
        self.assertEqual(egp_to_piasters("0.5"), 50)
        self.assertEqual(egp_to_piasters("7"), 700)

    def test_grouped_and_arabic_indic_input(self):
        self.assertEqual(egp_to_piasters("1,234.56"), 123456)
        self.assertEqual(egp_to_piasters("١٢٣٫٤٥".replace("٫", ".")), 12345)

    def test_round_trip_format_is_fixed_two_decimals(self):
        self.assertEqual(piasters_to_egp(0), "0.00")
        self.assertEqual(piasters_to_egp(10005), "100.05")
        self.assertEqual(egp_to_piasters(piasters_to_egp(987654)), 987654)

    def test_rejects_float_bool_negative_and_excess_precision(self):
        for value in (12.5, True, None):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    egp_to_piasters(value)
        for value in ("-1.00", "1.001", "1,23.00", ""):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    egp_to_piasters(value)

    def test_integer_piaster_contract(self):
        self.assertEqual(require_piasters(1), 1)
        for value in (1.0, True, "100"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    require_piasters(value)
        with self.assertRaises(ValueError):
            require_piasters(-1)


if __name__ == "__main__":
    unittest.main()
