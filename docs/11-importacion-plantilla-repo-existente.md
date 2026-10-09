# Importar NETLAB360 v0.2 en el repositorio ya inicializado

**Importante:** El repositorio `recm0708/netlab360` ya tiene commits, un README, un registro de continuidad, 37 issues y un workflow de gestión. **No** ejecutar `git init`, `git remote add origin` ni el «primer push» de `docs/08-inicio-github.md` en la plantilla antigua. En su lugar, clonar el repositorio existente.

## Paso A — Preparar Ubuntu Desktop

Cuando Ubuntu Desktop esté instalado y actualizado:

```bash
sudo apt update
sudo apt install -y git gh unzip rsync ca-certificates jq
gh auth login
gh auth setup-git
gh auth status
```

Elegir GitHub.com, HTTPS y autenticación por navegador; no pegar tokens en el chat.

## Paso B — Descargar o copiar el ZIP

Guardar `NETLAB360_Planificacion_v0.2.zip` en `~/Descargas/` o `~/Downloads/`. En un Ubuntu nuevo puede volver a descargarse desde la conversación o transferirse mediante carpeta compartida VMware.

## Paso C — Clonar e incorporar plantilla

```bash
mkdir -p ~/proyectos
cd ~/proyectos
git clone https://github.com/recm0708/netlab360.git
cd ~/proyectos/netlab360

ZIP="$HOME/Descargas/NETLAB360_Planificacion_v0.2.zip"
[[ -f "$ZIP" ]] || ZIP="$HOME/Downloads/NETLAB360_Planificacion_v0.2.zip"
test -f "$ZIP" || { echo "Falta el ZIP"; exit 1; }

TEMP="$(mktemp -d)"
unzip -q "$ZIP" -d "$TEMP"

rsync -a --exclude='.git/' \
  "$TEMP/NETLAB360_Planificacion_Inicial/" \
  "$HOME/proyectos/netlab360/"

git status --short
```

La carpeta `NETLAB360_Planificacion_Inicial` NO debe quedar anidada en el repositorio.

## Paso D — Revisar y publicar

Comprobar `.gitignore` y los archivos antes de hacer commit.

```bash
cd ~/proyectos/netlab360
git status
git add -A
git diff --cached --stat
git commit -m "docs: importar planificación integral v0.2"
git push origin main
```

Si Git solicita identidad, configurar nombre y correo con `git config --local user.name` y `git config --local user.email`, respectivamente.

## Paso E — Verificar

```bash
gh repo view recm0708/netlab360 --json nameWithOwner,isPrivate --jq '{repo: .nameWithOwner,privado: .isPrivate}'
gh issue list -R recm0708/netlab360 --state all --limit 100
gh run list -R recm0708/netlab360 --limit 5
```

Ya existen las 37 issues: no volver a crearlas manualmente. GitHub Actions `bootstrap-github.yml` gestiona automáticamente etiquetas, milestones y su asociación al sincronizarse el directorio `backlog/`.

**Nota:** Los cuerpos de las issues fueron inicializados con un resumen de aceptación; la plantilla original de `backlog/` tiene un detalle mayor. Actualizar los cuerpos solo tras comprobar que no se perderán casillas marcadas o comentarios.
