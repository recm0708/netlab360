/* Consola de trabajos: autoridad del servidor, sondeo sin renovar sesión y muestras reales. */
"use strict";

function createJobsView(context, request, formatDate) {
  const byId = id => document.getElementById("jobs-" + id);
  const fields = ["action", "route", "profile"].map(byId);
  const start = byId("start"), cancel = byId("cancel"), notice = byId("notice");
  const history = byId("history");
  const actions = {"test.ping.short":"Ping corto", "test.ping.long":"Ping extendido",
    "test.traceroute":"Traceroute", "test.http":"HTTP", "test.iperf.tcp":"iPerf3 TCP",
    "test.iperf.udp":"iPerf3 UDP", "test.content.tcp":"Transferencia de contenido TCP"};
  const routes = {HQ_A_S1:"HQ → S1", HQ_A_S2:"HQ → S2", S2_A_FRONTAL_HQ:"S2 → Frontal HQ"};
  // Las etiquetas son de presentación; el contrato y los identificadores de exportación se conservan.
  const configurations = {"test.ping.short":"4 paquetes ICMP", "test.ping.long":"20 paquetes ICMP",
    "test.traceroute":"Hasta 12 saltos", "test.http":"HTTP · plazo de 5 s"};
  const profiles = {"tcp-10s":"10 s · 20 Mbit/s", "udp-10s":"10 s · 20 Mbit/s",
    "tcp-100mb":"100 MB · 20 Mbit/s", "tcp-500mb":"500 MB · 100 Mbit/s",
    "tcp-1gb":"1 GB · 100 Mbit/s", "tcp-2gb":"2 GB · 100 Mbit/s", "tcp-5gb":"5 GB · 100 Mbit/s",
    "content-100mb":"100 MB · 100 Mbit/s", "content-500mb":"500 MB · 100 Mbit/s",
    "content-1gb":"1 GB · 100 Mbit/s", "content-2gb":"2 GB · 100 Mbit/s",
    "content-5gb":"5 GB · 100 Mbit/s"};
  const states = {QUEUED:"En cola", RUNNING:"En ejecución", SUCCEEDED:"Completada",
    FAILED:"Fallida", CANCELLED:"Cancelada"};
  const actionLabel = row => actions[row.action] || row.action;
  const profileLabel = row => row.profile === "default" ? (configurations[row.action] || row.profile) :
    (profiles[row.profile] || row.profile);
  const dateLabel = value => {
    const date = new Date(value);
    return typeof value === "string" && Number.isFinite(date.getTime()) ? formatDate(date) : "—";
  };
  const statusLabel = job => job.execution_quality === "UNCERTAIN" || job.data?.execution_quality === "UNCERTAIN" ?
    "Incierto" : (states[job.status] || job.status) +
    ((job.cancel_requested || job.data?.cancel_requested) && job.status === "RUNNING" ? " · Cancelación solicitada" : "");
  const active = job => ["QUEUED","RUNNING"].includes(job?.status);
  const uuid = value => typeof value === "string" && /^[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}$/.test(value);
  let generation = 0, configured = false, pending = false, choices = [], selected = null, owner = null, occupied = false;
  let lastPoll = 0, loaded = false, requestedId = null;
  let historical=null,historyFingerprint=null,historicalOpen=false;
  const text = (id,value) => {byId(id).textContent = String(value ?? "—");};
  const number = NetlabNumbers.format;
  const permitted = () => location.pathname === "/diagnostics" && context()?.role === "OPERATOR" && context()?.active;
  const selection = () => choices.find(row => fields.every((field,i) => field.value === row[["action","route","profile"][i]]));
  function options(field, values, labels = {}) {
    const previous = field.value;
    field.replaceChildren(...values.map(value => new Option(labels[value] || value,value)));
    if (values.includes(previous)) field.value = previous;
  }
  function filters() {
    options(fields[0], [...new Set(choices.map(x=>x.action))], actions);
    options(fields[1], [...new Set(choices.filter(x=>x.action===fields[0].value).map(x=>x.route))], routes);
    const relevant = choices.filter(x=>x.action===fields[0].value&&x.route===fields[1].value);
    options(fields[2], [...new Set(relevant.map(x=>x.profile))],
      Object.fromEntries(relevant.map(row=>[row.profile,profileLabel(row)])));
    const row = selection();
    const rateNote = row && row.profile !== "default" ? "Tasa objetivo configurada, no rendimiento garantizado. " : "";
    text("profile-note", row ? rateNote + (row.live_progress ? "Contadores reales en vivo y cancelación activa de la transferencia." :
      "Seguimiento del estado; métricas de la prueba al finalizar. Cancelación solo en cola.") + " Plazo máximo: " + number(row.deadline_s,"count") + " s." : "");
    controls();
  }
  function controls() {
    const enabled = permitted() && configured && !pending;
    fields.forEach(field=>{field.disabled=!enabled || occupied;});
    start.disabled = !enabled || occupied || !selection();
    cancel.disabled = !enabled || !active(selected) || selected?.data?.cancel_requested === true ||
      selected?.data?.execution_quality === "UNCERTAIN" ||
      (selected.status !== "QUEUED" && selected?.data?.stream_enabled !== true);
    byId("json").disabled = byId("csv").disabled = !enabled || !selected || active(selected);
  }
  function clearResult() {
    selected = null;
    text("title","Resultado de la prueba");
    text("state","Sin trabajo");
    byId("transfer-panel").hidden=true;
    byId("diagnostic-panel").hidden=true;
    byId("diagnostic-rows").replaceChildren(); byId("state").dataset.state="unknown";
    for (const id of ["detail","tx","rx","tx-rate","rx-rate","metrics","output"]) text(id,"—");
    byId("events").replaceChildren(); byId("progress").hidden=true; byId("progress").value=0;
    text("progress-note","Sin medición.");
  }
  function reset() {
    generation++; configured=false; pending=false; loaded=false; occupied=false; choices=[]; owner=null; requestedId=null;
    historical=null;historyFingerprint=null;historicalOpen=false;lastPoll=0;
    fields.forEach(field=>field.replaceChildren()); history.replaceChildren(); clearResult();
    text("profile-note",""); notice.textContent="Sin catálogo autenticado."; controls();
  }
  function samples(job) {
    const progress = job.data?.progress || [], m = job.data?.result?.measurement || {};
    if (progress.length) return progress.map(x=>({role:x.role,time:x.elapsed_s,bytes:x.bytes,rate:x.mbps,kind:Number.isFinite(x.interval_bytes)?"IPERF_ACUMULADO":"CONTENIDO_ACUMULADO",intervalBytes:x.interval_bytes,start:x.start_s}));
    return ["sender","receiver"].flatMap(role=>(m[role+"_intervals"] || []).map(x=>(
      {role,time:x.end_s,bytes:x.bytes,rate:x.mbps,kind:"IPERF_INTERVALO_FINAL"})));
  }
  function measurementSummary(job){
    const data=job.data,m=data.result?.measurement;
    const metrics=m?[["Estado de medición",m.status],["Paquetes enviados",m.sent,"count"],["Paquetes recibidos",m.received,"count"],
      ["RTT mín. (ms)",m.rtt_min_ms,"latency"],["RTT medio (ms)",m.rtt_avg_ms,"latency"],["RTT máx. (ms)",m.rtt_max_ms,"latency"],
      ["RTT p95 (ms)",m.rtt_p95_ms,"latency"],["Pérdida (%)",m.loss_pct,"loss"],
      ["Saltos",Array.isArray(m.hops)?m.hops.length:null,"count"],
      ["Destino alcanzado",typeof m.reached==="boolean"?(m.reached?"Sí":"No"):null],
      ["Tiempo HTTP (ms)",m.elapsed_ms,"latency"],["Backend activo",m.active_backend],
      ["Jitter (ms)",m.jitter_ms,"jitter"],["Retransmisiones TCP",m.retransmissions,"count"],["HTTP",m.http_status],
      ["Integridad de contenido",data.selection.action==="test.content.tcp" && typeof m.content_integrity_verified==="boolean"?(m.content_integrity_verified?"Verificada":"No verificada"):null]]:
      [];
    if(job.status==="CANCELLED")metrics.push(["Limpieza",data.cleanup_verified===true?"Verificada":"Sin confirmar"]);
    return metrics.filter(x=>x[1]!==null&&x[1]!==undefined).map(x=>x[0]+": "+(x[2]?number(x[1],x[2]):x[1])).join(" · ");
  }
  function render(job) {
    if (!uuid(job?.job_id) || job?.actor_id!==owner || !job.data?.selection) throw new Error("INVALID_JOB");
    selected=job;
    const data=job.data, m=data.result?.measurement, points=samples(job);
    const tx=points.filter(x=>x.role==="sender").at(-1), rx=points.filter(x=>x.role==="receiver").at(-1);
    text("title","Resultado · "+actionLabel(data.selection));
    text("state",statusLabel(job)+" · "+job.status);
    byId("state").dataset.state=data.execution_quality==="UNCERTAIN"?"warn":job.status==="SUCCEEDED"?"ok":job.status==="FAILED"?"fault":"unknown";
    text("detail",dateLabel(job.created_at_utc)+" · "+profileLabel(data.selection)+" · "+
      (routes[data.selection.route]||data.selection.route)+" · ID: "+job.job_id);
    const transfer = data.selection.action.startsWith("test.iperf.") || data.selection.action === "test.content.tcp";
    byId("transfer-panel").hidden=!transfer;
    byId("diagnostic-panel").hidden=transfer;
    text("tx",number(m?.bytes_sent ?? (data.progress?.length ? tx?.bytes : undefined),"bytes")+" bytes");
    text("rx",number(m?.bytes_received ?? (data.progress?.length ? rx?.bytes : undefined),"bytes")+" bytes");
    text("tx-rate",number(m?.sender_mbps ?? tx?.rate,"rate")+" Mbit/s");
    text("rx-rate",number(m?.receiver_mbps ?? rx?.rate,"rate")+" Mbit/s");
    const targets={"content-100mb":100000000,"content-500mb":500000000,"content-1gb":1000000000,"content-2gb":2000000000,"content-5gb":5000000000,
      "tcp-100mb":100000000,"tcp-500mb":500000000,"tcp-1gb":1000000000,"tcp-2gb":2000000000,"tcp-5gb":5000000000};
    const target=m?.target_bytes ?? targets[data.selection.profile];
    const received=m?.bytes_received ?? (data.progress?.length ? rx?.bytes : undefined);
    const measured=Number.isFinite(target)&&target>0&&Number.isFinite(received);
    byId("progress").hidden=!measured;
    if (measured) byId("progress").value=Math.min(100,received*100/target);
    text("progress-note",measured?number(received,"bytes")+" / "+number(target,"bytes")+" bytes observados · "+number(received*100/target,"percentage")+" % del objetivo":
      Number.isFinite(rx?.time)?"Tiempo observado del receptor: "+number(rx.time,"seconds")+" s":
      active(job)?"Esperando medición; no se estima el avance por tiempo.":"Sin volumen medible.");
    text("metrics",measurementSummary(job));
    const diagnosticRows = (Array.isArray(m?.hops)?m.hops:Array.isArray(m?.samples)?m.samples:[]).map(item=>{
      const li=document.createElement("li");
      li.textContent=Array.isArray(m.hops)?"Salto "+item.hop+" · "+(item.address ?? "Sin respuesta")+
        (item.rtt_ms==null?"":" · "+number(item.rtt_ms,"latency")+" ms")+(item.annotation?" · "+item.annotation:""):
        "Paquete "+item.seq+" · "+number(item.rtt_ms,"latency")+" ms";
      return li;
    });
    byId("diagnostic-rows").replaceChildren(...diagnosticRows);
    text("diagnostic-note",m?(diagnosticRows.length?"Mediciones individuales observadas.":"Consulte el resumen y el resultado detallado."):
      active(job)?"Esperando resultado del diagnóstico.":"Sin medición confirmada.");
    const rows=points.map(point=>{
      const tr=document.createElement("tr");
      for(const value of [point.role==="sender"?"Emisor":"Receptor",number(point.time,"seconds"),number(point.kind==="IPERF_INTERVALO_FINAL"?null:point.bytes,"bytes"),number(point.kind==="IPERF_INTERVALO_FINAL"?point.bytes:point.intervalBytes,"bytes"),number(point.rate,"rate")]){
        const td=document.createElement("td");td.textContent=value;tr.append(td);
      }
      return tr;
    });
    byId("events").replaceChildren(...rows);
    text("output",data.result?JSON.stringify(data.result,null,2):data.execution_quality==="UNCERTAIN"?
      "Resultado no confirmado; la reserva permanece activa.":"Sin resultado final.");
    controls();
  }
  async function call(path, options={}) {
    const response=await request(path, options);
    if (!response.ok) throw new Error("HTTP "+response.status);
    return response.json();
  }
  async function loadHistory(epoch, preferred=null) {
    const body=await call("/api/v1/jobs");
    if(epoch!==generation || !permitted()) return;
    if(!Array.isArray(body.jobs)||body.jobs.length>50)throw new Error("INVALID_HISTORY");
    occupied=body.jobs.some(active);
    const fingerprint=JSON.stringify(body.jobs);
    if(fingerprint!==historyFingerprint){
    const focused=document.activeElement?.closest("tr[data-job-id]")?.dataset.jobId;
    const rows=body.jobs.map(job=>{
      if(!uuid(job.job_id))throw new Error("INVALID_HISTORY_ID");
      const tr=document.createElement("tr");
      tr.dataset.jobId=job.job_id;
      tr.dataset.selected=String(historical?.job_id===job.job_id);
      for(const [index,value] of [dateLabel(job.created_at_utc),actionLabel(job.selection),profileLabel(job.selection),
          routes[job.selection.route]||job.selection.route,statusLabel(job)].entries()){
        const td=document.createElement("td");td.textContent=value;
        if(index===4){td.dataset.state=job.execution_quality==="UNCERTAIN"?"warn":job.status==="SUCCEEDED"?"ok":job.status==="FAILED"?"fault":"unknown";td.title=job.status;}
        tr.append(td);
      }
      const td=document.createElement("td"),button=document.createElement("button");
      button.type="button";button.textContent=historical?.job_id===job.job_id?"Ocultar resultado":"Ver resultado";button.className="secondary";
      button.setAttribute("aria-expanded",String(historical?.job_id===job.job_id));
      button.setAttribute("aria-label","Ver resultado de "+actionLabel(job.selection)+" · "+dateLabel(job.created_at_utc));
      button.addEventListener("click",()=>openResult(job.job_id));
      td.append(button);tr.append(td);return tr;
    });
    history.replaceChildren(...rows);historyFingerprint=fingerprint;
    if(historical&&!body.jobs.some(job=>job.job_id===historical.job_id))historical=null;
    mountHistorical();
    if(focused)Array.from(history.querySelectorAll("tr[data-job-id]")).find(row=>row.dataset.jobId===focused)?.querySelector("button")?.focus({preventScroll:true});
    }
    text("history-status",number(body.jobs.length,"count")+" trabajos · Historial actualizado automáticamente.");
    const id=preferred || body.jobs.find(active)?.job_id || selected?.job_id;
    if(id&&uuid(id)&&(preferred||active(selected)||selected?.job_id!==id)){
      const job=await call("/api/v1/jobs/"+id);
      if(epoch===generation&&permitted())render(job);
    }
    if(historical&&active(historical)){
      const id=historical.job_id,job=await call("/api/v1/jobs/"+id);
      if(epoch===generation&&permitted()&&historical?.job_id===id){
        if(job?.job_id!==id||job.actor_id!==owner||!job.data?.selection)throw Error("INVALID_JOB");
        historical=job;mountHistorical();
      }
    }
  }
  function mountHistorical(){
    const previous=history.querySelector(".jobs-history-detail");
    previous?.remove();
    for(const row of history.querySelectorAll("tr[data-job-id]")){
      const current=row.dataset.jobId===historical?.job_id,button=row.querySelector("button");
      row.dataset.selected=String(current);button.textContent=current?"Ocultar resultado":"Ver resultado";
      button.setAttribute("aria-expanded",String(current));
    }
    if(!historical)return;
    const row=Array.from(history.querySelectorAll("tr[data-job-id]")).find(r=>r.dataset.jobId===historical.job_id);
    if(!row)return;
    const job=historical,detail=document.createElement("tr"),td=document.createElement("td"),panel=document.createElement("section");
    detail.className="jobs-history-detail";td.colSpan=6;panel.className="panel";
    const add=(tag,value)=>{const node=document.createElement(tag);node.textContent=value;panel.append(node);return node;};
    add("h3",actionLabel(job.data.selection)+" · "+statusLabel(job));
    add("p",dateLabel(job.created_at_utc)+" · "+profileLabel(job.data.selection)+" · "+routes[job.data.selection.route]);
    add("p",measurementSummary(job)||"Sin medición final confirmada.");
    const m=job.data.result?.measurement,points=samples(job),tx=points.filter(p=>p.role==="sender").at(-1),rx=points.filter(p=>p.role==="receiver").at(-1);
    const sent=m?.bytes_sent??tx?.bytes,received=m?.bytes_received??rx?.bytes;
    if(Number.isFinite(sent)||Number.isFinite(received))add("p","Emisor: "+number(sent,"bytes")+" bytes · Receptor: "+number(received,"bytes")+" bytes · Rendimiento receptor: "+number(m?.receiver_mbps??rx?.rate,"rate")+" Mbit/s");
    if(points.length){
      const list=document.createElement("ul");
      for(const p of points){const li=document.createElement("li");li.textContent=(p.role==="sender"?"Emisor":"Receptor")+" · "+number(p.time,"seconds")+" s · "+number(p.bytes,"bytes")+" bytes ("+(p.kind==="IPERF_INTERVALO_FINAL"?"intervalo":"acumulados")+") · "+number(p.rate,"rate")+" Mbit/s";list.append(li);}
      const samplesDetail=document.createElement("details"),caption=document.createElement("summary");caption.textContent="Muestras de transferencia ("+number(points.length,"count")+")";samplesDetail.append(caption,list);panel.append(samplesDetail);
    }
    const diagnostic=Array.isArray(m?.hops)?m.hops:Array.isArray(m?.samples)?m.samples:[];
    if(diagnostic.length){const list=document.createElement("ul");for(const p of diagnostic){const li=document.createElement("li");li.textContent=(Array.isArray(m.hops)?"Salto "+p.hop+" · "+(p.address??"Sin respuesta"):"Paquete "+p.seq)+(p.rtt_ms==null?"":" · "+number(p.rtt_ms,"latency")+" ms");list.append(li);}panel.append(list);}
    const details=document.createElement("details"),summary=document.createElement("summary"),pre=document.createElement("pre");
    details.open=historicalOpen;details.addEventListener("toggle",()=>{if(details.isConnected)historicalOpen=details.open;});summary.textContent="Registro completo (JSON original)";pre.textContent=JSON.stringify(job,null,2);details.append(summary,pre);panel.append(details);
    const actions=document.createElement("div");actions.className="action-row";
    for(const format of ["json","csv"]){const button=document.createElement("button");button.type="button";button.textContent="Exportar "+format.toUpperCase();button.disabled=active(job);button.addEventListener("click",()=>download(format,job));actions.append(button);}
    panel.append(actions);td.append(panel);detail.append(td);row.after(detail);
  }
  function openResult(id) {
    if(!permitted()||!configured||!uuid(id))return;
    if(pending){requestedId=id;return;}
    if(historical?.job_id===id){historical=null;historicalOpen=false;mountHistorical();return;}
    void perform(async epoch=>{
      const result=await call("/api/v1/jobs/"+id);
      if(epoch===generation&&permitted()){
        if(!uuid(result?.job_id)||result.job_id!==id||result.actor_id!==owner||!result.data?.selection)throw Error("INVALID_JOB");
        historical=result;historicalOpen=false;mountHistorical();
      }
    });
  }
  async function perform(work) {
    if(pending||!permitted())return;
    const epoch=generation;pending=true;controls();
    try{await work(epoch);}
    catch(error){if(epoch===generation&&permitted()){
      const unavailable=!loaded && error.message==="HTTP 404";
      if(["HTTP 401","HTTP 403"].includes(error.message)){reset();lastPoll=performance.now()+5000;}
      else{configured=false;loaded=unavailable;lastPoll=performance.now()+5000;}
      notice.textContent=unavailable?"Ejecución de pruebas no habilitada en esta instancia.":"Consulta no confirmada ("+error.message+"). No se repite ninguna ejecución.";
    }}
    finally{if(epoch===generation){
      pending=false;controls();
      const id=requestedId;requestedId=null;
      if(id&&configured)openResult(id);
    }}
  }
  async function sync() {
    if(location.pathname!=="/diagnostics")return;
    if(!permitted()){
      if(owner!==null||loaded)reset();
      notice.textContent="Se requiere una sesión de operador vigente.";
      return;
    }
    const username=context().username;
    if(owner!==username){reset();owner=username;}
    if(document.hidden||pending||performance.now()-lastPoll<(loaded&&!occupied&&!active(selected)?10000:1000))return;
    lastPoll=performance.now();
    if(!loaded){
      await perform(async epoch=>{
        const result=await call("/api/v1/jobs/catalog");
        if(epoch!==generation||!permitted())return;
        if(result.transport_configured!==true||!Array.isArray(result.selections)||result.selections.length!==34)throw new Error("INVALID_CATALOG");
        choices=result.selections;configured=true;loaded=true;
        filters();await loadHistory(epoch);notice.textContent="Catálogo configurado. El broker confirma cada ejecución.";
      });
    }else{await perform(epoch=>loadHistory(epoch));}
  }
  fields.forEach(field=>field.addEventListener("change",filters));
  start.addEventListener("click",()=>perform(async epoch=>{
    const row=selection();if(!configured||occupied||!row)return;
    const job=await call("/api/v1/jobs",{method:"POST",headers:{"Content-Type":"application/json","X-CSRF-Token":context().csrf},
      body:JSON.stringify({action:row.action,route:row.route,profile:row.profile})});
    if(epoch===generation&&permitted()){render(job);occupied=true;await loadHistory(epoch,job.job_id);}
  }));
  cancel.addEventListener("click",()=>perform(async epoch=>{
    if(!active(selected))return;
    const job=await call("/api/v1/jobs/"+selected.job_id+"/cancel",{method:"POST",headers:{"X-CSRF-Token":context().csrf}});
    if(epoch===generation&&permitted()){render(job);await loadHistory(epoch,job.job_id);}
  }));
  function download(format,job=selected){
    if(!permitted()||!configured||!job||job.actor_id!==owner||active(job))return;
    const quote=value=>{
      // Neutralizar fórmulas de hojas de cálculo sin modificar el JSON original.
      let field=String(value??"");
      if(typeof value==="string"&&/^[\s]*[=+\-@]/.test(field))field="'"+field;
      return '"'+field.replaceAll('"','""')+'"';
    };
    const identity=[job.job_id,job.created_at_utc,dateLabel(job.created_at_utc),
      job.data.selection.action,actionLabel(job.data.selection),job.data.selection.profile,
      profileLabel(job.data.selection),job.data.selection.route,job.status];
    const rows=[["job_id","fecha_utc","fecha_panama","accion_id","prueba","perfil_id","configuracion",
      "ruta","estado","tipo","extremo","tiempo_s","bytes","mbps","metrica","valor"],
      ...samples(job).map(x=>[...identity,x.kind,x.role,x.time,x.bytes,x.rate,"",""])];
    for(const point of samples(job))if(Number.isFinite(point.intervalBytes))
      rows.push([...identity,"IPERF_INTERVALO_NATIVO",point.role,point.time,point.intervalBytes,point.rate,"inicio_s",point.start]);
    const m=job.data.result?.measurement || {};
    for(const [key,value] of Object.entries(m)){
      if(value!==null && ["string","number","boolean"].includes(typeof value))
        rows.push([...identity,"RESUMEN","","","","",key,value]);
    }
    for(const hop of Array.isArray(m.hops)?m.hops:[])rows.push([...identity,"SALTO","","","","","salto_"+hop.hop,JSON.stringify(hop)]);
    for(const packet of Array.isArray(m.samples)?m.samples:[])rows.push([...identity,"ICMP","","","","","paquete_"+packet.seq,packet.rtt_ms]);
    if(rows.length===1)rows.push([...identity,"SIN_MEDICION","","","","","",""]);
    const data=format==="json"?JSON.stringify(job,null,2):rows.map(row=>row.map(quote).join(",")).join("\r\n")+"\r\n";
    const url=URL.createObjectURL(new Blob([data],{type:format==="json"?"application/json":"text/csv;charset=utf-8"}));
    const link=document.createElement("a");link.href=url;link.download="netlab360-trabajo-"+job.job_id+"."+format;link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  }
  byId("json").addEventListener("click",()=>download("json"));
  byId("csv").addEventListener("click",()=>download("csv"));
  return {sync,reset,controls};
}
