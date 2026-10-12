# NETLAB360 — Candidatas FRRouting para ensayo B2-L3

**Estado:** configuración propuesta y versionada, **no desplegada ni validada en ejecución**.

- R-HQ: `10.79.0.1/32`, dos WAN `10.78.0.1/30` (costo 10) y `10.78.0.5/30` (costo 100), LAN `10.70.10.0/24`.
- R-S1: `10.79.0.2/32`, dos WAN `10.78.0.2/30` y `10.78.0.6/30`, LAN `10.71.10.0/24`.
- `frr.conf` contiene comandos FRR; la asignación IP y la creación de interfaces se harán por un orquestador posterior aislado. La configuración `daemons` y la forma de inicio dependen de inspeccionar el arranque real de la imagen `quay.io/frrouting/frr:10.7.1`.
- No se emplea `network host`. No conectar interfaces a `ens33` o VMnet8; no modificar rutas, IP, NetworkManager ni iptables del anfitrión.
- Advertencia: el archivo de configuración está diseñado como propuesta. No considerarlo aceptado hasta ejecutar y comprobar `vtysh`, vecinos OSPF y cambios de rutas. La existencia de binarios FRR no basta.
- Evidencia previa: `docs/sesiones/2026-10-12-inspeccion-interna-frr-y-capturas.md`.
- Precondición de laboratorio con cambios: verificar en VMware Snapshot Manager la instantánea `NETLAB360-BASE-HERRAMIENTAS`; su existencia/nombre aún no han sido confirmados directamente.
