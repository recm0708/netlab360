# Conservación y reanudación segura del laboratorio

Este procedimiento corresponde al entorno NETLAB360 posterior a la implementación de la fase S05. Distinguimos **suspensión**, **apagado del sistema invitado** y **reconstrucción** porque afectan de forma diferente a los componentes virtuales.

## Línea base que debemos preservar

- VM Ubuntu Desktop `netlab360-lab`, interfaz administrativa `ens33 192.168.47.40/24`, gateway `192.168.47.2`.
- 21 namespaces, cuatro contenedores (FRRouting ×3, Faucet) y seis servicios asociados a observabilidad/HTTP/NOC.
- Enlaces WAN, VLAN, bonds LACP, bridge OVS, reglas OpenFlow y archivos de estado conservados fuera del control de versiones.
- Registro y manifiestos de evidencias S05; ningún respaldo debe darse por verificado sin comprobar su integridad.

## Pausa temporal del proyecto

1. Confirmamos la publicación y sincronización de Git, y comprobamos que las evidencias locales tengan una copia recuperable.
2. Verificamos `sudo ip netns list`, `sudo docker ps`, `systemctl is-active` para los servicios y la conectividad administrativa.
3. **Suspendemos la VM desde VMware Workstation**, sin ejecutar comandos de apagado dentro de Ubuntu. Confirmamos visualmente el estado suspendido.
4. Al reanudar, verificamos nuevamente identidad, red administrativa, 21 namespaces, cuatro contenedores, seis servicios, NOC y OVS/Faucet antes de continuar con nuevas fases.

La suspensión fue utilizada anteriormente y permitió recuperar el estado del laboratorio. No sustituye a un respaldo ni garantiza comportamiento ante fallos del host, almacenamiento o energía.

## Apagado o reinicio del sistema invitado

**No autorizado en el corte S05**. Antes de apagar Ubuntu debemos desarrollar y validar el procedimiento de reconstrucción idempotente desde configuraciones y estados protegidos; comprobar respaldos íntegros con copia externa; y demostrar una restauración de los dominios S02/S05 sin alterar `ens33`. La planificación corresponde al seguimiento S08 sobre recuperación de la VM.

## Trabajo académico sin recursos activos

El informe, las figuras, los datos históricos y el control de issues pueden actualizarse desde Windows y GitHub con la VM suspendida, siempre que todos los archivos necesarios estén previamente sincronizados. Para las fases S06/S07 se reanuda la misma VM después del precheck operativo.

[Estado técnico](00-estado-y-continuidad.md) · [Reanudación](REANUDAR-AQUI.md) · [Issue de reconstrucción](https://github.com/recm0708/netlab360/issues/106).
