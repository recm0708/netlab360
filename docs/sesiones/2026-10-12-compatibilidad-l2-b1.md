# Bitácora B1 — Validación de capacidades L2/L3 y red de gestión

**Fecha y hora del laboratorio:** 12 de octubre de 2026, 18:03:35 (Panamá, UTC−05:00).  
**Host:** `netlab360-lab`; usuario Linux `rc-aa-ec`; Ubuntu Desktop 26.04.1 LTS, kernel `7.0.0-38-generic`.  
**Fase / issue:** S01, B1, [#11](https://github.com/recm0708/netlab360/issues/11).  
**Estado:** preflight validado, **no hubo despliegue ni cambios de red**.

## 1. Procedimiento ejecutado

1. `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`: avanzó por *fast-forward* de `c26c48f` a `cf586fb`. `git status --short --branch` mostró `## main...origin/main`, sin cambios en el árbol local a esa hora.
2. `bash -n scripts/diagnostico/precheck-l2-b1.sh`: terminó sin salida/error.
3. `bash scripts/diagnostico/precheck-l2-b1.sh`: **`RESULTADO_L2=0`**; log local creado en `~/netlab360-bootstrap/evidencias/04-b1-compatibilidad-l2-20261012-180335.log`.
4. `ip -d -br link show`, `ip -4 route show table main`, `ip netns list`, `sudo docker network ls`, `git status`: inspecciones solo lectura.
5. `python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml`: **`VALIDACIÓN B1: OK`**, 3 sedes (S2 reservada), 9 VLAN, 2 enlaces WAN, 15 redes revisadas incluida VMnet8. El preflight IPAM previo verificó 14 redes candidatas frente a 3 redes/rutas del host y Docker sin solapamientos.

## 2. Resultados observados

| Componente | Resultado |
| --- | --- |
| `8021q` | Módulo **disponible** para kernel actual, no figuró cargado |
| `bonding` | Módulo disponible, no figuró cargado |
| `openvswitch` | Módulo disponible, no figuró cargado |
| `veth` | Módulo disponible, no figuró cargado |
| `bridge` | Disponible y **cargado** |
| `ovs-vsctl`, `vtysh`, `containerlab` | **No instalados**; esto no invalida el preflight |
| `ip`, `tc`, `bridge` | Disponibles (`/usr/sbin`) |
| `net.ipv4.ip_forward` | `1` (observación; NO usar como prueba de segmentación o firewall seguro) |
| Namespaces definidos | Ninguno |
| Interfaces | `lo`, `ens33`, `docker0` |
| Rutas | default por `192.168.47.2`; `172.17.0.0/16` vía `docker0` linkdown; `192.168.47.0/24` por `ens33` |
| Docker | 29.9.0, almacenamiento overlayfs, cgroup v2; redes por defecto bridge/host/none; **0 contenedores** |
| Servicios | docker, ssh, open-vm-tools activos; 0 unidades systemd fallidas |
| VM | 8 vCPU, 15 GiB RAM total (~13 GiB disponibles), raíz 157 GB (136 GB libres) |

**Interpretación:** `modinfo` demuestra presencia de archivos/metadatos del módulo, **no** compatibilidad operativa integral; LACP, VLAN, OVS y OSPF continúan **sin implementar ni probar**. La red de gestión `ens33 = 192.168.47.40/24` permaneció intacta.

## 3. Evidencias informadas por el usuario

- `B1_01_Validacion_IPAM_y_Redes.png`: captura tomada, **aún no subida/ubicada en el repositorio**.
- `B1_02_Compatibilidad_Capa2.png`: captura tomada, **aún no subida/ubicada en el repositorio**.
- Evidencia textual IPAM: `~/netlab360-bootstrap/evidencias/03-b1-preflight-20261012-173813.log`.
- Evidencia textual compatibilidad: `~/netlab360-bootstrap/evidencias/04-b1-compatibilidad-l2-20261012-180335.log`.

Se conserva el archivo local; el repo contiene el **resumen técnico sin secretos**, no se afirma haber adjuntado capturas o logs completos.

## 4. Decisiones y pendientes

- Fuente de verdad en borrador: `inventario/ipam/topologia-b1.yaml`; definir arquitectura L2 (Linux Bridge/OVS) y FRR después de respaldo/snapshot, con rollback y pruebas de recuperación.
- Distinguir: WAN dual con OSPF ≠ LACP 802.3ad ≠ redundancia de routers ≠ doble NIC.
- Verificar la instantánea VMware `NETLAB360-BASE-HERRAMIENTAS` **antes** de modificar redes Linux, crear bridges/namespaces o instalar OVS/FRR. **No hay confirmación de su creación**.
- Próxima actividad: análisis de implementación y chequeos solo lectura; preparar un prototipo reproducible, no ejecutar cambios todavía.
- Registrar un checkpoint GitHub después de una prueba funcional sustancial o antes de pausa, no por cada comando.

**Continuidad prioritaria:** `docs/00-estado-y-continuidad.md` y [#11](https://github.com/recm0708/netlab360/issues/11). 
