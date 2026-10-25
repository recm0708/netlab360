# NETLAB360 — Fase 3: OpenTofu metadata-only y GitOps (25/10/2026)

## Fuente de resultados y límites de validación

Resultados **ejecutados realmente en Ubuntu** según registro de terminal aportado por el estudiante `Texto pegado(20261025-205301).txt` (838 líneas). La VM estaba en Git `92090e3` cuando ejecutó los ensayos; GitHub se actualizó posteriormente. Este documento no contiene state, manifiesto de datos sensibles, contraseñas ni material de clase.

### OpenTofu aplicado y verificado

- Host: Ubuntu Desktop 26.04.1; `ens33 192.168.47.40/24`, puerta de enlace `192.168.47.2`, sin cambios en red de administración.
- Fase 2: desmontada intencionalmente; sin routers Docker S02, namespaces S02 ni estados WAN/LAN activos. No fue necesario reconstruirla.
- Preparador metadata-only: modo `S03_TOFU_MODO_S02=PAUSADA_Y_LIMPIA`; workspace y state bajo `~/netlab360-bootstrap/iac/s03/work`, **fuera del repositorio**.
- Validación previa: suite OpenTofu **7/7** y suite del plan **5/5**; `tofu init` y `validate` satisfactorios, plan exclusivo `terraform_data` de **17 creates, 0 changes, 0 destroys**.
- Aplicación real: **`Apply complete! Resources: 17 added, 0 changed, 0 destroyed.`** y `RESULTADO_S03_APPLY=0`.
- State: **17/17**; manifiesto `s03_manifest` coincide con SoT mediante SHA del inventario y cardinalidad **3/3 sedes, 4/4 WAN, 9/9 VLAN**, guarda VMnet8 conforme.
- Segundo plan: `-detailed-exitcode` **0**, `No changes. Your infrastructure matches the configuration.`; `S03_IDEMPOTENCIA_OPENTOFU=OK`.
- Regresión: dos ejecuciones adicionales (mismo bloque repetido por estudiante), cada una con 7+5 pruebas satisfactorias, administración intacta, fase 2 pausada, Git limpio y `RESULTADO_S03_REGRESION=0`.
- El contenido de `terraform_data` es un **manifiesto de metadatos**, **no** aprovisionamiento de routers, enlaces WAN, switches ni configuración FRR viva. Ansible cumplió el rol de reconciliación real previamente validado.

### Evidencias

- `S03_06_OpenTofu_Plan_17_Recursos_SoT`: salida compacta de plan validado, **generada en terminal**.
- `S03_07_OpenTofu_Apply_Manifesto_17_Recursos`: salida compacta de apply/manifiesto, **generada en terminal**.
- `S03_08_OpenTofu_Segundo_Plan_Sin_Cambios`: salida compacta de segundo plan/red administrativa, **generada en terminal**.
- **Guardado físico de estas PNG en Windows pendiente de confirmación**; no confundir ejecución del comando con existencia de screenshot.
- Registros locales de la VM (no versionados): `~/netlab360-bootstrap/evidencias/S03_OpenTofu_Apply_Manifest_17_Recursos.log` y `S03_OpenTofu_Segundo_Plan_Regresion.log`. No subir `terraform.tfstate`, `*.tfplan` o `s03-plan.json` sin revisión de confidencialidad.

## GitHub Actions y PR

- El workflow específico `.github/workflows/ci-s03-sot-opentofu.yml` pasó **SUCCESS** en ejecución [#7 / run 40229604798](https://github.com/recm0708/netlab360/actions/runs/40229604798), commit `4be2c60`: tests offline S03, `tofu init`, `validate` y `plan`, sin apply.
- La regresión general en el mismo commit [run 40229604811](https://github.com/recm0708/netlab360/actions/runs/40229604811) falló con 3 errores por `Path.home()/proyectos/netlab360` en scripts S02, incompatibles con la ruta checkout del runner GitHub. **No afectó las pruebas reales de la VM ni las tareas OpenTofu**.
- PR [#49](https://github.com/recm0708/netlab360/pull/49) corrigió la resolución de `ROOT` en tres scripts a `Path(__file__).resolve().parents[2]` y agregó `tests/test_s02_portable_paths.py`. Se revisó el diff: solo 3 modificaciones de ROOT y un archivo de tests; directorios de estado fuera del clon intactos.
- Workflow general **SUCCESS en PR #49**: [run 40233116672](https://github.com/recm0708/netlab360/actions/runs/40233116672). PR se fusionó por squash a `main` mediante commit `6e89b1c245e48512596bf6d1b46c3ee99293ecfb`. Comprobar también el check de push a main antes de cerrar GitOps; la ejecución en PR no implica necesariamente el estado de la ejecución posterior a merge.
- Evidencia `S03_09_GitOps_CI_Regresion_PullRequest` se reserva para captura de la página real del PR y checks; **no afirmar PNG guardado** antes de verificarlo.

## Pendientes y criterios de siguiente corte

1. Git pull fast-forward sobre VM, **sin sobrescribir state externo**; ejecutar full tests offline y sintaxis Bash, solo lectura.
2. Verificar check real de main después del merge.
3. Confirmar físicamente los archivos PNG de evidencia en Windows y sus huellas.
4. Registrar aceptación de `#17` (OpenTofu) y `#19` (CI/PR) al cumplir sus evidencias, conservando abierta la fase 3 global hasta documentación consolidada.
5. Continuar informe único hasta fase 3; artefactos finales en **TAR externo**, sin capítulo de anexos, sin incluir state, credenciales ni material docente.

## Actualización documentada tras regresión y auditoría Windows (25/10/2026)

El estudiante remitió `Texto pegado(20261025-210817).txt` (415 líneas). **Regresión post-merge en VM `RESULTADO_S03_POSTMERGE=0`** tras `git pull --ff-only` hasta `417c244`:
- `S03_REVISION_PR49=OK`: scripts WAN/LAN/HTTP portables con `Path(__file__).resolve().parents[2]`.
- Suite S02 `Ran 29 tests`, **OK**. Suite completa `Ran 87 tests`, **OK**. `S03_BASH_SINTAXIS=OK`.
- State OpenTofu externo persistente **17/17**, manifiesto 3/3 sedes–4/4 WAN–9/9 VLAN, `S03_PLAN_SIN_CAMBIOS_CONSERVADO=OK`, ens33/gateway intactos y fase 2 pausada.
- Auditoría PowerShell: **6/7 PNG**, `S03_03` a `S03_08` existen (archivos distintos y tamaño >0), `S03_09` ausente; CSV local `NETLAB360_S03_Evidencias_20261025_160701.csv` con huellas SHA-256 no transferidas ni verificadas por este repositorio. No afirmar contenido visual de imágenes no examinadas.
- [PR #49](https://github.com/recm0708/netlab360/pull/49) **merged**, SHA `6e89b1c245e48512596bf6d1b46c3ee99293ecfb`; CI general [40233116672](https://github.com/recm0708/netlab360/actions/runs/40233116672) PR SUCCESS, main [40233253796](https://github.com/recm0708/netlab360/actions/runs/40233253796) SUCCESS, además [40233355346](https://github.com/recm0708/netlab360/actions/runs/40233355346) SUCCESS y CI OpenTofu [40233355350](https://github.com/recm0708/netlab360/actions/runs/40233355350) SUCCESS.
- La **evidencia de GitOps** se mantiene en el propio repositorio: [`S03_09_GitOps_CI_Regresion_PullRequest.md`](../evidencias/S03_09_GitOps_CI_Regresion_PullRequest.md), con enlaces auténticos; esto evita exigir al usuario una inspección manual de GitHub. El documento no se presenta como captura PNG.
- El usuario pidió formalmente que ChatGPT **gestione directamente GitHub** (PR, Actions, issues, repositorio, validaciones y documentación), mientras él ejecuta solamente comandos locales del laboratorio. No volver a asignarle como paso manual revisar PR o verificar Actions.
- **Por realizar antes de cerrar fase 3 global:** insertar desarrollo académico específico de fase 3 en el Word y comprobar nueva exportación; evaluar paquete TAR final por separado. No repetir scripts `up/down`, `tofu apply` ni drift.


### Interpretación de una salida de tests potencialmente confusa

La regresión general offline imprimió `S03_WAN_COSTOS_VERIFICADOS=8/8 TARGET=150` y `S03_CONFIG_APLICADA=R-S1/s1b COSTO=150` mientras ejecutaba `test_*.py`. **Estos mensajes proceden del conjunto de pruebas unitarias/fixtures** y no de un cambio real de costo en el FRRouting de la VM. La infraestructura S02 se mantuvo desmontada, sin routers activos ni states WAN/LAN; el ensayo real de drift del 23/10 terminó con la restauración 150→100. No atribuir a esta regresión offline una nueva inyección de drift ni un escenario live.
