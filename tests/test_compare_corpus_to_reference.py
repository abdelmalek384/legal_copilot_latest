import json,sys,tempfile,unittest
from unittest import mock
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from tools.compare_corpus_to_reference import build_report,label,segment,main
REF="""المادة الأولى
يعمل بأحكام القانون.
المادة الثانية
تنشر في الوقائع.
مادة (1)
مدة الإخطار ثلاثين يوما.
مادة (2)
القيمة 5000 جنيه.
مادة (3) مكرر
حكم إضافي.
"""
class T(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.d=Path(self.tmp.name);self.ref=self.d/"r.txt";self.ref.write_text(REF,encoding="utf-8")
  rows=[{"article":"1","text":"يعمل بأحكام القانون."},{"article":"2","text":"تنشر في الوقائع."},{"article":"1","text":"مدة الإخطار ستين يوما."},{"article":"2","text":"القيمة 50000 جنيه."},{"article":"9","text":"مادة زائدة."}]
  self.c=self.d/"c.jsonl";self.c.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in rows),encoding="utf-8")
 def tearDown(self):self.tmp.cleanup()
 def test_labels(self):
  self.assertEqual(label("مادة (٥)"),"5");self.assertEqual(label("المادة الأولى"),"1");self.assertEqual(label("12 مكرر"),"12 مكرر");self.assertIsNone(label("غير مفهوم"))
  self.assertEqual([(x["key"],x["occurrence"]) for x in segment(REF)[:4]],[("1",1),("2",1),("1",2),("2",2)])
  self.assertEqual(segment("مادة (7) نص داخل العنوان") [0]["text"],"نص داخل العنوان")
 def test_differences(self):
  r=build_report(self.c,self.ref);s={(x["article"],x["occurrence"]):x["status"] for x in r["articles"]}
  self.assertEqual(s[("1",1)],"identical_after_normalization");self.assertEqual(s[("2",1)],"identical_after_normalization")
  self.assertEqual(s[("1",2)],"numeric_difference");self.assertEqual(s[("2",2)],"numeric_difference")
  self.assertEqual(s[("3 مكرر",1)],"missing_in_candidate");self.assertEqual(s[("9",1)],"extra_in_candidate");self.assertTrue(r["evidence_only"])
 def test_cli(self):
  o=self.d/"out";self.assertEqual(main(["--candidate",str(self.c),"--reference",str(self.ref),"--out-dir",str(o)]),0)
  self.assertTrue((o/"comparison_report.json").exists());self.assertIn("evidence only",(o/"comparison_report.md").read_text().lower())
  self.assertEqual(main(["--candidate",str(self.c),"--reference",str(self.ref),"--out-dir",str(o),"--fail-on-difference"]),1)
 def test_pdf_reference_preserves_article_page_ranges(self):
  pdf=self.d/"official.pdf";pdf.write_bytes(b"%PDF synthetic fixture")
  rows=[
   {"article":"1","text":"يعمل بأحكام القانون. ويستمر العمل به."},
   {"article":"2","text":"تنشر في الوقائع."},
  ]
  self.c.write_text("\n".join(json.dumps(x,ensure_ascii=False) for x in rows),encoding="utf-8")
  class Page:
   def __init__(self,text):self.text=text
   def extract_text(self):return self.text
  class Reader:
   def __init__(self,*args,**kwargs):
    self.is_encrypted=False
    self.pages=[
     Page("المادة الأولى\nيعمل بأحكام القانون."),
     Page("ويستمر العمل به.\nالمادة الثانية\nتنشر في الوقائع."),
    ]
  with mock.patch("tools.compare_corpus_to_reference.PdfReader",Reader):
   report=build_report(self.c,pdf)
  self.assertEqual(report["reference"]["format"],"pdf")
  self.assertEqual(report["reference"]["page_count"],2)
  self.assertEqual(report["reference"]["page_matter_lines_removed"],2)
  self.assertTrue(any("header/footer" in warning for warning in report["warnings"]))
  by_article={x["article"]:x for x in report["articles"]}
  self.assertEqual((by_article["1"]["reference_page_start"],by_article["1"]["reference_page_end"]),(1,2))
  self.assertEqual((by_article["2"]["reference_page_start"],by_article["2"]["reference_page_end"]),(2,2))

 def test_pdf_reference_warns_when_a_page_has_no_extractable_text(self):
  pdf=self.d/"scanned.pdf";pdf.write_bytes(b"%PDF synthetic fixture")
  class Page:
   def extract_text(self):return ""
  class Reader:
   def __init__(self,*args,**kwargs):self.is_encrypted=False;self.pages=[Page()]
  with mock.patch("tools.compare_corpus_to_reference.PdfReader",Reader):
   report=build_report(self.c,pdf)
  self.assertTrue(any("no extractable text" in warning for warning in report["warnings"]))
  self.assertFalse(report["all_identical"])

 def test_bad_json_warns(self):
  b=self.d/"bad.jsonl";b.write_text('bad json\n[1]\n{"article":"???","text":"x"}',encoding="utf-8");self.assertTrue(build_report(b,self.ref)["warnings"])
if __name__=="__main__":unittest.main()
