# NETLAB360 — S02: inicio y plan de integración multisede (17/10/2026)

**Estado:** diseño candidato y preflight pendiente; **NO se ha desplegado topología S02 ni modificado la VM por este registro**. La máquina Ubuntu fue encendida por el usuario y `git pull --ff-only origin main` se completó correctamente sobre commit `94339de` sin cambios locales visibles al cierre de esa operación.

## Confirmación académica relevante
- El estudiante confirmó que envió a Teams el título **«Diseño e implementación de una plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede»**. **Aprobación docente pendiente**, issue #46.
- Revisión 30/10: Introducción, Objetivos y Planteamiento del problema; 13/11 Fundamento técnico y Diseño. Se muestra el Word en Teams por representante; no PPT de corte.
- Demostración final EN VIVO con datos reales; ZIP externo de anexos autorizado, manual técnico posentrega.
- No guardar aquí archivos de clase/guías o transcripciones.

## Observaciones técnicas de S01 (comprobadas, NO S02)
- Archivo `inventario/ipam/topologia-b1.yaml` sigue `status: draft`, tres sedes en inventario pero **HQ y S1 proposed, S2 reserved**.
- Validador `scripts/validacion/validar-ipam.py` obliga que S2 permanezca `reserved`, por compatibilidad con IPAM B1 original. **No modificar silenciosamente el validador ni reescribir el inventario histórico**: para S02 introducir una revisión/nuevo esquema y prueba correspondiente.
- B2 VLAN/ACL de HQ y FRRouting/OSPF WAN HQ–S1 han sido validados **en ensayos diferentes**. El HTTP WAN previo utiliza interfaces veth P2P y rutas /32, no la misma troncal 802.1Q.
- Dos WAN existentes HQ–S1: `10.78.0.0/30` (cost 10), `10.78.0.4/30` (cost 100).
- VM gestión protegida: `ens33 192.168.47.40/24`, puerta de enlace `192.168.47.2`. No tocar IP del anfitrión, routing host, NetworkManager, nftables host ni VMnet8.

## Topología CANDIDATA S02 — sujeta a precheck y acuerdo antes de activar

- Tres routers FRRouting: `R-HQ`, `R-S1`, `R-S2`, ejecutados en contenedores con red NONE, no en `--network host`.
- VLAN por sede de IPAM B1 (HQ 110/120/130, S1 210/220/230, S2 310/320/330) con switches Linux/bridge VLAN aware y enlaces trunk 802.1Q hacia subinterfaces del router.
- Rutas WAN con **dos enlaces entre HQ y S1** ya contemplados: principal `10.78.0.0/30`, respaldo `10.78.0.4/30`.
- **Propuesta adicional, todavía NO asignada:** HQ↔S2 WAN principal `10.78.0.8/30`, extremos HQ `10.78.0.9` / S2 `10.78.0.10`, costo OSPF 10; WAN respaldo `10.78.0.12/30`, extremos HQ `10.78.0.13` / S2 `10.78.0.14`, costo 100.
- Loopbacks existentes `10.79.0.1/32`, `10.79.0.2/32`, `10.79.0.3/32`. S1↔S2 inicialmente vía HQ (hub-and-spoke); **redundancia de router HQ NO queda cubierta**. Enlaces S1-S2/equipo alterno quedan para decisión posterior tras pruebas/recursos.
- Clientes y servidores representativos en VLAN reales en cada sede. Flujo mínimo `HQ VLAN110 -> S1 VLAN220 -> servicio HTTP` y `HQ VLAN110 -> S2 VLAN320 -> servicio HTTP` con ACL positiva/negativa, WAN-P→WAN-B→restauración.
- Las redes 10.78.0.8/30 y 10.78.0.12/30 son **reservas propuestas, NO verificadas contra rutas host/Docker/VPN**, y no aparecen todavía en IPAM B1.

## Etapas técnicas antes de despliegue

1. **PRECHECK solo lectura**: hostname, fecha, estado Git, ens33/gateway, servicios, Docker/netns, rutas IPv4 host, memoria/disco y subredes Docker/VPN.
2. **Revisar compatibilidad**: validar IPAM B1 `scripts/validacion/validar-ipam.py`; correr `bash scripts/diagnostico/precheck-b1.sh`, que escribe log en `~/netlab360-bootstrap/evidencias` pero no modifica redes/contendedores. **No ejecutar** scripts de laboratorio con `up`, `fail` o `down` en este paso.
3. **Diseñar S02** sin sobrescribir S01: nuevo inventario `topologia-s02.yaml`, validador S02 y scripts `s02-*` que validan prefijos, propiedad de recursos, snapshots y rollback.
4. Validación estática de IPAM actualizado; comprobar explícitamente colisiones con rutas y Docker reales.
5. Desplegar topología de forma controlada SOLO con precheck limpio y rollback, proteger `ens33`, mantener sesión SSH y acceso a consola VMware.
6. Evidenciar **baseline→falla→esperado vs. observado→recuperación→postcheck** con nombres de capturas por prueba; registrar logs y SHA256 de capturas reales.
7. Actualizar Informe ÚNICO (7 Implementación, 8 Pruebas, 9 Análisis) y issues técnicas. No cerrar S01/S02 ni afirmar integración S2 antes de éxito medido.

**Próximo paso exacto del usuario:** ejecutar la tanda de precheck (sin despliegue ni cambios de red) y remitir los resultados. Se decidirá entonces la asignación definitiva de nuevos enlaces y el diseño del script S02.
