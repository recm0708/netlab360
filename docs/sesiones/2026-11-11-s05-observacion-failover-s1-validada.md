# NETLAB360 · S05 — Conmutación S1 observada desde NOC, con retorno confirmado

**Fecha:** 11 de noviembre de 2026, hora de Panamá. **Naturaleza:** ejecución real y evidencias aportadas por el operador; no se alteró el entorno a través de GitHub. **Separación de resultados:** una prueba de enrutamiento y observación de FIB, no una medición de tráfico.

## Línea base antes del corte

- VM `netlab360-lab` con `ens33=192.168.47.40/24`, ruta por defecto `192.168.47.2`.
- NOC `127.0.0.1:9130` y exporter S04 `127.0.0.1:9110` recuperados en sesiones separadas con `sudo -v` cuando corresponde.
- En `main` se sincronizó commit `0a5500c`, con insignias compactas de router `ACTIVO / INACTIVO / SIN DATOS`. **36/36** tests Python S05 aprobados y `S05_NOC_PRECHECK=OK_SIN_CAMBIOS`: S04 y FIB verificables, baseline S1 `s1p`.
- Interfaces de ruta inicialmente elegidas por FIB HQ: S1 `s1p` / next-hop `10.78.0.2`; S2 `s2p` / `10.78.0.10`.

## Lote 76 — Observador NOC de solo lectura (terminal 5)

Comando ejecutado:
```bash
python3 scripts/validacion/s05-observar-conmutacion-noc.py --watch --site S1 --seconds 120 --interval 0.5
```
Resultado:
```text
S05_NOC_PRECHECK=OK_SIN_CAMBIOS
S05_NOC_OBSERVADOR_LISTO=S1
S05_NOC_CAMBIO=S1:PRINCIPAL->RESPALDO FIB=s1b NEXT_HOP=10.78.0.6
S05_NOC_RESPALDO_OBSERVADO=S1:OK
S05_NOC_CAMBIO=S1:RESPALDO->PRINCIPAL FIB=s1p NEXT_HOP=10.78.0.2
S05_NOC_RETORNO_PRINCIPAL_OBSERVADO=S1:OK
S05_NOC_MUESTRAS=119
S05_NOC_CICLO_COMPLETO=OK
```
Archivo JSONL real del operador: `~/netlab360-bootstrap/s05/evidencias/failover-noc/S05_NOC_S1_OBSERVACION_20261111T052859Z.jsonl`. El script tiene control de lectura de fuente S04 y FIB, registra cada muestra en JSONL, detecta transiciones por ruta real. **Aún falta ejecutar auditoría de su integridad SHA256 en la VM y empaquetar los logs originales.**

## Lote 77 — Simulador controlado de S1 (terminal 6)

Comando ejecutado después del mensaje del observador `S05_NOC_OBSERVADOR_LISTO=S1`:
```bash
python3 scripts/laboratorio/s02-failover-wan.py S1 --hold-seconds 25
```
Resultado documentado:
```text
S02_S1_WAN_PRINCIPAL=DOWN
S02_S1_RUTA_RESPALDO_HQ=10.79.0.2 via 10.78.0.6 dev s1b src 10.78.0.5
S02_S1_RUTA_RESPALDO_SUCURSAL=10.79.0.1 via 10.78.0.5 dev s1b src 10.78.0.6
S02_S1_OTRA_SEDE_ESTABLE=SI
S02_S1_CONMUTACION=OK
S05_S1_VENTANA_NOC_SEG=25
S02_S1_WAN_PRINCIPAL=RESTAURADA
S02_S1_RUTA_RESTAURADA_HQ=10.79.0.2 via 10.78.0.2 dev s1p src 10.78.0.1
S02_S1_RUTA_RESTAURADA_SUCURSAL=10.79.0.1 via 10.78.0.1 dev s1p src 10.78.0.2
S02_S1_RETORNO_PRINCIPAL=OK
S02_S1_PRUEBA_COMPLETA=OK
LOTE77_FAILOVER=OK
```
Archivo en VM: `~/netlab360-bootstrap/s05/evidencias/failover-noc/11_Failover_Observado_S1.txt`. La prueba mantiene la WAN primaria S1 deshabilitada durante la ventana elegida, la restablece y comprueba recuperación y comunicación ICMP. No confundir con caída de equipo completo ni con redundancia física.

## Lote 78 — Postcheck (terminal 3)

```text
S1_FIB=s1p
S1_NEXT_HOP=10.78.0.2
S2_FIB=s2p
S2_NEXT_HOP=10.78.0.10
S05_FIB_RESTAURADA=OK
ens33 UP 192.168.47.40/24
default via 192.168.47.2 dev ens33
## main...origin/main
LOTE78_POSTCHECK=OK
```
Archivo en VM: `~/netlab360-bootstrap/s05/evidencias/failover-noc/12_Postcheck_Failover_Observado.txt`.

## Auditoría de las 3 capturas remitidas

| Nombre lógico aportado | Veredicto | Detalle |
| --- | --- | --- |
| `S05_29_Inspector_FIB_Ruta_Principal` | **Aceptada** | Cabecera del mapa, principal HQ–S1 verde lima seleccionada por usuario, FIB principal y siguiente salto `10.78.0.2` en inspector |
| `S05_30_Codigo_Colores_y_Estados` | **Aceptada** | Tarjeta íntegra con título, tonos operativos/selección y explicación semántica, incluyendo `FIB no equivale a tráfico medido` |
| `S05_31_NOC_Conmutacion_S1_Respaldo_Seleccionado` | **Aceptada como evidencia visual de estado** | Primaria HQ–S1 roja y respaldo HQ–S1 azul discontinuo seleccionado, S2 principal verde. **El inspector y next-hop `10.78.0.6` no se ven en este PNG**; la ruta exacta se verifica en JSONL y log del simulador. No es necesario repetir una intervención WAN para obtener una toma redundante si se adjuntan ambos archivos de soporte |

Las tres imágenes fueron recibidas por conversación, **no por un commit de PNG a GitHub**. En `main` la carpeta `evidencias/capturas/fase5` todavía no contiene el lote binario, ni se calculó su SHA256 desde la VM. Registrar la diferencia entre **revisión visual** y **publicación definitiva de evidencias**.

## Próximas acciones y limitaciones

1. Auditar `JSONL`, rutas y conteo de muestras desde archivo local; generar manifiesto SHA256 portable de JSONL, log y postcheck; empaquetar el TAR técnico sin modificar Git.
2. Si se quieren comparar simétricamente las sedes, repetir observación controlada *solo S2* (opcional; el failover de consola S2 ya se ejecutó y documentó anteriormente). No es prerrequisito de la recuperación S1.
3. Iniciar issue [#32](https://github.com/recm0708/netlab360/issues/32): **redundancia de equipos/servidores**, no solo enlaces; revisar inventario, IPAM, 12 namespaces, servicios/puertos y posibilidades de HA antes de desplegar o conectar nuevas interfaces.
4. Continuar [#31](https://github.com/recm0708/netlab360/issues/31) LACP y [#23](https://github.com/recm0708/netlab360/issues/23) OVS/Faucet, aislados de `ens33`; no declarar terminada la milestone S05 ni prometer capacidad física a partir de tasas veth.

**La instantánea VMware `NETLAB360_S05_PreLAN_20261110` fue gestionada manualmente por el operador; no tocarla.**
