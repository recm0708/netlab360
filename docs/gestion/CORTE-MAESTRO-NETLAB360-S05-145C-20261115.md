# NETLAB360 — Corte maestro S05: captura 145C y cierre restante

> **ACTUALIZACION 146A (15/11/2026):** el lote 146A detectó discrepancia SHA-256 en los tres JSON P1: el log original coincide, pero JSON actuales y manifiesto histórico no. **Los valores P1 de este corte son provisionales; no copiarlos al informe hasta reconciliar** los originales del TAR, sin sobrescribir archivos ni recalcular manifiestos. Las verificaciones HA/NOC/SDN hasta 146A-12 sí fueron correctas, pero 146A abortó en 146A-13. Leer [auditoría de procedencia P1](../evidencias/s05-reconciliacion-p1-146a-20261115.md).

**Fecha:** 15 de noviembre de 2026. **Alcance:** S05 exclusivamente. Continúa el [corte maestro 145B](CORTE-MAESTRO-NETLAB360-S05-145B-20261115.md) y sustituye sus instrucciones operativas de «captura 63 no tomada». Los datos históricos 145A/145B permanecen válidos.

## 145C: evidencia visual verificada

- **145A/145B previamente aprobados:** observador root nuevo, respaldo del anterior, NOC/API saludable, 18 nodos/21 enlaces, FIB S1=s1p/S2=s2p, tres LACP 2/2, Faucet conectado (25 flujos entonces), HTTP BACKEND_HQ/PRINCIPAL, seis servicios activos, gestión 192.168.47.40/24 default 192.168.47.2. No repetirlos.
- **Captura 63 RECIBIDA Y APROBADA VISUALMENTE:** archivo adjuntado en conversación S05_63_NOC_LACP_Multisede_y_Faucet_Operativos(1).png, PNG válido, **1917 × 712**, **155432 bytes**, SHA-256 calculado sobre esos bytes **d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe**.
- Evidencia visible: Topología ACTIVA; HQ/S1/S2; 3 FRR, 3 conmutadores, 9/9 equipos/VLAN, 4 WAN; LACP HQ/S1/S2 OPERATIVO, switch 2/2 y cliente 2/2; Faucet/OpenFlow CONECTADO con **26 reglas observadas**; HTTP HQ principal; reloj de Panamá 15/11/2026 10:25:57 a. m. Tarjetas y cabecera legibles.
- **26 reglas en la imagen no contradicen las 25 de un instante anterior**: son observaciones distintas. El número de reglas no mide caudal ni demuestra, aisladamente, aislamiento VLAN.
- **Pendiente #105:** comparar el hash del PNG original Windows con este hash del archivo efectivamente recibido e importar binario/manifest al repositorio. Este corte **no** afirma que el PNG exista todavía en GitHub. Captura 64 solo complementaria si hiciera falta.

## Estadística descriptiva P1/P1B (sin nuevas pruebas)

Fuentes: [P1 piloto](../sesiones/2026-11-10-s05-lacp-multistream-piloto-validado.md) y [P1B CPU](../sesiones/2026-11-10-s05-lacp-p1b-capacidad-validada.md). Cifras **registradas previamente**.

| Prueba | Miembros/flujos | RX Mb/s | Retransmisiones TCP | Interpretación |
|---|---|---:|---:|---|
| P1 limitado a 120 Mb/s por flujo | 2 / 1 | 120,06 | 0 | Límite experimental, no capacidad máxima |
| P1 limitado a 120 Mb/s por flujo | 2 / 8 | 959,81 | 0 | TX 62,51/37,49 % entre miembros |
| P1 con fallo y restauración | 2→1→2 / 8 | 960,31 promedio | 553 | Recupera el bond, pero hay perturbación TCP |
| P1B sin limitador | 2 / 1 | 70 205,77 | 2 | CPU local/remota 98,32/71,07 % |
| P1B sin limitador | 2 / 8 | 113 299,56 | 178 | CPU 178,88/123,80 %, TX 50,26/49,74 % |
| P1B sin limitador | 1 / 8 | 127 389,56 | 243 | CPU 199,58/140,75 %, TX 0/100 % |
| P1B restaurado | 2 / 8 | 118 303,70 | 75 | CPU 186,04/131,32 %, TX 69,61/30,39 % |

**Análisis técnico #31:** P1 demuestra distribución por hash de flujos, no duplicación de rendimiento para un único flujo. El resultado de ocho flujos se aproxima a 8 × 120 Mb/s porque el generador limitó cada flujo. El ensayo de fallo tuvo 553 retransmisiones: no afirmar cero pérdidas. En P1B, con ocho flujos, el caudal con dos miembros fue **11,06 % inferior** al registrado con uno (113 299,56 frente a 127 389,56 Mb/s), pero **no** prueba que un solo enlace sea intrínsecamente mejor: escenarios secuenciales, una ejecución por condición, sin aleatorización ni replicaciones y CPU cercana al límite de los núcleos fijados. El retorno a dos miembros arrojó 118 303,70 Mb/s. La variación puede depender de carga de CPU, planificación del hipervisor, caché y distribución de flujos. Son tasas memoria/kernel virtuales, no capacidades Ethernet físicas; faltan muestras para inferencia estadística, desviaciones estándar o intervalos de confianza válidos. La interpretación descriptiva está completada; la integridad de archivos primarios sigue pendiente en #105.

## HA de instancia #32: siguiente lote

El repositorio ya contiene [s05-ha-noc-ciclo.py](../../scripts/validacion/s05-ha-noc-ciclo.py): perturba únicamente el servicio backend HQ y registra en JSONL el ciclo **BACKEND_HQ → BACKEND_S1 → BACKEND_HQ**, con FIB S1=s1p y S2=s2p invariantes. Ya existe un failover HTTP lógico anterior, pero falta el ciclo con observación NOC integrada y fuente S2. Este guion tiene restauración finally, **insuficiente ante caída abrupta de SSH/proceso/VM**; antes del único ensayo controlado hay que armar un temporizador systemd autónomo que reactive exclusivamente backend HQ, y verificarlo. El frontend HQ, el monitor S2 y enlaces permanecen activos. No se afirma HA del frontal, host físico o VMware: todo permanece en una sola VM.

**Orden:** 146A únicamente prechecks (Git, 6 unidades, NOC, S2, FIB, IP/GW, originales); 146B solo tras aprobar esos resultados (temporizador de rescate más una prueba reversible del backend HQ); completar contrato de limpieza selectiva sin destruir OVS activo #23; verificar/manifiestar archivos PNG/JSON/TXT #105; aceptación de solo lectura y cierre coherente #64/#31/#32/#23/#105, después #5 y milestone S05. **Solo entonces iniciar incorporación de S05 al informe único.**

**No hacer:** reinicio del invitado Ubuntu, LACP/SDN down/up, fallos WAN repetidos, redeploy de 145A/145B, retoques ens33 ni declarar archivos importados a GitHub sin verificarlos.
