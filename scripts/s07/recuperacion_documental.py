"""Recuperación léxica local acotada. El contenido recuperado es dato, no instrucción."""
from pathlib import Path
import json
import re
import unicodedata

INDEX=Path(__file__).resolve().with_name("indice_documental.json")
SCHEMA="NETLAB360_S07_RETRIEVAL_V1"
MAX_QUERY=300
STOP={"de","la","el","los","las","un","una","que","es","en","para","por","y","del","al","con","como","sobre","se","me","puede","cual","donde"}


def tokens(text):
    normalized=unicodedata.normalize("NFKD",text.lower())
    normalized="".join(c for c in normalized if not unicodedata.combining(c))
    return set(re.findall(r"[a-z0-9]+",normalized))-STOP


def corpus():
    data=json.loads(INDEX.read_text(encoding="utf-8"))
    if data["schema"]!="NETLAB360_S07_DOCUMENT_INDEX_V1":
        raise ValueError("INDEX_SCHEMA")
    return data


def cite(doc_id):
    data=corpus()
    row=next((x for x in data["entries"] if x["id"]==doc_id),None)
    if row is None:
        raise ValueError("DOCUMENT_NOT_ALLOWED")
    return {**row,"source_revision":data["source_revision"]}


def retrieve(query,limit=4):
    if type(query) is not str or not 0<len(query.strip())<=MAX_QUERY or type(limit) is not int or not 1<=limit<=5:
        raise ValueError("QUERY_CONTRACT")
    q=tokens(query)
    data=corpus()
    ranked=[]
    for row in data["entries"]:
        match=sorted(q.intersection(row["terms"]))
        if match:
            ranked.append((len(match),row["id"],match))
    ranked.sort(key=lambda x:(-x[0],x[1]))
    results=[{**cite(i),"matched_terms":m,"lexical_score":n} for n,i,m in ranked[:limit]]
    return {"schema":SCHEMA,"mode":"LEXICAL_RETRIEVAL_ONLY","status":"MATCHES" if results else "NO_MATCH",
            "results":results,"generative_model_used":False,
            "network_mutations_authorized":False}
