# Research Agent 2 — Criminal legislation text acquisition tranche
## 19 November 2026 — Arabic text first, low checkpoint overhead

**Repository:** `abdelmalek384/legal_copilot_latest`  
**Dedupe:** use the existing document IDs in `docs/phase_2_document_inventory.json`; new IDs are registered there, not as duplicate EG-CRIM aliases.  
**Lawyer verification:** none. Every item remains unverified by Egyptian counsel.  
**Acquisition meaning:** “full text accessible” means a complete Arabic text is readable at the cited source; it does **not** mean the original file was downloaded, hashed, independently collated, or cleared for bulk/commercial reuse.  
**Collection compliance:** no restricted court database was bypassed; no robots restriction was bypassed; no bulk scraping/download was performed. Publicly readable source text was inspected manually. Permission for local archiving, commercial indexing, display, and redistribution remains a separate gate.

---

## A. New complete Arabic texts and high-value source captures

### A1. Penal Code — Law 58/1937 — existing ID: `EG-PENAL-CODE-58-1937`

**Full Arabic text located:** 540 articles, complete secondary reproduction, with article-by-article amendment annotations. Source says text is transcribed from the Court of Cassation legislation portal and updated through 4 December 2023. The Court of Cassation portal remains separately identified as the official source; do not label the secondary reproduction itself as the Gazette original.

- Full text: https://alhasswalawfirm.com/law-library/law-58-1937
- Alternative full-text reproduction: https://lawhub.info/eg/?p=11750
- Official Gazette citation shown by the transcription: No. 71, 5 August 1937.
- Text page reports commencement 15 October 1937.
- Source class: T3 full-text reproduction; official portal not independently fetched.
- Amendment leads: Law 141/2021 (15 August 2021) and Law 185/2023 (Gazette 48 bis (b), 4 December 2023). Law 185/2023 is a later amendment than the Manshurat metadata's “last amendment 15 August 2021”.

**Verbatim issuance extract (Arts 1–2):**

> مادة (الأولى)  
> يلغى قانون العقوبات الجاري العمل به أمام المحاكم الأهلية وقانون العقوبات الذي تطبقه المحاكم المختلطة ويستعاض عنهما بقانون العقوبات المرافق لهذا القانون.

> مادة (الثانية)  
> على وزير الحقانية تنفيذ هذا القانون ويعمل به من ١٥ أكتوبر سنة ١٩٣٧.

**Law 185/2023 — original Gazette PDF text, three amended provisions:**

- Gazette: No. 48 bis (b), 4 December 2023.
- Commencement: 5 December 2023.
- Original Gazette PDF copy: https://mediadr.sis.gov.eg/bitstream/handle/123456789/49252/OG48_20231204_0120.pdf?isAllowed=y&sequence=2
- Alternative PDF: https://manshurat.org/sites/default/files/alamiria_2023_185.pdf

**Article 1 opening:**

> يستبدل بنصوص المواد (٣٠٦ مكرراً أ، ٣٠٦ مكرراً ب/ فقرة ثانية، ٣٠٩ مكرراً ب/ فقرة ثالثة) من قانون العقوبات، النصوص الآتية:

**Article 306 bis (a), as replaced:**

> يُعاقب بالحبس مدة لا تقل عن سنتين ولا تجاوز أربع سنوات، وبغرامة لا تقل عن مائة ألف جنيه ولا تزيد على مائتي ألف جنيه، أو بإحدى هاتين العقوبتين كل من تعرض للغير في مكان عام أو خاص أو مطروق بإتيان أمور أو إيحاءات أو تلميحات جنسية أو إباحية سواء بالإشارة أو بالقول أو بالفعل بأية وسيلة بما في ذلك وسائل الاتصالات السلكية أو اللاسلكية أو الإلكترونية، أو أية وسيلة تقنية أخرى.  
> وتكون العقوبة الحبس مدة لا تقل عن ثلاث سنوات ولا تجاوز خمس سنوات، وبغرامة لا تقل عن مائتي ألف جنيه ولا تزيد على ثلاثمائة ألف جنيه، أو بإحدى هاتين العقوبتين إذا ارتكبت الجريمة في مكان العمل أو في إحدى وسائل النقل أو من شخصين فأكثر أو إذا كان الجاني يحمل سلاحاً أو إذا تكرر الفعل من الجاني من خلال الملاحقة والتتبع للمجني عليه.  
> وإذا توافر ظرفان أو أكثر من الظروف المشددة الواردة بالفقرة الثانية من هذه المادة يكون الحد الأدنى لعقوبة الحبس أربع سنوات.  
> وفي حالة العود تضاعف عقوبة الحبس والغرامة في حديهما الأدنى والأقصى.

**Article 306 bis (b), second paragraph (as replaced):**

> فإذا كان الجاني ممن نص عليهم في الفقرة الثانية من المادة (٢٦٧) من هذا القانون أو ممن له سلطة وظيفية أو أسرية أو دراسية على المجني عليه أو مارس عليه أي ضغط تسمح له الظروف بممارسته عليه، أو إذا ارتكبت الجريمة في مكان العمل أو في إحدى وسائل النقل أو من شخصين فأكثر أو إذا كان الجاني يحمل سلاحاً تكون العقوبة السجن مدة لا تقل عن سبع سنوات، أما إذا توافر ظرفان أو أكثر من الظروف المشددة الواردة بهذه الفقرة تكون العقوبة السجن مدة لا تقل عن عشر سنوات.

**Article 309 bis (b), third paragraph:** retain exact wording from the linked Gazette PDF during the next extraction pass; the PDF is located, but this tranche does not normalize the complete paragraph.

**Amendment gap:** read and collate the whole 540-article code and every amendment after 4 December 2023. The complete reproduction's update claim is not proof that no later amendment exists.

---

### A2. Criminal Procedure Law — Law 174/2025 — existing ID: `EG-CRIMINAL-PROCEDURE-174-2025`

**Full Arabic text accessible in two sources:**

1. Official Ministry of Justice-hosted Gazette PDF, Gazette 45 bis (d), 12 November 2025:  
   https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B
2. Full-text secondary reproduction, 3,167 extracted lines and code through Article 546:  
   https://temp.manshurat.org/content/qnwn-ljrt-ljnyy-rqm-174-lsn-2025-0

The secondary reproduction is not the Gazette original. The official Ministry of Justice PDF is the primary text source. Law 160/2026 changes commencement to 1 October 2027.

**Important transcription conflict — issuance Article 2:**

The official Ministry of Justice Gazette PDF reads **مواد الجنايات**:

> يستمر نظر الطعون في الأحكام الغيابية الصادرة في مواد الجنايات قبل سريان هذا القانون بذات الأوضاع والإجراءات المقررة قبل العمل به.

The Manshurat full-text reproduction reads **مواد الجنح**. Preserve this as a source discrepancy. For the official-text field, use the Ministry of Justice Gazette PDF reading (**الجنايات**) and retain the secondary variant in the audit log.

**Issuance Article 4:**

> يلغى قانون الإجراءات الجنائية الصادر بالقانون رقم ١٥٠ لسنة ١٩٥٠، والقانون رقم ١٤٠ لسنة ٢٠١٤ في شأن الأحكام الخاصة بتسليم المتهمين ونقل المحكوم عليهم، كما يلغى كل حكم يخالف أحكام هذا القانون والقانون المرافق له.

**Issuance Article 5:**

> مع عدم الإخلال بما ورد في شأن نص خاص في القانون المرافق بشأن الاختصاص بإصدار القرارات التنفيذية، يصدر وزير العدل القرارات اللازمة لتنفيذ أحكام هذا القانون والقانون المرافق له، وإلى حين صدور هذه القرارات يستمر العمل بالقرارات المعمول بها بما لا يتعارض مع أحكام هذا القانون والقانون المرافق له.

**Article 6 after Law 160/2026:**

> ينشر هذا القانون في الجريدة الرسمية، ويعمل به اعتبارًا من الأول من أكتوبر من عام 2027.

**Code Article 1:**

> تتولى النيابة العامة التحقيق، وتحريك، ومباشرة الدعوى الجنائية، ولا تتخذ هذه الإجراءات من غيرها إلا في الأحوال المحددة في القانون.  
> ولا يجوز ترك الدعوى الجنائية، أو وقفها، أو تعطيل سيرها إلا في الأحوال المحددة في القانون.

**Code Article 3 (complaint and 90-day period):**

> لا يجوز رفع الدعوى الجنائية أو اتخاذ أي إجراء من إجراءات التحقيق فيها إلا بناء على شكوى شفهية أو كتابية من المجني عليه أو من وكيله الخاص، إلى النيابة العامة أو إلى أحد مأموري الضبط القضائي في الجرائم المنصوص عليها في المواد ١٨٥، ٢٧٤، ٢٧٧، ٢٧٩، ٢٩٢، ٢٩٣، ٣٠٣، ٣٠٦، ٣٠٧، ٣٠٨ من قانون العقوبات، وكذلك في الأحوال الأخرى التي ينص عليها القانون.  
> ولا تقبل الشكوى بعد تسعين يومًا من يوم علم المجني عليه بالجريمة وبمرتكبها ما لم ينص القانون على خلاف ذلك.

**Code Article 16 (extinction of criminal action):**

> تنقضي الدعوى الجنائية بموت المتهم، أو بمضي المدة، أو بصدور حكم بات فيها، أو بالعفو الشامل، أو بالصلح أو التصالح أو بالأسباب الأخرى التي ينص عليها القانون.

**Code Article 37 (arrest/search/detention outside flagrante delicto):**

> فيما عدا حالة التلبس، لا يجوز القبض على أحد، أو تفتيشه، أو حبسه، أو تقييد حريته بأي قيد إلا بأمر قضائي مسبب يستلزمه التحقيق.  
> وكل من يُقبض عليه أو يُحبس أو تُقيد حريته، تجب معاملته بما يحفظ عليه كرامته، ولا يجوز تعذيبه ولا ترهيبه ولا إكراهه ولا إيذاؤه بدنيًا أو معنويًا.  
> وللمتهم حق الصمت، وكل قول يثبت أنه صدر من محتجز تحت وطأة شيء مما تقدم، أو التهديد بشيء منه، يُهدر ولا يعول عليه.

**Code Article 41 (notification and access to counsel):**

> يجب على مأمور الضبط القضائي أن يبلغ فورًا المتهم المضبوط بسبب تقييد حريته، وبالتهم المنسوبة إليه، وأن يسمع أقواله، وأن يحيطه بحقوقه كتابة، وأن يمكنه من الاتصال بذويه وبمحاميه.  
> وإذا لم يأت المتهم بما ينفي التهمة عنه، يرسله مأمور الضبط القضائي خلال أربع وعشرين ساعة من وقت تقييد حريته إلى سلطة التحقيق المختصة.

**Code Article 521 (extradition / transfer):**

> استثناءً من أحكام هذا الكتاب، يجوز لرئيس الجمهورية بناءً على عرض النائب العام وبعد موافقة مجلس الوزراء، الموافقة على تسليم المتهمين ونقل المحكوم عليهم إلى دولهم، وذلك لمحاكمتهم أو تنفيذ العقوبة المقضي بها عليهم بحسب الأحوال، متى اقتضت مصلحة الدولة العليا ذلك.

**Extraction status:** complete Arabic source located, selected provisions transcribed here; full 552-article article segmentation and comparison against the official PDF remain to be performed.

---

### A3. Criminal Procedure Law — Law 150/1950 — existing ID: `EG-CRIMINAL-PROCEDURE-150-1950`

Full Arabic secondary text source:
- https://kanonmisr.com/ar/نص-قانون-الإجراءات-الجنائية-طبقا-لآخر/
- https://alhasswalawfirm.com/law-library/law-150-1950
- https://manshurat.org/node/14419

Law 1/2024 is already registered in the project. Do not re-create its checkpoint; use it as an amendment relation and extract only any missing article replacements.

**Historical/current separation:** Law 150/1950 remains the current-procedure candidate pending Egyptian lawyer review and any intervening legislation. Law 174/2025's repeal clause must not be applied before its amended commencement date. Law 140/2014 repeal is linked to the same commencement question.

---

### A4. Cybercrime Law — Law 175/2018 — existing ID: `EG-CYBERCRIME-175-2018`

**Complete official-hosted Arabic Gazette PDF:**
https://escc.gov.eg/assets/docs/law-175-2018.pdf

Gazette: No. 32 bis (c), 14 August 2018. The PDF is hosted on the Supreme Constitutional Court domain and contains 416 extracted text lines. No later amending statute was identified in this pass; this is not proof none exists.

**Article 2 — provider retention (180 days):**

> حفظ وتخزين سجل النظام المعلوماتي أو أي وسيلة لتقنية المعلومات، لمدة مائة وثمانين يوما متصلة.

The retained data include user-identification data, content where under provider control, traffic data, terminal-device data and other data determined by the NTRA board.

**Article 6 — reasoned investigative orders:**

> لجهة التحقيق المختصة، بحسب الأحوال، أن تصدر أمراً مسبباً لمأموري الضبط القضائي المختصين، لمدة لا تزيد على ثلاثين يوماً قابلة للتجديد لمرة واحدة...

The permitted measures include seizing/collecting/preserving data and systems, searching computer programs and databases, and requiring providers to supply data under their control. The order must be reasoned and is appealable before the competent criminal court in chambers.

**Article 11 — digital evidence (exact article number resolved):**

> يكون للأدلة المستمدة أو المستخرجة من الأجهزة أو المعدات أو الوسائط أو الدعامات الإلكترونية أو من النظم المعلوماتية أو من برامج الحاسب، أو من أى وسيلة لتقنية المعلومات ذات قيمة وحجية الأدلة الجنائية المادية فى الإثبات الجنائى متى توافرت بها الشروط الفنية الواردة باللائحة التنفيذية لهذا القانون.

**Article 14 — unlawful access (opening):**

> يعاقب بالحبس مدة لا تقل عن سنة، وبغرامة لا تقل عن خمسين ألف جنيه ولا تجاوز مائة ألف جنيه، أو بإحدى هاتين العقوبتين، كل من دخل عمداً، أو دخل بخطأ غير عمدى وبقى بدون وجه حق، على موقع أو حساب خاص أو نظام معلوماتى محظور الدخول عليه.

**Article 17 — integrity of data and systems (opening):**

> يعاقب بالحبس مدة لا تقل عن سنتين، وبغرامة لا تقل عن مائة ألف جنيه ولا تجاوز خمسمائة ألف جنيه، أو بإحدى هاتين العقوبتين، كل من أتلف أو عطل أو عدل مسار أو ألغى كلياً أو جزئياً متعمداً وبدون وجه حق البرامج والبيانات أو المعلومات المخزنة أو المعالجة أو المولدة أو المخلقة على أي نظام معلوماتي وما في حكمه، أياً كانت الوسيلة التي استخدمت في الجريمة.

**Article 28 — digital-evidence tampering by site/account administrator (opening):**

> يعاقب بالحبس مدة لا تقل عن ستة أشهر، وبغرامة لا تقل عن عشرين ألف جنيه ولا تجاوز مائتي ألف جنيه، أو بإحدى هاتين العقوبتين، كل مسؤول عن إدارة موقع أو حساب خاص أو بريد إلكتروني أو نظام معلوماتي أخفى أو عبث بالأدلة الرقمية لإحدى الجرائم المنصوص عليها في هذا القانون...

#### Executive Regulations — PM Decree 1699/2020

**Correct instrument:** قرار رئيس مجلس الوزراء رقم 1699 لسنة 2020, issued 27 August 2020, published in Official Gazette No. 35 follow-up (c), effective 28 August 2020.

- FRA / official-regulator cross-reference: https://manshurat.org/node/68283 (access restrictions may apply; do not bypass).
- Full Arabic secondary text: https://masaar.net/ar/egypt_laws/اللائحة-التنفيذية-لقانون-مكافحة-جرائم-تقنية-المعلومات/
- Eastlaws metadata: https://www.eastlaws.com/legislation-full-text/ar/egypt/prime-minister-decision/27-08-2020/no-1699?id=2000041&type=1

**Regulations Article 9 — digital evidence conditions:**

> تحوز الأدلة الرقمية ذات القيمة والحجية للأدلة الجنائية المادية في الإثبات الجنائى إذا توافرت فيها الشروط والضوابط الآتية:

The conditions include forensic acquisition methods that prevent alteration, deletion or distortion; relevance to the case and scope of the judicial/investigative order; collection and preservation by authorized judicial officers or appointed experts; recording the tools/software/hardware used; recording the hash code of forensic copies; and preserving the original without tampering.

**Regulations Article 10 — documentation metadata:**

> يتم توصيف وتوثيق الدليل الرقمى من خلال طباعة نسخ من الملفات المخزن عليها أو تصويرها بأى وسيلة مرئية أو رقمية...

Required metadata include date/time, operator name/signature, operating system/version, software/version or commands, evidence content, and devices/tools used.

**Regulations Article 11 — key disclosure:**

> وفي جميع الأحوال يلتزم الممثل القانونى ومسئول الإدارة الفعلية ومدير الموقع لدى أى مقدم خدمة بإتاحة مفاتيح التشفير الخاصة به للمحكمة المختصة أو لجهات التحقيق المختصة في حال وجود تحقيق في إحدى الشكاوى أو المحاضر أو الدعاوى عند طلبها رسميًا من تلك الجهات.

**False/uncertain 635 lead:** an ESCC-hosted PDF path previously surfaced with a document headed “635/2020”. It is not accepted as the implementing regulation. The 1699/2020 instrument is independently supported by its Gazette date, Gazette number, FRA/regulatory cross-reference and complete secondary Arabic text. Keep the 635 PDF quarantined as a mislabelled or unrelated document until its provenance is explained; do not create a second executive-regulation record from it.

---

### A5. Anti-Money Laundering Law — Law 80/2002 — existing external project ID: `EG-CRIM-006`; add project document ID `EG-AML-80-2002`

**Full updated Arabic text hosted by the Financial Regulatory Authority (FRA):**
https://fra.gov.eg/wp-content/uploads/2024/05/قانون-مكافحة-غسل-الأموال-1.pdf

FRA identifies the consolidated text as updated through Law 154/2022. A second FRA copy is available at:
https://www.fra.gov.eg/wp-content/uploads/2024/05/قانون.pdf

**Amendment chain identified by the FRA page:**
- Law 78/2003
- Law 181/2008
- Decree-Law 36/2014
- Law 17/2020
- Law 154/2022

**Article 2 (money-laundering offence; updated text opening):**

> يعد مرتكبا لجريمة غسل الأموال كل من علم أن الأموال متحصلة من جريمة أصلية، وقام عمدا بأي مما يلي:

The provision includes converting/transferring proceeds to conceal or disguise origin/ownership/location, and acquiring, possessing, using, managing, keeping, replacing, depositing, guaranteeing, investing, manipulating value, concealing or disguising their true nature/source/location/movement/ownership.

**Article 3 bis (added by Law 154/2022):**

> يكون للوحدة مدير تنفيذي يعين بقرار من رئيس مجلس الأمناء بعد موافقة المجلس، ويحدد القرار مهام واختصاصات وظيفته ومعاملاته المالية.

**Article 9 bis (1) (added by Law 154/2022):**

> تلتزم المؤسسات المالية، وأصحاب المهن والأعمال غير المالية، وكل شخص طبيعي أو اعتباري يمكن أن يكون بحوزته أموال أو أصول أخرى ذات صلة بالأشخاص أو الكيانات المدرجة بموجب قرارات مجلس الأمن ذات الصلة بتمويل الإرهاب وتمويل انتشار أسلحة الدمار الشامل بتنفيذ الآليات التي تصدرها الوحدة تطبيقاً لتلك القرارات إعمالاً لحكم المادة (21) من هذا القانون، بما يشمل التجميد، والامتناع عن تقديم الخدمات المالية لهؤلاء الأشخاص والكيانات.

**Article 15 bis (added by Law 154/2022):**

> يعاقب بالحبس مدة لا تجاوز سنة أو بغرامة لا تقل عن مبلغ مائة ألف جنيه ولا تجاوز مبلغ ثلاثمائة ألف جنيه كل من خالف أحكام المادة (9 مكرراً 1) من هذا القانون.

**Article 17 bis (1) (added by Law 154/2022):**

> يجب على جهات إنفاذ القانون وسلطات التحقيق في قضايا غسل الأموال والجرائم الأصلية المرتبطة بها وجرائم تمويل الإرهاب إجراء التحقيقات المالية الموازية بنفسها أو بالاستعانة بمن تراه من الجهات الأخرى المختصة لتحديد مصدر هذه الأموال أو الأصول إن وجدت.

#### Law 154/2022 — amending instrument full Gazette text

- Gazette No. 30 follow-up (a), 28 July 2022.
- Original Gazette PDF text: https://dspace.id.com.eg/server/api/core/bitstreams/1fe32968-2f23-489d-9045-5a4032fdd9c3/content
- It replaces AML Law Art. 3; adjusts Art. 12 and Art. 14 bis; adds definitions (k) and (l) to Art. 1 and new Arts 3 bis, 9 bis 1, 15 bis and 17 bis 1.

**Law 154/2022 Art. 1, replacement Art. 3 (opening):**

> تنشأ بالبنك المركزي المصري وحدة مستقلة ذات طابع خاص لمكافحة غسل الأموال وتمويل الإرهاب تمثل فيها الجهات المعنية، وتتولى الاختصاصات المنصوص عليها في هذا القانون.

**Art. 3, board composition (opening):**

> ويكون للوحدة مجلس أمناء يرأسه أحد الخبرات القضائية الذي لا تقل مدة خبرته عن خمسة عشر عاما في محكمة النقض أو إحدى محاكم الاستئناف...

#### Executive Regulations — PM Decree 951/2003, as updated in 2023

**FRA consolidated Arabic regulation page:**
https://fra.gov.eg/regulations/اللائحة-التنفيذية-لقانون-مكافحة-غسل-ا/

**FRA full text of Law 154/2022 and consolidated regulation pages list the following amendment decrees:**
- PM Decree 1463/2006
- PM Decree 2367/2008
- PM Decree 1569/2016
- PM Decree 2910/2019
- PM Decree 3331/2023

PM Decree 457/2020 is separately identified in secondary sources. Its relation to the FRA consolidation/amendment chain must be reconciled; do not omit it.

#### PM Decree 3331/2023 — full Official Gazette text

- Gazette No. 35 follow-up (a), 31 August 2023.
- Full official-regulator-hosted Gazette PDF (722 extracted lines): https://fra.gov.eg/wp-content/uploads/2023/09/3331.pdf
- Duplicate PDF path: https://www.fra.gov.eg/wp-content/uploads/2024/03/قرار-رقم-3331-لسنة-2023-بتعديل-بعض-احكام-اللائحة-التنفيذية-لقانون-غسل-الاموال.pdf

**Preamble confirms the base decree:**

> وعلى اللائحة التنفيذية لقانون مكافحة غسل الأموال الصادرة بقرار رئيس مجلس الوزراء رقم ٩٥١ لسنة ٢٠٠٣؛

**Article 1 (replacement of multiple regulations articles):**

> يستبدل بنصوص المواد ١ و٣ و٤ و١٢ مكرراً و١٥ و٢١ مكرراً و٢٢ مكرراً (أ) و٢٢ مكرراً (ب) و٢٢ مكرراً (ج) و٢٢ مكرراً (د) و٢٧ و٢٩ و٣١ و٣٢ و٣٤ و٣٦ و٤٣ مكرراً (أ) و٤٢ مكرراً (ب) و٤٧ و٤٨ و٤٩ و٥٠ و٥٢ و٥٣ من اللائحة التنفيذية لقانون مكافحة غسل الأموال المشار إليها، النصوص الآتية:

**Article 2** adds new regulation articles including 2 bis (a), 2 bis (b), 2 bis (c), 3 bis (d) through 3 bis (j), 28 bis (a), 28 bis (b), 29 bis (a), 31 bis (d), 43 bis (a), 50 bis (a), 50 bis (b), 53 bis (a) and 53 bis (b).

**New Regulation Article 2 bis (b) (anti-money-laundering as autonomous offence):**

> تعد جريمة غسل الأموال جريمة مستقلة عن الجريمة الأصلية، بحيث لا يشترط أن يتم إدانة الشخص بارتكاب الجريمة الأصلية مسبقاً من أجل اعتبار الأموال أو الأصول متحصلات إجرامية.

**Regulation Article 42 (international judicial cooperation; opening):**

> يكون تبادل الجهات القضائية المصرية مع الجهات القضائية الأجنبية التعاون القضائي في مجال مكافحة غسل الأموال والجرائم الأصلية المرتبطة بها وتمويل الإرهاب في كافة صوره المنصوص عليها في المادة (١٨) من القانون وفق القواعد التي تقررها الاتفاقيات الثنائية أو المتعددة الأطراف التي تكون مصر طرفاً فيها أو وفقاً لمبدأ المعاملة بالمثل.

---

### A6. Narcotics Law — Law 182/1960 — existing external ID: `EG-CRIM-007`; add project document ID `EG-DRUGS-182-1960`

**Full Arabic code text located (secondary reproduction):**
https://lawhub.info/eg/?p=11739

**Official Egyptian Drug Authority amendment index:**
https://edaegypt.gov.eg/ar/المرجع-التنظيمي-لهيئة-الدواء-المصرية/القوانين-واللوائح-التنفيذية/تعديلات-قانون-رقم-182-لسنة-1960/

The EDA index lists the following amending statutes:
- Law 206/1960 — 12 July 1960
- Law 40/1966 — 18 August 1966
- Law 16/1973 — 5 April 1973
- Law 61/1977 — 24 November 1977
- Law 45/1984 — 31 March 1984
- Law 122/1989 — 4 July 1989
- Law 134/2019 — 16 July 2019
- Law 19/2020 — 18 March 2020

**Article 1:**

> تعتبر جواهر مخدرة في تطبيق أحكام هذا القانون المواد المبينة في الجدول رقم (1)- الملحق به ، ويستثنى منها المستحضرات المبينة بالجدول رقم (2) .

**Article 1 bis (added by Law 134/2019):**

> تعتبر فى حكم الجواهر المخدرة فى تطبيق أحكام هذا القانون المواد المخلقة المبينة فى الجدول رقم (1) الملحق به ، ويصدر بتحديد ضوابط ومعايير هذه المواد قرار من الوزير المختص.  
> وتسرى على هذه المواد المخلقة جميع الأحكام الواردة فى هذا القانون.

Law 134/2019:
- Gazette No. 28 bis (a), 16 July 2019.
- Full Arabic text: https://www.yahyadhshan.com/2019/11/134-2019-182-1960.html
- Alternative: https://www.egyptlawfirm.net/قانون-رقم-134-لسنة-2019-بتعديل-بعض-أحكام-القانون-رقم-182-لسنة-1960-في-شأن-مكافحة-المخدرات-وتنظيم-استعمالها-والاتجار-فيها/

**Law 19/2020 (joint amendment of Prisons Law 396/1956 and Narcotics Law 182/1960):**
- Gazette No. 11 bis (l), 18 March 2020; effective 19 March 2020.
- Full Arabic text: https://www.laweg.net/framePlain.aspx?ItemID=115433&NID=142457&Type=6&action=ViewActivePages
- Alternative: https://www.eglf.org/قانون-19-لسنة-2020/

**Law 19/2020 Art. 2:**

> تلغى الفقرة الثانية من المادة (٤٦ مكرراً "أ") من القانون رقم ١٨٢ لسنة ١٩٦٠ فى شأن مكافحة المخدرات وتنظيم استعمالها والاتجار فيها.

#### Schedule decisions 2026 — important correction to v0.1

**Health Minister Decision 44/2026** replaced all schedules annexed to Law 182/1960:
- Gazette: Egyptian Proceedings No. 39 follow-up (c), 17 February 2026.
- Official EDA-hosted PDF: https://dev.edaegypt.gov.eg/media/dkjooww3/قرار-وزارة-الصحة-والسكان-رقم-44-لسنة-2026-ar-2026_.pdf
- Official SIS report confirming decision number, date and Supreme Constitutional Court judgment: https://sis.gov.eg/ar/المركز-الإعلامي/الأخبار/وزير-الصحة-يصدر-قرار-ا-عاجل-ا-لمواجهة-ظاهرة-تعاطي-المواد-المخدرة/

**Article 1:**

> تستبدل الجداول المرافقة لهذا القرار ، بالجداول الملحقة بالقانون رقم 182 لسنة 1960 المشار إليه.

**Article 2:**

> ينشر هذا القرار في الوقائع المصرية ، ويعمل به من تاريخ نشره.

The decision's preamble cites the Supreme Constitutional Court judgment in constitutional case No. 33/47 judicial, dated 16 February 2026. The Court's judgment and the complete schedules should be separately ingested; do not rely on press summaries for the legal holding.

**Health Minister Decision 242/2026** subsequently amended the schedules as replaced by Decision 44/2026:
- Issued 20 July 2026; published in Egyptian Proceedings No. 179, 17 August 2026.
- Official EDA-hosted Gazette PDF (4 pages): https://dev.edaegypt.gov.eg/media/lydpgqi5/لمكافحة-المخدرات_2026_242-وزير-الصحة.pdf
- Official EDA legal index lists Decision 242 as modifying the schedules replaced by Decision 44: https://edaegypt.gov.eg/ar/المرجع-التنظيمي-لهيئة-الدواء-المصرية/القوانين-واللوائح-التنفيذية/
- Gazette metadata: https://dspace.id.com.eg/items/138712af-f2d5-4fbf-873e-4ae961269c6e/full

**Decision 242/2026 Article 1 (official PDF OCR):**

> يُستبدل بنص البند (12) الوارد بالجدول رقم (1) - القسم الأول (ب) المرافق لقرار وزير الصحة والسكان رقم 44 لسنة 2026 المشار إليه النص الآتي:

**Decision 242/2026 Article 2:**

> ينشر هذا القرار بالوقائع المصرية، ويعمل به من اليوم التالي لتاريخ نشره.

Thus Decision 242/2026 is not an unverified stale lead: it is a confirmed later amendment to Decision 44/2026. The original v0.1 metadata saying 242 was unexplained is superseded.

---

### A7. Weapons and Ammunition Law — Law 394/1954 — existing external ID: `EG-CRIM-008`; add project document ID `EG-WEAPONS-394-1954`

**Full Arabic law text located (secondary):**
- https://lawhub.info/eg/?p=11748
- https://ar.wikisource.org/wiki/قانون_الأسلحة_والذخائر_(eg)
- https://alhasswalawfirm.com/law-library/law-394-1954

**Official Gazette metadata:** Waqa'i' No. 53 bis (extraordinary), 8 July 1954. The LawHub/Wikisource text gives the full statute and historical amendment annotations. Keep 475/1953 excluded as an amendment to this 1954 law; it predates the law.

**Article 1 (opening):**

> يحظر بغير ترخيص من وزير الداخلية أو من ينيبه عنه حيازة أو إحراز الأسلحة النارية المبينة بالجدول رقم ٢ وبالقسم الأول من الجدول رقم ٣ وكذلك الأسلحة البيضاء المبينة في الجدول رقم ١ المرافق.

**Article 1 bis (added by Law 5/2019):**

> يصرح بإحراز أو حيازة مسدسات وبنادق الصوت وضغط الهواء وضغط الغاز وذخائرها المبينة بالجدول رقم (٥) المرافق وفقاً للشروط والإجراءات التى يصدر بها قرار من وزير الداخلية.

#### Newly identified amendment: Law 163/2022

This was absent from the v0.1 amendment list and must be added.
- Gazette No. 44 follow-up (a), 3 November 2022.
- Official Court of Cassation publication catalogue identifies the Gazette issue and instrument: https://register.cc.gov.eg/publications/30/download
- Official issue metadata: https://mediadr.sis.gov.eg/xmlui/handle/123456789/12845
- Full Arabic secondary reproduction: https://ahmedazimelgamel.blogspot.com/2022/11/163-2022-394-1954.html

Law 163/2022 amends Arts 4, 8, 10, 12, 26 and 30; adds Art. 4 sixth paragraph and Arts 26 bis, 26 bis (a), 26 bis (b).

**Law 163/2022 Article 2 — new Article 26 bis (opening):**

> يعاقب بالسجن المؤبد ، وبغرامة لا تجاوز خمسمائة ألف جنيه كل من جلب بغير ترخيص سلاحًا ناريا أو أيا من أجزائه المبينة بالجداول أرقام (2، 3 ، 4) من هذا القانون أو ذخائرها أو المفرقعات أو أي من مكوناتها ، ولو بقصد إدخالها لدولة أخري.

**New Article 26 bis (b) — online display / incitement:**

> مع عدم الإخلال بأي عقوبة أشد ، يعاقب بالحبس مدة لا تقل عن ستة أشهر ولا تجاوز سنتين ، وبغرامة لا تجاوز عشرة آلاف جنيه أو بإحدى هاتين العقوبتين كل من أنشأ أو أدار أو استخدم موقعًا أو حسابًا خاصًا علي شبكة معلوماتية يعرض صورًا أو مقاطع فيديو للأسلحة المنصوص عليها في هذا القانون ، وكل من نشر أو بث بإحدى طرق العلانية شيئًا مما ذكر سلفًا للتحريض علي العنف باستعراض القوة أو التلويح بها أو تخويف الغير.

**Implementing decisions:** Minister of Interior Decree 770/1954 (weapons and ammunition regulations) is located at https://manshurat.org/node/7415. Full current regulatory text and later ministerial changes remain to be collected. Do not misclassify Prime Minister Decree 1610/2015 as the weapons regulation; the located record describes it as establishing an Interior Ministry department.

---

### A8. Child Law — Law 12/1996 — existing external ID: `EG-CRIM-009`; add project document ID `EG-CHILD-12-1996`

**Full Arabic Law 12/1996 text:** https://lawyeregypt.net/قانون-الطفل-المصرى-رقم-12-لسنة-1996

**Law 126/2008 amendment:** Gazette No. 24 bis, 15 June 2008. Arabic text:
https://www.laweg.net/framePlain.aspx?ItemID=8964&NID=7658&Type=6&action=ViewActivePages

Law 126/2008 rewrote substantial Child Law provisions, changed the terms “محكمة الأحداث” and “نيابة الأحداث” to “محكمة الطفل” and “نيابة الطفل”, inserted victim/witness protections, and added Arts 242 bis and 291 to the Penal Code.

**Law 126/2008 — new Penal Code Art. 291 (opening):**

> يحظر كل مساس بحق الطفل فى الحماية من الاتجار به أو الاستغلال الجنسى أو التجارى أو الاقتصادى، أو استخدامه فى الأبحاث والتجارب العلمية ويكون للطفل الحق فى توعيته وتمكينه من مجابهة هذه المخاطر.

**Child Law Art. 111 (as reproduced after 2008 amendment):**

> لا يحكم بالإعدام ولا بالسجن المؤبد ولا بالسجن المشدد على المتهم الذى لم يجاوز سنه الثامنة عشرة سنة ميلادية كاملة وقت ارتكاب الجريمة.

**Child Law Art. 112 (separation from adults):**

> لا يجوز احتجاز الأطفال أو حبسهم أو سجنهم مع غيرهم من البالغين فى مكان واحد، ويراعى فى تنفيذ الاحتجاز تصنيف الأطفال بحسب السن والجنس ونوع الجريمة.

#### Child Law Executive Regulations

The older PM Decree 3452/1997 is a historical regulation, not the current text.

**PM Decree 2075/2010** issued the current replacement Executive Regulations and repealed the 1997 regulations. A complete 194-article Arabic secondary reproduction is located; its page states updated through 9 June 2020:
https://alhasswalawfirm.com/law-library/decree-2075-2010

The 2010 regulation text and post-2020 amendments need official Gazette comparison. Preserve the 1997 version separately as historical.

---

### A9. Prisons Law 396/1956 — existing external ID: `EG-CRIM-010`; add project document ID `EG-PRISONS-396-1956`

**Full Arabic law text located (secondary):**
https://www.notariesofegypt.org/article.php?id=469

Original publication shown: Waqa'i' No. 96 bis (b), 29 November 1956.

#### Law 19/2020 — joint prison/narcotics amendment

See §A6. It added Article 52 bis to Law 396/1956.

**Article 52 bis:**

> لا تسرى أحكام الإفراج تحت شرط الواردة فى هذا القانون على المحكوم عليهم لارتكابهم أيًا من الجرائم المنصوص عليها فى القانون رقم ١٠ لسنة ١٩١٤ فى شأن التجمهر، والقانون رقم ١٨٢ لسنة ١٩٦٠ فى شأن مكافحة المخدرات وتنظيم استعمالها والاتجار فيها عدا الجناية المنصوص عليها فى المادة (٣٧) منه، وقانون مكافحة غسل الأموال الصادر بالقانون رقم ٨٠ لسنة ٢٠٠٢، وقانون مكافحة الإرهاب الصادر بالقانون رقم ٩٤ لسنة ٢٠١٥.

#### Law 14/2022 — Official Gazette PDF text

- Gazette No. 11 bis (b), 20 March 2022.
- Full PDF copy of Gazette text: https://temp.manshurat.org/file/87963/download?token=oPuxA7uk

**Article 1 replaces Arts 1, 2, 31 and 81.**

**Replacement Article 1 (opening):**

> تنفذ العقوبات المقيدة للحرية في مراكز الإصلاح والتأهيل طبقاً لأحكام القانون، وتخضع للإشراف القضائي، وتهدف إلى رعاية وتأهيل المحكوم عليهم اجتماعياً وثقافياً، وهي ثلاثة أنواع:

**Critical correction to the prior dossier:** Law 14/2022 does **not** simply rename the statute to “Correction and Rehabilitation Centres”. Its Article 2 says the law's title “في شأن تنظيم مراكز الإصلاح والتأهيل المجتمعي” is replaced with “في شأن تنظيم السجون”, while the operative facility terminology in Article 1 is “مراكز الإصلاح والتأهيل”. Preserve this exact title/terminology distinction.

**Article 2 title substitution:**

> مسمى القانون «في شأن تنظيم مراكز الإصلاح والتأهيل المجتمعي» بمسمى «في شأن تنظيم السجون».

Other substitutions include “قطاع الحماية المجتمعية” → “قطاع السجون”; “مركز إصلاح وتأهيل” / “مركز إصلاح” → “سجن” except where used as a penalty; and “نزيل” → “سجين” / “مسجون” in the specified contexts.

#### Internal Prison Regulations

Interior Minister Decree 79/1961 (لائحة السجون), not a statute:
https://manshurat.org/node/12358

Full text and subsequent amendments still need collection. The 1961 decree may contain obsolete terminology; do not assume every provision is compatible with Law 14/2022.

---

### A10. Extradition / transfer of sentenced persons — Law 140/2014 — existing external ID: `EG-CRIM-011`; add project document ID `EG-EXTRADITION-140-2014`

- Gazette No. 46 follow-up, 13 November 2014.
- Effective 14 November 2014.
- Full Arabic text:
  - https://www.aldhshan.com/2026/02/140-2014.html
  - https://kanonmisr.com/ar/قرار-رئيس-الجمهورية-رقم-١٤٠-لسنة-٢٠١٤-قانون-تسليم-ونقل-المحكوم-عليهم/
  - https://manshurat.org/node/6565

**Article 1:**

> مع عدم الإخلال بأحكام القوانين والاتفاقيات الدولية ذات الصلة بتسليم المجرمين ونقل المحكوم عليهم النافذة في مصر، يجوز لرئيس الجمهورية بناءً على عرض النائب العام وبعد موافقة مجلس الوزراء الموافقة على تسليم المتهمين ونقل المحكوم عليهم إلى دولهم، وذلك لمحاكمتهم أو تنفيذ العقوبة المقضي بها بحسب الأحوال، متى اقتضت مصلحة الدولة العليا ذلك.

**Article 2:**

> يُنشر هذا القرار بقانون في الجريدة الرسمية، ويُعمل به اعتباراً من اليوم التالي لتاريخ نشره.

Law 174/2025 Article 4 repeals Law 140/2014 when the new Criminal Procedure Law commences. Keep Law 140/2014 historical/future-repeal linked, not prematurely repealed. The new Code's Article 521 reproduces the presidential extradition/transfer power (see §A2). The detailed extradition procedure is in Arts 514–520 of the new Code; extract those in the next pass.

**International cooperation gap:** collect bilateral and multilateral extradition treaties, Arab League Convention on Extradition (Law 83/1954 approval), mutual legal assistance instruments, transfer-of-sentenced-persons agreements, and treaty implementation instruments.

---

## B. Amendment corrections and source discrepancies

1. **Penal Code:** Law 185/2023 is a full later amendment than the “last amended 15 August 2021” metadata. It changes Arts 306 bis (a), 306 bis (b) second paragraph and 309 bis (b) third paragraph.
2. **CPL 174/2025 Art. 2:** official Ministry of Justice Gazette text says **الجنايات**; Manshurat secondary full text says **الجنح**. Use the official Gazette reading and retain the variant in audit.
3. **Cybercrime Executive Regulations:** Decree 1699/2020 is the identified regulation. Do not promote the unexplained “635/2020” PDF to a separate record.
4. **AML Executive Regulations:** add PM Decree 3331/2023. Reconcile PM Decree 457/2020 with the FRA 2023 consolidation; preserve both leads.
5. **Narcotics schedules:** Decision 44/2026 replaced all schedules; Decision 242/2026 subsequently amended the replacement schedule. Decision 242 is confirmed, not an unverified 2026 lead.
6. **Weapons:** Law 163/2022 is missing from the prior amendment list and adds Arts 26 bis, 26 bis (a), 26 bis (b), plus changes to Arts 4, 8, 10, 12, 26 and 30.
7. **Prisons:** Law 14/2022's title substitution must be represented accurately: statutory title back to “تنظيم السجون”, while facilities are called “مراكز الإصلاح والتأهيل” in the replacement Article 1.
8. **Child regulations:** PM Decree 2075/2010 supersedes 3452/1997; keep 1997 text historical.
9. **Extradition:** Law 140/2014 repeal follows commencement of Law 174/2025, now postponed by Law 160/2026.

---

## C. Acquisition status by assigned topic

| Topic | Complete Arabic text accessible? | New text saved in this tranche? | Main gap |
|---|---|---|---|
| Penal Code 58/1937 | Yes, full 540-article T3 reproduction; Gazette 185/2023 PDF | Selected issuance and 185/2023 articles | Official consolidated source, article diff, post-2023 search |
| CPL 174/2025 | Yes, official Gazette PDF + full secondary HTML | Selected issuance/code articles | Full 552-article segmentation and Gazette collation |
| CPL 150/1950 | Yes, secondary full text | Source references and status note | Complete amendments and official consolidated copy |
| Cybercrime 175/2018 | Yes, official-hosted Gazette PDF | Arts 2, 6, 11, 14, 17, 28 excerpts | Complete 41-article extraction; no amendments search |
| Cybercrime Decree 1699/2020 | Yes, complete secondary text | Arts 9–11 excerpts | Official Gazette copy, all appendices and later amendments |
| AML 80/2002 | Yes, FRA updated 2022 text | Arts 2, 3 bis, 9 bis 1, 15 bis, 17 bis 1 | Complete 2022 consolidated extraction |
| AML Decree 951/2003 | Yes, FRA updated 2023 text | Decree 3331/2023 provisions | Full 2023 consolidation and 457/2020 reconciliation |
| Drugs 182/1960 | Yes, full T3 code; official EDA amendment index | Arts 1, 1 bis; Law 134/2019, Law 19/2020 | Official full code, full current schedules |
| Drugs Decisions 44/2026 & 242/2026 | Yes, official EDA-hosted PDFs | operative Articles 1–2 | Full schedule OCR and SCC judgment collation |
| Weapons 394/1954 | Yes, full T3 text | Art 1 and Law 163/2022 new provisions | Official full code, all ministerial decisions |
| Child 12/1996 | Yes, full secondary text | 126/2008 selected text | Official consolidation and full article segmentation |
| Child Decree 2075/2010 | Yes, 194-article T3 text | Source and replacement relation | Official Gazette copy, amendments after 2020 |
| Prisons 396/1956 | Yes, full secondary text | Law 19/2020 Art 52 bis; Law 14/2022 Arts 1–2 | Official consolidation, 79/1961 current regulations |
| Extradition 140/2014 | Yes, full short text | Arts 1–2 | Treaty corpus and new Code Arts 514–520 |

---

## D. Updated progress

**Estimated criminal-law domain completion: 45%** (up from the previous 36%; approximate weighted research assessment, not a measured corpus statistic).

**Complete Arabic texts located/readable at source:** 11 core laws/codes or consolidations plus 5 executive-regulation / schedule instruments. This is a source-access count, not a count of fully archived or lawyer-approved documents.

**Official/primary Arabic text read or accessible:** Law 174/2025 Gazette PDF; Law 160/2026 official text/issue record; Law 175/2018 court-hosted Gazette PDF; AML Law 80/2002 updated FRA text; Law 154/2022 Gazette PDF; PM Decree 3331/2023 Gazette PDF; Health Decisions 44/2026 and 242/2026 EDA-hosted Gazette PDFs; Law 14/2022 Gazette-text PDF; Law 185/2023 Gazette PDF.

**Secondary full Arabic text available:** Penal Code 58/1937, CPL 150/1950, Law 182/1960, Law 394/1954, Child Law 12/1996, PM Decree 2075/2010, Prison Law 396/1956, Law 140/2014, and PM Decree 1699/2020.

**Persisted verbatim text in this tranche:** selected statutory provisions and amendment instruments; this is not yet a full article-level corpus.

**Lawyer verified:** 0%.

**Contribution to total Egyptian legal knowledge coverage:** not computable without the master index denominator and domain weighting. Do not substitute the criminal-domain percentage for whole-project coverage.

---

## E. Next acquisition pass — do not re-run discovery above

1. Extract all 552 articles of Law 174/2025 from the official Ministry of Justice PDF and compare with the 3,167-line secondary text.
2. Extract all 41 articles of Law 175/2018 and all articles/appendices of PM Decree 1699/2020; capture all digital-evidence requirements.
3. Parse the complete FRA 2022 AML consolidation and all 722 lines of Decree 3331/2023; reconcile Decree 457/2020 and the earlier amendment decrees.
4. OCR all 34 pages of Decision 44/2026 and all 4 pages of Decision 242/2026; build a schedule version table, preserving the superseded schedules.
5. Extract the full 540 Penal Code articles and article-level amendment annotations; collect all Gazette amendments after 2023.
6. Extract the 194 articles of Child Executive Regulations 2075/2010 and verify whether amendments exist after 9 June 2020.
7. Extract the complete Weapons Law 394/1954 and all implementing ministerial decisions; include Law 163/2022 and 5/2019.
8. Extract the complete Prisons Law 396/1956 and the full 79/1961 internal regulations; verify later amendment and implementing decisions.
9. Extract Law 150/1950 with all amendments through the current date, including Law 1/2024; do not duplicate the existing 2024 checkpoint.
10. Extract new Code 174/2025 Arts 514–520; collect extradition and MLA treaties, including Law 83/1954 and any bilateral agreements.
11. Search for all Justice Minister decisions issued under Law 174/2025 Art. 5; preserve the fact that the law is not yet in force.
12. Search special criminal laws relevant to evidence/investigation (Terrorism Law 94/2015, organized-crime, trafficking, corruption, public funds, and sector-specific offence laws) as a separate extension, not as a substitute for the assigned core.

**Do not repeat a source discovery already recorded above unless the next action obtains missing Arabic text, a missing Gazette copy, a later amendment, or a legal-status verification.**

---

## F. Further Arabic text acquisition — terrorism, trafficking, migration, privacy, telecom and e-signature

These related instruments govern criminal offences, special investigation powers, judicial cooperation, electronic evidence and data access. Texts below are selected verbatim provisions; full source texts are linked and their acquisition states are recorded separately.

### F1. Anti-Terrorism Law 94/2015 and Law 15/2020

Full Arabic text (secondary reproduction): https://manshurat.org/node/14679

Law 94/2015 was issued and published 15 August 2015 and commenced 16 August 2015. The source identifies Law 15/2020 (3 March 2020) as its latest amendment. Law 15/2020 replaces Art. 1(f) and Arts 3 and 13, changes references from الأموال to الأموال أو الأصول الأخرى, and adds a paragraph to Art. 39.

**Issuance Art. 1:**

> يُعمل بأحكام قانون مكافحة الإرهاب المرافق، وتسري على ما لم يرد في شأنه نص في هذا القانون أحكام قانوني العقوبات والإجراءات الجنائية.

**Art. 40 — temporary investigative retention:**

> لمأمور الضبط القضائي، لدى قيام خطر من أخطار جريمة الإرهاب ولضرورة تقتضيها مواجهة هذا الخطر، الحق في جمع الاستدلالات عنها والبحث عن مرتكبيها والتحفظ عليهم لمدة لا تجاوز أربع وعشرين ساعة.  
> ويحرر مأمور الضبط القضائي محضراً بالإجراءات، ويعرض المتحفظ عليه صحبة المحضر على النيابة العامة أو سلطة التحقيق المختصة بحسب الأحوال.  
> وللنيابة العامة أو سلطة التحقيق المختصة، لذات الضرورة المنصوص عليها في الفقرة الأولى من هذه المادة وقبل انقضاء المدة المنصوص عليها فيها، أن تأمر باستمرار التحفظ، لمدة أربعة عشر يوماً، ولا تجدد إلا مرة واحدة، ويصدر الأمر مسبباً من محام عام على الأقل أو ما يعادلها.

**Art. 41 — notice and lawyer contact:**

> يبلغ مأمور الضبط القضائي كل من يتحفظ عليه وفقاً للمادة (٤٠) من هذا القانون بأسباب ذلك، ويكون له حق الاتصال بمن يرى إبلاغه من ذويه بما وقع والاستعانة بمحام، وذلك دون الإخلال بمصلحة الاستدلال.

**Art. 45 — search:**

> في الأحوال التي يجوز فيها التحفظ على مرتكب جريمة إرهابية أو حبسه احتياطياً، ولدى قيام خطر أو خوف من ضياع الأدلة، لمأمور الضبط القضائي أن يستصدر إذناً مسبباً من النيابة العامة أو سلطة التحقيق المختصة، بحسب الأحوال، بتفتيش مسكن المتحفظ عليه أو المحبوس احتياطياً، وضبط الأشياء والمتعلقات الخاصة بالجريمة التي يجرى التفتيش بشأنها.

**Art. 46 — interception/surveillance:**

> للنيابة العامة أو سلطة التحقيق المختصة، بحسب الأحوال، في جريمة إرهابية أن تأذن بأمر مسبب لمدة لا تزيد على ثلاثين يوماً، بمراقبة وتسجيل المحادثات والرسائل التي ترد على وسائل الاتصال السلكية واللاسلكية وغيرها من وسائل الاتصال الحديثة، وتسجيل وتصوير ما يجري في الأماكن الخاصة أو عبر شبكات الاتصال أو المعلومات أو المواقع الإلكترونية وما يدون فيها، وضبط المكاتبات والرسائل العادية أو الإلكترونية والمطبوعات والطرود والبرقيات بجميع أنواعها.

**Art. 48 — account information:**

> للنائب العام أو من يفوضه من المحامين العامين على الأقل أو سلطة التحقيق المختصة، بحسب الأحوال، أن يأمر بالاطلاع أو الحصول على أية بيانات أو معلومات تتعلق بالحسابات أو الودائع أو الأمانات أو الخزائن أو المعاملات المتعلقة بها، إذا اقتضى ذلك كشف الحقيقة في أعمال الاستدلال أو التحقيق على ارتكاب المتهم أو اشتراكه في أية جريمة إرهابية قامت الدلائل الكافية على وقوعها.

Law 15/2020 text: https://www.eglf.org/قانون-15-لسنة-2020/

### F2. Terrorist Entities and Terrorists Lists — Law 8/2015

**Full official Gazette PDF hosted by FRA:**  
https://fra.gov.eg/wp-content/uploads/2021/11/قانون-8-لسنة-2015-فى-شأن-تنظيم-قوائم-الكيانات-الإرهابية.pdf

Gazette No. 7 bis (z), 17 February 2015; effective 18 February 2015.

Amendments identified: Law 11/2017, Law 2/2020 and Law 14/2020. Law 2/2020 replaces Art. 5. Law 14/2020 changes Art. 1 definitions and Art. 7 consequences, and adds paragraphs to Arts 6 and 9.

**Art. 3 — application and filing:**

> تختص دائرة أو أكثر من دوائر الجنايات بمحكمة استئناف القاهرة تحددها الجمعية العمومية للمحكمة سنوياً تكون منعقدة في غرفة المشورة، بنظر طلبات الإدراج على قائمتي الكيانات الإرهابية والإرهابيين.  
> ويقدم طلب الإدراج من النائب العام إلى الدائرة المختصة مشفوعاً بالتحقيقات والمستندات المؤيدة لهذا الطلب.  
> وتفصل الدائرة المختصة في طلب الإدراج بقرار مسبب خلال سبعة أيام من تاريخ تقديم الطلب لها مستوفياً المستندات اللازمة.

**Art. 4 — duration:**

> يكون الإدراج على أي من القائمتين لمدة لا تجاوز ثلاث سنوات.

**Art. 6 — challenge:**

> لذوي الشأن وللنيابة العامة الطعن في القرار الصادر في شأن الإدراج على أي من القائمتين المشار إليهما خلال ستين يوماً من تاريخ نشر القرار أمام الدائرة الجنائية بمحكمة النقض التي تحددها الجمعية العمومية للمحكمة سنوياً، وذلك وفقاً للإجراءات المعتادة للطعن.

**Art. 9 — international cooperation:**

> في مجال مكافحة أنشطة الكيانات الإرهابية والإرهابيين، تتعاون الجهات القضائية والأجهزة المصرية المعنية بشئون الإرهاب - كل في حدود اختصاصه وبالتنسيق بينها - مع نظيراتها الأجنبية، من خلال تبادل المعلومات والمساعدات والإنابات القضائية وتسليم الأشخاص والأشياء واسترداد الأموال ونقل المحكوم عليهم، وإخطار الدول والمنظمات المعنية بالقرارات المشار إليها في هذا القانون، وغير ذلك من صور التعاون القضائي والمعلوماتي، وذلك كله وفقاً للقواعد التي تقررها الاتفاقيات الدولية النافذة في جمهورية مصر العربية، أو وفقاً لمبدأ المعاملة بالمثل.

Amendment texts: https://www.eglf.org/قانون-2-لسنة-2020/ and https://www.eglf.org/قانون-14-لسنة-2020/

### F3. Human Trafficking Law 64/2010 and Executive Regulations 3028/2010

**Full Arabic Law 64/2010:**  
https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/89881/eg%2064%20of%202010.pdf  
Additional Arabic text updated to 2025: https://lawyeregypt.net/قانون-مكافحة-الاتجار-بالبشر-رقم-64-لسنة-2010/

Gazette No. 18 bis, 9 May 2010; effective 10 May 2010.

**Art. 1 — organized criminal group:**

> الجماعة الإجرامية المنظمة: الجماعة المؤلفة وفق تنظيم معين من ثلاثة أشخاص على الأقل للعمل بصفة مستمرة أو لمدة من الزمن بهدف ارتكاب جريمة محددة أو أكثر من بينها جرائم الاتجار بالبشر وحدها أو مع غيرها وذلك من أجل الحصول بشكل مباشر أو غير مباشر على منفعة مادية أو معنوية.

**Art. 2 — trafficking conduct (opening):**

> يعتبر مرتكباً لجريمة الاتجار بالبشر كل من يتعامل بأية صورة في شخص طبيعي بما في ذلك البيع أو العرض للبيع أو الشراء أو الوعد بهما أو الاستخدام أو النقل أو التسليم أو الإيواء أو الاستقبال أو التسلم سواء في داخل البلاد أو عبر حدودها الوطنية...

**Art. 5 — base penalty:**

> يعاقب كل من ارتكب جريمة الاتجار بالبشر بالسجن المشدد وبغرامة لا تقل عن خمسين ألف جنيه ولا تجاوز مائتي ألف جنيه أو بغرامة مساوية لقيمة ما عاد عليه من نفع أيهما أكبر.

**Art. 11 — actual management liability (opening):**

> يعاقب المسؤول عن الإدارة الفعلية للشخص الاعتباري إذا ارتكبت أي من الجرائم المنصوص عليها في هذا القانون بواسطة أحد العاملين بالشخص الاعتباري باسمه ولصالحه بذات العقوبات المقررة عن الجريمة المرتكبة إذا ثبت علمه بها أو إذا كانت الجريمة قد وقعت بسبب إخلاله بواجبات وظيفته.

**Art. 16 — extraterritorial application (opening):**

> مع مراعاة حكم المادة (٤) من قانون العقوبات، تسري أحكام هذا القانون على كل من ارتكب خارج جمهورية مصر العربية من غير المصريين جريمة الاتجار بالبشر المنصوص عليها في المادتين ٥ و٦ منه، متى كان الفعل معاقباً عليه في الدولة التي وقع فيها تحت أي وصف قانوني...

**Art. 21 — victim non-liability:**

> لا يعد المجني عليه مسؤولاً مسؤولية جنائية أو مدنية عن أي جريمة من جرائم الاتجار بالبشر متى نشأت أو ارتبطت مباشرة بكونه مجنياً عليه.

#### PM Decree 3028/2010 — Executive Regulations

Complete 28-article Arabic text: https://alhasswalawfirm.com/law-library/decree-3028-2010  
Alternative: https://www.aldhshan.com/2026/02/3028-2010-64-2010.html  
Official regulator PDF directory: https://fra.gov.eg/wp-content/uploads/2021/11/

Gazette No. 47 bis, 30 November 2010; effective 1 December 2010. A secondary source says the text is updated through 2025; the amending instruments behind that claim must be identified.

**Regulation Art. 3 — child victim / consent:**

> تقوم جريمة الاتجار في البشر دائماً في حق مرتكبها إذا كان المجنى عليه طفلاً أو من عديمي الأهلية.  
> ولا يستطيع مرتكب جريمة الاتجار بالبشر أن يتمسك برضاء المجنى عليه لدرء مسئوليته الجنائية طالما استخدم الجاني معه الوسائل والأساليب التي نص عليها القانون في ارتكاب جريمة الاتجار بالبشر.

**Regulation Art. 5 — international cooperation:**

> تقوم الجهات المشار إليها في المادة السابقة في سبيل تحقيق المكافحة بتبادل المعلومات وإجراء التحريات عن مرتكبي الجريمة وملاحقتهم وتقديم المساعدات فيما بينها, واتخاذ إجراءات المساعدات والإنابات القضائية وتسليم المجرمين والأشياء, واسترداد الأموال, ونقل المحكوم عليهم...

**Regulation Art. 6 — asset tracing/freezing:**

> تتولى المحاكم والنيابات المختصة بنظر جرائم الاتجار بالبشر في جمهورية مصر العربية ومن خلال إدارة التعاون الدولي والثقافي بوزارة العدل ومكتب التعاون الدولي وتنفيذ الأحكام ورعاية المسجونين بمكتب النائب العام اتخاذ ما يلزم من إجراءات قانونية بالتعاون مع الجهات القضائية الأجنبية لتعقب أو ضبط أو تجميد الأموال موضوع جرائم الاتجار أو عائداتها أو الحجز عليها, وذلك كله مع عدم الإخلال بحقوق الغير حسنى النية.

**Regulation Art. 8 — victim non-liability:**

> المجني عليه في جريمة الاتجار في البشر لا يكون مسئولاً مدنياً أو جنائياً عن أي جريمة أخرى يرتكبها تنفيذاً لاستغلاله في جريمة الاتجار في البشر متى نشأت الجريمة الأخرى أو ارتبطت بكونه مجنياً عليه في جريمة الاتجار بالبشر.

**Related decisions:** PM Decision 192/2017; PM Decision 1123/2017; PM Decision 60/2020; Social Solidarity Minister Decision 289/2021; Presidential Decision 349/2024 organizing the Fund for Assisting Victims of Human Trafficking (Gazette 34 bis (a), 26 August 2024): https://hrightsstudies.sis.gov.eg/media/28148/العدد-34-مكرر-ا-مو-م-من.pdf

Correction: PM Decision 2353/2010 is reported as a committee-reconstitution decision, not the Executive Regulations. The Executive Regulations are PM Decree 3028/2010.

### F4. Illegal Migration and Migrant Smuggling Law 82/2016, Law 22/2022 and Decree 983/2018

**Full 38-article Arabic Law 82/2016:**  
https://alhasswalawfirm.com/law-library/law-82-2016  
**Official Gazette PDF hosted by FRA:**  
https://fra.gov.eg/wp-content/uploads/2021/11/قانون-رقم-82-لسنة-2016-لمكافحة-الهجرة-غير-الشرعية-وتهريب-المهاجرين.pdf

Gazette No. 44 bis (a), 7 November 2016; effective 8 November 2016.

**Law 22/2022** amends Arts 6, 7, 8 and 15; issued/published 11 April 2022; effective 12 April 2022. Full amendment text: https://dfatermasr.net/القانون-رقم-22-لسنة-2022-بشأن-تعديل-بعض-أحكام/  
Consolidated text updated through 11 April 2022: https://lawyeregypt.net/قانون-مكافحة-الهجرة-غير-الشرعية/

**Current Art. 6 (opening):**

> يعاقب بالسجن المشدد وبغرامة لا تقل عن مائتي ألف جنيه ولا تزيد عن خمسمائة ألف جنيه أو بغرامة مساوية لقيمة ما عاد عليه من نفع أيهما أكبر كل من ارتكب جريمة تهريب المهاجرين أو الشروع فيها أو توسط في ذلك.

**Current Art. 7 (opening):**

> تكون العقوبة السجن المؤبد، وغرامة لا تقل عن مليون جنيه ولا تزيد على خمسة ملايين جنيه، أو غرامة مساوية لقيمة ما عاد على الجاني من نفع أيهما أكبر إذا ارتكبت أي من الجرائم المنصوص عليها بالفقرة الأولى من المادة (٦) من هذا القانون في أي من الحالات الآتية...

**Current Art. 8:**

> يعاقب بالسجن وبغرامة لا تقل عن مائتي ألف جنيه ولا تزيد على خمسمائة ألف جنيه كل من هيأ أو أدار مكاناً لإيواء المهاجرين المهربين أو جمعهم أو نقلهم أو سهل أو قدم لهم أية خدمات مع ثبوت علمه بذلك.

**Current Art. 15 (opening):**

> يعاقب بالحبس مدة لا تقل عن سنة وبغرامة لا تقل عن خمسين ألف جنيه ولا تزيد على مائتي ألف جنيه، أو بإحدى هاتين العقوبتين، كل من علم بارتكاب أي من الجرائم المنصوص عليها في هذا القانون أو بالشروع فيها ولم يبلغ السلطات المختصة بذلك.

#### PM Decree 983/2018 — Executive Regulations

Full Arabic text: https://lawhub.info/eg/?p=12572  
Gazette reproduction: https://www.laweg.net/framePlain.aspx?NID=138273&action=viewactivepages&itemid=111688&type=6

Gazette No. 19 bis (z), 15 May 2018; Decree 983/2018 issued 16 May 2018.

**Regulation Art. 1 — transnational crime:**

> الجريمة ذات الطابع عبر الوطني: أية جريمة ارتكبت في أكثر من دولة، أو ارتكبت في دولة واحدة وتم الإعداد أو التخطيط لها أو التوجيه أو الإشراف عليها أو تمويلها في دولة أخرى أو بواسطتها أو ارتكبت في دولة واحدة عن طريق جماعة إجرامية منظمة تمارس أنشطة إجرامية في أكثر من دولة، أو ارتكبت في دولة واحدة وكانت لها آثار في دولة أخرى.

**Regulation Art. 10 — asset tracing/freezing:**

> مع عدم الإخلال بحقوق غير الحسنى النية، تتولى المحاكم والنيابات المختصة بنظر جرائم تهريب المهاجرين في جمهورية مصر العربية ومن خلال إدارة التعاون الدولي والثقافي بوزارة العدل ومكتب التعاون الدولي وتنفيذ الأحكام ورعاية المسجونين بمكتب النائب العام اتخاذ ما يلزم من إجراءات قانونية بالتعاون مع الجهات القضائية الأجنبية لتعقب أو ضبط أو تجميد الأموال موضوع جرائم تهريب المهاجرين أو عائداتها أو الحجز عليها.

**Regulation Art. 11 — foreign criminal judgments:**

> تتولى النيابة العامة من خلال مكتب التعاون الدولي وتنفيذ الأحكام ورعاية المسجونين بمكتب النائب العام الأمر بتنفيذ الأحكام الجنائية الصادرة من الجهات القضائية الأجنبية المختصة بضبط أو تجميد أو مصادرة أو استرداد الأموال المتحصلة من جرائم تهريب المهاجرين وعائداتها وذلك وفق القوانين النافذة والإجراءات التي تضمنتها الاتفاقيات الثنائية أو متعددة الأطراف النافذة في جمهورية مصر العربية، أو وفقاً لمبدأ المعاملة بالمثل...

Law 82/2016 Art. 2 transfers the former coordinating committee from Law 64/2010 into the national committee; Law 64 itself is not repealed.

### F5. Personal Data Protection Law 151/2020 and Ministerial Decision 816/2025

**Official full Arabic Law 151/2020 PDF (723 extracted lines):**  
https://escc.gov.eg/assets/docs/law-151-2020.pdf

Gazette No. 28 bis (e), 15 July 2020. Issuance Art. 7 makes it effective after three months from the day following publication.

**Issuance Art. 3(4) — judicial-data exclusion:**

> البيانات الشخصية المتعلقة بمحاضر الضبط القضائي والتحقيقات والدعاوى القضائية.

**Issuance Art. 5 — jurisdiction:**

> تختص المحاكم الاقتصادية بنظر الجرائم التي ترتكب بالمخالفة لأحكام القانون المرافق.

**Art. 34 — judicial-police status:**

> يكون للعاملين بالمركز الذين يصدر بتحديدهم قرار من وزير العدل بناءً على اقتراح الوزير المختص صفة الضبطية القضائية في إثبات الجرائم التي تقع بالمخالفة لأحكام هذا القانون.

**Art. 36 — unlawful processing/disclosure (opening):**

> يعاقب بغرامة لا تقل عن مائة ألف جنيه ولا تجاوز مليون جنيه كل حائز أو متحكم أو معالج جمع أو عالج أو أفشى أو أتاح أو تداول بيانات شخصية معالجة إلكترونياً بأي وسيلة من الوسائل في غير الأحوال المصرح بها قانوناً أو بدون موافقة الشخص المعني بالبيانات.

**Art. 41 — sensitive data:**

> يعاقب بالحبس مدة لا تقل عن ثلاثة شهور وبغرامة لا تقل عن خمسمائة ألف جنيه ولا تجاوز خمسة ملايين جنيه، أو بإحدى هاتين العقوبتين، كل حائز أو متحكم أو معالج جمع أو أتاح أو تداول أو عالج أو أفشى أو خزن أو نقل أو حفظ بيانات شخصية حساسة بدون موافقة الشخص المعني بالبيانات أو في غير الأحوال المصرح بها قانوناً.

**Art. 46 — obstruction of judicial officers:**

> يعاقب بالحبس مدة لا تقل عن ستة أشهر وبغرامة لا تقل عن مائتي ألف جنيه ولا تجاوز مليوني جنيه، أو بإحدى هاتين العقوبتين، كل من منع أحد العاملين بالمركز ممن يتمتعون بصفة الضبطية القضائية من أداء عمله.

**Art. 47 — corporate-management liability:**

> يعاقب المسؤول عن الإدارة الفعلية للشخص الاعتباري المخالف بذات العقوبات المقررة عن الأفعال التي ترتكب بالمخالفة لأحكام هذا القانون، إذا ثبت علمه بها، وكان إخلاله بالواجبات التي تفرضها عليه تلك الإدارة قد أسهم في وقوع الجريمة.

#### Minister of Communications and IT Decision 816/2025 — Executive Regulations

Gazette Waqa'i' No. 244 follow-up (a), 1 November 2025; effective 2 November 2025. Full 43-article Arabic text: https://alhasswalawfirm.com/law-library/decree-816-2025  
Metadata: https://www.eastlaws.com/legislation-full-text/ar/egypt/tech-minister-decision/01-11-2025/no-816?id=5008447&type=1

**Regulation Art. 2 (collection):**

> يكون جمع البيانات الشخصية ومعالجتها وحفظها وتأمينها وفقا للضوابط والمعايير القياسية والإجراءات والسياسات الآتية.

It requires authorization/licensing, consent and purpose notice subject to exceptions, approved collection mechanisms, defined retention periods, confidentiality and security procedures.

**Regulation Art. 4 (processing):**

> تكون معالجة البيانات الشخصية وفقا للضوابط والمعايير والإجراءات السياسات الآتية.

The secondary page says updated through 2026, but no amending instrument after 816/2025 has been identified. Do not infer a 2026 amendment from that label.

### F6. Telecommunications Law 10/2003 and Law 172/2022

Full Arabic text (secondary): https://lawhub.info/eg/?p=11621  
Official MCIT legislation index: https://mcit.gov.eg/ar/TeleCommunications/Regulations/Laws_and_Legislations

Law 10/2003, Gazette No. 5 bis (a), 4 February 2003; effective 5 February 2003.

**Art. 69 — judicial-police status:**

> يجوز بقرار من وزير العدل بالاتفاق مع الوزير المختص تخويل العاملين الذين يحددهم الجهاز والقوات المسلحة وأجهزة الأمن القومي صفة مأموري الضبط القضائي بالنسبة إلى الجرائم التي تقع بالمخالفة لأحكام هذا القانون وتكون متعلقة بأعمال وظائفهم.

**Law 172/2022:** Gazette No. 51 bis (e), 26 December 2022; effective 27 December 2022. Replaces Art. 44 first paragraph and Art. 77. Gazette PDF record: https://dspace.id.com.eg/items/380cc2e4-a7fc-4068-9337-33addccf8ede

**Current Art. 77 (opening):**

> مع مراعاة حكم الفقرة الأخيرة من المادة (٤٨) من هذا القانون، يعاقب بالحبس مدة لا تقل عن سنة ولا تجاوز خمس سنوات، وبغرامة لا تقل عن مليوني جنيه ولا تجاوز خمسة ملايين جنيه، أو بإحدى هاتين العقوبتين كل من قام باستيراد أو تصنيع أو تجميع أو تسويق أي معدة من معدات الاتصالات دون الحصول على تصريح من الجهاز بالمخالفة للمادة (٤٤/ فقرة أولى) من هذا القانون.

The current text also criminalizes unauthorized possession, use, installation and operation of telecom equipment and provides an aggravated national-security limb. Map Arts 64–69 and 77–87 to telecom-provider obligations and the exact procedural authorization required; do not infer blanket interception powers.

### F7. Electronic Signature Law 15/2004 and Executive Regulations

**Official Arabic Gazette PDF hosted by ITIDA:** https://itida.gov.eg/English/Documents/1.pdf  
Gazette No. 17 follow-up (d), 22 April 2004; effective 23 April 2004.

**Art. 14:**

> للتوقيع الإلكتروني، في نطاق المعاملات المدنية والتجارية والإدارية، ذات الحجية المقررة للتوقيعات في أحكام قانون الإثبات في المواد المدنية والتجارية، إذا روعي في إنشائه وإتمامه الشروط المنصوص عليها في هذا القانون والضوابط الفنية والتقنية التي تحددها اللائحة التنفيذية لهذا القانون.

**Art. 15:**

> للكتابة الإلكترونية وللمحررات الإلكترونية، في نطاق المعاملات المدنية والتجارية والإدارية، ذات الحجية المقررة للكتابة والمحررات الرسمية والعرفية في أحكام قانون الإثبات في المواد المدنية والتجارية، متى استوفت الشروط المنصوص عليها في هذا القانون وفقاً للضوابط الفنية والتقنية التي تحددها اللائحة التنفيذية لهذا القانون.

These articles expressly concern civil, commercial and administrative transactions; they are not a standalone criminal-evidence rule. For criminal digital evidence use Law 175/2018 Art. 11 and its Executive Regulations Art. 9.

#### Ministerial Decision 109/2005 — Executive Regulations

Gazette Waqa'i' No. 115, 25 May 2005; effective 26 May 2005. Full Arabic text (475 lines): https://lawhub.info/eg/?p=12201  
Government MCIT confirmation: https://mcit.gov.eg/Ar/Media_Center/Press_Room/Press_Releases/1158

**Regulation Art. 2 — secure signature system:**

> تكون منظومة تكوين بيانات إنشاء التوقيع الإلكتروني مؤمنة متى استوفت ما يأتي:  
> (أ) الطابع المتفرد لبيانات إنشاء التوقيع الإلكتروني.  
> (ب) سرية بيانات إنشاء التوقيع الإلكتروني.  
> (ج) عدم قابلية الاستنتاج أو الاستنباط لبيانات إنشاء التوقيع الإلكتروني.  
> (د) حماية التوقيع الإلكتروني من التزوير، أو التقليد، أو التحريف، أو الاصطناع أو غير ذلك من صور التلاعب، أو من إمكان إنشائه من غير الموقع.  
> (هـ) عدم إحداث أي إتلاف بمحتوى أو مضمون المحرر الإلكتروني المراد توقيعه.  
> (و) ألا تحول هذه المنظومة دون علم الموقع علماً تاماً بمضمون المحرر الإلكتروني قبل توقيعه له.

**Amendments to Decision 109/2005:**
- Decision 307/2010 — identified by the regulation's amendment note; full text pending.
- Decision 331/2020 — dated 19 April 2020; Gazette No. 95 follow-up, 23 April 2020. Official-hosted PDF: https://esignature-egypt.com/English/Documents/E-Signature%20executive%20directive.pdf
- Decision 467/2024 — dated 12 June 2024; published Waqa'i' No. 141 follow-up, 2 July 2024; effective 3 July 2024. Official Gazette archive: https://dspace.id.com.eg/items/2985ae5e-f38f-4b3b-b8f8-040e4976ba84 ; SIS record: https://mediadr.sis.gov.eg/handle/123456789/70196 ; text metadata: https://www.eastlaws.com/legislation-full-text/ar/egypt/tech-minister-decision/02-07-2024/no-467?id=2137048&type=1

Decision 467/2024 updates trust-service regulation, including electronic signature, seal, timestamp, registered electronic mail and website authentication. Full amended regulation must be collated against the 2005 text and 2020 amendment.

### F8. Related instruments and corrections

- Law 82/2016 is amended by Law 22/2022 (Arts 6, 7, 8, 15).
- PM Decree 983/2018 is the Executive Regulations for Law 82/2016; Arts 10–11 cover asset tracing and enforcement of foreign criminal judgments.
- PM Decree 3028/2010 is the Executive Regulations for Law 64/2010. Decision 2353/2010 concerns committee reconstitution, not the regulation.
- Presidential Decision 349/2024 organizes the Human Trafficking Victims Assistance Fund under Law 64/2010 Art. 27.
- Law 151/2020 Art. 3(4) excludes data relating to police reports, investigations and judicial proceedings from the attached Data Protection Law.
- Ministerial Decision 816/2025 issues the 43-article Executive Regulations for Law 151/2020.
- Law 172/2022 amends Telecom Law 10/2003 Arts 44 and 77.
- Electronic Signature Law 15/2004 Executive Regulations have at least Decisions 307/2010, 331/2020 and 467/2024.
- Law 8/2015 amendments: 11/2017, 2/2020, 14/2020.
- Law 94/2015 amendment: 15/2020.

## H. Updated progress

**Estimated criminal-law domain completion: 49%** (up from 45% at the first tranche; approximate research rubric, not a measured article-count metric).

This tranche adds 20 new inventory records covering terrorism, terrorist listings, human trafficking, migrant smuggling, data protection, telecom and electronic signature. It adds full Arabic text sources and selected exact articles, including special investigation powers, victim protection, digital data offences and evidence-related rules.

**Complete Arabic texts accessible at source:** at least 20 laws/codes and executive/ministerial instruments across the assigned and directly related criminal/evidence domain. This is a source-access count, not a count of fully archived or lawyer-approved documents.

**Full official text locally archived and hash-verified:** 0 in this session. Browser-readable official PDFs are not represented as local archived files.

**Article-level full extraction:** incomplete; selected articles are persisted in this file.  
**Lawyer verification:** 0%.  
**Whole-project coverage:** not computable without the master index denominator and weighting.

## I. Next acquisition actions

1. Extract the 2024 current Executive Regulations of Electronic Signature under Decision 467/2024; collate Decisions 331/2020 and 307/2010.
2. Extract all 43 articles of Data Protection Executive Regulations 816/2025 and all 49 articles of Law 151/2020, preserving Arts 3(4), 34 and 36–49.
3. Extract Law 94/2015 Arts 40–48 and the complete 2020 amendment; search for any post-2020 amendment.
4. Build the full current Law 8/2015 consolidation after Laws 11/2017, 2/2020 and 14/2020.
5. Extract all 28 articles of Decree 3028/2010 and Presidential Decision 349/2024; collect the later committee and victim-support decisions.
6. Extract Law 82/2016 as amended by Law 22/2022 and all 487 lines of Decree 983/2018.
7. Obtain original Gazette PDFs for Law 22/2022, Decision 467/2024 and Presidential Decision 349/2024; hash only after lawful download.
8. Collect Palermo Protocols, Arab Convention on Combating Organized Crime, extradition and mutual legal assistance treaties, and Egyptian ratification instruments.
9. Extract current Telecom Law 10/2003 Arts 64–69 and 77–87; map each provider duty to the specific criminal-investigation authorization.
10. Continue with missing texts and schedules already in the acquisition queue; do not repeat discovery absent a new amendment or better text source.

---

## J. Extradition, mutual legal assistance and treaty corpus — new acquisition

This section closes part of the gap previously recorded for international criminal cooperation. It adds the regional convention, Egyptian accession instrument, UNTOC and Palermo Protocols, and several bilateral judicial-cooperation treaties. Treaty applicability must be checked by party status, reservations, entry-into-force date, and the treaty's relation to bilateral agreements.

### J1. Riyadh Arab Agreement for Judicial Cooperation (1983) — Egypt accession

**Full Arabic convention text, 72 articles:**  
https://www.qanouni.org/ar/convention/1581  
Additional official/ministerial-hosted Arabic PDF: https://adala.justice.gov.ma/api/uploads/2024/04/19/اتفاقية%20الرياض%20العربية-1713540273243.pdf  
Full text with article headings: https://www.sahwanlaw.com/ar/laws/RAC1983.html

**Egyptian accession instrument: Presidential Decision 278/2014**

- Gazette: No. 49, 4 December 2014.
- Issued: 19 August 2014.
- Original Gazette PDF (38 pages): https://manshurat.org/file/6694/download?token=OWECKZVo
- Source record: https://manshurat.org/node/3842

**Official Gazette image — opening and operative article:**

> قرار رئيس جمهورية مصر العربية  
> رقم ٢٧٨ لسنة ٢٠١٤  
> بشأن الموافقة على انضمام جمهورية مصر العربية إلى اتفاقية الرياض العربية للتعاون القضائي  
> الموقعة بتاريخ ٦/٤/١٩٨٣، وعلى تعديل المادة (٦٩) من هذه الاتفاقية بتاريخ ٢٦/١١/١٩٩٧  
> 
> (مادة وحيدة)  
> 
> ووفق على انضمام جمهورية مصر العربية إلى اتفاقية الرياض العربية للتعاون القضائي، الموقعة بتاريخ ٦/٤/١٩٨٣، وعلى تعديل المادة (٦٩) من هذه الاتفاقية بتاريخ ٢٦/١١/١٩٩٧، وذلك مع التحفظ بشرط التصديق.

The original Gazette PDF's first page is visually readable. The decision was issued 19 August 2014 and published 4 December 2014. Manshurat metadata shows an “effective date” of 10 August 2014, which predates the issuance date and is internally inconsistent. A separate international-status listing reports an Egypt date of 8 September 2014. Do not adopt either date as the treaty's definitive entry-into-force date without the Arab League deposit record. The legal accession instrument itself is now located.

**Convention Article 68 — accession:**

> يجوز لأي دولة من دول الجامعة العربية غير الموقعة على الاتفاقية أن تنضم إليها بطلب ترسله إلى أمين عام الجامعة.  
> تعتبر الدولة طالبة الانضمام مرتبطة بهذه الاتفاقية بمجرد إيداع وثيقة تصديقها عليها أو قبولها أو إقرارها ومضى 30 يوماً من تاريخ الإيداع.

**Article 69 — relation to bilateral agreements (as amended 26 November 1997):**

> لا تخل هذه الاتفاقية بالاتفاقيات الخاصة بين بعض الدول الأعضاء، وفي حالة تعارض أحكام هذه الاتفاقية مع أحكام أي اتفاقية خاصة فتطبق الاتفاقية الأكثر تحقيقاً لتسليم المتهمين والمحكومين وتحقيق التعاون الأمني والقضائي في المجالات الأخرى.

**Article 72 — supersession of 1952 Arab League agreements:**

> تحل هذه الاتفاقية بالنسبة للدول التي صادقت عليها محل الاتفاقيات الثلاث المعقودة عام 1952 في نطاق جامعة الدول العربية والمعمول بها حاليا بشأن كل من الإعلانات والإنابات القضائية وتنفيذ الأحكام وتسليم المجرمين.

**Important consequence:** Egypt's 2014 accession approval means Law 83/1954 and the 1953 Arab League extradition convention must not be treated as the sole current regional instrument. Article 72 provides for replacement of the 1952 instruments for states bound by Riyadh. Confirm the accession deposit and entry-into-force date before marking Law 83/1954 as formally superseded in the operative-status field. Bilateral agreements remain separately relevant under the amended Article 69.

### J2. Historical Arab League Extradition Convention — Law 83/1954

**Law 83/1954** approved the Arab League Extradition Convention signed 9 June 1953.
- Issued/published: 20 February 1954.
- Gazette: No. 14 bis (d), 20 February 1954.
- Full Gazette text and attached agreement: https://manshurat.org/file/44665/download?token=Uk23PdHT
- Record: https://manshurat.org/node/34483

**Sole article of Law 83/1954:**

> يوافق على اتفاقية تسليم المجرمين المعقودة بين دول الجامعة العربية والموقعة في ٩ يونيو سنة ١٩٥٣ والموفق عليها من مجلس الجامعة.

**Egyptian reservations reproduced in the Gazette copy:**

> (أولاً) عدم قبول مصر لتسليم المجرم الذي يكون التسليم فيها واجباً والمنصوص عليها في المادة الرابعة وهي جرائم الاعتداء على الثلاث رؤساء الدول أو زوجاتهم أو أصولهم أو فروعهم وجرائم الاعتداء على أولي العهد وجرائم القتل العمد والجرائم الإرهابية.  
> 
> (ثانياً) استبدال كلمة الجواز الواردة بالمادة عشرة: «الجنس» وعدم النص على التبعية.

Status: historical treaty approval; assess supersession under Riyadh Convention Art. 72 after Egypt's accession under Decision 278/2014. Preserve the 1954 text and reservations for historical and transitional cases.

### J3. UN Convention against Transnational Organized Crime (UNTOC) — Presidential Decision 294/2003

**Official Gazette PDF:**  
https://media.mof.gov.eg/mof-prd/2003_294_b4ded04751.pdf  
Gazette No. 37, 9 September 2004. The Ministry of Finance identifies the convention as active and hosts the Gazette text.  
Arabic treaty text: https://ar.wikisource.org/wiki/اتفاقية_الأمم_المتحدة_لمكافحة_الجريمة_المنظمة_عبر_الوطنية  
Additional Arabic PDF: https://haqqi.info/sites/default/files/2014-04/HRIDIL0042_UNGARES5525_Ar_2000.pdf

**UNTOC Article 16 — extradition (opening):**

> تنطبق هذه المادة على الجرائم المشمولة بهذه الاتفاقية، أو في الحالات التي تنطوي على ضلوع جماعة إجرامية منظمة في ارتكاب جرم مشار إليه في الفقرة 1 (أ) أو (ب) من المادة 3 وعلى وجود الشخص الذي هو موضوع طلب التسليم في إقليم الدولة الطرف متلقية الطلب، شريطة أن يكون الجرم الذي يُلتمس بشأنه التسليم معاقبا عليه بمقتضى القانون الداخلي لكل من الدولة الطرف الطالبة والدولة الطرف متلقية الطلب.

**Article 18 — mutual legal assistance (opening):**

> تقدم الدول الأطراف، بعضها لبعض، أكبر قدر ممكن من المساعدة القانونية المتبادلة في التحقيقات والملاحقات والإجراءات القضائية فيما يتصل بالجرائم المشمولة بهذه الاتفاقية، حسبما تنص عليه المادة 3...

Purposes include obtaining evidence or statements; service of judicial documents; searches, seizures and freezing; examination of objects and sites; expert evidence; original documents and records including government, bank, financial, company and business records; tracing proceeds and instrumentalities; and voluntary appearance of persons.

**Article 18(3)(c) — search, seizure and freezing:**

> تنفيذ عمليات التفتيش والضبط، والتجميد.

**Article 18(3)(f) — bank/financial records:**

> تقديم أصول المستندات والسجلات ذات الصلة، بما فيها السجلات الحكومية أو المصرفية أو المالية أو سجلات الشركات أو الأعمال، أو نسخ مصدقة عنها.

### J4. Palermo Trafficking Protocol — Presidential Decision 295/2003

**Official Ministry of Finance record:**  
https://mof.gov.eg/ar/legislation/legislation-5fea7d377bfc600007cc655a  
**Official PDF (16 pages):**  
https://media.mof.gov.eg/mof-prd/2003_295_6161158f4b.pdf?response-content-disposition=attachment%3B+filename%3D%222003-295.pdf%22  
Gazette No. 37, 9 September 2004. Ministry of Finance marks the agreement active and describes it as the Protocol to Prevent, Suppress and Punish Trafficking in Persons, Especially Women and Children, supplementing UNTOC.

**Protocol Article 3(a) — trafficking in persons:**

> يقصد بتعبير "الاتجار بالأشخاص" تجنيد أشخاص أو نقلهم أو تنقيلهم أو إيواؤهم أو استقبالهم بواسطة التهديد بالقوة أو استعمالها أو غير ذلك من أشكال القسر أو الاختطاف أو الاحتيال أو الخداع أو إساءة استعمال السلطة أو إساءة استغلال حالة استضعاف، أو بإعطاء أو تلقي مبالغ مالية أو مزايا لنيل موافقة شخص له سيطرة على شخص آخر لغرض الاستغلال.

**Protocol Article 5 — criminalization:**

> تعتمد كل دولة طرف ما قد يلزم من تدابير تشريعية وتدابير أخرى لتجريم السلوك المبين في المادة 3 من هذا البروتوكول، عندما يرتكب عمدا.

**Protocol Article 6 — assistance and protection to victims:** requires privacy protection, information about proceedings, physical/psychological recovery, housing, counselling, medical and material assistance, and employment/education/training opportunities as appropriate.

**Protocol Article 10 — information exchange and training:** requires law-enforcement, immigration and other relevant authorities to cooperate by exchanging information and training, including methods used by organized criminal groups, routes, false documents and victim identification.

**Protocol Article 11 — border measures:** requires stronger border controls and consideration of carrier obligations to verify travel documents.

Full Arabic text: https://treaties.un.org/doc/treaties/2000/11/20001115%2011-38%20am/ch_xviii_12_ap.pdf

### J5. Migrant Smuggling Protocol — Presidential Decision 297/2004

**Official Ministry of Finance record:**  
https://mof.gov.eg/ar/legislation/legislation-5fea7bbd7bfc600007cc64be  
**Official Gazette PDF (21 pages):**  
https://media.mof.gov.eg/mof-prd/2004_297_fcd4bfe94d.pdf?response-content-disposition=attachment%3B+filename%3D%222004-297.pdf%22  
Gazette No. 21, 26 May 2005. Ministry of Finance marks the agreement active. The instrument approves Egypt's accession to the Protocol against the Smuggling of Migrants by Land, Sea and Air, supplementing UNTOC.

**Protocol Article 2 — purpose:**

> أغراض هذا البروتوكول هي منع ومكافحة تهريب المهاجرين، وكذلك تعزيز التعاون بين الدول الأطراف تحقيقا لتلك الغاية، مع حماية حقوق المهاجرين المهرَّبين.

**Article 5 — migrant non-liability:**

> لا يصبح المهاجرون عرضة للملاحقة الجنائية بمقتضى هذا البروتوكول، نظرا لكونهم هدفا للسلوك المبيّن في المادة 6 من هذا البروتوكول.

**Article 6 — criminalization (opening):**

> تعتمد كل دولة طرف ما قد يلزم من تدابير تشريعية وتدابير أخرى لتجريم الأفعال التالية في حال ارتكابها عمدا ومن أجل الحصول، بصورة مباشرة أو غير مباشرة، على منفعة مالية أو منفعة مادية أخرى:  
> (أ) تهريب المهاجرين؛  
> (ب) القيام، بغرض تسهيل تهريب المهاجرين، بإعداد وثيقة سفر أو هوية مزورة أو تدبير الحصول عليها أو توفيرها أو حيازتها.

**Article 8 — maritime enforcement:** establishes cooperation and authorization rules for action against vessels suspected of migrant smuggling; flag-state consent and limits must be preserved.

**Article 11 — border measures:** requires border controls and considers carrier obligations to verify travel documents.

**Article 16 — protection and assistance:** protects the life, safety and rights of smuggled migrants and requires appropriate protection from violence and assistance where life or safety is at risk.

Full Arabic text: https://ar.wikisource.org/wiki/بروتوكول_مكافحة_تهريب_المهاجرين_عن_طريق_البر_والبحر_والجو،_المكمل_لاتفاقية_الأمم_المتحدة_لمكافحة_الجريمة_المنظمة_عبر_الوطنية

### J6. Bilateral judicial cooperation and extradition agreements

Bilateral treaties remain relevant under Riyadh Convention Art. 69 (as amended 1997): where a bilateral agreement conflicts with the regional agreement, the provision more conducive to extradition and cooperation applies. The agreements below have full Arabic text or official-government source records.

#### Egypt–Turkey — Presidential Decision 222/1989

- Agreement signed Ankara, 4 April 1988.
- Decision 222/1989 issued 4 June 1989.
- Gazette publication 26 December 1991.
- Entry into force metadata discrepancy: 12 January 1992 in one record; 2 January 1992 in another.
- Full Arabic text: https://mksegypt.org/public/ar/decisions/30632
- Manshurat record/PDF: https://manshurat.org/node/20932

The agreement contains two sections: judicial cooperation in criminal matters and extradition. Article 1 includes preliminary investigation, hearing accused/witnesses/experts, searches, seizure of objects, service of documents and notices; it excludes execution of arrest warrants and convictions from the first section. Articles 14–17 regulate channels, translations, authentication and refusal/notification. Articles 21 onward regulate extradition.

**Agreement Art. 1 (opening):**

> تتعهد الدولتان المتعاقدتان، بمقتضى أحكام هذا القسم، بأن تتبادلا التعاون القضائي على أوسع نطاق ممكن بالنسبة لأى إجراء يتعلق بجرائم تختص بها السلطات القضائية فى الدولة الطالبة وقت طلب المساعدة.

**Agreement Art. 14:**

> يتم التخاطب بين السلطات القضائية في الدولتين المتعاقدتين من خلال وزارتي العدل في هاتين الدولتين. وإذا اقتضى الحال يجوز التخاطب بالطريق الدبلوماسي.

#### Egypt–Morocco — Presidential Decision 229/1989

- Agreement signed Rabat, 22 March 1989.
- Decision issued 4 June 1989.
- Gazette publication metadata conflict: 20 November 1997 (Manshurat) versus 7 November 1997 (another Manshurat record); Moroccan publication record is 12 August 1997.
- Entry into force metadata: 11 September 1997.
- Full Arabic text: https://www.mksegypt.org/ar/decisions/27512
- Manshurat record/PDF: https://manshurat.org/node/20931

The agreement covers criminal judicial cooperation and extradition. Its opening Article 1 provides for the widest possible judicial cooperation in procedures concerning offences within the jurisdiction of either state's judicial authorities. Article 2 allows refusal where the request concerns political/tax/customs/currency offences or would prejudice sovereignty, security, public order or essential interests.

**Agreement Art. 1 (opening):**

> تتعهد الدولتان بمقتضى هذه الاتفاقية بأن تتبادلا التعاون القضائى على أوسع نطاق ممكن لأى إجراء يتعلق بجرائم تختص بها السلطات القضائية فى أى منهما.

#### Egypt–Hungary — Presidential Decision 129/1988

- Decision 129/1988 dated 26 March 1988.
- Gazette publication 17 November 1988.
- Entry-into-force metadata: 3 October 1988 (predates publication; verify treaty notification).
- Manshurat full agreement PDF record: https://manshurat.org/node/20933

#### Egypt–Romania — Presidential Decision 76/2003

- Decision 76/2003 dated 22 March 2003.
- Gazette publication 28 August 2003.
- Entry-into-force metadata: 10 July 2003 (predates publication; verify treaty notification).
- Manshurat full agreement PDF record: https://manshurat.org/node/37361

Agreement covers criminal judicial cooperation, transfer of sentenced persons and extradition.

#### Egypt–Switzerland — Presidential Decision 177/2001

- Ministry of Finance official treaty record marks the agreement active.
- Official MoF text page: https://mof.gov.eg/ar/legislation/legislation-5fea7dcc7bfc600007cc664d
- Official PDF (19 pages): https://media.mof.gov.eg/mof-prd/2001_177_c317b57cfe.pdf?response-content-disposition=attachment%3B+filename%3D%222001-177.pdf%22
- Agreement concerns judicial cooperation in criminal matters between Egypt and the Swiss Confederation.

#### Egypt–Pakistan — Presidential Decision 233/1994

- Gazette No. 31 follow-up, 4 August 1994.
- Full Gazette text and agreement: https://manshurat.org/file/50795/download?token=7arjmwr3
- Approval of the extradition agreement signed in Islamabad on 14 July 1994, subject to ratification.
- Full agreement has 15 articles; Article 14 governs entry into force following exchange of instruments of ratification.

### J7. Law 174/2025 — new Code, Book Five: international judicial cooperation and extradition

The official Ministry of Justice Gazette PDF and full secondary code text contain the new Book Five. The following provisions are extracted from the full Arabic text; they will replace the old procedure-law framework only when Law 174/2025 commences (currently 1 October 2027 under Law 160/2026).

**Article 511 — incoming foreign cooperation requests:**

> ترسل طلبات التعاون القضائي الدولي في المسائل الجنائية الواردة من الجهات القضائية الأجنبية عبر الطريق الدبلوماسي إلى وزارة العدل متضمنة ملخص الواقعة، ونوع وموضوع الطلب المترجم إلى اللغة العربية.  
> ويجب أن يرفق بالطلب المستندات المؤيدة له.  
> وتتولى وزارة العدل التحقق من مدى توفر الشروط المبينة بالفقرة الأولى من هذه المادة، ولها أن تتخذ أيًا من الإجراءين الآتيين:  
> (أولًا) حفظ الطلب إذا تبين لها عدم توفر الشروط المشار إليها مع إخطار الجهة الطالبة بأسباب الحفظ عبر الطريق الدبلوماسي.  
> (ثانيًا) إحالة الطلبات المستوفاة للشروط المشار إليها إلى النيابة العامة لإعمال شئونها طبقًا لأحكام هذا الكتاب.  
> ويُعرض كل من يُقبض عليه تنفيذًا لحكم الفقرة الأولى من هذه المادة على النيابة العامة خلال أربع وعشرين ساعة من وقت القبض عليه، والتي تباشر معه إجراءات التحقيق في التهمة المنسوبة إليه والمبينة بالطلب وذلك بحضور محاميه...

The article further permits a senior prosecutor to order consecutive periods of provisional detention of up to 15 days each, with a total ceiling of 60 days pending the formal extradition request and decision; the Public Prosecutor may place the person on travel-ban or arrival-watch lists.

**Article 514 — mandatory refusal of extradition:**

> لا يجوز تسليم الأشخاص في أي من الحالات الآتية:  
> 1- إذا كان المطلوب تسليمه مصري الجنسية، ويجوز للجهة القضائية الأجنبية تقديم طلب محاكمته مصحوبًا بالتحقيقات التي أجرتها الدولة الطالبة والمستندات، ويتعين إخطار الجهة القضائية الأجنبية بما آلت إليه الدعوى الجنائية، وموافاتها بنسخة من التصرف النهائي في فترة زمنية مناسبة.  
> 2- إذا كانت الجريمة موضوع طلب التسليم غير معاقب عليها وفقًا لأحكام القانون المصري.  
> 3- إذا انعقد الاختصاص للجهات القضائية المصرية بالجريمة المطلوب التسليم من أجلها.  
> 4- إذا كانت الجريمة موضوع الطلب جريمة سياسية أو جريمة مرتبطة بها.  
> 5- إذا كانت الجريمة المطلوب التسليم من أجلها تنحصر في الإخلال بواجبات عسكرية.

**Article 515 — reasoned decision and challenge:**

> يصدر النائب العام أو من يفوضه قرارًا مسببًا في طلب التسليم، ويجوز لكل من صدر قرار بتسليمه، أن يطعن فيه أمام محكمة جنح مستأنف أو المحكمة العسكرية للجنح المستأنفة بالقاهرة بحسب الأحوال، وذلك بتقرير بالطعن بقلم كتاب المحكمة خلال مدة لا تزيد على سبعة أيام من تاريخ إعلانه بالقرار، وتحدد في التقرير جلسة لنظر الطعن والفصل فيه خلال مدة لا تزيد على سبعة أيام، ويعتبر التقرير بالطعن إعلانًا بالجلسة المحددة ولو كان التقرير من وكيل، ويفصل في الطعن بقرار مسبب لا يقبل الطعن فيه، ولا ينفذ القرار الصادر بالتسليم إلا عقب الفصل في الطعن أو فوات مواعيده.

**Article 516 — Egyptian request for surrender:**

> يجوز للنيابة العامة أن تطلب من الجهة القضائية الأجنبية تسليم المتهم أو المحكوم عليه، وفي حالة رفض التسليم لها أن تطلب محاكمته وفقًا لقانون الدولة المطلوب منها، ويجوز للنيابة العامة أن تصدر أمرًا مسببًا بالقبض على المطلوب تسليمه، وتعتبر مدة حبسه التي تمت بالخارج مدة حبس احتياطي في شأن تطبيق قواعد تنفيذ العقوبة.

**Article 517 — controlled delivery:**

> يجوز للنائب العام، أو من يفوضه، بناءً على طلب الجهة الطالبة ووفقًا للشروط التي يتم الاتفاق عليها، أن يأذن بدخول أشياء تعد حيازتها جريمة أو متحصلة من جريمة أو أداة في ارتكابها إلى داخل البلاد أو عبورها إلى خارجها، دون ضبطها، أو استبدالها كليًا أو جزئيًا، وذلك تحت رقابة السلطات المصرية المختصة، متى كان من شأن ذلك التعرف على وجهة تلك الأشياء أو ضبط الجناة، وما بحوزتهم.  
> ولا يجوز إصدار الإذن المشار إليه في الفقرة الأولى من هذه المادة، إذا كان من شأن تنفيذه الإضرار بالأمن أو سيادة الدولة أو النظام العام أو الآداب العامة أو يتعارض مع مقتضيات الأمن القومي.

**Article 518 — conditions for foreign judicial assistance:**

> يشترط لإجابة طلب المساعدة القضائية المقدم من الجهة القضائية الأجنبية توافر الشروط الآتية:  
> 1- أن يتعلق طلب المساعدة القضائية بجريمة معاقب عليها في الدولة الطالبة، وتدخل في اختصاص جهاتها القضائية ولو كانت جريمة مدرجة تحت وصف آخر.  
> 2- أن تكون المساعدة القضائية مرتبطة بمباشرة إجراءات قضائية في دعوى جنائية منظورة أمام الجهة القضائية الأجنبية.  
> 3- ألا يكون من شأن تنفيذ طلب المساعدة القضائية الإضرار بالأمن أو سيادة الدولة أو النظام العام أو الآداب العامة أو التعارض مع مقتضيات الأمن القومي.

**Article 519 — refusal grounds for judicial assistance:**

> يجوز للنيابة العامة رفض طلب المساعدة القضائية في الحالات الآتية:  
> 1- إذا كانت الجريمة موضوع طلب المساعدة القضائية غير معاقب عليها وفقًا لأحكام القانون المصري.  
> 2- إذا كانت الجريمة موضوع طلب المساعدة القضائية جريمة سياسية أو جريمة مرتبطة بها.  
> 3- إذا كانت الجريمة موضوع طلب المساعدة القضائية تنحصر في الإخلال بواجبات عسكرية.  
> 4- إذا قُصد بطلب المساعدة القضائية معاقبة شخص لأسباب تتعلق بانتمائه العرقي أو الديني أو لجنسيته أو لآرائه السياسية، أو أن يكون من شأن توافر أي من هذه الأسباب الإضرار بمركزه القانوني.  
> 5- إذا انعقد الاختصاص للجهات القضائية المصرية بالجريمة المطلوب المساعدة القضائية من أجلها.  
> 6- إذا تعارض تنفيذ طلب المساعدة القضائية مع مبدأ عدم جواز محاكمة الشخص عن ذات الجريمة أكثر من مرة.  
> 7- إذا انقضت الدعوى الجنائية، أو سقطت العقوبة المقضي بها بمضي المدة، وفقًا للقانون المصري أو قانون الدولة الطالبة النافذ عند تلقي طلب المساعدة القضائية.  
> 8- إذا كان تنفيذ طلب المساعدة القضائية يخرج عن اختصاص الجهات القضائية المصرية.

**Article 520 — decision:**

> يصدر النائب العام أو من يفوضه قرارًا في طلب المساعدة القضائية المقدم من الجهات القضائية الأجنبية، وفي حالة الموافقة يُنفذ على وجه السرعة.

**Article 521 — exceptional presidential surrender/transfer:**

> استثناء من أحكام هذا الكتاب، يجوز لرئيس الجمهورية بناء على عرض النائب العام وبعد موافقة مجلس الوزراء، الموافقة على تسليم المتهمين ونقل المحكوم عليهم إلى دولهم، وذلك لمحاكمتهم أو تنفيذ العقوبة المقضي بها عليهم بحسب الأحوال، متى اقتضت مصلحة الدولة العليا ذلك.

**Unextracted:** Articles 508–510 and 512–513 must be transcribed from the official Gazette PDF in the next pass; do not infer their wording from the surrounding provisions.

### J8. International-cooperation acquisition status and gaps

- Egypt's accession to Riyadh 1983 is supported by Presidential Decision 278/2014 and the original Gazette image; deposit/entry-into-force date needs the Arab League deposit record.
- Law 83/1954 and the 1953 Arab League Extradition Convention are preserved as historical; Article 72 of Riyadh replaces the 1952 agreements for states bound by Riyadh.
- UNTOC, Trafficking Protocol and Smuggling Protocol are listed as active on the Ministry of Finance international agreements database and have official Gazette PDFs.
- The bilateral agreements with Turkey, Morocco, Hungary, Romania, Switzerland and Pakistan have been located; dates and entry-into-force metadata contain conflicts and must be checked against exchange-of-ratification records.
- The amended Riyadh Article 69 gives priority to the agreement more conducive to extradition and judicial/security cooperation where bilateral and regional rules conflict.
- Law 174/2025 Book Five provides a future domestic procedural framework; it is not operative until the postponed commencement date.
- The next collection pass must include the full treaties, their ratification instruments, reservations, party status, effective dates and any termination notices. Do not treat a Ministry of Finance “active” label as a substitute for treaty-status verification.

## K. Progress update — international cooperation acquisition

**Estimated criminal-law domain completion: 52%** (up from 49%; approximate research-progress estimate, not a measured article-count metric).

This pass added:
- Egypt's Riyadh Convention accession instrument and the 72-article Arabic convention;
- historical Law 83/1954 and its reservations;
- UNTOC and both Palermo Protocols, with official Ministry of Finance Gazette PDFs;
- six bilateral judicial-cooperation/extradition instruments;
- Law 174/2025 Book Five Arts 511 and 514–521, with exact Arabic wording.

**Complete Arabic text accessible at source:** expanded to include the regional convention, UNTOC, the two Palermo Protocols, and bilateral agreements.  
**Full local official PDF archive and hash verification:** still 0 in this session.  
**Lawyer verification:** 0%.  
**Whole-project coverage:** not computable without the master-index denominator.


---

## L. Criminal evidence, judicial police, experts and forensic examination

### L1. Law 174/2025 — new Code: police powers, evidence preservation, searches, communications and experts

**Primary source:** Ministry of Justice-hosted Official Gazette PDF, issue 45 bis (d), 12 November 2025:  
https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B

The following provisions are part of the promulgated code but are not operative until the postponed commencement date (1 October 2027 under Law 160/2026).

**Code Article 24 — police inquiry:**

> يتولى مأمورو الضبط القضائي البحث عن الجرائم ومرتكبيها، وجمع الاستدلالات التي تلزم للتحقيق والدعوى.

**Article 25 — subordination to the Public Prosecution:**

> مأمورو الضبط القضائي تابعون للنائب العام وخاضعون لإشرافه فيما يتعلق بأعمال وظائف الضبط القضائي.  
> ويجوز للنائب العام أن يطلب إلى الجهة المختصة النظر في أمر كل من تقع منه مخالفة لواجباته، أو تقصير في عمله، وله أن يطلب إحالته إلى المحاكمة التأديبية، وهذا كله لا يمنع من رفع الدعوى الجنائية.

**Article 26 — judicial-officer categories (opening and special nationwide categories):**

> يكون من مأموري الضبط القضائي في دوائر اختصاصهم:  
> 1. أعضاء النيابة العامة ومعاونوها.  
> 2. ضباط الشرطة وضباط الشرف وأمناؤها والمساعدون ومراقبو ومندوبي الشرطة وضباط الصف ومعاونو الأمن.  
> 3. العمد، ومشايخ البلاد، ومشايخ الخفراء.  
> 4. نظار ووكلاء محطات السكك الحديدية الحكومية.

The article then gives nationwide jurisdiction to specified National Security, Public Security, Community Protection, Transport Police, mounted police and Tourism Inspectorate officers, and permits designation of certain public employees by joint Justice Minister / competent minister decision. The exact list must be preserved in the code's article table, not summarized into an open-ended generic “police” category.

**Article 27 — receiving reports and preserving evidence:**

> يجب على مأموري الضبط القضائي أن يتلقوا البلاغات والشكاوى التي ترد إليهم بشأن الجرائم، وأن يرسلوها فورًا إلى النيابة العامة، ويجب عليهم وعلى مرؤوسيهم أن يحصلوا على جميع الإيضاحات، ويجروا المعاينات اللازمة لتسهيل تحقيق الوقائع التي تبلغ إليهم، أو التي يعلنون بها أية كانت، وعليهم أن يتخذوا جميع الوسائل التحفظية اللازمة للمحافظة على أدلة الجريمة.  
> ويجب على مأموري الضبط القضائي إثبات بيانات الرقم القومي للمتهم فور تحديد هويته، وإرفاق مستخرج من هذه البيانات بالمحضر.

**Article 32 — police questioning and expert assistance:**

> يجوز لمأموري الضبط القضائي أثناء جمع الاستدلالات سماع أقوال من يكون لديهم معلومات عن الوقائع الجنائية ومركبها وسؤال المتهم عن ذلك، ولهم أن يستعينوا بالأطباء، وغيرهم من أهل الخبرة ويطلبوا رأيهم شفهياً أو بالكتابة.  
> ولا يجوز لهم تحليف الشهود أو الخبراء اليمين إلا إذا خيف ألا يستطيعوا فيما بعد سماع الشهادة بيمين.

**Article 34 — scene examination and physical trace preservation in flagrante delicto:**

> يجب على مأمور الضبط القضائي في حالة التلبس بجناية أو جنحة أن ينتقل فورًا إلى محل الواقعة، ويعاين الآثار المادية للجريمة، ويحافظ عليها، ويثبت حالة الأماكن والأشخاص، وكل ما يفيد في كشف الحقيقة، ويسمع أقوال من كان حاضرًا، أو من يمكن الحصول منه على إيضاحات في شأن الواقعة ومركبها.  
> ويجب عليه أن يخطر النيابة العامة فورًا بانتقاله، وعليها بمجرد إخطارها بجناية متلبس بها الانتقال فورًا إلى محل الواقعة متى اقتضى الأمر ذلك.

**Article 54 — seizure of evidence:**

> يجوز لمأمور الضبط القضائي أن يضبط الأشياء والأوراق التي يحتمل أن تكون قد استعملت في ارتكاب الجريمة، أو نتجت عن ارتكابها، أو وقعت عليها، وكل ما يفيد في كشف الحقيقة.  
> وتوصف هذه الأشياء والأوراق وتعرض على المتهم، ويطلب منه إبداء ملاحظاته عليها، ويحرر بذلك محضر يوقعه المتهم، أو يذكر فيه امتناعه عن التوقيع.

**Article 55 — sealed exhibits:**

> توضع الأشياء والأوراق المضبوطة وفقًا للمادة ٥٤ من هذا القانون في حرز مغلق، ويختم عليها، ويكتب على شريط داخل الختم تاريخ المحضر المحرر بضبطها، ويشار إلى الواقعة التي حصل الضبط من أجلها.

**Article 56 — opening seals:**

> لا يجوز فض الأختام الموضوعة طبقًا للمادتين ٥٣، ٥٥ من هذا القانون إلا بحضور المتهم أو وكيله ومن ضبطت هذه الأشياء أو الأوراق، أو بعد دعوتهم لذلك.

**Article 64 — delegation to judicial officers:**

> يجوز لعضو النيابة العامة من درجة مساعد نيابة عامة على الأقل أن يندب أحد مأموري الضبط القضائي للقيام بعمل معين أو أكثر من أعمال التحقيق عدا استجواب المتهم.

**Article 80 — communications, social media and digital monitoring:**

> يجوز لعضو النيابة العامة، بعد الحصول على إذن من القاضي الجزئي، أن يصدر أمراً بضبط جميع الخطابات، والرسائل، والبرقيات، والجرائد والمطبوعات، والطرود، وأن يأمر بمراقبة الاتصالات السلكية واللاسلكية، وحسابات مواقع وتطبيقات التواصل الاجتماعي ومحتوياتها المختلفة غير المتاحة للكافة، والبريد الإلكتروني، والرسائل النصية أو المسموعة أو المصورة على الهواتف أو الأجهزة أو أية وسيلة تقنية أخرى، وضبط الوسائط الحاوية لها أو إجراء تسجيلات لأحاديث جرت في مكان خاص متى كان لذلك فائدة في ظهور الحقيقة في جناية أو جنحة معاقب عليها بالحبس لمدة تزيد على ثلاثة أشهر.  
> ويجب أن يكون الأمر بالضبط أو الاطلاع أو المراقبة أو التسجيل لمدة لا تزيد على ثلاثين يوماً.  
> ويصدر القاضي الإذن المشار إليه مسببا بناء على الأوراق والتحقيقات، ويجوز له أن يحدده لمدة أو لمدد أخرى مماثلة.

**Article 81 — targeted monitoring of a device/site in specified offences:**

> يجوز للقاضي الجزئي بناءً على طلب النيابة العامة في حالة قيام دلائل قوية على أن مرتكب إحدى الجرائم المنصوص عليها في المواد ١٦٦ مكرراً، ٣٠٨ مكرراً، ١٢ من قانون العقوبات، والبند ٢/ من المادة ٧٦ من قانون تنظيم الاتصالات الصادر بالقانون رقم ١٠ لسنة ٢٠٠٣ قد استخدم في ارتكابها هاتفاً معيناً ثابتاً أو محمولاً، أو أي موقع إلكتروني، أو أي وسيلة تقنية أخرى، أن يصدر أمراً مسببا بناءً على تقرير فني وشكوى المجني عليه في الجريمة المذكورة يوضح هذه الوسيلة أو ذلك الجهاز تحت المراقبة لمدة لا تزيد على ثلاثين يوماً قابلة للتجديد لمدة أو مدد أخرى مماثلة.

**Article 99 — appointment of experts:**

> إذا اقتضى التحقيق الاستعانة بخبير وجب على عضو النيابة العامة أن يصدر أمراً بندبه يفضل فيه المهمة التي يكلف بها، ويحلف الخبير اليمين أمام عضو النيابة العامة بأن يؤدي عمله بالأمانة والصدق ما لم يكن من فئات الخبراء الذين سبق أن أدوا اليمين قبل مزاولة أعمال الخبرة.

**Article 100 — deadline and replacement:**

> يحدد عضو النيابة العامة للخبير ميعاداً لتقديم التقرير، وله أن يستبدل به خبيراً آخر إذا لم يقدم التقرير في الميعاد المحدد.

**Article 101 — expert attendance:**

> يجوز لعضو النيابة العامة أن يحضر وقت مباشرة الخبير مهمته، ويجوز للخبير أن يؤدي مهمته بغير حضور الخصوم.

**Article 102 — party-appointed consultant:**

> يجوز للخصوم أن يستعينوا بخبير استشاري، ولهم أن يطلبوا تمكينه من الاطلاع على الأوراق وسائر ما سبق تقديمه للخبير المنتدب من قبل النيابة العامة، على ألا يترتب على ذلك تأخير السير في الدعوى.

**Article 103 — challenge to expert:**

> يجوز للخصوم إذا وجدت أسباب قوية تدعو لذلك، ويقدم طلب الرد مبيناً فيه أسبابه إلى عضو النيابة العامة للفصل فيه خلال ثلاثة أيام من يوم تقديمه.

**Article-number/OCR note:** the official PDF OCR displays the arrest-outside-flagrante provision after the separate Articles 24–27 judicial-police section with a second “مادة (٢٧)” label. The sequence and prior transcription identify this arrest provision as Article 37, not a second Article 27. Preserve the OCR anomaly and visually collate the Gazette image before final normalization. The article numbering is not to be silently duplicated.

### L2. Current Criminal Procedure Law 150/1950 — expert and evidence provisions

Full Arabic secondary text:
- https://alhasswalawfirm.com/law-library/law-150-1950
- https://www.notariesofegypt.org/article.php?id=432
- https://www.manshurat.org/node/14676

**Article 86 — expert oath and written report:**

> يجب على الخبراء أن يحلفوا أمام قاضي التحقيق يميناً على أن يبدوا رأيهم بالذمة وعليهم أن يقدموا تقريرهم كتابة.

**Article 87 — report deadline / replacement:**

> يحدد قاضي التحقيق ميعاداً للخبير ليقدم تقريره فيه، وللقاضي أن يستبدل به خبيراً آخر إذا لم يقدم التقرير في الميعاد المحدد.

**Article 88 — defence expert:**

> للمتهم أن يستعين بخبير استشاري ويطلب تمكينه من الاطلاع على الأوراق وسائر ما سبق تقديمه للخبير المعين من قبل القاضي، على ألا يترتب على ذلك تأخير السير في الدعوى.

**Article 89 — expert challenge:**

> للخصوم رد الخبير إذا وجدت أسباب قوية تدعو لذلك، ويقدم طلب الرد إلى قاضي التحقيق للفصل فيه، ويجب أن تبين فيه أسباب الرد. وعلى القاضي الفصل فيه في مدة ثلاثة أيام من يوم تقديمه.  
> ويترتب على هذا الطلب عدم استمرار الخبير في عمله إلا في حالة الاستعجال بأمر من القاضي.

These are the currently applicable expert provisions until Law 174/2025 commences, subject to intervening amendments and lawyer review. The corresponding future code provisions are Arts 99–103 (see L1).

### L3. Experts before judicial authorities — Decree-Law 96/1952 and Law 91/2016

**Full text / metadata:**
- Eastlaws: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/26-06-1952/no-96?id=800&type=1
- Manshurat PDF record: https://manshurat.org/node/38162

Decree-Law 96/1952, issued 20 June 1952, published 26 June 1952; amended by Law 91/2016 (Gazette No. 50 bis (d), 21 December 2016; effective 22 December 2016).

**Article 1 — recognized expert categories:**

> يقوم بأعمال الخبرة أمام جهات القضاء خبراء الجدول الحاليون وخبراء وزارة العدل ومصلحة الطب الشرعي والمصالح الأخرى التي يعهد إليها بأعمال الخبرة، وكل من ترى جهات القضاء عند الضرورة الاستعانة برأيهم الفني من غير من ذكروا.

**Article 50 — judicial appointment:**

> لجهات القضاء أن تندب للقيام بأعمال الخبرة خبيراً أو أكثر من خبراء الجدول، أو تندب مكتب خبراء وزارة العدل أو قسم الطب الشرعي أو إحدى المصالح الأخرى المعهود إليها بأعمال الخبرة فإذا رأت الظروف خاصة أن تندب من غير هؤلاء وجب أن تبين ذلك في الحكم، وفي مواد الضرائب لا يقع الندب إلا لخبراء وزارة العدل.

**Law 91/2016 Article 1:**

> تُستبدل عبارة (مساعد أول وزير العدل) بعبارة "الوكيل الدائم لوزارة العدل" أينما وردت في المرسوم بقانون رقم ٩٦ لسنة ١٩٥٢ بشأن تنظيم الخبرة أمام جهات القضاء.

Law 91/2016 is an administrative amendment to the expert statute; it does not replace the substantive expert appointment and report provisions.

### L4. Judicial Authority Law 46/1972 — prosecution and judicial police

**Full Arabic text (secondary, with amendment notes):**
- https://manshurat.org/node/63718
- https://lawhub.info/eg/?p=16481

Current copy says last amendment 26 June 2019 by Law 77/2019. The law contains the institutional basis for Public Prosecution supervision and judicial-police subordination.

**Article 21 — Public Prosecution exclusive authority:**

> تُمارِس النيابة العامة الاختصاصات المخولة لها قانوناً، ولها دون غيرها الحق في رفع الدعوى الجنائية ومباشرتها ما لم ينص القانون على خلاف ذلك.

**Article 22 — judicial police subordination:**

> مأمورو الضبط القضائي يكونون فيما يتعلق بأعمال وظائفهم تابعين للنيابة العامة، ويجوز لها عند الضرورة تكليف معاون النيابة تحقيق قضية بأكملها.

**Article 27 — prison supervision:**

> تتولى النيابة العامة الإشراف على السجون وغيرها من الأماكن التي تنفذ فيها الأحكام الجنائية ويحيط النائب العام وزير العدل بما يبدو للنيابة العامة من ملاحظات في هذا الشأن.

**Article 134 — expert statute cross-reference:**

> يُنظم القانون الخبرة أمام جهات القضاء ولدى النيابة العامة ويحدد حقوق الخبراء وواجباتهم وطريقة تأديبهم.

**Law 77/2019** (Gazette 25 bis (b), 26 June 2019; effective 27 June 2019) amends Law 46/1972 among other laws, including the appointment framework for the Public Prosecutor. Text: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/26-06-2019/no-77?id=1944174&sub=9636789&type=1

Law 142/2006 is another material amendment to Law 46/1972 and appears in the amendment annotations for Arts 22, 24, 26, 27 and other provisions. The complete amendment chronology must be extracted before relying on a consolidated version.

### L5. Minister of Justice Decision 3066/2021 — economic-court experts

**Official Gazette text copy:** Waqa'i' No. 123, 3 June 2021, pages 3–6:  
https://media.elbalad.news/2024/10/large/877/0/789.pdf

Decision 3066/2021 issues rules for the work and engagement of experts registered in the Economic Courts' expert tables. It is not a general criminal-procedure rule, but is relevant to expert evidence in financial/economic offences.

**Article 2 — appointment:**

> للمحكمة، أو هيئة التحضير، أو إدارة الإفلاس، أو قضاة دائرة الإفلاس، أو الأوامر، أو التنفيذ، أو المستعجل بالمحاكم الاقتصادية عند الاقتضاء ندب خبير أو أكثر من جدول خبراء المحاكم الاقتصادية للقيام بمهام محددة يستلزم بحثها الاستعانة بالخبرة الفنية.

**Article 4 — electronic expert register and appointment:**

> ينشأ سجل إلكتروني لقيد الخبراء داخل النظام الإلكتروني للتقاضي أمام المحاكم الاقتصادية، ويعين الخبير صاحب الدور إلكترونياً من خلال هذا النظام، وتبلغ جهة الندب بالمحكمة الاقتصادية إلكترونياً بهذا التعيين خلال ٢٤ ساعة التالية لإيداع أمانة الخبير خزانة المحكمة.

**Article 7 — expert electronic signature:**

> يجب أن يكون للخبير المقيد أمام المحكمة الاقتصادية توقيع إلكترونى صالح للاستخدام، ولا يجوز تعيين الخبير أو الاستعانة به إلا فى حال توافر وصلاحية التوقيع الإلكترونى...

**Article 8 — video conference meetings:**

> ويجوز له الاجتماع بهم عن طريق خاصية الفيديو كونفرانس وفقاً للتقنية الفنية والإلكترونية التى تتوافق مع نظام التقاضى الإلكترونى أمام المحاكم الاقتصادية فى حال صدور موافقة كتابية بذلك من الخصوم ترفق بملف تقرير الخبرة.

**Article 9 — signed digital expert report:**

> يلتزم الخبير المعين بتحرير محاضر الأعمال والتقرير على الحاسب الآلي ويتم إيداع نسخة ورقية منه ممهورة بتوقيع الخبير أو لجنة الخبراء في ملف الدعوى ويتم تسليم نسخة رقمية موقعة إلكترونياً من الخبير المعين أو من الخبراء أعضاء لجنة الخبراء مجتمعين وذلك للقلم المختص باستلام الملفات الرقمية بأي من المحاكم الاقتصادية مرفقاً بها تسجيل لجلسات الفيديو كونفرانس الخاصة باجتماعاته مع أطراف النزاع.

This is a particularly useful procedural source for authenticity, signature and preservation of electronic expert reports in economic-court matters. Decision 367/2021 in the same Gazette (No. 123, 3 June 2021) sets fees and expenses for economic-court experts and repeals Decision 3997/2009.

### L6. Forensic document examination / expert offices — 2026 decisions

**Minister of Justice Decision 439/2026**
- Gazette: Waqa'i' No. 38, 16 February 2026.
- Issued 25 January 2026; effective 31 January 2026.
- Official Amiri Printing Presses text: https://www.alamiria.com/Sec/TashTxt?id=F9RwWnqSQgc%3D
- SIS Gazette PDF: https://mediadr.sis.gov.eg/xmlui/bitstream/handle/123456789/121095/WQ38_20260216_3241.pdf?sequence=2

**Article 1:**

> ينقل مقر الإدارة العامة لشئون أبحاث التزييف والتزوير بالجيزة الكائن بديوان عام وزارة العدل بلاظوغلى إلى مقرها الجديد بمجمع مصالح وزارة العدل - حى السيدة زينب - محافظة القاهرة.

This is an administrative location change for the General Department for Forgery and Counterfeiting Research, not a change to evidentiary standards.

**Minister of Justice Decision 440/2026** in the same Gazette issue moves the Central Cairo Experts Office to the new premises at the Experts Department, 2B, 23 July Street, Abbassia. Official text: https://www.alamiria.com/Sec/TashTxt?id=pkBhei+HAPU%3D

No separate comprehensive Forensic Medicine Act was identified in this pass. The statutory expert framework remains Decree-Law 96/1952 and the criminal-procedure provisions governing expert appointment, reports, oath, challenge and defence expert access.

### L7. Evidence and investigation corrections / version mapping

1. Until 1 October 2027, use Law 150/1950 as the current procedure-code source, including Arts 86–89 on experts; Law 174/2025 Arts 99–103 are future provisions.
2. Law 174/2025 Arts 24–27 describe judicial-police duties, categories and evidence preservation; do not activate them before commencement.
3. Law 174/2025 Art. 80 requires a reasoned order from the competent judge for monitoring specified communications, private social-media content, email, messages, devices and private conversations, for periods not exceeding 30 days per order.
4. Law 174/2025 Art. 81 creates a separate targeted monitoring route for specified offences and requires strong evidence, a technical report and a victim complaint.
5. Cybercrime Law 175/2018 Art. 11 remains the specific criminal digital-evidence rule, subject to technical conditions in PM Decree 1699/2020 Art. 9. Electronic Signature Law 15/2004 Arts 14–15 have a different civil/commercial/administrative scope.
6. Law 96/1952 Art. 1 and Art. 50 establish recognized expert categories and judicial appointment sources; Law 46/1972 Art. 134 cross-refers to the expert statute.
7. Minister of Justice Decision 3066/2021 applies only to Economic Courts' registered experts; it does not automatically govern all criminal forensic experts.
8. Decisions 439/2026 and 440/2026 are administrative location changes, not amendments to substantive expert or evidence rules.

## M. Progress update — evidence and expert rules

**Estimated criminal-law domain completion: 55%** (up from 52%; approximate research-progress estimate).

This pass adds the expert statute, judicial authority statute, expert amendments and current ministerial decisions, plus selected exact Arabic provisions from the old and future criminal procedure codes covering:
- judicial-police authority and subordination;
- report intake, scene examination and preservation;
- seizure, sealing and chain of custody;
- communications and digital-content monitoring;
- expert appointment, written reports, defence experts and challenge;
- economic-court expert e-signatures and video-conference records.

**Full Arabic text accessible at source:** further expanded.  
**Full official files locally archived and hash-verified:** still 0 in this session.  
**Article-level full extraction:** incomplete; selected articles now persisted.  
**Lawyer verification:** 0%.  
**Whole-project coverage:** not computable without the master-index denominator.


---

## N. Criminal Procedure Law 150/1950 — amendment chronology correction and new Arabic texts

### N1. Critical correction: the 2020 amendment is Law 177/2020, not Law 189/2020

A secondary copy of Law 150/1950 on Manshurat displays “last amendment: 5 September 2020 by Law 189/2020”. This is a misattribution.

- **Law 177/2020** is the actual amendment to Criminal Procedure Law 150/1950.
- It adds Article 113 bis protecting the identity/data of victims in specified sexual and child offences.
- Gazette: No. 36 bis, 5 September 2020.
- Effective: 6 September 2020.
- Full Arabic text: https://www.aldhshan.com/2026/02/177-2020-150-1950.html
- Manshurat PDF record: https://manshurat.org/node/67605

**Article 1 — new Article 113 bis:**

> لا يجوز لمأموري الضبط أو جهات التحقيق الكشف عن بيانات المجنى عليه فى أى من الجرائم المنصوص عليها فى الباب الرابع من الكتاب الثالث من قانون العقوبات الصادر بالقانون رقم ٥٨ لسنة ١٩٣٧، أو فى أى من المادتين (٣٠٦ مكرراً / أ ، ٣٠٦ مكرراً / ب) من ذات القانون، أو فى المادة (٩٦) من قانون الطفل الصادر بالقانون رقم ١٢ لسنة ١٩٩٦، إلا لذوى الشأن.

**Law 189/2020 is not a Criminal Procedure amendment.** It amends the Penal Code by adding Article 309 bis (b) on bullying. Its full Arabic text is separately identified at https://manshurat.org/node/67632 and its source reproduction: https://www.eglf.org/عقوبة-التنمر-في-القانون-المصري-189-لسنة-2020/

Do not copy the 189/2020 label from the Manshurat CPL page into the Criminal Procedure amendment chain.

### N2. Current amendment chronology — known instruments

This is an acquisition chronology, not yet an exhaustive article-by-article consolidation. The Manshurat relations page for Law 150/1950 identifies the following historical amendments; the later full-text sources confirm additional instruments.

| Instrument | Main amendment / subject | Arabic source state |
|---|---|---|
| Law 271/1955 | Amends Art. 550 (execution) | Metadata / relation identified; full text pending |
| Law 107/1962 | Amends Art. 151 and related provisions | Metadata / relation identified; full text pending |
| Law 37/1972 | Amends Art. 143 (pre-trial detention) | Full provision notes in consolidated text |
| Law 23/1992 | Amends CPL | Metadata / relation identified; full text pending |
| Law 95/2003 | Repeals State Security Courts and amends CPL; adds Art. 206 bis and related financial-crime measures | Full text source required |
| Law 145/2006 | Pre-trial detention, alternatives and Art. 206 bis | Official PDF record and full secondary text |
| Law 74/2007 | Amends Arts 18 bis, 297, 323, 324, 325 bis, 327 and 398; reconciliation/appeal procedure | Full Gazette reproduction |
| Law 71/2009 | Mental Health Care Law; consequential changes to CPL and Penal Code | Full Arabic text and Gazette source |
| Law 83/2013 | Amends Art. 143 pre-trial detention in death/life-imprisonment cases | PDF record located |
| Law 49/2014 | Amends Art. 479 CPL alongside Penal Code and Prisons Law | Full Gazette text |
| Law 138/2014 | Replaces Arts 64, 65 and 74; adds Art. 66; judicial investigation delegation | Full Arabic text and PDF record |
| Law 16/2015 | Amends Art. 15; adds Arts 18 bis (b) and 208 bis (e) | Full Arabic text and PDF record |
| Law 11/2017 | Replaces Arts 12, 277, 289, 384 and 395 | Official Gazette PDF and full text |
| Law 177/2020 | Adds Art. 113 bis victim-identity protection | Full Arabic text |
| Law 1/2024 | Felony appeal / two-tier adjudication; new appellate chapters and Arts 367, 419 bis et seq. | Official Gazette PDF and full Arabic text |

**Core relation page:** https://manshurat.org/node/14419/relations  
It lists the historical amendments, including Laws 271/1955, 107/1962, 37/1972, 23/1992, 95/2003, 145/2006, 74/2007, 71/2009, 83/2013, 49/2014, 138/2014, 16/2015, 11/2017 and 177/2020. Law 1/2024 is the subsequent amendment.

### N3. Full amendment texts newly located

#### Law 95/2003

- Full PDF/source relation: https://manshurat.org/node/14419/relations
- Adds Article 206 bis, authorizing specified senior prosecutors to exercise investigating-judge powers in defined categories of felonies; also adds/changes financial precautionary measures in Arts 208 bis (a)–(e).
- Gazette No. 25 follow-up, 19 June 2003.
- Full original Gazette scan still to be obtained and visually collated.

#### Law 145/2006 — pre-trial detention

- Gazette metadata and PDF: https://manshurat.org/node/14577
- Issued 15 July 2006; published 27 July 2006; effective 28 July 2006.
- Amends Art. 201 and related pre-trial detention provisions; adds alternative measures to detention such as remaining at a specified residence, reporting to police at specified times, and prohibitions on visiting specified places.
- Art. 143's detention-duration rules were also amended by Law 37/1972 and later Law 153/2007; preserve the full sequence.

#### Law 74/2007

- Gazette No. 22 follow-up, 31 May 2007.
- Full Arabic text: https://www.laweg.net/framePlain.aspx?ItemID=18326&NID=18336&Type=6&action=ViewActivePages
- Replaces Arts 18 bis, 297, 323, 324, 325 bis (first and second paragraphs), 327 (first paragraph) and 398 (first paragraph).

**Article 1 opening:**

> يستبدل بنصوص المواد 18 مكرراً، 297، 323، 324، 325 مكرراً (الفقرتان الأولى والثانية)، 327 (فقرة أولى)، 398 (فقرة أولى) من قانون الإجراءات الجنائية، النصوص الآتية:

#### Law 71/2009 — Mental Health Care Law and consequential amendments

- Gazette No. 20 follow-up, 14 May 2009; effective 15 May 2009.
- Full Arabic text: https://www.laweg.net/framePlain.aspx?ItemID=91349&NID=111486&Type=6&action=ViewActivePages
- Manshurat PDF record: https://manshurat.org/node/14473
- Replaces terminology in CPL concerning mental illness / mental disorder and provides rules relevant to detention, examination and trial of persons with mental disorders.

#### Law 83/2013 — detention duration for death/life cases

- Issued and published 23 September 2013; effective 24 September 2013.
- Manshurat PDF record: https://manshurat.org/node/6546
- Amends Art. 143 concerning the maximum period of pre-trial detention in cases where the charged offence carries death or life imprisonment.

#### Law 49/2014

- Gazette No. 23 follow-up, 5 June 2014; effective 6 June 2014.
- Full Arabic text: https://www.laweg.net/framePlain.aspx?ItemID=91349&NID=111486&Type=6&action=ViewActivePages (cross-reference; verify exact Law 49 record before using this URL)
- Eastlaws metadata and text: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/05-06-2014/no-49?id=1759016&type=1
- Replaces CPL Art. 479 together with Penal Code Art. 18(2) and Prisons Law Art. 52(1).

#### Law 138/2014

- Issued 11 November 2014; Gazette 45 bis (c), 12 November 2014; effective 13 November 2014.
- Full Arabic text: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/12-11-2014/no-138?id=1771683&sub=8630302&type=1
- Manshurat PDF record: https://manshurat.org/node/14421
- Replaces Arts 64, 65 and 74; adds Art. 66 concerning delegation of judicial investigations.

#### Law 16/2015

- Gazette No. 11 follow-up, 12 March 2015; effective 13 March 2015.
- Full Arabic text: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/12-03-2015/no-16?id=1780988&sub=8694489&type=1
- Manshurat PDF record: https://manshurat.org/node/14420

**Article 1 — limitation period for public officials:**

> تستبدل بالفقرة الثالثة من المادة (١٥) من قانون الإجراءات الجنائية الفقرة الآتية:  
> ومع عدم الإخلال بأحكام الفقرتين السابقتين لا تبدأ المدة المسقطة للدعوى الجنائية في الجرائم المنصوص عليها في البابين الثالث والرابع من الكتاب الثاني من قانون العقوبات والتي تقع من موظف عام إلا من تاريخ انتهاء الخدمة أو زوال الصفة ما لم يبدأ التحقيق فيها قبل ذلك.

**Article 2** adds Articles 18 bis (b) and 208 bis (e). The complete text must be parsed; do not assume the amendments are only limitation-related.

#### Law 11/2017

- Gazette No. 17 follow-up, 27 April 2017; effective 28 April 2017.
- Official Gazette PDF hosted by FRA: https://fra.gov.eg/wp-content/uploads/2017/04/alamiria_2017_11.pdf
- Full text: https://lawyeregypt.net/قانون-رقم-11-لسنة-2017-بشأن-تعديل-بعض-أحكام-ق-2/
- Eastlaws: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/27-04-2017/no-11?id=1871703&type=1

**Article 1** replaces CPL Arts 12, 277, 289, 384 and 395. It also amends the Court of Cassation Appeals Law, Terrorist Lists Law 8/2015 and Anti-Terrorism Law 94/2015.

#### Law 177/2020

See N1. Adds Article 113 bis and protects victim identity in specified offences. Do not confuse it with Law 189/2020 (Penal Code bullying).

#### Law 1/2024 — felony appeals

- Gazette No. 2 bis, 16 January 2024; effective 17 January 2024.
- Official SIS-hosted Gazette PDF: https://mediadr.sis.gov.eg/bitstream/handle/123456789/51750/OG2_20240116_1055.pdf?isAllowed=y&sequence=2
- Manshurat PDF: https://manshurat.org/sites/default/files/qnwn_rqm_1_lsn_2024.pdf
- Eastlaws full text: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/16-01-2024/no-1?id=2106397&type=1

It changes terminology throughout the CPL and replaces the first two chapters of Book II, Title III to create a felony-appeal system. It adds provisions including Article 367 and Articles 419 bis et seq. The original Gazette PDF should be article-split and compared with the consolidated current Law 150 text.

### N4. Article 113 bis and the future code — transition

- Law 177/2020 Article 113 bis is part of the current Law 150/1950 text until 1 October 2027, subject to any further legislation.
- Law 174/2025 contains victim-protection and witness rules in its own code, but these are future provisions until commencement.
- Do not treat Law 177/2020 as a general anonymity rule for all victims; its scope is the specific offences listed in the article.
- Law 1/2024 felony appeals apply from 17 January 2024; Law 174/2025 issuance Article 3 contains a transitional rule tied to proceedings not decided from the Law 1/2024 date.

### N5. Date discrepancy — original Law 150/1950

The original publication metadata remains conflicting:
- Manshurat record: publication 15 October 1950; commencement 14 November 1950.
- Eastlaws record: publication 15 October 1951; commencement 14 November 1951.
- Both identify issuance on 3 September 1950 and Waqa'i' No. 90.

Do not lock 1950 or 1951 without inspecting the original Waqa'i' No. 90. The prior dossier's 1951 date is not confirmed; the Manshurat 1950 metadata is also not independently verified against the Gazette image.

### N6. Status update

The Criminal Procedure Law 150/1950 amendment chain is materially more complete than the v0.1 dossier. The high-priority missing original instruments are now Law 95/2003, Law 145/2006, Law 83/2013, Law 49/2014, Law 138/2014, Law 16/2015, Law 11/2017, Law 177/2020 and Law 1/2024. Several are already accessible as full Arabic texts or Gazette PDFs; the remaining older amendment candidates are metadata-only and must be separated from verified text.


### N7. Law 1/2024 — selected exact provisions on felony appeals

The full 33-article Arabic text is accessible from the SIS-hosted Gazette PDF and a full secondary transcription:
- Official Gazette PDF: https://hrightsstudies.sis.gov.eg/media/9281/القانون-رقم-1-لسنة-2024-بتعديل-قانون-الا-جرا-ءات-الجنا-ي-ية.pdf
- SIS Gazette record: https://mediadr.sis.gov.eg/handle/123456789/51750
- Full 33-article text: https://alhasswalawfirm.com/law-library/law-1-2024

**Article 1** also substitutes terminology in multiple CPL provisions and replaces the second paragraph of Art. 151. The new Art. 151 paragraph provides that, outside the court term, the matter is handled by the Misdemeanour Appeal Court sitting in chambers when referring to a first-instance felony court or appealing before the felony appeal court.

**Article 3 — new felony-appeal chapter:**

> يضاف عنوان «الفصل الأول: فى استئناف مواد الجنح» إلى عنوان الباب الثانى «فى الاستئناف» من الكتاب الثالث من قانون الإجراءات الجنائية، كما يضاف إلى الباب الثانى من الكتاب الثالث من قانون الإجراءات الجنائية فصل ثانى بعنوان (فى استئناف مواد الجنايات) يتضمن المواد أرقام ٤١٩ مكرراً، ٤١٩ مكرراً ١، ٤١٩ مكرراً ٢، ٤١٩ مكرراً ٣، ٤١٩ مكرراً ٤، ٤١٩ مكرراً ٥، ٤١٩ مكرراً ٦، ٤١٩ مكرراً ٧، ٤١٩ مكرراً ٨، ٤١٩ مكرراً ٩، نصوصها الآتية:

**Article 419 bis:**

> لكل من النيابة العامة والمتهم أن يستأنف الأحكام الحضورية الصادرة من محكمة جنايات أول درجة.

**Article 419 bis (1):**

> يجوز استئناف الأحكام الصادرة فى الدعوى المدنية من محكمة جنايات أول درجة من المدعى بالحقوق المدنية أو المسئول عنها أو المتهم فيما يختص بالحقوق المدنية وحدها، إذا كانت التعويضات المطلوبة تزيد على النصاب الذى تحكم فيه المحكمة الابتدائية نهائياً.

**Article 419 bis (2):**

> يجوز للنيابة العامة أن تستأنف الأحكام الغيابية الصادرة فى مواد الجنايات.

**Article 419 bis (3):**

> يُتبع فى نظر الاستئناف والفصل فيه جميع الأحكام المقررة للاستئناف فى مواد الجنح، ما لم ينص القانون على خلاف ذلك.

**Article 419 bis (4) — appeal time limits:**

> يحصل الاستئناف بتقرير فى قلم كتاب المحكمة التى أصدرت الحكم، وذلك خلال أربعين يوماً من تاريخ صدور الحكم.  
> فإذا كان الاستئناف مرفوعاً من هيئة قضايا الدولة يجب أن يكون التقرير موقعاً من مستشار بها على الأقل.  
> وإذا كان مرفوعاً من النيابة العامة فيجب أن يكون التقرير موقعاً من محام عام على الأقل.  
> وللنائب العام أن يستأنف الحكم خلال ستين يوماً من تاريخ صدوره، وله أن يقرر بالاستئناف فى قلم كتاب المحكمة المختصة بنظر الاستئناف.

**Article 419 bis (7) — order of oral submissions:**

> تسمع المحكمة أقوال المستأنف، والأوجه التى يستند إليها فى استئنافه، وأوجه دفاعه ودفوعه، كما تسمع باقى الخصوم، على أن يكون المتهم آخر من يتكلم.

**Article 419 bis (8) — death sentence:**

> إذا كان الحكم صادراً حضورياً بعقوبة الإعدام، ولم يجر استئنافه خلال الميعاد المقرر قانوناً، وجب على النيابة العامة اتباع حكم المادة ٤٦ من قانون حالات وإجراءات الطعن أمام محكمة النقض الصادر بالقانون رقم ٥٧ لسنة ١٩٥٩.

**Article 419 bis (9) — execution pending appeal:**

> لا يترتب على استئناف الحكم الصادر من محكمة جنايات أول درجة وقف تنفيذ الحكم، إلا إذا رأت محكمة الجنايات المستأنفة وقف التنفيذ، أو كان الحكم صادراً بالإعدام.  
> وإذا تخلف المحكوم عليه أو وكيله بغير عذر عن الحضور في الجلسة المحددة لنظر استئنافه أو في أى جلسة تالية تندب له المحكمة محامياً للدفاع عنه وتفصل في الاستئناف.

**Article 4 — transition:**

> لا تسري أحكام هذا القانون إلا على الدعاوى التي لم يُفصل فيها من محاكم الجنايات اعتباراً من تاريخ العمل بهذا القانون.

**Article 5 — commencement:**

> ينشر هذا القانون في الجريدة الرسمية، ويعمل به اعتباراً من اليوم التالي لتاريخ نشره.

This amendment commenced 17 January 2024. Law 174/2025 issuance Article 3 separately protects the transitional position of cases not decided by felony courts from the date Law 1/2024 came into force. Keep both transition rules in the version model.

---

## O. Penal Code 58/1937 — additional 2021 amendments and post-2023 check

### O1. Current amendment chronology update

The Penal Code amendment chain now includes these later instruments, in addition to the earlier annotations and Law 185/2023:

| Instrument | Subject / articles | Source state |
|---|---|---|
| Law 189/2020 | Adds Art. 309 bis (b), bullying | Full Gazette PDF text accessible |
| Law 10/2021 | Replaces Arts 242 bis and 242 bis (a), female genital mutilation | Full Arabic Gazette text accessible |
| Law 71/2021 | Adds Art. 186 bis, unauthorized recording/publication of criminal trial sessions | Full Arabic Gazette text accessible |
| Law 141/2021 | Replaces Arts 306 bis (a) and 306 bis (b), sexual harassment | Full official Gazette PDF hosted by DSpace / text accessible |
| Law 150/2021 | Replaces Art. 80(a), state secrets / national defence information | Full Arabic Gazette PDF hosted by DSpace |
| Law 185/2023 | Replaces Art. 306 bis (a), Art. 306 bis (b) second paragraph and Art. 309 bis (b) third paragraph | Full Arabic text and Gazette PDF record accessible |

**No Penal Code amending statute after Law 185/2023 was identified in this pass through 19 November 2026.** This is a negative search result, not proof that no such instrument exists. Recheck the Official Gazette before treating 185/2023 as the definitive latest amendment.

### O2. Law 10/2021 — female genital mutilation

- Gazette No. 16 bis (w), 28 April 2021; effective 29 April 2021.
- Full Gazette text: https://www.elmodawanaeg.com/wp-content/uploads/2021/08/10.pdf
- Eastlaws: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/28-04-2021/no-10?id=2016749&sub=10227115&type=1

**Article 1 (opening):**

> يستبدل بنصي المادتين (٢٤٢ مكرراً) و(٢٤٢ مكرراً/أ) من قانون العقوبات، النصان الآتيان:

**New Article 242 bis (opening):**

> يعاقب بالسجن مدة لا تقل عن خمس سنوات كل من أجرى ختاناً لأنثى بإزالة أي جزء من أعضائها التناسلية الخارجية بشكل جزئي أو تام أو ألحق إصابات بتلك الأعضاء، فإذا نشأ عن ذلك الفعل عاهة مستديمة تكون العقوبة السجن المشدد مدة لا تقل عن سبع سنوات، أما إذا أفضى الفعل إلى الموت تكون العقوبة السجن المشدد لمدة لا تقل عن عشر سنوات.

The amendment increases penalties and provides aggravated consequences where the perpetrator is a physician or nursing professional, including professional-practice disqualification and closure consequences.

### O3. Law 71/2021 — recording criminal trial sessions

- Gazette No. 23 bis, 13 June 2021; effective 14 June 2021.
- Full Arabic text: https://lawyeregypt.net/قانون-تسجيل-أو-تصوير-جلسة-محاكمة-71-لسنة-2021/
- PDF: https://kanonmisr.com/ar/wp-content/uploads/2021/06/القانون-71-لسنة-2021-بتعديل-بعض-أحكام-قانون-العقوبات-1.pdf

**Article 1 — new Article 186 bis:**

> مع عدم الإخلال بأي عقوبة أشد يعاقب بغرامة لا تقل عن مائة ألف جنيه ولا تزيد على ثلاثمائة ألف جنيه كل من صور أو سجل كلمات أو مقاطع أو بث أو نشر أو عرض بأي طريق من طرق العلانية لوقائع جلسة محاكمة مخصصة لنظر دعوى جنائية دون تصريح من رئيس المحكمة المختصة بعد أخذ رأى النيابة العامة.  
> ويُحكم فضلاً عن ذلك بمصادرة الأجهزة أو غيرها مما يكون قد استخدم في الجريمة، أو ما نتج عنها، أو محو محتواها، أو إعدامه، بحسب الأحوال.  
> وتُضاعف الغرامة في حالة العـود.

This is directly relevant to criminal evidence and court-recording policy. It must be cross-linked with Law 174/2025's future rules on evidence, media and trial publicity.

### O4. Law 141/2021 — sexual harassment

- Gazette No. 32 bis (a), 15 August 2021; effective 16 August 2021.
- Full Arabic text: https://lawyeregypt.net/قانون-رقم-141-لسنة-2021-بتعديل-قانون-العقوبات/
- Official Gazette PDF record: https://dspace.id.com.eg/items/cdd29154-1f0e-4f12-86f6-0184791301c7
- Gazette text copy: https://serviceapi.egyptianlaws.com/Images/Index?T=1&folder=3&path=2021-8-15-2021-141.pdf

**Article 1** replaces Penal Code Arts 306 bis (a) and 306 bis (b), expressly including electronic means of communication and other technical means in the sexual-harassment offence.

**New Article 306 bis (a) (opening):**

> يعاقب بالحبس مدة لا تقل عن سنتين، ولا تجاوز أربع سنوات، وبغرامة لا تقل عن مائة ألف جنيه ولا تزيد عن مائتي ألف جنيه، أو بإحدى هاتين العقوبتين كل من تعرض للغير في مكان عام أو خاص، أو مطروق بإتيان أمور أو إيحاءات أو تلميحات جنسية، أو إيحائية سواء بالإشارة أو بالقول أو بالفعل بأية وسيلة بما في ذلك وسائل الاتصالات السلكية أو اللاسلكية أو الإلكترونية، أو أية وسيلة تقنية أخرى.

### O5. Law 150/2021 — state secrets

- Gazette No. 46 bis, 20 November 2021; effective 21 November 2021.
- Official DSpace record with Arabic PDF: https://dspace.id.com.eg/items/a6361f52-7211-435a-af37-a1da5f1b7408
- Eastlaws full article metadata: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/20-11-2021/no-150?id=2038708&sub=10327246&type=1
- Manshurat PDF record: https://manshurat.org/node/74640

**Article 1** replaces Penal Code Art. 80(a). The new provision concerns unlawful disclosure, publication or transmission of information relating to state secrets and national defence, including by information technology means, with aggravated consequences according to the circumstances.

The full Article 80(a) replacement text must be transcribed from the Gazette PDF and cross-referenced with the Cybercrime Law and the current National Security classification regime.

### O6. Law 189/2020 — bullying, corrected classification

- Gazette No. 36 bis (b), 5 September 2020; effective 6 September 2020.
- Full Gazette PDF text: https://www.elwatannews.com/data/iframe/pdf/1095256981600164645.pdf
- Manshurat: https://manshurat.org/node/67632

Adds Article 309 bis (b), criminalizing bullying based on use of force/control, exploitation of vulnerability or a characteristic such as sex, race, religion, physical description, health/mental condition or social status, for intimidation, ridicule, degradation or social exclusion. This is a Penal Code amendment, not a Criminal Procedure amendment.

### O7. Law 185/2023 — latest amendment identified

- Gazette No. 48 bis (b), 4 December 2023; effective 5 December 2023.
- Full Arabic text: https://mksegypt.org/public/ar/laws/17352
- Eastlaws: https://www.eastlaws.com/legislation-full-text/ar/egypt/law/04-12-2023/no-185?id=2102522&type=1
- PDF record: https://manshurat.org/content/tdyl-bd-hkm-qnwn-lqwbt-blqnwn-rqm-185-lsn-2023

Replaces:
- Art. 306 bis (a);
- Art. 306 bis (b), second paragraph;
- Art. 309 bis (b), third paragraph.

It increases penalties and aggravating circumstances for sexual harassment and specified exploitation/abuse contexts. This is the latest amendment identified in the present search, but a 2024–2026 Gazette sweep remains required.



## P. Current consolidated progress — 19 November 2026

- **Estimated assigned criminal-law domain completion: 58%** (rough research rubric; not article-count completeness).
- **Inventory:** 166 unique document records, including 81 new records added in this session.
- **Acquisition queue:** 24 active collection tasks.
- **Cross-check register:** 19 discrepancy/source-audit entries.
- **Complete Arabic texts accessible at source:** more than 20 laws, codes, treaties and implementing instruments; selected article text has been persisted throughout this dossier.
- **Official files locally archived and SHA-256 verified in this session:** 0.
- **Egyptian lawyer-verified records:** 0.
- **Contribution to total Egyptian legal knowledge coverage:** not computable without the master index denominator and weighting method.



---

## Q. Acquisition pass — AML, child justice, prisons, narcotics schedules
**Research date:** 19 November 2026  
**Method:** acquired readable Arabic text and original Gazette/regulator PDF access paths; no restricted source bypassed. The sources below are browser-readable, not locally archived or hash-verified. Source permission for storage, indexing, display and redistribution remains unknown.

### Q1. Anti-Money Laundering Law — Law 80/2002 and amendments

**New source acquisition:** FRA-hosted updated Arabic Law 80/2002 PDF, Gazette-origin legal text and amendment annotations:
- Updated Law 80/2002 text: https://fra.gov.eg/wp-content/uploads/2024/05/قانون.pdf
- Official Gazette copy of Law 154/2022: https://dspace.id.com.eg/server/api/core/bitstreams/1fe32968-2f23-489d-9045-5a4032fdd9c3/content
- FRA consolidated Executive Regulations (1448 extracted lines, current through 3331/2023): https://fra.gov.eg/wp-content/uploads/2024/06/لائحة-القانون-وفقا-لاخر-تعديل-الاصدار.pdf
- FRA further hosted consolidated regulation copy: https://fra.gov.eg/wp-content/uploads/2025/04/اللائحة-التنفيذية-لقانون-مكافحة-غسل-الأموال-1-1.pdf
- Official Gazette PDF, PM Decree 3331/2023: https://fra.gov.eg/wp-content/uploads/2023/09/3331.pdf
- PM Decree 457/2020, Gazette issue 8 bis (23 February 2020): https://www.laweg.net/framePlain.aspx?ItemID=115318&NID=142337&Type=6&action=ViewActivePages

**Statutory amendment chain now cross-confirmed:** Laws 78/2003, 181/2008, Decree-Law 36/2014, Law 17/2020 and Law 154/2022. The FRA 2022 consolidation itself contains article-level amendment annotations. Law 154/2022 adds, among other things, Art. 3 bis (executive director), Art. 9 bis 1 (targeted financial sanctions implementation), and Art. 17 bis 1 (parallel financial investigations).

**Executive regulation amendment chain resolved:** PM Decrees 1463/2006, 2367/2008, 1569/2016, 2910/2019, 457/2020 and 3331/2023. The FRA portal's short “previous legislation” list omitted 457/2020, but the current FRA consolidated PDF expressly annotates Art. 1 as amended by 457/2020 and its footnote lists Gazette issue 13 bis (e), 31 March 2020; the Laweg full text identifies Decree 457/2020 and Gazette issue 8 bis, 23 February 2020. Treat the 457/2020 instrument's issuance/publication-date discrepancy as an audit item: Laweg and multiple transcriptions say 23 February / issue 8 bis, while the FRA 2024 consolidated PDF's amendment footnote says issue 13 bis (e), 31 March 2020. Do not silently harmonize this.

**Exact Arabic excerpts — Law 80/2002 (FRA updated text):**

Article 2 opening:

> يعد مرتكبا لجريمة غسل الأموال كل من علم أن الأموال متحصلة من جريمة أصلية، وقام عمدا بأي مما يلي:
> 1- تحويل متحصلات أو نقلها، وذلك بقصد إخفاء المال أو تمويه طبيعته أو مصدره أو مكانه أو صاحبه أو صاحب الحق فيه أو تغيير حقيقته أو الحيلولة دون اكتشاف ذلك أو عرقلة التوصل إلى مرتكب الجريمة الأصلية.

Article 4 opening:

> تختص الوحدة بتلقي الإخطارات الواردة من المؤسسات المالية وأصحاب المهن والأعمال غير المالية، عن العمليات التي يشتبه في أنها تشكل متحصلات أو تتضمن غسل الأموال أو الأصول أو تمويل الإرهاب أو محاولات القيام بهذه العمليات.

Article 8 opening:

> تلتزم المؤسسات المالية وأصحاب المهن والأعمال غير المالية بإخطار الوحدة فوراً عن أي من العمليات التي تشتبه في أنها تشكل متحصلات أو تتضمن غسل الأموال أو الأصول أو تمويل الإرهاب، أو محاولات القيام بهذه العمليات أيا كانت قيمتها...

Article 9 provides a minimum five-year retention period for relevant transaction records and customer/beneficial-owner data, measured from termination of the relationship or account closure, subject to longer retention requests.

Article 17 bis provides for precautionary freezing/seizure measures on request by the AML Unit's board chair, with reference to CPL Arts. 208 bis (a) through (e). Article 17 bis 1 requires parallel financial investigations by law-enforcement and investigative authorities in money-laundering, predicate-offence and terrorist-financing cases.

**Exact Arabic excerpt — Executive Regulations, Art. 2 bis added by Decree 3331/2023:**

> تعد جريمة غسل الأموال جريمة مستقلة عن الجريمة الأصلية، بحيث لا يشترط أن يتم إدانة الشخص بارتكاب الجريمة الأصلية مسبقاً من أجل اعتبار الأموال أو الأصول متحصلات إجرامية.

Decree 3331/2023 was published in Official Gazette No. 35 follow-up (a), 31 August 2023, and Article 3 makes it effective the following day (1 September 2023). Article 1 replaces a long list of existing regulation provisions; Article 2 adds new provisions including Arts. 2 bis, 2 bis (a), 3 bis and subparagraphs, 28 bis and subparagraphs, 29 bis, 31 bis, 43 bis (d), 50 bis and subparagraphs, and 53 bis and subparagraphs. The new Art. 28 bis requires parallel financial investigations; Art. 28 bis (a) allows money-laundering/terrorist-financing criminal proceedings to proceed without waiting for disposition of the predicate offence; Art. 29 bis requires a documented, risk-based AML/CTF/PF assessment updated at least annually.

**Remaining AML gaps:** obtain and visually compare the original Gazette issue for Decree 457/2020; collate every article in the updated 2023 regulation against Decrees 1463/2006, 2367/2008, 1569/2016, 2910/2019, 457/2020 and 3331/2023; compare the 2022 Law 80 consolidation article by article with all statutory amendment Gazettes. The FRA PDF is a consolidated text, not itself proof of Gazette-by-Gazette collation.

### Q2. Child Law — Law 12/1996, Law 126/2008 and Executive Regulations 2075/2010

**Full Arabic text sources located:**
- Law 12/1996 full Arabic text, 694 extracted lines: https://www.mksegypt.org/public/index.php/ar/laws/23925
- Secondary full-text reproduction: https://manshurat.org/node/12718
- PM Decree 2075/2010 full Arabic text, 1,636 extracted lines: https://lawhub.info/eg/?p=12124
- Gazette issue 29 follow-up (a), 22 July 2010, decree issuance and repeal clause: https://www.laweg.net/framePlain.aspx?NID=64854&action=viewactivepages&itemid=50826&type=6
- Law 126/2008 amendment text: https://www.laweg.net/framePlain.aspx?ItemID=8964&NID=7658&Type=6&action=ViewActivePages

PM Decree 2075/2010 expressly repeals the earlier PM Decree 3452/1997. It was published 22 July 2010 and took effect the following day, 23 July 2010. The full secondary text states it contains 194 articles; the Gazette-hosted Laweg page confirms issuance, repeal and commencement but exposes only the introductory provisions.

**Exact Arabic excerpts — Executive Regulations 2075/2010:**

Article 1 defines the child by reference to the age limit of eighteen years and expressly identifies Law 12/1996 as amended by Law 126/2008:

> الطفل: كل من لم يتجاوز سنه الثامنة عشرة سنة ميلادية كاملة, وفق وسائل الإثبات الواردة في المادة (2) من القانون.

Article 3:

> يثبت سن الطفل بموجب شهادة الميلاد أو بطاقة الرقم القومي أو أي مستند رسمي آخر. فإذا لم يوجد أي مستند من المستندات المذكورة أو أي مستند رسمي آخر قدرت السن بمعرفة إحدى الجهات التي يصدر بتحديدها قرار من وزير العدل بالاتفاق مع وزير الصحة.

Article 4 sets out the rights and best-interests principles, including protection against physical, moral and sexual abuse and the child's right to be heard in judicial and administrative matters.

**Criminal-justice provisions located in the Law 12/1996 text:** Art. 94 states criminal responsibility does not attach to a child under seven; Art. 95 applies the special criminal-treatment chapter to persons under eighteen at the time of the offence; Arts. 111–112 prescribe special penalty limits for children aged fifteen to under eighteen, including exclusion of death and life/temporary hard labour sentences in the terms of the source text. These provisions require current-text comparison against Law 126/2008 and the full Gazette before operational use.

**Remaining child-law gaps:** visually inspect the original Gazette PDF for Decree 2075/2010; extract and segment all 194 articles into the project text corpus; search for post-2020 amending decisions and child-protection regulations; preserve Decree 3452/1997 as repealed historical material only.

### Q3. Prisons / correction and rehabilitation legislation

**Law 396/1956 full Arabic text source:** https://www.notariesofegypt.org/article.php?id=469  
The page identifies Official Proceedings No. 96 bis (b), 29 November 1956, and reproduces the statute text. Opening provisions include the types of facilities, lawful written admission orders and intake recording.

**Law 19/2020 — joint prisons/narcotics amendment:**
- Full Arabic text: https://www.eglf.org/قانون-19-لسنة-2020/
- Gazette: Official Gazette No. 11 bis (l), 18 March 2020; effective 19 March 2020.
- Adds Art. 52 bis to Law 396/1956, excluding specified categories of convictions from conditional release; separately repeals the second paragraph of Art. 46 bis (a) of Law 182/1960. Preserve this instrument as linked to both the prisons and narcotics statutes, not as a prison-only amendment.

**Law 14/2022 — amendment of Law 396/1956:**
- Full Arabic transcription: https://dfatermasr.net/الاكْتفاء-بتغيير-اسم-السجون-ليس-الحل-قا-2/
- Gazette No. 11 bis (b), 20 March 2022; effective 21 March 2022 according to the Gazette issue/date and the Eastlaws metadata.
- Replaces Arts. 1, 2, 31 and 81; substitutes statutory terminology; repeals Arts. 3, 4, 34 and paragraph 3 of Art. 90, and deletes the specified final phrase of Art. 48.
- Article 1 establishes three types of correction/rehabilitation centres, including public, geographic and special centres, with judicial supervision.
- Article 31 requires facilitating study and examinations for inmates; Article 81 requires personal notification and allows a copy of the notice to be sent to a person nominated by the inmate.
- Date discrepancy: one Manshurat catalogue entry reports 13 March issuance / 14 March publication / 15 March commencement, while the Gazette issue No. 11 bis (b) and the full transcription identify 20 March 2022 / next-day commencement. Preserve the catalogue conflict and prefer the Gazette issue evidence pending inspection of the original scan.

**Interior Minister Decree 79/1961 — Internal Prison Regulations:**
- Full 101-article Arabic consolidated text, with source claiming update through 21 June 2022: https://alhasswalawfirm.com/law-library/decree-79-1961
- Original publication: Official Proceedings No. 103, 28 December 1961.
- The consolidated text's amendment notes identify, among others, Decrees 1675/2011, 1342/2013, 3320/2014, 345/2017 and later amendments through 21 June 2022. A 2022 report identifies Interior Minister Decree 1265/2022, published in Official Proceedings No. 139 follow-up (c), 21 June 2022, as replacing several provisions including Arts. 11, 15 bis, 59, 7 (second paragraph), 75, 82 bis and 85-related text. Exact instrument text and article list require Gazette-image collation.
- Manshurat record for the original decree: https://manshurat.org/node/12358

**Exact Arabic excerpts — Law 14/2022:**

Article 1 opening:

> تنفذ العقوبات المقيدة للحرية في مراكز الإصلاح والتأهيل طبقاً لأحكام القانون، وتخضع للإشراف القضائي، وتهدف إلى رعاية وتأهيل المحكوم عليهم اجتماعياً وثقافياً، وهي ثلاثة أنواع:

Article 31 opening:

> على إدارة مراكز الإصلاح والتأهيل العمومية أن تشجع النزلاء على الاطلاع والتعلم وأن تيسر الاستذكار لمن لديهم الرغبة في استكمال الدراسة.

**Remaining prison-law gaps:** obtain original Gazette scans for Laws 19/2020 and 14/2022; collate the full current Law 396 text article by article; acquire original Gazette copies of all 79/1961 amending ministerial decisions, particularly 1265/2022; verify whether any post-June-2022 amendment exists through 19 November 2026.

### Q4. Narcotics Law — Law 182/1960 and current schedules

**Official EDA source paths:**
- Law 182/1960 original statute scan, 14-page PDF (browser text extraction returned no readable lines): https://dev.edaegypt.gov.eg/media/ekgifxb3/1960-182.pdf
- EDA amendment index: https://dev.edaegypt.gov.eg/ar/المرجع-التنظيمي-لهيئة-الدواء-المصرية/القوانين-واللوائح-التنفيذية/تعديلات-قانون-رقم-182-لسنة-1960/
- Decision 44/2026, Official Proceedings No. 39 follow-up (c), 17 February 2026, 34-page EDA-hosted PDF: https://dev.edaegypt.gov.eg/media/dkjooww3/قرار-وزارة-الصحة-والسكان-رقم-44-لسنة-2026-ar-2026_.pdf
- Decision 242/2026, Official Proceedings No. 179, 17 August 2026, 4-page EDA-hosted PDF: https://dev.edaegypt.gov.eg/media/lydpgqi5/لمكافحة-المخدرات_2026_242-وزير-الصحة.pdf
- Decision 44/2026 secondary full-text/search result: https://www.eastlaws.com/legislation-full-text/ar/egypt/health-population-minister-decision/17-02-2026/no-44?id=5386660&type=1

The EDA index lists amendment Laws 206/1960, 40/1966, 16/1973, 61/1977, 45/1984, 122/1989, 134/2019 and 19/2020. Keep these as separate amendment relations and do not treat the 2026 schedule decisions as amendments to the statute itself.

**Decision 44/2026:** replaces all schedules annexed to Law 182/1960. It cites Supreme Constitutional Court case 33/47 (constitutional) and hearing date 16 February 2026; Article 2 makes it effective on publication, 17 February 2026. This follows the SCC ruling against the EDA head's Decision 600/2023 and related EDA-head schedule amendments. Do not conflate the Minister of Health's Decision 44/2026 with the invalidated EDA-head decision.

**Decision 242/2026:** issued 20 July 2026; published in Official Proceedings No. 179 on 17 August 2026; Article 2 provides commencement the day after publication (18 August 2026). Article 1 replaces item 12 in Table 1, section I(B), of Decision 44/2026 and adds/changes specified entries in Table 3. The EDA-hosted PDF is visually readable; OCR is incomplete. Screenshots of pages 10–12 show the replacement table item and added Table 3 entries. Do not rely on the current OCR alone for the chemical names or schedule rows; transcribe the original page images and have a specialist verify nomenclature.

**Law 19/2020 cross-link:** Article 2 repeals the second paragraph of Art. 46 bis (a) of Law 182/1960. This must be included in the current statutory version map.

**Remaining narcotics gaps:** transcribe the 14-page Law 182 Gazette scan; obtain and compare Gazette texts for all eight listed statutory amendments; visually transcribe all 34 pages of Decision 44 and the amended pages of Decision 242; check for later schedule decisions after 17 August 2026; preserve each superseded schedule as a dated historical version.

### Q5. Weapons Law — acquisition status

The complete 53-article Arabic text remains accessible in secondary reproductions:
- https://ar.wikisource.org/wiki/قانون_الأسلحة_والذخائر_(eg)
- https://lawhub.info/eg/?p=11748
- Original-law metadata/PDF record: https://manshurat.org/node/7414

This pass did not establish a new primary Gazette text or complete the 163/2022 amendment collation. Keep the weapons task open; do not downgrade its source status or infer that the 2015 implementing lead is the final instrument.

---

## R. Progress update after acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 61%** (qualitative research-coverage estimate; not an article-count, corpus-ingestion or lawyer-verification metric). Baseline was 58%.
- **Inventory:** 166 existing document records retained; no duplicate base-law records created. Two new distinct instrument records added for PM Decree 457/2020 (AML executive-regulation amendment) and Interior Minister Decree 1265/2022 (prison-regulation amendment).
- **Newly improved source coverage:** AML Law 80/2002 and the full 951/2003 regulation updated through 3331/2023; Child Law 12/1996 and full 2075/2010 executive regulation; Law 396/1956, Law 14/2022 and 101-article Regulation 79/1961; official EDA PDFs for Law 182/1960 and the 2026 schedules Decisions 44/2026 and 242/2026.
- **Official-hosted or Gazette PDF text paths newly verified:** AML Law/Regulations and Decree 3331/2023; narcotics Law 182/1960, Decision 44/2026 and Decision 242/2026. Full OCR/transcription and Gazette visual collation remain incomplete.
- **Local original files archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.
- **Outstanding source/use permission:** unknown for local storage, bulk retrieval, commercial indexing and public display; no permission inferred from public readability.
- **Next acquisition focus:** complete schedule OCR and Law 182 amendments; exact prison regulation amendment PDFs; AML Decree 457 Gazette-date conflict; then return to the remaining criminal procedure and evidence instruments.


---

## S. Acquisition pass — child-law current amendments and weapons legislation
**Research date:** 19 November 2026. This pass corrects the earlier “post-2020 amendments not yet identified” status for Child Law 12/1996 and expands the weapons text set.

### S1. Child Law 12/1996 — current amendment chain extended through 2025

**Newly acquired complete amendment texts / authoritative text paths:**
- Law 182/2023, 16-page Gazette-derived PDF, Official Gazette No. 46 follow-up, 16 Nov 2023: https://alhasswalawfirm.com/uploads/files/law-182-2023-1789187066518-373514976.pdf
- Law 182/2023 full text and Gazette metadata: https://alhasswalawfirm.com/law-library/law-182-2023
- Law 186/2023, Amiri Press official text: https://alamiria.com/Sec/TashTxt?id=MVvKfrT%2F9dg%3D
- Law 186/2023 Arabic PDF in MELES institutional repository: https://dspace.id.com.eg/items/83e5a2b8-181a-4eb7-8ae1-d405cb9b5ca5
- Law 12/2025 (Social Security Law) full text, Official Gazette No.14 follow-up, 3 Apr 2025: https://alhasswalawfirm.com/law-library/law-12-2025
- Law 6/2015: https://ahmedazimelgamel.blogspot.com/2015/06/6-2015-12-1996.html
- Law 7/2015: https://ahmedazimelgamel.blogspot.com/2015/06/7-2015-12-1996.html
- Law 161/2021: https://ahmedazimelgamel.blogspot.com/2025/12/161-2021-66-1973-12-1996.html
- Current full Child Law reproduction states it is amended through 3 Apr 2025: https://lawyeregypt.net/قانون-الطفل-المصرى-رقم-12-لسنة-1996/

**Statutory amendment chain now identified for Child Law 12/1996:** Law 126/2008; Decree-Law 6/2015; Decree-Law 7/2015; Law 161/2021; Law 182/2023; Law 186/2023; and Law 12/2025 (Social Security Law, which repeals Child Law Art. 49). Law 182/2023 and Law 186/2023 were not present in the previous acquisition list; Law 12/2025 is the newest identified amendment affecting the current Child Law text.

**Law 182/2023 — exact legal effect:**
- Official Gazette No.46 follow-up, 16 November 2023; Article 6 makes it effective the day after publication (17 November 2023).
- Article 4 expressly repeals paragraphs 5 and 6 of Child Law Art. 97 and the whole of Chapter IX, as well as Presidential Decree 54/1988 on the National Council for Childhood and Motherhood.
- It transfers the former Council and Child and Motherhood Care Fund into the newly reorganized Council/Fund framework.
- The 16-page PDF reproduces the Gazette text. The first pages show the repeal clause and commencement; preserve the full statute as a distinct instrument, not merely as an annotation to Law 12/1996.

**Exact Arabic excerpt — Law 182/2023, Article 4:**

> تلغى الفقرتان الخامسة والسادسة من المادة (97) والباب التاسع من قانون الطفل المشار إليه، كما يلغى قرار رئيس الجمهورية رقم 54 لسنة 1988 المشار إليه، كما يلغى كل حكم يخالف أحكام هذا القانون والقانون المرافق.

**Law 186/2023 — exact legal effect:**
- Official Gazette No.49 bis, 10 December 2023; effective 11 December 2023.
- Article 1 replaces Child Law Arts. 23, 24, 113 and 114.
- Article 2 adds Art. 72 bis.
- Amended Arts. 113–114 address failure to supervise a child and failure to perform duties by a person entrusted with a child, including a judicial option to order rehabilitation/training programmes in the circumstances specified in Art. 113.
- New Art. 72 bis extends the rights under Arts. 71 and 72 to a female worker who is fostering or has custody of a child under six months, subject to executive-regulation rules.

**Exact Arabic excerpt — Law 186/2023, Art. 72 bis:**

> للعاملة فى الدولة والقطاع العام وقطاع الأعمال العام والقطاع الخاص، بحسب الأحوال، حالة كفالتها أو حضانتها طفلاً عمره أقل من ستة أشهر ذات الحقوق الواردة بالمادتين (71، 72) من هذا القانون، وتحدد اللائحة التنفيذية القواعد المنظمة لذلك.

The Amiri Press search result reproduces the full Arabic text of the replacement provisions. The MELES institutional repository hosts an Arabic PDF, but its abstract only summarizes Arts. 23, 24, 113, 114 and new Art. 72 bis. The actual PDF should be archived and visually checked.

**Law 12/2025 — cross-statute repeal correcting the current consolidation:**
- Social Security Law 12/2025, Official Gazette No.14 follow-up, 3 April 2025.
- Article 4 expressly repeals Child Law Art. 49 as well as repealing Social Security Law 137/2010.
- Article 6 states commencement on the day following the lapse of three months from publication; calculated commencement is 4 July 2025. Confirm against the original Gazette before treating this date as production-grade.
- This is not a standalone Child Law amendment title; inventory it as Social Security Law 12/2025 with an explicit cross-reference to Child Law Art. 49.

**Exact Arabic excerpt — Law 12/2025, Article 4:**

> يُلغى قانون الضمان الاجتماعي الصادر بالقانون رقم 137 لسنة 2010، والمادة 49 من قانون الطفل الصادر بالقانون رقم 12 لسنة 1996، كما يُلغى كل حكم يخالف أحكام هذا القانون والقانون المرافق له.

**Earlier amendments recovered from current text annotations:**
- Law 6/2015, Official Gazette No.3 bis (z), 21 Jan 2015; effective 22 Jan 2015; replaces “سنتين” in Child Law Art. 46(1) with “ثلاثة أشهر”.
- Law 7/2015, Official Gazette No.6 follow-up (a), 5 Feb 2015; effective 6 Feb 2015; replaces the 21-year age references in Arts. 110 and 141 with 18 years.
- Law 161/2021, Official Gazette No.51 bis (b), 27 Dec 2021; effective 28 Dec 2021; replaces Child Law Art. 50(1) with the rule that, except where the Traffic Law provides otherwise, a child may not be granted a motor-vehicle driving licence.

### S2. Child Law Executive Regulations — PM Decree 2075/2010 amendment chain

The full 194-article text at LawHub is annotated through PM Decree 1143/2020. New distinct amending-instrument records added for:
- PM Decree 208/2014 — amendment of Arts. 85 and 87 (exact Gazette issue/date and full original text still require inspection; current consolidated text shows the amendments).
- PM Decree 178/2016 — Egyptian Proceedings No.19 follow-up (a), 24 Jan 2016; changes the minimum age wording in Arts. 85 and 87 to children older than three months; replaces Arts. 89, 90, 99 and 102; adds Arts. 91 bis and 94 bis; repeals listed provisions.
- PM Decree 1783/2018 — Official Gazette No.37 bis (a), 18 Sep 2018; amends foster-care provisions including Arts. 89, 90, 93, 99 and 101; adds Arts. 89 bis, 90 bis, 96 bis and 98 bis.
- PM Decree 1143/2020 — Official Gazette No.23 bis, 9 Jun 2020; effective the day after publication (10 Jun 2020); amends terminology and Arts. 85, 89, 89 bis, 90, 92 and 99; adds Arts. 90 bis (a), 99 bis and 112 bis.

**Full Arabic text sources:**
- Decree 2075/2010 consolidated through 2020: https://lawhub.info/eg/?p=12124
- Decree 178/2016 full transcription: https://ahmedazimelgamel.blogspot.com/2025/12/178-2016-2075-2010.html
- Decree 1783/2018 full transcription: https://ahmedazimelgamel.blogspot.com/2018/09/1783-2018-2075-2010.html
- Decree 1143/2020 full transcription: https://ahmedazimelgamel.blogspot.com/2025/12/1143-2020-2075-2010.html
- Decree 208/2014 current-text relation: https://lawhub.info/eg/?p=12124
- Decree 1783/2018 metadata/text lead: https://egyptianlaws.com/?p=146344
- Decree 178/2016 metadata/text lead: https://egyptianlaws.com/?p=145145

**Remaining child regulation gaps:** acquire original Gazette images for Decrees 208/2014, 178/2016, 1783/2018 and 1143/2020; confirm exact 208/2014 issue metadata; search for any post-2020 regulation or ministerial rules implementing Law 186/2023 Art. 72 bis; complete an article-by-article current consolidation through Law 12/2025. Do not use repealed Art. 49 in current law outputs.

### S3. Weapons and Ammunition Law — Law 394/1954, Law 5/2019, Law 163/2022 and ministerial decisions

**Full/current text and Gazette sources:**
- Law 394/1954 current 53-article Arabic text, current-text reproduction states updated through November 2022: https://mizanai.vercel.app/laws
- Full Arabic consolidated statute with amendments: https://lawhub.info/eg/?p=11748
- Law 163/2022, official Gazette No.44 follow-up (a), 3 Nov 2022 PDF hosted by Al-Ahram Gate: https://gate.ahram.org.eg/media/News/2022/11/6/2022-638033396014725011-472.pdf
- Law 5/2019 full text: https://www.eglf.org/كتاب-دوري-2-لسنة-2019-بشأن-قانون-الاسلحة/
- Interior Minister Decision 1300/2019 full Arabic text: https://www.mohamah.net/law/نصوص-ومواد-القرار-رقم-1300-لسنة-2019-باجراءات/
- Laweg image-only record for the 1954 ministerial decision “قرار بشأن الأسلحة وذخائرها”: https://www.laweg.net/Default.aspx?ItemID=75&Type=14&action=ViewActivePages&قرار-بشأن-الأسلحة-وذخائرها=
- SCC judgment 1/47, dated 9 Sep 2026, Gazette No.37 follow-up, 10 Sep 2026: https://www.eastlaws.com/legislation-full-text/ar/egypt/constitutional-court/10-09-2026/no-1?id=5669806&type=1

**Law 5/2019:**
- Official Gazette No.6 follow-up, 7 February 2019; effective 8 February 2019.
- Adds Art. 1 bis, authorizing licensing of sound, air-pressure and gas-pressure pistols/rifles and their ammunition listed in Table 5 under Interior Minister conditions.
- Replaces Arts. 25 bis and 28(1) and provides associated licensing/criminal penalty changes.
- Full Arabic text located in secondary legal reproductions; Gazette visual check still required.

**Law 163/2022:**
- Official Gazette No.44 follow-up (a), 3 November 2022; Article 4 makes it effective 4 November 2022.
- Replaces provisions in Arts. 4, 8, 10, 12, 26 and 30; adds Art. 4(6), Art. 26 bis, Art. 26 bis (a), and Art. 26 bis (b).
- Art. 26 bis criminalizes unlicensed importation of firearms, parts, ammunition and explosives, with life imprisonment and a fine up to EGP 500,000; where the specified security/terrorist purpose is established, the text prescribes death.
- Art. 26 bis (a) penalizes breach of Art. 11 bis restrictions on carrying/displaying weapons in specified places.
- Art. 26 bis (b) creates a network-site/account and publication/broadcast offence involving images or videos of covered weapons when used to incite violence by showing force, threatening or intimidating others. The penalty escalates where the weapons are unlicensed and further escalates where committed in the course of unlicensed weapons/ammunition trade.
- Art. 30(1) also provides for confiscation and blocking the site used in the Art. 26 bis (b) offence, without prejudice to bona fide third-party rights.

**Exact Arabic excerpt — Law 163/2022, Art. 26 bis (b):**

> مع عدم الإخلال بأي عقوبة أشد، يعاقب بالحبس مدة لا تقل عن ستة أشهر ولا تجاوز سنتين، وبغرامة لا تجاوز عشرة آلاف جنيه أو بإحدى هاتين العقوبتين كل من أنشأ أو أدار أو استخدم موقعاً أو حساباً خاصاً على شبكة معلوماتية يعرض صوراً أو مقاطع فيديو للأسلحة المنصوص عليها في هذا القانون، وكل من نشر أو بث بإحدى طرق العلانية شيئاً مما ذكر سلفاً للتحريض على العنف باستعراض القوة أو التلويح بها أو تخويف الغير.

**Interior Minister Decision 1300/2019:**
- Published in Egyptian Proceedings No.158 follow-up (b), 14 July 2019.
- Full secondary Arabic text acquired. It regulates permits for sound pistols/rifles and air/gas-pressure weapons and ammunition, including eligibility, applications and supporting medical/criminal-record documentation.
- The decision's preamble cites Interior Minister Decision 1/1954 “بشأن الأسلحة وذخائرها”, which is catalogued by Laweg only as an image-based page. Number 1/1954 is a secondary cross-reference; do not treat it as visually verified from the Laweg record yet.
- Separate 1954 decision record created as metadata-only, image-only source. The search did not verify any supposed “770/1954” number; do not use that number.

**Current judicial status lead:** SCC case 1/47 (constitutional), dated 9 September 2026 and published in Official Gazette No.37 follow-up on 10 September 2026, held that the Court lacked jurisdiction over the challenge to Law 394/1954 Art. 35 bis and found inadmissible the challenge to Art. 9 of Interior Minister Decision 1300/2019 insofar as it barred silencers/sound suppressors and telescopes for sound/air/gas-pressure pistols and rifles. This is not a merits ruling declaring either provision unconstitutional. Preserve the distinction.

**Remaining weapons gaps:** acquire the full original Gazette issue for Law 5/2019 and visually collate it; verify every change made by Law 163/2022 against the official scan; acquire the full original text and amendments of the 1954 ministerial decision (number 1/1954 per the 2019 decision's preamble); identify all subsequent ministerial decisions implementing Arts. 1 bis, 11 bis, 12, 15 and 37; inspect the 2015 schedule instrument cited by some consolidations; and check for any post-November-2022 amendments through 19 November 2026.

### S4. Progress update after second acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 63%** (qualitative research-coverage estimate; not an article-count, local corpus-ingestion or lawyer-verification metric). Prior pass: 61%.
- **Inventory:** 168 prior records retained; 13 distinct amendment/implementing instrument records added; no duplicate base-law records created. Total inventory: 181 records.
- **Newly upgraded areas:** Child Law 12/1996 amendment chain now identified through 2025, including the Art.49 repeal; Child Law Executive Regulations 2075/2010 amendment chain extended through 1143/2020; Law 394/1954 and Law 163/2022 official Gazette PDF text acquired; Law 5/2019 and Decision 1300/2019 full Arabic reproductions located.
- **Original Gazette/regulator PDFs locally archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.
- **Next acquisition focus:** finish child-law implementing instruments and current consolidation; obtain the original 1954 weapons decision and full Law 5/2019 Gazette scan; then continue to cybercrime, AML/narcotics and criminal-procedure acquisition gaps.


---

## T. Acquisition pass — cybercrime, digital evidence, personal data, trafficking and migrant smuggling
**Research date:** 19 November 2026.

### T1. Cybercrime Law 175/2018 and Executive Regulations

**Full Arabic text sources acquired:**
- Law 175/2018, Official Gazette No.32 bis (c), 14 Aug 2018, full official PDF: https://escc.gov.eg/assets/docs/law-175-2018.pdf
- PM Decree 1699/2020, FRA-hosted full Arabic text: https://fra.gov.eg/wp-content/uploads/2025/01/يُعمل-بأحكام-اللائحة-التنفيذية-المرافقة-فى-شأن-قانون-مكافحة-جرائم-تقنية-المعلومات-المشـار-إليـه.pdf
- Full 15-article reproduction: https://alhasswalawfirm.com/law-library/decree-1699-2020

**Law 175/2018 — selected exact provisions:** Article 2(1) requires service providers to preserve and store system logs for a continuous 180 days, including user-identifying data, content data under provider control, traffic data, terminal-device data and additional data specified by NTRA Board decision. Article 2(2) requires confidentiality and prohibits disclosure without a reasoned order from a competent judicial authority. Article 6 permits a reasoned investigative order for up to 30 days, renewable once, to seize, collect, preserve, search, inspect or access data/systems and require providers to produce stored information and connection data. Article 7 regulates website blocking and requires presentation to the court within 24 hours and a decision within 72 hours.

**Exact Arabic excerpt — Law 175/2018, Art. 2(1):**

> حفظ وتخزين سجل النظام المعلوماتي أو أي وسيلة لتقنية المعلومات، لمدة مائة وثمانين يوما متصلة.

**PM Decree 1699/2020:** Official Proceedings/Gazette No.35 follow-up (c), 27 Aug 2020; effective 28 Aug 2020. The FRA-hosted text contains the full 15-article regulation. Article 9 sets technical admissibility/handling requirements for digital evidence: integrity-preserving collection and extraction; relevance and conformity with the investigative/judicial mandate; collection, extraction, preservation and sealing by authorized judicial officers or appointed experts; identification of tools/software; hash documentation; and preservation of the original. Article 10 requires documentation of the evidence and its metadata.

**Exact Arabic excerpt — Executive Regulations, Art. 9(3):**

> أن يتم جمع الدليل الرقمى واستخراجه وحفظه وتحريزه بمعرفة مأمورى الضبط القضائى المخول لهم التعامل فى هذه النوعية من الأدلة، أو الخبراء أو المتخصصين المنتدبين من جهات التحقيق أو المحاكمة، على أن يبين فى محاضر الضبط، أو التقارير الفنية على نوع ومواصفات البرامج والأدوات والأجهزة والمعدات التى تم استخدامها، مع توثيق كود وخوارزم Hash الناتج عن استخراج نسخ مماثلة ومطابقة للأصل من الدليل الرقمى بمحضر الضبط أو تقرير الفحص الفنى، مع ضمان استمرار الحفاظ على الأصل دون عبث به.

**Numbering discrepancy:** the ESCC-hosted PDF at https://escc.gov.eg/assets/docs/law-175-2018-regulations.pdf displays “قرار رئيس مجلس الوزراء رقم (635) لسنة 2020” in its heading. The FRA-hosted full text, FRA catalogue, Eastlaws, Manshurat, LawHub and other complete reproductions identify the instrument as PM Decree 1699/2020, published 27 Aug 2020 and effective 28 Aug 2020. The ESCC heading is likely a source-copy defect, but the original Gazette No.35 follow-up (c) must be visually inspected. Do not create a separate 635/2020 instrument record on this evidence alone.

### T2. Personal Data Protection Law 151/2020 and Executive Regulations 816/2025

**Full Arabic text sources acquired:**
- Law 151/2020, Official Gazette No.28 bis (e), 15 July 2020, official ESCC PDF: https://escc.gov.eg/assets/docs/law-151-2020.pdf
- Decree 816/2025, full 43-article Arabic text: https://alhasswalawfirm.com/law-library/decree-816-2025
- 26-page Arabic PDF reproducing Official Proceedings No.244 follow-up (a), 1 Nov 2025, reviewed 29 Oct 2026: https://legalin.law/wp-content/uploads/2026/10/LegalIn-PDPL-Executive-Regulations-816-2025-rev.pdf
- Official PDPC endpoint (exists but was inaccessible in this pass): https://pdpc.gov.eg/assets/pdf-data/Executive%20Regulation.pdf

**Law 151/2020 criminal provisions — exact Arabic excerpts:**

Article 36:

> يعاقب بغرامة لا تقل عن مائة ألف جنيه ولا تجاوز مليون جنيه كل حائز أو متحكم أو معالج جمع أو عالج أو أفشى أو أتاح أو تداول بيانات شخصية معالجة إلكترونياً بأي وسيلة من الوسائل في غير الأحوال المصرح بها قانوناً أو بدون موافقة الشخص المعني بالبيانات.

Article 36 further provides imprisonment of at least six months and a fine of EGP 200,000–1,000,000, or either penalty, where the conduct is for material/moral benefit or to expose the data subject to danger or harm.

Article 41:

> يعاقب بالحبس مدة لا تقل عن ثلاثة شهور وبغرامة لا تقل عن خمسمائة ألف جنيه ولا تجاوز خمسة ملايين جنيه، أو بإحدى هاتين العقوبتين، كل حائز أو متحكم أو معالج جمع أو أتاح أو تداول أو عالج أو أفشى أو خزن أو نقل أو حفظ بيانات شخصية حساسة بدون موافقة الشخص المعني بالبيانات أو في غير الأحوال المصرح بها قانوناً.

Articles 42–43 criminalize specified cross-border data-transfer and direct electronic marketing violations. Article 47 addresses liability of the person responsible for actual management of a violating legal entity; Article 48 provides for publication of conviction, increased penalties on recidivism and punishment of attempt; Article 49 provides settlement routes.

**Executive Regulations 816/2025:** Gazette No.244 follow-up (a), 1 Nov 2025; effective 2 Nov 2025. The full 43-article text covers collection/consent, controller and processor obligations, breach response, DPO registration and functions, digital evidence, sensitive data, children's data, cross-border processing, direct marketing and licensing. Article 5 requires breach notification to the Centre within 72 hours of awareness and notification to the data subject within three working days after reporting to the Centre. Article 13 sets integrity, relevance, authorized collection and documentation conditions for digital evidence derived from personal data. Article 15 requires express written parental consent before collecting personal data of children under 15; for ages 15 to under 18, consent is governed by the stated child/guardian mechanism.

**Exact Arabic excerpt — Decree 816/2025, Art. 5:**

> يلتزم المتحكم والمعالج، بحسب الأحوال، حال حصول خرق أو انتهاك بإبلاغ المركز من خلال البوابة الإلكترونية أو الخط الساخن المعد لهذا الغرض من المركز، وذلك خلال اثنتين وسبعين ساعة من تاريخ علمه بحصول الخرق أو الانتهاك.

Law 151 Art. 6 requires regulated entities to regularize their status within one year from issuance of the Executive Regulations. Since Decree 816 was issued 1 Nov 2025, the one-year period calculates to 1 Nov 2026; verify the exact deadline calculation against the original Gazette scan.

### T3. Human trafficking — Law 64/2010 and Executive Regulations 3028/2010

**Full Arabic texts acquired:**
- Law 64/2010, full 30-article Arabic text, Gazette No.18 bis, 9 May 2010, text reproduced as updated through 2025: https://alhasswalawfirm.com/law-library/law-64-2010
- Bilingual Arabic/English full statute PDF, ILO NATLEX: https://natlex.ilo.org/dyn/natlex2/natlex2/files/download/89881/eg%2064%20of%202010.pdf
- PM Decree 3028/2010, full 28-article Arabic text, Gazette No.47 bis, 30 Nov 2010: https://alhasswalawfirm.com/law-library/decree-3028-2010
- Alternative full text: https://www.aldhshan.com/2026/02/3028-2010-64-2010.html

The 3028/2010 regulation contains victim identification, protection, legal assistance, witness protection, shelter, international cooperation, asset tracing/freezing/confiscation and victim-support fund procedures. Arts. 4–7 address international police/judicial cooperation, mutual legal assistance, extradition of persons/objects, asset tracing/freezing and enforcement of foreign confiscation/recovery orders.

**Numbering discrepancy:** one secondary SIS report says “2038/2010”; the Gazette-derived full text, Gazette No.47 bis (30 Nov 2010), Alhasswa and other complete reproductions identify PM Decree 3028/2010. Use 3028/2010 as the working record and retain 2038/2010 as an erroneous secondary citation pending original Gazette inspection. Law 82/2016 replaced the committee structure established under Law 64/2010; it did not repeal the substantive offences and penalties in Law 64/2010.

### T4. Illegal Migration and Migrant Smuggling — Law 82/2016 and Executive Regulations 983/2018

**Full Arabic text sources acquired:**
- Law 82/2016, Official Gazette No.44 bis (a), 7 Nov 2016, official FRA PDF: https://fra.gov.eg/wp-content/uploads/2021/11/قانون-رقم-82-لسنة-2016-لمكافحة-الهجرة-غير-الشرعية-وتهريب-المهاجرين.pdf
- Full law text: https://lawhub.info/eg/?p=12568
- PM Decree 983/2018 full 24-article Arabic text: https://alhasswalawfirm.com/law-library/decree-983-2018
- Alternative full text: https://lawhub.info/eg/?p=12572
- Gazette No.19 bis (z), 15 May 2018 metadata/full text: https://www.laweg.net/framePlain.aspx?NID=138273&action=viewactivepages&itemid=111688&type=6
- 14-page PDF copy hosted by Manshurat: https://manshurat.org/file/54431/download?token=y4SR-ZwS

Law 82/2016 was published 7 Nov 2016 and effective 8 Nov 2016. Its issuance Art.2 transfers the committee and its rights/obligations from the Law 64/2010 framework to the new National Coordinating Committee. Decree 983/2018 was published 15 May 2018 and took effect 16 May 2018.

Decree 983/2018 Arts. 8–11 designate the Ministry of Justice International and Cultural Cooperation Department, the Public Prosecution's International Cooperation/Execution Office and Cairo Interpol as cooperation points; regulate information exchange, investigations, mutual legal assistance, letters rogatory, extradition, asset recovery/freezing/confiscation and enforcement of foreign orders. Art.5 addresses unaccompanied children and safe return.

**Exact Arabic excerpt — Decree 983/2018, Art. 9 opening:**

> تقوم الجهات المشار إليها فى المادة السابقة فى سبيل تحقيق مكافحة الجرائم المنصوص عليها فى القانون بتبادل المعلومات وإجراء التحريات عن مرتكبى الجريمة وملاحقتهم وتقديم المساعدات فيما بينها، واتخاذ إجراءات المساعدات والإنابات القضائية وتسليم المجرمين والأشياء، واسترداد الأموال، ونقل المحكوم عليهم، وغير ذلك من صور التعاون القضائى والشرطى فى مجال المكافحة.

### T5. Progress update after third acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 65%** (qualitative research-coverage estimate; not an article-count, local corpus-ingestion or lawyer-verification metric). Prior pass: 63%.
- **Inventory:** 181 records retained; no duplicate base-law records created in this pass.
- **Newly upgraded:** official full Law 175/2018 PDF; full FRA-hosted Decree 1699/2020 text; official Law 151/2020 PDF and full 43-article Decree 816/2025 Arabic text; full Law 64/2010 and Decree 3028/2010 texts; official Law 82/2016 PDF and full Decree 983/2018 text.
- **Exact-text extracts:** cybercrime 180-day retention and investigative orders; cybercrime regulation Art.9 digital-evidence integrity/hash rules; personal-data criminal Arts.36–49; Decree 816 Art.5 72-hour breach reporting and Art.13 digital-evidence rules; human-trafficking victim safeguards and international cooperation; migrant-smuggling MLA/extradition/asset recovery provisions.
- **Source conflicts recorded:** Decree 1699/2020 versus “635/2020” heading in ESCC-hosted PDF; Decree 3028/2010 versus erroneous “2038/2010” in one secondary report.
- **Original Gazette/regulator PDFs locally archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.
- **Next acquisition focus:** resolve the original Gazette source for 1699/2020; obtain original PDPC/Gazette copy of Decree 816/2025; continue with remaining implementing decisions and post-2025 criminal amendments.


---

## U. Acquisition pass — complete official Law 174/2025 text and Law 160/2026 commencement amendment
**Research date:** 19 November 2026.

### U1. Law 174/2025 — complete official Arabic text acquired

**Primary source:** Ministry of Justice-hosted Official Gazette PDF, Official Gazette No.45 bis (d), 12 November 2025, 2,386 extracted lines, ending at Art.546:  
https://moj.gov.eg/backend/api/documents/download/20F3150C-29F1-487E-A0F0-FCCE10CB207B

The full 546-article Arabic text is readable in the browser. It has not been downloaded into the project repository or SHA-256 archived.

**Issuance provisions — current effect:**
- Art. 2 preserves the pre-existing procedure for appeals against absentia judgments issued in felony matters before the new Code commences.
- Art. 3 limits the new felony appeal rules to cases not decided by felony courts as of the effective date of Law 1/2024.
- Art. 4 repeals CPL Law 150/1950 and Law 140/2014 on surrender of accused persons and transfer of sentenced persons, and repeals inconsistent provisions.
- Art. 5 authorizes Minister of Justice implementation decisions and continues existing decisions insofar as they do not conflict with the new Code.
- Art. 6 originally set commencement for 1 October following publication; Law 160/2026 replaced that with a fixed date of 1 October 2027.

**Critical current-status correction:** Law 174/2025 is enacted but not yet in force. Law 160/2026 took effect on 1 October 2026 and fixes the new Code's commencement at **1 October 2027**. Accordingly, CPL Law 150/1950 and Law 140/2014 remain operative through 30 September 2027, absent a later amendment. Their repeal under Art. 4 of Law 174/2025 is not yet operative.

**Official/secondary discrepancy:** official Ministry of Justice PDF Art. 2 says “مواد الجنايات”. The Manshurat reproduction says “مواد الجنح”. The official PDF is the primary text; preserve the discrepancy and inspect the Gazette page image before finalizing the character-level transcript.

### U2. Law 160/2026 — full amending text and official publication metadata

- Law 160/2026 was issued and published 30 September 2026 in Official Gazette No.39 bis (b); it became effective 1 October 2026.
- Amiri Press official text: https://www.alamiria.com/Sec/TashTxt?id=Aalg37zxdcU%3D
- Official Gazette issue metadata (PDF file restricted and requires a formal copy request): https://dspace.id.com.eg/items/1b1e2a48-59d9-4307-b215-1ac3a07b4ee3

**Exact Arabic text — Law 160/2026, Article 1:**

> تستبدل عبارة "الأول من أكتوبر لعام 2027" بعبارة "الأول من أكتوبر التالى لتاريخ نشره" الواردة بالمادة السادسة من القانون رقم 174 لسنة 2025 بإصدار قانون الإجراءات الجنائية.

**Exact Arabic text — Law 160/2026, Article 2:**

> ينشر هذا القانون فى الجريدة الرسمية ، ويعمل به اعتبارًا من اليوم التالى لتاريخ نشره.

### U3. Book Five, Arts. 508–521 — full text now extracted from the official PDF

The complete 14-article text of Book Five (international judicial cooperation, extradition, mutual legal assistance, controlled delivery and asset recovery) has been extracted from the official PDF and article-mapped in the dossier. Key exact Arabic provisions:

**Article 508**

> مع عدم الإخلال بأحكام الاتفاقيات متعددة الأطراف أو الثنائية النافذة التي تكون جمهورية مصر العربية طرفًا فيها، ومع مراعاة مبدأ المعاملة بالمثل، يعمل بأحكام هذا الكتاب في شأن التعاون القضائي الدولي في المسائل الجنائية، وتسري القواعد العامة في كل ما لم يرد بشأنه نص خاص في هذا الكتاب وبما لا يتعارض مع أحكامه.

**Article 511**

> ترسل طلبات التعاون القضائي الدولي في المسائل الجنائية الواردة من الجهات القضائية الأجنبية عبر الطريق الدبلوماسي إلى وزارة العدل متضمنة ملخص الواقعة، ونوع وموضوع الطلب المترجم إلى اللغة العربية.

**Article 513** provides for advance arrest of a person sought for extradition, presentation to the Public Prosecution within 24 hours, detention in successive periods not exceeding 15 days each and 60 days in total pending receipt and determination of the extradition request, and travel-ban/arrival-watchlist measures.

**Article 514** sets 13 mandatory non-surrender grounds, including Egyptian nationality, absence of double criminality, Egyptian jurisdiction, political or military offences, discriminatory/political motive, prior final judgment, limitation, amnesty, lack of fair-trial/human-rights guarantees, immunity, sovereignty/security/public-order conflict and political-refugee status.

**Article 515** requires a reasoned surrender decision and permits challenge within seven days; the challenge is decided within seven days and the surrender decision is not executed until challenge determination or expiry of the challenge period.

**Article 517** permits controlled delivery of specified objects under Egyptian authority supervision, subject to sovereignty, security, public-order and national-security safeguards. Its OCR wording requires page-image collation.

**Articles 518–520** set conditions for foreign judicial assistance, grounds for refusal and the Public Prosecutor's decision process.

**Article 521**

> استثناءً من أحكام هذا الكتاب، يجوز لرئيس الجمهورية بناءً على عرض النائب العام وبعد موافقة مجلس الوزراء، الموافقة على تسليم المتهمين ونقل المحكوم عليهم إلى دولهم، وذلك لمحاكمتهم أو تنفيذ العقوبة المقضي بها عليهم بحسب الأحوال، متى اقتضت مصلحة الدولة العليا ذلك.

**Transcription/verification notes:** Article 517's wording around controlled-delivery objects is OCR-uncertain and must be checked against the Gazette page image. Apparent article-number duplications in the later remote-hearing chapter also need page-image review. This is an acquisition transcript, not a lawyer-approved consolidated edition.

### U4. Progress update after fourth acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 67%** (qualitative research-coverage estimate; not article-count, local corpus-ingestion or lawyer-verification metric). Prior pass: 65%.
- **Newly upgraded:** full official 546-article Law 174/2025 PDF; full Law 160/2026 Amiri Press text and Gazette issue metadata; complete Book Five Arts. 508–521 extracted into the dossier.
- **Current procedural-law status:** Law 174/2025 commences 1 October 2027 after Law 160/2026. Law 150/1950 and Law 140/2014 remain operative until then, absent further amendment.
- **Transition correction:** official Law 174 Art.2 says felony absentia judgments (“مواد الجنايات”); a secondary reproduction says misdemeanours (“مواد الجنح”). The official PDF wording is preferred; the discrepancy remains logged.
- **Original Gazette PDFs locally archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.


---

## V. Acquisition pass — current consolidated Criminal Procedure Law 150/1950 text through Law 1/2024
**Research date:** 19 November 2026.

### V1. Full current Arabic text acquired

- Full 178-page PDF reproduction of the current Code: https://alhasswalawfirm.com/uploads/files/1501950-1788831619834-5385881.pdf
- Full text page: https://alhasswalawfirm.com/law-library/law-150-1950
- The host states the text is reproduced verbatim from the Court of Cassation Legislation Portal and reflects amendments through 16 January 2024. The official portal link is exposed at https://cc.gov.eg/legislation_single/3012435102 but returned a 502 error in this pass; no bypass attempted.
- The PDF contains the full text, article-level amendment footnotes, and runs through numbered Art.560. It includes Law 177/2020 Art.113 bis and the Law 1/2024 changes to felony-court terminology and Arts.419 bis–419 bis 9.
- This is a secondary-hosted reproduction of a Court of Cassation portal text, not an original Gazette scan. It is readable and suitable as a temporary consolidation base, subject to comparison against the Gazette amendments.

**Exact Arabic excerpt — Law 150/1950 Art.113 bis (added by Law 177/2020):**

> لا يجوز لمأموري الضبط أو جهات التحقيق الكشف عن بيانات المجني عليه في أي من الجرائم المنصوص عليها في الباب الرابع من الكتاب الثالث من قانون العقوبات الصادر بالقانون رقم 58 لسنة 1937، أو في أي من المادتين (306 مكررا / أ ، 306 مكررا / ب) من ذات القانون، أو في المادة (96) من قانون الطفل الصادر بالقانون رقم 12 لسنة 1996، إلا لذوي الشأن.

**Law 1/2024 additions and current article crosswalk:** the consolidated text incorporates the nine new felony-appeal provisions, Arts.419 bis through 419 bis 9, and footnotes the terminology replacements in Arts.11, 12, 13, 529, 536 and 524. The Law 1/2024 original Gazette PDF is separately linked in the inventory.

### V2. Amendment chronology expanded from consolidated-code footnotes

The current full text's article-level footnotes expose additional older amendment instruments not previously represented as separate records in the inventory. The footnotes identify, among others:
- Laws 178/1951 and 228/1951 (issuance provisions);
- Decree-Laws 353/1952, 340/1952 and 252/1952;
- Law 426/1954;
- Laws 271/1955, 627/1955, 121/1956 and 113/1957;
- Law 43/1958;
- Laws 107/1962, 37/1972 and 63/1975;
- Law 170/1981;
- Law 23/1992;
- Laws 95/2003, 145/2006, 74/2007, 71/2009, 83/2013, 49/2014, 138/2014, 16/2015, 11/2017, 177/2020 and 1/2024.

This expands the older amendment queue beyond the previously listed metadata-only candidates. The full consolidation footnotes establish the amendment relations, but the underlying Gazette texts for the older instruments have not all been acquired. They remain separate acquisition targets and must not be treated as fully verified from footnotes alone.

**Metadata correction:** a Manshurat page for a different CPL consolidation says the last amendment was Law 189/2020. That attribution is wrong for CPL: the actual text inserts Art.113 bis under Law 177/2020, while Law 189/2020 amended the Penal Code. The full 2024 consolidation page correctly states that it reflects amendments through 16 January 2024.

### V3. Current operative status

Law 150/1950 remains the operative Criminal Procedure Code through 30 September 2027, absent a later amendment. Law 174/2025 repeals it only when the new Code commences on 1 October 2027 under Law 160/2026. Use this current consolidated Law 150 text for present-day procedure, while retaining the 174/2025 text as future law.

### V4. Progress update after fifth acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 69%** (qualitative research-coverage estimate; not article-count, local corpus-ingestion or lawyer-verification metric). Prior pass: 67%.
- **Newly upgraded:** full 178-page consolidated Law 150/1950 text, article-level footnotes through Law 1/2024, and the official Court of Cassation source endpoint.
- **Current CPL coverage:** both current Law 150/1950 and future Law 174/2025 now have complete readable Arabic text sources. The current code's older amendment chain is materially expanded, but original Gazette acquisition for older amendments remains open.
- **Original Gazette PDFs locally archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.


---

## W. Acquisition pass — older Criminal Procedure Law amendments recovered from full-text footnotes
**Research date:** 19 November 2026.

This pass converts several older amendment citations from the Law 150/1950 consolidated text into distinct instrument records and acquires full Arabic text for the amendments where accessible.

### W1. Full Arabic amendment texts acquired

**Law 426/1954** — Official Proceedings No.63 bis, 5 August 1954. Laweg full Arabic text:
https://www.laweg.net/framePlain.aspx?ItemID=20871&NID=22302&Type=6&action=ViewActivePages

It replaces the second paragraph of Art.9, first paragraph of Art.10 and Art.39 CPL. It clarifies when investigations may proceed without a complaint/request where public officials are victims of specified offences committed because of their office, and the related right to withdraw the complaint/request.

**Law 627/1955** — Official Proceedings 1955. Laweg year index and current consolidated reproductions:
https://www.laweg.net/Default.aspx?Year=1955&action=LegsYears
https://lawyeregypt.net/قانون-الإجراءات-الجنائية-طبقا-لاحدث-التعديلات-بالقانون-95-لسنة-2003/

It replaces Art.381 CPL with the rule applying misdemeanour/misdemeanour-procedure rules before felony courts unless otherwise provided. Later amendments to Art.381 include Law 107/1962 (the death-sentence unanimity/opinion provision).

**Law 121/1956** — Egyptian Proceedings No.24 bis, 25 March 1956. Full Arabic text:
https://www.aldhshan.com/2026/02/121-1956.html

It replaces Arts.63, 64, 162, 210, 214 and 232 CPL.

**Law 113/1957** — published 19 March 1957. Full Arabic text:
https://www.aldhshan.com/2026/02/113-1957.html

It amends Art.123 CPL concerning the investigator's first questioning of the accused, including identity, notification of the charge and recording the accused's statements.

**Law 63/1975** — Official Gazette No.31, 31 July 1975. Full Arabic text:
https://www.aldhshan.com/2026/02/63-1975.html

It amends both the Penal Code and CPL and adds Art.160 bis CPL, authorizing the Public Prosecutor or an Advocate General, in the specified Art.118 bis (a) Penal Code cases, to refer the case to misdemeanour courts under the special procedure.

**Law 174/1998** — Official Gazette No.51 bis, 20 December 1998. Full Arabic text:
https://mksegypt.org/ar/laws/24110

It replaces multiple CPL provisions, including Arts.63, 208 bis (a)–(c), 233, 260, 267, 309, 323, 324, 325 bis, 401, 402 and 412; adds Arts.18 bis, 18 bis (a), 24 bis and 251 bis; and changes monetary values used for detention/work deductions. This is a significant asset-freezing, settlement and criminal-procedure amendment.

**Law 340/1952** — Egyptian Proceedings No.16 bis, 18 December 1952. Full Arabic text:
https://www.aldhshan.com/2026/02/340-1952-17-150-1950-150-1950.html

It amends Art.17 on interruption of limitation periods and removes the transitional paragraph added by Law 178/1951 to the issuance provisions of Law 150/1950.

**Law 107/1962** — Official Gazette No.136, 17 June 1962. Full Arabic text:
https://www.aldhshan.com/2025/12/107-1962.html

It replaces “مستشار الإحالة” with “غرفة الاتهام” in listed provisions and modifies other procedure provisions. The full current Law 150 consolidation and secondary sources identify Law 107/1962, although one older code transcription misprints 107/1963; retain that as a date/number cross-check.

### W2. Additional historical instruments and source discrepancies

- Decree-Law 353/1952: the consolidated text identifies it as repealing CPL Arts.66 and 68 and amending Art.53. A separate full instrument text was not located in this pass.
- Law 252/1952: LawHub identifies this as repealing CPL Arts.19 and 20, Official Proceedings No.42 bis, 20 December 1952.
- Law 252/1953: a separate Aldhshan text page identifies a Law 252/1953 published 21 May 1953. Do not conflate it with Law 252/1952; the two are separate year-number combinations pending original Gazette comparison.
- Law 43/1958 remains a footnote-identified amendment with no full text located in this pass.

**Exact Arabic excerpt — Law 426/1954, Article 1 (Art.9 second paragraph):**

> وفى جميع الأحوال التى يشترط القانون فيها لرفع الدعوى الجنائية تقديم شكوى أو الحصول على اذن أو طلب من المجنى عليه أو غيره لا يجوز اتخاذ اجراءات التحقيق فيها إلا بعد تقديم هذه الشكوى أو الحصول على هذا الإذن أو الطلب على أنه فى الجريمة المنصوص عليها فى المادة 185 من قانون العقوبات وفى الجرائم المنصوص عليها فى المواد 303 و306 و307 و308 من القانون المذكور إذا كان المجنى عليه فيها موظفا عاما أو شخصا ذا صفة نيابية عامة أو مكلفا بخدمة عامة وكان ارتكاب الجريمة بسبب أداء الوظيفة أو النيابة أو الخدمة العامة يجوز اتخاذ اجراءات التحقيق فيها دون حاجة إلى تقديم شكوى أو طلب أو إذن.

**Exact Arabic excerpt — Law 113/1957, Art.1:**

> تعدل المادة 123 من قانون الإجراءات الجنائية على الوجه الآتي: "عند حضور المتهم لأول مرة في التحقيق يجب على المحقق أن يثبت شخصيته ثم يحيطه علماً بالتهمة المنسوبة إليه ويثبت أقواله في المحضر.

**Exact Arabic excerpt — Law 63/1975, Art.160 bis:**

> يجوز للنائب العام أو المحامى العام فى الأحوال المبينة فى الفقرة الأولى من المادة 118 مكررا (أ) من قانون العقوبات أن يحيل الدعوى إلى محاكم الجنح لتقضى فيها وفقا لأحكام المادة المذكورة.

### W3. Progress update after sixth acquisition pass — 19 November 2026

- **Estimated assigned criminal-law domain completion: 71%** (qualitative research-coverage estimate; not article-count, local corpus-ingestion or lawyer-verification metric). Prior pass: 69%.
- **New distinct historical amendment records added:** 10, including 426/1954, 627/1955, 121/1956, 113/1957, 63/1975, 174/1998, 340/1952, 252/1952, 252/1953 and 353/1952. Law 107/1962 was upgraded from metadata-only to full Arabic text accessible.
- **Full texts acquired:** six amendment instruments in this pass (426/1954, 121/1956, 113/1957, 63/1975, 174/1998, 340/1952), plus accessible full text/operative excerpt for 627/1955 and 107/1962.
- **Outstanding:** Law 43/1958, original Gazette scans for 1950s instruments, and article-by-article reconciliation of every footnote.
- **Original Gazette PDFs locally archived and SHA-256 verified:** 0.
- **Egyptian lawyer-verified records:** 0.
