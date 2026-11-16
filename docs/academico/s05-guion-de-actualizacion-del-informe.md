# Guion técnico para incorporar la fase 5 al informe

**Base verificable:** lotes de validación de S05 concluidos hasta el 158, 15/11/2026. Este texto sirve para actualizar los capítulos del **mismo informe académico**; todavía no representa una nueva versión del archivo Word.

## Implementación

Extendimos la infraestructura multisede de HQ, S1 y S2 construida previamente para evaluar alta disponibilidad de servicios, agregación de enlaces y segmentación definida por software. Conservamos los cuatro enlaces WAN y las nueve VLAN existentes como base de conectividad. En S05 incorporamos backends HTTP independientes de HQ y S1, un frontal de servicio y observación remota desde S2; configuramos enlaces LACP 802.3ad de dos miembros en cada sede y un dominio OVS/Faucet separado de la red administrativa.

Actualizamos el NOC para mostrar las rutas FIB, selección del backend HTTP, estados reales de LACP y conexión del controlador OpenFlow. La presentación de estados diferencia las fuentes disponibles de mediciones no observadas, sin atribuir indisponibilidad de enlace a la ausencia de telemetría.

## Pruebas y resultados

En la WAN comprobamos rutas preferidas y respaldo bajo OSPF; en LACP verificamos operación de dos miembros, falla de un miembro y restauración en HQ/S1/S2. En SDN confirmamos conectividad de A y B en VLAN410 y aislamiento del host C en VLAN420; el puerto `sdna0` volvió a su estado operativo tras un ensayo acotado.

Para HTTP realizamos una prueba real de suspensión temporal del backend HQ, observando en el NOC una secuencia `BACKEND_HQ → BACKEND_S1 → BACKEND_HQ` con **17 muestras**. El temporizador independiente de rescate se armó antes de la prueba y se canceló después de verificar el retorno. Las seis unidades de sistema se encontraron activas tras la recuperación.

En P1, la sesión original del **10/11** registró 120,057 Mb/s con un flujo y 959,810 Mb/s con ocho flujos; el ensayo de falla y retorno arrojó 960,311 Mb/s y 553 retransmisiones. La segunda sesión del **11/11** produjo 120,050, 959,356 y 959,613 Mb/s respectivamente, con 9 retransmisiones en ocho flujos y 745 durante la falla. Identificamos las sesiones por log y SHA distintos, sin reescribir archivos originales. Para P1B conservamos el manifiesto íntegro de cinco archivos. Las medidas corresponden a una VM y no representan velocidades de enlaces físicos.

## Análisis y limitaciones

La restauración de un miembro LACP, la conmutación de ruta WAN y la selección de otro backend HTTP son mecanismos distintos: sus resultados no deben agregarse como si representaran la misma falla. La plataforma demostró tolerancia a interrupciones lógicas acotadas, pero **no** redundancia del anfitrión, alta disponibilidad física ni recuperación tras reiniciar Ubuntu. Las 21 interfaces de namespaces dependen de una plataforma efímera que exige suspensión o reconstrucción controlada.

## Evidencia para el informe

Priorizaremos las capturas de topología general, adyacencias OSPF, FIB, failover, HTTP HA, LACP multisede, Faucet/aislamiento y panel NOC, complementadas por el PNG64 del ciclo HTTP. El catálogo técnico reúne 71 PNG originales y dos registros HA con manifiestos. Antes de numerar figuras se deberá cotejar la última versión editable del manuscrito.

[Tablero S05](../gestion/s05-tablero-vigente.md) · [Catálogo de imágenes](../../evidencias/capturas/README.md) · [Control del manuscrito](../entregables/01-proyecto-investigacion-maestro.md).
