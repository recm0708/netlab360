# S03_09 — Evidencia GitOps: pull request y GitHub Actions

**Fecha de comprobación:** 25 de octubre de 2026. **Origen:** GitHub, consultado mediante la conexión del repositorio privado `recm0708/netlab360`. **Tipo:** evidencia documental verificable **con enlaces a ejecuciones auténticas**, no una captura PNG fabricada.

## Pull request comprobado

- **[PR #49: fix(ci): rutas portables para pruebas offline WAN/LAN/HTTP](https://github.com/recm0708/netlab360/pull/49)**.
- **Estado verificado:** `closed` y `merged=true`; fusionado el **25/10/2026 20:58:23 UTC**.
- **Commit de merge (squash):** `6e89b1c245e48512596bf6d1b46c3ee99293ecfb`.
- **Cambios inspeccionados:** sustitución de la raíz del repositorio derivada de `Path.home()` por `Path(__file__).resolve().parents[2]` en tres scripts ya existentes de la fase 2, y creación de `tests/test_s02_portable_paths.py`. **No se cambiaron** IPAM, interfaces, Docker, estados OpenTofu, scripts `up/down` ni la configuración administrativa.
- **Causa anterior:** el workflow general intentaba buscar archivos bajo `/home/runner/proyectos/netlab360`, aunque GitHub Actions clonaba el repo en `/home/runner/work/netlab360/netlab360`. En [ejecución anterior fallida 40229604811](https://github.com/recm0708/netlab360/actions/runs/40229604811) había tres errores de ruta en pruebas S02. Se conserva el fallo histórico como diagnóstico real, no como fallo de red empresarial.

## Ejecuciones de CI verificadas

| Alcance | GitHub Actions | Evento | Resultado comprobado |
|---|---|---|---|
| PR #49: regresión general | [40233116672](https://github.com/recm0708/netlab360/actions/runs/40233116672) | `pull_request` | **completed / success** |
| Main después del merge: regresión general | [40233253796](https://github.com/recm0708/netlab360/actions/runs/40233253796) | `push` | **completed / success** |
| Main: regresión general posterior | [40233355346](https://github.com/recm0708/netlab360/actions/runs/40233355346) | `push` | **completed / success** |
| Main: CI declarativa OpenTofu fase 3 | [40233355350](https://github.com/recm0708/netlab360/actions/runs/40233355350) | `push` | **completed / success** |

Las dos ejecuciones finales corresponden al commit `9e894d3f19051a7ca90662b4076febf8320986b3`, antes de los commits documentales siguientes. **No inferir automáticamente el resultado de runs futuros; consultar la ejecución del SHA que se esté evaluando.**

## Validación cruzada de Ubuntu (registro del estudiante)

En la VM, después de sincronizar el merge, `git log` llegó al commit `417c244`, las rutas portables de los tres scripts se verificaron, la regresión S02 obtuvo **29/29 pruebas OK**, la general **87/87 pruebas OK**, y la sintaxis Bash se validó. `tofu state list` conservó **17/17** registros; el manifiesto correspondió a **3/3 sedes, 4/4 WAN y 9/9 VLAN**, sin desplegar nuevos routers. `ens33=192.168.47.40/24` y GW `.2` permanecieron intactos; la fase 2 siguió pausada y `RESULTADO_S03_POSTMERGE=0`.

## Auditoría local de evidencias comunicada desde Windows

Carpeta auditada por PowerShell: `Pictures\Screenshots`, prefijo `S03_03` a `S03_09`.

- `S03_03`: una PNG, 63885 bytes.
- `S03_04`: una PNG, 35413 bytes.
- `S03_05`: una PNG, 38655 bytes.
- `S03_06`: una PNG, 41823 bytes.
- `S03_07`: una PNG, 40383 bytes.
- `S03_08`: una PNG, 39899 bytes.
- `S03_09`: **PNG no encontrada**; resultado de auditoría `S03_EVIDENCIAS_VALIDAS=6/7`.
- CSV de auditoría generado localmente: `Documents\NETLAB360_S03_Evidencias_20261025_160701.csv`. **No se ha transferido al repositorio ni se han contrastado las huellas SHA-256 individuales**, aunque el script las calculó localmente.

**Criterio de documentación:** para la parte de GitHub, este documento y los enlaces de ejecución son la evidencia primaria comprobable directamente en el repositorio, y el usuario no necesita abrir un PR o comprobar checks manualmente. **No declarar `S03_09` como PNG capturada.** Si la docente solicita obligatoriamente imagen de GitHub, se incorporará una captura genuina adicional; nunca una imagen sintética que parezca la interfaz real.

## Límites

La CI de GitHub ejecuta pruebas **offline** y verificaciones de sintaxis/plan. No demuestra por sí sola que FRRouting esté vivo en la VM ni que la topología WAN/LAN permaneciera encendida. La aplicación real OpenTofu metadata-only y la reconciliación Ansible sobre FRR están respaldadas por otras evidencias. El `.tar` técnico se prepara por separado, sin anexo dentro del Word.
