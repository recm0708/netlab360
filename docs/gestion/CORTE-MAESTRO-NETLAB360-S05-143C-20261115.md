# CORTE MAESTRO NETLAB360 — S05, 143A/B/C aprobados; HTTP HA en diagnóstico

> **ARCHIVO HISTÓRICO.** La anomalía HA se resolvió en las muestras 144A y los GET HTTP 200 de 144B; 144C conservó FIB/observador legacy. Reanudar desde [corte maestro 144C](CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md) y ejecutar 145A/B con rollback; NO volver a ejecutar 144.

Fecha 15/11/2026. **Documento primario para reanudar un chat futuro.** Actualizar aquí tras lotes nuevos. No confundir código GitHub versionado con despliegue efectivo en VM.

## Entorno y reglas

Repositorio privado https://github.com/recm0708/netlab360; VM VMware Workstation netlab360-lab Ubuntu Desktop 26.04.1, usuario rc-aa-ec, ens33 192.168.47.40/24 y gateway 192.168.47.2. Repo local ~/proyectos/netlab360. NOC HTTP 127.0.0.1:9130 accesible desde PowerShell mediante tunel SSH -L 127.0.0.1:9130:127.0.0.1:9130; exporter 9110. No ejecutar clear ni reiniciar Ubuntu: 21 namespaces S02/HA/LACP/SDN efímeros; una suspensión/reanudación completa VMware ya conservó el estado, pero no existe reconstrucción validada tras reboot guest. No repetir pruebas de fallas WAN, HTTP HA, LACP o SDN previamente aceptadas.

## Lo ya comprobado

- S01–S04 cerradas según milestones internos; S05 implementó FRR OSPF HQ/S1/S2, 9 VLAN, 4 WAN, HTTP HA HQ/S1, LACP HQ/S1/S2 2/2 con fallos 2→1→2 probados y Faucet/OVS aislado. VLAN410 permite A↔B, VLAN420 aísla C, caída y retorno sdna0 acreditados; usuario confirmó capturas 60, 61, 62 tomadas. Faltan verificar bytes SHA256 de PNG originales; los TXT sí fueron verificados.
- Lotes 139A/B/140/141: NOC y exporter activos, FIB HQ→S1=s1p y HQ→S2=s2p; 3 bonds 2/2; Faucet conectado, 18/18 pruebas, topología 18 nodos/21 enlaces. NOC desplegado todavía sin tarjetas LACP/SDN.
- 142A OK 49 tests, helper sudoers instalado antiguo root:root 0755 SHA 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad. 142B abortó dos veces por ad_num_ports=None en JSON; 142C no ejecutado.
- Fix PR #139 fusionado main 1fba8c5: el parser consulta /proc/net/bonding para Number of ports cuando JSON iproute2 no ofrece ad_num_ports, siempre valida namespace/device fijos, owner, IEEE 802.3ad. 
- **143A OK**: 55/55 tests (21 nuevos, 14 topología, 14 layout, 6 HA UI), Git y gestión intactos, helper antiguo sin sustituir. Logs 08_Precheck_Parser_Bond_Proc.txt.
- **143B OK**: 6/6 bonds HQ/S1/S2 switch y cliente, cada uno JSON=None pero /proc Number of ports=2, modo/alias/flags correctos. OVS owner NETLAB360_S05_SDN_V1, Faucet running, Controller connected, 25 reglas. FIB S1=s1p S2=s2p. API LACP/SDN SIN_DESPLEGAR (esperado). Log 09_Validacion_Real_Bonds_Proc_y_OVS.txt.
- **OBSERVACIÓN ANÓMALA 143B**: ha_service del NOC status=offline, available=true, backend/path None, timestamp 2026-11-15T12:39:45+00:00, source_warnings=[]; significa que la muestra HTTP desde S2 fue aceptada pero el frontal no acreditó servicio. **No declarar HA saludable ni caído por completo sin verificar**; cotejar servicios, monitor S2, endpoints 10.70.20.21:8088, 10.71.20.21:8088, 10.70.20.23:8080 desde namespace S2.
- **143C OK**: HTML tarjetas HQ/S1/S2 y SDN, SVG intacto, node --check, app y helper nuevo hasheados, NOC/exporter active, ens33/GW Git intactos. Log 10_PreRollout_NOC_Panel_y_Hashes.txt. Hash nuevo helper repositorio ba2a87081cf8537dcd388bb86a8e2437679aea4a079411094948695b252ef54f, app 8bf182ab2443019314f3b305d746e665bab15becdfb40dc8e90ecaa26b30a034, HTML 74f3d582a96793f9eaf6b30aa715e91015fd319c2b8219ac229eef09354a1ff9. Estos hashes son para el commit de esa prueba; verificar hashes nuevos si Git cambió.
- **No se ha instalado el helper nuevo en /usr/local/libexec ni reiniciado NOC.** El motor de lectura LACP/SDN está listo en repositorio, NO en ejecución.

## SIGUIENTE ACCIÓN OPERATIVA (SIN CAMBIOS)

Ejecutar **solo** [lotes 144A, 144B y 144C](../operacion/s05-lotes-144a-144c-diagnostico-http-ha-pre-noc-20261115.md) con logs locales en ~/netlab360-bootstrap/s05/evidencias/noc-integracion/:
1. 144A dos muestras NOC 4s separadas y JSON raw de monitor S2, 6 servicios, NTP/gestión; archivo 11_Diagnostico_HA_Muestras_S2.txt, marcador LOTE144A_DIAGNOSTICO_HA=COMPLETADO.
2. 144B curl desde S2 VLAN320 a ambos backends y frontal, códigos HTTP/cuerpos JSON, process/systemd/journal; archivo 12_Diagnostico_HTTP_Desde_S2.txt, marcador LOTE144B_HTTP_S2=COMPLETADO. Ojo: COMPLETADO no significa HA sano. **No hacer reparación antes de diagnóstico.**
3. 144C verificar helper legacy con hash, sudoers snapshot FIB, systemd NOC y código candidato; archivo 13_Baseline_Helper_Legacy_PreRollout.txt, marcador LOTE144C_BASELINE_PRE_ROLLOUT=COMPLETADO.
4. Analizar el estado HA de 144A/B y decidir: solucionar problema real si persiste, o continuar con despliegue atómico del helper root conservando copia SHA del anterior, permisos root:root, mismos sudoers, validar FIB+LACP+SDN y reiniciar exclusivamente NOC con rollback. Nunca tocar ens33/FRR/OVS/LACP/VM. Después evaluar en Chrome cuatro tarjetas y fecha en zona Panamá. No capturar imagen hasta ver estados reales y correctos.

## Pendientes principales

S05 #64 NOC telemetría real LACP/SDN, #32 HA instancia/equipo independiente, #31 evaluación P1/P1B, #105 PNG originales + SHA, #5 cierre de fase y milestone. Después S06 datasets + ML reproducible, S07 AIOps supervisado, S08 informe único/bitácora/TAR/presentación/demo/entrega y #106 reconstrucción reproducible VM. Preferencias: 10–15 pasos por mensaje agrupados, comandos PowerShell/SSH, capturas solo cuando correspondan con nombre sin extensión y desde/hasta exacto. GitHub repo/issues/README/REANUDAR-AQUI deben quedar actualizados por chat.
