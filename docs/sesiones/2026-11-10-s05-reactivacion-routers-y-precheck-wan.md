# NETLAB360 S05 — Reactivación S02: routers FRR aislados y WAN preparadas

**Fecha del ensayo:** 10/11/2026, hora local de Panamá. **Fuente:** transcripción del operador de lotes 45–47, dos imágenes de terminal y comprobación de acceso SSH desde Windows.

## Resultado ejecutado

- **Lote 45, archivo `02_Verificacion_Runtime_FRR.txt`:** `bash -n scripts/laboratorio/s02-routers-start.sh` correcto. Los archivos de ejecución `daemons`, `frr.conf` y `vtysh.conf` existen, no son enlaces simbólicos y los tres `frr.conf` coinciden con su render. Docker Compose válido y sin colisiones con contenedores S02. **`LOTE45_FRR_PREPARADO=OK`.**
- **Lote 46, archivo `03_Arranque_Routers_FRR.txt`:** se iniciaron exactamente tres contenedores `nl360-s02-r-hq`, `nl360-s02-r-s1`, `nl360-s02-r-s2`, cada uno en estado `Running=True` y con `HostConfig.NetworkMode=none`. Mensajes `S02_ROUTER_START_OK=3`, `S02_ENLACES_WAN_CREADOS=0`, `S05_S02_ROUTERS=OK`, `LOTE46_ROUTERS_AISLADOS=OK`.
- **Lote 47, archivo `04_Precheck_WAN_y_FRR.txt`:** cuatro WAN declarativas registradas con subredes `10.78.0.0/30`, `10.78.0.4/30`, `10.78.0.8/30`, `10.78.0.12/30`; costo OSPF 10 en principales, 100 en respaldos; `S02_WAN_PRECHECK=OK`. Los tres comandos `show ip ospf neighbor` devolvieron tablas sin vecinos, **comportamiento esperado con contenedores aislados y antes de crear WAN**.
- **Integración S04/NOC:** ambas consultas devolvieron fuente confiable y topología `active` tras iniciar contenedores. Significa **procesos observados**, no adyacencias FULL, rutas FIB verificadas, conectividad entre sedes ni enlaces seleccionados.
- **Red administrativa:** `ens33=192.168.47.40/24`, default `192.168.47.2`, `S05_GESTION_INTACTA=SI`; Git `main...origin/main` limpio. Conexión SSH por clave desde Windows confirmó host y misma IP.
- **Evidencias visuales:** `S05_14_Routers_FRR_Aislados_Iniciados` y `S05_15_Precheck_WAN_y_Routers_FRR` examinadas y aceptadas para el alcance de sus pruebas. PNG originales aún sin importar al repositorio o un manifiesto SHA-256 propio.

## Salvaguarda obligatoria antes de modificar WAN

El script `scripts/laboratorio/s02-wan-links.py` comprueba pertenencia de los contenedores, Git limpio, `ens33`, rutas host, colisiones de veth y ausencia del archivo `~/netlab360-bootstrap/s02/wan-links-state.json`. La operación `up` exige **`--snapshot-confirmado`**, sin crear la instantánea: antes hay que **crear y verificar una instantánea temporal en VMware Workstation Pro**. No ejecutar `up` solo para probar el indicador. Mantener la instantánea hasta validar WAN/OSPF/FIB/LAN y retirarla cuando se cierre el escenario de laboratorio sin incidencias.

El comando `up` únicamente debe ejecutarse tras dicha confirmación. Genera las cuatro parejas `veth`, las loopbacks `10.79.0.1/32`, `10.79.0.2/32`, `10.79.0.3/32` y aplica FRR dentro de los contenedores. En caso de fallo, el script intenta revertir exclusivamente sus enlaces, pero puede conservar `wan-links-state.json` si la reversión no termina. **No eliminar ni reconstruir contenedores si un fallo deja estado parcial; diagnosticar propiedad antes de usar `down`.**

## Validación siguiente

1. Capturar baseline de contenedores y red host, confirmar acceso Windows e instantánea VMware con nombre único.
2. Ejecutar `python3 scripts/laboratorio/s02-wan-links.py up --snapshot-confirmado` **solo después** de verificar instantánea; conservar log completo y detenerse ante fallo.
3. Comprobar `status`, vecinos OSPF FULL (esperado HQ 4, S1 2, S2 2), rutas hacia loopbacks remotas por `s1p` y `s2p` y `ens33` intacta. No inferir tráfico de `S04_TOPOLOGIA=active`.
4. Crear LAN/9 VLAN mediante procedimiento distinto y su precheck/snapshot confirmado; demostrar conectividad extremo a extremo antes de ensayos de failover.

**Estado al cierre de este registro:** routers activos y aislados, **WAN no desplegadas**, instantánea anterior a las WAN **aún no confirmada**.
