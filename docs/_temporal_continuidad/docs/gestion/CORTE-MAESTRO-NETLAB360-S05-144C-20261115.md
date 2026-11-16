# CORTE MAESTRO NETLAB360 — 15/11/2026: 144A/B/C OK, siguiente 145A/B

> **HISTÓRICO SUPERADO:** 145A y 145B YA FUERON EJECUTADOS Y APROBADOS EN VM. No volver a correr sus scripts. Para continuar: [CORTE MAESTRO 145B](CORTE-MAESTRO-NETLAB360-S05-145B-20261115.md), que sitúa el siguiente paso en captura 63, y [Auditoría S05–S08](AUDITORIA-ISSUES-MILESTONES-S05-S08-145B-20261115.md).

**PUNTO VIGENTE DE REANUDACIÓN; leer primero.** Los cortes 142B y 143C quedan históricos.

## Entorno

GitHub privado recm0708/netlab360, rama main. VM VMware Workstation netlab360-lab Ubuntu 26.04.1, usuario rc-aa-ec, ens33 192.168.47.40/24 gateway 192.168.47.2, repo ~/proyectos/netlab360. NOC en 127.0.0.1:9130 con túnel SSH desde Windows; exporter S04 9110. **No reiniciar guest Ubuntu ni destruir namespaces:** 21 netns y 4 contenedores son efímeros y la reconstrucción tras reboot no está validada (issue #106). Suspensión VMware previamente comprobada. No repetir fallos WAN/LACP/SDN/HTTP ya aceptados. No clear. Capturas con nombre sin extensión.

## Práctica ya validada

S01–S04 milestones cerrados. S05 incluye 3 sedes HQ/S1/S2, 9 VLAN, 4 WAN, FRR OSPF, HTTP HA con dos backends y frontal, LACP HQ/S1/S2 802.3ad con caída/retorno 2→1→2 por sede, Open vSwitch + Faucet OpenFlow 1.3 en isla S05, VLAN410 A/B conectados y VLAN420 C aislado, falla/restauración de sdna0. Capturas 60,61,62 reportadas tomadas, pero falta verificar PNG originales SHA256; TXT principales sí tienen hashes.

142A tuvo 49 tests OK; 142B falló por ad_num_ports=None de iproute2 JSON; PR #139 introdujo fallback de Number of ports desde /proc/net/bonding. 143A pasó 55/55 tests, 143B comprobó 6/6 bonds 2/2 por /proc y OpenFlow Faucet connected/25 flows, 143C verificó HTML de cuatro tarjetas y node --check. No repetir.

**144A COMPLETADO:** NOC y cinco servicios más activos, sin reinicios. Dos muestras 4s apartes: HTTP HA available=true status=running BACKEND_HQ ruta PRINCIPAL, FIB S1=s1p y S2=s2p, warnings=[]; monitor HTTP S2 con edad 1.69s, BACKEND_HQ y BACKEND_S1 running, frontal BACKEND_HQ PRINCIPAL. Offline aislado de 143B no persistió.

**144B COMPLETADO:** desde S2 VLAN320 tres respuestas HTTP 200 con JSON identidad saludable: HQ backend 10.70.20.21:8088, S1 backend 10.71.20.21:8088, frontal HQ 10.70.20.23:8080 BACKEND_HQ PRINCIPAL; cuatro servicios HA activos, NRestarts=0. No repetir failover.

**144C COMPLETADO:** helper instalado legacy root:root 0755 /usr/local/libexec/netlab360-observer, SHA256 8c4480989b675f50b3b561b8a1fb0887c48f1352fba06ee611317808b3b04bad; sudo -n snapshot RC0, FIB S1=s1p S2=s2p; LACP/SDN aún SIN_INSTALAR en helper y API en ejecución. app/HTML/candidato nuevo en GitHub, no instalados. NOC 9130 activo, Git limpio, gestión intacta. SHA candidato root ba2a87081cf8537dcd388bb86a8e2437679aea4a079411094948695b252ef54f.

## SIGUIENTE CAMBIO REAL (NO EJECUTADO EN LA VM TODAVÍA)

1. [Lote 145A — instalar helper root con SHA, backup y rollback](../operacion/s05-lote-145a-deploy-helper-seguro-20261115.md). Únicamente archivo observador instalado; staging root:root 0755 y backup único root en /var/backups/netlab360/s05-observer-legacy-20261115, snapshot sudoers debe confirmar 3 routers FIB, 3 LACP 2/2 y Faucet connected con flows>0. Log ~/netlab360-bootstrap/s05/evidencias/noc-integracion/14_Instalacion_Atomica_Observador_NOC.txt, gate LOTE145A_HELPER_ROOT_NOC=OK. No reinicia NOC.
2. [Lote 145B — reiniciar solo NOC y probar 2 muestras LACP/SDN API](../operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md). Reinicio exclusivo netlab360-s05-noc, no la VM; healthz, 18 nodos/21 enlaces, FIB, seis servicios, API con LACP HQ/S1/S2 2/2, Faucet connected, HTML cuatro tarjetas y hora Panamá. Rollback del helper antiguo y restart solo NOC en caso de error. Log 15_Rollout_NOC_LACP_SDN_2Muestras.txt, gate LOTE145B_NOC_LACP_SDN=OK.
3. 145C evidencia visual en Windows (túnel SSH localhost:9130): recarga Ctrl+Shift+R, confirmar 4 tarjetas y formato hora es-PA, screenshot S05_63_NOC_LACP_Multisede_y_Faucet_Operativos, opcional S05_64_NOC_FIB_HA_y_Observabilidad_Integrada. No guardar PNG sin auditoría binaria posterior.

Si 145A o 145B fallan, NO volver a ejecutar a ciegas; leer el TXT y SHA de backup/helper antes de reparar. No hay nuevas fallas WAN/LACP/SDN por ejecutar.

## Porcentaje y ruta crítica

S05 aproximadamente 85% antes de desplegar NOC. Proyecto práctico S01–S07 alrededor de 70% (estimación no oficial, las fases S06 y S07 sin implementación terminada). S05 aún necesita NOC real #64, alcance razonable de HA de instancia/equipo o documentar limitación mono-VM #32, caracterización estadística P1/P1B #31, verificación/importación PNG #105 y cierre #5. **No confundir HA de enlace con HA física de VM.**

S06 #6/#25/#26 dataset etiquetado trazable, entrenamiento y comparación de modelo contra reglas sin fuga de datos. S07 #7 integración de ciclo detecta/recomienda/aprobación humana/actúa/verifica/rollback seguro. S08 informe único ya existente con más de 100 páginas S01–S04 (continuarlo EN PARALELO, no rehacerlo), TAR separado, presentación/demo y recuperación VMware #106. No es necesario esperar fin de práctica para empezar escrito.

Mantener actualizado README, docs/REANUDAR-AQUI.md, docs/gestion/s05-tablero-vigente.md, issues #5/#32/#64/#105 y este corte al terminar cada lote. Los logs de ejecución viven en la VM; solo validar el siguiente lote cuando el usuario comparta salida real.
