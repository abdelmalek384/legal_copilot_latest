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
