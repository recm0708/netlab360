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
    if (refresh.disabled) return;
    refresh.disabled = true;
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
    } finally {
      refresh.disabled = false;
    }
  }

  refresh.addEventListener("click", update);

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
      if (location.pathname === "/home") {
        update().then(() => restoreContentIfUnchanged());
      } else if (location.pathname === "/debug") {
        loadDebug().then(() => restoreContentIfUnchanged());
      }
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
    if (!session) return;
    const remaining = Math.ceil(session.expiresAt - serverNow());
    if (remaining <= 0) {
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
    document.getElementById("module-view").hidden = home || debug;
    document.getElementById("debug-view").hidden = !debug;
    const label = active.querySelector(".nav-text").textContent;
    document.getElementById("module-title").textContent = label;
    document.title = "NETLAB360 | " + label;
  }

  // El explorador nunca toma URLs del usuario ni exporta respuestas de error.
  const debugSelect = document.getElementById("debug-select");
  const debugRun = document.getElementById("debug-run");
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
    debugEpoch++;
    debugResult = null;
    debugReady = false;
    debugBusy = false;
    debugSelect.replaceChildren();
    debugCatalog.replaceChildren();
    debugSelect.disabled = true;
    debugRun.disabled = true;
    exportButtons.forEach(button => button.disabled = true);
    debugOutput.textContent = "Sin resultados.";
    debugMeta.textContent = "Sin consulta.";
    debugNotice.textContent = "Esperando catálogo.";
  }

  async function debugRead(path) {
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
        if (size > 262144) throw new Error("LIMIT");
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
      debugRun.disabled = false;
      debugNotice.textContent = "Catálogo disponible. Seleccione una consulta.";
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
    debugResult = null;
    debugRun.disabled = true;
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
        debugRun.disabled = !debugAllowed() || !debugReady;
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

  debugRun.addEventListener("click", runDebug);
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
  setInterval(tick, 1000);
  recover();
}
