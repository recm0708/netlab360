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
