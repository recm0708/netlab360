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

/* La autoridad reside en FastAPI, no en el estado visual del navegador. */
const form = document.getElementById("login-form");
const loginFields = document.getElementById("login-fields");
const username = document.getElementById("username");
const password = document.getElementById("password");
const sessionPanel = document.getElementById("session-panel");
const logout = document.getElementById("logout");
const authNotice = document.getElementById("auth-notice");
const accessState = document.getElementById("access-state");
const identityLabel = document.getElementById("identity-label");

let session = null;
let busy = false;
let expiryTimer = null;

function controls() {
  loginFields.disabled = busy || session !== null;
  logout.disabled = busy || session === null;
}

function clearIdentity(message) {
  clearTimeout(expiryTimer);
  session = null;
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
  // Rutas constantes del mismo origen. La cookie HttpOnly la gestiona el navegador.
  return fetch(path, {
    credentials: "same-origin", cache: "no-store", redirect: "error",
    signal: AbortSignal.timeout(10000), ...options
  });
}

function showIdentity(data) {
  const remaining = data.expires_at * 1000 - Date.now();
  if (!validIdentity(data) || typeof data.csrf_token !== "string" ||
      !/^[A-Za-z0-9_-]{43}$/.test(data.csrf_token) ||
      !Number.isSafeInteger(data.expires_at) || remaining <= 0) {
    throw new Error("INVALID_IDENTITY");
  }
  session = {username: data.username, role: data.role, csrf: data.csrf_token,
             expiresAt: data.expires_at};
  document.getElementById("session-user").textContent = session.username;
  document.getElementById("session-role").textContent = session.role;
  document.getElementById("session-expiry").textContent =
    formatPanama(new Date(session.expiresAt * 1000));
  identityLabel.textContent = session.username + " · " + session.role;
  accessState.textContent = "Autenticado";
  accessState.dataset.state = "ok";
  form.hidden = true;
  sessionPanel.hidden = false;
  authNotice.textContent = "Sesión iniciada. Acciones de red deshabilitadas.";
  expiryTimer = setTimeout(() => clearIdentity("Sesión expirada. Inicie sesión nuevamente."),
    Math.min(remaining, 1800000));
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
      logout.focus();
    }
  } catch {
    clearIdentity("No se pudo confirmar el inicio de sesión. Vuelva a intentarlo.");
  } finally {
    password.value = "";
    busy = false;
    controls();
    if (session !== null) logout.focus();
  }
});

logout.addEventListener("click", async () => {
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
    authNotice.textContent = "No se confirmó el cierre remoto. Reintente; la sesión tiene expiración absoluta.";
  } finally {
    busy = false;
    controls();
    if (session === null) username.focus();
  }
});

// Una sesión reemplazada o deshabilitada se detecta al regresar a la ventana.
window.addEventListener("focus", async () => {
  if (busy || session === null) return;
  busy = true;
  controls();
  try {
    const response = await authRequest("/api/v1/auth/me");
    if (response.status === 401) {
      clearIdentity("Sesión no vigente. Inicie sesión nuevamente.");
    } else {
      if (!response.ok) throw new Error("IDENTITY_UNAVAILABLE");
      const data = await response.json();
      if (!validIdentity(data) || !session ||
          data.username !== session.username || data.role !== session.role) {
        clearIdentity("Identidad no confirmada. Inicie sesión nuevamente.");
      } else {
        accessState.textContent = "Autenticado";
        accessState.dataset.state = "ok";
        authNotice.textContent = "Sesión verificada. Acciones de red deshabilitadas.";
      }
    }
  } catch {
    authNotice.textContent = "No se pudo verificar la sesión. No se muestran datos privados.";
    accessState.textContent = "UNKNOWN";
    accessState.dataset.state = "unknown";
  } finally {
    busy = false;
    controls();
  }
});

clearIdentity("Inicie sesión. Al recargar, deberá autenticarse nuevamente.");
