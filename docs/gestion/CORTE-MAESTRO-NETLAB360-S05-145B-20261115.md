# CORTE MAESTRO NETLAB360 — S05 — Lotes 145A y 145B completados

**Fecha:** 15/11/2026. **Es el documento prioritario de reanudación** para cualquier chat posterior. Los cortes 142B, 143C y 144C son históricos. La instrucción vigente del usuario es terminar **SOLO S05**, sin anticipar fases S06/S07/S08 salvo dependencias imprescindibles expresamente justificadas.

## Acceso y seguridad

- GitHub: https://github.com/recm0708/netlab360, branch main. VM VMware Workstation Ubuntu 26.04.1, usuario rc-aa-ec, nombre netlab360-lab, repo ~/proyectos/netlab360.
- Gestión: ens33 192.168.47.40/24, gateway 192.168.47.2. NOC API/HTML en 127.0.0.1:9130 con túnel SSH Windows; exporter S04 9110.
- La red se sostiene en 21 namespaces efímeros y contenedores FRR x3/Faucet. No reiniciar Ubuntu guest, no hacer LACP/SDN down/up ni repetir failovers. Suspensión/reanudación VMware se validó anteriormente, NO se ha probado reinicio del invitado.
- Sin clear; agrupar varios pasos por respuesta; capturas con nombre sin extensión, momento y encuadre exactos. GitHub/issues/tablero deben sincronizarse al cierre de cada tanda.

## S05 ya implementado y probado; no repetir

- Tres sedes HQ/S1/S2, nueve VLAN, cuatro WAN, FRR OSPF, FIB S1 por s1p/S2 por s2p, HTTP HA BACKEND_HQ principal y backend S1 de respaldo; las fallas WAN y HTTP ya se probaron.
- Agregación LACP 802.3ad HQ/S1/S2, 2/2 miembros en switch y cliente; fallos 2→1→2 y regresiones comprobados previamente.
- Open vSwitch/Faucet aislado: bridge br-s05-sdn, SDN VLAN410 A/B permitida y VLAN420 C aislada, OpenFlow1.3, 25 flujos en la observación actual, fallo y regreso sdna0 probados.
- 144A/B/C cerraron el único estado transitorio HTTP offline detectado anteriormente: dos muestras RUNNING BACKEND_HQ/PRINCIPAL, tres GET HTTP desde S2 200 OK, FIB y servicios íntegros.
- 145A **ejecutado y OK**: scripts/operacion/s05-lote-145a-instalar-observador.sh instaló helper nuevo como root:root 0755, guardó una copia única del ejecutable antiguo en /var/backups/netlab360/s05-observer-legacy-20261115. Snapshot sudo -n del nuevo helper RC0: tres FRR, FIB principal, tres LACP up 2/2 switch+cliente, Faucet connected con 25 flujos, edad UTC 0.18 s; ens33/GW/Git sin cambios. Marcador LOTE145A_HELPER_ROOT_NOC=OK; registro VM: ~/netlab360-bootstrap/s05/evidencias/noc-integracion/14_Instalacion_Atomica_Observador_NOC.txt.
- 145B **ejecutado y OK**: scripts/operacion/s05-lote-145b-activar-noc.sh reinició SOLO el servicio netlab360-s05-noc. Primera consulta curl falló con RC7 mientras levantaba el servicio, el reintento devolvió JSON healthz healthy=true y después dos muestras NOC sin warnings: 18 nodos/21 enlaces, FIB S1=s1p S2=s2p, HTTP BACKEND_HQ/PRINCIPAL, HQ/S1/S2 LACP up 2/2, SDN connected/25 flows, horario Panamá 10:07:17 y 10:07:21, seis systemd active, ens33/GW/Git intactos. Marcador LOTE145B_NOC_LACP_SDN=OK; registro VM: ~/netlab360-bootstrap/s05/evidencias/noc-integracion/15_Rollout_NOC_LACP_SDN_2Muestras.txt.
- Candidata instalada helper SHA-256 ba2a87081cf8537dcd388bb86a8e2437679aea4a079411094948695b252ef54f; helper anterior respaldado SHA 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad.
- **NO ejecutar nuevamente 145A ni 145B.** Ambos acabaron OK. Todavía no existe la imagen S05_63: el operador lo indicó.

## Próxima tarea: Lote 145C visual (no hay comando de instalación)

1. Mantener SSH túnel en Windows 127.0.0.1:9130 → 127.0.0.1:9130 de VM. Abrir http://127.0.0.1:9130/ en Chrome, forzar recarga Ctrl+Mayús+R.
2. Inspeccionar cuatro tarjetas LACP HQ/S1/S2 y SDN Faucet: LACP 2/2 ambos lados y OPERATIVO; Faucet CONECTADO con conteo de flujos observado; encabezado/reloj Panamá. Verificar que el HTML no solapa texto, la topología de 18 nodos/21 enlaces y HA/FIB son legibles. Fuente de la API ya acreditada: no pedir recapturar 145A/B.
3. Si bien, **tomar** S05_63_NOC_LACP_Multisede_y_Faucet_Operativos, desde encabezado/fecha/hora hasta las cuatro tarjetas con fuente/estados completos. S05_64_NOC_FIB_HA_y_Observabilidad_Integrada solo si ofrece contexto sin recortar.
4. Usuario comparte imagen o confirma; todavía se debe verificar PNG real, tamaño y SHA-256 en #105, nunca inventar hashes.

## Qué queda de S05 luego de 145C

- #32: definir alcance y probar UNA falla/restauración independiente de instancia de backend, con rollback y monitor S2 (sin repetir falla de enlace). Aclarar límites mono-VM y si realmente se exige otro equipo.
- #31: interpretar datos P1/P1B que ya existen (iperf3, CPU/retransmisión), límites del throughput virtual; no repetir ensayos de carga sin necesidad.
- #23: documentar diferencias OVS vs Linux bridge/FRR y limitación de limpieza selectiva; vincular imágenes auténticas.
- #105: inventariar y verificar originales PNG/JSON/TXT/CSV, SHA256/manifiestos, aceptación integral y documentación S05. Solo después cerrar #5 y milestone S05.
- #64 NOC se puede cerrar tras confirmación visual 145C, PNG S05_63 y su verificación; **no está cerrada todavía**.

## Milestones e issues S05–S08 tras auditoría

[Auditoría de las 24 issues, abiertas y cerradas](AUDITORIA-ISSUES-MILESTONES-S05-S08-145B-20261115.md). Estado actual: S05 6 abiertas/1 cerrada; S06 3 abiertas; S07 1 abierta; S08 11 abiertas/2 cerradas. Las abiertas mantienen sus hitos; no se cerró prematuramente ningún milestone.

- S06: #6/#25/#26 solo disponen de insumos reales de S04/S05 y reglas baseline; no se creó dataset etiquetado ni modelo evaluado.
- S07: #7 pendiente; telemetría S05 no equivale a ciclo AIOps.
- S08: #27 informe maestro v4.6 (113 páginas hasta S04) sigue sin S05 incorporado; #34 compatibilidad OVS/Faucet ahora sí comprobada; #106 **suspensión VMware validada** pero NO reboot guest; #48 dictamen docente del 13/11 no confirmado; TAR/PPT/OVA condicional pendientes. No adelantar redacción S06–S08.
- Históricos de grandes issues S05 y algunas S08 preservados en [docs/gestion/historico-issues/20261115](historico-issues/20261115/). Los checklists vigentes fueron normalizados para eliminar indicaciones desactualizadas tipo “145A/B no ejecutados”.

**En otro chat:** abrir primero este corte; leer únicamente la última salida de ejecución del usuario; seguir S05 desde la captura 63 o lo último que realmente se haya completado. No pedir repetir material ya comprobado. 
