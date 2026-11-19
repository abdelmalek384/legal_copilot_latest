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
