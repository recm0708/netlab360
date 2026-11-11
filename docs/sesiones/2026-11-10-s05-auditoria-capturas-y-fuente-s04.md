# NETLAB360 — Auditoría de capturas S05/P1, P1B y visor V6

**Fecha de revisión:** 10/11/2026 (Panamá). **Ámbito:** evidencia aportada por el operador en la conversación: 14 PNG y una transcripción Ubuntu de los lotes 41 y 42. Este documento registra el examen visual y la interpretación de la consola, **sin afirmar que los PNG se hayan incorporado al repositorio ni que se hayan revalidado sus bytes/hash localmente**.

## Estado de capturas recibidas

| Nombre lógico (sin la copia local `(1)`) | Resultado | Alcance |
|---|---|---|
| `S05_01_Precheck_Red_Gestion_y_Repositorio` | Aceptada | `ens33 192.168.47.40/24`, GW `192.168.47.2`, Git limpio, precheck de red |
| `S05_02_Dictamen_Inicial_y_Herramientas` | Aceptada | Detección de herramientas, cero fallas; avisos reconocidos |
| `S05_01_LACP_Flujo_Unico` | Aceptada | IEEE 802.3ad, 2 puertos/bond, 120,06 Mb/s, 0 retransmisiones |
| `S05_02_LACP_Ocho_Flujos_Distribucion` | Aceptada | 959,81 Mb/s, ocho flujos, distribución TX, 0 retransmisiones |
| `S05_03_LACP_Falla_y_Restauracion` | Aceptada | 2→1→2; 960,31 Mb/s; 553 retransmisiones durante el ensayo |
| `S05_04_LACP_Limpieza_y_Postcheck` | Aceptada | Integridad de gestión, retorno 0, log local |
| `S05_05_LACP_Referencia_Un_Flujo` | Aceptada | 70 205,77 Mb/s virtuales, carga CPU observada |
| `S05_06_LACP_Capacidad_Ocho_Flujos_Dos_Enlaces` | Aceptada | 113 299,56 Mb/s virtuales, 178 retransmisiones |
| `S05_07_LACP_Capacidad_Con_Un_Solo_Enlace` | Aceptada | 127 389,56 Mb/s virtuales, un miembro, 243 retransmisiones |
| `S05_08_LACP_Capacidad_Despues_Restauracion` | Aceptada | 118 303,70 Mb/s virtuales, 75 retransmisiones y 2 puertos activos |
| `S05_09_LACP_Limpieza_Final` | Aceptada | Gestión intacta, log y estado exitoso |
| `S05_10_Topologia_General_Tres_Sedes` | Aceptada | V6: HQ, S1, S2 y WAN primaria/respaldo de ambas sucursales |
| `S05_11_Topologia_Inspector_Enlace_WAN` | Aceptada | Respaldo HQ–S2 seleccionado, ID/IP y estado `Sin datos verificables` |
| `S05_12_Topologia_Estado_Sin_Telemetria` | Complementaria, con reserva | Captura válida de `UNKNOWN`/hora Panamá, pero muestra aviso de namespaces no consultables de una ejecución anterior; auditoría posterior confirmó enumeración de namespaces posible |

Las capturas `S05_10` y `S05_11` cubren el criterio visual y no necesitan repetirse. `S05_12` puede conservarse como evidencia histórica de fuente desconectada; si se incorpora a informe final, conviene sustituirla por un pantallazo de versión y servidor actualizados, sin el aviso de permisos ya superado. Los nombres de archivos aportados llevaban `(1)` como sufijo de copia local, no parte del identificador de evidencia del informe.

## Regresión y estado real (transcripción lotes 41–42)

- `test_s05_*.py` **18/18 OK**; `S05_V6_ACEPTACION_TECNICA=OK`; Git `main` limpio, commit observado `4cecabd`.
- La API del visor `--check` pasó con inventario de **3 sedes, 3 routers, 3 switches, 9 VLAN/hosts y 4 WAN**.
- Red administrativa `ens33=192.168.47.40/24`, puerta de enlace `192.168.47.2`, sin cambios.
- SoT `~/netlab360-bootstrap/s03/rendered/sot-s03.json` disponible y exportador S04 `--check` OK (`candidate`).
- `sudo docker ps -a`: **sin contenedores registrados**; `ip netns list`: **vacío**.
- `s04_exporter_multisede.py --once`: `source_ok=true`, `topology=offline`, `R-HQ=0`, `R-S1=0`, `R-S2=0` y 9 VLAN/4 enlaces WAN con estado admin `-1` (no disponible, no activo). No se observó una falla de red; la topología de S02 está desmontada.
- `127.0.0.1:9110/healthz`: conexión rechazada, **exporter HTTP S04 no iniciado**. `127.0.0.1:9130/healthz`: visor sano.
- **Interpretación:** `UNKNOWN` en el NOC sin fuente HTTP fresca no contradice la muestra puntual `offline` confiable de S04. Solo cuando el exporter esté sirviendo datos frescos y válidos puede el visor publicar `offline` observado.

## Limitaciones de aceptación y próximos pasos

Las tasas P1B pertenecen a pruebas virtuales dentro de una VM con afinidad CPU y **no certifican capacidad física ni efecto causal de LACP**. Las retransmisiones P1 durante la conmutación impiden afirmar cero perturbación. La aprobación visual V6 **no prueba rutas OSPF Full, FIB activa, tráfico ni recuperación automática de equipos**.

1. **No repetir** P1/P1B ni rediseñar V6 únicamente para obtener más capturas.
2. Verificar el exporter S04 en modo solo lectura, con privilegios temporales autorizados; observar la transición `UNKNOWN → OFFLINE` mientras los routers no están desplegados. No confundirla con failover.
3. Importar los 14 PNG originales de forma controlada al repositorio, conservando nombres estables y un manifiesto SHA-256, cuando se realice el lote de consolidación de evidencias. **No se ha hecho todavía.**
4. Preparar despliegues de pruebas posteriores S05 (OSPF/FIB, conmutación de enlaces, HA/SDN) solo tras validar inventario/recursos y procedimientos de rollback, sin tocar `ens33`.

**Dictamen:** evidencia visual del piloto LACP, comparativa P1B y mapa V6 **aceptada en su alcance específico**. Integración de estado real, pruebas de failover de red/equipos y empaquetado de evidencias siguen pendientes.
