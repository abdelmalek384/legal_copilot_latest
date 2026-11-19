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

