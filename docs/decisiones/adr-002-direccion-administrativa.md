# ADR-002 — Dirección IPv4 de administración

## Contexto

El proyecto necesita una dirección estable para acceder desde Windows al invitado Ubuntu y evitar que las pruebas de WAN, VLAN y SDN interfieran con el plano de administración.

## Decisión

Configuramos `ens33` con IPv4 fija `192.168.47.40/24` y puerta de enlace `192.168.47.2` dentro de VMware VMnet8. La red administrativa se mantiene separada de los enlaces virtuales del laboratorio.

## Implementación

La VM utiliza Ubuntu Desktop 26.04.1 LTS, servicio SSH y autenticación mediante claves de usuario para el acceso remoto autorizado. Los routers FRRouting, enlaces WAN, bonds y switches SDN funcionan en recursos virtuales independientes.

## Validación

Comprobamos la dirección, la ruta por defecto y la conectividad SSH desde Windows. Las pruebas de las fases 01–05 mantuvieron la interfaz de administración activa antes y después de los escenarios controlados de falla.

## Limitaciones

La reserva IPv4 corresponde al segmento local de laboratorio. No constituye una dirección de producción ni debe copiarse a otro entorno sin verificar su planificación de red.

## Documentación relacionada

[Infraestructura VMware](../infraestructura/inventario-host-y-vmware.md) · [Preparación de Ubuntu](../infraestructura/ubuntu-desktop-y-ssh.md).
