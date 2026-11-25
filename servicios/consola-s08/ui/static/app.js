/* Preferencia visual compartida entre acceso y consola. No contiene datos de sesión. */
"use strict";

const themeKey = "netlab360.theme.v1";
const themes = ["auto", "light", "dark"];
const systemTheme = matchMedia("(prefers-color-scheme: dark)");

function validTheme(value) {
  return themes.includes(value) ? value : "auto";
}

function readTheme() {
  try {
    return validTheme(localStorage.getItem(themeKey));
  } catch {
    return "auto";
  }
}

let themePreference = readTheme();

function applyTheme() {
  const effective = themePreference === "auto"
    ? (systemTheme.matches ? "dark" : "light")
    : themePreference;
  document.documentElement.dataset.theme = effective;
  const frame = document.getElementById("swagger-frame");
  if (frame?.contentDocument?.documentElement) {
    frame.contentDocument.documentElement.dataset.theme = effective;
  }
  const selector = document.getElementById("theme-select");
  if (selector) selector.value = themePreference;
}

function setTheme(value) {
  themePreference = validTheme(value);
  try {
    localStorage.setItem(themeKey, themePreference);
  } catch {
    // La selección sigue funcionando durante la página actual.
  }
  applyTheme();
}

// Aplicamos antes de construir el contenido y sincronizamos las pestañas.
applyTheme();
systemTheme.addEventListener("change", () => {
  if (themePreference === "auto") applyTheme();
});
window.addEventListener("storage", event => {
  if (event.key === themeKey || event.key === null) {
    themePreference = readTheme();
    applyTheme();
  }
});

document.addEventListener("DOMContentLoaded", () => {
  const selector = document.getElementById("theme-select");
  if (selector) {
    applyTheme();
    selector.addEventListener("change", () => setTheme(selector.value));
  }
  if (document.getElementById("console-shell")) initializeConsole();
});

/* Proyección del dashboard: inventario explícito y vigencia conservadora. */
const dashboardInventory = {
  sources: [
    ["EXPORTER_S04","MULTISEDE","Exportador","Inventario de routers",60],
    ["NOC_S05","MULTISEDE","Supervisión","Topología observada",60],
    ...["HQ","S1","S2"].map(s => ["NOC_S05","LACP-"+s,"Supervisión","LACP "+s,60]),
    ["NOC_S05","FAUCET","Supervisión","Faucet",60],
    ["NOC_S05","FRONTAL_HQ","Supervisión","Frontal HTTP HQ",60]
  ],
  metrics: [
    ["PROMETHEUS_S04","S04-EXPORTER","Prometheus","Exportador",60],
    ["PROMETHEUS_S04","S04-COLLECTOR","Prometheus","Colector",60],
    ["PROMETHEUS_S04","MULTISEDE","Prometheus","Inventario multisede",60],
    ...["HQ","S1","S2"].flatMap((s,i) => [
      ["PROMETHEUS_S04","R-"+s,"Prometheus","Router "+s,60],
      ...(i===0?["s1p","s1b","s2p","s2b"]:i===1?["s1p","s1b"]:["s2p","s2b"])
        .map(n => ["PROMETHEUS_S04","WAN-END-"+s+"-"+n,"Prometheus","WAN "+s+" / "+n,60]),
      ...[110,120,130].map(n => ["PROMETHEUS_S04","VLAN-"+(n+i*100),"Prometheus","VLAN "+(n+i*100),60])
    ])
  ],
  diagnostics: ["S1","S2"].map(s => ["IA_S06","HQ_A_"+s,"Inferencia","HQ → "+s,30]),
  advisory: ["INCIDENTS","HYPOTHESES","RUNBOOKS"].map((r,i) =>
    ["ADVISORY_S07",r,"Asesor",["Incidentes candidatos","Hipótesis","Runbooks"][i],60])
};

function dashboardBatch(key, payload, started) {
  const inventory = dashboardInventory[key];
  if (!inventory || payload?.project !== "NETLAB360" || payload.schema_version !== 1 ||
      payload.network_mutations_authorized !== false || payload.infrastructure_state !== "UNKNOWN" ||
      !Array.isArray(payload.observations) || payload.observations.length !== inventory.length) {
    throw new Error("INVALID_BATCH");
  }
  const map = new Map();
  for (const row of payload.observations) {
    const id = row?.source + "/" + row?.resource;
    const expected = inventory.find(x => x[0]+"/"+x[1]===id);
    if (!expected || map.has(id) || row.schema !== "NETLAB360_S08_SOURCE_V1" ||
        row.network_mutations_authorized !== false || row.max_age_seconds !== expected[4] ||
        !["OK","UNAVAILABLE","NOT_STARTED","INVALID"].includes(row.transport) ||
        !["VALID","MISSING","INVALID","FUTURE","STALE"].includes(row.quality) ||
        !["NORMAL","DEGRADED","FAULT","RECOVERY","UNKNOWN"].includes(row.state)) {
      throw new Error("INVALID_OBSERVATION");
    }
    const expectedKind = key === "diagnostics" ? "INFERENCE" : key === "advisory" ? "ADVISORY_SNAPSHOT" : "OBSERVATION";
    const scope = row.resource === "FRONTAL_HQ" ? "HTTP_FROM_S2" :
      row.resource === "FAUCET" ? "CONTROLLER_ONLY" :
      row.resource.startsWith("LACP-") ? "BOND_MEMBER_STATE" :
      row.resource.startsWith("WAN-END-") || row.resource.startsWith("VLAN-") ? "ADMIN_STATE_ONLY" :
      row.source === "EXPORTER_S04" ? "ROUTER_EXISTENCE_ONLY" :
      row.source === "NOC_S05" ? "TOPOLOGY_OBSERVATION" :
      row.resource === "S04-EXPORTER" ? "SCRAPE_AVAILABILITY" :
      row.resource === "S04-COLLECTOR" ? "COLLECTOR_READ" :
      row.source === "PROMETHEUS_S04" ? (row.resource === "MULTISEDE" ?
        "ROUTER_EXISTENCE_ONLY" : "CONTAINER_RUNNING_ONLY") :
      key === "diagnostics" ? "HQ_CLIENT_EGRESS_NETWORK_STATE" : null;
    if (row.kind !== expectedKind || (scope && row.scope !== scope)) throw new Error("INVALID_SCOPE");
    const valid = row.quality === "VALID";
    if (valid && (row.transport !== "OK" || typeof row.age_seconds !== "number" ||
        !Number.isFinite(row.age_seconds) || row.age_seconds < 0 || row.age_seconds > expected[4] ||
        typeof row.observed_at_utc !== "string" ||
        !Number.isFinite(Date.parse(row.observed_at_utc)) ||
        !row.details || typeof row.details !== "object" || Array.isArray(row.details))) {
      throw new Error("INVALID_FRESHNESS");
    }
    const state = valid && key !== "advisory" &&
      (key !== "diagnostics" || row.state === "NORMAL") &&
      !["ADMIN_STATE_ONLY","CONTAINER_RUNNING_ONLY","ROUTER_EXISTENCE_ONLY","TOPOLOGY_OBSERVATION"].includes(row.scope) ? row.state : "UNKNOWN";
    map.set(id, {source:expected[0],resource:expected[1],label:expected[2],
      name:expected[3],maxAge:expected[4],started,transport:row.transport,
      quality:row.quality,state,stamp:valid?row.observed_at_utc:null,
      age:valid?row.age_seconds:null,details:valid?row.details:{}});
  }
  return inventory.map(x => map.get(x[0]+"/"+x[1]));
}

function dashboardRows(batches, now) {
  return Object.entries(dashboardInventory).flatMap(([key, inventory]) => {
    const batch = batches[key];
    if (!batch || !Array.isArray(batch.rows)) {
      return inventory.map(x => ({source:x[0],resource:x[1],label:x[2],name:x[3],
        quality:batch?.error || "PENDING",state:"UNKNOWN",stamp:null,details:{}}));
    }
    return batch.rows.map(row => {
      // Sumamos el tiempo de ida y vuelta completo para no ampliar la vigencia.
      if (row.quality === "VALID" && row.age + Math.max(0,now-row.started)/1000 > row.maxAge) {
        return {...row, quality:"STALE",state:"UNKNOWN",details:{},stamp:row.stamp};
      }
      return row;
    });
  });
}

function dashboardSummary(rows) {
  const get = (source, resource) => rows.find(r => r.source===source && r.resource===resource);
  const valid = r => r?.quality==="VALID";
  const items = (source,prefix) => rows.filter(r => r.source===source && r.resource.startsWith(prefix));
  const count = (subset,predicate) => subset.filter(r => valid(r)&&predicate(r)).length;
  const result = {};
  const item = (id,text,state,detail) => {result[id]={text,state,detail};};
  const operational = rows.filter(r => !["IA_S06","ADVISORY_S07"].includes(r.source));
  const live = operational.filter(valid).length;
  item("coverage",live+" / "+operational.length,live===operational.length?"ok":live?"warn":"unknown",
    "Cobertura de observaciones; no equivale a disponibilidad de red.");
  const routers = get("EXPORTER_S04","MULTISEDE");
  const sites = ["R-HQ","R-S1","R-S2"];
  const values = sites.map(k=>routers?.details[k]);
  const present = valid(routers) && values.every(v=>v===0||v===1);
  const running = present ? values.reduce((a,b)=>a+b,0):null;
  item("routers",present?running+" / 3":"Sin datos","unknown","Contenedores detectados; no acredita OSPF ni forwarding.");
  for (const [id,prefix,total] of [["wan","WAN-END-",8],["vlan","VLAN-",9]]) {
    const subset = items("PROMETHEUS_S04",prefix);
    const known = count(subset,r=>[0,1].includes(r.details.admin_up));
    const up = count(subset,r=>r.details.admin_up===1);
    item(id,known?up+" / "+known+" activas":"Sin datos","unknown",
      known+" de "+total+" interfaces con muestra administrativa vigente; no acredita conectividad.");
  }
  const ha = get("NOC_S05","FRONTAL_HQ");
  const backend = {BACKEND_HQ:"HQ · principal",BACKEND_S1:"S1 · respaldo"};
  item("ha",valid(ha)?({NORMAL:"Normal",DEGRADED:"Degradado",FAULT:"Falla",UNKNOWN:"Desconocido",RECOVERY:"Recuperación"}[ha.state]):"Sin datos",
    valid(ha)?ha.state.toLowerCase():"unknown",
    valid(ha)&&backend[ha.details.active_backend]?backend[ha.details.active_backend]+" · desde S2":"Observación del frontal desde S2.");
  const lacp = items("NOC_S05","LACP-");
  const n = count(lacp,r=>r.state==="NORMAL"), k=lacp.filter(valid).length;
  const bondState = lacp.some(r=>valid(r)&&r.state==="FAULT")?"fault":
    lacp.some(r=>valid(r)&&r.state==="DEGRADED")?"degraded":n===3?"normal":"unknown";
  item("lacp",k?n+" / 3 normales":"Sin datos",bondState,k+" de 3 sedes con observación vigente de miembros.");
  const sdn=get("NOC_S05","FAUCET");
  const connected=valid(sdn)&&typeof sdn.details.connected==="boolean";
  item("sdn",connected?(sdn.details.connected?"Conectado":"Desconectado"):"Sin datos",
    connected?sdn.state.toLowerCase():"unknown",
    connected&&Number.isSafeInteger(sdn.details.flow_count)?sdn.details.flow_count+" flujos observados; no acredita forwarding.":"Estado del controlador, no de la red completa.");
  for (const [id,source,detail] of [["inference","IA_S06","Inferencias exploratorias; no confirman incidentes."],["advisory","ADVISORY_S07","Resúmenes históricos; no acreditan salud actual."]]) {
    const subset=rows.filter(r=>r.source===source);
    const available=subset.filter(valid).length;
    item(id,available?available+" / "+subset.length+" vigentes":"Sin datos","unknown",detail);
  }
  return result;
}

function dashboardDetail(row) {
  if(row.quality!=="VALID") return "—";
  const d=row.details;
  if (row.resource.startsWith("LACP-") && Number.isInteger(d.switch_members) && Number.isInteger(d.client_members))
    return "Switch "+d.switch_members+" / cliente "+d.client_members+" miembros";
  if (row.resource==="FAUCET" && typeof d.connected==="boolean")
    return d.connected?"Conectado · "+(Number.isSafeInteger(d.flow_count)?d.flow_count+" flujos":"flujos no disponibles"):"Desconectado";
  if (row.resource==="FRONTAL_HQ") return {BACKEND_HQ:"HQ · principal",BACKEND_S1:"S1 · respaldo"}[d.active_backend] || "Sin backend confirmado";
  if ([0,1].includes(d.admin_up)) return d.admin_up===1?"Admin. activa":"Admin. inactiva";
  if ([0,1].includes(d.running)) return d.running===1?"Contenedor activo":"Contenedor inactivo";
  if ([0,1].includes(d.up)) return d.up===1?"Scrape disponible":"Scrape fallido";
  if ([0,1].includes(d.source_up)) return d.source_up===1?"Lectura disponible":"Lectura fallida";
  if (["active","partial","offline"].includes(d.reported_topology))
    return {active:"Inventario activo",partial:"Inventario parcial",offline:"Inventario inactivo"}[d.reported_topology];
  if(row.source==="IA_S06"){
    const methods=["P95_RTT","IsolationForest","LogisticRegression"];
    const labels={NORMAL:"Normal",DEGRADED:"Indicio de degradación",UNKNOWN:"Sin consenso"};
    if(!methods.every(m=>["NORMAL","DEGRADED"].includes(d[m]))||
       !Number.isFinite(d.rtt_avg_ms)||!Number.isFinite(d.loss_pct))return "Inferencia sin detalle confirmado";
    return "RTT "+d.rtt_avg_ms.toFixed(3)+" ms · Pérdida "+d.loss_pct+" % · "+
      methods.map(m=>m+": "+labels[d[m]]).join(" · ")+" · Consenso: "+(labels[d.consensus]||"Desconocido")+" · Verdad de terreno desconocida";
  }
  return row.source==="ADVISORY_S07"?"Resumen histórico":"Observación delimitada";
}

/* Fin de la proyección pura del dashboard. */

// Los recursos compartidos no se atribuyen a una sede sin evidencia.
function observationSite(row){
  const id=row.resource;
  const direct=/^(?:R-|WAN-END-|LACP-)(HQ|S1|S2)(?:-|$)/.exec(id);
  if(direct)return direct[1];
  const vlan=/^VLAN-([123])[123]0$/.exec(id);
  if(vlan)return ["HQ","S1","S2"][Number(vlan[1])-1];
  if(id==="FRONTAL_HQ"||/^HQ_A_S[12]$/.test(id))return "HQ";
  return null;
}
function siteInventory(rows,site){
  const filtered=rows.filter(row=>observationSite(row)===site);
  const router=filtered.find(row=>row.resource==="R-"+site);
  const counts=prefix=>{
    const items=filtered.filter(row=>row.resource.startsWith(prefix));
    const known=items.filter(row=>row.quality==="VALID"&&[0,1].includes(row.details.admin_up));
    return {up:known.filter(row=>row.details.admin_up===1).length,known:known.length,total:items.length};
  };
  const running=router?.quality==="VALID"&&[0,1].includes(router.details.running)?router.details.running:null;
  return {running,wan:counts("WAN-END-"),vlan:counts("VLAN-")};
}
function automaticPage(path){
  return ["/home","/topology","/wan","/lan","/services","/lacp","/sdn","/intelligence"].includes(path);
}

/* Preferencias de actualización global: únicamente valores de presentación. */
const refreshIntervals=Object.freeze([5,10,15,30,60,300]);
const refreshKey="netlab360.refresh.v1";
function parseRefresh(value){
  const match=/^(on|off):(5|10|15|30|60|300)$/.exec(typeof value==="string"?value:"");
  return match?{auto:match[1]==="on",seconds:Number(match[2])}:{auto:true,seconds:5};
}
function refreshValue(auto,seconds){
  return (auto===true?"on":"off")+":"+(refreshIntervals.includes(seconds)?seconds:5);
}
function refreshScheduler(run,clock){
  let timer=null;
  return {
    configure(preference){
      if(timer!==null)clock.clearInterval(timer);
      timer=null;
      if(preference.auto)timer=clock.setInterval(()=>run("auto"),preference.seconds*1000);
    },
    stop(){if(timer!==null)clock.clearInterval(timer);timer=null;}
  };
}
/* Fin de preferencias de actualización. */

/* La consola solo se inicializa en su documento autenticado. */
function initializeConsole() {
  const refresh = document.getElementById("refresh");
  const apiState = document.getElementById("api-state");
  const capabilities = document.getElementById("capabilities");
  const observed = document.getElementById("observed");
  const notice = document.getElementById("notice");

  // Una zona horaria y un formato comunes para toda la presentación.
  const panamaClock = new Intl.DateTimeFormat("en-US", {
    timeZone: "America/Panama", year: "numeric", month: "2-digit",
    day: "2-digit", hour: "2-digit", minute: "2-digit", second: "2-digit",
    hourCycle: "h12"
  });

  function formatPanama(date) {
    const parts = Object.fromEntries(panamaClock.formatToParts(date)
      .filter(part => part.type !== "literal").map(part => [part.type, part.value]));
    return parts.month + "/" + parts.day + "/" + parts.year + " " +
      parts.hour + ":" + parts.minute + ":" + parts.second + " " + parts.dayPeriod;
  }

  const fields = [
    ["authentication_enabled", "Autenticación HTTP"],
    ["persistence_enabled", "Persistencia privada"],
    ["source_readers_enabled", "Lectores operacionales"],
    ["diagnostics_enabled", "Diagnóstico exploratorio"],
    ["advisory_enabled", "Consulta asesora"],
    ["frontend_enabled", "Estructura visual"]
  ];

  async function readPublic(path) {
    const response = await fetch(path, {
      method: "GET", credentials: "omit", cache: "no-store",
      redirect: "error", signal: AbortSignal.timeout(5000)
    });
    if (!response.ok) throw new Error("PUBLIC_METADATA_UNAVAILABLE");
    return response.json();
  }

  function showCapabilities(data) {
    capabilities.replaceChildren();
    for (const [key, label] of fields) {
      const title = document.createElement("dt");
      const value = document.createElement("dd");
      title.textContent = label;
      value.textContent = data[key] === true ? "Habilitada" :
        data[key] === false ? "No habilitada" : "UNKNOWN";
      capabilities.append(title, value);
    }
  }

  async function update() {
    notice.textContent = "Consultando metadatos locales…";
    apiState.textContent = "Consultando";
    apiState.dataset.state = "unknown";
    observed.textContent = "Sin timestamp de respuesta.";
    showCapabilities({});
    try {
      const [health, caps] = await Promise.all([
        readPublic("/healthz"), readPublic("/api/v1/capabilities")
      ]);
      if (health.project !== "NETLAB360" || caps.project !== "NETLAB360" ||
          health.service !== "netlab360-s08-console" ||
          health.mode !== "AUTHENTICATED_READ_ONLY" ||
          caps.mode !== health.mode ||
          health.network_mutations_authorized !== false ||
          caps.network_mutations_authorized !== false) {
        throw new Error("INVALID_PUBLIC_METADATA");
      }
      const stamp = new Date(health.generated_at_utc);
      if (!Number.isFinite(stamp.getTime())) throw new Error("INVALID_TIMESTAMP");
      apiState.textContent = health.healthy === true ? "Disponible" : "UNKNOWN";
      apiState.dataset.state = health.healthy === true ? "ok" : "unknown";
      observed.textContent = "Respuesta del proceso (Panamá): " + formatPanama(stamp);
      showCapabilities(caps);
      notice.textContent = "Metadatos recibidos. La salud global de red sigue siendo UNKNOWN.";
    } catch {
      apiState.textContent = "UNKNOWN";
      apiState.dataset.state = "unknown";
      showCapabilities({});
      notice.textContent = "No se pudieron validar los metadatos. No se conservan valores previos.";
    }
  }

  /* La sesión se recupera con cookie HttpOnly; la autoridad reside en el servidor. */
  const shell = document.getElementById("console-shell");
  const recoveryPanel = document.getElementById("session-recovery");
  const recoveryNotice = document.getElementById("recovery-notice");
  const logout = document.getElementById("logout");
  const authNotice = document.getElementById("auth-notice");
  const accessState = document.getElementById("access-state");
  const identityLabel = document.getElementById("identity-label");
  const idleDialog = document.getElementById("idle-dialog");
  const idleContinue = document.getElementById("idle-continue");
  const idleLogout = document.getElementById("idle-logout");
  const idleNotice = document.getElementById("idle-notice");
  const idleCountdown = document.getElementById("idle-countdown");
  const idleDescription = document.getElementById("idle-description");

  let session = null;
  let busy = false;
  let activityTimer = null;
  let lastActivitySent = -Infinity;

  // Los plazos proceden del servidor. El reloj monotónico evita que un
  // cambio del reloj local prolongue la presentación de una sesión vencida.
  function serverNow() {
    return session.serverNow + (performance.now() - session.receivedAt) / 1000;
  }

  function controls() {
    syncRefreshControls();
    logout.disabled = busy || session === null;
    idleLogout.disabled = busy || session === null;
    idleContinue.disabled = busy || session === null ||
      session.expiresAt >= session.absoluteExpiresAt;
  }

  function clearIdentity(message, redirect = true) {
    clearTimeout(activityTimer);
    activityTimer = null;
    lastActivitySent = -Infinity;
    session = null;
    resetDebug();
    clearDashboard();
    clearHistory();
    clearTopology();
    clearNetwork();
    if (idleDialog.open) idleDialog.close();
    shell.hidden = true;
    recoveryPanel.hidden = false;
    recoveryNotice.textContent = message;
    for (const id of ["session-user","session-role","session-expiry"]) {
      document.getElementById(id).textContent = "";
    }
    identityLabel.textContent = "Sin sesión";
    accessState.textContent = "Sin sesión";
    accessState.dataset.state = "unknown";
    controls();
    if (redirect) location.replace("/login");
  }

  function validIdentity(data) {
    return data && typeof data.username === "string" &&
      /^[a-z][a-z0-9_-]{2,31}$/.test(data.username) &&
      ["VIEWER", "OPERATOR"].includes(data.role) &&
      data.network_mutations_authorized === false;
  }

  async function authRequest(path, options = {}) {
    return fetch(path, {
      credentials: "same-origin", cache: "no-store", redirect: "error",
      signal: AbortSignal.timeout(10000), ...options
    });
  }

  function showIdentity(data) {
    if (!validIdentity(data) || typeof data.csrf_token !== "string" ||
        !/^[A-Za-z0-9_-]{43}$/.test(data.csrf_token) ||
        ![data.warning_at, data.expires_at, data.absolute_expires_at, data.server_now]
          .every(Number.isSafeInteger) ||
        data.server_now >= data.expires_at || data.warning_at > data.expires_at ||
        data.expires_at > data.absolute_expires_at ||
        data.expires_at - data.warning_at > 60 ||
        data.expires_at - data.server_now > 360) {
      throw new Error("INVALID_IDENTITY");
    }
    const first = session === null;
    session = {
      username: data.username, role: data.role, csrf: data.csrf_token,
      expiresAt: data.expires_at, warningAt: data.warning_at,
      absoluteExpiresAt: data.absolute_expires_at,
      serverNow: data.server_now, receivedAt: performance.now()
    };
    document.getElementById("session-user").textContent = session.username;
    document.getElementById("session-role").textContent = session.role;
    document.getElementById("session-expiry").textContent =
      formatPanama(new Date(session.expiresAt * 1000));
    identityLabel.textContent = session.username + " · " + session.role;
    document.querySelector('[data-view="debug"]').hidden = session.role !== "OPERATOR";
    if (location.pathname === "/debug" && session.role !== "OPERATOR") {
      resetDebug();
      location.replace("/home");
      return;
    }
    accessState.textContent = "Autenticado";
    accessState.dataset.state = "ok";
    shell.hidden = false;
    recoveryPanel.hidden = true;
    if (first) {
      restorePresentation();
      refreshCurrent("initial").then(() => restoreContentIfUnchanged());
      if (debugAllowed() && new URLSearchParams(location.search).get("tab") === "docs") openSwagger();
    }
    authNotice.textContent = "Sesión vigente. Acciones de red deshabilitadas.";
    controls();
    tick();
  }

  async function recover() {
    if (busy) return;
    busy = true;
    controls();
    try {
      const response = await authRequest("/api/v1/auth/resume", {
        method: "POST", headers: {"X-Netlab360-Resume": "1"}
      });
      if (response.status === 401) {
        clearIdentity("Inicie sesión para continuar.");
      } else if (response.ok) {
        showIdentity(await response.json());
      } else {
        throw new Error("SESSION_NOT_CONFIRMED");
      }
    } catch {
      clearIdentity("No se pudo comprobar la sesión. Reintente el acceso.", false);
    } finally {
      busy = false;
      controls();
    }
  }

  function tick() {
    syncRefreshControls();
    if (!session) return;
    const remaining = Math.ceil(session.expiresAt - serverNow());
    if (remaining <= 0) {
      clearDashboard();
      clearHistory();
      clearTopology();
      clearNetwork();
      resetDebug();
      // Otra pestaña puede haber renovado la misma sesión. Consultamos una vez
      // sin extender el plazo; una respuesta no válida retira la identidad.
      if (!busy) recover();
      idleCountdown.textContent = "00:00";
      return;
    }
    if (serverNow() >= session.warningAt) {
      clearTimeout(activityTimer);
      activityTimer = null;
      idleCountdown.textContent =
        String(Math.floor(remaining / 60)).padStart(2, "0") + ":" +
        String(remaining % 60).padStart(2, "0");
      idleDescription.textContent = session.expiresAt >= session.absoluteExpiresAt
        ? "Se alcanzará el límite máximo de la sesión. Vuelva a autenticarse al finalizar."
        : "Detectamos inactividad. Confirme que desea continuar antes de que venza la sesión.";
      if (!idleDialog.open) {
        idleNotice.textContent = "";
        idleDialog.showModal();
      }
    } else if (idleDialog.open) {
      idleDialog.close();
    }
    controls();
  }

  async function renew(confirmed) {
    if (busy || session === null) return;
    if (!confirmed && serverNow() >= session.warningAt) return;
    busy = true;
    lastActivitySent = performance.now();
    controls();
    try {
      const response = await authRequest(
        confirmed ? "/api/v1/auth/continue" : "/api/v1/auth/activity", {
          method: "POST", headers: {"X-CSRF-Token": session.csrf}
        });
      if (response.status === 401 || response.status === 403) {
        busy = false;
        await recover();
      } else if (response.ok) {
        showIdentity(await response.json());
      } else {
        throw new Error("ACTIVITY_NOT_CONFIRMED");
      }
    } catch {
      authNotice.textContent = "No se confirmó la renovación. El plazo anterior sigue vigente.";
      idleNotice.textContent = "No se confirmó la renovación. Reintente.";
    } finally {
      busy = false;
      controls();
      tick();
    }
  }

  function recordActivity(event) {
    // No renovamos por carga, foco, sondeos, movimientos accidentales ni
    // eventos sintéticos. Limitamos a una solicitud cada quince segundos.
    if (!event.isTrusted || !session || busy || serverNow() >= session.warningAt ||
        idleDialog.open) return;
    clearTimeout(activityTimer);
    const delay = Math.max(0, 15000 - (performance.now() - lastActivitySent));
    activityTimer = setTimeout(() => {
      activityTimer = null;
      renew(false);
    }, delay);
  }

  for (const event of ["pointerdown", "keydown", "wheel", "touchstart"]) {
    document.addEventListener(event, recordActivity, {passive: true});
  }

  async function closeSession() {
    if (busy || session === null) return;
    busy = true;
    controls();
    try {
      const response = await authRequest("/api/v1/auth/logout", {
        method: "POST", headers: {"X-CSRF-Token": session.csrf}
      });
      if (response.status === 401) {
        clearIdentity("Sesión no vigente. Inicie sesión nuevamente.");
      } else if (response.ok && (await response.json()).logged_out === true) {
        clearIdentity("Sesión cerrada correctamente.");
      } else {
        throw new Error("LOGOUT_NOT_CONFIRMED");
      }
    } catch {
      authNotice.textContent = "No se confirmó el cierre remoto. Reintente.";
      idleNotice.textContent = "No se confirmó el cierre remoto. Reintente.";
    } finally {
      busy = false;
      controls();
    }
  }

  logout.addEventListener("click", closeSession);
  idleLogout.addEventListener("click", closeSession);
  idleContinue.addEventListener("click", () => renew(true));
  idleDialog.addEventListener("cancel", event => event.preventDefault());
  window.addEventListener("focus", () => { if (session) recover(); });
  document.addEventListener("visibilitychange", () => {
    if (!document.hidden && session) recover();
  });

  // Cada ruta se comprueba en el servidor; las vistas no habilitadas no consultan fuentes.
  const links = Array.from(document.querySelectorAll("#navigation a[data-view]"));
  const active = links.find(link => link.getAttribute("href") === location.pathname);
  if (active) {
    active.classList.add("current");
    active.setAttribute("aria-current", "page");
    const home = active.dataset.view === "home";
    document.getElementById("home-view").hidden = !home;
    const debug = active.dataset.view === "debug";
    const history = active.dataset.view === "observability";
    const topology = active.dataset.view === "topology";
    const network = ["/wan","/lan","/services","/lacp","/sdn","/intelligence"].includes(location.pathname);
    document.getElementById("module-view").hidden = home || debug || history || topology || network;
    document.getElementById("network-view").hidden = !network;
    document.getElementById("topology-view").hidden = !topology;
    document.getElementById("history-view").hidden = !history;
    document.getElementById("debug-view").hidden = !debug;
    const label = active.querySelector(".nav-text").textContent;
    document.getElementById("module-title").textContent = label;
    document.title = "NETLAB360 | " + label;
  }

  // El explorador nunca toma URLs del usuario ni exporta respuestas de error.
  const debugSelect = document.getElementById("debug-select");
  const debugNotice = document.getElementById("debug-notice");
  const debugMeta = document.getElementById("debug-meta");
  const debugOutput = document.getElementById("debug-output");
  const debugCatalog = document.getElementById("debug-catalog");
  const exportButtons = ["debug-copy", "debug-json", "debug-csv"].map(id => document.getElementById(id));
  const debugPaths = new Map([
    ["health", "/healthz"], ["capabilities", "/api/v1/capabilities"],
    ["sources", "/api/v1/sources"], ["metrics", "/api/v1/metrics"],
    ["diagnostics", "/api/v1/diagnostics"], ["advisory", "/api/v1/advisory"]
  ]);
  let debugEpoch = 0;
  let debugResult = null;
  let debugReady = false;
  let debugBusy = false;

  function debugAllowed() {
    return location.pathname === "/debug" && session?.role === "OPERATOR" &&
      serverNow() < session.expiresAt;
  }

  function resetDebug() {
    closeSwagger();
    debugEpoch++;
    debugResult = null;
    debugReady = false;
    debugBusy = false;
    debugSelect.replaceChildren();
    debugCatalog.replaceChildren();
    debugSelect.disabled = true;

    exportButtons.forEach(button => button.disabled = true);
    debugOutput.textContent = "Sin resultados.";
    debugMeta.textContent = "Sin consulta.";
    debugNotice.textContent = "Esperando catálogo.";
  }

  // El documento Swagger comparte origen y sesión, no estilos ni estado de las consultas.
  const swaggerHost = document.getElementById("swagger-host");
  const swaggerPanel = document.getElementById("debug-docs");
  const queryPanel = document.getElementById("debug-queries");
  const docsTab = document.getElementById("debug-tab-docs");
  const queriesTab = document.getElementById("debug-tab-queries");

  function closeSwagger() {
    swaggerHost.replaceChildren();
    swaggerPanel.hidden = true;
    queryPanel.hidden = false;
    docsTab.classList.add("secondary");
    queriesTab.classList.remove("secondary");
  }

  function openSwagger() {
    if (!debugAllowed() || serverNow() >= session.warningAt) return;
    queryPanel.hidden = true;
    swaggerPanel.hidden = false;
    docsTab.classList.remove("secondary");
    queriesTab.classList.add("secondary");
    if (swaggerHost.firstElementChild) return;
    const frame = document.createElement("iframe");
    frame.id = "swagger-frame";
    frame.title = "Documentación interactiva de la API";
    frame.addEventListener("load", () => {
      const doc = frame.contentDocument;
      if (!doc || !debugAllowed()) return;
      doc.documentElement.dataset.theme = document.documentElement.dataset.theme;
      for (const event of ["pointerdown", "keydown", "wheel", "touchstart"]) {
        doc.addEventListener(event, recordActivity, {passive: true});
      }
    });
    frame.src = "/docs?embedded=1";
    swaggerHost.append(frame);
  }

  docsTab.addEventListener("click", openSwagger);
  queriesTab.addEventListener("click", closeSwagger);
  window.addEventListener("pagehide", closeSwagger);

  async function debugRead(path, maxBytes = 262144) {
    const response = await fetch(path, {method: "GET", credentials: "same-origin",
      cache: "no-store", redirect: "error", signal: AbortSignal.timeout(15000)});
    if (!response.ok) return {status: response.status, data: null};
    const reader = response.body.getReader();
    const decoder = new TextDecoder("utf-8", {fatal: true});
    let size = 0, raw = "";
    try {
      for (;;) {
        const {done, value} = await reader.read();
        if (done) break;
        size += value.byteLength;
        if (size > maxBytes) throw new Error("LIMIT");
        raw += decoder.decode(value, {stream: true});
      }
      raw += decoder.decode();
      return {status: response.status, data: JSON.parse(raw)};
    } finally {
      await reader.cancel().catch(() => {});
      reader.releaseLock();
    }
  }

  async function loadDebug() {
    if (!debugAllowed()) return;
    resetDebug();
    const epoch = debugEpoch;
    try {
      const {status, data} = await debugRead("/api/v1/debug/catalog");
      if (epoch !== debugEpoch || !debugAllowed()) return;
      if (status !== 200 || data?.network_mutations_authorized !== false ||
          !Array.isArray(data.endpoints) || data.endpoints.length !== debugPaths.size) {
        throw new Error("CATALOG");
      }
      const seen = new Set();
      for (const item of data.endpoints) {
        if (seen.has(item.id) || !debugPaths.has(item.id) || debugPaths.get(item.id) !== item.path ||
            item.method !== "GET" || item.role !== "OPERATOR" ||
            item.probe !== "/api/v1/debug/probe/" + item.id) throw new Error("CATALOG");
        seen.add(item.id);
        const option = document.createElement("option");
        option.value = item.id;
        option.textContent = item.description;
        debugSelect.append(option);
        const row = document.createElement("p");
        const anchor = document.createElement("a");
        anchor.href = item.path;
        anchor.target = "_blank";
        anchor.rel = "noopener noreferrer";
        anchor.textContent = "GET " + item.path;
        row.append(anchor, document.createTextNode(" — " + item.schema + " · " + item.description));
        debugCatalog.append(row);
      }
      debugReady = true;
      debugSelect.disabled = false;

      debugNotice.textContent = "Catálogo disponible. Seleccione una consulta y pulse Ejecutar consulta.";
    } catch {
      if (epoch !== debugEpoch) return;
      resetDebug();
      debugNotice.textContent = "No se pudo validar el catálogo. Recargue la página.";
    }
  }

  async function runDebug() {
    if (!debugReady || !debugAllowed() || debugBusy || !debugPaths.has(debugSelect.value)) return;
    const epoch = debugEpoch;
    const key = debugSelect.value;
    debugBusy = true;
    debugSelect.disabled = true;
    debugResult = null;

    exportButtons.forEach(button => button.disabled = true);
    debugOutput.textContent = "Consultando…";
    debugNotice.textContent = "Consulta en curso.";
    debugMeta.textContent = "Sin resultado confirmado.";
    const start = performance.now();
    try {
      const {status, data} = await debugRead("/api/v1/debug/probe/" + key);
      if (epoch !== debugEpoch || !debugAllowed()) return;
      debugMeta.textContent = "HTTP " + status + " · " + Math.round(performance.now()-start) + " ms";
      if (status !== 200 || data?.network_mutations_authorized !== false ||
          data.endpoint !== debugPaths.get(key) || !Array.isArray(data.records) ||
          data.records.length > 128 || typeof data.summary !== "object" || data.summary === null ||
          !Number.isFinite(Date.parse(data.queried_at_utc))) {
        debugOutput.textContent = "Sin respuesta exportable.";
        debugNotice.textContent = status === 429 ? "Límite de consultas. Reintente después de dos segundos." :
          "No se confirmó la consulta.";
        if (status === 401 || status === 403) recover();
        return;
      }
      debugResult = data;
      debugMeta.textContent += " · " + formatPanama(new Date(data.queried_at_utc));
      debugOutput.textContent = JSON.stringify(data, null, 2);
      debugNotice.textContent = "Respuesta normalizada: " + data.records.length + " observaciones.";
      exportButtons.forEach(button => button.disabled = false);
    } catch {
      if (epoch !== debugEpoch) return;
      debugOutput.textContent = "Sin respuesta exportable.";
      debugNotice.textContent = "Consulta no disponible o respuesta demasiado extensa.";
    } finally {
      if (epoch === debugEpoch) {
        debugBusy = false;
        debugSelect.disabled = !debugReady || !debugAllowed();

      }
    }
  }

  function csvCell(value) {
    let text = String(value ?? "");
    if (/^[\s]*[=+@-]|^[\t\r\n]/.test(text)) text = "'" + text;
    return '"' + text.replace(/"/g, '""') + '"';
  }

  function debugCsv(data) {
    const fields = ["endpoint","queried_at_utc","source","resource","scope","transport",
      "quality","state","observed_at_utc","received_at_utc","age_seconds","max_age_seconds","value"];
    const rows = data.records.length ? data.records :
      Object.entries(data.summary).map(([resource,value]) => ({resource,value}));
    return [fields.map(csvCell).join(","), ...rows.map(row =>
      fields.map(field => csvCell(field === "endpoint" || field === "queried_at_utc" ?
        data[field] : row[field])).join(","))].join("\r\n") + "\r\n";
  }

  function saveDebug(format) {
    if (!debugResult || !debugAllowed()) return;
    const text = format === "csv" ? debugCsv(debugResult) : JSON.stringify(debugResult, null, 2);
    const url = URL.createObjectURL(new Blob([text], {type: format === "csv" ?
      "text/csv;charset=utf-8" : "application/json"}));
    const link = document.createElement("a");
    link.href = url;
    link.download = "netlab360-diagnostico-" + Date.now() + "." + format;
    link.click();
    setTimeout(() => URL.revokeObjectURL(url), 1000);
  }

  debugSelect.addEventListener("change",()=>{
    debugResult=null;
    exportButtons.forEach(button=>button.disabled=true);
    debugOutput.textContent="Sin resultados.";debugMeta.textContent="Sin consulta.";
    debugNotice.textContent="Pulse Ejecutar consulta para consultar el recurso seleccionado.";
  });
  exportButtons[0].addEventListener("click", async () => {
    if (!debugResult || !debugAllowed()) return;
    try {
      await navigator.clipboard.writeText(JSON.stringify(debugResult, null, 2));
      debugNotice.textContent = "JSON copiado.";
    } catch {
      debugNotice.textContent = "No se pudo copiar. Seleccione el texto del resultado.";
    }
  });
  exportButtons[1].addEventListener("click", () => saveDebug("json"));
  exportButtons[2].addEventListener("click", () => saveDebug("csv"));

  // Las consultas son independientes; no se conserva telemetría en almacenamiento web.
  const dashboardStatus = document.getElementById("dashboard-status");
  const dashboardTable = document.getElementById("dashboard-rows");
  const dashboardSite = document.getElementById("dashboard-site");
  const siteOverview = document.getElementById("site-overview");
  const dashboardPaths = {
    sources:"/api/v1/sources",metrics:"/api/v1/metrics",
    diagnostics:"/api/v1/diagnostics",advisory:"/api/v1/advisory"
  };
  const qualityLabels = {VALID:"Vigente",STALE:"Vencida",MISSING:"Ausente",INVALID:"Inválida",
    FUTURE:"Fecha futura",PENDING:"Sin consultar",ERROR:"No disponible",LIMITED:"Ocupada"};
  const stateLabels = {NORMAL:"Normal",DEGRADED:"Degradado",FAULT:"Falla",RECOVERY:"Recuperación",UNKNOWN:"Desconocido"};
  let dashboardBatches = {};
  let dashboardEpoch = 0, dashboardBusy = false, dashboardSignature = "";

  function dashboardAllowed() {
    return location.pathname === "/home" && session !== null && serverNow() < session.expiresAt;
  }

  function renderDashboard(force=false) {
    const rows=dashboardRows(dashboardBatches,performance.now());
    const signature=JSON.stringify([dashboardSite.value,rows.map(r=>[r.resource,r.quality,r.state,r.stamp,r.details])]);
    if(!force && signature===dashboardSignature) return;
    dashboardSignature=signature;
    const summary=dashboardSummary(rows);
    for(const [id,value] of Object.entries(summary)) {
      const node=document.getElementById("dash-"+id);
      node.textContent=value.text;
      node.dataset.state=value.state;
      document.getElementById("dash-"+id+"-detail").textContent=value.detail;
    }
    const selected=dashboardSite.value;
    const sites=selected==="all"?["HQ","S1","S2"]:[selected];
    const cards=document.createDocumentFragment();
    for(const site of sites){
      const inventory=siteInventory(rows,site);
      const card=document.createElement("article"),title=document.createElement("h3"),router=document.createElement("p");
      card.className="site-card";title.textContent=site;
      router.textContent=inventory.running===null?"Router · Sin datos":inventory.running?"Router · Contenedor activo":"Router · Contenedor detenido";
      router.dataset.state=inventory.running===null?"unknown":inventory.running?"ok":"fault";
      card.append(title,router);
      for(const [name,counts] of [["WAN",inventory.wan],["VLAN",inventory.vlan]]){
        const line=document.createElement("p");
        line.textContent=name+" · "+counts.up+"/"+counts.total+" administrativamente activas · "+counts.known+" observadas";
        card.append(line);
      }
      cards.append(card);
    }
    siteOverview.replaceChildren(cards);
    const fragment=document.createDocumentFragment();
    for(const row of rows.filter(row=>selected==="all"||observationSite(row)===selected)) {
      const tr=document.createElement("tr");
      const date=row.stamp?formatPanama(new Date(row.stamp)):"—";
      for(const [i,value] of [row.label,row.name,qualityLabels[row.quality],stateLabels[row.state],
                              dashboardDetail(row),date].entries()) {
        const td=document.createElement("td");
        td.textContent=value;
        if(i===2) td.dataset.state=row.quality==="VALID"?"ok":row.quality==="STALE"?"warn":"unknown";
        if(i===3) td.dataset.state=row.state.toLowerCase();
        tr.append(td);
      }
      fragment.append(tr);
    }
    dashboardTable.replaceChildren(fragment);
  }

  function clearDashboard() {
    dashboardEpoch++;
    dashboardBatches={};
    dashboardBusy=false;

    dashboardSignature="";
    dashboardStatus.textContent="Sin observaciones autenticadas.";
    renderDashboard(true);
  }

  async function updateDashboard() {
    if(!dashboardAllowed()||dashboardBusy||serverNow()>=session.warningAt) return;
    const epoch=dashboardEpoch;
    dashboardBusy=true;

    dashboardStatus.textContent="Consultando fuentes independientes…";
    const requests=Object.entries(dashboardPaths).map(async ([key,path])=>{
      const started=performance.now();
      let batch;
      try {
        const {status,data}=await debugRead(path);
        if(status===401||status===403) {
          if(epoch===dashboardEpoch) {
            clearDashboard();
            recover();
          }
          return;
        }
        batch=status===200?{rows:dashboardBatch(key,data,started)}:{error:status===429?"LIMITED":"ERROR"};
      } catch {
        batch={error:"ERROR"};
      }
      if(epoch!==dashboardEpoch||!dashboardAllowed()) return;
      dashboardBatches[key]=batch;
      renderDashboard(true);
    });
    try {
      await Promise.allSettled([update(),...requests]);
      if(epoch===dashboardEpoch&&dashboardAllowed()) {
        dashboardStatus.textContent="Última consulta: "+formatPanama(new Date(serverNow()*1000))+
          " · La vigencia se calcula por muestra.";
      }
    } finally {
      if(epoch===dashboardEpoch) {
        dashboardBusy=false;

      }
    }
  }

  dashboardSite.addEventListener("change",()=>{if(dashboardAllowed())renderDashboard(true);});
  setInterval(() => { if(dashboardAllowed()) renderDashboard(); },1000);

  // Vistas de dominio: reutilizamos los contratos validados del panel inicial.
  const networkConfig=Object.freeze({
    "/wan":{title:"WAN / OSPF",key:"metrics",prefix:"WAN-END-",scope:"Estado administrativo de extremos WAN. Adyacencias OSPF y conectividad extremo a extremo aún no verificadas en esta vista."},
    "/lan":{title:"LAN / VLAN / ACL",key:"metrics",prefix:"VLAN-",scope:"Estado administrativo de subinterfaces VLAN. No acredita forwarding ni cumplimiento de ACL."},
    "/services":{title:"Servicios HTTP / HA",key:"sources",prefix:"FRONTAL_HQ",scope:"Selección de backend observada desde S2; no acredita disponibilidad desde todas las sedes."},
    "/lacp":{title:"Agregación LACP",key:"sources",prefix:"LACP-",scope:"Miembros de bond observados en switch y cliente. No acredita capacidad agregada ni tráfico."},
    "/sdn":{title:"SDN / OVS / Faucet",key:"sources",prefix:"FAUCET",scope:"Conexión al controlador y flujos observados; no acredita forwarding."},
    "/intelligence":{title:"Diagnóstico inteligente",key:"diagnostics",prefix:"HQ_A_",scope:"Inferencia exploratoria del egreso HQ a S1 y S2. Verdad de terreno desconocida; ninguna predicción confirma un incidente ni autoriza cambios."}
  });
  const networkCurrent=networkConfig[location.pathname];
  const networkBody=document.getElementById("network-rows"),networkStatus=document.getElementById("network-status");
  const networkSite=document.getElementById("network-site");
  document.getElementById("network-filter").hidden=!["/wan","/lan","/lacp"].includes(location.pathname);
  networkSite.addEventListener("change",()=>{networkSignature="";renderNetwork();});
  let networkEpoch=0,networkBusy=false,networkBatches={},networkSignature="";
  if(networkCurrent){
    document.getElementById("network-title").textContent=networkCurrent.title;
    document.getElementById("network-scope").textContent=networkCurrent.scope;
  }
  function networkAllowed(){return !!networkCurrent&&session!==null&&serverNow()<session.expiresAt;}
  function clearNetwork(){
    networkEpoch++;networkBusy=false;networkBatches={};networkSignature="";
    networkBody.replaceChildren();networkStatus.textContent="Sin observaciones autenticadas.";
  }
  function renderNetwork(){
    if(!networkAllowed())return;
    const rows=dashboardRows(networkBatches,performance.now()).filter(r=>
      r.source===({metrics:"PROMETHEUS_S04",sources:"NOC_S05",diagnostics:"IA_S06"}[networkCurrent.key])&&
      r.resource.startsWith(networkCurrent.prefix)&&(networkSite.value==="all"||observationSite(r)===networkSite.value));
    const signature=JSON.stringify(rows.map(r=>[r.resource,r.quality,r.state,r.stamp,r.details]));
    if(signature===networkSignature)return;
    networkSignature=signature;
    const fragment=document.createDocumentFragment();
    for(const row of rows){
      const tr=document.createElement("tr");
      for(const [i,value] of [row.label,row.name,qualityLabels[row.quality],stateLabels[row.state],dashboardDetail(row),row.stamp?formatPanama(new Date(row.stamp)):"—"].entries()){
        const td=document.createElement("td");td.textContent=value;
        if(i===2)td.dataset.state=row.quality==="VALID"?"ok":row.quality==="STALE"?"warn":"unknown";
        if(i===3)td.dataset.state=row.state.toLowerCase();
        tr.append(td);
      }
      fragment.append(tr);
    }
    networkBody.replaceChildren(fragment);
  }
  async function updateNetwork(){
    if(!networkAllowed()||networkBusy||serverNow()>=session.warningAt)return;
    const epoch=networkEpoch,key=networkCurrent.key,started=performance.now();
    networkBusy=true;
    try{
      const {status,data}=await debugRead(dashboardPaths[key]);
      if(epoch!==networkEpoch||!networkAllowed())return;
      if(status===401||status===403){clearNetwork();recover();return;}
      if(status===429){networkStatus.textContent="Consulta compartida ocupada; reintento en la próxima actualización.";return;}
      networkBatches[key]=status===200?{rows:dashboardBatch(key,data,started)}:{error:"ERROR"};
      networkStatus.textContent=status===200?"Última consulta: "+formatPanama(new Date(serverNow()*1000)):"Fuente no disponible.";
    }catch{
      if(epoch!==networkEpoch)return;
      networkBatches[key]={error:"ERROR"};networkStatus.textContent="Fuente no disponible.";
    }finally{
      if(epoch===networkEpoch){networkBusy=false;renderNetwork();}
    }
  }
  setInterval(()=>{if(networkAllowed())renderNetwork();},1000);

  // Una consulta fija alimenta ambas vistas. Los errores transitorios no borran el mapa.
  const topologyMap=document.getElementById("topology-map");
  const topologyStatus=document.getElementById("topology-status");
  const topologyDetails=document.getElementById("topology-details");
  const topologySelection=document.getElementById("topology-selection");
  const topologyWorkspace=document.getElementById("topology-workspace");
  const topologyFull=document.getElementById("topology-fullscreen");
  const topologyMode=new URLSearchParams(location.search).get("view")==="detailed"?"detailed":"summary";
  let topologyEpoch=0,topologyBusy=false,topologyData=null,topologySelected=null;
  let topologyReceived=0,topologyUnavailable=false,topologyInspectorKey="";
  const detailed=topologyMode==="detailed";
  const topologySite=document.getElementById("topology-site");
  let topologyBox=window.NetlabTopology.viewport(topologyMode);
  function applyTopologyBox(){topologyMap.setAttribute("viewBox",topologyBox.join(" "));}
  function resetTopologyBox(){topologySite.value="all";topologyBox=window.NetlabTopology.viewport(topologyMode);applyTopologyBox();}
  topologySite.addEventListener("change",()=>{
    topologyBox=window.NetlabTopology.viewport(topologyMode,topologySite.value);applyTopologyBox();
  });
  for(const [id,zoom,dx,dy] of [["zoom-in",0.8,0,0],["zoom-out",1.25,0,0],["left",1,-0.2,0],["right",1,0.2,0],["up",1,0,-0.2],["down",1,0,0.2]]){
    document.getElementById("topology-"+id).addEventListener("click",()=>{
      topologyBox=window.NetlabTopology.moveViewport(topologyMode,topologyBox,zoom,dx,dy);applyTopologyBox();
    });
  }
  document.getElementById("topology-reset").addEventListener("click",resetTopologyBox);
  document.getElementById("topology-expand").hidden=detailed;
  document.getElementById("topology-return").hidden=!detailed;
  topologyFull.hidden=!detailed;
  document.getElementById("topology-title").textContent=detailed?"Topología detallada":"Topología en vivo";

  function topologyAllowed() {
    return location.pathname==="/topology" && session!==null && serverNow()<session.expiresAt;
  }

  function clearTopology() {
    topologyEpoch++;topologyBusy=false;topologyData=null;topologySelected=null;
    topologyUnavailable=false;topologyInspectorKey="";
    window.NetlabTopology.reset(topologyMap);topologyDetails.replaceChildren();
    resetTopologyBox();
    topologySelection.textContent="Seleccione un equipo o enlace.";
    topologyStatus.textContent="Sin observación topológica vigente.";

    if(document.fullscreenElement===topologyWorkspace)document.exitFullscreen().catch(()=>{});
  }

  function renderTopology() {
    if(!topologyData||!topologyAllowed()) return;
    const model=window.NetlabTopology;
    const elapsed=(performance.now()-topologyReceived)/1000;
    const aged=model.aged(topologyData,elapsed,topologyUnavailable);
    if(!topologyUnavailable&&!model.isFresh(topologyData.graph,elapsed))
      topologyStatus.textContent="Observación caducada. Inventario conservado sin estados vigentes.";
    const display=model.view(aged,topologyMode);
    model.render(topologyMap,aged,topologySelected,id=>{
      topologySelected=topologySelected===id?null:id;
      renderTopology();
    },topologyMode);
    applyTopologyBox();
    const item=[...display.nodes,...display.links].find(x=>x.id===topologySelected);
    const label=item?model.name(item):"Seleccione un equipo o enlace.";
    const rows=item?model.details(item):[];
    const key=JSON.stringify([label,rows]);
    if(key!==topologyInspectorKey){
      topologyInspectorKey=key;topologySelection.textContent=label;
      topologyDetails.replaceChildren();
      for(const [name,value] of rows){
        const dt=document.createElement("dt"),dd=document.createElement("dd");
        dt.textContent=name;dd.textContent=value;topologyDetails.append(dt,dd);
      }
    }
  }

  async function updateTopology() {
    if(!topologyAllowed()||topologyBusy)return;
    if(serverNow()>=session.warningAt)return;
    const epoch=topologyEpoch,started=performance.now();
    topologyBusy=true;
    try {
      const {status,data}=await debugRead("/api/v1/topology");
      if(epoch!==topologyEpoch||!topologyAllowed()) return;
      if(status===401||status===403) {clearTopology();recover();return;}
      if(status===429){
        topologyStatus.textContent="Consulta compartida ocupada. Intente nuevamente o espere la próxima actualización.";
        return;
      }
      if(status!==200||!window.NetlabTopology.valid(data)||data.graph.quality!=="VALID") throw new Error("GRAPH");
      topologyData=data;topologyReceived=started;topologyUnavailable=false;
      renderTopology();
      topologyStatus.textContent="Consulta: "+formatPanama(new Date(data.graph.observed_at_utc))+
        " · "+data.nodes.length+" equipos y "+data.links.length+" enlaces en inventario · "+data.warning_count+" advertencias de origen.";
    } catch {
      if(epoch!==topologyEpoch) return;
      topologyUnavailable=true;
      renderTopology();
      topologyStatus.textContent="Fuente temporalmente no disponible. Conservamos el inventario sin estados vigentes.";
    } finally {
      if(epoch===topologyEpoch) topologyBusy=false;
    }
  }
  setInterval(()=>{
    if(topologyData&&topologyAllowed())renderTopology();
  },1000);
  topologyFull.addEventListener("click",async()=>{
    try {
      if(document.fullscreenElement===topologyWorkspace)await document.exitFullscreen();
      else await topologyWorkspace.requestFullscreen();
    } catch {topologyStatus.textContent="El navegador no permitió cambiar a pantalla completa.";}
  });
  document.addEventListener("fullscreenchange",()=>{
    if(document.fullscreenElement===topologyWorkspace)topologyWorkspace.prepend(refreshControls);
    else document.getElementById("refresh-slot").append(refreshControls);
    topologyFull.textContent=document.fullscreenElement===topologyWorkspace?"Salir de pantalla completa":"Pantalla completa";
  });

  // Las series históricas permanecen en memoria y se descartan al perder la sesión.
  const historyGroup = document.getElementById("history-group");
  const historyWindow = document.getElementById("history-window");
  const historyStatus = document.getElementById("history-status");
  const historyPlot = document.getElementById("history-plot");
  let historyEpoch = 0, historyBusy = false, historyData = null, alertsData=null;
  const alertsSite=document.getElementById("alerts-site"),alertsExport=document.getElementById("alerts-export");
  const alertNames=Object.freeze({
    NETLAB360S04ExporterUnavailable:"Exportador no disponible",NETLAB360S04CollectorUnknown:"Colector sin observación",
    NETLAB360S04WANAdminDown:"WAN administrativamente inactiva",NETLAB360S04VLANAdminDown:"VLAN administrativamente inactiva"
  });
  function clearAlerts(){
    alertsData=null;alertsExport.disabled=true;
    for(const id of ["alerts-current-rows","alerts-history-rows"])document.getElementById(id).replaceChildren();
    for(const id of ["alerts-current-status","alerts-history-status"])document.getElementById(id).textContent="Sin consulta confirmada.";
  }
  function validateAlerts(data){
    if(data?.project!=="NETLAB360"||data.schema_version!==1||data.network_mutations_authorized!==false)throw Error("ALERTS");
    for(const [batch,max,historical] of [[data.current,50,false],[data.history,200,true]]){
      if(!batch||!["OK","INVALID","UNAVAILABLE","NOT_STARTED"].includes(batch.transport)||
         !Array.isArray(batch.records)||batch.records.length>max||(batch.transport!=="OK"&&batch.records.length))throw Error("ALERT_BATCH");
      if(historical&&batch.transport==="OK"&&(!Number.isSafeInteger(batch.total)||batch.total<batch.records.length||
          !Number.isFinite(Date.parse(batch.captured_at_utc))))throw Error("ALERT_HISTORY");
      for(const row of batch.records){
        if(!Object.hasOwn(alertNames,row.alertname)||!["HQ","S1","S2","GLOBAL"].includes(row.site)||
           !["pending","firing",...(historical?["resolved"]:[])].includes(row.state)||
           typeof row.resource!=="string"||row.resource.length>64||
           !Number.isFinite(Date.parse(historical?row.observed_at_utc:row.active_at_utc))||
           (historical&&!["verified_G3_terminal_log","prometheus_active_alerts"].includes(row.source)))throw Error("ALERT_RECORD");
      }
    }
    return data;
  }
  function alertRows(batch){
    return batch.records.filter(row=>alertsSite.value==="all"||row.site===alertsSite.value||row.site==="GLOBAL");
  }
  function renderAlerts(){
    if(!alertsData||!historyAllowed())return;
    for(const [batch,key,historical] of [[alertsData.current,"current",false],[alertsData.history,"history",true]]){
      const rows=alertRows(batch),body=document.getElementById("alerts-"+key+"-rows");
      const fragment=document.createDocumentFragment();
      for(const row of rows){
        const tr=document.createElement("tr");
        const values=[alertNames[row.alertname],row.site,row.resource,{pending:"Pendiente",firing:"Activa",resolved:"Resuelta"}[row.state],
          formatPanama(new Date(historical?row.observed_at_utc:row.active_at_utc))];
        if(historical)values.push(row.source==="verified_G3_terminal_log"?"Registro de ensayo verificado":"Prometheus");
        for(const [i,value] of values.entries()){
          const td=document.createElement("td");td.textContent=value;
          if(i===3)td.dataset.state={pending:"warn",firing:"fault",resolved:"ok"}[row.state];
          tr.append(td);
        }
        fragment.append(tr);
      }
      body.replaceChildren(fragment);
      const status=document.getElementById("alerts-"+key+"-status");
      status.textContent=batch.transport!=="OK"?"Fuente no disponible; no equivale a cero alertas.":
        historical?rows.length+" registros de la copia · "+batch.total+" registrados en origen · Copia: "+formatPanama(new Date(batch.captured_at_utc)):
        rows.length+" alertas observadas en la vista"+(batch.truncated?" · Resultado limitado":"")+". Consulta: "+formatPanama(new Date(batch.queried_at_utc));
    }
    alertsExport.disabled=alertsData.history.transport!=="OK";
  }
  alertsSite.addEventListener("change",renderAlerts);
  alertsExport.addEventListener("click",()=>{
    if(!alertsData||!historyAllowed()||alertsData.history.transport!=="OK")return;
    const lines=[["Alerta","Sede","Recurso","Estado","Observado UTC","Origen"],...alertRows(alertsData.history).map(row=>
      [alertNames[row.alertname],row.site,row.resource,row.state,row.observed_at_utc,row.source])];
    const url=URL.createObjectURL(new Blob([lines.map(row=>row.map(csvCell).join(",")).join("\r\n")+"\r\n"],{type:"text/csv;charset=utf-8"}));
    const link=document.createElement("a");link.href=url;link.download="alertas-historicas.csv";link.click();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
  });
  async function updateAlerts(){
    if(!historyAllowed()||historyBusy||serverNow()>=session.warningAt)return;
    const epoch=historyEpoch;historyBusy=true;clearAlerts();
    historyStatus.textContent="Consultando alertas y transiciones…";
    try{
      const {status,data}=await debugRead("/api/v1/alerts");
      if(epoch!==historyEpoch||!historyAllowed())return;
      if(status===401||status===403){clearHistory();recover();return;}
      if(status!==200)throw Error("ALERTS_HTTP");
      alertsData=validateAlerts(data);renderAlerts();
      historyStatus.textContent="Consulta de alertas completada.";
    }catch{
      if(epoch===historyEpoch){clearAlerts();historyStatus.textContent="No se pudo confirmar la consulta de alertas.";}
    }finally{if(epoch===historyEpoch)historyBusy=false;}
  }
  let plotlyLoading = null, historyDraw = Promise.resolve();

  function historyAllowed() {
    return location.pathname === "/observability" && session !== null &&
      serverNow() < session.expiresAt;
  }

  function clearHistory() {
    historyEpoch++;
    historyData = null;
    clearAlerts();
    historyBusy = false;

    for (const id of ["history-valid","history-null","history-series","history-scope"])
      document.getElementById(id).textContent = "—";
    historyStatus.textContent = "Sin consulta histórica vigente.";
    historyPlot.hidden = true;
    // Serializamos el borrado después de cualquier dibujo pendiente.
    historyDraw = historyDraw.catch(()=>{}).then(()=>{
      if (window.Plotly) window.Plotly.purge(historyPlot);
      historyPlot.replaceChildren();
    });
  }

  function loadPlotly() {
    if (window.Plotly) return Promise.resolve(window.Plotly);
    if (!plotlyLoading) {
      plotlyLoading = new Promise((resolve,reject)=>{
        const script=document.createElement("script");
        script.src="/ui/static/plotly.js";
        script.onload=()=>window.Plotly?.newPlot?resolve(window.Plotly):reject(new Error("PLOTLY"));
        script.onerror=()=>reject(new Error("PLOTLY"));
        document.head.append(script);
      }).catch(error=>{plotlyLoading=null;throw error;});
    }
    return plotlyLoading;
  }

  function drawHistory(data,epoch) {
    historyDraw=historyDraw.catch(()=>{}).then(async ()=>{
      const plotly=await loadPlotly();
      if(epoch!==historyEpoch||!historyAllowed()||historyData!==data) return;
      const style=getComputedStyle(document.documentElement);
      const color=name=>style.getPropertyValue("--"+name).trim();
      const figure=window.NetlabHistory.figure(data,formatPanama,{
        theme:document.documentElement.dataset.theme,
        surface:color("surface"),text:color("text"),line:color("line"),
        ok:color("ok"),fault:color("fault"),unknown:color("unknown")
      });
      historyPlot.hidden=false;
      await plotly.react(historyPlot,figure.traces,figure.layout,{
        responsive:true,displaylogo:false,scrollZoom:true,
        modeBarButtonsToRemove:["lasso2d","select2d","toImage"]
      });
      if(epoch!==historyEpoch||!historyAllowed()) historyPlot.hidden=true;
    });
    return historyDraw;
  }

  async function updateHistory() {
    if(!historyAllowed()||historyBusy||serverNow()>=session.warningAt) return;
    const group=historyGroup.value, span=historyWindow.value;
    if(group==="alerts")return updateAlerts();
    if(!window.NetlabHistory.allowed(group,span)) return;
    const epoch=historyEpoch;
    historyBusy=true;

    historyStatus.textContent="Consultando muestras históricas…";
    try {
      const {status,data}=await debugRead("/api/v1/history/"+group+"/"+span,1048576);
      if(epoch!==historyEpoch||!historyAllowed()) return;
      if(status===401||status===403) {clearHistory();recover();return;}
      if(status===429) throw new Error("LIMITED");
      if(status!==200) throw new Error("UNAVAILABLE");
      const result=window.NetlabHistory.validate(data,group,span);
      if(result.transport!=="OK") throw new Error("UNAVAILABLE");
      historyData=result;
      const counts=window.NetlabHistory.counts(result);
      document.getElementById("history-valid").textContent=String(counts.valid);
      document.getElementById("history-null").textContent=String(counts.missing);
      document.getElementById("history-series").textContent=counts.series+" / "+result.series.length;
      document.getElementById("history-scope").textContent=window.NetlabHistory.description(group);
      if(counts.valid) await drawHistory(result,epoch);
      else {historyPlot.hidden=true;if(window.Plotly)window.Plotly.purge(historyPlot);}
      if(epoch!==historyEpoch||!historyAllowed()) return;
      historyStatus.textContent=(counts.valid?"Intervalo consultado: ":"Sin muestras válidas: ")+
        formatPanama(new Date(result.start_epoch*1000))+" — "+formatPanama(new Date(result.end_epoch*1000));
    } catch(error) {
      if(epoch!==historyEpoch) return;
      if(error.message==="LIMITED"&&historyData){
        historyStatus.textContent="Consulta ocupada; se conserva el intervalo anterior: "+formatPanama(new Date(historyData.start_epoch*1000))+" — "+formatPanama(new Date(historyData.end_epoch*1000));
        return;
      }
      clearHistory();
      historyStatus.textContent=error.message==="LIMITED"?
        "Consulta ocupada. Intente nuevamente después de dos segundos.":
        "No fue posible obtener o representar el histórico.";
    } finally {
      if(epoch===historyEpoch) historyBusy=false;
    }
  }

  function historySelectionChanged(){
    clearHistory();
    const alerts=historyGroup.value==="alerts";
    document.getElementById("history-chart-content").hidden=alerts;
    document.getElementById("alerts-content").hidden=!alerts;
    historyWindow.disabled=alerts;
    historyStatus.textContent=alerts?"Pulse Consultar histórico para obtener alertas y transiciones.":"Pulse Consultar histórico para obtener el intervalo seleccionado.";
  }
  historyGroup.addEventListener("change",historySelectionChanged);
  historyWindow.addEventListener("change",historySelectionChanged);
  new MutationObserver(()=>{
    if(historyData&&historyAllowed()) drawHistory(historyData,historyEpoch).catch(()=>{
      clearHistory();historyStatus.textContent="No fue posible actualizar la apariencia del gráfico.";
    });
  }).observe(document.documentElement,{attributes:true,attributeFilter:["data-theme"]});

  // Guardamos exclusivamente preferencias visuales por pestaña, nunca identidad ni CSRF.
  const menuToggle = document.getElementById("menu-toggle");
  const navigation = document.getElementById("navigation");
  const contentPanel = document.getElementById("main");
  const presentationKey = "netlab360.presentation.v1";
  const allowedPages = links.map(link => link.getAttribute("href"));

  function scrollValue(value) {
    return Number.isFinite(value) ? Math.max(0, Math.min(1000000, Math.round(value))) : 0;
  }

  function readPresentation() {
    const clean = {collapsed: false, menu: {expanded: 0, collapsed: 0}, pages: {}};
    try {
      const saved = JSON.parse(sessionStorage.getItem(presentationKey) || "{}");
      if (!saved || typeof saved !== "object") return clean;
      clean.collapsed = saved.collapsed === true;
      for (const mode of ["expanded", "collapsed"]) {
        clean.menu[mode] = scrollValue(saved.menu?.[mode]);
      }
      for (const path of allowedPages) {
        clean.pages[path] = scrollValue(saved.pages?.[path]);
      }
    } catch {
      // La navegación sigue siendo funcional si el navegador bloquea almacenamiento.
    }
    return clean;
  }

  const presentation = readPresentation();
  let presentationReady = false;
  let contentRestore = null;

  function menuMode() {
    return presentation.collapsed ? "collapsed" : "expanded";
  }

  function contentScroller() {
    return matchMedia("(min-width: 701px)").matches ? contentPanel : document.scrollingElement;
  }

  function savePresentation() {
    if (!presentationReady || shell.hidden) return;
    if (navigation.clientHeight > 0) presentation.menu[menuMode()] = scrollValue(navigation.scrollTop);
    if (allowedPages.includes(location.pathname)) {
      presentation.pages[location.pathname] = scrollValue(contentScroller().scrollTop);
    }
    try {
      sessionStorage.setItem(presentationKey, JSON.stringify(presentation));
    } catch {
      // No dependemos del almacenamiento para autenticar ni consultar.
    }
  }

  function setMenuState() {
    shell.classList.toggle("menu-collapsed", presentation.collapsed);
    menuToggle.setAttribute("aria-expanded", String(!presentation.collapsed));
    menuToggle.setAttribute("aria-label", presentation.collapsed ? "Expandir menú" : "Contraer menú");
  }

  function restorePresentation() {
    if (presentationReady) return;
    setMenuState();
    navigation.scrollTop = presentation.menu[menuMode()];
    const desired = presentation.pages[location.pathname] || 0;
    const scroller = contentScroller();
    scroller.scrollTop = desired;
    contentRestore = {desired, initial: scroller.scrollTop};
    presentationReady = true;
  }

  // El inicio puede crecer al recibir sus metadatos. Restauramos el punto
  // guardado tras cargar solo si el usuario aún no desplazó el contenido.
  function restoreContentIfUnchanged() {
    if (!contentRestore || shell.hidden) return;
    const scroller = contentScroller();
    if (scroller.scrollTop === contentRestore.initial) {
      scroller.scrollTop = contentRestore.desired;
    }
    contentRestore = null;
  }

  menuToggle.addEventListener("click", () => {
    savePresentation();
    presentation.collapsed = !presentation.collapsed;
    setMenuState();
    navigation.scrollTop = presentation.menu[menuMode()];
    savePresentation();
  });

  navigation.addEventListener("scroll", savePresentation, {passive: true});
  contentPanel.addEventListener("scroll", savePresentation, {passive: true});
  window.addEventListener("scroll", savePresentation, {passive: true});
  window.addEventListener("pagehide", savePresentation);
  document.querySelectorAll("#navigation a, .sidebar .brand").forEach(link => {
    link.addEventListener("click", savePresentation);
  });

  // Comprobar la sesión también al volver desde la caché de navegación.
  window.addEventListener("pageshow", event => {
    if (event.persisted) recover();
  });
  // Un solo temporizador de adquisición; la caducidad visual continúa sin consultas.
  const refreshControls=document.getElementById("refresh-controls");
  const refreshAuto=document.getElementById("refresh-auto");
  const refreshInterval=document.getElementById("refresh-interval");
  let refreshPreference=parseRefresh(null),refreshBusy=false;
  try{refreshPreference=parseRefresh(localStorage.getItem(refreshKey));}catch{}
  const scheduler=refreshScheduler(refreshCurrent,window);
  const manualHistory=location.pathname==="/observability",manualDebug=location.pathname==="/debug";
  const autoPage=automaticPage(location.pathname);
  const slot=document.getElementById("refresh-slot");
  if(manualHistory)document.getElementById("history-refresh-slot").append(refreshControls);
  if(manualDebug)document.getElementById("debug-refresh-slot").append(refreshControls);
  slot.hidden=!autoPage;
  document.getElementById("refresh-auto-label").hidden=!autoPage;
  document.getElementById("refresh-interval-label").hidden=!autoPage;
  const manualLabel=manualHistory?"Consultar histórico":manualDebug?"Ejecutar consulta":"Actualizar";
  function refreshAvailable(){
    return dashboardAllowed()||topologyAllowed()||networkAllowed()||historyAllowed()||debugAllowed();
  }
  function syncRefreshControls(){
    refresh.disabled=refreshBusy||!refreshAvailable()||!session||serverNow()>=session.warningAt;
    refresh.textContent=refreshBusy?"Consultando…":manualLabel;
  }
  async function refreshCurrent(reason="manual"){
    if(refreshBusy||!refreshAvailable()||document.hidden||serverNow()>=session.warningAt)return;
    if(reason==="auto"&&(!autoPage||!refreshPreference.auto))return;
    if(reason==="initial"&&manualHistory)return;
    refreshBusy=true;syncRefreshControls();
    try{
      if(dashboardAllowed())await updateDashboard();
      else if(topologyAllowed())await updateTopology();
      else if(networkAllowed())await updateNetwork();
      else if(historyAllowed())await updateHistory();
      else if(debugAllowed()){
        if(!debugReady)await loadDebug();
        else if(reason!=="initial")await runDebug();
      }
    }finally{refreshBusy=false;syncRefreshControls();}
  }
  function applyRefreshPreference(){
    refreshAuto.checked=refreshPreference.auto;
    refreshInterval.value=String(refreshPreference.seconds);
    refreshInterval.disabled=!refreshPreference.auto;
    scheduler.configure({...refreshPreference,auto:autoPage&&refreshPreference.auto});
    syncRefreshControls();
  }
  function saveRefreshPreference(){
    const value=refreshValue(refreshAuto.checked,Number(refreshInterval.value));
    refreshPreference=parseRefresh(value);
    try{localStorage.setItem(refreshKey,value);}catch{}
    applyRefreshPreference();
  }
  refresh.addEventListener("click",()=>refreshCurrent("manual"));
  refreshAuto.addEventListener("change",saveRefreshPreference);
  refreshInterval.addEventListener("change",saveRefreshPreference);
  window.addEventListener("storage",event=>{
    if(event.key===refreshKey||event.key===null){
      refreshPreference=parseRefresh(event.key===null?null:event.newValue);applyRefreshPreference();
    }
  });
  document.addEventListener("visibilitychange",()=>{
    if(!document.hidden&&autoPage&&refreshPreference.auto)refreshCurrent("auto");
  });
  applyRefreshPreference();
  setInterval(tick, 1000);
  recover();
}
