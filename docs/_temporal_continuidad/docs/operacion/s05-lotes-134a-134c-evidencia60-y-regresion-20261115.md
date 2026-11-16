# NETLAB360 S05 — Lotes 134A–134C (15/11/2026)

## Corte real del operador
- 133A: 20/20 tests OK, premisas del fallo Errno13 verificadas.
- 133B: Faucet recuperado SIN recrear contenedor o bridge. El canal OpenFlow conectó; estado SDN=active; 25 reglas, A/B permitido, C aislado.
- 133C: status OK; 31 reglas, OpenFlow activo, capturas 58 y 59 contienen salida real válida. En captura 60, ping A→C mostró 2 enviados, 0 recibidos y 100% pérdida. El timeout EXTERNO de 10 segundos devolvió RC124 en vez de RC1 de ping; se detuvo el script antes de C→A. LOTE133C_SDN_POLITICAS=OK NO APARECIÓ.
- 133D: no ejecutó verificaciones; el texto pegado tenía secuencias 200~, BASH~ y el heredoc fue cancelado con Ctrl+C. No confundir con fallo de infraestructura.
- FRR, seis servicios NOC/HA, gestión ens33 y tres agregadores LACP sin modificaciones comprobadas hasta 133B.

## Cambio de validación
El nuevo script scripts/validacion/s05-sdn-evidencia60-aislamiento.py es solo consulta. Valida propietario y estado activo, y ejecuta status antes y después. Lanza ping 2 paquetes con deadline interno (-w 8) más un watchdog de Python de 20 segundos; NO envuelve sudo/netns en timeout externo. A→B requiere RC0 y 2/2 entregados, A→C/C→A requieren RC1 y 0/2 con 100% pérdida. RC124, RC2 o falta de estadísticas se rechazan. Escribe COMANDO y RESUMEN en un rango de captura compacto. Las pruebas automatizadas cubren rechazo de timeout y aceptación sin falso OK.

## Secuencia (no repetir 133A/133B, up, down, docker restart ni reboot)

### Lote 134A, pasos 728–732 (solo lectura)
1. Sincronizar main con git pull --ff-only, verificar Git limpio y el script nuevo.
2. Comprobar logs 08_Precheck_Reparacion_Permisos_Faucet.txt y 09_Recuperacion_Controlador_Faucet.txt con marcadores 133A/B=OK; conservar 10_Validacion_OpenFlow_VLAN410_420_Recuperado.txt incompleto sin sobrescribir.
3. Python py_compile y unittest discover para test_s05_sdn_evidencia60_aislamiento.py.
4. Ejecutar scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status y confirmar canal OpenFlow, pings permitidos y denegados.
5. Registrar log 13_Precheck_Evidencia60_SDN.txt y marcador LOTE134A_SDN_PRECHECK=OK solo si se valida todo.

### Lote 134B, pasos 733–736 (solo lectura)
1. Exigir marcador 134A=OK.
2. Ejecutar python3 scripts/validacion/s05-sdn-evidencia60-aislamiento.py; guardar en log NUEVO 14_Captura60_VLAN420_Aislamiento_Validado.txt (no sobrescribir 10 histórico).
3. Confirmar S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO.
4. Comprobar ens33, gateway y Git limpio; emitir LOTE134B_CAPTURA60=OK.
5. Tomar UNICAMENTE S05_60_SDN_VLAN420_Aislamiento_Verificado. El segmento INICIO_CAPTURA_S05_60...FIN_CAPTURA contiene COMANDO y RESUMEN de A→B, A→C y C→A. Si no cabe en pantalla recuperar con awk desde el log 14, SIN repetir pings. Conservar 58/59 originales.

### Lote 134C, pasos 737–744 (solo lectura)
1. Exigir marcadores 134B y S05_SDN_CAPTURA60.
2. Status SDN y LACP HQ/S1/S2, rutas FRR OSPF HQ→S1 por s1p y HQ→S2 por s2p.
3. Verificar seis servicios S04/S05 activos, ens33=192.168.47.40/24 y default via 192.168.47.2, Git limpio.
4. Registrar 15_Regresion_Global_SDN_Recuperado.txt y marcador LOTE134C_SDN_Y_MULTISEDE=OK.
5. Manifestar con sha256sum y comprobar con sha256sum -c los logs originales 06/07/08/09/10 y nuevos 13/14/15, en 16_Manifiesto_SHA256_SDN_Recuperado.txt. El archivo 10 sigue documentando fallo de procedimiento, no constituye aceptación.
6. Estos hashes acreditan archivos TXT, NO PNG. Guardar nueva captura 60 y su fuente para futura auditoría de evidencia.

Si falla cualquier lote detenerse; no ejecutar el siguiente. No reiniciar Windows/Ubuntu; los netns S02/HA/LACP/SDN siguen sin recuperación comprobada. Próximos temas: failover de controlador SDN y NOC real, HA de instancia y fases S06/S07.
