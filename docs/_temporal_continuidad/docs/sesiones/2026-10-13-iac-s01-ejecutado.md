# NETLAB360 — IaC S01 ejecutada y verificada en Ubuntu (OpenTofu + Ansible)

**Fecha de ensayo:** 2026-10-13, 22:27–22:30 Panamá (UTC-05:00). **Fuentes:** salida íntegra real del operador de pasos 156–168, fotografías 9 PNG, y logs locales referidos. No se han subido los PNG de esta nueva tanda; ver [auditoría visual](../evidencias/07-auditoria-visual-iac-s01-2026-10-13.md).

## Pruebas ejecutadas y resultado observado

| Área | Resultado real |
|---|---|
| SoT | `VALIDACIÓN B1: OK`, 3 sedes, 9 VLAN, 2 WAN, sin conflictos internos con VMnet8, rc0 |
| Herramientas | OpenTofu 1.13.1, Ansible core 2.20.1 |
| OpenTofu init/validate | 0/0; provider built-in `terraform_data` |
| Plan inicial | 5 add, 0 change, 0 destroy, rc0 |
| Apply | 5 recursos declarativos creados, rc0 |
| Manifest JSON | HQ/S1 activos, S2 reservada, dos WAN, guarda ens33 `192.168.47.40/24` y GW `192.168.47.2` OK |
| Ansible primera | 2 FRR candidatas de 725 bytes cada una; recap `ok=3 changed=2 failed=0`, rc0 |
| Compliance candidato | `R-HQ=COMPLIANT`, `R-S1=COMPLIANT`, rc0 |
| Ansible segunda | `ok=3 changed=0 failed=0`, rc0 |
| OpenTofu segundo plan | `No changes`; detailed-exitcode=0 |
| Tests previos | 2/2 unittest de comparador, incluyendo drift controlado de una copia, OK |
| Postcheck | 22:30:22, Docker y netns vacíos, ens33/GW y servicios intactos, Git `main...origin/main` sin cambios |

OpenTofu `terraform_data` únicamente registró **metadatos de recursos declarativos**; no aprovisionó red real. Ansible generó **archivos candidatos**, sin configurar routers vivos. Los dos estados y plantillas se encuentran FUERA de GitHub, en `~/netlab360-bootstrap/iac/s01/work/terraform.tfstate`, `manifest.json`, `rendered/R-HQ.frr.conf` y `R-S1.frr.conf`; no publicar el state ni tokens. La advertencia de Ansible acerca del intérprete Python 3.14 no causó errores.

**Evaluación interna:** S01 **65→68/100** (+3 en IaC, fila 1→4/10), y permanece abierta. Resto de IaC para ownership de equipos, reconciliación de configuraciones reales e integración/telemetría.

## Registros históricos para recuperar pantallas mejor encuadradas

- `01-tofu-plan.log`: prueba de 5 resources, 0 destroy.
- `02-tofu-apply.log`: cinco creaciones y `Apply complete`.
- `03-ansible-primera.log`: 2 cambios y 0 fallos.
- `04-ansible-idempotencia.log`: 0 cambios.
- `05-tofu-idempotencia.log`: No changes.
- `scripts/evidencias/resumir-iac-s01.py` reconstruye salidas ***desde logs sin reejecutar*** para capturas 01, 03, 04, 05 opcional, 06, con límites explícitos INICIO/FIN. Las capturas existentes de plan (tres fragmentos) y postcheck están aceptadas.

## Fase siguiente ya preparada (NO EJECUTADA)

- `scripts/laboratorio/iac-s01-drift-reconciliacion-local.py`: prueba sobre COPIAS fuera de repo; deriva OSPF cost10→50 en R-HQ, debe detectar `NON_COMPLIANT`, usa Ansible para reponer baseline y una nueva corrida verifica `changed=0`. Nunca toca FRR vivo ni VMnet8.
- `scripts/validacion/precheck-iac-b2.py`: gate solo lectura que verifica hash SoT del manifest, protección ens33, HQ/S1, S2 reservada, costos OSPF, dos FRR candidatos fieles a B2.
- `scripts/laboratorio/b2-dualwan-ospf.sh`: ahora admite el **origen opcional** `NETLAB360_IAC_CONFIG_DIR=$HOME/netlab360-bootstrap/iac/s01/rendered` al ejecutar `precheck` o `up`. Si no está definido, conserva exactamente el origen histórico por defecto. El gate debe pasar antes de crear contenedores. `status/fail/restore/down` conservan su comportamiento habitual.
- **Todavía NO se ha arrancado B2 usando los configs IaC.** Exigir snapshot VMware confirmado, bash -n, precheck de Docker/netns y VMnet8 antes de tocar recursos. Al concluir siempre `down` y postcheck sin residuos. Verificar fuente `B2_FUENTE_CONFIG_R-HQ`/`R-S1` en registro y pruebas Full/FIB. Esto será despliegue real de FRR con archivos originados en IaC, no aprovisionamiento de Docker por OpenTofu.

**Fotos de la siguiente prueba:** `IAC_S01_08_Drift_Detectado.png`, `IAC_S01_09_Reconciliacion.png`, `IAC_B2_01_Precheck_Origen.png`, `IAC_B2_02_Contenedores_FRR_Configurados.png`, `IAC_B2_03_OSPF_y_Rutas.png`, `IAC_B2_04_Postcheck.png`. Cada comando de la tanda incluye delimitadores concretos. Registrar el checkpoint después de la ejecución real, no antes.
