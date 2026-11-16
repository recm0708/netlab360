# S05 — Lotes 133A–133D: recuperación selectiva Faucet (15/11/2026)

## Corte comprobado

L128 16/16 tests OK. L129 parcial: state-sdn.json needs_inspection, bridge br-s05-sdn con propietario S05, tres clientes/netns/OFPORT 1,2,3. L132A mostró nl360-s05-faucet Exited(255); TCP 127.0.0.1:16653 no escucha y OVS Controller is_connected=false, Connection refused. L132B detectó causa: Starting with UID=0 GID=0, seguido por [Errno 13] Permission denied: /var/log/faucet/faucet.log. FRR, LACP y seis servicios S04/S05 intactos; ens33 .40/24, GW .2.

**No repetir UP ni ejecutar DOWN; no eliminar contenedor, OVS, veth ni namespaces. No reiniciar VM/Windows.** No utilizar los lotes antiguos 129–131: conservan registro fallido y gates que no representan la recuperación.

## Reparación versionada y límites de seguridad

Script: scripts/laboratorio/s05-sdn-recuperar-faucet-logs.py. Precheck inspecciona estado, imagen Docker por digest, propiedad bridge/controller, OFPORTs/IPs, mounts de /etc/faucet (read-only) y /var/log/faucet (read-write), publicación solo localhost de 16653→6653, logs Errno13 y baseline S02. Si algo no coincide, NO modifica nada.

La acción recover --confirm-recovery cambia exclusivamente el propietario del directorio local de logs a UID root:grupo original del usuario y modo 0750; inicia el **contenedor existente** por docker start (nunca docker run/restart/rm), confirma OVS OpenFlow connected, reglas y cuatro pings (A↔B permitido, A↔C aislado), verifica gestión/FRR/namespaces. Solo entonces cambia state-sdn.json de needs_inspection a active, con registro del error anterior. Ante un fallo el state sigue needs_inspection.

## Lote 133A — solo lectura, pasos 706–711

1. Entrar en ~/proyectos/netlab360, comprobar Git limpio y ejecutar git pull --ff-only origin main.
2. Comprobar marcadores exactos en registros 06_Diagnostico_OpenFlow_Estado_y_TCP.txt y 07_Diagnostico_Logs_Puertos_y_S02.txt.
3. Validar sintaxis y ejecutar suites test_s05_sdn_recuperar_faucet_logs.py (8 tests) y test_s05_sdn_ovs_faucet_aislado.py (12 tests).
4. Consultar stat -c '%u:%g %a %n' de ~/netlab360-bootstrap/s05/sdn-faucet/logs.
5. Ejecutar python3 scripts/laboratorio/s05-sdn-recuperar-faucet-logs.py precheck, sin sudo porque el script realiza operaciones de consulta con sudo -n internamente.
6. Conservar 08_Precheck_Reparacion_Permisos_Faucet.txt y emitir LOTE133A_RECOVERY_PRECHECK=OK solo si todo pasa.

## Lote 133B — reparación del contenedor existente, pasos 712–715

Tras el marcador de 133A, ejecutar exactamente:
python3 scripts/laboratorio/s05-sdn-recuperar-faucet-logs.py recover --confirm-recovery

Esta acción modifica solo permisos del directorio logs, inicia el contenedor existente y valida las políticas. Después consultar inspect SDN, Docker ps, Controller is_connected/status, ens33, Git. Guardar 09_Recuperacion_Controlador_Faucet.txt; emitir LOTE133B_RECOVERY=OK solo si script reporta S05_SDN_RECOVERY=OK_SIN_RECREAR_RECURSOS. Si SSH se desconecta, NO repetir recover automáticamente, usar inspect.

## Lote 133C — aceptación y PNG reales 58–60, pasos 716–721

Requiere marcador de 133B. Usar status para verificar tráfico, ovs-vsctl show y ovs-ofctl -O OpenFlow13 dump-flows br-s05-sdn.
- S05_58_SDN_Faucet_OpenFlow_Conectado: Controller is_connected=true y flujo de tablas.
- S05_59_SDN_VLAN410_Comunicacion_Permitida: ping real A(198.18.41.11)→B(.12), B→A éxito.
- S05_60_SDN_VLAN420_Aislamiento_Verificado: ping A→C(.13), C→A falla exactamente con exitcode 1, no aceptar exitcode 2 ni fallos de comando.
Guardar 10_Validacion_OpenFlow_VLAN410_420_Recuperado.txt; emitir LOTE133C_SDN_POLITICAS=OK solo si todos los controles pasan.

## Lote 133D — regresión y hashes, pasos 722–727

Requiere marcador de 133C. Status SDN; status LACP HQ/S1/S2 (2 miembros por extremo), FRR rutas HQ→S1 s1p y HQ→S2 s2p, seis servicios HA/NOC activos, ens33 192.168.47.40/24 GW .2, Git limpio. Guardar 11_Regresion_Tras_Recuperar_Faucet.txt; emitir LOTE133D_REGRESION_GLOBAL=OK si todo pasa. Manifestar y comprobar SHA-256 de logs 06,07,08,09,10,11 en 12_Manifiesto_SHA256_Recuperacion_Faucet.txt. Los hashes TXT no verifican aún los PNG.

**Próximo bloque después de OK:** falla controlada y retorno del dominio SDN con protección, NOC de telemetría real y redundancia de instancia/servidor. No reiniciar PC hasta completar práctica, backup y procedimiento de recuperación probado (#106).
