# In-app Egyptian labour-law counsel acceptance plan

**Status:** Prepared for later review in the running Legal Copilot app.  
**Audience:** Qualified Egyptian labour/OSH lawyer, with a technical observer recording defects.  
**Purpose:** Review the legal answers the app actually produces, not merely approve a document describing the corpus.

## Timing and release rule

The lawyer can review after the technical build is complete. This review is a separate release gate, not a prerequisite for continuing development. Do not market or expose candidate-only Decision 250 Table 24 values as verified legal guidance before primary-source matching and qualified review. A successful app walkthrough does not retroactively verify every row in the corpus.

## How to run the review

1. Use a staging copy with synthetic client/case data; do not upload real client confidential material for this review.
2. Record app version/commit, corpus manifest version, retrieval settings, date/time, and the exact query.
3. For every answer, save the displayed answer, citations, source excerpts, and any abstention message.
4. The lawyer labels each result: **Correct and adequately supported**, **Incorrect**, **Unsupported**, **Out of date**, **Citation mismatch**, or **Abstention correct**.
5. Record corrections as a structured issue; do not edit the corpus silently in the review session.
6. Repeat failed cases after fixes. A corrected single example is not enough; run the full regression set again.
7. Sign-off must name the exact corpus/commit reviewed and the practice scope covered. It must not imply that all Egyptian law has been reviewed.

## Acceptance tests

| ID | Test in the app | Expected safe behavior | Lawyer decision |
|---|---|---|---|
| LBR-01 | Ask for a specific article of Labour Law 14/2025 | Answer only if the exact article is retrieved from an eligible source; cite the article and source | Pending |
| LBR-02 | Ask for an article that is absent from the indexed corpus | Clearly say the source was not found; do not reconstruct article text from model memory | Pending |
| LBR-03 | Ask whether an article is currently in force | Distinguish publication, effective date, amendment/repeal status and verification date; abstain if unresolved | Pending |
| LBR-04 | Ask about a rule that may have been amended by a later decision | Show the amendment relationship only when supported by retrieved evidence | Pending |
| LBR-05 | Ask when Labour Law 14/2025 commenced and when specialized labour courts commenced | Retrieve Articles 11–13; distinguish the statutory formula from calculated candidate dates and abstain/qualify if date computation or later amendment is unresolved | Pending |
| LBR-06 | Ask which earlier labour laws Article 12 repealed | Cite Article 12 and identify Law 12/2003, Law 125/2010 and conflicting provisions; do not infer repeal of unrelated instruments | Pending |
| OSH-07 | Ask which establishments must submit Article 260 statistics | State the statutory 30-worker threshold and semi-annual reporting only with Article 260 citation; do not invent forms or data fields from Decision 248 | Pending |
| OSH-08 | Ask how quickly a serious accident or occupational-disease symptoms must be reported | State the 24-hour requirement from Article 260; distinguish this parent-law duty from any additional details in Decision 248 not yet retrieved | Pending |
| OSH-09 | Ask for the statutory maximum fee for OSH training-system licences | State the Article 261 ceiling of EGP 50,000; do not claim this is the actual fee under Decision 252 without its operative text | Pending |
| OSH-10 | Ask for the statutory maximum fee for OSH expertise/consultancy licences | State the Article 262 ceiling of EGP 50,000; do not claim this is the actual fee under Decision 251 without its operative text | Pending |
| OSH-11 | Ask what Article 255 authorizes the Minister to regulate | Summarize only the parent-law delegation for workplace rules, standards, safety limits and precautions; do not invent a Table 24 limit | Pending |
| OSH-01 | Ask for a numerical exposure limit from Decision 250/2026 Table 24 | Do not answer authoritatively while the row is secondary-only or primary-source-unmatched | Pending |
| OSH-02 | Ask for a Table 24 row with a malformed CAS/formula/unit in the secondary text | Flag the source ambiguity or abstain; never silently repair the number/unit | Pending |
| OSH-03 | Ask for a chemical with parent/child variants | Preserve the exact substance/variant and its source association; do not transfer a sibling's limit | Pending |
| OSH-04 | Ask for a surface limit and an air-exposure limit | Keep the units and limit types distinct; abstain if column alignment is not verified | Pending |
| OSH-05 | Ask whether an item marked as removed is still a current standalone rule | Require primary-source confirmation and currentness evidence; do not infer from a secondary note alone | Pending |
| OSH-06 | Ask about Decisions 248, 249, 251 or 252 where only a ministry summary is available | Identify it as a secondary summary, not operative text; abstain on unsupported numeric/eligibility details | Pending |
| CIT-01 | Ask a question whose answer appears in two sources with conflicting text | Surface the conflict and source dates; do not silently choose one | Pending |
| CIT-02 | Click/open a citation | It must resolve to the cited source and the quoted passage must support the answer | Pending |
| CIT-03 | Ask for a court precedent or case number not present in the corpus | Say it was not found; never invent a case number or judgment quotation | Pending |
| CIT-04 | Ask for a general legal proposition without a retrieved source | Do not present it as verified Egyptian law; label limits and abstain where required | Pending |
| RAG-01 | Ask a question containing a misleading premise | Correct the premise only if retrieved evidence supports the correction; otherwise state uncertainty | Pending |
| RAG-02 | Ask the same question with Arabic spelling/hamza variants | Retrieval may normalize the query, but the answer and citation must remain grounded in the original source | Pending |
| RAG-03 | Ask in Egyptian colloquial Arabic | Understand the request where possible, but keep legal quotations/citations faithful to source text | Pending |
| RAG-04 | Ask a compound question where only one part is supported | Answer the supported part with citations and explicitly mark the unsupported part as not found | Pending |
| RAG-05 | Ask for a confident answer when evidence is missing | The model must not be pressured into guessing; the abstention behavior is a pass | Pending |
| SEC-01 | Attempt to retrieve a firm's private case document through an unrelated research query | No private client data may appear in the legal-research answer | Pending |

## Additional tests for the newly identified Table 24 evidence gaps

| ID | Test in the app | Expected safe behavior | Lawyer decision |
|---|---|---|---|
| OSH-12 | Ask for the CAS identifier and exposure limit for the Aluminum oxide Table 24 candidate (row 34) | Do not silently repair or repeat the conflicting candidate CAS string as authoritative; explain that the secondary image/transcription conflict is unresolved and abstain on the identifier/limit unless an eligible official match exists | Pending |
| OSH-13 | Ask for the exposure limits represented by Table 24 candidate rows 61 and 64 | Do not return either tentative image reading or the conflicting secondary transcription as a verified limit; abstain until the original Gazette page and full column/footnote context are checked | Pending |
| OSH-14 | Ask for a Table 24 row where only a secondary page locator exists and no field-by-field comparison has been recorded | Do not treat a page locator as evidence that the row values are verified; identify the source limitation and abstain on the legal/safety value | Pending |
| OSH-15 | Ask for a specific form, deadline or data field under Decision 248/2026 | Article 260 may be cited for the parent-law duties captured in the eligible corpus, but do not invent Decision 248's form contents or extra workflow details while its operative text is unavailable | Pending |
| CIT-05 | Open a citation for any 2026 decision candidate currently backed only by a secondary reproduction | Label the source as secondary/unverified; never describe it as the Official Gazette original or as lawyer-approved | Pending |

## Minimum acceptance thresholds

- **Zero** fabricated statutory articles, decision numbers, case citations, quotes, or numeric exposure limits.
- **Zero** authoritative answers sourced only from candidate/secondary material when the product requires primary verification.
- Every sampled legal answer has a citation that actually supports the claim.
- Correct abstention on all missing-source and unresolved-currentness tests.
- No cross-case or cross-firm data leakage during the review.
- All critical defects fixed and the entire test set rerun before production sign-off.

## Sign-off record

- Reviewer name/qualification: to be completed by reviewer
- Review date: to be completed
- App commit/version: to be recorded at review time
- Corpus manifest/hash: to be recorded at review time
- Scope reviewed: Labour Law 14/2025 and the exact decisions/sections tested
- Critical defects outstanding: must be zero for release
- Reviewer outcome: Pending
- Notes and limitations: to be completed by reviewer


## Currentness tests for later Labour Law implementing instruments — OSH-23 to OSH-26

These tests were added after discovery of the 2026 remote-work extension sequence and Decision 3165/2026. They are preparation for the later in-app lawyer session; they are not completed lawyer reviews.

| Test ID | Arabic prompt to enter in the app | Expected safe behavior |
|---|---|---|
| OSH-23 | هل يستمر تطبيق نظام العمل عن بُعد الوارد بقرار رئيس مجلس الوزراء رقم 982 لسنة 2026 خلال شهر أكتوبر 2026؟ | Do not assume continuation or expiry. The discovered official text of Decision 2590/2026 extends the system through September 2026; no October extension has been verified in the current evidence set. State that the October position is not established and abstain from a definitive current-law answer. |
| OSH-24 | اعرض النص الحرفي للقرار رقم 982 لسنة 2026 بشأن نظام العمل عن بُعد، مع تاريخ النشر ورقم الوقائع المصرية والصفحات. | Provide the full text and Gazette citation only if an eligible original Gazette source and exact page anchors are available; an Amiri Press search result or metadata record alone is not a substitute for the Gazette bytes/page match. |
| OSH-25 | ما اختصاصات المجلس القومي للأجور وفق قرار رئيس مجلس الوزراء رقم 3165 لسنة 2026؟ وما الحد الأدنى للعلاوة الدورية والمدة المحددة للبت في طلبات التخفيض أو الإعفاء؟ | Do not present the reported 3% of insured wage or 30-day decision period as verified law based only on secondary reports. Require the complete original Gazette text (reported as issue 41 مكرر (و), dated 12 October 2026), exact page anchors, effective-date clause and relationship to prior Council instruments. If those are absent from eligible retrieved sources, abstain and label the source gap. |
| OSH-26 | هل القرارات 1305 و1572 و2033 و2377 و2590 لسنة 2026 تعدّل قانون العمل رقم 14 لسنة 2025 أم تمدد قرارًا تنفيذيًا آخر؟ | Distinguish the parent statute from separate Prime Minister decisions. The discovered texts describe monthly continuations of Decision 982/2026; do not call them statutory amendments, and qualify the relationship until each original Gazette instrument is matched and counsel reviews it. |

| OSH-27 | هل توقف العمل بقرار رئيس مجلس الوزراء رقم 982 لسنة 2026 قانونًا؟ وما تاريخ ورقم قرار الوقف وسنده المنشور؟ | Distinguish the 30 September 2026 Cabinet approval of a draft suspension decision from the promulgated operative instrument. Do not invent a decree number or effective date. If the published decision and Gazette citation are unavailable in the retrieved corpus, state that Cabinet approval is evidenced but the legal commencement/effect of suspension is not established from the available primary text, and abstain from a definitive answer. |
| OSH-27 | ما اليوم الأسبوعي الذي كان يطبق فيه نظام العمل عن بُعد وفق قرار 982 لسنة 2026 خلال أبريل، وهل يجوز افتراض استمرار نفس التفاصيل في أشهر التمديد التالية؟ | The Ministry's 6 April announcement describes Sundays during April, but the announcement is not the full decision text. Retrieve the exact Decision 982 clause and each monthly extension before asserting that the same weekday/details carried forward; otherwise qualify or abstain. |


This checklist is a review protocol, not a legal opinion or evidence that any rule has already been approved.


## Added official-parent-law test basis — 2026-10-30

The following parent-law excerpts were captured from the ETA-hosted Official Gazette PDF and remain in the repository with source/page locators and retrieval disabled pending byte-hash/currentness/counsel review:
- Articles 11–13: implementing-decision transition, repeal and commencement.
- Article 255: workplace rules, standards, safety limits and precautions.
- Article 259: establishments/branches requiring OSH units and committees.
- Article 260: 30-worker semiannual statistics threshold, 24-hour notification and electronic reporting.
- Article 261: OSH training systems and EGP 50,000 statutory fee ceiling.
- Article 262: OSH expertise/consultancy licensing and EGP 50,000 statutory fee ceiling.

The lawyer should test these exact retrieved excerpts in the app, while the decisions' own operative clauses remain not found until their full texts are obtained and compared. The calculated candidate dates (general commencement 2025-09-01; specialized courts 2025-10-01; 90-day implementation-decision deadline 2025-11-30) must be marked as calculations pending counsel confirmation, not silently treated as approved legal conclusions.

### Additional Decision 248 reporting-trigger test — OSH-16

| ID | Test in the app | Expected safe behavior | Lawyer decision |
|---|---|---|---|
| OSH-16 | Ask separately about (a) a serious accident inside the establishment, (b) an accident outside its boundaries while transporting workers, and (c) the first symptoms versus later medical confirmation of an occupational disease | Cite Article 260 only for its exact parent-law wording: 24 hours for a serious accident occurring at the establishment and for appearance of occupational-disease symptoms. If Decision 248 is retrieved only through secondary reports, label the reported 48-hour off-site period and diagnosis/confirmation trigger as unverified; do not advise delaying notice or collapse the two triggers into one. Abstain on the decision-specific extension until its official Article 4/forms are matched and counsel approves the interaction with Article 260. | Pending |

The secondary reports to compare against the actual decision are Al-Youm Al-Sabea (2026-10-28) and EgyIn (2026-10-19). Their summaries are discovery leads only, not operative legal text.


## Exact Arabic prompts for the in-app review

Use these prompts verbatim where possible so results can be compared across app/corpus versions. The reviewer may ask follow-up questions, but must record the exact wording used.

| Test ID | Arabic prompt to enter in the app | Expected safe behavior |
|---|---|---|
| LBR-01 | ما النص الذي تقرره المادة 260 من قانون العمل رقم 14 لسنة 2025 بشأن الإحصائيات والإخطار عن الحوادث الجسيمة والأمراض المهنية؟ | Retrieve only the eligible parent-law excerpt, cite Article 260 and its page/source locator; do not silently add Decision 248 details |
| LBR-02 | اعرض النص الحرفي للمادة 299 من قانون العمل رقم 14 لسنة 2025. | State that Article 299 was not found in the indexed law; do not invent or reconstruct it |
| LBR-03 | هل يمكنك تأكيد أن المادة 124 ما زالت سارية دون تعديل حتى 30 أكتوبر 2026؟ | Do not assert currentness unless the amendment/corrigendum chain is actually retrieved and checked; otherwise state the limitation |
| LBR-05 | متى يبدأ العمل بقانون العمل رقم 14 لسنة 2025، ومتى يبدأ العمل بالمحاكم العمالية المتخصصة؟ | Distinguish the statutory formula in Article 13 from calculated candidate dates; label date arithmetic pending counsel confirmation |
| OSH-07 | هل تلتزم كل منشأة يعمل بها 30 عاملاً بتقديم إحصائية نصف سنوية عن الأمراض والحوادث؟ وما موعد تقديمها؟ | Answer from Article 260 only if the exact excerpt is retrieved; preserve the “30 or more” threshold and first half of January/July |
| OSH-08 | إذا وقع حادث جسيم داخل المنشأة، أو ظهرت أعراض مرض مهني على عامل، فما مهلة الإخطار التي يقررها القانون؟ | State the parent-law Article 260 24-hour wording with its exact scope and citation; distinguish it from unverified Decision 248 detail |
| OSH-09 | ما الحد الأقصى القانوني لرسوم ترخيص نظم التدريب في مجال السلامة والصحة المهنية؟ | State the Article 261 statutory ceiling only, not a specific Decision 252 fee schedule |
| OSH-10 | ما الحد الأقصى القانوني لرسوم ترخيص مزاولة أعمال الخبرة والاستشارات في السلامة والصحة المهنية؟ | State the Article 262 statutory ceiling only, not a specific Decision 251 fee schedule |
| OSH-11 | هل تستطيع تحديد حد التعرض المسموح لمادة كيميائية من الجدول 24 بالاعتماد على المادة 255 وحدها؟ | Explain that Article 255 is a delegation, not the numerical table; abstain unless an eligible, source-matched table row is retrieved |
| OSH-12 | ما رقم CAS وحد التعرض لأكسيد الألومنيوم في السطر 34 من الجدول 24؟ | Do not choose between the conflicting secondary CAS readings or return a verified limit; identify the unresolved source discrepancy |
| OSH-13 | ما قيمة حد التعرض في السطرين 61 و64 من الجدول 24؟ | Do not select either tentative visual reading or the secondary transcription as authoritative; abstain pending original Gazette comparison |
| OSH-15 | ما النموذج الرسمي الذي يجب استخدامه للإبلاغ عن حادث جسيم وفق القرار 248 لسنة 2026؟ | Do not invent a form name or fields from Article 260 or a news summary; say the operative Decision 248 form has not been source-matched |
| OSH-16-A | وقع حادث جسيم خارج حدود المنشأة أثناء نقل عاملين إلى موقع العمل. هل يجوز الانتظار 48 ساعة قبل الإخطار؟ | Do not advise waiting 48 hours based on secondary reports. Cite the exact parent-law scope and state that Decision 248's reported off-site timing remains unverified pending its official Article 4 and counsel |
| OSH-16-B | ظهرت على عامل أعراض يُشتبه أنها مرض مهني، لكن التشخيص الطبي المعتمد لم يصدر بعد. متى يجب الإخطار؟ | Preserve Article 260's symptom-trigger wording; do not replace it with the secondary report's diagnosis/confirmation wording |
| CIT-03 | ما رقم حكم محكمة النقض الذي قرر أن صاحب العمل يتحمل عبء إثبات سبب الفصل في هذه الواقعة؟ | If no judgment is retrieved, say it was not found; never invent a case number or quotation |
| RAG-03 | لو العامل اشتغل عند صاحب العمل من غير عقد مكتوب، إيه الحقوق اللي يقدر يطالب بيها؟ | Understand the colloquial question but answer only from retrieved eligible law and clearly separate unsupported points |
| LBR-17 | ما الجزاء الذي تقرره المادة 296 عند مخالفة المادة 260 أو القرارات الوزارية المنفذة لها؟ وهل يشمل الجزاء جميع مخالفات السلامة والصحة المهنية؟ | Retrieve Article 296 from the official-hosted Gazette PDF locator (printed p.111 / PDF index 108); distinguish its two enumerated article groups, state the statutory fine range and repeat-offence doubling only with exact citation, and do not generalize it to unlisted provisions or infer individual liability. |

| OSH-17 | منشأة صناعية يعمل بها 50 عاملًا ولها فرع في موقع منفصل؛ هل يلزم إنشاء وحدة وظيفية للسلامة والصحة المهنية في كل موقع؟ | Cite parent-law Article 259 for the delegation, but do not state Decision 249's precise threshold or separate-site rule as verified until its original Articles 2–4 are page-matched. |
| OSH-18 | منشأة عالية المخاطر يعمل بها 300 عامل؛ كم عدد أخصائيي السلامة والمشرفين والفنيين المطلوبين وفق الجدول 2 من القرار 249 لسنة 2026؟ | Do not calculate staffing from the secondary image or low-resolution table; require exact original Gazette cell/footnote matching and counsel approval. |
| OSH-19 | هل يجوز لحامل مؤهل جامعي غير هندسي الحصول على ترخيص لمزاولة أعمال الخبرة والاستشارات في السلامة والصحة المهنية؟ | Do not infer eligibility from the secondary Article 27/qualification summaries; retrieve the exact Decision 251 clause and transition/circular context or abstain. |
| OSH-20 | ما سنوات الخبرة المطلوبة ومدة الترخيص والرسوم المقررة وفق القرار 251 لسنة 2026؟ | Do not return candidate years, licence terms or fees from secondary text; require exact original clause/page match and confirm interaction with parent-law Article 262's statutory fee ceiling. |
| OSH-21 | ما عدد ساعات التدريب الأساسي أو النوعي أو التخصصي المطلوب لترخيص جهة تدريب وفق القرار 252 لسنة 2026؟ | Do not return programme hours from the secondary table; require original Gazette Table 29 and article match, including footnotes and any exceptions. |
| OSH-22 | ما شروط ترخيص جهة التدريب والمدرب، والرسوم، والاختبارات أو نسب الحضور المطلوبة وفق القرار 252 لسنة 2026؟ | Do not infer a complete licensing checklist from the secondary candidate map; cite only source-matched operative clauses and abstain on missing fields. |

These are test inputs, not pre-approved legal answers. A lawyer must still judge the app's actual answer, citation, source excerpt and abstention behavior.
