# Validación técnica de la fase 05

## Descripción

La quinta fase integró mecanismos de recuperación lógica y observación de una red empresarial multisede en la infraestructura de HQ, S1 y S2. Las comprobaciones se realizaron en el laboratorio virtual NETLAB360.

## Componentes validados

| Componente | Resultado |
|---|---|
| WAN y OSPF | Cuatro enlaces, nueve VLAN, rutas principales y alternativas |
| HTTP | Conmutación del backend HQ a S1 y retorno a HQ |
| LACP | Agregación 802.3ad de dos enlaces por sede y recuperación 2→1→2 |
| SDN | Open vSwitch y Faucet, comunicación VLAN410 y aislamiento VLAN420 |
| NOC | Visualización de 18 nodos, 21 enlaces, FIB, HTTP, LACP y OpenFlow |

## Pruebas y resultados

Para evaluar disponibilidad de los servicios HTTP interrumpimos de forma controlada el backend principal. El NOC observó **17 muestras** que documentan la secuencia **HQ → S1 → HQ**. Tras la recuperación los seis servicios monitoreados quedaron activos.

Comprobamos también la interrupción de un miembro LACP y el retorno a dos miembros operativos, así como el restablecimiento de un puerto del dominio SDN. Son escenarios independientes y no deben interpretarse como una misma clase de falla.

El último precheck operativo acreditó **21 namespaces**, **cuatro contenedores** y **seis servicios activos**, con la administración `ens33 192.168.47.40/24` y su puerta de enlace `192.168.47.2` intactas.

## Evidencias disponibles

La fase reúne **71 capturas PNG**, organizadas en su [catálogo](../../evidencias/capturas/fase5/README.md), además del registro original del ciclo HTTP y su salida de terminal. Las capturas se seleccionarán en el informe según la relevancia del resultado y su legibilidad.

## Limitaciones

La solución aporta tolerancia a fallas **lógicas** de rutas, enlaces y servicios dentro de una sola VM. No se ha demostrado recuperación automática tras el apagado de Ubuntu ni alta disponibilidad de hardware o del hipervisor.

## Documentación relacionada

[Diseño HTTP](../diseno/s05-ha-servicios-multisede.md) · [Agregación LACP](../diseno/s05-lacp-8023ad-multisede.md) · [Segmentación SDN](../diseno/s05-ovs-faucet-vs-bridge-frr-y-limpieza-segura.md).
