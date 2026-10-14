# NETLAB360 — Bitácora técnico-práctica S01

**Versión:** V0.1, edición en curso. **Origen:** registros del 12–13/10/2026 en docs/sesiones, scripts y evidencias/capturas; no sustituye logs originales fuera del repositorio. **Estado de red tras la última sesión:** contenedores y namespaces vacíos, ens33 192.168.47.40/24, GW 192.168.47.2, servicios activos.

## 1. Método de evidencia
Por cada bloque: objetivo; línea base; ejecución; comando/salida verificables; captura o log; condiciones de rollback; y límites de interpretación. Se conserva el archivo original con hash y no se mezclan evidencias de sesiones distintas para aparentar una prueba única.

## 2. B0 — Base operativa
VMware Workstation Pro 26H1u1, VM Ubuntu Desktop 26.04.1 LTS, 8 vCPU, 16 GB RAM, 160 GB disco. Gestión por VMnet8 NAT; SSH y GitHub; Docker, OpenTofu y Ansible disponibles. Pre/postcheck comprueba ens33, gateway y servicios docker/ssh/open-vm-tools. Referencia: docs/infraestructura/01-inventario-host-y-vmware.md.

## 3. B1 — Diseño de la topología
SoT YAML inventario/ipam/topologia-b1.yaml; tres sedes previstas, nueve VLAN, dos WAN. El validador Python devolvió VALIDACIÓN B1: OK, sin solapamientos en quince redes/subredes revisadas. HQ/S1 para el MVP y S2 reservada. La matriz topológica no acredita que todas las redes estén desplegadas.

## 4. B2-L2 — Segmentación y ACL
Se validaron VLAN 110/120 con trunk 802.1Q y aislamiento entre dominios. Router-on-a-stick con eth0.110/eth0.120, cliente 10.70.10.10 y servidor 10.70.20.20. HTTP 8080 y 8081 respondieron sin ACL; después nftables permitió 8080 y bloqueó 8081 con contadores accept/drop, manteniendo el servicio 8081 activo. Resultado script 0; cleanup sin residuos.
**Figuras:** B2_L2_02_Trunk_8021Q_VLAN110_120.png; B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png.

## 5. B2-L3 — WAN dual y servicio
R-HQ/R-S1, OSPF área0, enlaces 10.78.0.0/30 costo10 y 10.78.0.4/30 costo100. Dos Full por router; FIB wan-p→wan-b→wan-p ante fail/restore. HTTP HQ–S1 comprobado en tres estados estables. Serie de 76 ICMP sin pérdidas observadas en sondeos. No medir convergencia exacta con número de intentos.
**Figuras:** B2_L3_01_HTTP_WAN_Principal.png, B2_L3_02_HTTP_WAN_Respaldo.png, B2_L3_03_HTTP_WAN_Restaurada.png.

## 6. LACP y doble NIC virtual
Bonding IEEE802.3ad activo en ambos extremos, dos miembros→un miembro→dos miembros, tráfico HTTP correcto en estados estabilizados. Ensayo active-backup veth con failover, sin NIC física adicional ni switches redundantes de VMware.
**Figuras:** B2_LACP_01_Agregacion_Dos_Enlaces.png; B2_DUALNIC_02_Conmutacion_Respaldo.png.

## 7. IaC y compliance
OpenTofu cinco terraform_data y manifiesto JSON. Ansible produjo archivos R-HQ/R-S1; primer render cambió dos archivos; repetición changed=0. Baseline COMPLIANT; copia con costo 10→50 NON_COMPLIANT; Ansible reparó changed=1 seguido de changed=0. Configs derivadas de Ansible alimentaron FRRouting real y produjeron dos OSPF Full por router, failover y restore. La reconciliación no se ejecutó sobre router vivo.
**Figuras:** IAC_S01_02_Tofu_Plan-3.png; IAC_S01_08_Drift_Detectado.png; IAC_S01_09_Reconciliacion.png; IAC_B2_03_OSPF_y_Rutas_IAC.png.

## 8. B3 métricas, Prometheus y alertas
Exporter de eventos live y vista NOC. Prometheus 3.7.0 scrape up=1, tres reglas. Fallo WAN-P generó dos alertas firing; restore dejó cero alertas WAN activas. Cierre liberó puertos y red aislada. No receptor Alertmanager acreditado.
**Figuras:** B3_08_Dashboard_NOC_En_Vivo.png; B3_12_Alerta_Prometheus_WAN_Down.png; B3_13_Alerta_Prometheus_Resuelta.png.

## 9. B4 análisis y CI
CSV real con 76 ICMP, resumen derivado y 12 eventos JSONL de otras sesiones. Diagnóstico por reglas: ICMP fallido=0, FIB inesperada=0, RTT fuera de 3xP95=0, cuatro transiciones de fase (sondeos 15/16/32/61). Factores 3 y 5 originaron umbrales 0.147 y 0.245 ms, ambos sin señal. Test suite Python 24/24, CI offline success. No se entrenó ni evaluó ML.
**Figuras:** B4_05_Perfil_Estadistico_Real.png; B4_08_Diagnostico_Reglas_Reales.png; B4_10_Sensibilidad_Umbral_RTT.png.

## 10. Publicación y continuidad
Lotes 01–06: 86 PNG directamente en evidencias/capturas y siete CSV en evidencias/manifiestos, SHA256 verificados. Commit b410548f9338233c8dc23816ce78a11d67bb2896, HEAD local/remoto idénticos. Último postcheck: 13/10 23:35:02, sin contenedores ni namespaces, host gestión intacta. Cuatro evidencias IaC recuperadas de logs históricos con exit0 todavía requieren fotografía suplementaria. El log fuente es distinto de una nueva ejecución de tofu apply.

## 11. Pendientes de bitácora
Añadir figuras seleccionadas con pies, identificación de script y resultado, diagrama general, fecha de cada sesión, snapshot/release, OVA exportada y reimportada si exigido; registrar aprobación/rúbrica docente. Estado V0.1, no entrega definitiva.
