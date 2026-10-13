# NETLAB360 — REANUDAR AQUÍ (checkpoint operativo)

## ACTUALIZACIÓN PRIORITARIA — 13/10/2026 (DESPUÉS DE 15:52) | LOTE 01 DE 19 PNG AUDITADO; API B3 PROBADA, POSTCHECK PENDIENTE

**ESTA SECCIÓN PREVALECE SOBRE LAS MENCIONES HISTÓRICAS "CAPTURAS SUPUESTAS" EN DOCUMENTOS ANTERIORES.**
- **Lote 01 de 19 capturas B1/B2:** archivos **realmente recibidos e inspeccionados visualmente**. Hay registro oficial con nombres canónicos, clasificación de éxito/diagnóstico, observaciones y 19 SHA256 en [`docs/evidencias/01-auditoria-visual-b1-b2-2026-10-13.md`](evidencias/01-auditoria-visual-b1-b2-2026-10-13.md). La issue #43 está actualizada; sigue ABIERTA para otros lotes e importación de bytes PNG al repositorio. Los **PNG aún NO están físicamente subidos al repo**, pero se preparó un ZIP con los 19 sin alterar sus píxeles, los nombres normalizados, manifiesto CSV y registro. SHA256 ZIP `a81a6ceaf8daace88f740d288327231ea6818bac80241d0017d5ca32438bef66`. En el ZIP `B2_06_Arranque_FRR_V2_Exitoso.png` → `B2_06_Diagnostico_FRR_V2_Permisos.png` (resultado original smoke v2=2) y `B2_16_Diagnostico_Convergencia.png` → `B2_16_Medicion_Continua_Convergencia.png` (76/76 muestras y cleanup OK). B2_L2_01, B2_15, B2_16 tienen notas de encuadre; NO repetir ensayo solo por ese detalle.
- **B3 API realmente probada** por usuario (salida de 3 terminales a 15:48–15:52): `B3_SINTAXIS: OK`, `--check` código0 y 76 muestras, `python3 servicios/noc-historico/app.py --serve` escuchó en `127.0.0.1:8765`. `GET /healthz`, `GET /api/v1/baseline`, `GET /metrics`, `GET /` todos **200**, URL inexistente **404**, POST **405**. `/healthz` dice `historical`, `live_monitoring:false`; no confundir con exporter actual, Prometheus desplegado, dashboard de incidente real ni alarma. [Bitácora](sesiones/2026-10-13-b3-api-noc-historico-probada.md). Túnel `ssh -N -L 8765:127.0.0.1:8765 netlab360` iniciado, **imagen de navegador B3_03 todavía NO enviada para validación visual**.
- **PENDIENTE OPERATIVO INMEDIATO:** La salida de B3_04 a las 15:52:24 mostraba **`PUERTO_8765_LIBRE: NO`**, sin salida de Ctrl+C ni `B3_SERVIDOR_DETENIDO=SI`. Detener túnel PowerShell (Ctrl+C), detener Python en Terminal SSH 1 (Ctrl+C), verificar con `ss -H -ltn '( sport = :8765 )'` que puerto no quede ocupado. NO cerrar el postcheck B3 antes de salida de `PUERTO_8765_LIBRE: SI`; no matar procesos ajenos.
- **S01 ~43% provisional**, pendiente de reevaluación tras cierre, evidencia visual de UI y siguientes controles B3; issues #1, #12, #15, #20, #21, #35, #42, #43 ABIERTAS. Git local verificado en `07c2731` **antes de nuevos commits remotos de auditoría**. Hace falta `git pull --ff-only origin main` cuando no haya cambios locales; no repetir smoke FRR/OSPF/ICMP de B2.
- **Próxima incorporación de PNG:** transferir ZIP desde el chat a Windows y Ubuntu, verificar SHA256, extraer en carpeta de evidencias dentro de repositorio, `git add/commit/push` solo tras inspección. No afirmar subida GitHub sin verificar commit real. El usuario enviará las capturas restantes para auditar una segunda tanda; no volver a cuestionar la existencia de las 19 del lote 01.

---


## PUNTO DE REANUDACIÓN ACTUAL — 2026-10-13 15:29 PANAMÁ | B3-01 DATOS OK; API NOC NO PROBADA

**PREVALECE SOBRE LOS REGISTROS DE LAS 11:52 O ANTERIORES:** el usuario volvió a encender `NETLAB360-Ubuntu-Desktop`; SSH `netlab360-lab` OK, Ubuntu 26.04.1 kernel 7.0.0-38; `ens33 UP 192.168.47.40/24`, GW `192.168.47.2` inalterados; servicios docker/ssh/open-vm-tools activos, Docker/netns vacíos; raíz 9% ocupada, memoria disponible 13Gi; APT upgrade/autoclean 0 paquetes, dpkg audit limpio, no reboot. `git pull --ff-only` a `c53f0a6`, estado Git limpio/sincronizado **ANTES DE LOS NUEVOS COMMITS DE ESTA RESPUESTA**.

**B3-01 RESULTADO REAL COMPROBADO:** CSV de `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.csv` existe, **76 filas/76 recibidas/0 pérdidas**, `CSV_INTEGRIDAD: OK`. Se ejecutó el generador de línea base y dio **`B3_ANALISIS_RETROSPECTIVO=OK`**; produjo realmente `~/netlab360-bootstrap/evidencias/b3-linea-base/b3-resumen-convergencia.json` (1.3 KiB), `b3-metricas-retrospectivas.prom` (~653 B). Fases: normal 14, cambio_respaldo 1, respaldo 16, cambio_principal 29, restaurada 16. Rutas FIB normal WAN-P, respaldo WAN-B, retorno wan-b:27/wan-p:2, restaurada WAN-P. `python3 -m json.tool` y formato Prom revisados. Captura **`B3_01_Linea_Base_Observabilidad_ICMP.png`** a 15:28 considerada tomada, aún NO auditada visualmente/subida (#43).

**Nuevo componente versionado, TODAVÍA NO EJECUTADO EN VM:** `servicios/noc-historico/app.py` y [su manual](../servicios/noc-historico/README.md). Python biblioteca estándar, `--check`, `--serve` solamente `127.0.0.1:8765`, HTML con banner **HISTÓRICO / NO EN VIVO**, API `/api/v1/baseline`, salud `/healthz` y `/metrics` de exposición estática. No es Prometheus instalado ni telemetría dinámica. Siguiente acción: `git pull --ff-only`, `ast.parse`, `--check`, ejecutar servidor en foreground de primera terminal SSH, `curl` desde segunda terminal, túnel Windows `ssh -N -L 8765:127.0.0.1:8765 netlab360` para comprobar panel, Ctrl+C túnel/servidor y postcheck. **No declarar API funcional hasta recibir resultados reales**.

**GitHub:** nueva [bitácora B3](sesiones/2026-10-13-b3-linea-base-retrospectiva-validada.md), issues #1/#12/#15/#20/#21/#35/#43 actualizadas, todas abiertas. S01 **43% estimado**, sin puntos B3 adicionales hasta probar aplicación. No reejecutar B2 FRR/ping por costumbre; no modificar ens33/VMnet8, no subir credenciales, logs CSV ni PNG sin revisar y permiso. Evidencias nuevas al probar app: B3_02 API y métricas históricas; B3_03 panel NOC histórico, indicadas en manual. **La línea base NO refleja datos en vivo ni alarma real**.

---


## ACTUALIZACIÓN DEFINITIVA DEL ENSAYO — 13/10/2026 11:52 | MEDICIÓN REAL TERMINADA

**El mensaje anterior de que el ensayo está “NO EJECUTADO” es histórico.** El usuario SÍ ejecutó `scripts/laboratorio/b2-dualwan-medicion-continua.py --snapshot-confirmado` entre 11:51:41–11:52:40 Panamá; `RESULTADO_EJECUCION_CONVERGENCIA=0`. El nuevo registro [2026-10-13-b2-convergencia-icmp-continuo-verificada.md](sesiones/2026-10-13-b2-convergencia-icmp-continuo-verificada.md) es la referencia autorizada:
- `up` OSPF dual Full correcto, 14/14 muestras ICMP normal por WAN-P; en el corte 1/1 muestra ICMP en respaldo; 16/16 estable por WAN-B; durante retorno 29/29 muestras ICMP (cambio WAN-B→WAN-P en muestra #59); y 16/16 final por WAN-P. **76/76 muestras correctas, 0 pérdidas observadas**. Origen HQ LAN dummy `10.70.10.1`→destino LAN dummy S1 `10.71.10.1`.
- Primera observación FIB `wan-b` **0.186 s** después del inicio de acción de falla; primera observación del regreso `wan-p` **10.147 s** después de acción de restauración. Intervalo muestreo ~0.37s. **NO son segundos exactos de convergencia FRR ni prometen cero pérdidas fuera de las ventanas muestreadas.**
- `down` código 0, `LIMPIEZA_FINAL=OK`, `CONTENEDORES_B2_RESIDUALES=0`, host protegido, postcheck Docker/netns vacíos y `ens33` con GW intactos. Archivo local `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.log` + `.csv` (~76 filas); PNG `B2_16_Medicion_Continua_Convergencia.png` asumido tomado y pendiente auditoría #43.
- **S01 nuevo avance estimado 43/100**, antes 42/100; +1 punto B2-L3 por observación de transición, total 17/18 de B2-L3, quedan clientes y servicios finales. Issues #1, #12, #42, #43, #35 permanecen abiertas. No aumentar % solamente por documentación.
- **USUARIO SOLICITÓ CIERRE INMEDIATO (SIN ESPERAR A LAS 12:00)**: detener pruebas, traer commits GitHub a Ubuntu con `git pull --ff-only`, verificar hashes HEAD/origin/main, git limpio, Docker/netns vacíos, ens33/GW/servicios OK; `sync; sudo systemctl poweroff`, esperar VMware Powered Off y apagar Windows. Apagado todavía NO confirmado. No empezar nuevos ensayos.
---

## NUEVO ENSAYO PREPARADO — 13/10/2026 ~11:46 | TODAVÍA NO EJECUTADO

**No sustituye el último hito real de 11:24:** el laboratorio dual-WAN con 30/30 ICMP entre LAN simuladas SÍ fue probado y limpiado. Aún **NO se ha medido** la pérdida durante la transición.

- Se creó `scripts/laboratorio/b2-dualwan-medicion-continua.py` que automatiza el ensayo en un solo proceso: `precheck` / `up`, lanza un hilo para ping `HQ 10.70.10.1 → S1 10.71.10.1` y consulta FIB, espera baseline, activa `fail`, observa respaldo, activa `restore`, observa retorno y realiza `down` en `finally`. Genera `17-b2-convergencia-*.log` y `17-b2-convergencia-*.csv` en `~/netlab360-bootstrap/evidencias/`. Los CSV no se suben automáticamente. **Script no validado ni ejecutado en VM todavía**.
- Antes de ejecutar, el usuario debe traer nuevos commits `git pull --ff-only`, comprobar sintaxis Python vía `python3 -c "import ast,pathlib; ast.parse(pathlib.Path('scripts/laboratorio/b2-dualwan-medicion-continua.py').read_text())"`, revisar script y precheck; ejecutar **solo una vez** con `python3 scripts/laboratorio/b2-dualwan-medicion-continua.py --snapshot-confirmado` si hora Panamá **anterior a 11:53** el 13/10, para dejar 12:00–12:15 libre para cierre.
- Seguridad: flujo con `--network none` usando scripts previos, no altera `ens33`; al terminar verificar `sudo docker ps -a`, `sudo ip netns list`, `ip -4 -br addr show ens33`, gateway y servicios. Ante error de cleanup, **NO apagar con recursos residuales**, evaluar logs y down.
- El ensayo contempla intervalos y sondeos discretos; el primer cambio de FIB detectado es una **aproximación limitada por sondeo**, no el tiempo exacto de convergencia OSPF; valores serán desconocidos hasta salida.
- Si la prueba no termina con suficiente margen o hay dudas, **no ejecutarla** hoy: el hito de ICMP de tres fases ya está preservado, y el script queda listo para próximo arranque.

---


**Última comprobación del usuario:** **2026-10-13 11:24:09, América/Panamá**.  
**Estado real observado:** **B2-L3 DUAL-WAN y tráfico ICMP bidireccional verificados, topología retirada correctamente.**  
**Fase general:** S01 **ABIERTA, 42% estimado y documentado** — no es nota oficial.  
**Plan del usuario:** debe salir y **apagar VM Ubuntu y Windows a más tardar 12:15 p. m. del 13/10/2026**. **A las 12:00 dejar de iniciar pruebas y comenzar el cierre GitHub/postcheck**. El apagado **NO está confirmado** hasta que el usuario lo ejecute.

> Si una conversación se corta, **leer ESTE archivo primero**, luego `docs/00-estado-y-continuidad.md`, `docs/control/01-avance-s01.md`, issues [#1](https://github.com/recm0708/netlab360/issues/1), [#42](https://github.com/recm0708/netlab360/issues/42), [#12](https://github.com/recm0708/netlab360/issues/12), [#43](https://github.com/recm0708/netlab360/issues/43). Los apartados cronológicos antiguos que dicen “FRR no ejecutado” o “ping pendiente” son históricos y han quedado superados.

## Infraestructura esencial que NO debe modificarse

- Host Windows 11 / VMware Workstation Pro 26.0.1; VM `NETLAB360-Ubuntu-Desktop`, hostname `netlab360-lab`, cuenta Ubuntu `rc-aa-ec`; acceso Windows: `ssh netlab360` con clave Ed25519 y passphrase local.
- Ubuntu Desktop **26.04.1 LTS**, kernel `7.0.0-38-generic`, 8 vCPU, 16 GB RAM, disco 160 GB.
- NIC de administración **`ens33=192.168.47.40/24`, default `192.168.47.2`, VMware VMnet8 NAT**. NO cambiar ens33, default route, NetworkManager, firewall host ni redes existentes Docker.
- Docker 29.9.0, Compose 5.6.0, FRRouting 10.7.1, Python 3.14, OpenTofu 1.13.1, Ansible 2.20.1, Node 24, GitHub CLI autenticado.
- Snapshot VMware **`NETLAB360-BASE-HERRAMIENTAS`** fue confirmado por el usuario. No solicitar ni regenerar el snapshot por costumbre. Nunca publicar tokens GitHub ni `~/.config/gh/hosts.yml`, clave SSH privada u OVA sin sanitizar.
- Git privado [`recm0708/netlab360`](https://github.com/recm0708/netlab360), checkout local `~/proyectos/netlab360`, rama `main`. Tras las actualizaciones remotas actuales, **debe ejecutarse un nuevo `git pull --ff-only` en Ubuntu**; `## main...origin/main` del usuario correspondía al checkout anterior a estos commits de documentación. No declarar sincronización local posterior sin salida.

## Qué quedó confirmado (no repetir salvo necesidad concreta)

1. Base Ubuntu y mantenimiento preventivo 13/10 10:47 OK: `apt update` sin paquetes pendientes, `dpkg --audit` vacío, no reboot-required; docker, ssh, open-vm-tools activos.
2. B1 IPAM `inventario/ipam/topologia-b1.yaml`: validación correcta; 3 sedes, 9 VLAN, 2 WAN previstas; todavía `draft`.
3. B2-L2: VLAN 110 conectividad, aislamiento VLAN 120 y recuperación (log previo).
4. FRRouting v5 en contenedor aislado: `FRR_MOUNT_READABLE: SI`, `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`. **No repetir ensayos fallidos v1–v4**.
5. **B2-L3 doble WAN — primer ensayo 13/10 11:03–11:11:** script `scripts/laboratorio/b2-dualwan-ospf.sh` con `up/status/fail/restore/down`. Dos routers Docker `--network none` `nl360-b2-r-hq`/`nl360-b2-r-s1`; WAN primaria `10.78.0.0/30`, costo10, backup `10.78.0.4/30`, costo100; loopbacks `10.79.0.1/.2`, LAN dummy HQ `10.70.10.1/24` y S1 `10.71.10.1/24`. **Dos vecinos OSPF Full por router**, FIB normal `via 10.78.0.2 dev wan-p`, failover `via 10.78.0.6 dev wan-b`, retorno `wan-p`, códigos up/status/fail/restore/down=0. Logs `15-b2-dualwan-*.log`; bitácora `docs/sesiones/2026-10-13-b2-dualwan-ospf-failover-resultado.md`.
6. **B2-L3 tráfico ICMP de LAN — segundo ensayo 13/10 11:22–11:24:** script `scripts/laboratorio/b2-dualwan-ping-lan.sh`:
   - NORMAL, ruta `wan-p` simétrica: 5/5 HQ→S1 + 5/5 S1→HQ, **0% pérdida**.
   - RESPALDO tras `fail`, ruta `wan-b` simétrica: 5/5 + 5/5, **0% pérdida**.
   - RESTAURADA tras `restore`, ruta `wan-p` simétrica: 5/5 + 5/5, **0% pérdida**.
   - **30/30 ICMP** entre **IPs dummy de los routers** en tres estados, *después de estabilizar cada fase*, no tráfico continuo durante instante de falla. `RESULTADO_PING_LAN_normal/respaldo/restaurada=0`. `fail=0`, `restore=0`; `RESULTADO_DOWN=0`, `RESULTADO_B2_LIMPIEZA=0`. `sudo docker ps -a` y `sudo ip netns list` vacíos, `ens33` y GW intactos, servicios activos; Git limpio antes de nuevos commits. Bitácora `docs/sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md`.

**Logs originales LOCALES, no subidos automáticamente a GitHub:**
```text
~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-20261013-112221.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-up-20261013-112226.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-normal-20261013-112307.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-fail-20261013-112313.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-respaldo-20261013-112317.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-restore-20261013-112324.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-restaurada-20261013-112346.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-down-20261013-112352.log
```

**Capturas:** el usuario estableció que TODAS las capturas solicitadas se **consideran tomadas salvo aviso contrario**. B2_11 precheck, B2_12 vecinos/rutas Full, B2_13 failover, B2_14 restauración, B2_15 **30/30 ICMP**; no se han recibido los PNG para revisión gráfica ni subido archivos al repo. No solicitar que repita pruebas solo para fotografiar una terminal. Indicar siempre nombre PNG y marcador textual exacto **INICIO CAPTURA** hasta **FIN CAPTURA** con comando de consulta a logs, nunca `clear`.

## Control del proyecto e issues

- S01 **42% técnico ponderado**, frente a 40% previo, por dos puntos nuevos de B2-L3. Desglose `docs/control/01-avance-s01.md`: B0 12/12, B1 8/10, B2-L2 3/10, B2-L3 16/18, LACP 0/10, IaC 1/10, B3 0/15, B4 0/5, documentación 2/5, B5 0/5 = **42/100**. No es % oficial de docente.
- Hasta este corte: **43 issues, 3 cerradas** (#39 IP fija, #40 GitHub CLI, #41 herramientas/snapshot), 40 abiertas. #1 S01 **ABIERTA**, #42 dual-WAN **ABIERTA** pese a subhitos aprobados, #12 alerta/dashboard **ABIERTA**, #43 auditoría PNG **ABIERTA**, #35 documentos finales **ABIERTA**. No cerrar por adelantado.
- Pendiente **prioritario**: medir convergencia y pérdida durante caída con tráfico ICMP continuo/timestamps, y de ser necesario un cliente detrás de cada LAN; después B3 exporter/Prometheus, alarma y dashboard que muestren evento WAN. Otras áreas S01: VLAN trunks/ACL, LACP/dualNIC/redundancia, OpenTofu/Ansible, analítica, informe APA7/bitácora/manual, CI/tag/release, OVA sanitizada e importación/checksum, rúbrica docente.
- El éxito de 30/30 NO acredita cero paquetes perdidos **durante el instante de falla**, pues se hicieron pings después de la conmutación. Tampoco prueba hosts/servidores finales, solo las LAN `dummy` que residen en los routers.
- Estado S01 y futuros cierres deben mantenerse sincronizados en issue #1, #12, #42, #43 y matrices. No incrementar porcentaje solo por editar archivos.

## Pausa y comandos de cierre obligatorio (12:00–12:15, 13/10)

**A las 12:00 parar nuevos ensayos**. Para sincronizar `main` *después* de las actualizaciones del asistente:

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
sudo docker ps -a
sudo ip netns list
ip -4 -br address show ens33
ip -4 route show default
systemctl is-active docker ssh open-vm-tools
```

Comprobar Git limpio, **ambos hashes idénticos**, docker/netns vacíos, IP/GW correctos, servicios activos. Los logs originales siguen en la VM fuera de Git; si se solicita respaldarlos/subirlos, revisar sensibilidad y agregarlos de modo explícito. **No afirmar apagado ejecutado hasta que el usuario reporte**. Tras verificaciones exitosas:

```bash
sync
sudo systemctl poweroff
```

Esperar VMware **Powered Off** y apagar Windows. Si aparece un contenedor B2, ejecutar exclusivamente `bash scripts/laboratorio/b2-dualwan-ospf.sh down` tras revisar marcador del estado, sin destruir recursos ajenos; no apagar con recursos no identificados. Si quedan problemas, capturar/loguear y detener proceso de apagado para resolver, sin correr experimentos nuevos.

**Preferencias operativas del usuario:** entregar paquetes de 6–10 pasos cuando sea útil, no microconfirmaciones; explicar de qué marca a cuál va cada captura; actualizar GitHub continuamente y preservar checkpoint para cambios de conversación; cada vez que VM arranca, mantenimiento preventivo antes de trabajo; al final apagar ordenadamente.
