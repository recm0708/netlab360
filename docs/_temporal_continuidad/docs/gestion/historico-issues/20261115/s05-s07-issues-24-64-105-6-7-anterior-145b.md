# Archivo histórico de issues S05–S07, antes de la auditoría 145B · 15/11/2026

Respaldo de descripciones anteriores. Checklists vigentes: consultar las issues, no usar este documento histórico como instrucciones.


---

# ISSUE #24 · [016] WireGuard/sucursales adicionales — ampliación S05 condicionada · estado closed

# Extensión opcional de red — fase 5

- [x] Comparar beneficio: las tres sedes HQ/S1/S2 ya tienen WAN 2+2, 9 VLAN y OSPF con failover; un cuarto sitio o túnel WireGuard no añade validación central de HA de equipos/OVS.
- [x] Evaluar alcance y riesgos: una sede más o VPN exige más rutas, fuentes, inventario, escenarios de falla y validación de aislamiento de `ens33`; amplía superficies sin completar el núcleo S05.
- [x] **No adoptado en S05:** implementación de WireGuard/4.ª sede no es un requisito acreditado ni se declarará realizada; mantener como propuesta futura condicionada, sin ejecutar servicios.
- [x] Registrar **descarte de alcance S05**: priorizar HA de equipo/servicio, SDN OVS/Faucet, NOC FIB y evidencias, antes que una cuarta sede/VPN.

**No es un requisito acreditado de cierre S02/S03.** Mantener abierto como opción de fase 5 hasta la decisión de alcance.

**Decisión de planificación 11/11/2026:** cerrar esta issue como **not planned**; funcionalidad opcional no implementada. Se podrá reabrir si la docente requiere expresamente una nueva sede o túnel. El cierre de esta issue no acredita WireGuard ni cifrado.



---

# ISSUE #64 · [S05] NOC WAN/HTTP operativo; integrar LACP y SDN observados · estado open

## Continuidad 15/11/2026 — scripts 145A/145B probados en CI y fusionados

- [x] Lotes **144A/B/C** completados en VM: monitor HTTP S2 de 1.69s con ambos backends running y frontal BACKEND_HQ/PRINCIPAL, 2 muestras NOC sin advertencias y rutas FIB S1=s1p/S2=s2p; 3 GET HTTP desde S2 200 OK; helper legacy root:root 0755/FIB sin cambios.
- [x] **PR #141** fusionado (docs, commit cc6f2a67): [corte maestro operativo](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), procedimiento de backup/rollback y validación NOC LACP/SDN.
- [x] **PR #142** fusionado tras **dos workflows CI SUCCESS** (commit 50f18f30): scripts ejecutables [145A](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145a-instalar-observador.sh) y [145B](https://github.com/recm0708/netlab360/blob/main/scripts/operacion/s05-lote-145b-activar-noc.sh), test offline bash -n y prohibición de mutaciones de red. Incidencia previa en aserción de test estático corregida y la revisión final de CI aprobada. **NO se han ejecutado todavía en la VM.**
- [ ] **SIGUIENTE ACCIÓN REAL**: en VM `cd ~/proyectos/netlab360 && git pull --ff-only origin main`; con Git limpio y SHA del helper legacy correcto, ejecutar `bash scripts/operacion/s05-lote-145a-instalar-observador.sh` y confirmar marcador `LOTE145A_HELPER_ROOT_NOC=OK` y snapshot FRR/FIB/LACP/SDN. **Después solamente** ejecutar `bash scripts/operacion/s05-lote-145b-activar-noc.sh`, confirmar dos muestras API y marcador `LOTE145B_NOC_LACP_SDN=OK`. Los scripts tienen respaldo root y retorno ante error y registran logs TXT 14 y 15 en noc-integracion.
- [ ] Tras 145B OK, revisar dashboard en Chrome con SSH túnel 9130, cuatro tarjetas reales LACP HQ/S1/S2 + Faucet, hora Panamá, capturar S05_63. Si hay error, NO repetir sin diagnosticar hash/backup y leer log.
- [ ] S05 restante: #32 HA independiente instancia/equipo y su alcance mono-VM, #31 P1/P1B estadística, #105 auditoría PNG originales; pasar a S06/S07 cuanto antes. Informe S01–S04 existente puede ampliarse **ya**, sin esperar S07 ni reescribirse de cero.


---

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

## Corte vigente S05 · 15/11/2026 · 143A/B/C aprobados, HTTP HA en diagnóstico

- [x] **143A COMPLETADO:** Git local main 1fba8c5, 21/21 pruebas del parser, 14/14 topología, 14/14 layout, 6/6 HA/UI = **55/55**. Helper autorizado INSTALADO sigue LEGACY root:root 755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`. ens33 .40/24 gateway .2 y Git limpio.
- [x] **143B COMPLETADO:** 6/6 bonds HQ/S1/S2 switch y cliente, `ip JSON ad_num_ports=None` en los seis y `/proc/net/bonding Number of ports:2` en todos, alias y 802.3ad correctos. OVS propietario S05, Faucet running, OpenFlow connected, 25 reglas. FIB S1=s1p, S2=s2p. API en ejecución aún sin LACP/SDN (NO desplegada).
- [x] **143C COMPLETADO:** cuatro tarjetas HTML fuera del SVG, `node --check` OK, NOC/exporter active, gestión y Git intactos.
- [ ] **Anomalía por investigar, NO declarar HA correcto:** 143B capturó fuente HTTP de S2 válida `available=true`, `ha_service.status=offline`, backend/path `None`, timestamp 2026-11-15T12:39:45+00:00; `source_warnings=[]`. No implica necesariamente caída de los tres servicios. Diagnosticar monitor y endpoints HTTP desde cliente S2 antes de cualquier rollout.
- [x] [PR #140](https://github.com/recm0708/netlab360/pull/140) fusionada en main (commit `70bd06cc`): [corte maestro actual](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-143C-20261115.md) y [lotes 144A/B/C SOLO LECTURA](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-144a-144c-diagnostico-http-ha-pre-noc-20261115.md). Los marcadores `COMPLETADO` de 144 representan diagnósticos, no aceptación HA.
- [ ] **Próximas ejecuciones (NO hechas todavía):** 144A dos muestras de NOC y observación S2, 144B tres GET HTTP desde netns S2 y journal, 144C hash/helper legacy y FIB. No sobrescribir logs históricos 08/09/10, no instalar binario root, no reiniciar NOC ni guest. Tras revisar resultados, definir instalación atómica root:root con backup/rollback y validación UI/FIB/LACP/SDN.


---

## CORTE VIGENTE 15/11/2026 — incidencia 142B y continuación segura

**Estado de ejecución (verificado por el TXT del usuario):** 142A **APROBADO**, 49/49 pruebas (15 nuevas + 14 topología + 14 layout + 6 HA/UI), `LOTE142A_CODIGO_Y_BASELINE=OK`, main de VM sincronizado hasta `eef8946`, Git limpio, `ens33=192.168.47.40/24`, GW `192.168.47.2`. El ejecutable autorizado `/usr/local/libexec/netlab360-observer` **sigue en versión LEGACY** root:root 0755 SHA-256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; el código NUEVO del NOC está en GitHub pero **NO desplegado en la VM**.

**142B ABORTÓ DOS VECES** en paso 826, primer `HQ_SW`: alias correcto `S05_HQ_a14ac59efb1e996a`, modo 802.3ad y flags UP/LOWER_UP; `ip -n ... -j -d link` devolvió `ad_num_ports=None`, lo que produjo `AssertionError` en el verificador, antes de validar los otros cinco bonds y OVS. El TXT histórico `~/netlab360-bootstrap/s05/evidencias/noc-integracion/06_Precheck_Raw_Bonds_OVS_Observador.txt` documenta la segunda ejecución fallida. **No existe marcador 142B=OK** y **142C NO se ejecutó**. Esto **no demuestra falla del bond**: el auditor anterior de `ip -d` mostró 2 miembros y el validador probado usa `/proc/net/bonding`.

**Corrección [PR #139 fusionada en main](https://github.com/recm0708/netlab360/pull/139), CI SUCCESS, commit 1fba8c5f75c2fae57ba7268aebdeaf8616312af5:** observador de lectura solo acepta seis pares namespace/dispositivo fijos, verifica propietario/modo 802.3ad mediante JSON y, si `ad_num_ports` está ausente, consulta `/proc/net/bonding` exigiendo `Number of ports` único (0–2); faltantes/inconsistencias se expresan UNKNOWN, nunca se fabrican dos puertos. Incluye 6 tests nuevos. La corrección GitHub no se ha instalado ni validado aún en la VM.

**Retomar directamente:** [CORTE MAESTRO](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-142B-20261115.md) y [lotes 143A/143B/143C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-143a-143c-reparacion-parser-y-continuidad-20261115.md). Ejecutar 143A tests/legacy hash, 143B seis bonds JSON+/proc y OVS/FIB/HTTP, 143C UI/JS/hashes; conservar todos los TXT históricos. No repetir 142A ni 142B ORIGINAL. **NO instalar helper root, reiniciar NOC, reiniciar guest ni modificar ens33/FRR/OVS/LACP/Faucet hasta gates OK.** S05 y esta issue continúan abiertas; HA instancia #32, evidencia PNG #105 y S06/S07 pendientes.

---

## Estado vigente · 14/11/2026 · **ABIERTA**
El NOC interactivo y el HA HTTP están funcionando. **Todavía faltan las observaciones de LACP multisede y OVS/Faucet, más aceptación visual y evidencias finales.**

### Validado
- [x] Vista de tres sedes HQ/S1/S2, routers y switches, 9 VLAN y 4 WAN, selección en UI y panel de inspección FIB.
- [x] WAN primaria/respaldo S1/S2 observada y estados diferenciados; no representar selección de interfaz como cambio FIB real.
- [x] Corregido formato de hora Panamá; panel HTTP HA, backend HQ preferido y S1 de respaldo; NOC observa HQ→S1→HQ con 22 muestras JSONL.
- [x] S04 exporter y S05 NOC independientes de sesión SSH mediante systemd; monitor S2 HTTP en servicio activo.
- [x] Capturas S05_39A/39B aceptadas como vista HA, salida S05_40 de ciclo; correcciones UI versionadas con CI.
- [x] LACP HQ real activo en VLAN120 (lotes 109–110), aunque **todavía no representado en el NOC mediante fuente de telemetría**.

### Pendientes de aceptación
- [ ] Mostrar componentes LACP HQ/S1/S2 con estado alimentado por observación real y caducidad; no colorear como `RUNNING` sin fuentes y no inventar métricas.
- [ ] Incorporar SDN OVS/Faucet después de desplegarlo realmente (#23), sin mezclar su bridge con WAN/VMnet8.
- [ ] Revisar con el operador diagrama final y refresco de datos, etiquetas/horas, espacio/legibilidad y comportamiento ante falla/restauración.
- [ ] Ejecutar postcheck HTTP HA+FIB+gestión tras la integración final, documentando limitaciones de disponibilidad de telemetría.
- [ ] Auditar/importar originales PNG, JSONL y manifiestos SHA256 [#105](https://github.com/recm0708/netlab360/issues/105); cerrar esta issue solo con evidencia y pruebas satisfechas.

Estado general: [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md); histórico: [histórico íntegro de esta issue](https://github.com/recm0708/netlab360/blob/main/docs/gestion/historico-issues/s05-issue-64-antes-de-consolidacion-20261114.md).
## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.

## Corte real 15/11/2026 — resiliencia de enlace SDN aceptada (lotes 136–138)

- [x] **Lote 136**: Faucet sigue conectado, 25 reglas OpenFlow, A↔B permitido y C aislado, ens33 `.40/24` GW `.2`, Git limpio. Se verificaron **7/7 registros TXT** por SHA-256 (incluidos 135A/B/C y recuperación anterior). `LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK`.
- [x] **137A**: 9/9 tests de seguridad OK; precheck de ownership/puerto SDN A, OpenFlow conectado, 31 reglas, servicios S02/FRR/NOC/HA preservados; `LOTE137A_PRECHECK_FALLA_SDN=OK`.
- [x] **137B**: watchdog `nl360-s05-sdn-port-a-rescate-68997ee0a7.timer` armado; **solo `sdna0` DOWN**. Ping A→B mostró `10 transmitidos, 0 recibidos, 100% pérdida, RC1`, controlador Faucet siguió conectado; preservación de FRR, NOC, HA comprobada. Restauración `sdna0` solicitada; A↔B volvió en **intento 1**, A↔C/C↔A permanecieron aislados, OpenFlow 31 reglas; watchdog cancelado tras validación, `S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A`. Operador confirma capturas **S05_61 y S05_62** tomadas, pendiente auditoría bytes PNG.
- [x] **138**: SDN OK, 3 LACP 2/2, 4/4 pings por sede, rutas OSPF S1 via s1p y S2 via s2p, seis servicios active, ens33/GW/Git inalterados; `LOTE138_REGRESION_FALLA_SDN=OK`. **3/3 TXT** verificados SHA256.
- [ ] **Pendiente dentro de #23:** comparar técnicamente con bridge Linux/FRR, distinguir la falla probada de `sdna0` de una caída de controlador/equipo, integrarlo con NOC real y auditar/importar PNG originales. **No repetir el fallo SDN, ni los LACP.**
- [ ] **Siguiente paso**: precheck de NOC 9130/exporter 9110 y observador privilegiado root:root instalado; diseñar telemetría real de 3 agregadores y OVS/Faucet con caducidad/UNKNOWN, sin mostrar estado estático como disponibilidad.

## Próxima secuencia #64 · Precheck sin cambios del NOC antes de telemetría nueva

- [x] Lotes **136–138** SDN respaldados por logs, PNG 61/62 reportados y SHA256 TXT correcto; OVS/Faucet y tres LACP conservados.
- [x] **PR #136** fusionada (commit `a0c5fe95`): [runbook 139A/139B/140/141](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-139-141-precheck-fuentes-noc-20261115.md) para consultar NOC 9130, exporter 9110 y dos muestras, grafo actual, root helper `/usr/local/libexec/netlab360-observer snapshot`, tres LACP switch/client y OVS Controller con estado real, y pruebas UI. **NO ejecutado todavía en VM.**
- [ ] Tras auditar permisos y contrato del observador, versionar API/visualización de LACP y Faucet/OVS con muestras frescas y estado UNKNOWN al faltar datos. El helper de root debe preservar el contrato FIB existente; no exponer root ni modificar sudoers de manera improvisada.
- [ ] Captura visual final pendiente de API, capa de estados y formato horario Panamá; no inventar tráfico medido ni inferir disponibilidad LACP de state=active.

## Corte comprobado 15/11/2026 — auditoría NOC 139A/B/140/141 y PR #138 preparada

- [x] **139A**: seis servicios S04/S05 activos, 9130 y 9110 LISTEN loopback. Dos muestras 4s separadas: exporter `source_ok=true` y topología active, NOC `routing.available=true` con FIB S1=`s1p` S2=`s2p`, HA HTTP principal HQ `running`, warnings=[], hora `America/Panama` coherente y gestión `.40/24` GW `.2`.
- [x] **139B**: helper `/usr/local/libexec/netlab360-observer` root:root 0755 idéntico al fichero anterior por SHA `8c4480...`; `sudo -n ... snapshot` RC0, FRR x3 y rutas FIB legítimas. systemd NOC corre como rc-aa-ec y consulta helper autorizado por sudoers.
- [x] **140**: LACP HQ/S1/S2 2/2 en switch/cliente, `ad_num_ports 2`, alias de propiedad S05; Faucet/OVS state active, OF1.3 connected, OFPORT1/2/3 LIVE. No se repitieron pruebas de falla, ni se modificó gestión.
- [x] **141**: 14/14 pruebas de topología + 4/4 HA/NOC, 18 nodos/21 enlaces, warnings=[], campos LACP/SDN aun no integrados en API desplegada.
- [x] [PR #138](https://github.com/recm0708/netlab360/pull/138) fusionada (CI success, commit `eef89467`): helper sudoers actual extendido con fuentes read-only acotadas a 3 bonds 802.3ad y OVS/Faucet; app valida propietarios/antigüedad <=15s y devuelve UNKNOWN sin muestra, interfaz con 4 tarjetas sin alterar SVG, formateo horario es-PA. 
- [ ] **NO desplegado todavía en VM:** ejecutar [lotes 142A/142B/142C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-142a-142c-preflight-telemetria-noc-20261115.md) para comparar root helper anterior, correr pruebas, comprobar JSON real iproute2 en 6 bonds y OVS, sintaxis JS y hooks UI. Si JSON no coincide, corregir parser antes de instalar.
- [ ] Tras logs 142 OK: preparar instalación atómica del helper root:root con copia de retorno, validar FIB/LACP/SDN desde mismo sudoers, reiniciar SOLO NOC 9130, medir API y verificar vista real y hora Panamá. No hacer `up/down`, reiniciar guest o alterar FRR/OSPF/LACP/OVS/ens33.



---

# ISSUE #105 · [S05] Auditoría de evidencias originales, SHA-256 y aceptación integral · estado open

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

## Objetivo
Consolidar las evidencias originales S05 de NETLAB360 y ejecutar la aceptación final **antes** de cerrar la issue madre #5 y milestone S05. Separada de implementación para evitar que las tareas de evidencia se pierdan entre notas históricas.

## Confirmado a 14/11/2026

- [x] Existe [tablero S05 vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md) y [auditoría de 50 issues](https://github.com/recm0708/netlab360/blob/main/docs/gestion/auditoria-issues-20261114.md).
- [x] LACP HQ desplegado: 2/2 miembros 802.3ad en switch/cliente VLAN120; HTTP HA/OSPF/gestión conservados en lotes 109–110.
- [x] Captura S05_45 reportada tomada; salidas delimitadas S05_46 y S05_47 técnicamente correctas. **No se ha verificado que sus archivos PNG existan o estén importados**.
- [x] Logs del diagnóstico L111D-R/S: cliente LACP HQ llega a 4/4 destinos, hosts base 3/3, rutas OSPF primarias; SSH activo, conexión reset intermitente sin causa acreditada.

## Checklist para cierre

- [ ] Inventariar los **archivos PNG reales** S05 en Windows y/o VM, confirmar cuáles están realmente tomados (incluidas S05_46 y S05_47) y cuáles faltan, sin generar capturas inventadas.
- [ ] Incorporar evidencia real de falla 2→1→2 HQ (S05_48/49), LACP S1/S2, redundancia de instancia, OVS/Faucet y vista NOC final. No exigir repetir pilotos que ya tienen evidencia validada.
- [ ] Revisar y consolidar fuentes originales JSON, TXT, JSONL, CSV (P1/P1B, failover WAN/HTTP, OVS/Faucet y tests); evitar duplicados e inconsistencias de numeración.
- [ ] Crear y verificar manifiesto SHA-256 de **cada archivo realmente importado**; auditar tamaño, nombre, hash y procedencia.
- [ ] Ejecutar regresión integral S01–S05 y controles de no regresión de `ens33`, OSPF, puertos HA, servicios y repositorio Git.
- [ ] Incorporar las evidencias a carpetas versionadas y referenciarlas en [informe único](https://github.com/recm0708/netlab360/issues/27); no publicar secretos ni estados sensibles.
- [ ] Emitir acta de aceptación S05 que identifique capacidades **implementadas**, límites virtuales, descartes de alcance y pendientes S06–S08. Cerrar #5 y milestone S05 solo después de contrastar #23, #31, #32, #64 y esta issue.

## Referencias

- [Histórico completo previo al ajuste](https://github.com/recm0708/netlab360/tree/main/docs/gestion/historico-issues)
- [Documento operativo vigente](https://github.com/recm0708/netlab360/blob/main/docs/gestion/s05-tablero-vigente.md)
- [Punto de reanudación](https://github.com/recm0708/netlab360/blob/main/docs/REANUDAR-AQUI.md)

**Estado:** pendiente, no cerrar por adelantado.
## 14/11/2026 · Lotes 114A-S, 114B, 114C y 114D completados realmente

- [x] **114A-S:** Git a `832b6e1`; dos rondas a gateway HQ `10.70.20.1`, frontal HQ `10.70.20.23`, backend S1 `10.71.20.21` y host S2 `10.72.20.20`: **16/16 paquetes recibidos, 0% pérdida en esas rondas**. Bonds switch/cliente IEEE 802.3ad 2/2; `ens33=.40` GW `.2`, Git limpio. `LOTE114A_S_ESTABILIDAD=OK`.
- [x] **114B:** falla controlada de miembro `s5c1` con watchdog `systemd-run` temporal; switch y cliente pasaron **2/2→1/1→2/2**. Durante 1/1 ping 4/4 destinos y HTTP real `200_BACKEND_HQ`; HA/FIB y puertos S02 conservados. Tras restauración 4/4 ping, VLAN120 PVID untagged, gestión intacta y rescate cancelado. `S05_LACP_HQ_PRUEBA=OK_2_1_2`, `LOTE114B_FALLA_RETORNO=OK`. Esto no demuestra 0 pérdidas durante cada milisegundo de conmutación.
- [x] **114C:** secciones de salida `INICIO_CAPTURA_S05_48/49` a `FIN_CAPTURA` extraídas y revisadas; **no consta confirmación de archivos PNG guardados**, ni importación binaria.
- [x] **114D:** validador selectivo S1/S2 `plan` + `precheck` = OK; candidatas `10.71.20.40` VLAN220 y `10.72.20.40` VLAN320 no asignadas en inventario de 36 direcciones ni responden ICMP desde host VLAN; 3 FRR running, interfaces/VLAN protegidas, NOC/HTTP HA OK; HQ conserva 2/2. `LOTE114D_S1S2_PRECHECK=OK`. La ausencia de respuesta ICMP **no garantiza** globalmente IP libre.
- [x] El operador confirmó capturas recientes tomadas, incluidas 48/49/51/52; **sin verificar archivos PNG originales o hashes en GitHub todavía**.

Evidencia local: `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/30_Estabilidad_PreFailover_HQ.txt`, `25_Falla_Retorno_HQ_2_1_2.txt`, `31_Preparacion_LACP_S1_S2.txt`.
## Corte 14/11/2026 · Lotes 115–117 y evidencias revisadas

- [x] **Lote 115:** CI y 7 tests locales de contratos S1/S2 OK; precheck S1/S2/HQ, gestión `ens33=192.168.47.40/24`, gateway `.2` y Git intactos.
- [x] **Lote 116:** **LACP S1 desplegado realmente** en VLAN220 y `10.71.20.40/24`, switch `nl360-s02-sw-s1/s5bond0` y cliente `nl360-s05-lacp-s1/bond0` en 802.3ad **2/2 miembros**; pings 4/4 (S1 GW, HQ frontal, S1 backend, S2 host), `S05_LACP_S1_SERVICIOS_HA_FIB=OK`, S02 protegido, HQ 2/2, VLAN220 PVID untagged y gestión intactos. `LOTE116_LACP_S1=OK`. PNG de captura **S05_50 recibido y visualmente validado**, no importado aún al repo.
- [x] **Lote 117 paso 596:** precheck S2 OK; inventario aumentó de 36→**37 IPv4** tras agregar S1. IP `10.72.20.40` propuesta sin asignación observada, VLAN320 sin conflictos y servicios HA/NOC correctos.
- [x] **Lote 117 paso 597 falló antes de crear nuevos recursos S2**: `TimeoutExpired` a 15s en `sudo ip netns exec nl360-s02-sw-s2 bridge vlan show`, durante **precheck** de `up`; no apareció `S05_LACP_S2_DESPLIEGUE=OK`, y 598–600 no corrieron. **No asumir S2 instalada** ni repetir UP sin comprobar state e interfaces.
- [x] [PR #115](https://github.com/recm0708/netlab360/pull/115) integrada tras CI OK, commit `2424d87bbd2806d9060c3fb56117e7d8515d2e03`: consulta `bridge vlan show` ahora solo lectura con **2 intentos hasta 30s**, cuenta timeout y falla cerrado si continúa.

## Capturas recibidas / confirmadas en el corte 14/11/2026

- [x] Se recibieron 18 capturas originales del usuario de S05_32–47 (incluidas 39A/39B) y S05_50; revisadas visualmente. 39A (solo cabecera parcial del NOC) y 44 (limpieza no explícita) son complementables.
- [x] Usuario confirmó después que **tomó las capturas adicionales** de los lotes 117R/118-R y recuperación HQ; **no implica que sus archivos binarios hayan sido importados o que su SHA256 esté comprobado en GitHub**.
- [ ] Incorporar y verificar SHA-256 de los PNG originales S05_48/49, S05_51/52 y S05_53–57. Las salidas 53–57 se han generado en los ensayos reales; no consta verificación de los bytes PNG originales.
- [x] Resultado L118-R verificado en salida de terminal: HQ/S1/S2 2/2, OSPF s1p/s2p, seis servicios active y gestión intacta; pendiente importación de originales.


**Mantenimiento checklist (14/11/2026):** Se retiraron las instrucciones operativas de lotes 114/115–118 ya superados, preservadas en GitHub y documentos de reanudación. Las casillas abiertas restantes se refieren a trabajo aún no completado; no declarar fase S05 cerrada.

## Corte 15/11/2026 · SDN Faucet operativo, falta evidencia 60 y cierre de regresión

- [x] **133A**: 20/20 tests offline OK (8 recuperación + 12 SDN), state previo `needs_inspection`, mounts/propietario/Docker/Errno13 verificados. Primer intento de sincronización sufrió reset SSH sin demostrar regresión.
- [x] **133B**: recuperación selectiva en sitio exitosa; permisos del directorio de logs ajustados y **mismo contenedor Faucet iniciado**, OpenFlow connected al intento 9, 25 reglas, cuatro pings/aislamientos correctos, baseline S02/FRR/gestión intacto; state a `active`, `LOTE133B_RECOVERY=OK`.
- [x] **133C pasos 716–718**: OpenFlow connected y `31` reglas, capturas **S05_58 y S05_59** con resultados válidos, A↔B 2/2 y 2/2 (0% pérdida).
- [ ] **133C paso 719**: A→C devolvió 2 transmitidos/0 recibidos/100% pérdida, pero wrapper externo `timeout -k 2s 10s` marcó **RC124** y abortó el lote (se exigía RC1 del ping). No se ejecutó C→A ni se imprimió FIN_CAPTURA_60 o LOTE133C_OK. No inferir que SDN falló por este RC124.
- [ ] **133D**: NO se ejecutó. El paste en terminal contenía secuencias `[200~` y delimitador `BASH~`, produjo heredoc abierto/errores de sintaxis, cancelado por Ctrl+C. No existe auditoría completa ni manifiesto SHA de 133D.
- [x] [PR #129](https://github.com/recm0708/netlab360/pull/129) propuesta: verificador solo consulta de captura 60 con ping RC1/0 recibidos/100% pérdida, control positivo A→B RC0/2/2, sin timeout externo de 10 s, tests de rechazo RC124 y RC2 y [lotes 134A–134C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-134a-134c-evidencia60-y-regresion-20261115.md) para cerrar evidencia/regresión. **No se han ejecutado lotes 134.**
- [x] Captura S05_60 reportada tomada por el operador y comprobada mediante log con INICIO/FIN y RC0/RC1. **Pendiente:** verificar el PNG original y su SHA-256. No repetir 133A/133B ni ejecutar up/down.

## Corte del 15/11/2026 — suspensión VMware solicitada y fallo de formato ICMP en 134B

- [x] **134A** completado: 10/10 tests offline; `S05_SDN_FAUCET_OPENFLOW=CONNECTED`, 25 reglas, pings A/B y aislamiento C correctos, gestión `ens33=192.168.47.40/24` GW `.2`, repo limpio.
- [x] **134B diagnosticado**, NO completado: estado SDN active, 31 reglas OpenFlow; ping negativo A→C regresó RC1 y `10 packets transmitted, 0 received, +10 errors, 100% packet loss`. El parser solo aceptaba `received, 100%` sin `+10 errors` y 2 enviados; abortó sin FIN_CAPTURA ni marcador OK. Reintento sufrió caída SSH; otro reprodujo lo mismo. **Captura S05_60 pendiente** y 134C no iniciado.
- [x] [PR #131](https://github.com/recm0708/netlab360/pull/131) CI OK y fusionada (commit `d49ff77b`): corregir parsing de salidas iputils con `+N errors` y múltiples transmisiones negativas de ARP, manteniendo RC1+0 recibidos+100% pérdida como gate, rechazando RC124/RC2/timeout, conservando exigencia 2/2 RC0 en A→B. Tests reproducen el caso real.
- [ ] **Pausa operativa antes de más pruebas:** usuario desea reiniciar Windows. Verificar espacio de volumen anfitrión vs RAM guest, baseline en TXT, sincronizar disco y **suspender completamente `netlab360-lab` en VMware Workstation** antes de reiniciar Windows. La suspensión aún **no está confirmada**, ni la reanudación. No reiniciar guest Ubuntu; los netns efímeros requieren estado de RAM conservado. No borrar .vmss/.vmem/.lck, no snapshots permanentes.
- [ ] Tras reanudar, verificar fecha, ens33/route, Faucet/OpenFlow, contenedor/3 namespaces, FRR/LACP/HA/NOC. Entonces repetir **solo** captura 60 con el parser corregido, usando un TXT nuevo que preserve el histórico fallido; completar regresión global y SHA256, y auditar PNG.

## Corte 15/11/2026 — VMware reanudada; LACP status detectó falso drift de tabla completa

- [x] VMware Workstation restauró el estado suspendido de Ubuntu tras reinicio Windows: NTP sincronizado, `ens33=192.168.47.40/24`, default GW `.2`, 21 namespaces y cuatro contenedores (FRR x3 y Faucet) activos.
- [x] SDN state active, OpenFlow connected con 28 reglas, VLAN410 A↔B comunicada y VLAN420 C aislado, baseline S02/FRR/gestión conservado.
- [ ] **LACP de HQ**: bonds 2/2 y cuatro pings OK, pero `status` lanzó `Red de gestión cambió respecto del precheck` al comparar texto literal de TODA la tabla de rutas. La diferencia exacta frente al state-hq.json aún requiere auditoría; S1/S2 y seis servicios no llegaron a validarse en esa ejecución. `NETLAB360_REANUDACION=OK` no apareció.
- [x] [PR #132](https://github.com/recm0708/netlab360/pull/132) CI OK fusionada (`78a03738`): HQ/S1/S2 comprueban ens33 IPv4 y rutas propias/defaults protegidas, no exigen rutas ajenas idénticas; no cambia JSON de state ni configuraciones. Seis pruebas de regresión rechazan drift real.
- [x] [PR #133](https://github.com/recm0708/netlab360/pull/133) fusionada: [lotes 135A/B/C](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-135a-135c-reanudacion-y-captura60-20261115.md), sin acciones mutantes.
- [x] Ejecutados 135A (23/23 tests), 135B (tres LACP y regresión multisede) y 135C (13/13 tests y evidencia 60 RC0/RC1 validada). El usuario confirma PNG S05_60 tomado; bytes y SHA-256 del PNG no están auditados.

## Corte verificado 15/11/2026 — 135A/B/C completos, S05_60 obtenida; siguientes 136–138

- [x] **135A**: 23/23 tests aprobados (6 gestión+10 HQ+7 sucursales). La diferencia exacta de gestión es `docker0 172.17.0.0/16`: la ruta antigua tenía `linkdown` y la actual no; IPv4 `ens33=192.168.47.40/24` y ruta predeterminada `.2` iguales, las 3 sedes pasaron protección crítica.
- [x] **135B**: LACP HQ/S1/S2 2/2 en ambos extremos, 4 pings por sitio OK, HA/FIB/VLAN conservados; Faucet OpenFlow conectado 28 reglas, segmentación A/B-C correcta; rutas OSPF HQ→S1 por s1p, HQ→S2 por s2p, seis servicios activos, NTP, Git limpio. `LOTE135B_VMWARE_REANUDACION_COMPLETA=OK`.
- [x] **135C**: 13/13 tests de parser, OpenFlow 31 reglas; A→B `RC0 2/2`, A→C y C→A `RC1, 0 recibidos, 100% pérdida` (10 transmisiones por ARP). `S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO`, `LOTE135C_EVIDENCIA60=OK`. El operador **confirma haber guardado S05_60**; la existencia y SHA-256 del PNG original no se han auditado.
- [x] [PR #134](https://github.com/recm0708/netlab360/pull/134) fusionada (CI success, commit `9925ce62`): script S05 de pérdida/restauración **solo de sdna0** con precheck de ownership, timer restore-only systemd de 120s y pruebas ICMP/OpenFlow/servicios sin tocar ens33/FRR/LACP. [PR #135](https://github.com/recm0708/netlab360/pull/135) fusionada: punto de reanudación actualizado.
- [ ] **Próximas ejecuciones, aún NO realizadas en la VM:** [lotes 136, 137A, 137B y 138](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md): hashes TXT estáticos, precheck, falla/retorno protegida puerto A y regresión. Capturas S05_61 y S05_62 pendientes. No repetir 135 ni fault LACP. La resiliencia de puerto SDN no es HA física/instancia.

## Corte real 15/11/2026 — resiliencia de enlace SDN aceptada (lotes 136–138)

- [x] **Lote 136**: Faucet sigue conectado, 25 reglas OpenFlow, A↔B permitido y C aislado, ens33 `.40/24` GW `.2`, Git limpio. Se verificaron **7/7 registros TXT** por SHA-256 (incluidos 135A/B/C y recuperación anterior). `LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK`.
- [x] **137A**: 9/9 tests de seguridad OK; precheck de ownership/puerto SDN A, OpenFlow conectado, 31 reglas, servicios S02/FRR/NOC/HA preservados; `LOTE137A_PRECHECK_FALLA_SDN=OK`.
- [x] **137B**: watchdog `nl360-s05-sdn-port-a-rescate-68997ee0a7.timer` armado; **solo `sdna0` DOWN**. Ping A→B mostró `10 transmitidos, 0 recibidos, 100% pérdida, RC1`, controlador Faucet siguió conectado; preservación de FRR, NOC, HA comprobada. Restauración `sdna0` solicitada; A↔B volvió en **intento 1**, A↔C/C↔A permanecieron aislados, OpenFlow 31 reglas; watchdog cancelado tras validación, `S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A`. Operador confirma capturas **S05_61 y S05_62** tomadas, pendiente auditoría bytes PNG.
- [x] **138**: SDN OK, 3 LACP 2/2, 4/4 pings por sede, rutas OSPF S1 via s1p y S2 via s2p, seis servicios active, ens33/GW/Git inalterados; `LOTE138_REGRESION_FALLA_SDN=OK`. **3/3 TXT** verificados SHA256.
- [ ] **Pendiente dentro de #23:** comparar técnicamente con bridge Linux/FRR, distinguir la falla probada de `sdna0` de una caída de controlador/equipo, integrarlo con NOC real y auditar/importar PNG originales. **No repetir el fallo SDN, ni los LACP.**
- [ ] **Siguiente paso**: precheck de NOC 9130/exporter 9110 y observador privilegiado root:root instalado; diseñar telemetría real de 3 agregadores y OVS/Faucet con caducidad/UNKNOWN, sin mostrar estado estático como disponibilidad.



---

# ISSUE #6 · [S06] Datos etiquetados y evaluación de diagnóstico IA · estado open

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

# Fase 6 — Analítica inteligente

**Estado: no iniciada como experimento ML evaluado.** La fase1 incluyó estadísticas y diagnóstico determinista por reglas, no un modelo entrenado.

- [x] Perfil estadístico y reglas explicables históricas como baseline de comparación.
- [ ] Construir dataset etiquetado real, auditable, con eventos y partición adecuada por origen/tiempo [#25](https://github.com/recm0708/netlab360/issues/25).
- [ ] Entrenar/evaluar únicamente métodos técnicamente justificables; comparar precisión/recobrado, falsas alarmas y la línea base de reglas [#26](https://github.com/recm0708/netlab360/issues/26).
- [ ] Validar latencias y diferencias entre predicción/recomendación y ejecución real, sin autonomía peligrosa.
- [ ] Capturas `S06_*`, métricas reproducibles, limitaciones y resultados documentados.

**No transferir esta carga** a S01–S03 ni describir el diagnóstico por reglas como modelo ML entrenado. Informe académico único, TAR técnico independiente.


---

# ISSUE #7 · [S07] Integración AIOps y recuperación supervisada extremo a extremo · estado open

## CORTE ACTUAL 15/11/2026 — 144A/B/C COMPLETADOS, desplegar NOC en 145A/B

**En VM (logs reales del usuario):**
- [x] **144A:** seis servicios active (NRestarts=0), dos muestras 4 s apartes: `ha_service.status=running` con `BACKEND_HQ/PRINCIPAL` y `available=true`; monitor S2 1.69 s fresco confirma BACKEND_HQ/S1 running y frontal HQ running, `source_warnings=[]`. FIB S1=`s1p` y S2=`s2p`. La muestra aislada offline de 143B no se reprodujo.
- [x] **144B:** desde cliente S2 VLAN320, HTTP 200 e identidad saludable de backend HQ 10.70.20.21:8088, backend S1 10.71.20.21:8088 y frontal HQ 10.70.20.23:8080 (cabeceras BACKEND_HQ/PRINCIPAL). Cuatro servicios HA active sin reinicios, ens33 y Git intactos. **No hay reparación HTTP HA pendiente por esta auditoría**; no repetir failovers.
- [x] **144C:** root helper instalado permanece en versión legacy root:root 0755, SHA256 `8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad`; sudoers snapshot RC0 y 3 routers/FIB intactos. NOC 9130 corre como usuario rc-aa-ec y sigue sin campos LACP/SDN: **nuevo código GitHub NO instalado todavía**. Repo limpio `70bd06c`, ens33 `192.168.47.40/24`, default GW `192.168.47.2`.
- [x] [PR #141](https://github.com/recm0708/netlab360/pull/141) fusionado en main `cc6f2a67` para acelerar: [corte maestro 144C](https://github.com/recm0708/netlab360/blob/main/docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md), [145A instalar helper root con SHA/backup/rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md), [145B reiniciar SOLO NOC y validar 2 muestras API + rollback](https://github.com/recm0708/netlab360/blob/main/docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md).
- [ ] **145A y 145B aún NO se ejecutaron**; no afirmar despliegue del observador nuevo. Tras 145B=OK, confirmar en navegador y tomar **S05_63_NOC_LACP_Multisede_y_Faucet_Operativos**; no repetir LACP/SDN WAN/HA antes probados ni reiniciar Ubuntu.
- [ ] Después: #32 alcance HA independiente de instancia/equipo (sin confundir con redundancia de enlace), #31 valoración P1/P1B y #105 originales PNG + SHA y cierre S05. S06 ML (#6/#25/#26) y S07 AIOps (#7) siguen pendientes. El informe largo S01–S04 ya existe y **puede ampliarse en paralelo**.


---

# Fase 7 — Integración final de servicios y procesos

**Estado: pendiente de ejecución.** La secuencia prevista no equivale a autonomía certificada.

- [ ] Validar entorno integrador tras completar el núcleo de S04, S05 y S06 con sus propias limitaciones.
- [ ] Construir escenario compuesto de enlaces, rutas, VLAN, dispositivos y servicios con falla segura.
- [ ] Correlacionar telemetría, reglas/modelo, incidencia y ruta de recuperación con registros temporales verificables.
- [ ] Ejecutar `detectar → recomendar → aprobar → actuar → verificar → rollback` con **aprobación humana** antes de cambios operativos.
- [ ] Verificar procedimientos de recuperación, reversión, regresión y acceso administrativo inalterado.
- [ ] Capturas `S07_*`, scripts seguros y resultados en el informe.

**No asumir** remediación autónoma, redundancia física o ausencia de pérdida de paquetes sin pruebas propias. Los entregables finales y demostración están en fase8. TAR externo, sin anexos en Word.
