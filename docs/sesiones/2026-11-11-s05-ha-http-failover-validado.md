# S05 · Alta disponibilidad lógica HTTP intersede — resultado verificado

**Fecha local:** 11/11/2026, 08:48, zona América/Panamá. **Evidencia primaria:** transcripción del operador y capturas `S05_37`, `S05_38` confirmadas; logs en `~/netlab360-bootstrap/s05/evidencias/ha-http/` de la VM. Los PNG no están incorporados aún en binario a GitHub.

## Infraestructura

Se reutilizaron la topología S02 de tres routers FRRouting, tres switches de VLAN y los cuatro enlaces WAN con selección OSPF/FIB, sin alterarlos. La red HA S05 se había creado y comprobado en lotes 84–86: `BACKEND_HQ=10.70.20.21/24` en VLAN120, `BACKEND_S1=10.71.20.21/24` en VLAN220 y `FRONTAL_HQ=10.70.20.23/24` en VLAN120; cliente S2 de VLAN320 (`10.72.20.20`). Los tres servicios HTTP se administran mediante units `systemd` sin habilitación automática al boot, porque los namespaces requieren restauración planificada.

## Ejecuciones del 11/11, lotes 87–90

| Lote | Control | Resultado real |
| --- | --- | --- |
| 87 | Sincronización `main` a `855809a`; regresión S05 | **62/62 tests OK**; `S05_HTTP_PRECHECK=OK_SIN_CAMBIOS`; 3 IPs y puertos libres antes de instalación; FIB principales S1 `s1p` S2 `s2p` |
| 88 | Tres units `systemd` en netns propios | **3/3 active**; `10.70.20.21:8088`, `10.71.20.21:8088`, `10.70.20.23:8080` en escucha |
| 89 | Solicitudes HTTP con identidad desde cliente S2 | Ambos backends respondieron HTTP 200; frontal eligió `BACKEND_HQ`, modo `PRINCIPAL`; `S05_HTTP_S2_A_HQ_S1=OK` |
| 90 | Detener solo unit backend HQ, mantener frontal y S1, observar respaldo 8 segundos y restaurar | `BACKEND_S1` respondió en respaldo; **15 muestras correctas**; `S05_HTTP_FALLBACK_VERIFICADO=OK`, `S05_HTTP_RETORNO=OK`, `S05_HTTP_PRUEBA_CICLO_COMPLETO=OK`; tres units nuevamente activas |
| 90 | Controles finales | S1 `s1p`, S2 `s2p` sin alteración; SHA-256 **6/6 logs OK**; `LOTE90_HTTP_HA=OK` |

**Capturas**: `S05_37_Servidores_HTTP_y_Frontal_Principal` y `S05_38_Conmutacion_HTTP_Principal_Respaldo_Retorno`, con líneas marcadoras inicio y fin verificadas en la transcripción. El usuario confirmó que fueron tomadas. No inventar que los PNG estén dentro de GitHub.

## Interpretación y límites

Se validó conmutación **de servicio HTTP** entre dos backends colocados en sedes lógicas diferentes, mediante healthcheck y prioridad HQ. La elección de aplicación no cambia ni sustituye la ruta OSPF/FIB; durante la prueba la WAN principal de ambas sucursales siguió seleccionada. Los 15 sondeo de respuesta de respaldo no prueban cero pérdidas en todo instante ni cuantifican tiempos de indisponibilidad extremos sin un sondeo continuo independiente. El frontal HQ sigue siendo punto único de fallo y todo el laboratorio reside en una sola VM VMware: no hay alta disponibilidad física ni tolerancia real a pérdida del host.

## Integración NOC siguiente

- El inventario `inventario/topologia-extensiones-s05.json` fue ampliado con tres activos realizados y enlaces de acceso + selección de aplicación tras los resultados de lotes 87–90. No implica observación en tiempo real.
- `servicios/ha-s05/monitor_http_s2.py` y `netlab360-s05-ha-monitor-s2.service` son componentes **pendientes de desplegar en VM**. Desde el netns del cliente S2 sondearán cada segundo los tres endpoints HTTP reales, escribirán `~/netlab360-bootstrap/s05/ha/observacion-http-s2.json` y el NOC lo aceptará solo si es una muestra fresca, con identidad válida. Si falla el monitor, el NOC indicará SIN DATOS. No abrir acceso HTTP HA por VMnet8.
- Validar visualmente en Chrome principal HQ, fallback S1 controlado y retorno HQ, con `source_warnings` y aplicación/FIB separadas. No repetir fallas WAN S1/S2 para crear capturas del frontal.

**Tareas futuras:** automatizar el orden de dependencias para reinicios (red S02 y HA antes de las units), LACP multistream integrado en el escenario multisede, experimento OVS/Faucet aislado y pruebas finales, luego actualizar el Word maestro único.
