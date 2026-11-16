# Bitácora B1 — Validación IPAM y preflight de redes

**Fecha/hora registrada:** 2026-10-12 17:38:04–17:38:13 (América/Panamá).  
**VM:** `netlab360-lab` / Ubuntu Desktop 26.04.1 LTS / usuario `rc-aa-ec`.  
**Fase:** S01, bloque B1. **Issue:** #11.

## Actividad verificada en Ubuntu

- Se ejecutó `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`: avance de `926c743` hasta `c26c48f`. Rama `main...origin/main`, sin cambios locales en ese momento.
- Se confirmó recepción de `docs/arquitectura/01-topologia-ipam-b1-borrador.md`, `inventario/ipam/topologia-b1.yaml`, `scripts/validacion/validar-ipam.py` y `scripts/diagnostico/precheck-b1.sh`.
- `python3 -c 'import yaml'`: PyYAML **6.0.3**.
- `python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml`: **VALIDACIÓN B1: OK**; tres sedes (HQ/S1 propuestas, S2 reservada), nueve VLAN, dos WAN, quince redes/subredes revisadas incluyendo VMnet8; no solapamientos internos.
- `bash -n scripts/diagnostico/precheck-b1.sh`: sin error.
- `bash scripts/diagnostico/precheck-b1.sh`: **resultado de salida 0**; catorce redes propuestas comparadas con tres rutas/subredes activas; **SIN CONFLICTOS DETECTADOS**. El script no realizó cambios.
- Ruta evidencia local `~/netlab360-bootstrap/evidencias/03-b1-preflight-20261012-173813.log` (aprox. 1,9 KiB).
- `git status --short --branch`: limpio después de la prueba, antes de los nuevos commits remotos de diseño.

## Redes y estado operacional observados

| Componente | Estado |
|---|---|
| VMware VMnet8 administración | `192.168.47.0/24`; Ubuntu `ens33=192.168.47.40/24`; gateway `192.168.47.2` |
| Docker default bridge | `docker0=172.17.0.0/16`, estado `linkdown` sin contenedores |
| Red empresariales candidatas | `10.70/16` HQ, `10.71/16` S1, `10.72/16` reservada S2, `10.78/16` WAN, `10.79/16` loopbacks |
| Servicios del sistema | docker, ssh, open-vm-tools activos; 0 servicios fallidos |
| CPU | 8 vCPU |
| Memoria | 15 GiB; ~13 GiB disponibles al ejecutar |
| Almacenamiento | 157 GB raíz; 136 GB disponibles |
| Contenedores de proyecto | Ninguno |

**Limitaciones:** las pruebas no descartan redes VPN inactivas, entornos fuera de la VM, otros dispositivos no visibles ni la compatibilidad real de OVS/LACP/FRR. Las 15 redes de la validación interna incluyen VMnet8; las 14 propuestas son solo las virtuales empresariales.

## Nuevos artefactos de diseño — después de la prueba

- [Matriz propuesta de equipos, puertos y enlaces](../arquitectura/02-matriz-enlaces-equipos-b1.md), con R-HQ/R-S1, switches L2, endpoints, WAN primaria/respaldo y cost OSPF 10/100.
- [Precheck L2/L3 del anfitrión](../../scripts/diagnostico/precheck-l2-b1.sh) diseñado para inspeccionar módulos sin cargarlos ni alterar interfaces.
- Diseño todavía en **borrador**, no desplegado. Los nombres lógicos de puertos no están asignados aún a dispositivos Linux.

## Próximos procedimientos

1. `cd ~/proyectos/netlab360 && GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`.
2. Revisar matriz de puertos y validar sintaxis de `scripts/diagnostico/precheck-l2-b1.sh`.
3. Ejecutar `bash scripts/diagnostico/precheck-l2-b1.sh` y conservar su log.
4. Revisar compatibilidad 802.1Q/veth/OVS/bonding y decidir implementación L2-L3 sin tocar `ens33`.
5. **Confirmar** si existe snapshot VMware `NETLAB360-BASE-HERRAMIENTAS`; no iniciar B2 con cambios de red antes del snapshot.

**Criterios de cierre:** esta bitácora documenta un precheck y diseño, **no demuestra OSPF, LACP, VLAN ni redundancia funcional**.
