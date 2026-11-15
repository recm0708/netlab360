# NETLAB360 — Corte maestro de reanudación al 15/11/2026 (S05 NOC · 142B)

**LEER PRIMERO EN CUALQUIER CHAT NUEVO.** Esta nota es el estado operativo más reciente. El histórico en REANUDAR-AQUI.md y en las issues es cronológico, y puede contener tareas antiguas cuyos resultados ya se cerraron en lotes posteriores.

## Contexto y ambiente

- Repositorio privado: https://github.com/recm0708/netlab360; rama estable main. En la última salida del usuario la VM había sincronizado main a eef8946, con Git limpio. La corrección de 142B se desarrolla en GitHub; hacer git pull --ff-only antes de ejecutar los nuevos lotes.
- VM VMware Workstation: netlab360-lab, Ubuntu 26.04.1, usuario rc-aa-ec, IP ens33 **192.168.47.40/24**, gateway **192.168.47.2**. Windows con PowerShell; SSH con túnel -L 127.0.0.1:9130:127.0.0.1:9130.
- Repo: ~/proyectos/netlab360. Logs locales: ~/netlab360-bootstrap/s05/evidencias/noc-integracion/. No hacer clear, no snapshots permanentes, no reboot guest. Suspender VMware ha permitido reiniciar el host Windows preservando namespaces, pero NO hay reconstrucción validada tras shutdown/reboot Ubuntu.
- Servicios: exporter S04 9110, NOC S05 9130, HTTP HA HQ/S1 y monitor S2 (6 systemd activos en el último auditado). Enrutamiento 3 contenedores FRR OSPF, HQ→S1 FIB s1p, HQ→S2 s2p; LACP HQ/S1/S2 802.3ad 2/2 extremos; Faucet controlador OpenFlow13 en br-s05-sdn, VLAN410 A/B permitida y VLAN420 C aislada.

## Qué ya está acreditado (NO REPETIR)

- S01–S04: cerradas en GitHub. S05 WAN/HTTP HA y tres LACP HQ/S1/S2 con fallo 2→1→2 ya probados; no repetir.
- S05 SDN OVS/Faucet desplegado aislado; capturas 58 y 59 previas, **60, 61 y 62 tomadas según usuario**. 135C validó aislamiento A→C/C→A RC1 0 respuestas y A→B RC0 2/2. 137B probó caída y retorno **solo de sdna0**, OpenFlow conectado, servicio HA/FRR conservado; 138 regresión y hashes TXT correctos. No inventar hashes PNG: auditar originales de Windows antes de cerrar #105.
- Suspender/Reanudar VMware conservó 21 namespaces, 4 contenedores y OVS, LACP, HTTP HA; fue corregido el falso drift de rutas docker0 (flag linkdown). No confundir suspensión con persistencia tras reboot Ubuntu.
- 139A/B/140/141: NOC 9130, exporter 9110, fuentes FIB/HTTP sanas, 3 bonds 2/2, Faucet OVS conectado, UI 18 nodos/21 enlaces y **18/18 tests**. Grafo actualmente en ejecución SIN campos lacp/sdn; PR #138 introdujo código nuevo en repo, NO desplegado.
- **142A=OK**. Archivo 05_Precheck_Codigo_Observabilidad_NOC.txt con 15 tests nuevos +14 topología +14 layout +6 HA/UI =49/49, gestión .40/24 GW .2 intacta, main eef8946, Git limpio. Helper instalado /usr/local/libexec/netlab360-observer root:root modo 0755, SHA viejo 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad. No fue reemplazado.
- **142B FALLÓ en el paso 826, DOS INTENTOS**. En HQ_SW, alias correcto S05_HQ_a14ac59efb1e996a, mode=802.3ad, flags UP/LOWER_UP, pero info_data.ad_num_ports no existe en JSON de iproute2, por tanto ACTIVOS=None y AssertionError. El TXT histórico 06_Precheck_Raw_Bonds_OVS_Observador.txt documenta fallo. 827–830 NO ejecutados. No se puede afirmar que los seis JSON cumplan el esquema antiguo.
- **142C NO se ejecutó**. No tocar instalador ni reiniciar NOC ni añadir sudoers.
- Fix GitHub: verificador root S05 ajustado para fallback a /proc/net/bonding con pares namespace/device fijos, validación alias, modo 802.3ad, Number of ports único 0–2. Test unitarios nuevos (None y casos adversos) y runbook 143A/B/C versionados. Código en GitHub, no instalado en VM.

## Retomar exactamente aquí

Documento con comandos, gates y nombres de TXT NUEVOS:
[LOTE 143A–143C: parser /proc y aceptación de fuentes](../operacion/s05-lotes-143a-143c-reparacion-parser-y-continuidad-20261115.md)

1. **143A**: git pull --ff-only a main, comprobar marcador 142A, py_compile y tests nuevos/regresión, confirmar SHA del helper LEGACY sin instalar. Log 08_Precheck_Parser_Bond_Proc.txt; gate LOTE143A_PARSER_CORREGIDO=OK.
2. **143B**: leer seis namespaces con ip -j -d y /proc/net/bonding, exigir owner/alias, mode IEEE 802.3ad y 2 puertos reales en SW y cliente; consultar OVS/flows/HTTP HA/FIB/gestión, sin tocar interfaz. Log 09_Validacion_Real_Bonds_Proc_y_OVS.txt; gate LOTE143B_FUENTES_6_BONDS_OVS=OK.
3. **143C**: JS/HTML cuatro tarjetas, sistema, SHA256, gestión y Git limpio. Log 10_PreRollout_NOC_Panel_y_Hashes.txt; gate LOTE143C_PRE_ROLLOUT_NOC=OK.
4. Después, no antes: ejecutar despliegue de helper ROOT con respaldo verificable, owner root:root 0755, sin ejecutarlo desde Git como root. Con el sudoers existente validar FRR/FIB/S1/S2, 3 LACP con 2/2, Faucet conectado, flujos>0, hora UTC fresca; reiniciar SOLO servicio NOC 9130 con rollback, comprobar API y vista web. NUNCA restar disponibilidad de un fichero state=active; usar UNKNOWN si hay datos obsoletos.
5. Capturas nuevas solo cuando el NOC real muestre estados LACP/SDN correctos y formato horario Panamá, no durante el precheck.

## Riesgos y trabajo restante

- #64 NOC: desplegar 4 tarjetas de LACP HQ/S1/S2 y Faucet, refresco y UNKNOWN; no afirmar implementación activa todavía.
- #32 HA: falta ensayo independiente de falla/retorno de instancia servidor o equipo; no es lo mismo que fallo enlace LACP o puerto SDN.
- #31 estadística/mediciones P1/P1B y evidencia original; #105 auditoría SHA256 de PNG originales Windows e informe único; #5 y milestone S05 permanecen abiertos.
- #106 recuperación real de topología efímera tras reboot guest; no apagar Ubuntu antes del cierre práctico. Fases S06 ML y S07 AIOps siguen pendientes, luego S08 informe/bitácora/TAR/presentación/demo/exportación.
- Preferencias usuario: varios pasos por mensaje, agrupados; indicar capturas exactas y nombres sin extensión cuando correspondan; evitar clear; no repetir pruebas ya aprobadas; GitHub actualizaciones gestionadas desde ChatGPT; no declarar CI OK ni deploy sin validación real.

**Para el siguiente chat:** abre el repositorio main y este corte maestro primero. Comprueba estado de PR/CI de la corrección 142B y lee el último TXT del usuario. No empieces desde el runbook 142B antiguo.
