"""Measured claim-support false-pass/false-block rates on fictional evidence only."""
import json
import unittest

from app import norm, tokens, _mask_markdown_code
from tools.claim_support import has_unsupported_claims


CASES = (
    # Supported: 12
    ("supported", "The limitation period is five years [1].", "The limitation period is five years."),
    ("supported", "The employee may request annual leave after six months [1].", "The employee may request annual leave after six months."),
    ("supported", "The employer must provide written notice [1].", "The employer must provide written notice."),
    ("supported", "The employer must not deduct wages [1].", "The employer must not deduct wages."),
    ("supported", "The employee is not required to submit the form [1].", "The employee is not required to submit the form."),
    ("supported", "مدة التقادم خمس سنوات [1].", "مدة التقادم خمس سنوات."),
    ("supported", "يجوز للعامل طلب الإجازة بعد ستة أشهر [1].", "يجوز للعامل طلب الإجازة بعد ستة أشهر."),
    ("supported", "يلتزم صاحب العمل بتقديم إخطار مكتوب [1].", "يلتزم صاحب العمل بتقديم إخطار مكتوب."),
    ("supported", "لا يجوز لصاحب العمل خصم الأجر [1].", "لا يجوز لصاحب العمل خصم الأجر."),
    ("supported", "لا يلتزم العامل بتقديم الطلب [1].", "لا يلتزم العامل بتقديم الطلب."),
    ("supported", "A tenant may request repairs after written notice [1].", "A tenant may request repairs after written notice."),
    ("supported", "تستحق الأسرة التعويض عند تحقق الضرر [1].", "تستحق الأسرة التعويض عند تحقق الضرر."),

    # Unsupported number: 12
    ("unsupported_number", "The limitation period is ten years [1].", "The limitation period is five years."),
    ("unsupported_number", "The employee may request leave after twelve months [1].", "The employee may request leave after six months."),
    ("unsupported_number", "The employer must give thirty days notice [1].", "The employer must give fifteen days notice."),
    ("unsupported_number", "A tenant must pay 900 pounds monthly [1].", "A tenant must pay 700 pounds monthly."),
    ("unsupported_number", "The fine is 50,000 pounds [1].", "The fine is 5,000 pounds."),
    ("unsupported_number", "مدة التقادم عشر سنوات [1].", "مدة التقادم خمس سنوات."),
    ("unsupported_number", "يجوز للعامل طلب الإجازة بعد اثني عشر شهرا [1].", "يجوز للعامل طلب الإجازة بعد ستة أشهر."),
    ("unsupported_number", "يلتزم صاحب العمل بإخطار العامل خلال ثلاثين يوما [1].", "يلتزم صاحب العمل بإخطار العامل خلال خمسة عشر يوما."),
    ("unsupported_number", "قيمة الغرامة عشرة آلاف جنيه [1].", "قيمة الغرامة خمسة آلاف جنيه."),
    ("unsupported_number", "تستحق الأسرة تعويضا قدره مائة ألف جنيه [1].", "تستحق الأسرة تعويضا قدره عشرة آلاف جنيه."),
    ("unsupported_number", "The appeal must be filed within ninety days [1].", "The appeal must be filed within thirty days."),
    ("unsupported_number", "The insurance contribution is 14 percent [1].", "The insurance contribution is 11 percent."),

    # Unsupported qualitative claim, including no-expiry claims: 12
    ("unsupported_qualitative", "The claim never expires [1].", "The limitation period is five years."),
    ("unsupported_qualitative", "The right does not expire [1].", "The right is subject to a three-year limitation period."),
    ("unsupported_qualitative", "There is no limitation period for this claim [1].", "The claim is subject to a five-year limitation period."),
    ("unsupported_qualitative", "The claim is permanent and can never lapse [1].", "The claim is subject to a five-year limitation period."),
    ("unsupported_qualitative", "الحق لا يتقادم أبدا [1].", "مدة التقادم خمس سنوات."),
    ("unsupported_qualitative", "الدعوى لا تسقط مطلقا [1].", "مدة سقوط الدعوى ثلاث سنوات."),
    ("unsupported_qualitative", "الحق لا ينقضي نهائيا [1].", "مدة التقادم خمس سنوات."),
    ("unsupported_qualitative", "لا توجد أي مدة للتقادم في هذه المطالبة [1].", "مدة التقادم خمس سنوات."),
    ("unsupported_qualitative", "The deadline never ends [1].", "The filing deadline is thirty days."),
    ("unsupported_qualitative", "The employer is always liable for every injury [1].", "The employer may be liable when negligence is established."),
    ("unsupported_qualitative", "All tenants are automatically entitled to renewal [1].", "A tenant may request renewal if rent is paid."),
    ("unsupported_qualitative", "كل عامل يستحق الإجازة فور تعيينه [1].", "يجوز للعامل طلب الإجازة بعد ستة أشهر."),

    # Reversed meaning / polarity: 12
    ("reversed_meaning", "The employee may not request leave [1].", "The employee may request leave."),
    ("reversed_meaning", "The employee must request leave [1].", "The employee may request leave."),
    ("reversed_meaning", "The employer may deduct wages [1].", "The employer must not deduct wages."),
    ("reversed_meaning", "The employee is not required to submit the form [1].", "The employee must submit the form."),
    ("reversed_meaning", "The employer must not provide written notice [1].", "The employer must provide written notice."),
    ("reversed_meaning", "يجوز للعامل طلب الإجازة [1].", "لا يجوز للعامل طلب الإجازة."),
    ("reversed_meaning", "يجب على العامل طلب الإجازة [1].", "يجوز للعامل طلب الإجازة."),
    ("reversed_meaning", "يجوز لصاحب العمل خصم الأجر [1].", "لا يجوز لصاحب العمل خصم الأجر."),
    ("reversed_meaning", "لا يلتزم صاحب العمل بتقديم إخطار [1].", "يلتزم صاحب العمل بتقديم إخطار."),
    ("reversed_meaning", "لا يحق للعامل طلب الإجازة [1].", "يحق للعامل طلب الإجازة."),
    ("reversed_meaning", "The employer is permitted to deduct wages [1].", "The employer is not permitted to deduct wages."),
    ("reversed_meaning", "The employee is obliged to submit the request [1].", "The employee is not obliged to submit the request."),

    # Over-generalization beyond a condition or limited class: 12
    ("over_generalization", "Every employee may request annual leave immediately [1].", "An employee may request annual leave after six months."),
    ("over_generalization", "All tenants may renew the lease automatically [1].", "A tenant may request renewal if rent is paid."),
    ("over_generalization", "The employer must compensate every worker in all cases [1].", "The employer must compensate workers if negligence is established."),
    ("over_generalization", "All employees must receive the benefit after one day [1].", "Employees must receive the benefit after three years of service."),
    ("over_generalization", "The employer must give notice in every situation [1].", "The employer must give notice only for dismissals for cause."),
    ("over_generalization", "A tenant may terminate the lease for any reason [1].", "A tenant may terminate the lease if the premises are unsafe."),
    ("over_generalization", "كل عامل يجوز له طلب الإجازة فورا [1].", "يجوز للعامل طلب الإجازة بعد ستة أشهر."),
    ("over_generalization", "يستحق جميع العمال المنحة فور التعيين [1].", "يستحق العامل المنحة بعد استيفاء شروط الخدمة."),
    ("over_generalization", "يلتزم صاحب العمل بالتعويض في كل الحالات [1].", "يلتزم صاحب العمل بالتعويض إذا ثبت الخطأ."),
    ("over_generalization", "يستحق كل عامل التعويض دائما [1].", "يستحق العامل التعويض إذا ثبت الخطأ."),
    ("over_generalization", "The rule applies in every case [1].", "The rule applies only when notice is served."),
    ("over_generalization", "يحق لكل مستأجر إنهاء العقد لأي سبب [1].", "يجوز للمستأجر إنهاء العقد إذا أصبح العقار غير صالح."),
)


class FictionalClaimSupportMeasurementTests(unittest.TestCase):
    def test_60_fictional_claims_report_false_pass_and_false_block_rates(self):
        self.assertEqual(len(CASES), 60)
        expected_counts = {
            "supported": 12,
            "unsupported_number": 12,
            "unsupported_qualitative": 12,
            "reversed_meaning": 12,
            "over_generalization": 12,
        }
        report = {}
        false_pass = 0
        false_block = 0
        unsupported_total = 0
        supported_total = 0

        for label, answer, evidence in CASES:
            blocked = has_unsupported_claims(
                answer, [{"text": evidence}], tokens, norm, _mask_markdown_code
            )
            expected_block = label != "supported"
            item = report.setdefault(label, {"n": 0, "blocked": 0, "passed": 0})
            item["n"] += 1
            item["blocked"] += int(blocked)
            item["passed"] += int(not blocked)

            if expected_block:
                unsupported_total += 1
                false_pass += int(not blocked)
            else:
                supported_total += 1
                false_block += int(blocked)

        for label, count in expected_counts.items():
            self.assertEqual(report[label]["n"], count)

        report["summary"] = {
            "total": len(CASES),
            "false_pass": false_pass,
            "unsupported_total": unsupported_total,
            "false_pass_rate": false_pass / unsupported_total,
            "false_block": false_block,
            "supported_total": supported_total,
            "false_block_rate": false_block / supported_total,
        }
        print("FICTIONAL_CLAIM_SUPPORT_BENCHMARK=" + json.dumps(report, ensure_ascii=False, sort_keys=True))
        self.assertEqual(false_pass, 0, "unsupported fictional claims passed the checker")


if __name__ == "__main__":
    unittest.main()
