# NETLAB360 — REANUDAR AQUÍ

**Checkpoint canónico actualizado:** 14/10/2026, tras preparar estructura documental acumulativa. **Próximo trabajo:** obtener aprobación de índices y redactar Documento 01 por secciones en chat para que el usuario lo copie en su plantilla Word institucional. **No iniciar S02 ni nuevos ensayos AIOps.**

## Estado técnico real al último postcheck 13/10 23:35:02 (Panamá)
- En Ubuntu: `~/proyectos/netlab360`, rama `main...origin/main` limpia al commit `b410548` **antes de los commits documentales posteriores**.
- Lote06 importado y publicado: **86 PNG** directamente en `evidencias/capturas/`, **7 CSV**, SHA-256 y unicidad validados, subdirectorios=0; local/remoto idénticos.
- CI [38511477595](https://github.com/recm0708/netlab360/actions/runs/38511477595) `offline-regression` exitosa.
- Docker y namespaces vacíos, ens33 `192.168.47.40/24`, gateway `192.168.47.2`, servicios docker/ssh/open-vm-tools activos.
- IaC capturas históricas `IAC_S01_01/03/04/06` extraídas desde logs con rc0, pero **cuatro PNG nuevos todavía no recibidos ni publicados**. `LOTE06_Postcheck_Publicacion.png` fue recibido en chat y está pendiente de incorporación posterior.
- S01 **ABIERTA**, **72/100 técnico estimado** según [matriz](control/01-avance-s01.md); no confundir laboratorios aislados funcionales con criterios integrales aceptados.

## Principales capacidades demostradas
IPAM draft HQ/S1/S2 reservada; VLAN 802.1Q y ACL HTTP dentro de HQ; FRRouting OSPF dos WAN y HTTP HQ–S1 por estados estables WAN-P/B/P; LACP 2→1→2 y virtual NIC active-backup; OpenTofu metadata→Ansible configs FRR usadas en contenedores; exporter/API/NOC inicial; Prometheus con dos alertas firing y resolución; B4 reglas descriptivas sobre 76 ICMP sin pérdida, cuatro transiciones operativas, sin entrenamiento ML; 24 tests offline verdes.

## Brechas antes de cierre rubricado
Integración L2↔WAN↔servicio/NOC en topología única, failover de equipo/servidor no demostrado, reconciliación de FRR vivo no demostrada, Alertmanager/receptor y NOC multisede por completar, dataset/modelo ML evaluable pendiente, tag/release y OVA sanitizada/reimportada no acreditados. La necesidad de cubrir **todos** estos aspectos en S01 o distribuirlos S03/S06/S08 depende de la guía docente aún no aportada. [Matriz criterios 11](control/03-matriz-aceptacion-y-decisions-s01.md).

## Reglas documentales obligatorias
- Sólo **tres documentos maestros únicos** y acumulativos para S01–S08: [investigación](entregables/01-proyecto-investigacion-maestro.md), [memoria técnica](entregables/02-informe-tecnico-maestro.md), [manual](entregables/03-manual-usuario-maestro.md).
- El usuario trabaja en **su plantilla institucional Word**. El asistente envía texto aprobado sección por sección, con APA7, citas en texto y referencias reales verificadas; **un índice automático por documento**.
- Párrafos previos a todas las figuras/tablas, identificación con título/nota APA 7 cuando aplique; no insertar imágenes indiscriminadamente.
- No generar ni reciclar como finales los tres borradores V0.1 rechazados. [Política](entregables/00-politica-editorial-y-entrega-acumulativa.md).
- No seguir a S02 hasta resolver documentos y cierre S01; no confundir porcentaje con aprobación oficial.

## Reanudación en Ubuntu (sólo cuando se requiera)

    cd ~/proyectos/netlab360
    git status --short --branch
    GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main

No hacer git reset --hard ni push --force. Verificar red ens33/gateway y Docker/netns antes de ejecutar futuros ensayos; preservar snapshot y logs. No se necesitan nuevos comandos Ubuntu para comenzar a redactar los tres documentos.

**Issues prioritarias:** [#1 S01](https://github.com/recm0708/netlab360/issues/1), [#35 documentación](https://github.com/recm0708/netlab360/issues/35), [#36 guía](https://github.com/recm0708/netlab360/issues/36), [#43 evidencias](https://github.com/recm0708/netlab360/issues/43), [#29 OVA](https://github.com/recm0708/netlab360/issues/29).

**Historia y evidencia intactas:** `docs/sesiones/`, `docs/evidencias/`, `docs/decisiones/`, GitHub commits y comentarios de issues preservan la evolución y explican salidas antiguas.
