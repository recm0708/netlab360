# NETLAB360 — Integración real SoT/OpenTofu/Ansible → FRRouting B2 y drift local

**Ejecución observada:** 13/10/2026, 22:45:59–22:48:12 (hora Panamá). **Fuente:** transcripción completa recibida del operador de pasos 169–180; los PNG nuevos se recibirán después, y **NO están todavía publicados** en GitHub. No atribuir acciones que no consten en este registro.

## 1. Verificación técnica

| Hora / etapa | Resultado y procedencia |
|---|---|
| 22:45:59 precheck | `IAC_B2_PRECHECK=0`, `B2_ORIGEN_CONFIG=IAC_OPENTOFU_ANSIBLE`, `RESULTADO_PRECHECK_IAC_B2=0`, SoT hash validado, dos candidatos FRR COMPLIANT, WAN costos 10/100, host protegido |
| 22:46:22 up | Imágenes FRR con digest observado, configuraciones copiadas **desde** `~/netlab360-bootstrap/iac/s01/rendered/R-HQ.frr.conf` y `R-S1.frr.conf`; `OSPF_DUAL_FULL: SI`, 2 vecinos `Full` por router, rutas FIB seleccionadas `wan-p`, `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK`, `RESULTADO_UP_IAC_B2=0` |
| 22:47:11 status | Dos interfaces WAN UP por router, vecinos en estado `Full/-` sobre `wan-p` y `wan-b`, rutas `O>*` sobre `wan-p`; código 0 |
| 22:47:50 fail | WAN principal DOWN, ruta FIB HQ→S1 cambia a `wan-b` vía `10.78.0.6`, costo OSPF de respaldo, `CONMUTACION_WAN_B: OK (sondeo 1)`, `RESULTADO_FAIL_IAC_B2=0` |
| 22:47:54 restore | WAN-P UP, `RESTAURACION_WAN_P: OK (sondeo 11)`, vecino principal `Full` y FIB regresa a `wan-p` vía `10.78.0.2`, `RESULTADO_RESTORE_IAC_B2=0` |
| 22:48:07 down | `RESULTADO_B2_LIMPIEZA=0`, `RESULTADO_DOWN_IAC_B2=0` |
| 22:48:12 postcheck | Docker y namespaces vacíos, ens33 `192.168.47.40/24`, gateway `192.168.47.2`, servicios Docker/SSH/open-vm-tools activos, `main...origin/main` limpio |

Los avisos de `no ip ospf passive-interface` de FRRouting representan **comandos de sintaxis en desuso**, pero no impidieron la carga, adyacencia ni la prueba de ruta; actualizar sintaxis solo tras prueba aislada de regresión. El `status` y las rutas fueron leídos sobre routers realmente levantados. **No** se midió cero pérdida de tráfico durante la transición, ni latencia de convergencia exacta.

## 2. Drift y reconciliación separados del despliegue real

- 22:~45: desde archivos originales `COMPLIANT`, se generó copia aislada de R-HQ/R-S1 en `~/netlab360-bootstrap/iac/s01/drift-demo-2026-10-13`.
- Cambio **exclusivo en copia** `R-HQ wan-p ip ospf cost 10 → 50`; detector devuelve `NON_COMPLIANT` con exit1 esperado. R-S1 no se modificó.
- Playbook Ansible restaura la copia con recap `ok=3 changed=1 failed=0`; verificador de ambas candidatas `COMPLIANT`, hashes restaurados iguales a originales.
- Segunda ejecución: `changed=0 failed=0`. `RESULTADO_DRIFT_RECONCILIACION=0`; administración intacta y sin cambios de contenedores/interfaces.
- **Límite:** drift y reconciliación sobre **archivos candidatos en el filesystem**, NO sobre FRR vivo, no autorreconciliación continua ni aplicación de cambios detectados remotamente.

## 3. Auditoría de evidencias pendiente de archivos PNG

El usuario obtuvo salidas textuales con marcadores de estos bloques, pero anunció que las capturas **se enviarán después**. No afirmar recepción visual ni publicación de la tanda nueva:
- Complementos originales: `IAC_S01_01_Precheck_IPAM_Herramientas_Final`, `IAC_S01_03_Tofu_Apply_Manifest_Final`, `IAC_S01_04_Ansible_Render_Candidato_FRR_Final`, `IAC_S01_05_Compliance_FRR_Final` (opcional) y `IAC_S01_06_Idempotencia_Final`.
- Nuevos: `IAC_S01_08_Drift_Detectado`, `IAC_S01_09_Reconciliacion`, `IAC_B2_01_Precheck_Origen`, `IAC_B2_02_FRR_Configurado_Desde_Ansible`, `IAC_B2_03_OSPF_y_Rutas_IAC`, `IAC_B2_04_Postcheck_Final`.
- Falta aún un resumen fotográfico específico de la conmutación y restauración IaC (podrá recuperarse desde los logs `15-b2-dualwan-fail-20261013-224750.log` y `15-b2-dualwan-restore-20261013-224754.log`, sin reejecutar fail/restore); preparar cuando se gestione el lote.

## 4. Avance y próximos pasos

El bloque IaC gana **+3 puntos estimados** sobre 4/10 ya acreditados: +1 drift/reconciliación controlados en archivos, +2 integración de configuración Ansible sobre FRR realmente activo y reconvergencia observada. Resultado **IaC 7/10; S01 71/100 técnico estimado**. Los 3 restantes no se acreditan: falta ownership íntegro de recursos/aprovisionamiento de equipos y detección/corrección de drift de FRR en ejecución. La issue S01 sigue **abierta**. La rúbrica docente aún por ratificar; este es indicador interno, no calificación.

**Próxima vertical priorizada:** B4 analítica/AIOps: auditar calidad y variedad de los datos reales existentes (CSV de convergencia, resumen histórico, JSONL de exporter) **sin repetir otra caída WAN**. Determinar si es viable una evaluación ML reproducible o hace falta tomar muestras adicionales y etiquetar incidentes. No usar datos sintéticos como si fueran reales, ni presentar reglas simples como un modelo ML ya evaluado.
