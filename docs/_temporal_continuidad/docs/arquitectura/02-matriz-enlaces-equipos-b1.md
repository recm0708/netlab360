# B1 — Matriz propuesta de equipos, interfaces y enlaces

**Fecha:** 2026-10-12. **Estado:** DISEÑO, sin interfaces ni contenedores de red empresarial creados.  
**Referencia:** [IPAM v0.1](../../inventario/ipam/topologia-b1.yaml), [arquitectura general](01-topologia-ipam-b1-borrador.md), issues #11 y #1.

## 1. Separación absoluta entre administración y laboratorio

| Plano | Máquina/interfaz | IP o red | Condición |
|---|---|---|---|
| Gestión del anfitrión VMware | Ubuntu `ens33` | `192.168.47.40/24` | **Existente. No modificar.** |
| NAT VMware | Gateway VMnet8 | `192.168.47.2` | Existente. No tocar. |
| Bridge estándar Docker | `docker0` | `172.17.0.0/16` | Existente, actualmente `linkdown` sin contenedores |
| Redes virtuales del proyecto | Puertos de namespaces/OVS pendientes de definir | `10.70/16`, `10.71/16`, `10.78/16`, `10.79/16` | **Solo propuesta** |
| Reserva futura S2 | `10.72.0.0/16` | VLAN 310/320/330 | Sin desplegar |

El script preflight del 12/10/2026 confirmó ausencia de solapamiento con las rutas y redes Docker activas. Este resultado no predice conflictos con conexiones VPN o redes que todavía no existen.

## 2. Inventario mínimo propuesto

| ID lógico | Función | Cantidad prevista en B2 | Estado |
|---|---|---:|---|
| `R-HQ` | Router virtual FRR, OSPF área 0 | 1 | Por implementar |
| `R-S1` | Router virtual FRR, OSPF área 0 | 1 | Por implementar |
| `SW-HQ-A` | Switch L2 del HQ, VLAN 110/120/130 | 1 | Por implementar |
| `SW-S1-A` | Switch L2 de S1, VLAN 210/220/230 | 1 | Por implementar |
| `PC-HQ` | Endpoint cliente en VLAN 110 | 1 | Por implementar |
| `PC-S1` | Endpoint cliente en VLAN 210 | 1 | Por implementar |
| `SRV-HQ` | Servicio de prueba en VLAN 120 | 1 | Por implementar |
| `SRV-S1` | Servicio de prueba en VLAN 220 | Opcional en B2 | Por implementar |
| `SW-HQ-B` | Segundo switch para agregación/redundancia L2 | Reserva de diseño | No incluido en el MVP inicial |
| `R-HQ-B` | Router redundante real con mecanismo de gateway virtual | Reserva de diseño | No incluido en el MVP inicial |

**Advertencia:** redundancia de caminos WAN (OSPF), redundancia de routers, agregación de enlaces LACP y dual-NIC de un host son **cuatro funciones diferentes**. El MVP B2 probará primero WAN de dos caminos; el resto exige infraestructura y pruebas adicionales para satisfacer la rúbrica S01.

## 3. Matriz conceptual de enlaces

No suponer que los siguientes nombres serán los que entregue Linux: son identificadores de diseño. Los nombres reales de `veth`, interfaces OVS y namespaces se confirmarán en la implementación.

| Enlace lógico | Extremo A | Extremo B | Tipo | Configuración candidata |
|---|---|---|---|---|
| `WAN-P` | `R-HQ:wan-p` | `R-S1:wan-p` | L3 punto a punto | `10.78.0.1/30` ↔ `10.78.0.2/30`; OSPF cost 10 |
| `WAN-B` | `R-HQ:wan-b` | `R-S1:wan-b` | L3 punto a punto | `10.78.0.5/30` ↔ `10.78.0.6/30`; OSPF cost 100 |
| `TRUNK-HQ` | `R-HQ:trunk-hq` | `SW-HQ-A:uplink` | L2 802.1Q | VLAN permitidas: 110, 120, 130 |
| `TRUNK-S1` | `R-S1:trunk-s1` | `SW-S1-A:uplink` | L2 802.1Q | VLAN permitidas: 210, 220, 230 |
| `HQ-USR` | `SW-HQ-A:access-110` | `PC-HQ:eth0` | L2 access | VLAN 110 |
| `HQ-SRV` | `SW-HQ-A:access-120` | `SRV-HQ:eth0` | L2 access | VLAN 120 |
| `S1-USR` | `SW-S1-A:access-210` | `PC-S1:eth0` | L2 access | VLAN 210 |
| `S1-SRV` | `SW-S1-A:access-220` | `SRV-S1:eth0` | L2 access | VLAN 220; opcional para MVP |

## 4. Puertas de enlace router-on-a-stick (propuestas)

Los nombres `trunk-hq.110` y `trunk-s1.210` representan interfaces VLAN lógicas. El medio de creación (Linux namespace, OVS, contenedor privilegiado aislado, etc.) todavía debe validarse.

| Router | VLAN/subinterfaz conceptual | IP gateway | Red |
|---|---|---|---|
| R-HQ | `trunk-hq.110` | `10.70.10.1/24` | HQ usuarios |
| R-HQ | `trunk-hq.120` | `10.70.20.1/24` | HQ servicios |
| R-HQ | `trunk-hq.130` | `10.70.30.1/24` | HQ gestión simulada |
| R-S1 | `trunk-s1.210` | `10.71.10.1/24` | S1 usuarios |
| R-S1 | `trunk-s1.220` | `10.71.20.1/24` | S1 servicios |
| R-S1 | `trunk-s1.230` | `10.71.30.1/24` | S1 gestión simulada |

## 5. OSPF y pruebas que deben ser reproducibles

- **Dominio propuesto:** OSPFv2, área 0; router ID de R-HQ `10.79.0.1`, R-S1 `10.79.0.2`. Loopbacks /32.
- **Costos WAN:** primaria 10 y secundaria 100 **por sentido**, sobre interfaces L3 independientes.
- **LAN de usuario/servicios:** anunciar por OSPF según alcance; interfaces hacia endpoints pasivas, no intentar formar vecindad allí.
- **Precheck B2:** estado de interfaces, adyacencias OSPF, tabla de rutas, ping entre PC-HQ y PC-S1 o SRV-S1, estado servicio de prueba y timestamp.
- **Falla controlada:** bajar exclusivamente el enlace **virtual** WAN-P (no ens33, docker0 ni VMnet8); capturar pérdida de adyacencia primaria, preferencia por WAN-B, tiempos de convergencia y restauración.
- **Postcheck:** restablecer WAN-P, comprobar que el tráfico y routing vuelven a lo esperado, validar que SSH a `192.168.47.40` sigue disponible.
- **LACP y redundancia real:** crear un diseño separado con switch secundario, puertos físicos virtuales dobles y negociación 802.3ad; no clasificar dos rutas OSPF como LACP o redundancia de dispositivo.

## 6. Precondiciones para implementar

1. Confirmar snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` **creado y reconocible**. Sin esa confirmación, solo realizar tareas de diseño y lectura.
2. Revisar capacidades del kernel para 802.1Q, bonding, namespaces y (si se elige) OVS.
3. Definir el mecanismo L2 que permita VLAN etiquetadas y enlaces punto a punto sin modificar ens33.
4. Acotar recursos de redes/routers/servicios y definir rollback automático antes de ejecutar B2.
5. Mantener los criterios de la issue #1 de S01 separados de los del primer experimento B2; ambos siguen abiertos.

**Última evidencia de B1:** `~/netlab360-bootstrap/evidencias/03-b1-preflight-20261012-173813.log`. No contiene topología ejecutada.
