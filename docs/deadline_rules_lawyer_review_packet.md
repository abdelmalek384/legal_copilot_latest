# Draft deadline rules — Egyptian lawyer approval packet

**Status:** approval worksheet only. The source rules and holiday JSON files are unchanged. No rule is verified or approved for legal reliance.

## Draft rules to approve or correct

| Rule ID | الاسم العربي | Draft period | Current start-event assumption (as stored) | Likely instrument to inspect (unverified) |
|---|---|---:|---|---|
| civil_commercial_appeal_40d | الاستئناف في المواد المدنية والتجارية | 40 days | تاريخ بدء الميعاد يحتاج إلى مراجعة محامٍ بحسب نوع الحكم | قانون المرافعات المدنية والتجارية رقم 13 لسنة 1968؛ exact article/paragraph not supplied; source_article=null; verified=false. |
| civil_cassation_60d | الطعن بالنقض | 60 days | تاريخ بدء الميعاد يحتاج إلى مراجعة محامٍ بحسب نوع الحكم | قانون المرافعات المدنية والتجارية رقم 13 لسنة 1968؛ exact article/paragraph not supplied; source_article=null; verified=false. |
| misdemeanor_appeal_10d | استئناف الحكم في الجنح | 10 days | تاريخ بدء الميعاد يحتاج إلى مراجعة محامٍ بحسب حالة الحكم | قانون الإجراءات الجنائية رقم 150 لسنة 1950؛ exact article/paragraph not supplied; source_article=null; verified=false. |
| misdemeanor_opposition_3d | المعارضة في الحكم الغيابي في الجنح | 3 days | تاريخ الإعلان وغيره من التفاصيل يحتاج إلى مراجعة محامٍ | قانون الإجراءات الجنائية رقم 150 لسنة 1950؛ exact article/paragraph not supplied; source_article=null; verified=false. |
| administrative_annulment_60d | دعوى إلغاء القرار الإداري | 60 days | نشر القرار أو إعلانه أو العلم به يحتاج إلى مراجعة محامٍ | قانون مجلس الدولة رقم 47 لسنة 1972 and applicable administrative-procedure rules; exact article/paragraph not supplied; source_article=null; verified=false. |



The instruments named above are only likely source families inferred from the draft rule type. They are not confirmed citations; counsel must confirm the governing statute, amendments, special-law overrides and exact article before approving any period.

## Calculator assumptions (not legal conclusions)

- Day-count arithmetic currently excludes the trigger date and adds calendar days.
- The default weekend is Friday/Saturday; the calculator extends a result across configured non-working days, subject to its 31-day extension cap.
- An optional manually supplied distance-day adjustment can be added before non-working-day extension; its legal basis and value must be reviewed for each rule.
- The fixed draft holiday list contains: 7 January (عيد الميلاد المجيد), 25 January (عيد الشرطة وثورة 25 يناير), 25 April (عيد تحرير سيناء), 1 May (عيد العمال), 30 June (ثورة 30 يونيو), 23 July (ثورة 23 يوليو) and 6 October (عيد القوات المسلحة).
- No dated movable holidays are listed. complete_years=[]; no year is certified as having a complete holiday calendar.
- Eid holidays, Coptic Easter-related closures, official holiday-transfer decisions, court-specific closures and judicial recess are not comprehensively represented.
- The prototype's month-end clamping, distance-day extension, trigger exclusion and weekend/holiday handling must each be approved for each rule, not assumed valid across all proceedings.

## Lawyer tick-sheet

For each rule, confirm or correct:
- [ ] Primary statute/procedural code and exact article/paragraph.
- [ ] Applicable court, case type and territorial/subject scope.
- [ ] Trigger event and evidence of service/publication/knowledge.
- [ ] Calendar-day vs working-day count; inclusion/exclusion of trigger day.
- [ ] Weekends, official holidays, transferred holidays and court-specific closures.
- [ ] Suspension, interruption, extensions, emergency provisions and exceptions.
- [ ] Whether the draft period is correct and current as of the review date.

## Holiday calendar approval

- [ ] Confirm each fixed date and whether courts close on that date.
- [ ] Supply official dated movable holidays for each year.
- [ ] Review official decisions transferring holidays.
- [ ] Identify court-specific calendars and judicial recess.
- [ ] Mark a year complete only after the entire year has been checked against official notices.

## Sign-off

Lawyer: ____________________  Role/qualification: ____________________  
Date: ____________________  Source/review evidence reference: ____________________  
Approved rule IDs (if any): ____________________  
Corrections and exceptions: __________________________________________

Do not set verified=true or change the draft rules until this signed review is completed through the authorized review process.
