# Procedimiento: GitHub CLI desde Ubuntu por SSH, sin navegador gráfico

**Fecha:** 2026-10-09. **Issue:** #40. **Estado:** workaround documentado; autorización todavía pendiente de validación.

## Situación

- Host: `netlab360-lab` (Ubuntu 26.04.1), cuenta `rc-aa-ec`.
- Acceso desde Windows: `ssh netlab360` por clave Ed25519.
- GitHub CLI instalado mediante APT: `gh version 2.46.0`.
- `gh auth login -h github.com -p https -w` mostró código de dispositivo, pero al presionar Enter intentó lanzar navegador en Ubuntu por SSH y terminó con `Error: no DISPLAY environment variable specified`. Mensajes del empaquetado Snap aparecieron como efecto del lanzamiento del navegador, no prueban que GitHub o SSH estén fallando.

## Procedimiento recomendado

En la **sesión de Ubuntu abierta desde PowerShell**:

```bash
GH_BROWSER=/bin/true gh auth login -h github.com -p https -w
```

- Elegir **Yes** para autenticar operaciones Git por HTTPS.
- Copiar **manualmente** el código temporal generado (no guardarlo).
- Abrir **en el navegador de Windows**: `https://github.com/login/device`.
- Introducir el código nuevo, comprobar la cuenta y aprobar la conexión.
- Presionar Enter en SSH cuando la herramienta lo solicite; `GH_BROWSER=/bin/true` evita intentar iniciar una ventana gráfica remota.
- Si caduca el código, repetir la orden y obtener otro.

Comprobar sin imprimir tokens:

```bash
gh auth setup-git
gh auth status
gh api user --jq .login
gh repo view recm0708/netlab360 --json nameWithOwner,isPrivate
```

Clonar **solo después** de autenticación comprobada:

```bash
mkdir -p ~/proyectos
cd ~/proyectos
gh repo clone recm0708/netlab360
cd netlab360
git status --short --branch
git remote -v
```

Si la carpeta ya existe, no clonar encima; verificar la copia local primero.

## Estado y seguridad

- [x] Credencial SSH desde Windows comprobada.
- [x] Dirección fija `192.168.47.40` comprobada tras reinicio.
- [x] Se identificó el bloqueo por navegador headless.
- [ ] OAuth de GitHub CLI validado.
- [ ] Clonado del repositorio privado confirmado.
- [ ] Importación revisada de plantilla v0.2, sin sobrescribir documentos actuales.

No agregar en el repositorio contraseñas, tokens, códigos de dispositivo, claves privadas, `~/.config/gh/hosts.yml` ni archivos de autenticación.

## Documentación técnica

- GitHub CLI: https://cli.github.com/manual/gh_auth_login
- Variables: https://cli.github.com/manual/gh_help_environment
- Caso de SSH headless: https://github.com/cli/cli/issues/13445
