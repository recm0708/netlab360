# NETLAB360 — Reanudación técnica y documental

**Corte técnico actualizado: 26 de octubre de 2026.** Este es el punto de partida vigente; las bitácoras y commits anteriores se conservan como historial verificable. La documentación utiliza la [voz editorial del proyecto](convenciones/01-redaccion-y-nomenclatura.md).

## Estado de la máquina de laboratorio

- Ubuntu Desktop 26.04.1 LTS sobre VMware Workstation; administración por `ens33=192.168.47.40/24`, puerta de enlace `192.168.47.2`, SSH y Docker activos.
- Los routers, enlaces y namespaces de la **fase 2 quedaron desmontados intencionalmente** después de superar los ensayos y guardar configuraciones, estados históricos y registros. No volver a desplegarlos únicamente para repetir capturas.
- OpenTofu de la fase 3 tiene **17 recursos `terraform_data` de metadatos**, aplicados realmente. Su state se conserva **fuera de Git**, bajo `~/netlab360-bootstrap/iac/s03/work/`; no ejecutar otra vez `tofu apply` ni el preparador del workspace. El segundo plan terminó sin cambios.
- Ansible verificó los ocho costos de FRRouting, detectó la desviación controlada `100→150`, restauró `150→100` y comprobó idempotencia. Las pruebas offline posteriores no representan una nueva alteración de FRR.
- Última regresión registrada en Ubuntu: **29/29** pruebas específicas de la fase 2 y **87/87** pruebas generales, sin cambios administrativos.

## Git y control de cambios

- [PR #49](https://github.com/recm0708/netlab360/pull/49): corrección de rutas portables, fusionado. [CI general](https://github.com/recm0708/netlab360/actions/runs/40233355346) y [CI OpenTofu](https://github.com/recm0708/netlab360/actions/runs/40233355350) completadas satisfactoriamente.
- [PR #50](https://github.com/recm0708/netlab360/pull/50): reorganización de **86 PNG de la fase 1** sin modificar bytes; [CI posterior](https://github.com/recm0708/netlab360/actions/runs/40236374576) satisfactoria.
- [Issue #51](https://github.com/recm0708/netlab360/issues/51): auditoría de 111 capturas cerrada con **21 imágenes aprobadas publicadas** (4 complementarias fase1, 9 finales fase2 y 8 finales fase3), y cuatro preliminares excluidas. La auditoría [se documentó aquí](evidencias/09-auditoria-zip-fases1-2-3-2026-10-25.md).
- [PR #53](https://github.com/recm0708/netlab360/pull/53) fusionado: **107 capturas PNG** en `main` (90/9/8), manifestadas y verificadas por SHA-256. La [regresión GitHub Actions posterior a la fusión](https://github.com/recm0708/netlab360/actions/runs/40241580823) fue satisfactoria. No repetir el importador ni volver a subir las fotografías.
- La administración de GitHub, pull requests, issues y Actions queda centralizada en el mantenimiento del repositorio. Los comandos locales se limitan a operaciones de laboratorio o transferencia controlada de archivos, sin requerir revisión manual de PR en navegador.

## Limpieza de ramas e issues — 25/10/2026

- [Limpieza controlada de ramas fusionadas](https://github.com/recm0708/netlab360/actions/runs/40242595670) terminada con resultado SUCCESS: cinco ramas eliminadas tras comprobar PR y SHA; **única rama permanente `main`**.
- Se retiró el workflow temporal y se instaló `.github/workflows/limpiar-rama-tras-merge.yml` para que, en futuros PR fusionados, la rama de origen se elimine después de comprobar que sigue apuntando al SHA incluido en el merge.
- Se cerraron por alcance técnico verificado las issues #10, #11, #12, #13, #14, #18, #19 y #30. Se consolidaron #9→#36 y #37→#29, sin perder sus pendientes futuros.
- La **issue #2 de fase 2 se cerró** tras validar técnica y documentalmente el borrador académico 3.2 (94 páginas). Permanecen abiertas #1 (fundamentos/SSH) y #3 (formalización SoT/alcance OpenTofu). Las funciones de NOC S04, LACP S05 y entrega S08 dejaron de figurar como exigencias del cierre funcional de S02.
- [Puertas de cierre S01–S03](control/07-puertas-cierre-fases1-a-3-2026-10-25.md): **S01** requiere verificación/decisión SSH y compatibilidad fundacional; **S02 CERRADA** con Figura 1 y validación documental del escrito 3.2; **S03** tiene escritura comprobada en 5.5/6/7/8, pendiente únicamente de formalización SoT `candidate` y alcance externo OpenTofu. No repetir pruebas completas para completar capturas.

## Antecedente: preparación de la fase 4 — 26/10/2026

- [Issue #4](https://github.com/recm0708/netlab360/issues/4): inicio de S04 registrado; **sin ejecución de VM ni despliegue nuevo confirmado todavía**.
- Se verificó en el código que el exporter vivo B3 usa los contenedores **dos routers** `nl360-b2-r-hq`/`nl360-b2-r-s1` e interfaces `wan-p`/`wan-b`, mientras que S02 usa **tres routers**, cuatro WAN y nueve VLAN. La reutilización requiere adaptación y pruebas de telemetría fresca por sede.
- Primer procedimiento al arrancar Ubuntu: verificar hostname, `ens33`/gateway, Git, Docker/netns y puertos 8765/9108/9090. **No** iniciar servicios, desplegar S02, cambiar SSH o ejecutar OpenTofu hasta confirmar el preflight.

## Antecedente: primer incremento S04 tras auditoría de Ubuntu — 26/10/2026

- El 26/10 a las 21:10 (UTC−05) se comprobó Ubuntu 26.04.1, `ens33 192.168.47.40/24` y GW `.2`, SSH/Docker/VMware Tools activos; 0 contenedores, 0 netns, puertos `8765/9090/9108` libres; binarios Prometheus 3.7.0 disponibles y state OpenTofu externo presente.
- La sincronización de Ubuntu a `cc76800` terminó con código 0; árbol Git limpio. Sintaxis Python 3/3, `promtool check config` y `promtool check rules` (tres reglas) terminaron correctamente. SoT S03 `candidate` conserva 3 routers, 9 VLAN y 8 extremos de 4 WAN.
- [PR #55](https://github.com/recm0708/netlab360/pull/55), fusionado como `5848287`: `servicios/observabilidad/s04_exporter_multisede.py`, `tests/test_s04_exporter_multisede.py`, `README-S04.md` y workflow de pruebas offline. [CI de S04 en main](https://github.com/recm0708/netlab360/actions/runs/40438597012) y [regresión general en main](https://github.com/recm0708/netlab360/actions/runs/40438597219) SUCCESS. La rama del PR fue eliminada automáticamente.
- **Todavía no se ha ejecutado el colector S04 en Ubuntu real**. La próxima tarea es `git pull --ff-only origin main`, pruebas offline, `--check` y `--once` con `sudo -v`; el resultado real esperado con S02 desmontada es `topology=offline` y `source_ok=true`. El nuevo puerto `9110` solo se usará en una siguiente etapa y únicamente en loopback.
- **No confundir:** `active` significa tres contenedores presentes, no OSPF Full ni servicio HTTP validado. El antiguo exporter B3 y sus reglas para `wan-p`/`wan-b` no se alteraron. Pendientes NOC, Prometheus S04, incidentes, SLI/SLO y capturas `S04_*`.

## Observabilidad S04 — Ensayo real y panel NOC (26/10/2026)

- Terminal A: colector S04 `127.0.0.1:9110` con `source_ok=true`, `topology=offline` y 25 series de métricas; tres routers, ocho extremos WAN, nueve VLAN; edad observada 3,86 s.
- Terminal B: Prometheus 3.7.0 `127.0.0.1:9091`, reglas 4/4 y escenarios `promtool test rules` satisfactorios, `scrape_up=1`, `source_up=1`, `topology_offline=1`, cero alertas WAN/VLAN y cero activas. `ens33=192.168.47.40/24` y GW `.2` intactas. Sin Docker ni netns residuales.
- Capturas `S04_01_API_Telemetria_Real_Tres_Sedes_Offline` y `S04_02_Prometheus_Scrape_Real_Sin_Falsas_Alertas`: **confirmadas tomadas**, pendientes de recibir PNG, inspección visual, SHA256 y publicación.
- Al terminar la salida recibida, las terminales A/B seguían ejecutando colector y Prometheus; **no se ha certificado su detención**. No reiniciarlas sin comprobar estado.
- [PR #57](https://github.com/recm0708/netlab360/pull/57) fusionado como `dcc5c6ce` con panel NOC S04 `servicios/noc-s04/app.py` (puerto `127.0.0.1:9120`), vistas central/HQ/S1/S2, agregación del colector y Prometheus, estado UNKNOWN ante muestras antiguas o fuentes inaccesibles. **20 pruebas S04 offline** y [CI S04 `main`](https://github.com/recm0708/netlab360/actions/runs/40443847932) y [regresión general](https://github.com/recm0708/netlab360/actions/runs/40443847941) SUCCESS. La [autolimpieza de rama](https://github.com/recm0708/netlab360/actions/runs/40443848768) también fue satisfactoria.
- **Siguiente prueba**: NOC real `--check`, `--once`, `--serve` y verificación HTTP desde Ubuntu; visita visual por túnel SSH Windows y capturas `S04_03` / `S04_04` / opcional `S04_05`. No afirmar aún observabilidad de enlaces WAN **desplegados** ni NOC definitivamente aceptado.

## Auditoría visual y cierre limpio de NOC S04 — 26/10/2026, ~22:29

- Se recibieron **siete PNG correspondientes a seis identificadores S04_01–06** (S04_03 está dividida en dos vistas). Todas las imágenes se inspeccionaron y se aceptaron para el escenario real **offline**; [registro completo con SHA-256](https://github.com/recm0708/netlab360/issues/4#issuecomment-6433141415). **PNG aún pendientes de transferir/publicar en Git**, por lo cual no modificar el total de 107 capturas versionadas de S01–S03.
- `S04_01`: exporter S04 tres sedes, 8 extremos WAN, 9 VLAN y 25 series, muestra fresca; `S04_02`: Prometheus target UP, fuente 1, offline 1 y cero falsas alarmas; `S04_03` (2 PNG): NOC central con tarjetas de tres sedes y bloque de cero alertas; `S04_04`: selección S1, dos WAN/tres VLAN; `S04_05`: API agregada con `S04_05_VERIFICACION=OK`; `S04_06`: puertos 9091/9110/9120 libres, Docker/netns vacíos, red administrativa intacta, Git main limpio.
- Las terminales documentaron **20/20 pruebas S04 offline**, preflight NOC 0, vista real `offline` y Prometheus `scrape=up`. Se verificó la parada normal de NOC (`S04_NOC_DETENIDO=SI`), Prometheus (apagado ordenado) y exporter (`S04_EXPORTER_DETENIDO=SI`). La VM puede quedar apagada normalmente después de decidir si se continúa con ensayos WAN activas.
- Se preparó un ZIP de traslado con **siete PNG originales sin alteración** y un manifiesto SHA-256; el paso siguiente es transferirlo al clon Ubuntu y publicarlo tras cotejar hashes. No repetir capturas, no reconstruir S02 todavía y no ejecutar `tofu apply`.
- La fase 4 **permanece ABIERTA** para topología desplegada, estados WAN/OSPF/HTTP, alertas `firing/resolved` reales, eventos persistentes, SLI/SLO y decisiones de notificación.

## Último corte verificado: lote S04 importado, publicación Git pendiente — 26/10/2026

- La importación en Ubuntu comenzó desde `main` en **`c6ec108`**, árbol limpio. El ZIP `NETLAB360_S04_LOTE01_7PNG_AUDITADOS_2026-10-26.zip` fue transferido al HOME y verificado contra `MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv`. La salida REAL confirmó **7 líneas `S04_SHA256_OK`**, `S04_CAPTURAS_VERIFICADAS=7`, `S04_MANIFIESTO_VERIFICADO=SI`, `S04_IMPORTACION_RESULTADO=0`.
- `git status --short` mostró **8 archivos `??`** (7 PNG `S04_01` a `S04_06`, con dos partes de S04_03, y CSV del manifiesto). **Todavía no hay commit ni push remotos acreditados**. Primero ejecutar `git pull --ff-only origin main` para traer documentación actualizada, abrir rama única de evidencias, agregar únicamente esos ocho archivos, revisar staged, `git commit` y `git push -u origin feat/s04-evidencias-lote01`; aprobar PR solo tras cotejar lista/hash. No hacer `git clean`, no borrar ZIP ni añadir secretos o estados externos.
- El archivo [`docs/sesiones/2026-10-26-s04-noc-multisede-offline.md`](sesiones/2026-10-26-s04-noc-multisede-offline.md) documenta todos los resultados reales de las terminales, las pruebas 20/20, las capturas visuales y los límites del escenario offline. [`docs/operaciones/s04-cierre-observabilidad-multisede.md`](operaciones/s04-cierre-observabilidad-multisede.md) fija las puertas G0–G6 y orden protegido para desplegar WAN/LAN y terminar la fase. [Guion académico S04](academico/s04-guion-de-actualizacion-del-informe.md) preparado para redactar implementación, pruebas y análisis sin inventar resultados. [Tablero general](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) actualizado: S02 cerrada, S03 pendiente de alcance, S04 aceptación parcial.
- **Próximo trabajo técnico, después de publicar capturas y quedar `main` limpia:** prechecks de solo lectura; verificar snapshot VMware de `netlab360-lab` antes de permitir `--snapshot-confirmado`; despliegue protegido routers FRR→4 WAN→OSPF→LAN (9 VLAN), exporter→Prometheus→NOC, incidente WAN primario con *rollback*, captura firing/resolved y postcheck. La fase 4 NO está cerrada. No repetir `tofu apply`.
- **Escrito académico:** último borrador revisado es `1457-Proyecto Semestral_borrador3.2.pdf` (94 págs.), fases 1–3 incorporadas; falta ampliar el informe con fase 4 solo después de tener pruebas con WAN desplegadas. El informe no lleva anexos; TAR es independiente.
- **Seguridad y estado físico actual:** tras las pruebas NOC S04 quedaron libres los puertos 9091/9110/9120, sin contenedores ni netns, `ens33 192.168.47.40/24` y gateway `192.168.47.2`. El host no ejecuta NOC/Prometheus/exporter por defecto al reanudar.

## ACTUALIZACIÓN MÁS RECIENTE — 26/10/2026 22:52 y snapshot S04

- **Evidencias S04 ya PUBLICADAS.** [PR #58](https://github.com/recm0708/netlab360/pull/58) fusionado (`4babb2849`); rama temporal remota eliminada. Confirmado con árbol remoto GitHub: **114 PNG = 90 S01 + 9 S02 + 8 S03 + 7 S04**. El manifiesto CSV fue normalizado CRLF→LF exclusivamente; los 7 PNG son idénticos. [Catálogo S04](../evidencias/capturas/fase4/README.md) y [manifiesto](../evidencias/manifiestos/MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv).
- **Precheck de S04 para red activa, ejecutado realmente**: `S02_PRECHECK_RESULTADO=0`, `RESULTADO_PRECHECK_S02=0`, `RESULTADO_PLAN_WAN=0`, `RESULTADO_PLAN_LAN=0`; ningún contenedor, ningún netns, ningún state WAN/LAN residual; runtimes de R-HQ/R-S1/R-S2 presentes; 3 sedes, 4 WAN, 9 VLAN, 0 colisiones Docker/host. `ens33=192.168.47.40/24`, GW `.2`; 133 GiB libres de disco y ~13 GiB de RAM disponible.
- **Snapshot VMware confirmado por el operador**: creó una instantánea de la VM identificada como S04 y eliminó las dos instantáneas anteriores. En este corte solo queda la nueva instantánea como punto de retorno conocido; no se ha comprobado restauración.
- **Importante: clon Ubuntu quedó en la rama local `feat/s04-evidencias-lote01`**, commit `ce0217e`, aunque GitHub ya fusionó una corrección CRLF y cerró la rama remota. **PRÓXIMO COMANDO antes de arranque**: `git switch main` (árbol limpio) y `git pull --ff-only origin main`; comprobar `main` limpia. No borrar la rama local a la fuerza ni hacer reset/clean.
- **S04 infraestructura ACTIVA aún NO ejecutada.** Continuar secuencia con protecciones: `sudo -v`, `bash scripts/laboratorio/s02-routers-start.sh`; comprobar 3 routers; `python3 scripts/laboratorio/s02-wan-links.py precheck`, `up --snapshot-confirmado`, `validar-ospf-s02.py`; después `s02-lan-vlan.py precheck/up --snapshot-confirmado` y `validar-lan-s02.py`. Detenerse ante fallo, conservar state y logs. Snapshot confirma disponibilidad del checkpoint, **no** ejecuta backup automáticamente.
- El cierre S04 requiere pruebas de observabilidad con WAN/VLAN en funcionamiento, alertas reales de caída/restauración, persistencia, SLI/SLO o decisión explícita de alcance, nuevas capturas, desmontaje seguro e integración en informe académico 3.2. No tocar state OpenTofu.

## Indicadores de avance

| Fase | Corte actual | Pendiente para aceptación |
|---|---:|---|
| 1 | 72 % histórico | Decidir el cierre administrativo de la línea base sin atribuir las fases posteriores a esta fase |
| 2 | **Cerrada** | Pruebas y documentación aceptadas internamente; issue #2 cerrada |
| 3 | Técnicamente documentada | SoT `candidate` (#16) y data sources/ownership externo OpenTofu (#17) por decidir; informe 3.2 validado |
| 4–8 | 0 % de aceptación formal | Implementación, pruebas y entregables propios de cada fase |

[Tablero completo de criterios](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md). Las funciones experimentales de fases previas no se contabilizan como aceptación formal de fases posteriores.

## Informe académico y entregables

- Última exportación revisada: `1457-Proyecto Semestral_borrador3.2.pdf`, **94 páginas**. Las fases 1–3 se encuentran desarrolladas; la fase 2 está cerrada internamente. Queda pulido editorial general (coma desplazada pág. 7, sangría de 6.5 en índice pág. 5, espaciado de notas Figuras 12–15/Tabla 12, notas separadas de Figuras 1/5/7 y de Tabla 12), registrado en #27; fase 3 pendiente de definición de SoT y OpenTofu externo, no de pruebas adicionales.
- La **Figura 1** ya está insertada y las referencias a anexos fueron corregidas. No modificar las 15 figuras ni repetir las capturas; aplicar exclusivamente el pulido editorial pendiente en Word.
- Según la modalidad docente registrada, la entrega académica termina en **Referencias**, **sin capítulo de anexos**. El código, YAML/JSON, pruebas y evidencias seleccionadas se entregarán en un **archivo `.tar` externo**.
- Revisiones docentes: 30/10 (introducción, objetivos y planteamiento) y 13/11 (fundamento y diseño). Confirmar sus resultados reales antes de registrar aprobación.
- No incluir credenciales, claves SSH privadas, planes/state OpenTofu o archivos de clase en el TAR.

## Siguiente secuencia

1. Mantener la rama única `main`, el inventario de **107 capturas** y los manifiestos SHA-256 ya verificados.
2. Resolver la aceptación fundacional de la fase 1 sin alterar FRRouting: SSH seguro con rollback y notas de compatibilidad.
3. Mantener fase 2 cerrada y sus pruebas intactas; mejorar los tres detalles tipográficos transversales de #27 cuando se exporte el siguiente PDF.
4. Formalizar el contrato SoT `candidate` y decidir si el objetivo de data sources/ownership externo de OpenTofu se amplía, excluye o difiere; dejar constancia antes de cerrar fase 3.
5. Comenzar S04 mediante **preflight de solo lectura**; el exporter histórico B3 apunta a dos routers `nl360-b2-*` y no es compatible directamente con la topología S02 de tres routers `nl360-s02-*`. No desplegar S02 por fotografía.
6. Preparar el corte académico del 30/10 y continuar las fases 4–8 según sus hitos.

**Conservación histórica:** las sesiones detalladas permanecen en [`docs/sesiones/`](sesiones/), las decisiones en [`docs/academico/`](academico/) y los resultados de auditoría en [`docs/evidencias/`](evidencias/). Los registros cronológicos anteriores también son recuperables mediante el historial Git, sin duplicarlos en este punto de reanudación.

## Corte operativo posterior — S04 WAN activa (26/10/2026, ~23:48)

- **NUEVO último estado de Ubuntu:** `main` sincronizada a `d1aa854`, árbol local limpio, siete PNG S04 ya incluidos; SSH alternativo desde Windows comprobado (un intento fallido de contraseña seguido de acceso satisfactorio).
- **Infraestructura efectivamente desplegada:** 3/3 routers FRR aislados, 4/4 WAN, loopbacks HQ/S1/S2, OSPF FULL HQ=4/S1=2/S2=2, FIB preferente 6/6 y pings loopback 6/6. Resultado del usuario `S04_G1_WAN_OSPF=OK`; `ens33=192.168.47.40/24` y GW `192.168.47.2` sin cambios. [Bitácora detallada](sesiones/2026-10-26-s04-wan-ospf-activa.md).
- **NO desmontar routers ni WAN.** El próximo paso es `s02-lan-vlan.py precheck`, luego `up --snapshot-confirmado`, validador de 9 gateways/6 ICMP, `status` y postcheck de gestión. La instantánea VMware S04 fue confirmada por el operador, sin prueba de restauración. Si falla un paso, conservar state y diagnosticar sin cleanup global.
- **G1 parcial:** la WAN/OSPF está probada; LAN/VLAN todavía no. Exporter/Prometheus/NOC S04 aún no se han reactivado sobre esta topología; no anunciar alertas reales ni cerrar G1–G6 todavía.
- **Cierres independientes:** S01 permanece abierta con 72 % histórico hasta resolver SSH #38, compatibilidad #34 y aceptación documental; S03 ~90 % hasta contrato SoT #16 y decisión/implementación acotada OpenTofu externo #17. El avance S04 no cambia automáticamente esos indicadores. S02 sigue cerrada.

## Seguimiento más reciente — S04 G1 completada, G2 colector muestreado (26/10/2026, 23:58:53)

- **La topología sigue ACTIVADA**, no desmontada. G1 completa sobre red real: 3/3 FRR, 4/4 WAN, OSPF FULL 4/2/2, 6/6 FIB, 6/6 ICMP loopback; LAN 3 switches, 9 VLAN/9 hosts, gateways 9/9 e ICMP LAN inter-VLAN 6/6. `S04_G1_LAN_VALIDADA=OK`, `ens33=192.168.47.40/24` y GW `192.168.47.2` intactos.
- **Muestra S04 `--once` sobre topología activa**, `source_ok=true`, `topology=active`, `errors=[]`, routers 3/3, ocho extremos WAN y nueve VLAN con `admin_up=1`. No atribuir al colector prueba de OSPF ni HTTP. [Bitácora G1 LAN/G2 inicial](sesiones/2026-10-26-s04-g1-lan-y-muestra-activa.md).
- **Pendiente inmediato:** mantener S02 routers/WAN/LAN encendidos; desplegar *exporter* 9110, Prometheus 9091 y NOC 9120 en terminales diferentes; validar G2 con datos recientes y capturas S04_07–S04_09. Ninguna imagen nueva certificada todavía. Después evaluar G3 incidente y G4–G6 de manera individual.
- **Política de dependencias ratificada por el operador:** continuar S04→S08 aunque S01 y S03 conserven pendientes reales. Revaluar sus criterios conforme avanzan las fases y cerrarlas cuando haya pruebas o decisiones de alcance respaldadas; no adelantar una aceptación ni modificar porcentajes por asociación indirecta. Se puede resolver S01/S03 en un corte documental/operativo posterior sin bloquear S05.

## Último seguimiento — 27/10/2026 00:10–00:15 (S04 G2 pruebas funcionales OK)

- **Servicios activos sobre WAN/LAN real:** exporter `127.0.0.1:9110`, Prometheus 3.7.0 `127.0.0.1:9091`, NOC `127.0.0.1:9120`. `S04_G2_PRECHECK=OK`: 3 FRR, 12 netns y gestión `ens33` intacta. No detener servicios ni topología antes de G3.
- **Resultado real G2:** exporter 25 series y muestra 3.21 s, routers 3/3, WAN 8/8 y VLAN 9/9 administrativamente UP; Prometheus target UP, fuente 1, alertas 0 y 4 reglas comprobadas; NOC agregado frescura 1.86 s, tres sedes, `scrape=up`, 0 alertas. Marcadores `S04_G2_EXPORTER=OK`, `S04_G2_PROMETHEUS=OK`, `S04_G2_NOC=OK`. [Bitácora G2](sesiones/2026-10-27-s04-g2-servicios-activos.md).
- **Evidencia pendiente:** confirmar capturas `S04_07` y `S04_08`, establecer túnel interactivo SSH para visualizar NOC en navegador Windows y tomar `S04_09`; aún no hay nuevas PNG publicadas. El túnel previo estaba en autenticación y no acredita navegador.
- **Terminales simplificadas a cuatro:** Term2 exporter, Term3 Prometheus, Term4 NOC y Term1 consola de operaciones con `ssh -L 9120:127.0.0.1:9120 netlab360`. Cerrar Term5 y Term6 duplicadas antes de reabrir el túnel, sin interferir con Term2–4.
- **Siguiente puerta G3:** revisar temporización `WANAdminDown for:6s` y ciclo de corte/restauración seguro antes de inducir una falla. No registrar incidente `firing/resolved` hasta observarlo de verdad. G4–G6 pendientes.

## Nuevo corte 27/10/2026 — G2 fotografiada; G3 preparada, no ejecutada

- El usuario confirma S04_07, S04_08 y S04_09 tomadas; PNG aún sin auditoría de archivos ni publicación remota. El contador Git permanece en 114 PNG (S04=7).
- [PR #62](https://github.com/recm0708/netlab360/pull/62) fusionado (commit 0bc47c9) con nueva herramienta scripts/observabilidad/s04-incidente-wan.py, 5 pruebas offline y CI [SUCCESS](https://github.com/recm0708/netlab360/actions/runs/40457448149). El validador de capturas reconoce los manifiestos S04-S08 y comprueba SHA-256, bytes y dimensiones.
- [Guía G3](operaciones/s04-g3-incidente-wan-controlado.md) indica precheck, corte aislado HQ/s1p por 32 segundos, observación pending/firing, backup s1b y restauración protegida. NO se ha ejecutado todavía el corte.
- La topología G1 y los servicios G2 deben permanecer activos: FRR 3, WAN 4, VLAN 9, exporter 9110, Prometheus 9091, NOC 9120. Terminal 1 se usa para validaciones.
- Próximo paso: sincronizar main limpia en Ubuntu, compilar el script, ejecutar tests G3 y validador de capturas, luego ejecutar python3 scripts/observabilidad/s04-incidente-wan.py --check. Revisar salida antes de ejecutar --execute --snapshot-confirmado. S01 y S03 permanecen abiertas sin bloquear S04-S08.

## Último corte — 27/10/2026, 01:06:18 (S04 G3 REAL completada)

- **G3 validada en producción de laboratorio:** HQ/s1p DOWN 06:05:04Z → Prometheus pending 06:05:07Z → firing 06:05:13Z, visible desde NOC; respaldo S1 en s1b (ambas direcciones), S2 estable en s2p, ICMP correcto; HQ/s1p UP 06:06:07Z, retorno a s1p y alarma ausente de activas 06:06:18Z. Marcadores `S04_G3_RESULTADO=OK`, `S04_G3_EJECUCION_COMPLETA=OK`. [Bitácora de G3](sesiones/2026-10-27-s04-g3-incidente-real-y-recuperacion.md).
- **Capturas recibidas y auditadas en esta sesión:** lote S04 02 consta de 8 PNG originales (`S04_07`, `S04_08`, `S04_09` ×4, `S04_10`, `S04_11`). ZIP/CSV SHA-256 preparados para importar al repositorio, **no se han publicado**. Inventario remoto aún **114 PNG**; sería **122** tras la publicación del lote.
- **Servicios y red presumiblemente activos al finalizar G3:** se registró gestión intacta, rutas principales restauradas y fuente fresca. **Próximo paso postcheck read-only** de OSPF/FIB, LAN, exporter, Prometheus y NOC antes de asumir nuevas pruebas G4. Conservar Term1 operaciones y Term2/3/4 procesos, sin desmontar WAN/LAN.
- **Roadmap nuevo**: historial mínimo durable y vista por sede desde G4/G5 S04 (issue #21); diagrama gráfico animado en S05 (issue #64), colores por estado observado, respaldo distinguible y animaciones solo con tráfico medido. En S06 y S07 se amplía diagnóstico/integración, no adelantar esos hitos.

## G4 TSDB confirmada después de restart — 27/10/2026 (1:54 hora Panamá)

- El operador aportó salidas reales de Terminales 1–4. `main` sincronizada hasta `2b6689f` y 7/7 pruebas TSDB aprobadas. Baseline histórica de Prometheus `startTime=2026-10-27T05:11:42.574438879Z` contenía 68 puntos WAN HQ/s1p y 28 `ALERTS firing`.
- Se **reinició exclusivamente Prometheus S04** en Terminal 3, escuchando en 127.0.0.1:9091; recuperó bloques TSDB y WAL. Nuevo startTime `2026-10-27T06:54:31.491762152Z`; **68/68 WAN y 28/28 alertas idénticas**, `S04_G4_PERSISTENCIA_TSDB=OK`. NOC `active`/`fresh`, `scrape=up`, alertas actuales 0, `S04_G4_POSTREINICIO=OK`.
- Evidencias originales fuera de Git: `~/netlab360-bootstrap/s04/evidencias/S04_G4_TSDB_Antes_Reinicio.json` SHA256 `fb9ac6d761a7e8b5cf39df9d955b9171689c1d94746cd0238c2050209dcec095`; `S04_G4_TSDB_Despues_Reinicio.json` SHA256 `1e1be26c09e299f0488a5e773ff28a5989556860535b1f9f937322bbdfc200bf`. [Bitácora detallada](sesiones/2026-10-27-s04-g4-tsdb-persistente-tras-reinicio.md).
- **G4 sigue abierta parcialmente:** falta ensayo real fuente `UNKNOWN`, historial durable y vista NOC de incidentes. G5 indicadores/alcance avisos y G6 cierre documental pendientes. Captura `S04_12_Historico_Prometheus_G3_Persistente_Tras_Reinicio` reservada, aún sin confirmación de guardado. Repositorio ya tiene 122 PNG (15 S04), con CI específica verificada. Mantener 3 procesos y WAN/LAN activos para siguiente ensayo.

## Estado más reciente — 27/10/2026: S04 G4 cerrada, G5 en curso

- Usuario confirmó **G4 CERRADA TÉCNICAMENTE**: segundo reinicio solo NOC, PID 248883→263894, 3/3 eventos SQLite G3 idénticos, `S04_G4_SQLITE_PERSISTENCIA=OK`, `S04_G4_CIERRE_TECNICO=OK`, NOC active/scrape up. Previamente TSDB 68/68 WAN y 28/28 firing tras restart Prometheus, UNKNOWN sin falsas WAN/VLAN y recuperación de exporter.
- G5 baseline 15m a 07:41:31Z: `396/396` scrapes y `396/396` muestras de fuente con valor 1; ambos 100% **entre muestras registradas**, no disponibilidad final. Herramienta SLI y SLO 99% propuesto, no aprobado. [Metodología](operaciones/s04-g5-sli-slo-alcance-observabilidad.md).
- **G6:** S04_13, S04_14 y S04_15 reportadas tomadas; S04_12/S04_16 no confirmadas. GitHub 122 PNG; no atribuir publicación a archivos aún no recibidos. Term1 operativa; Term2 exporter 9110; Term3 Prometheus 9091; Term4 NOC 9120. FRR/WAN/LAN activos.

## Corte 27/10/2026 — G5 medida 15 y 60 minutos, G6 siete PNG localizadas

- Operador validó en Ubuntu `main=ee1eb22`, seis pruebas nuevas G5 y ocho del historial SQLite, NOC `active`, Prometheus `up`, G3 3/3 eventos. **15 min:** scrape 450/450 (100 %), fuente condicional 450/450 (100 %), presupuesto 99 % propuesto 4 fallos. **60 min:** scrape 1698/1740 (**97.586 %**), 42 fallos, presupuesto 17, remanente **−25**, **incumplimiento de propuesta 99 %**; fuente condicional 1698/1698 (100 % entre muestras existentes). No confundir fuente condicional con scrape ni disponibilidad de red. El objetivo es una propuesta aún no aprobada; [bitácora completa](sesiones/2026-10-27-s04-g5-mediciones-15m-60m-y-g6-inventario.md).
- Respaldo SQLite por API `backup`, íntegro y 3/3 eventos G3, ruta `~/netlab360-bootstrap/s04/evidencias/S04_G6_Respaldo_Historial_20261027T075205880317Z.sqlite3`, SHA256 `23f1db998a3e9b4811507e3f7b50d063d76e5e3971931acb491683c120f8d820`, fuera de Git.
- PowerShell confirmó físicamente **7 PNG S04_12–17** en Windows (S04_15 tiene 2 partes). Falta empaquetar/transferir/auditar 7 PNG y publicar manifiesto LOTE03. GitHub todavía 122 PNG (S04 15); meta tras PR 129 (S04 22). Capturas que antes figuraban no confirmadas ahora se localizaron como archivos; **contenido visual aún no auditado**.
- **Estado:** G0–G4 técnicamente cerradas; G5 SLI calculados, SLO candidato 99 % incumplido en 60m y no aprobado; G6 escrito/manifestación/postcheck por completar. Conservar Term1 operativa, Term2 exporter 9110, Term3 Prometheus 9091, Term4 NOC 9120 y red FRR/WAN/LAN activa. No repetir falla WAN G3.


## Corte 27/10/2026 — G6 evidencia publicada / G5 decisión pendiente

- [PR #75](https://github.com/recm0708/netlab360/pull/75) **fusionado**, commit `0f8e943f`, CI integridad SUCCESS tanto PR (40471188245) como main (40471266913). Inventario remoto **129 PNG** (S01 90, S02 9, S03 8, S04 **22**), tres manifiestos S04 7+8+7. En Ubuntu SHA origen Windows y dimensiones 7/7, inventario global y tests OK.
- G6 regresión final real **`S04_G6_POSTCHECK=OK`**: FRR OSPF FULL 4/2/2, FIB primaria 6/6, loopbacks 6/6, VLAN gateways 9/9, LAN 6/6, exporter `active_fresh`, Prometheus `up`, NOC `active`, cero alertas actuales, tres eventos G3 históricos, gestión `ens33=192.168.47.40/24` GW `.2` preservada.
- **No declarar S04 terminada académicamente:** G5 SLO 99 % sigue **candidato**, ventana 60m 97.586 % con remanente −25; notificaciones externas NO implantadas (solo visuales/locales). Falta ratificar el alcance y editar secciones 5–8 del informe único, revisión visual de figuras; issue #47 reunión 30/10 por celebrarse. [Propuesta G5](operaciones/s04-g5-decision-medida-notificaciones-locales.md) y [matriz G6](operaciones/s04-g6-matriz-aceptacion-evidencias-2026-10-27.md).
- Conservar Term1 operativa, exporter 9110 Term2, Prometheus 9091 Term3, NOC 9120 Term4 y FRR/WAN/LAN activos; **no** repetir G3 ni desmontar hasta definir próxima fase. La visualización topológica animada es futura S05 #64.
