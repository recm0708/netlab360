"""Construir snapshot de lectura S07, sin usarlo como evidencia de autorización."""
import json
from adquisicion_integrada import collect
from contrato_incidentes import candidates
from diagnostico_rca import diagnose
from recomendaciones_rca import recommend
from catalogo_runbooks import catalog

def snapshot():
    a=collect()
    return {"observed_at_utc":a["window"]["ended_at_utc"],"incidents":candidates(a),
            "hypotheses":{"diagnosis":diagnose(a),"recommendations":recommend(a)},
            "runbooks":catalog()}
if __name__=="__main__":
    print(json.dumps(snapshot(),indent=2,ensure_ascii=False,allow_nan=False))
