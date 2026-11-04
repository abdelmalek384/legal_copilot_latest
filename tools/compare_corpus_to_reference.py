"""Evidence-only comparison of JSONL article rows with manually saved reference text."""
import argparse,difflib,hashlib,json,re,shutil,subprocess,sys,unicodedata
from pypdf import PdfReader
from collections import Counter
from pathlib import Path
DIGITS=str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹","01234567890123456789")
DIAC=re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
ORD={"الاولى":1,"الاول":1,"الثاني":2,"الثانيه":2,"الثانية":2,"الثالث":3,"الثالثه":3,"الثالثة":3,"الرابع":4,"الرابعه":4,"الرابعة":4,"الخامس":5,"الخامسه":5,"الخامسة":5,"السادس":6,"السادسه":6,"السادسة":6,"السابع":7,"السابعه":7,"السابعة":7,"الثامن":8,"الثامنه":8,"الثامنة":8,"التاسع":9,"التاسعه":9,"التاسعة":9,"العاشر":10,"العاشره":10,"العاشرة":10,"الحادي عشر":11,"الحادية عشرة":11,"الثاني عشر":12,"الثانية عشرة":12,"الثالث عشر":13,"الثالثة عشرة":13,"الرابع عشر":14,"الرابعة عشرة":14,"الخامس عشر":15,"الخامسة عشرة":15,"السادس عشر":16,"السادسة عشرة":16,"السابع عشر":17,"السابعة عشرة":17,"الثامن عشر":18,"الثامنة عشرة":18,"التاسع عشر":19,"التاسعة عشرة":19,"العشرون":20,"العشرين":20}
ORD={re.sub(r"\s+"," ",k):v for k,v in ORD.items()}
WORDS=set("واحد واحده اثنين اثنان اثنتين ثلاثه ثلاث اربعه اربع خمسه خمس سته ست سبعه سبع ثمانيه ثماني تسعه تسع عشره عشر عشرين عشرون ثلاثين ثلاثون اربعين اربعون خمسين خمسون ستين ستون سبعين سبعون ثمانين ثمانون تسعين تسعون مائه مئه ميه الف الفين مليون مليار نصف ثلث ربع".split())
HEAD=re.compile(r"^\s*(?:المادة|مادة)\s*\(?\s*(.*?)\s*\)?\s*[:：\-–—]?\s*(.*)$")
def norm(s):
  s=unicodedata.normalize("NFKC",str(s or "")).translate(DIGITS);s=DIAC.sub("",s);s=re.sub(r"[أإآٱ]","ا",s).replace("ى","ي").replace("ی","ي").replace("ک","ك");return re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]","",s)
ORD = {norm(k): v for k, v in ORD.items()}
def label(v):
 if v is None:return None
 s=re.sub(r"^(?:المادة|مادة)\s*","",norm(v).strip())
 s=re.sub(r"^\(\s*(\d+)\s*\)",r"\1",s).strip()
 b=re.search(r"\s*(?:مكررا|مكررة|مكرر|bis)(?:\s+\(?\s*([ء-ي])\s*\)?)?\s*$",s,re.I)
 letter=b.group(1) if b else None
 if b:s=s[:b.start()].strip()
 s=re.sub(r"^\((.*?)\)$",r"\1",s).strip()
 s=re.sub(r"\s+"," ",s)
 if s.isdigit():n=s
 else:
  n=str(ORD.get(s,s))
  if n==s:return None
 return n+(" مكرر"+((" "+letter) if letter else "") if b else "")
def textnorm(s):return re.sub(r"\s+"," ",re.sub(r"[^\w\s]|_"," ",norm(s))).strip()
def nums(s):
 s=textnorm(s);return Counter(re.findall(r"\d+",s)),Counter(w for w in re.findall(r"\w+",s.replace("ة","ه")) if w in WORDS)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def extract_heading(line,reverse_rtl_digits=False):
 s=norm(line).strip()
 m=re.match(r"^[\s()（）]*(?:لك\s*)?(?:المادة|مادة)\s*(.*)$",s)
 if not m:return None,None
 rest=m.group(1).strip()
 rest=re.sub(r"^[\s()（）:：\-–—]+|[\s()（）:：\-–—]+$","",rest).strip()
 # pypdf can return Arabic-Indic heading digits in visual RTL order (e.g. ٠١ for article 10).
 # Correct the label only; body digits remain untouched for explicit human review.
 if reverse_rtl_digits:
  raw_digits="".join(ch for ch in line if ch in "٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹")
  if raw_digits:
   normalized_digits=raw_digits.translate(DIGITS)
   rest=re.sub(r"\d+",normalized_digits[::-1],rest,count=1)
 n=re.match(r"^\(?\s*(\d+)\s*\)?(?:\s+(مكرر(?:ا|ة)?(?:\s+\(?[ء-ي]\s*\)?)?))?(?:\s+(.*))?$",rest,re.I)
 if n:
  suffix_letter=re.search(r"مكرر(?:ا|ة)?\s+\(?([ء-ي])",n.group(2)) if n.group(2) else None
  key=n.group(1)+((" مكرر"+((" "+suffix_letter.group(1)) if suffix_letter else "")) if n.group(2) else "")
  return key,(n.group(3) or "").strip()
 for ordinal in sorted(ORD,key=len,reverse=True):
  if rest==ordinal:return str(ORD[ordinal]),""
  if rest.startswith(ordinal+" "):return str(ORD[ordinal]),rest[len(ordinal):].strip()
 return None,None

def _segment_lines(lines,reverse_rtl_digits=False):
 out=[];cur=None;seen=Counter()
 for line,page_number in lines:
  key,body=extract_heading(line,reverse_rtl_digits) if len(line)<400 else (None,None)
  key=label(key) if key is not None else None
  if key:
   seen[key]+=1
   cur={"key":key,"occurrence":seen[key],"heading":line.strip()[:120],"parts":[]}
   if page_number is not None:cur.update(page_start=page_number,page_end=page_number)
   out.append(cur)
   if body:cur["parts"].append(body)
  elif cur is not None:
   if page_number is not None:cur["page_end"]=page_number
   cur["parts"].append(line)
 for x in out:x["text"]="\n".join(x.pop("parts")).strip()
 return out
def segment(s):
 return _segment_lines((line,None) for line in s.splitlines())
def segment_pages(pages,reverse_rtl_digits=False):
 return _segment_lines(((line,page_number) for page_number,page_text in enumerate(pages,1) for line in page_text.splitlines()),reverse_rtl_digits)
def _is_gazette_page_matter(line):
 s=norm(line)
 return "الجريدة الرسمية" in s or "الوقائع المصرية" in s
def _clean_pdf_page_matter(page_text):
 lines=page_text.splitlines();kept=[];removed=0
 for index,line in enumerate(lines):
  normalized=norm(line).strip()
  if re.fullmatch(r"[٠-٩0-9۰-۹]+",normalized):
   # Standalone folio numbers are page furniture, not article text.
   continue
  if re.match(r"^(?:الكتاب|الباب|الفصل|القسم)\s+(?:الاول|الثاني|الثالث|الرابع|الخامس|السادس|السابع|الثامن|التاسع|العاشر|\d+)(?:\s|$)",normalized):
   # Section titles between articles must not extend the preceding article's page range.
   continue
  # The electronic-copy watermark is repeated over the page and is not statutory text.
  if ("صورة" in normalized and ("إلكترونية" in normalized or "الكترونية" in normalized)) or ("يعتد" in normalized and "التداول" in normalized):
   continue
  if len(normalized)<18 and normalized in {"لك","ل","تداول","عند","بها","تروني","ة ال يع"}:
   continue
  at_page_edge=index<3 or index>=max(0,len(lines)-3)
  if at_page_edge and _is_gazette_page_matter(line):
   removed+=1
  else:kept.append(line)
 return "\n".join(kept),removed

def read_reference(path):
 p=Path(path)
 if p.suffix.lower()==".pdf":
  try:
   page_texts=[];warnings=[];page_matter_removed=0;extraction="pypdf text extraction"
   poppler=shutil.which("pdftotext")
   if poppler:
    try:
     completed=subprocess.run([poppler,"-layout",str(p),"-"],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120,check=False)
     if completed.returncode==0 and completed.stdout.strip():
      page_texts=completed.stdout.split("\f")
      if page_texts and not page_texts[-1].strip():page_texts.pop()
      extraction="pdftotext -layout"
    except (OSError,subprocess.TimeoutExpired):
     page_texts=[]
   if not page_texts:
    reader=PdfReader(str(p),strict=False)
    if reader.is_encrypted:raise ValueError("encrypted reference PDFs are not supported; provide an authorized readable copy")
    for page_number,page in enumerate(reader.pages,1):
     try:text=page.extract_text() or ""
     except Exception as exc:
      text="";warnings.append(f"PDF page {page_number} text extraction failed ({type(exc).__name__}); review that page manually.")
     if not text.strip():warnings.append(f"PDF page {page_number} yielded no extractable text; image/OCR review is still required.")
     page_texts.append(text)
   cleaned=[]
   for text in page_texts:
    text,removed=_clean_pdf_page_matter(text);page_matter_removed+=removed;cleaned.append(text)
   if page_matter_removed:
    warnings.append(f"Excluded {page_matter_removed} apparent Gazette header/footer line(s) from page edges; verify the original page images before accepting matches.")
   return segment_pages(cleaned,reverse_rtl_digits=(extraction=="pypdf text extraction")),warnings,{"format":"pdf","page_count":len(cleaned),"extraction":extraction,"page_matter_lines_removed":page_matter_removed}
  except ValueError:raise
  except Exception as exc:raise ValueError(f"could not read reference PDF ({type(exc).__name__})") from exc
 return segment(p.read_text(encoding="utf-8")),[],{"format":"text","page_count":None,"extraction":"UTF-8 text"}

def readcand(p):
 out=[];warn=[];seen=Counter()
 for i,line in enumerate(Path(p).read_text(encoding="utf-8").splitlines(),1):
  if not line.strip():continue
  try:r=json.loads(line)
  except json.JSONDecodeError:warn.append(f"Malformed JSON on line {i}; skipped.");continue
  if not isinstance(r,dict):warn.append(f"Non-object JSON on line {i}; skipped.");continue
  k=label(r.get("article",r.get("label")));t=r.get("text",r.get("body"))
  if k is None or not isinstance(t,str):warn.append(f"Unlabelled row or missing text on line {i}; skipped.");continue
  seen[k]+=1;out.append({"key":k,"occurrence":seen[k],"text":t,"line":i})
 return out,warn
def compare(c,r,ratio=.97):
 cm={(x["key"],x["occurrence"]):x for x in c};rm={(x["key"],x["occurrence"]):x for x in r};out=[]
 for k in list(rm)+[k for k in cm if k not in rm]:
  a,b=rm.get(k),cm.get(k);x={"article":k[0],"occurrence":k[1]}
  if a is not None and "page_start" in a:x.update(reference_page_start=a["page_start"],reference_page_end=a["page_end"])
  if a is None:x.update(status="extra_in_candidate",candidate_line=b["line"])
  elif b is None:x.update(status="missing_in_candidate",reference_heading=a["heading"])
  else:
   at,bt=textnorm(a["text"]),textnorm(b["text"]);ad,aw=nums(a["text"]);bd,bw=nums(b["text"]);sim=difflib.SequenceMatcher(None,at,bt,autojunk=False).ratio() if at!=bt else 1
   x.update(similarity=round(sim,4),candidate_line=b["line"])
   if at==bt:x["status"]="identical_after_normalization"
   elif ad!=bd or aw!=bw:
    x["status"]="numeric_difference";x["numeric_difference"]={"digits":{"only_in_reference":dict(ad-bd),"only_in_candidate":dict(bd-ad)} if ad!=bd else None,"number_words":{"only_in_reference":dict(aw-bw),"only_in_candidate":dict(bw-aw)} if aw!=bw else None}
   else:x["status"]="minor_difference" if sim>=ratio else "major_difference"
   if at!=bt:
    op=next((o for o in difflib.SequenceMatcher(None,at,bt,autojunk=False).get_opcodes() if o[0]!="equal"),None)
    if op:
     _,i,j,l,m=op;x["reference_excerpt"]=at[max(0,i-40):j+40];x["candidate_excerpt"]=bt[max(0,l-40):m+40]
  out.append(x)
 return out
def build_report(cp,rp,ratio=.97):
 c,w=readcand(cp);r,reference_warnings,reference_meta=read_reference(rp);w.extend(reference_warnings)
 if not r:w.append("No article headings detected in reference; nothing aligned.")
 res=compare(c,r,ratio);counts=Counter(x["status"] for x in res)
 disclaimer="Text comparison only; it does not authenticate sources, establish legal status, prove amendment completeness, or authorize reuse/import. PDF text extraction is not visual page review or OCR verification. Human and lawyer review remain required."
 substantive_warnings=[warning for warning in w if not warning.startswith("Excluded ") or "apparent Gazette header/footer" not in warning]
 all_identical=bool(res) and set(counts)=={"identical_after_normalization"} and not substantive_warnings
 return {"tool":"compare_corpus_to_reference","evidence_only":True,"disclaimer":disclaimer,"candidate":{"path":str(cp),"sha256":digest(cp),"rows_compared":len(c)},"reference":{"path":str(rp),"sha256":digest(rp),"articles_detected":len(r),**reference_meta},"min_ratio":ratio,"summary":dict(sorted(counts.items())),"all_identical":all_identical,"warnings":w,"articles":res}
def render(r):
 lines=["# Corpus vs reference comparison (evidence only)","",r["disclaimer"],"",f"- Candidate SHA-256: {r['candidate']['sha256']}; rows: {r['candidate']['rows_compared']}",f"- Reference SHA-256: {r['reference']['sha256']}; articles: {r['reference']['articles_detected']}",f"- Reference format: {r['reference']['format']}; extraction: {r['reference']['extraction']}","","## Summary",""]+[f"- {k}: {v}" for k,v in r["summary"].items()]+[f"- all identical: {r['all_identical']}",""]
 if r["warnings"]:lines+=["## Warnings",""]+["- "+w for w in r["warnings"]]+[""]
 pr={"numeric_difference":0,"major_difference":1,"missing_in_candidate":2,"extra_in_candidate":3,"minor_difference":4}
 for x in sorted([x for x in r["articles"] if x["status"]!="identical_after_normalization"],key=lambda z:(pr.get(z["status"],9),z["article"]))[:200]:
  lines += [f"### Article {x['article']} occurrence {x['occurrence']}: {x['status']}"]
  if x.get("reference_page_start") is not None:lines.append(f"- reference PDF pages: {x['reference_page_start']}–{x['reference_page_end']}")
  if x.get("numeric_difference"):lines.append("- numeric differences: "+json.dumps(x["numeric_difference"],ensure_ascii=False))
  if "reference_excerpt" in x:lines += ["- reference: …"+x["reference_excerpt"]+"…","- candidate: …"+x["candidate_excerpt"]+"…"]
  lines.append("")
 return "\n".join(lines)+"\n"
def main(argv=None):
 p=argparse.ArgumentParser(description=__doc__);p.add_argument("--candidate",required=True);p.add_argument("--reference",required=True);p.add_argument("--out-dir",default="comparison_report");p.add_argument("--min-ratio",type=float,default=.97);p.add_argument("--fail-on-difference",action="store_true");a=p.parse_args(argv)
 if not 0<=a.min_ratio<=1:p.error("--min-ratio must be between 0 and 1")
 r=build_report(a.candidate,a.reference,a.min_ratio);o=Path(a.out_dir);o.mkdir(parents=True,exist_ok=True)
 (o/"comparison_report.json").write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding="utf-8");(o/"comparison_report.md").write_text(render(r),encoding="utf-8")
 print(json.dumps({"summary":r["summary"],"all_identical":r["all_identical"],"warnings":r["warnings"]},ensure_ascii=False,indent=2))
 return int(a.fail_on_difference and not r["all_identical"])
if __name__=="__main__":sys.exit(main())
