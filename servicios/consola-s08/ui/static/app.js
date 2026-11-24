/* Consultamos exclusivamente metadatos públicos; no almacenamos sesiones ni secretos. */
"use strict";

const refresh = document.getElementById("refresh");
const apiState = document.getElementById("api-state");
const capabilities = document.getElementById("capabilities");
const observed = document.getElementById("observed");
const notice = document.getElementById("notice");

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
    observed.textContent = "Respuesta del proceso (UTC): " + stamp.toISOString();
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
