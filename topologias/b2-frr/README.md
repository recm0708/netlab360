# NETLAB360 — Candidatas FRRouting para ensayo B2-L3

**Estado:** configuración propuesta y versionada, **no desplegada ni validada en ejecución**.

- R-HQ: `10.79.0.1/32`, dos WAN `10.78.0.1/30` (costo 10) y `10.78.0.5/30` (costo 100), LAN `10.70.10.0/24`.
- R-S1: `10.79.0.2/32`, dos WAN `10.78.0.2/30` y `10.78.0.6/30`, LAN `10.71.10.0/24`.
- `frr.conf` contiene comandos FRR; la asignación IP y la creación de interfaces se harán por un orquestador posterior aislado. La configuración `daemons` y la forma de inicio dependen de inspeccionar el arranque real de la imagen `quay.io/frrouting/frr:10.7.1`.
- No se emplea `network host`. No conectar interfaces a `ens33` o VMnet8; no modificar rutas, IP, NetworkManager ni iptables del anfitrión.
- Advertencia: el archivo de configuración está diseñado como propuesta. No considerarlo aceptado hasta ejecutar y comprobar `vtysh`, vecinos OSPF y cambios de rutas. La existencia de binarios FRR no basta.
- Evidencia previa: `docs/sesiones/2026-10-12-inspeccion-interna-frr-y-capturas.md`.
- Precondición de laboratorio con cambios: instantánea `NETLAB360-BASE-HERRAMIENTAS` **confirmada explícitamente por el operador el 12/10/2026**; no se ha inspeccionado su interfaz directamente desde el asistente.

## Registro del primer arranque temporal (2026-10-12, 19:07)

**NO REEJECUTAR `scripts/laboratorio/b2-frr-smoke-aislado.sh` en su versión inicial** hasta investigar. El primer ensayo retornó `RESULTADO_SMOKE_FRR=4` por ausencia de respuesta de `ospfd/vtysh` al cabo del tiempo de espera. La limpieza eliminó el contenedor y la red de gestión conservó su IP/ruta. No hay pruebas de zebra, ospfd ni OSPF en ejecución.

- Bitácora: `docs/sesiones/2026-10-12-smoke-frr-primer-intento.md`.
- Diagnóstico seguro siguiente: `bash scripts/diagnostico/diagnosticar-smoke-frr-b2.sh` tras `git pull` y `bash -n`; solo lectura de ficheros y lógica de inicio.
- Hipótesis a comprobar antes de la variante v2: propietarios `frr:frr` requeridos para ficheros de configuración; capacidades concedidas al contenedor (`--cap-drop ALL` + NET_ADMIN/NET_RAW); logs perdidos por `--rm` cuando el contenedor se apaga.
- No confundir el fallo de este arranque con un problema demostrado de OSPF o de la imagen FRR oficial: el motivo aún no fue diagnosticado.
