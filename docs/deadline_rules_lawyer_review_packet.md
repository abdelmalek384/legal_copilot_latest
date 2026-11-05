# Draft deadline rules — Egyptian lawyer approval packet

**Status:** approval worksheet only. The source rules and holiday JSON files are unchanged. No rule is verified or approved for legal reliance.

## Draft rules to approve or correct

| Rule ID | Draft period | Current trigger assumption / uncertainty | Assumed source |
|---|---:|---|---|
| civil_commercial_appeal_40d | 40 days | Start depends on the judgment type and applicable service/announcement rule; exact trigger is not identified. | source_article=null; no primary citation supplied. |
| civil_cassation_60d | 60 days | Start depends on judgment type and procedural route; exact trigger is not identified. | source_article=null; no primary citation supplied. |
| misdemeanor_appeal_10d | 10 days | Start depends on the case/judgment status and service rules; exact trigger is not identified. | source_article=null; no primary citation supplied. |
| misdemeanor_opposition_3d | 3 days | Draft text refers to notification, but the precise valid notice event and exceptions need review. | source_article=null; no primary citation supplied. |
| administrative_annulment_60d | 60 days | Publication, notification or proven knowledge may be relevant; which event controls needs review. | source_article=null; no primary citation supplied. |

## Calculator assumptions (not legal conclusions)

- Day-count arithmetic currently excludes the trigger date and adds calendar days.
- The default weekend is Friday/Saturday; the calculator extends a result across configured non-working days, subject to its 31-day extension cap.
- An optional manually supplied distance-day adjustment can be added before non-working-day extension; its legal basis and value must be reviewed for each rule.
- The fixed draft holiday list contains: 7 January, 25 January, 25 April, 1 May, 30 June, 23 July and 6 October.
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
