# NETLAB360 S05 — Reanudación VMware y lotes 135A–135C (15/11/2026)

## Corte respaldado por el registro del operador

Windows se reinició, Ubuntu 26.04.1 volvió a ejecutar procesos tras suspender y reanudar la VM VMware. Hora NTP sincronizada America/Panama; ens33 192.168.47.40/24, gateway 192.168.47.2. **21 namespaces presentes** (S02, HA, LACP y SDN); **4 contenedores** arriba (FRR HQ/S1/S2 y Faucet). OVS br-s05-sdn/controlador tcp:127.0.0.1:16653 conectado, state SDN active, **28 reglas** y pruebas A↔B permitidas / C aislado, management y FRR conservados. HQ LACP confirmó 2/2 miembros y 4/4 pings, pero luego abortó por comparar literalmente toda la tabla main de rutas guardada al desplegar LACP. No llegó a verificar S1/S2 ni seis servicios ni emitió NETLAB360_REANUDACION=OK.

La causa exacta de diferencia de líneas de rutas aún requiere comprobarse; **no atribuirla automáticamente a Docker**. La implementación de HQ/S1/S2 comparaba todas las rutas (incluidas nuevas interfaces de Docker/OVS), no solo gestión. PR #132 CI OK integrada con commit 78a03738bd92df0642dfd7a6431eafd0edd8cf5c: conserva y protege IPv4 ens33, todas las rutas dev ens33 y todas las defaults, pero ignora rutas de interfaces ajenas. No modifica state-hq.json, state-s1.json ni state-s2.json, IPs, bridges o Docker. Seis pruebas de regresión incluyen cambios de gateway y rutas reales denegados.

La captura S05_60 está pendiente tras el fallo anterior del parser iputils. PR #131 CI OK (d49ff77b) admite +N errors y múltiples transmisiones ARP en pings negativos, pero solo si RC1, recibidos=0 y pérdida=100%; RC124 y RC2 se rechazan. No volver a ejecutar Faucet up, down, docker restart ni fallas LACP.

## Secuencia propuesta (tres lotes, exclusivamente lectura)

### 135A: auditoría de baseline persistido y tests
1. Sincronizar main a un commit descendiente de 78a03738, Git limpio.
2. unittest discover para test_s05_lacp_postresume_management.py, test_s05_lacp_hq_integracion.py y test_s05_lacp_sucursales_integracion.py; sintaxis limpia.
3. Para cada sitio hq/s1/s2, cargar desde ~/netlab360-bootstrap/s05/lacp-multisede/state-{site}.json el before.mgmt original y compararlo con management actual: mostrar rutas agregadas/retiradas y ejecutar assert_management_preserved. Si existe drift real de ens33/default se detiene.
4. Registrar 20_Auditoria_Baseline_Gestion_PostResume.txt con marcador LOTE135A_BASELINE_POSTRESUME=OK.

### 135B: aceptación integral de reanudación VMware
1. Requiere 135A OK.
2. Verificar fecha/NTP, status LACP HQ/S1/S2 (cada uno 2/2, pings, VLAN y NOC), status SDN con conexión OpenFlow, permitidos A/B y C aislado, rutas OSPF hacia S1/S2, seis servicios activos y gestión ens33/GW/Repo.
3. Registrar 21_Validacion_Integral_Tras_Resume_VMware.txt; marcador LOTE135B_VMWARE_REANUDACION_COMPLETA=OK. Si falla NO declarar reanudación integral completa y no ejecutar captura 60.

### 135C: nueva prueba de captura 60 tras VMware
1. Requiere 135B OK.
2. Ejecutar pruebas test_s05_sdn_evidencia60_aislamiento.py y scripts/validacion/s05-sdn-evidencia60-aislamiento.py desde repo actualizado. No modificar recursos.
3. Guardar log **NUEVO** 22_Captura60_Tras_Reanudar_VMware.txt. Solo si aparecen S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO y LOTE135C_EVIDENCIA60=OK, extraer el rango INICIO_CAPTURA_S05_60..FIN_CAPTURA_S05_60 con awk para foto sin repetir pruebas.
4. Captura obligatoria S05_60_SDN_VLAN420_Aislamiento_Verificado, sin extensión: A→B RC0 2/2, A→C RC1 0 recibidos y C→A RC1 0 recibidos, 100% pérdida.
5. Nunca sobrescribir logs 10, 14 o 19 que registran intentos anteriores parciales.

**Tras completar 135C:** regresión y manifiesto SHA256 final, auditoría de PNG y continuación S05 (resiliencia SDN y NOC, HA de instancia). No reiniciar Ubuntu hasta disponer de recuperación real de namespaces y servicios; suspender VMware y reiniciar host Windows ya ha conservado memoria en esta ocasión, pero eso no prueba persistencia tras un verdadero reboot guest.
