/* Metadatos públicos e identidad local; el comprobante CSRF solo vive en memoria. */
"use strict";

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
update();

/* La sesión se recupera con cookie HttpOnly; la autoridad reside en el servidor. */
const form = document.getElementById("login-form");
const loginFields = document.getElementById("login-fields");
const username = document.getElementById("username");
const password = document.getElementById("password");
const sessionPanel = document.getElementById("session-panel");
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
  loginFields.disabled = busy || session !== null;
  logout.disabled = busy || session === null;
  idleLogout.disabled = busy || session === null;
  idleContinue.disabled = busy || session === null ||
    session.expiresAt >= session.absoluteExpiresAt;
}

function clearIdentity(message) {
  clearTimeout(activityTimer);
  activityTimer = null;
  lastActivitySent = -Infinity;
  session = null;
  if (idleDialog.open) idleDialog.close();
  form.hidden = false;
  sessionPanel.hidden = true;
  password.value = "";
  document.getElementById("session-user").textContent = "";
  document.getElementById("session-role").textContent = "";
  document.getElementById("session-expiry").textContent = "";
  identityLabel.textContent = "Sin sesión";
  accessState.textContent = "Sin sesión";
  accessState.dataset.state = "unknown";
  authNotice.textContent = message;
  controls();
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
  accessState.textContent = "Autenticado";
  accessState.dataset.state = "ok";
  form.hidden = true;
  sessionPanel.hidden = false;
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
    clearIdentity("No se pudo comprobar la sesión. Actualice la página o vuelva a autenticarse.");
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

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (busy || session !== null) return;
  busy = true;
  controls();
  authNotice.textContent = "Verificando credenciales…";
  try {
    const request = authRequest("/api/v1/auth/login", {
      method: "POST", headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username: username.value, password: password.value})
    });
    password.value = "";
    const response = await request;
    if (response.status === 401) {
      authNotice.textContent = "Credenciales incorrectas o cuenta no disponible.";
    } else if (response.status === 429) {
      authNotice.textContent = "Límite de intentos alcanzado. Intente nuevamente en un minuto.";
    } else if (!response.ok) {
      throw new Error("LOGIN_FAILED");
    } else {
      showIdentity(await response.json());
    }
  } catch {
    clearIdentity("No se pudo confirmar el inicio de sesión. Vuelva a intentarlo.");
  } finally {
    password.value = "";
    busy = false;
    controls();
    if (session !== null && !idleDialog.open) logout.focus();
  }
});

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
    if (session === null) username.focus();
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

setInterval(tick, 1000);
recover();
