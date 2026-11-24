/* Inicio de sesión independiente; no conservamos credenciales ni tokens en el cliente. */
"use strict";
const form = document.getElementById("login-form");
const fields = document.getElementById("login-fields");
const username = document.getElementById("username");
const password = document.getElementById("password");
const notice = document.getElementById("auth-notice");

form.addEventListener("submit", async event => {
  event.preventDefault();
  if (fields.disabled) return;
  fields.disabled = true;
  notice.textContent = "Verificando credenciales…";
  try {
    const pending = fetch("/api/v1/auth/login", {
      method: "POST", credentials: "same-origin", cache: "no-store",
      redirect: "error", signal: AbortSignal.timeout(10000),
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username: username.value, password: password.value})
    });
    password.value = "";
    const response = await pending;
    if (response.status === 401) {
      notice.textContent = "Credenciales incorrectas o cuenta no disponible.";
    } else if (response.status === 429) {
      notice.textContent = "Límite de intentos alcanzado. Intente nuevamente en un minuto.";
    } else if (response.ok) {
      // La consola vuelve a verificar la cookie y recupera el comprobante CSRF.
      location.replace("/home");
      return;
    } else {
      throw new Error("LOGIN_FAILED");
    }
  } catch {
    notice.textContent = "No se pudo confirmar el acceso. Vuelva a intentarlo.";
  } finally {
    password.value = "";
    fields.disabled = false;
  }
});
fields.disabled = false;
