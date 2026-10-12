# B1 — Arquitectura e IPAM preliminar de NETLAB360

**Estado:** BORRADOR v0.1 (12/10/2026). Sujeto a validación contra las rutas y redes Docker reales de la VM; **no está desplegado**.  
**Issues:** #11, #16 y #1. **Plan:** [bloques y pausas](../05-plan-operativo-y-pausas.md).

## 1. Capas separadas

- **Administración VMware/Windows:** VMnet8 `192.168.47.0/24`, anfitrión `.1`, gateway NAT `.2`, Ubuntu `ens33=192.168.47.40/24`. **PROHIBIDO** utilizar VMnet8 o `ens33` como segmento WAN, VLAN, switch OVS o enlace para alterar rutas de laboratorio. Se preserva SSH `rc-aa-ec@192.168.47.40`.
- **Red empresarial virtual:** segmentos `10.70.0.0/16` (HQ), `10.71.0.0/16` (Sucursal 1), `10.72.0.0/16` (Sucursal 2, reservada), WAN `10.78.0.0/16` y loopbacks `10.79.0.0/16`. **Las subredes usadas se especifican expresamente en el IPAM, no se puentean con VMnet8**.
- **Contenedores / namespaces / switches emulados:** definir después de comprobar compatibilidad y aislamientos L2/L3 de Docker, OVS, FRR y kernel Ubuntu 26.04; no atribuir a Docker Bridge la capacidad de emular enlaces punto a punto ni LACP real sin comprobación.

## 2. Esquema lógico de arranque (B1 diseño → B2 prueba)

```text
                Windows / VMnet8 (NAT de administración)
                 192.168.47.1 --- 192.168.47.40/24 (Ubuntu ens33)
                                     |
                    [laboratorio separado: bridges/namespaces]
                                     |
                        +--------- R-HQ ---------+
                        |    loopback 10.79.0.1   |
                        |    VLAN HQ             |
                        |                      WAN-P OSPF cost 10
                        |                      WAN-B OSPF cost 100
                        |                         |
                        +----------------------- R-S1
                                                  loopback 10.79.0.2
                                                  VLAN S1
```

WAN-P y WAN-B son **dos conexiones L3 separadas** entre los routers R-HQ y R-S1, cuyos extremos deben simular interfaces independientes. La preferencia de OSPF se definirá mediante costos 10/100 y se medirá la reconvergencia cuando caiga la ruta principal. No afirmar que OSPF/failover esté funcionando antes de ejecutar B2.

El sitio S2 aparece **reservado para ampliación** y no debe confundirse con infraestructura desplegada.

## 3. VLAN / subredes candidatas

| Sede | VLAN | Uso | Subred virtual | Gateway propuesto |
| --- | ---: | --- | --- | --- |
| HQ | 110 | Usuarios | `10.70.10.0/24` | `10.70.10.1` |
| HQ | 120 | Servicios | `10.70.20.0/24` | `10.70.20.1` |
| HQ | 130 | Gestión interna simulada | `10.70.30.0/24` | `10.70.30.1` |
| S1 | 210 | Usuarios | `10.71.10.0/24` | `10.71.10.1` |
| S1 | 220 | Servicios | `10.71.20.0/24` | `10.71.20.1` |
| S1 | 230 | Gestión interna simulada | `10.71.30.0/24` | `10.71.30.1` |
| S2 (reserva) | 310, 320, 330 | Usuarios, servicios, gestión | `10.72.10.0/24`, `10.72.20.0/24`, `10.72.30.0/24` | Primer host de cada segmento, sin asignación aún |

**WAN:** primaria `10.78.0.0/30` (R-HQ `.1`, R-S1 `.2`) y alternativa `10.78.0.4/30` (R-HQ `.5`, R-S1 `.6`).  
**Loopbacks:** R-HQ `10.79.0.1/32`, R-S1 `10.79.0.2/32`. 

Los rangos virtuales son propuestos, no reservados universalmente. **Detener B1 si cualquier ruta del anfitrión, red Docker, VPN u otra práctica entra en conflicto**.

## 4. Elementos que aún hay que decidir y comprobar

1. **Alcance docente:** ¿cuántas sucursales obligatorias desde la primera demostración? Por ahora HQ + S1 ejecutables y S2 reservado.
2. **L2/VLAN:** método de emulación de switches con trunks 802.1Q que no afecte `ens33`; comprobar que la VLAN de gestión simulada no permita atravesar a la administración VMware.
3. **LACP:** topología de doble enlace con extremos compatibles; se diferenciará de redundancia WAN OSPF y de redundancia de dispositivo.
4. **Redundancia de equipos:** diseño y prueba de router/switch de respaldo en fase posterior, con recursos y criterios explícitos.
5. **Datos observados:** telemetría y dashboard deben mostrar fallas reales con timestamps; no métricas inventadas.
6. **Seguridad e IPAM:** gateway + VLAN + interfaz deben corresponder a un único estado deseado versionado.

## 5. Primera prueba de B1 (solo lectura y validación)

```bash
cd ~/proyectos/netlab360
bash scripts/diagnostico/precheck-b1.sh
python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml
```

Los scripts **no crean redes, no activan contenedores y no cambian rutas ni firewall**. La evidencia local se guarda fuera de Git, en `~/netlab360-bootstrap/evidencias/`. Después de revisar las salidas con el usuario, actualizar ADR/IPAM y solo entonces iniciar implementación de B2.

**Checkpoint sugerido:** B0 verificado + B1 IPAM/validación y al menos un commit de documentación, con snapshot `NETLAB360-BASE-HERRAMIENTAS` confirmado antes de modificar redes. 
