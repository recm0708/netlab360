# NETLAB360 S05 — Comparativa Linux bridge/FRR vs Open vSwitch/Faucet y límites de limpieza

**Fecha:** 15 de noviembre de 2026. **Documento técnico de cierre de #23**, basado en código versionado y lotes de ejecución ya acreditados, sin intervención en la VM.

## Tecnologías con funciones distintas

| Aspecto | Red corporativa S02 reaprovechada en S05 | Dominio SDN S05 |
|---|---|---|
| Segmentación | Namespaces Linux, conmutadores virtuales Linux bridge y VLAN 802.1Q | Open vSwitch dedicado br-s05-sdn, OpenFlow 1.3 |
| Encaminamiento L3 | Contenedores FRRouting y OSPF, cuatro WAN HQ/S1/S2, FIB activa | No participa de las rutas OSPF corporativas; experimentación L2 |
| Política/decisión | FIB del kernel y configuración de bridge/VLAN | Faucet configura comportamiento de datapath OVS desde controlador |
| Observación | FRR/FIB y fuentes NOC | Estado de conexión controlador y reglas OpenFlow (conteo variable) |
| Tolerancia a fallas | Conmutación WAN y servicios HA demostrada separadamente | Se demostró fallo/restauración de **un puerto** sdna0; no redundancia de controlador |

## Alcance SDN realmente observado

- Código: [implementación aislada](../../scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py) y [configuración de Faucet](../../config/s05/sdn/faucet.yaml).
- Recursos propios: bridge br-s05-sdn; propietario NETLAB360_S05_SDN_V1; DPID 0x505; contenedor nl360-s05-faucet, publicado solo en localhost 16653→6653; namespaces nl360-s05-sdn-a, -b y -c.
- Puertos OpenFlow 1/2/3: sdna0, sdnb0, sdnc0; hosts 198.18.41.11/24, .12/24 y .13/24. VLAN 410 para A/B y VLAN 420 para C. La prueba ICMP A↔B fue positiva; A↔C y C↔A rechazadas, sin afirmar ACL L3 adicionales que no se midieron.
- Lotes 136–138 documentan pertenencia del dominio, controlador conectado, reglas OpenFlow presentes, caída y recuperación del **único puerto sdna0**, regresión de FRR/LACP/HTTP/NOC/gestión y no reutilización de ens33. [Evidencia de ejecución](../operacion/s05-lotes-136-138-aceptacion-y-falla-sdn-20261115.md).
- La captura 63 validada muestra Faucet CONECTADO y **26 reglas observadas**. Los recuentos anteriores de 25 y 31 corresponden a otras muestras; no constituyen medidas de rendimiento ni sustituyen comprobaciones de conectividad.

## Contrato de consulta y retirada selectiva

La operación que **sí está permitida ahora** es la inspección de solo lectura mediante el script con acción inspect y su verificación de estado con acción status; esta última emite tráfico ICMP de prueba, pero no cambia la infraestructura. El código actual dispone también de la acción destructiva down --confirm-isolated, con guardas básicas: state-sdn.json con owner esperado, propiedad del bridge por external_ids, etiqueta del contenedor, rechazo de puertos ajenos y comprobación de baseline. **Esta acción NO debe ejecutarse como parte de la aceptación final** porque retiraría el dominio SDN activo y los namespaces, perdiendo el servicio que precisamente se está demostrando.

Antes de autorizar una eventual retirada futura se deberá: comprobar el state y su hash; determinar dependencias y procesos en los namespaces; verificar exactamente puertos y ownership de bridge/contenedor; comprobar que no existen usuarios o puertos externos; preparar recuperación específica y validación posterior de FRR/LACP/HTTP/NOC/ens33; registrar aprobación de desmantelamiento. La prueba offline de rechazo de bridge ajeno está en [tests](../../tests/test_s05_sdn_ovs_faucet_aislado.py); **una prueba offline no acredita que down haya sido ejecutado y revertido en VM**. Por decisión de alcance, la retirada real se difiere: conservar los recursos activos para la demostración y las evidencias.

## Limitaciones técnicas que deben reflejarse en el informe

No existe un segundo controlador Faucet validado, plano de control redundante ni segundo hipervisor. Si Faucet figura CONECTADO, hay conectividad OpenFlow de control, **no** disponibilidad del plano de datos por sí sola. VLAN 420 aislada fue verificada mediante las pruebas indicadas, sin afirmar filtrado de otros protocolos. El laboratorio único VMware no resiste la pérdida de host físico ni asegura recuperación tras reiniciar Ubuntu con namespaces efímeros. No convertir la segregación SDN en una afirmación de HA física.

## Aceptación de #23

Quedan documentadas la diferencia entre tecnologías, los límites y el contrato de consulta/retirada **sin ejecutar una limpieza destructiva**. Para cerrar #23 restará vincular las imágenes originales pertinentes y sus SHA-256 mediante #105, ejecutar una última comprobación no destructiva del estado real y verificar que el informe académico conserva estos límites.
