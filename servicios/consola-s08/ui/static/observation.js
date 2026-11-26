/* Observabilidad propia: proyección de muestras reales, ventanas y notificaciones. */
(function(root){
  "use strict";
  const names=Object.freeze({
    "hq-s1-icmp":"HQ → S1 · ICMP","hq-s2-icmp":"HQ → S2 · ICMP",
    "s2-hq-http":"S2 → FE-HQ · HTTP","s2-hq-icmp":"S2 → FE-HQ · ICMP",
    "s2-hq-tcp":"S2 → FE-HQ · TCP"
  });
  const ids=Object.keys(names), minutes=[5,15,60];
  const quality={VALID:"Vigente al corte",STALE:"Desactualizada al corte",UNKNOWN:"Desconocida",
    ABSENT:"Sin muestras",INVALID:"Inválida",OBSERVED:"Completa",PARTIAL:"Parcial"};
  const finite=n=>typeof n==="number"&&Number.isFinite(n);
  const count=n=>Number.isSafeInteger(n)&&n>=0;
  const binary=n=>n===0||n===1;
  const nullable=(n,p)=>n===null||p(n);
  function requireValue(ok){if(!ok)throw Error("INVALID_OBSERVATION_CONTRACT");}
  function validate(data){
    requireValue(data?.schema==="NETLAB360_S08_OBSERVABILITY_V1"&&data.source==="PROMETHEUS_REAL"&&
      data.cadence_s===10&&data.target_pct===99&&finite(data.window_end_unix)&&
      Number.isFinite(Date.parse(data.window_end_utc))&&
      Math.abs(Date.parse(data.window_end_utc)/1000-data.window_end_unix)<0.002&&
      Array.isArray(data.probes)&&data.probes.length===5);
    const end=data.window_end_unix;
    const metrics=["up","probe_success","probe_duration_seconds","probe_http_status_code"];
    requireValue(metrics.every(k=>["OK","INVALID","UNAVAILABLE","UNKNOWN","NOT_STARTED"].includes(data.transport?.[k])));
    const seen=new Set();
    for(const row of data.probes){
      const id=row.probe?.id;
      requireValue(ids.includes(id)&&!seen.has(id)&&["VALID","STALE","UNKNOWN","ABSENT","INVALID"].includes(row.quality));
      seen.add(id);
      requireValue(Array.isArray(row.samples)&&row.samples.length<=400&&Array.isArray(row.windows)&&
        [0,3].includes(row.windows.length));
      let previous=end-3600;
      for(const s of row.samples){
        requireValue(finite(s.timestamp_unix)&&s.timestamp_unix>previous&&s.timestamp_unix<=end&&
          binary(s.scrape_up)&&nullable(s.probe_success,binary)&&
          nullable(s.duration_seconds,n=>finite(n)&&n>=0&&n<=5)&&
          nullable(s.http_status_code,n=>count(n)&&n<=599)&&
          (s.scrape_up===1||s.probe_success===null)&&
          (s.probe_success!==null||(s.duration_seconds===null&&s.http_status_code===null))&&
          (id==="s2-hq-http"||s.http_status_code===null));
        previous=s.timestamp_unix;
      }
      requireValue(row.samples.length?row.latest?.timestamp_unix===previous:row.latest===null);
      if(row.latest)for(const k of ["scrape_up","probe_success","duration_seconds","http_status_code"])
        requireValue(row.latest[k]===row.samples.at(-1)[k]);
      for(let i=0;i<row.windows.length;i++){
        const w=row.windows[i],m=minutes[i];
        requireValue(w.probe_id===id&&w.window_minutes===m&&w.nominal_slots===m*6&&
          w.target_pct===99&&w.cadence_s===10&&w.assessment==="PROVISIONAL_LAB_TARGET"&&
          ["OBSERVED","PARTIAL","ABSENT"].includes(w.quality)&&
          ["scrape_count","scrape_ok","probe_count","probe_ok","probe_fail","missing_slots","duplicate_slots"].every(k=>count(w[k]))&&
          w.probe_ok<=w.probe_count&&w.probe_count<=w.scrape_ok&&w.scrape_ok<=w.scrape_count&&
          w.probe_fail===w.probe_count-w.probe_ok);
        const samples=row.samples.filter(s=>s.timestamp_unix>end-m*60);
        requireValue(samples.length===w.scrape_count&&samples.filter(s=>s.scrape_up===1).length===w.scrape_ok&&
          samples.filter(s=>s.probe_success!==null).length===w.probe_count&&samples.filter(s=>s.probe_success===1).length===w.probe_ok);
        const pct=w.probe_count?100*w.probe_ok/w.probe_count:null;
        const budget=w.probe_count?Math.floor(w.probe_count/100)-w.probe_fail:null;
        const burn=w.probe_count?100*w.probe_fail/w.probe_count:null;
        requireValue(pct===null?w.observed_availability_pct===null:finite(w.observed_availability_pct)&&Math.abs(w.observed_availability_pct-pct)<1e-8);
        requireValue(w.remaining_budget_observed===budget&&
          (burn===null?w.burn_rate_observed===null:finite(w.burn_rate_observed)&&Math.abs(w.burn_rate_observed-burn)<1e-8));
        requireValue(w.meets_observed_target===(w.quality==="OBSERVED"&&pct!==null?pct>=99:null));
        if(w.quality==="OBSERVED")requireValue(w.scrape_count===w.nominal_slots&&w.probe_count===w.nominal_slots&&!w.missing_slots&&!w.duplicate_slots);
      }
    }
    return data;
  }
  function validateNotifications(data,scope){
    requireValue(data?.source==="ALERTMANAGER_WEBHOOK"&&data.scope===scope&&
      ["OK","INVALID","UNAVAILABLE","UNKNOWN"].includes(data.transport)&&Array.isArray(data.records)&&
      data.records.length<=200);
    if(data.transport!=="OK"){requireValue(data.total===null&&data.records.length===0);return data;}
    requireValue(count(data.total)&&data.records.length===Math.min(data.total,200)&&data.truncated===(data.total>data.records.length));
    let previous=Infinity;
    for(const r of data.records){
      requireValue(count(r.id)&&r.id>0&&r.id<previous&&r.scope===scope&&
        ["firing","resolved"].includes(r.status)&&typeof r.alertname==="string"&&r.alertname.length<=200&&
        Number.isFinite(Date.parse(r.starts_at_utc))&&Number.isFinite(Date.parse(r.received_at_utc))&&
        (r.status==="resolved"?Number.isFinite(Date.parse(r.ends_at_utc)):r.ends_at_utc===null));
      previous=r.id;
    }
    return data;
  }
  function httpLabel(code){return code===null?"Sin datos":code===0?"0 · Sin respuesta":code===200?"200 OK":String(code);}
  function httpState(code){return code===null||code===0?"unknown":code>=500?"fault":code>=400?"warn":code>=300?"recovery":code>=200?"ok":"unknown";}
  // Resúmenes de presentación: no sustituyen los valores del contrato.
  function overview(data){
    const fresh=data.probes.filter(p=>p.quality==="VALID"&&p.latest);
    return {fresh:fresh.length,acquired:fresh.filter(p=>p.latest.scrape_up===1).length,
      measured:fresh.filter(p=>p.latest.probe_success!==null).length,
      passed:fresh.filter(p=>p.latest.probe_success===1).length,
      complete:data.probes.flatMap(p=>p.windows).filter(w=>w.quality==="OBSERVED").length};
  }
  function httpHistory(data,span){
    requireValue(minutes.includes(span));
    const probe=data.probes.find(p=>p.probe.id==="s2-hq-http");
    const rows=probe.samples.filter(s=>s.timestamp_unix>data.window_end_unix-span*60).slice().reverse();
    const counts=new Map();
    for(const s of rows)counts.set(s.http_status_code,(counts.get(s.http_status_code)||0)+1);
    return {latest:probe.latest,quality:probe.quality,rows,recent:rows.filter(s=>s.timestamp_unix>data.window_end_unix-120),
      counts:[...counts].sort((a,b)=>(a[0]??Infinity)-(b[0]??Infinity))};
  }
  // Exportar el intervalo completo, sin imputar nulos ni redondear mediciones.
  function httpCsv(data,span){
    const h=httpHistory(data,span);
    const fields=["probe_id","window_minutes","window_end_utc","source","quality","http_transport","timestamp_utc","timestamp_unix","scrape_up","probe_success","duration_seconds","http_status_code"];
    const rows=h.rows.map(s=>["s2-hq-http",span,data.window_end_utc,data.source,h.quality,data.transport.probe_http_status_code,
      new Date(s.timestamp_unix*1000).toISOString(),s.timestamp_unix,s.scrape_up,s.probe_success,s.duration_seconds,s.http_status_code]);
    return [fields,...rows].map(row=>row.map(v=>v===null?"":String(v)).join(",")).join("\r\n")+"\r\n";
  }
  function durationStats(data,span){
    requireValue(minutes.includes(span));
    return ids.map(id=>{
      const points=data.probes.find(p=>p.probe.id===id).samples.filter(s=>s.timestamp_unix>data.window_end_unix-span*60&&s.duration_seconds!==null);
      const values=points.map(s=>s.duration_seconds*1000);
      return {id,count:values.length,last:values.at(-1)??null,
        mean:values.length?values.reduce((sum,n)=>sum+n,0)/values.length:null,
        max:values.length?Math.max(...values):null};
    });
  }
  function figure(data,key,format,colors,span){
    requireValue(["scrape_up","probe_success","duration_seconds"].includes(key)&&minutes.includes(span));
    const start=data.window_end_unix-span*60,end=data.window_end_unix, duration=key==="duration_seconds";
    const traces=[];
    const palette=colors.light?["#0069a6","#a33117","#536100","#753b9e","#006b54"]:["#72b7ff","#ff9d73","#e3cd64","#cf9aff","#69d5b5"];
    for(const [i,id] of ids.entries()){
      const row=data.probes.find(p=>p.probe.id===id);
      const points=row.samples.filter(s=>s.timestamp_unix>start);
      if(duration){
        const x=[],y=[],customdata=[];
        let last=null;
        for(const s of points){
          if(last!==null&&s.timestamp_unix-last>15){
            x.push(last+0.001);y.push(null);customdata.push("");
          }
          x.push(s.timestamp_unix);y.push(s[key]===null?null:s[key]*1000);
          customdata.push(format(new Date(s.timestamp_unix*1000)));last=s.timestamp_unix;
        }
        traces.push({type:"scatter",mode:"lines+markers",name:names[id],x,y,customdata,
          connectgaps:false,line:{color:palette[i],width:1.5},marker:{size:3},
          hovertemplate:names[id]+"<br>%{customdata}<br>%{y:.3f} ms<extra></extra>"});
      }else{
        const valid=points.filter(s=>binary(s[key]));
        traces.push({type:"scatter",mode:"markers",name:names[id],x:valid.map(s=>s.timestamp_unix),
          y:valid.map(()=>ids.length-1-i),customdata:valid.map(s=>[format(new Date(s.timestamp_unix*1000)),
            s[key]===1?(key==="scrape_up"?"Adquisición correcta":"Éxito"):(key==="scrape_up"?"Error de adquisición":"Fallo medido")]),
          marker:{size:span===60?2.5:span===15?4:6,color:valid.map(s=>s[key]===1?colors.ok:colors.fault),symbol:valid.map(s=>s[key]===1?"circle":"x")},
          showlegend:false,hovertemplate:names[id]+"<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>"});
      }
    }
    const ticks=Array.from({length:5},(_,i)=>start+(end-start)*(i+0.5)/5);
    return {traces,layout:{height:duration?400:215,autosize:true,paper_bgcolor:colors.surface,plot_bgcolor:colors.surface,
      font:{color:colors.text,size:12},margin:{l:duration?65:185,r:22,t:12,b:duration?105:45},
      hovermode:"closest",dragmode:"zoom",separators:".,",
      xaxis:{type:"linear",range:[start,end],tickmode:"array",tickvals:ticks,ticktext:ticks.map(t=>new Intl.DateTimeFormat("es-PA",{timeZone:"America/Panama",hour:"2-digit",minute:"2-digit",hourCycle:"h23"}).format(new Date(t*1000))),gridcolor:colors.line},
      yaxis:duration?{title:{text:"Duración (ms)"},rangemode:"tozero",gridcolor:colors.line}:
        {tickmode:"array",tickvals:ids.map((_,i)=>ids.length-1-i),ticktext:ids.map(id=>names[id]),ticklabelstandoff:12,range:[-0.6,4.6],fixedrange:true,gridcolor:colors.line,zeroline:false},
      legend:{orientation:"h",x:0.5,xanchor:"center",y:-0.24,yanchor:"top",entrywidth:138,entrywidthmode:"pixels",font:{size:11},traceorder:"normal"},uirevision:"sondas-"+key+"-"+span,showlegend:duration}};
  }
  function create(read,context,format,loadPlotly,number){
    const el=id=>document.getElementById("obs-"+id);
    const scope=el("scope");
    const charts=["scrape_up","probe_success","duration_seconds"];
    let epoch=0,data=null,busy=false,draw=Promise.resolve();
    let notifySequence=0,notifyTimer=null,probeTimer=null,notifyRequest=Promise.resolve();
    const permitted=()=>location.pathname==="/observability"&&context()?.active===true;
    const same=(e,actor)=>epoch===e&&permitted()&&context().key===actor;
    const text=(id,value)=>{el(id).textContent=value;};
    const state=(node,value)=>{node.dataset.state=value;};
    function cell(row,value,semantic){
      const td=document.createElement("td");td.textContent=String(value??"—");
      if(semantic)state(td,semantic);row.append(td);
    }
    function table(id,rows){el(id).replaceChildren(...rows);}
    function rowOf(values){
      const tr=document.createElement("tr");
      for(const v of values)Array.isArray(v)?cell(tr,v[0],v[1]):cell(tr,v);
      return tr;
    }
    function resetSummary(){
      for(const id of ["fresh","acquired","passed","complete","http-latest","http-detail","http-count","http-recent-count"])text(id,"—");
      el("http-export").disabled=true;
      table("http-codes",[]);table("http-distribution",[]);table("duration-stats",[]);
      state(el("http-latest"),"unknown");
    }
    function clear(){
      epoch++;data=null;busy=false;notifySequence++;
      clearTimeout(notifyTimer);clearTimeout(probeTimer);
      for(const id of ["latest","windows","http","notifications","cards"])table(id,[]);
      resetSummary();
      text("source","Sin observación vigente.");text("notice","Esperando observaciones autenticadas.");
      text("notify-status","Sin consulta de notificaciones.");
      for(const key of charts)el(key).hidden=true;
      draw=draw.catch(()=>{}).then(()=>{for(const key of charts){const node=el(key);if(root.Plotly)root.Plotly.purge(node);node.replaceChildren();}});
      controls();
    }
    function controls(){
      const active=permitted();
      scope.disabled=!active;
      el("http-export").disabled=!active||!data||!httpHistory(data,Number(el("span").value)).rows.length;
      const option=scope.querySelector('option[value="validation"]');
      option.hidden=context()?.role!=="OPERATOR";option.disabled=option.hidden;
      if(option.hidden&&scope.value==="validation"){scope.value="operational";table("notifications",[]);text("notify-status","Esperando notificaciones operacionales.");}
    }
    function render(result){
      const summary=overview(result);
      text("fresh",summary.fresh+" / 5");
      text("acquired",summary.acquired+" / 5");
      text("passed",summary.measured?summary.passed+" / "+summary.measured:"Sin datos");
      text("complete",summary.complete+" / 15");
      const labels={up:"Adquisición",probe_success:"Resultado",probe_duration_seconds:"Duración",probe_http_status_code:"HTTP"};
      const statuses={OK:"Disponible",INVALID:"Inválida",UNAVAILABLE:"No disponible",UNKNOWN:"Desconocida",NOT_STARTED:"Sin iniciar"};
      text("source","Prometheus · Blackbox · corte Panamá: "+format(new Date(result.window_end_unix*1000))+
        " · cadencia 10 s · "+Object.entries(result.transport).map(([k,v])=>labels[k]+": "+statuses[v]).join(" · "));
      table("latest",ids.map(id=>{
        const p=result.probes.find(r=>r.probe.id===id),s=p.latest;
        return rowOf([names[id],quality[p.quality],
          s?format(new Date(s.timestamp_unix*1000)):"—",
          s?[s.scrape_up===1?"Correcta":"Error",s.scrape_up===1?"ok":"fault"]:"Sin datos",
          s?.probe_success===1?["Éxito","ok"]:s?.probe_success===0?["Fallo medido","fault"]:["Sin datos","unknown"],
          s?.duration_seconds==null?"—":number(s.duration_seconds*1000,"latency")+" ms"]);
      }));
      const cards=ids.map(id=>{
        const section=document.createElement("section"),title=document.createElement("h3"),grid=document.createElement("div");
        section.className="obs-window";title.textContent=names[id];grid.className="obs-card-grid";
        const probe=result.probes.find(r=>r.probe.id===id);
        for(const m of minutes){
          const w=probe.windows.find(w=>w.window_minutes===m);
          const card=document.createElement("div"),label=document.createElement("span"),value=document.createElement("strong"),detail=document.createElement("small");
          card.className="obs-card";label.textContent=m+" min";
          value.textContent=w?.observed_availability_pct==null?"—":number(w.observed_availability_pct,"percentage")+" %";
          detail.textContent=w?quality[w.quality]+" · "+w.probe_count+"/"+w.nominal_slots+" medidas":"Sin datos";
          state(card,w?.meets_observed_target===true?"ok":w?.meets_observed_target===false?"fault":"unknown");
          card.append(label,value,detail);grid.append(card);
        }
        section.append(title,grid);return section;
      });
      table("cards",cards);
      table("windows",minutes.flatMap(m=>ids.map(id=>{
        const w=result.probes.find(r=>r.probe.id===id).windows.find(w=>w.window_minutes===m);
        if(!w)return rowOf([m+" min",names[id],"—","—","—","—","—","—","—","Sin datos"]);
        const assessment=w.meets_observed_target===true?["Objetivo observado","ok"]:w.meets_observed_target===false?["Bajo objetivo","fault"]:["No concluyente","unknown"];
        return rowOf([m+" min",names[id],w.observed_availability_pct===null?"—":number(w.observed_availability_pct,"percentage")+" %",
          w.scrape_count+" / "+w.nominal_slots,w.scrape_ok,w.probe_count,w.probe_ok,
          w.remaining_budget_observed===null?"—":number(w.remaining_budget_observed,"count"),
          w.burn_rate_observed===null?"—":number(w.burn_rate_observed,"burn")+"×",
          [quality[w.quality]+" · "+assessment[0],assessment[1]]]);
      })));
      renderInterval(result);
    }
    function renderInterval(result){
      const ms=n=>n===null?"—":number(n,"latency")+" ms";
      table("duration-stats",durationStats(result,Number(el("span").value)).map(s=>rowOf([names[s.id],s.count,ms(s.last),ms(s.mean),ms(s.max)])));
      const h=httpHistory(result,Number(el("span").value));
      text("http-latest",h.latest?httpLabel(h.latest.http_status_code):"Sin datos");
      state(el("http-latest"),h.quality==="VALID"&&h.latest?httpState(h.latest.http_status_code):"unknown");
      text("http-detail",h.latest?quality[h.quality]+" · "+format(new Date(h.latest.timestamp_unix*1000)):quality[h.quality]);
      text("http-count",h.rows.length+" muestras adquiridas en el intervalo");
      const tags=h.counts.map(([code,n])=>{
        const tag=document.createElement("span");
        tag.className="obs-code-tag";state(tag,httpState(code));
        tag.textContent=httpLabel(code)+" · "+n;
        return tag;
      });
      table("http-codes",tags);
      const segments=h.counts.map(([code,n])=>{
        const segment=document.createElement("span");state(segment,httpState(code));
        segment.style.flexGrow=String(n);segment.title=httpLabel(code)+" · "+n;return segment;
      });
      table("http-distribution",segments);
      el("http-distribution").setAttribute("aria-label",h.counts.length?h.counts.map(([code,n])=>httpLabel(code)+": "+n).join(", "):"Sin muestras adquiridas");
      text("http-recent-count",h.recent.length+" muestras");
      table("http",h.recent.map(s=>rowOf([format(new Date(s.timestamp_unix*1000)),[httpLabel(s.http_status_code),httpState(s.http_status_code)]])));
      el("http-export").disabled=!permitted()||!h.rows.length;
    }
    function renderPlots(){
      const current=data,e=epoch,actor=context()?.key;
      draw=draw.catch(()=>{}).then(async()=>{
        if(!current||!same(e,actor)||current!==data)return;
        const plot=await loadPlotly();
        if(!same(e,actor)||current!==data)return;
        const style=getComputedStyle(document.documentElement),color=k=>style.getPropertyValue("--"+k).trim();
        const colors={light:document.documentElement.dataset.theme==="light",surface:color("surface"),text:color("text"),line:color("line"),ok:color("ok"),fault:color("fault")};
        for(const key of charts){
          if(!same(e,actor)||current!==data)return;
          const node=el(key),f=figure(current,key,format,colors,Number(el("span").value));
          node.hidden=false;
          await plot.react(node,f.traces,f.layout,{responsive:true,displaylogo:false,modeBarButtonsToRemove:["lasso2d","select2d","toImage"]});
          if(!same(e,actor))node.hidden=true;
        }
      }).catch(()=>{if(same(e,actor)){for(const key of charts)el(key).hidden=true;text("notice","Datos recibidos; no se pudo representar el gráfico.");}});
      return draw;
    }
    async function refresh(retry=true){
      if(!permitted()||busy||document.hidden)return;
      clearTimeout(probeTimer);
      const e=epoch,actor=context().key;busy=true;controls();
      text("notice","Consultando muestras reales…");
      try{
        const {status,data:result}=await read("/api/v1/observability/probes",1048576);
        if(!same(e,actor))return;
        if(status===429&&retry){
          text("notice","Consulta ocupada; reintento acotado. Los datos anteriores conservan su corte.");
          clearTimeout(probeTimer);probeTimer=setTimeout(()=>{if(same(e,actor))void refresh(false);},2100);
          return;
        }
        if(status!==200)throw Error("HTTP_"+status);
        data=validate(result);render(data);
        text("notice","Observación al corte indicado. La actualización periódica solo consulta las sondas.");
        await renderPlots();
      }catch(error){
        if(same(e,actor)){data=null;for(const id of ["latest","windows","http","cards"])table(id,[]);
          for(const key of charts)el(key).hidden=true;resetSummary();text("source","Sin observación confirmada.");
          text("notice",error.message==="HTTP_429"?"Consulta ocupada. Reintente después de dos segundos.":"No se pudo confirmar la observación.");}
      }finally{if(epoch===e){busy=false;controls();}}
    }
    function refreshNotifications(){
      const sequence=++notifySequence;
      clearTimeout(notifyTimer);
      table("notifications",[]);text("notify-status","Consultando notificaciones…");
      notifyRequest=notifyRequest.catch(()=>{}).then(()=>queryNotifications(sequence,true));
      return notifyRequest;
    }
    async function queryNotifications(sequence,retry){
      if(!permitted()||document.hidden||sequence!==notifySequence)return;
      const e=epoch,actor=context().key,selected=scope.value;
      if(!["operational","validation"].includes(selected)||(selected==="validation"&&context().role!=="OPERATOR"))return;
      controls();table("notifications",[]);text("notify-status","Consultando notificaciones…");
      try{
        const {status,data:result}=await read("/api/v1/alerts/notifications/"+selected,2097152);
        if(!same(e,actor)||scope.value!==selected||sequence!==notifySequence)return;
        if(status===429&&retry){
          text("notify-status","Consulta ocupada; reintento en dos segundos.");
          notifyTimer=setTimeout(()=>{if(same(e,actor)&&sequence===notifySequence){notifyRequest=notifyRequest.catch(()=>{}).then(()=>queryNotifications(sequence,false));}},2100);
          return;
        }
        if(status!==200)throw Error("HTTP_"+status);
        const batch=validateNotifications(result,selected);
        text("notify-status",batch.transport==="OK"?number(batch.total,"count")+" registros · "+(batch.truncated?"Últimos 200 · ":"")+
          (selected==="validation"?"Validación sintética, no operacional.":batch.total===0?"No hay notificaciones operacionales registradas.":"Notificaciones operacionales."):"Fuente "+batch.transport+"; cantidad no confirmada.");
        const labels=Object.freeze({
          NETLAB360S08ProbeFailed:"Fallo medido de la sonda",
          NETLAB360S08ProbeAcquisitionFailed:"Fallo de adquisición de métricas",
          NETLAB360S08ProbeMetricMissing:"Métrica de resultado ausente",
          NETLAB360S08Validation:"Validación sintética de notificaciones"
        });
        table("notifications",batch.records.map(r=>{
          const row=rowOf([labels[r.alertname]||"Alerta sin descripción catalogada",names[r.labels?.probe_id]??"—",
            r.status==="firing"?["Activación","fault"]:["Resolución","recovery"],
            format(new Date(r.starts_at_utc)),r.ends_at_utc?format(new Date(r.ends_at_utc)):"—",
            format(new Date(r.received_at_utc))]);
          const id=document.createElement("small");id.className="muted obs-alert-id";id.textContent=r.alertname;row.firstChild.append(id);return row;
        }));
      }catch(error){if(same(e,actor)&&scope.value===selected&&sequence===notifySequence)text("notify-status",error.message==="HTTP_429"?"Consulta ocupada. Reintente después de dos segundos.":"No se pudo confirmar la fuente.");}
      finally{if(epoch===e)controls();}
    }
    function downloadHttp(){
      if(!permitted()||!data)return;
      const span=Number(el("span").value),h=httpHistory(data,span);
      if(!h.rows.length)return;
      const csv=httpCsv(data,span);
      const url=URL.createObjectURL(new Blob([csv],{type:"text/csv;charset=utf-8"}));
      const link=document.createElement("a");
      link.href=url;link.download="netlab360-http-s2-hq-"+span+"min-"+data.window_end_utc.replace(/[:.]/g,"-")+".csv";
      link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
    }
    el("http-export").addEventListener("click",downloadHttp);
    scope.addEventListener("change",refreshNotifications);
    el("span").addEventListener("change",()=>{if(data&&permitted()){renderInterval(data);renderPlots();}});
    new MutationObserver(()=>{if(data&&permitted())renderPlots();}).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});
    return {clear,controls,refresh,refreshNotifications};
  }
  root.NetlabObservation=Object.freeze({names,validate,validateNotifications,httpLabel,httpState,overview,httpHistory,httpCsv,durationStats,figure,create});
})(typeof window==="undefined"?globalThis:window);
