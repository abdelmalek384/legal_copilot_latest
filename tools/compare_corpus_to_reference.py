"""Evidence-only comparison of JSONL article rows with manually saved reference text."""
import argparse,difflib,hashlib,json,re,sys,unicodedata
from collections import Counter
from pathlib import Path
DIGITS=str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹","01234567890123456789")
DIAC=re.compile(r"[\u0610-\u061A\u064B-\u065F\u0670\u06D6-\u06ED\u0640]")
ORD={"الاولى":1,"الاول":1,"الثاني":2,"الثانيه":2,"الثانية":2,"الثالث":3,"الثالثه":3,"الثالثة":3,"الرابع":4,"الرابعه":4,"الرابعة":4,"الخامس":5,"الخامسه":5,"الخامسة":5,"السادس":6,"السادسه":6,"السادسة":6,"السابع":7,"السابعه":7,"السابعة":7,"الثامن":8,"الثامنه":8,"الثامنة":8,"التاسع":9,"التاسعه":9,"التاسعة":9,"العاشر":10,"العاشره":10,"العاشرة":10,"الحادي عشر":11,"الحادية عشرة":11,"الثاني عشر":12,"الثانية عشرة":12,"الثالث عشر":13,"الثالثة عشرة":13,"الرابع عشر":14,"الرابعة عشرة":14,"الخامس عشر":15,"الخامسة عشرة":15,"السادس عشر":16,"السادسة عشرة":16,"السابع عشر":17,"السابعة عشرة":17,"الثامن عشر":18,"الثامنة عشرة":18,"التاسع عشر":19,"التاسعة عشرة":19,"العشرون":20,"العشرين":20}
ORD={re.sub(r"\s+"," ",k):v for k,v in ORD.items()}
WORDS=set("واحد واحده اثنين اثنان اثنتين ثلاثه ثلاث اربعه اربع خمسه خمس سته ست سبعه سبع ثمانيه ثماني تسعه تسع عشره عشر عشرين عشرون ثلاثين ثلاثون اربعين اربعون خمسين خمسون ستين ستون سبعين سبعون ثمانين ثمانون تسعين تسعون مائه مئه ميه الف الفين مليون مليار نصف ثلث ربع".split())
HEAD=re.compile(r"^\s*(?:المادة|مادة)\s*\(?\s*(.*?)\s*\)?\s*[:：\-–—]?\s*(.*)$")
def norm(s):
 s=unicodedata.normalize("NFKC",str(s or "")).translate(DIGITS);s=DIAC.sub("",s);s=re.sub(r"[أإآٱ]","ا",s).replace("ى","ي");return re.sub(r"[\u200b-\u200f\u202a-\u202e\ufeff]","",s)
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
def extract_heading(line):
 s=norm(line).strip()
 m=re.match(r"^(?:المادة|مادة)\s*(.*)$",s)
 if not m:return None,None
 rest=m.group(1).strip()
 n=re.match(r"^\(?\s*(\d+)\s*\)?(?:\s+(مكرر(?:ا|ة)?(?:\s+\(?[ء-ي]\s*\)?)?))?(?:\s+(.*))?$",rest,re.I)
 if n:
  suffix_letter=re.search(r"مكرر(?:ا|ة)?\s+\(?([ء-ي])",n.group(2)) if n.group(2) else None
  key=n.group(1)+((" مكرر"+((" "+suffix_letter.group(1)) if suffix_letter else "")) if n.group(2) else "")
  return key,(n.group(3) or "").strip()
 for ordinal in sorted(ORD,key=len,reverse=True):
  if rest==ordinal:return str(ORD[ordinal]),""
  if rest.startswith(ordinal+" "):return str(ORD[ordinal]),rest[len(ordinal):].strip()
 return None,None

def segment(s):
 out=[];cur=None;seen=Counter()
 for line in s.splitlines():
  key,body=extract_heading(line) if len(line)<400 else (None,None)
  key=label(key) if key is not None else None
  if key:
   seen[key]+=1;cur={"key":key,"occurrence":seen[key],"heading":line.strip()[:120],"parts":[]};out.append(cur)
   if body:cur["parts"].append(body)
  elif cur is not None:cur["parts"].append(line)
 for x in out:x["text"]="\n".join(x.pop("parts")).strip()
 return out
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
 c,w=readcand(cp);r=segment(Path(rp).read_text(encoding="utf-8"))
 if not r:w.append("No article headings detected in reference; nothing aligned.")
 res=compare(c,r,ratio);counts=Counter(x["status"] for x in res)
 return {"tool":"compare_corpus_to_reference","evidence_only":True,"disclaimer":"Text comparison only; it does not authenticate sources, establish legal status, prove amendment completeness, or authorize reuse/import. Human and lawyer review remain required.","candidate":{"path":str(cp),"sha256":digest(cp),"rows_compared":len(c)},"reference":{"path":str(rp),"sha256":digest(rp),"articles_detected":len(r)},"min_ratio":ratio,"summary":dict(sorted(counts.items())),"all_identical":bool(res) and set(counts)=={"identical_after_normalization"} and not w,"warnings":w,"articles":res}
def render(r):
 lines=["# Corpus vs reference comparison (evidence only)","",r["disclaimer"],"",f"- Candidate SHA-256: {r['candidate']['sha256']}; rows: {r['candidate']['rows_compared']}",f"- Reference SHA-256: {r['reference']['sha256']}; articles: {r['reference']['articles_detected']}","","## Summary",""]+[f"- {k}: {v}" for k,v in r["summary"].items()]+[f"- all identical: {r['all_identical']}",""]
 if r["warnings"]:lines+=["## Warnings",""]+["- "+w for w in r["warnings"]]+[""]
 pr={"numeric_difference":0,"major_difference":1,"missing_in_candidate":2,"extra_in_candidate":3,"minor_difference":4}
 for x in sorted([x for x in r["articles"] if x["status"]!="identical_after_normalization"],key=lambda z:(pr.get(z["status"],9),z["article"]))[:200]:
  lines += [f"### Article {x['article']} occurrence {x['occurrence']}: {x['status']}"]
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
