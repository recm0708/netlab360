# Acta de aceptación técnica — Fase 05

## Descripción

La fase 05 integró alta disponibilidad lógica HTTP, agregación LACP, segmentación SDN y observabilidad sobre la red empresarial multisede desarrollada en NETLAB360.

## Resultados verificados

| Componente | Resultado |
|---|---|
| WAN/OSPF | Cuatro enlaces WAN y nueve VLAN, con recuperación de rutas |
| HTTP HA | Conmutación HQ → S1 → HQ observada en 17 muestras |
| LACP | Dos enlaces por sede, pérdida de un miembro y recuperación 2 → 1 → 2 |
| SDN | Comunicación entre A/B en VLAN 410 y aislamiento de C en VLAN 420 |
| NOC | 18 nodos, 21 enlaces y visualización de FIB, HA, LACP y Faucet |
| Entorno de ejecución | 21 namespaces, cuatro contenedores y seis servicios activos |
| Administración | `192.168.47.40/24`, gateway `192.168.47.2`, sin alteraciones |

## Evidencias

Conservamos **71 capturas PNG** de la fase, junto con los registros originales de la prueba de conmutación HTTP. Las imágenes representan configuraciones, estados y pruebas realmente realizados en el laboratorio.

## Alcance y limitaciones

Los componentes descritos se comprobaron en un entorno virtualizado. El resultado acredita recuperación lógica de servicios, enlaces y rutas; no demuestra redundancia física del servidor ni reconstrucción automática del escenario después de apagar Ubuntu.

## Resultado

Consideramos **completada la validación técnica de la fase 05**. La integración de estos resultados al informe académico único y las fases 06–08 constituyen actividades posteriores del proyecto.

[Validación técnica](../validacion/s05-integracion-y-aceptacion.md) · [Catálogo gráfico](../../evidencias/capturas/fase5/README.md).
