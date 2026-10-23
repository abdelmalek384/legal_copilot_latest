# Date-aware benchmark: Criminal Procedure Law transition

These cases are designed to test whether Legal Copilot accounts for an amendment that changed the scheduled commencement of a new code.

## Primary references
- Law No. 160 of 2026, Amiri Press: https://alamiria.com/Sec/TashTxt?id=Aalg37zxdcU%3D
- Egyptian Parliament notice dated 30 September 2026: https://parliament.gov.eg/News_Show.aspx?frm=5874
- Ministry of Justice-hosted PDF of Law No. 174 of 2025: https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B

## Required product behavior
- Every legal query should be interpreted against an explicit or clearly stated `as_of` date.
- New enactment and commencement are separate facts.
- Amendment laws must supersede earlier commencement language for queries after the amendment takes effect.
- The system must cite the amending instrument, not merely the original code.
- The exact effect of postponed commencement on repeal and transition language is a separate legal interpretation. The benchmark intentionally expects caution on categorical statements about Law No. 150/1950 until the full texts and transition provisions have been reviewed by Egyptian counsel.
- All records remain `pending_lawyer_review`; they are not a lawyer-approved gold set.
