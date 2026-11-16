# NETLAB360 S05 — Conmutación y restauración de WAN S1/S2 verificadas

**Corte operativo:** 11/11/2026, según el archivo de terminal `Texto pegado(20261111-014359).txt` aportado por el operador. **Alcance:** failover de **enlace** WAN virtual mediante OSPF/FIB; no certifica alta disponibilidad de routers, switches, servidores ni física. El operador indicó que tomó las capturas **S05_24**, **S05_25** y **S05_26**, pero los PNG originales todavía no se han adjuntado ni incorporado a GitHub para auditoría visual/Hash.

## Lote 56 — Precheck

`S05_ESTADOS_WAN_LAN=OK`. Las rutas baseline por las primarias `s1p` y `s2p` y respaldos disponibles `s1b`/`s2b` fueron comprobados; `S05_FAILOVER_PRECHECK=OK`. OSPF FULL: R-HQ **4**, R-S1 **2**, R-S2 **2**. `LOTE56_PRECHECK_FAILOVER=OK`. Fuente local: `~/netlab360-bootstrap/s05/evidencias/failover-wan/01_Precheck_Failover_WAN.txt`.

## Lote 57 — S1

Script versionado `scripts/laboratorio/s02-failover-wan.py S1`, que modifica exclusivamente la interfaz WAN principal `s1p` **en el namespace R-HQ** y la restaura mediante `finally`.

- Antes del corte: `10.79.0.2 via 10.78.0.2 dev s1p` y regreso desde S1 por `s1p`.
- Durante corte: `S02_S1_WAN_PRINCIPAL=DOWN`; selección FIB `10.79.0.2 via 10.78.0.6 dev s1b`, regreso S1 `via 10.78.0.5 dev s1b`. `S02_S1_OTRA_SEDE_ESTABLE=SI`; `S02_S1_CONMUTACION=OK`. Script verifica ICMP a loopbacks de ambas sedes.
- Restauración: `S02_S1_WAN_PRINCIPAL=RESTAURADA`, FIB principal `10.79.0.2 via 10.78.0.2 dev s1p`, ruta de retorno por `s1p`; `S02_S1_RETORNO_PRINCIPAL=OK`; `S02_S1_PRUEBA_COMPLETA=OK`; `LOTE57_FAILOVER_S1=OK`.
- El script imprimió espera FIB en el segundo 1 y 10 durante la recuperación. **Estos mensajes no son mediciones exactas de interrupción ni pruebas de cero pérdida.**
- Evidencia textual delimitada `INICIO_CAPTURA_S05_24` a `FIN_CAPTURA_S05_24`; captura reportada tomada por el operador, **PNG pendiente de recibir**.

## Lote 58 — S2

- Baseline `10.79.0.3 via 10.78.0.10 dev s2p`, retorno S2 por `s2p`.
- Fallo `S02_S2_WAN_PRINCIPAL=DOWN`; FIB alternativa en HQ `10.79.0.3 via 10.78.0.14 dev s2b`, regreso desde S2 `via 10.78.0.13 dev s2b`. La ruta hacia S1 permaneció estable; `S02_S2_CONMUTACION=OK`.
- Recuperación `S02_S2_WAN_PRINCIPAL=RESTAURADA`, regresó `via 10.78.0.10 dev s2p`, retorno S2 `via 10.78.0.9 dev s2p`, `S02_S2_RETORNO_PRINCIPAL=OK`, `S02_S2_PRUEBA_COMPLETA=OK`, `LOTE58_FAILOVER_S2=OK`. El script comprueba ICMP y gestión.
- Evidencia delimitada `INICIO_CAPTURA_S05_25` a `FIN_CAPTURA_S05_25`; captura reportada tomada, archivo original pendiente.

## Lote 59 — Postcheck

`S05_FAILOVER_S1=OK`, `S05_FAILOVER_S2=OK`, `S05_FIB_PRINCIPALES_RESTAURADAS=OK`: FIB de HQ a S1 `via 10.78.0.2 dev s1p`, HQ a S2 `via 10.78.0.10 dev s2p`. Pings finales desde host HQ VLAN110 a `10.71.10.10` y `10.72.10.10`, **2/2 respuestas en cada ensayo, 0 % pérdida solo en esos cuatro paquetes posteriores al retorno**. `S05_CONECTIVIDAD_INTERSEDE_FINAL=OK`; IP de gestión `ens33=192.168.47.40/24`, gateway `192.168.47.2`, `S05_GESTION_FINAL=OK`; `LOTE59_POSTCHECK=OK`.

Evidencia delimitada `INICIO_CAPTURA_S05_26` a `FIN_CAPTURA_S05_26`; el operador confirma captura tomada y conserva log local `04_Postcheck_Failover_WAN.txt`. Pendiente recepción del PNG e incorporación de los originales, métricas y hashes a repositorio. No es necesario repetir el ensayo para llenar un checkbox.

## Conclusión y límites

**Aprobado:** baseline OSPF 4/2/2 FULL, ambos failovers de WAN a `s1b/s2b` con tráfico ICMP de loopbacks verificado por script, restauración `s1p/s2p`, conectividad final HQ–S1/HQ–S2, otra sede no afectada en cada prueba y gestión host intacta. Los logs no bastan para afirmar una ventana de indisponibilidad en milisegundos, pérdida nula durante el corte, alta disponibilidad de **equipos** o selección de respaldo representada en tiempo real en NOC.

**Pendientes S05 principales:** telemetría FIB/OSPF solo lectura y estados visuales verificables en NOC V6; integración y ensayo de LACP en dominio multisede con control experimental, redundancia de equipo/servidor realmente construido, dominio OVS/Faucet aislado y validado, consolidación de evidencias y ampliación del informe.

**VMware:** el operador mantiene por GUI la instantánea manual `NETLAB360_S05_PreLAN_20261110`. No proporcionar comandos para creación/eliminación de instantáneas salvo petición expresa.

**Siguiente trabajo aconsejado:** instrumentar consulta de rutas kernel por namespace bajo identidad Docker/SoT/estado WAN, sin tocar `ens33` ni cambiar FRR. Solo representar **ruta FIB elegida** si la muestra es confiable; no colorear tráfico activo por esa sola razón. Mantener sin cerrar issues #5, #32 y #64 hasta su aceptación completa.
