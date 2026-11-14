# NETLAB360 S05 — Diseño candidato para integrar LACP a HQ, S1 y S2

**Estado:** propuesta para validación tras reanudar VM el 14/11/2026; **no desplegada ni aprobada en tiempo de ejecución**. Relacionada con issue #31. Datos de base: lote 104 (11/11) y scripts S02 versionados.

## Principio de arquitectura

LACP IEEE 802.3ad se negocia entre dos extremos del **mismo dominio de capa 2**. Los cuatro WAN HQ↔S1/S2 actuales son enlaces **enrutados** sobre interfaces FRR/OSPF, por lo tanto **no** se combinan en un bond LACP ni se sustituyen. Un bond no ofrece automáticamente HA de routers ni incrementa la tasa de un único flujo TCP.

**Propuesta no disruptiva:** en cada sede, agregar un cliente de laboratorio S05 (network namespace exclusivo) conectado mediante dos pares `veth` a un nuevo bond 802.3ad del switch S02 de esa sede. El bond del switch es un único puerto lógico de `br0`, etiquetado como **puerto de acceso de la VLAN de servicios existente**. En el extremo cliente, el segundo bond es `bond0`. Agregar primero esclavos a los bonds y solo después activar enlace, evitando conectarlos individualmente como puertos de bridge (riesgo de bucles). Las pruebas de falla afectan únicamente un miembro S05.

| Sede | Namespace switch EXISTENTE (intocable en propiedad) | VLAN de servicio existente | Cliente NUEVO candidato | IPv4 candidato SIN ASIGNAR |
|---|---|---:|---|---|
| HQ | `nl360-s02-sw-hq` | 120 | `nl360-s05-lacp-hq` | `10.70.20.40/24` |
| S1 | `nl360-s02-sw-s1` | 220 | `nl360-s05-lacp-s1` | `10.71.20.40/24` |
| S2 | `nl360-s02-sw-s2` | 320 | `nl360-s05-lacp-s2` | `10.72.20.40/24` |

Los tres IPv4 `.40` están **propuestos**, NO reservados ni verificados en runtime/IPAM. La selección exige auditoría de direcciones, ARP, rutas y puertos existentes. Una opción de diseño de menor riesgo es reservar direcciones distintas tras el precheck si se detectan conflictos.

## Invariantes

1. No modificar `ens33` (192.168.47.40/24), gateway 192.168.47.2, NetworkManager, iptables/nftables del host ni VMnet8.
2. No modificar ni reiniciar Docker FRR, interfaz `tr-sw`, trunks, VLAN de otros puertos, interfaces WAN, rutas OSPF ni servicios HA.
3. Conservar intactos `ha-hq21`, `ha-hq23` (VLAN 120) y `ha-s121` (VLAN 220) y los servidores HTTP reales.
4. El propietario de todo recurso nuevo debe ser S05. **Nunca** borrar `br0` o namespaces S02 ni reciclar un nombre ocupado.
5. Si se usa un bond `s5b-*` en el switch S02, se elimina **solo** ese bond y sus interfaces creadas por S05, con inventario de identidad previo, sin alterar otros dispositivos.
6. El rollback debe funcionar incluso si un cliente no responde, con `finally`/traps y comparación de configuración antes/después, y debe abortar ante recursos sin propiedad verificable.
7. Comprobar puertos LACP 2→1→2, FIB de las dos sucursales, ping local/inter-sede y `http://10.70.20.23:8080` desde ubicación autorizada. Un resultado de capa 2 no acredita por sí solo HA de hardware.
8. No mostrar como **activos** nodos LACP en el NOC hasta obtener observación real con telemetría fresca; si el dato falta, usar **SIN DATOS**.

## Etapas siguientes

- **Lote 105:** reanudación y comprobaciones de host (solo lectura), tres Docker FRR, seis units, NOC API y fecha de observación, Git e IPAM.
- **Lote 106:** auditoría de nombres, puertos, `bridge vlan`, `/proc/net/bonding`, direcciones y rutas en tres sedes; recopilar los resultados en `~/netlab360-bootstrap/s05/evidencias/lacp-integracion/` sin mutación.
- **Diseño ejecutable posterior:** script `plan/precheck/up/status/down` con propietario, state local, pruebas unitarias y CI. Primera ejecución únicamente HQ; comparar inventario S02 antes/después, probar fallback, limpieza selectiva y entonces pasar a S1/S2.
- **Fase ulterior:** OVS/Faucet separado y observable. No introducir OVS ni un segundo bridge en trunks de producción sin justificar no-bucles.

**Evidencia siguiente:** captura `S05_45_LACP_Precheck_Recuperacion_e_Integracion_Multisede` solo cuando los lotes 105–106 demuestren recuperación y se compruebe legibilidad; conservar capturas 41–44 sin repetir el piloto.
