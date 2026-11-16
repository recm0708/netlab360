# NETLAB360 — B4: protocolo de adquisición de datos temporales para AIOps (diseño)

**Estado:** diseño técnico versionado 13/10/2026; **SIN EJECUTAR**. No existe dataset etiquetado nuevo, entrenamiento ML ni métricas de evaluación válidas.

## Objetivo y separación de fuentes

Ampliar el histórico de una sesión de 76 sondeos sin pérdidas y 12 eventos JSONL de otras sesiones mediante nuevas **sesiones reales independientes** de un laboratorio B2 FRRouting. No crear datos artificiales para reportarlos como reales. Un evento detectado por el mismo exporter bajo prueba **no puede actuar como etiqueta independiente** de ese detector.

Dos artefactos por sesión:

1. `observaciones.csv` — muestreo periódico independiente, desde R-HQ hacia IP remota S1 `10.71.10.1`, con `timestamp_utc`, `elapsed_monotonic_s`, `probe_seq`, `icmp_success`, `rtt_ms` (nulo si falla), `fib_interface` (`wan-p`, `wan-b`, `none`), `ospf_full_neighbors`, `probe_exit_code`, `session_id`. Nunca inferir valores faltantes ni tratar `timeout` de sudo como falla ICMP.
2. `intervenciones.jsonl` — marcadores MANUALES/exógenos antes/después de cada acción de control `baseline_start`, `fail_requested`, `fail_ack`, `restore_requested`, `restore_ack`, `cleanup_requested`, `cleanup_ack`; con hora UTC y `session_id`. Las etiquetas se obtendrán de estas intervenciones verificadas y sus intervalos, **no** de los eventos del exporter; la ventana de reconvergencia llevará etiqueta `transicion`, no incidente persistente.

## Requisitos técnicos de seguridad

- Nunca modificar `ens33`, IP de gestión `192.168.47.40/24`, GW `192.168.47.2`, VMnet8, redes del host ni firewall para recolectar.
- Guardar CSV/JSONL/bitácoras en `~/netlab360-bootstrap/analitica/b4/sesiones/<session_id>/` fuera de GitHub; directorios 0700 y datos 0600; SHA256 por fuente y manifiesto al concluir.
- Precheck de snapshot VMware vigente, Docker/netns sin residuos y gate IaC–B2 aprobado. Reutilizar `NETLAB360_IAC_CONFIG_DIR=~/netlab360-bootstrap/iac/s01/rendered` validado previamente, sin tocar OpenTofu `terraform.tfstate`.
- No ejecutar acciones de fallo automáticas ni editar routers hasta completar un `precheck` y conseguir autorización explícita del operador para un nuevo ensayo. Toda falla será **únicamente del enlace wan-p de namespaces aislados de FRRouting**, nunca de `ens33`.
- El controlador B2 `up --snapshot-confirmado`, `status`, `fail`, `restore`, `down` debe devolver 0, y el recolector no debe confundir fallos de herramienta con errores de red.
- Si hay error de adquisición/failover, terminar muestreo sin borrar evidencia parcial y ejecutar `down` controlado; no repetir ciegamente; postcheck Docker/netns/Git y VMnet8 intactos.
- Primera prueba del nuevo recolector: **solamente fase normal sin fallo** por al menos 30 observaciones, seguida de `down`. Luego programar tres sesiones completas separadas (normal → transición → respaldo estable → restauración) para crear conjuntos entren/evaluación independientes.
- Mantener código y esquemas en GitHub, pero datos reales en bootstrap. No copiar inadvertidamente logs que contengan identificadores de host o credenciales al repositorio público.

## Evaluación propuesta (no realizada)

1. Perfil de datos: fracción de observaciones disponibles, RTT, pérdidas, FIB, convergencia, timestamp UTC estable y lag de muestreo.
2. Etiquetado independiente por intervención del operador, con intervalos explícitos `normal` / `transicion` / `respaldo_controlado` / `restaurada` y un evento de incidente solo si hay desviación respecto a intención real.
3. Particiones **por sesión completa**, nunca división aleatoria por filas consecutivas, para evitar contaminación temporal de la evaluación.
4. Baseline reglas existente `scripts/analitica/b4-diagnostico-reglas.py` vs futuro clasificador/no supervisado `sklearn` si datos suficientes. Calcular confusión TP/FP/FN/TN solo con etiquetas independientes y reporte de limitaciones; no computar métricas de entrenamiento como desempeño final.
5. Separar **disponibilidad de aplicación** de visibilidad de rutas/ICMP, ya que un ping satisfactorio no garantiza HTTP ni cero pérdida entre sondeos.

**Siguiente implementación:** prototipo pasivo, sin intervención, de recolector que registre en CSV las métricas reales del router B2 y admita marcadores externos, más validación offline de esquema y pruebas con fixtures explícitamente sintéticos. Tras validar, iniciar un único ensayo normal con snapshot y cleanup. Ninguna adquisición nueva está acreditada todavía.
