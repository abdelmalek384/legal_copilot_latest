# Agent 3 — FRA leasing/factoring licensing text expansion (18 November 2026)

**Repository:** `abdelmalek384/legal_copilot_latest`  
**Scope:** Egyptian commercial, corporate and investment law — non-bank financial regulation.  
**Status:** incremental text capture; source-matched, not lawyer-reviewed.

## Deduplication and baseline

The latest Agent 3-specific checkpoint inspected before this pass is `agent3_progress_checkpoint_2026-11-18_31.md`: 245 unique instruments and at least 2,281 fully normalized provision/contract/circular units, plus 1 partial and 3 identified provisions outstanding; 55% assigned-domain planning estimate; 13/13 families touched; 0/13 currentness-complete; lawyer review 0%.

The existing record already contains Decision 137/2018 Articles 1–5 and its 2023 amendment lead. This file does not recount the instrument or those earlier articles. It adds the remaining substantive Articles 6–16 from the FRA-hosted consolidated text, plus the three issuing articles of Decision 91/2023 and the replacement wording for Article 4(2). These are 14 additional provision-level text units, subject to final normalization against the existing extraction.

## Primary source and Gazette provenance

- Issuer: Financial Regulatory Authority (FRA), Egypt.
- Instrument: FRA Board Decision 137/2018 dated 13 September 2018, licensing and continued-licensing controls for financial-leasing and factoring companies.
- Official current consolidated PDF: https://fra.gov.eg/wp-content/uploads/2023/05/قرار-91-2023-بتعديل-قرار-137-2018.pdf
- Official FRA landing page: https://fra.gov.eg/en/regulations/قرار-رقم-137-لعام-2018-2/
- Consolidation cover states updated through 12 April 2023.
- Amendment overlay: FRA Board Decision 91/2023 dated 12 April 2023; Egyptian Proceedings issue 91 supplement (أ), 19 April 2023.
- Decision 91/2023 Article 3 states commencement on the day after publication.
- The consolidated PDF itself includes the amending instrument and the current consolidated decision in one file. It is a regulator-hosted consolidation, not a separately acquired original Gazette binary for the 2018 base decision.
- Searchable PDF text was read at 377 extracted lines. The file is suitable for text extraction; page-image validation and SHA-256 archival are still required.

## New Arabic text captured

### Decision 91/2023 — issuing Articles 1–3

**Issuing Article 1 (replacement of Decision 137/2018 Article 4(2)):**

> يستبدل بنص البند (٢) من المادة الرابعة من قرار مجلس إدارة الهيئة رقم (١٣٧) لسنة ٢٠١٨ المشار إليه، النص الآتي:
> (المادة الرابعة – البند "٣"):
> ٢- ألا يقل رأس مال الشركة المصدر والمدفوع عن خمسة وسبعين مليون جنيه نقداً أو ما يعادلها بالعملات الأجنبية بسعر الصرف الصادر عن البنك المركزي المصري.

**Issuing Article 2 (regularisation period):**

> تلتزم الشركات المرخص لها بمزاولة نشاط التأجير التمويلي أو التخصيم بتوفيق أوضاعها وفقاً لأحكام هذا القرار خلال مدة لا تجاوز عام من تاريخ العمل به، ويجوز لمجلس إدارة الهيئة مد هذه المهلة لمدة لا تجاوز عامين في ضوء المبررات الجدية التي تقدمها الشركة.

**Issuing Article 3 (publication/commencement):**

> ينشر هذا القرار في الوقائع المصرية، وعلى الموقع الإلكتروني للهيئة، ويعمل به من اليوم التالي لتاريخ نشره بالوقائع المصرية.

### Decision 137/2018 — Articles 6–16

**Article 6 — preliminary approval to add an activity:**

> تلتزم الجهات المرخص لها بمزاولة أحد الأنشطة التمويلية (التمويل العقاري، التأجير التمويلي، التخصيم) عند الجمع بين أحد هذه الأنشطة أن تتقدم بطلب من الممثل القانوني للشركة للحصول على الموافقة المبدئية لإضافة النشاط، على أن يكون متضمناً رؤية الشركة وخطتها حال إضافة أحد هذه الأنشطة أو جميعها.
>
> كما تلتزم الجهات المرخص لها بمزاولة نشاط التمويل متناهي الصغر عند إضافة نشاط التأجير التمويلي متناهي الصغر، أن تتقدم للهيئة بطلب من الممثل القانوني للجهة للحصول على الموافقة المبدئية لمزاولة النشاط، على أن يكون متضمناً رؤية الجهة وخطتها حال النشاط.

**Article 7 — multiple financing activities:**

> يجب أن يتوافر في الشركات الراغبة في الحصول على ترخيص بمزاولة أكثر من نشاط تمويلي الالتزام بشروط التأسيس والترخيص الواجب توافرها للأنشطة المطلوب الترخيص بها بالإضافة إلى الشروط الآتية:
>
> ١. أن يكون غرض الشركة مزاولة كل أو بعض أنشطة التأجير التمويلي، التمويل العقاري، التخصيم، وألا يتضمن أي أنشطة أخرى.
> ٢. ألا يقل رأس مال الشركة عن الحد الأدنى للأنشطة المراد مزاولتها مجتمعة.
> ٣. ألا يقل عدد أعضاء مجلس إدارة الشركة عن خمسة أعضاء، وأن يتضمن تشكيل مجلس الإدارة عضوين على الأقل من المستقلين.
> ٤. أن يتوافر في رئيس وغالبية أعضاء مجلس الإدارة خبرة عملية في أحد مجالات العمل المصرفي أو التمويلي أو المالي غير المصرفي أو المالي أو القانوني لا تقل عن خمس سنوات بعد الحصول على مؤهل عال في ذات المجال.
> ٥. أن يكون لكل نشاط إدارة مستقلة لإدارة عمليات النشاط وشئون العملاء وأن يكون لكل مدير تنفيذي متفرغ على أن يتوافر لديه خبرة عملية في أحد مجالات العمل المصرفي أو التمويلي أو المالي أو القانوني لا تقل عن عشر سنوات بعد الحصول على مؤهل عال مناسب، ويجوز أن يكون العضو المنتدب أو المدير التنفيذي هو المشرف على أحد الأنشطة التمويلية.
> ٦. أن يكون للشركة مراقبان للحسابات من بين المقيدين لدى الهيئة.
> ٧. تقديم دراسة جدوى تتضمن خطة عمل الشركة ورؤيتها المستقبلية.

**Article 8 — documents for multiple activities:**

> يقوم طلب الترخيص على النموذج المعد لهذا الغرض مرفقاً به المستندات المطلوبة للترخيص للأنشطة التمويلية المطلوب مزاولتها بالإضافة إلى المستندات الآتية:
>
> ١. الهيكل التنظيمي للشركة موضحاً به آلية مزاولة كل نشاط من الأنشطة التمويلية المطلوب مزاولتها.
> ٢. صورة من شهادة المؤهل العلمي وشهادات الخبرة العملية للمديرين التنفيذيين للأنشطة التمويلية المطلوب مزاولتها.
> ٣. دراسة الجدوى تتضمن خطة الشركة ورؤيتها واستراتيجيتها في مزاولة الأنشطة التمويلية المطلوب مزاولتها مجتمعة.
> ٤. إيصال سداد مقابل خدمة دراسة طلب الحصول على الموافقة لإضافة نشاط تمويلي أو الترخيص بأكثر من نشاط تمويلي.

**Article 9 — microfinance entities adding micro-leasing:**

> يجب أن يتوافر في الشركات والجمعيات والمؤسسات الأهلية العامة والمرخص لها بمزاولة نشاط التمويل متناهي الصغر الراغبة في مزاولة نشاط التأجير التمويلي الالتزام بالشروط الآتية:
>
> ١. ألا تقل قيمة محفظة التمويل متناهي الصغر للشركة أو الجمعية أو المؤسسة الأهلية من واقع آخر قوائم مالية معتمدة عن خمسة ملايين جنيه.
> ٢. ألا تزيد قيمة الحد الأقصى لعقود التمويل وأغراض التمويل عن الحد الوارد بالقانون رقم ١٤١ لسنة ٢٠١٤.
> ٣. ألا تكون الشركة أو الجمعية أو المؤسسة العاملة في مجال العمل الأهلي قد ارتكبت أي مخالفة للقانون ١٤١ لسنة ٢٠١٤ أو القرارات الصادرة تنفيذاً له ولم يصدر ضدها أية جزاءات إدارية أو تدابير احترازية (عدا التنبيه والإنذار) من الهيئة خلال السنوات الثلاث السابقة على طلب إضافة النشاط ما لم تكن قد أزيلت أسبابها ومرت ستة أشهر على تلك الإزالة.
> ٤. أن تقدم الشركة أو الجمعية أو المؤسسة العاملة في مجال العمل الأهلي خطة عمل تتضمن آليات مزاولة نشاط التأجير التمويلي متناهي الصغر بالإضافة إلى نشاطها.
> ٥. أن يتوافر في العضو المنتدب أو رئيس الجمعية أو المؤسسة الأهلية والمديرين المسؤولين خبرة عملية في أحد مجالات العمل المالي أو التمويلية أو القانوني لا تقل عن سبع سنوات بعد الحصول على مؤهل عال في أحد المجالات ذات العلاقة.

**Article 10 — application documents for micro-leasing:**

> يقدم طلب الترخيص على النموذج المعد لهذا الغرض مرفقًا به المستندات الآتية:
>
> ١. صورة من آخر قوائم مالية معتمدة للجهة التي تمارس نشاط التمويل متناهي الصغر.
> ٢. صورة من ترخيص مزاولة نشاط التمويل متناهي الصغر.
> ٣. خطة عمل الجهة ورؤيتها واستراتيجيتها بعد إضافة النشاط.
> ٤. إقرار من الممثل القانوني للجهة بالالتزام بعدم تجاوز قيمة عقود التأجير التمويلي متناهي الصغر لقيمة الحد الأقصى لعقود التمويل المقررة وفقاً لأغراض التمويل المحددة بالقانون ١٤١ لسنة ٢٠١٤.
> ٥. صورة من شهادة المؤهل العلمي وبيان الخبرة العملية الخاصة بكل من العضو المنتدب للشركة أو رئيس الجمعية أو المؤسسة الأهلية والمديرين المسؤولين.
> ٦. إيصال سداد مقابل خدمة دراسة طلب الحصول على الموافقة على إضافة نشاط التأجير التمويلي.

**Article 11 — decision timetable:**

> تقوم الهيئة بإعطاء طالب الترخيص شهادة باستلام المستندات المقدمة منه أو بيان بما يلزم تقديمه من مستندات أخرى، وعليه استيفاء هذه المستندات خلال الثلاثة أشهر التالية وإلا سقط طلبه.
>
> وتقوم الهيئة بالبت في طلب الترخيص وإخطار الطالب كتابة بقرارها في شأنه، وذلك خلال ثلاثين يوماً من تاريخ استيفاء الشركة لكافة المتطلبات والشروط الواردة بهذا القرار.
>
> وفي حالة رفض طلب الترخيص تقوم الهيئة بإخطار مقدم الطلب بأسباب الرفض.

**Article 12 — fees and service charges (as printed in the 2023 consolidated text):**

> يسدد رسم الترخيص بمزاولة النشاط للشركة قيمة مائة ألف جنيه.
>
> يسدد مقابل خدمة فحص ودراسة طلب الحصول على الموافقة المبدئية للتأسيس بقيمة عشرة آلاف جنيه.
>
> يسدد مقابل خدمة فحص ودراسة طلب إضافة نشاط أو الترخيص بأكثر من نشاط تمويلي بقيمة عشرة آلاف جنيه.
>
> يسدد مقابل خدمة فحص ودراسة طلب نقل ملكية أسهم الشركة بقيمة خمسة وعشرون ألف جنيه.
>
> يتم سداد الرسوم ومقابل الخدمات السابق الإشارة إليها من خلال أحد حسابات الهيئة البنكية المحددة لهذا الغرض.

**Article 13 — independent director:**

> عضو مجلس الإدارة المستقل هو عضو مجلس الإدارة غير التنفيذي من غير مساهمي الشركة والذي لا تربط بينه وبين الشركة وشركاتها القابضة أو شركاتها التابعة أو الشقيقة وأيًّا من الأطراف ذات العلاقة بها، أي رابطة عمل أو علاقة تعاقدية أو عضوية مجلس إدارة، أيًّا منها خلال الثلاث سنوات السابقة على تعيينه، وليس زوجًا أو من أقارب الدرجة الثانية لأي من هؤلاء.

**Article 14 — regularisation requirements:**

> تلتزم شركات التأجير التمويلي والتخصيم القائمة في تاريخ العمل بأحكام هذا القرار بتوفيق أوضاعها وفقًا لأحكامه خلال ستة أشهر من تاريخ صدور قانون التأجير التمويلي والتخصيم رقم ١٧٦ لسنة ٢٠١٨ والأحكام الصادرة بقرارات مجلس إدارة الهيئة وذلك لكل من الآتي:
>
> – الشكل القانوني للشركة.
> – رأس المال المصدر والمدفوع.
> – اقتصار غرض الشركة على الأنشطة التمويلية غير المصرفية.
> – هيكل ملكية الشركة ونسبة مساهمة المؤسسات المالية والأشخاص الاعتبارية.
> – تشكيل مجلس إدارة الشركة وتوافر المؤهلات والخبرات اللازمة.
> – المؤهلات والخبرات اللازم توافرها في كل من العضو المنتدب أو المدير التنفيذي ومديري الإدارات بالشركة (المالية – الائتمان – المخاطر – المراجعة الداخلية – الفروع).

**Article 15 — application of Decision 53/2018:**

> تلتزم الشركات الراغبة في الحصول على الترخيص والشركات القائمة عند توفيق أوضاعها بالأحكام الواردة بقرار مجلس الإدارة رقم (٥٣) لسنة ٢٠١٨ بشأن ضوابط منح الترخيص واستمراره وقواعد تملك أسهم الشركات العاملة في الأنشطة المالية غير المصرفية.

**Article 16 — publication and commencement:**

> ينشر هذا القرار في الوقائع المصرية وعلى الموقع الالكتروني للهيئة، ويعمل بهذا القرار من اليوم التالي لتاريخ نشره بالوقائع المصرية.

## Text-derived regulatory findings (not legal advice)

- The 2023 amendment raises the minimum issued and paid-up capital in Decision 137/2018 Article 4(2) to EGP 75 million or foreign-currency equivalent at the CBE exchange rate.
- The amendment provides up to one year for regularisation, with FRA Board power to extend by up to two years for serious reasons.
- The consolidated text sets a three-month period to complete missing licensing documents and a 30-day FRA decision period after all requirements are satisfied.
- Multiple-activity firms have a combined capital requirement, at least five board members and at least two independent directors, plus separate operational management for each activity.
- Fees printed in the consolidated copy should be checked against later FRA fee schedules and amendments before operational use.

## Source rights and reliability

- Access: public regulator-hosted PDF and public regulator landing page.
- Source rights: no commercial republication or redistribution permission established; public access is not a licence.
- Text quality: searchable text extraction; no full Gazette page-image comparison or local file hash recorded in this pass.
- Legal status: consolidated as of 12 April 2023, not proven current through November 2026. Later amendments/fee schedules may exist.
- Trust label: `source-matched, not lawyer-reviewed`.
- No provision is marked `verified`.

## Next acquisition queue (distinct work only)

1. Retrieve and transcribe FRA Decision 138/2018 on financial statements and filing deadlines.
2. Retrieve and transcribe FRA Decision 139/2018 on the financial-leasing contract register; distinguish it from the non-binding FRA industry guide summary.
3. Reconcile Decisions 191/2018 and 192/2018 current consolidated solvency PDFs against Decisions 69/2020, 70/2020 and 161/2022.
4. Transcribe Decision 100/2020 governance annex and map its effect on leasing/factoring firms.
5. Obtain Gazette images and compare the 2023 replacement Article 4(2), especially the cross-reference and currency conversion language.

## Progress accounting after this pass

- Newly added unique instruments: **0 confirmed** (Decision 137/2018 and Decision 91/2023 were already represented in the prior acquisition register; this is a text-depth expansion).
- New article/provision bodies: **14** (Decision 91/2023 issuing Articles 1–3, replacement Decision 137 Article 4(2), and Decision 137 Articles 6–16), pending normalized-ID deduplication.
- Running minimum: **245 unique instruments / at least 2,295 normalized provision units**, if all 14 IDs are confirmed distinct against the existing 2,281-unit baseline.
- Assigned domain: **55% provisional**, unchanged; no validated denominator.
- Whole Egyptian corpus: **about 2% provisional**, unchanged.
- Families touched: 13/13; currentness-complete: 0/13.
- Lawyer review: 0%; commercial republication permissions: 0%.
