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
