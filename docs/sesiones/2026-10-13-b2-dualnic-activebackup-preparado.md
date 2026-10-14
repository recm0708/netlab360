# NETLAB360 — Preparación de redundancia virtual de servidor dual-NIC, active-backup

**Fecha:** 13/10/2026, posterior a la validación LACP 20:51 Panamá.  
**Estado:** NUEVO SCRIPT VERSIONADO, **NO EJECUTADO AÚN** en Ubuntu. No sumar puntos por código preparado.

## Laboratorios ya comprobados

1. HTTP HQ→S1 con OSPF dual-WAN WAN-P/B/restaurada, código0.
2. Trunk VLAN110/120, routing inter-VLAN, ACL nftables y HTTP, código0.
3. Bond IEEE802.3ad en dos namespaces con 2→1→2 puertos agregados, HTTP correcto en cada estado y limpieza, 20:43–20:51. Este éxito no prueba dos NIC físicas ni un segundo switch.
4. Nuevos 20 PNG B2-L2/B2-L3/B3 realmente recibidos, **18 válidos y 2 válidos con observación**, paquete ZIP + CSV preparados. ZIP aún pendiente de importar a GitHub como binarios. [Auditoría lote03](../evidencias/04-auditoria-visual-lote03-2026-10-13.md).

## Próximo incremento programado

Nuevo archivo versionado [`scripts/laboratorio/b2-dualnic-activebackup-http.sh`](../../scripts/laboratorio/b2-dualnic-activebackup-http.sh) usa dos namespaces aislados propios `nl360-dnica` y `nl360-dnicb`, `bond0 mode active-backup miimon 100` en cada uno, dos enlaces veth `a1/b1` y `a2/b2`, IP privada de benchmark `198.18.251.0/30`, cliente y servidor Python HTTP.

El procedimiento previsto — sin ejecución todavía — verifica:
- **B2_DUALNIC_01:** dos miembros en ambos bonds; `Currently Active Slave a1` y `b1` mientras HTTP responde.
- **B2_DUALNIC_02:** apagar `a1` exclusivamente en namespace A; esperar paso automático a `a2/b2`, ambos miembros siguen registrados y HTTP responde.
- **B2_DUALNIC_03:** restaurar interfaz `a1`; la interfaz regresa como respaldo disponible, pero la activa sigue `a2/b2` (no se exige revertir al primario sin `primary` configurado), HTTP responde. Esto verifica **failover y disponibilidad del segundo enlace**, no failback forzado.
- **B2_DUALNIC_04:** postcheck externo, Docker/netns vacíos, ens33/GW protegidos, servicios activos y Git limpio.

El script comprueba hostname, usuario no root, snapshot, herramientas, ens33 y gateway, namespaces propios ausentes; guarda log `~/netlab360-bootstrap/evidencias/b2-dualnic-activebackup-*.log`; `trap EXIT` mata servidores y retira solamente namespaces de esta prueba y verifica host management. Si falla, no repetir sin revisar log y estado.

**Límites:** es una demostración de dos interfaces Ethernet **virtuales dentro de network namespaces**, no de dos adaptadores de red del VM invitado configurados en VMware, ni redundancia de NIC física, routers/switches o servicio productivo. El bloque de redundancia en matriz S01 permanece 4/10 hasta resultados observados y rúbrica ratificada. **Nunca tocar `ens33 192.168.47.40/24`, VMnet8, gateway `192.168.47.2`, firewall o rutas del host.**
