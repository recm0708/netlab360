# NETLAB360 — B2-L2 Router-on-a-stick, servicio HTTP real y ACL validados

**Fecha de prueba:** 2026-10-13, 19:14:13–19:15:56, zona Panamá (UTC−05).  
**Estado:** FUNCIONAL y LIMPIO según salidas de terminal del operador. **No demuestra servicio entre HQ y S1, todavía.**

## 1. Precheck reproducido

- Se sincronizó repositorio al commit local `89c2541` (antes de nuevas actualizaciones remotas), `bash -n scripts/laboratorio/b2-l2-acl-http-real.sh` -> `RESULTADO_SINTAXIS_ACL=0`.
- Herramientas `ip`, `bridge`, `nft`, `python3`, `curl`, `sysctl` disponibles; no se instalaron paquetes adicionales.
- Docker/netns vacíos y `nl360-acl*` ausentes; `ens33=192.168.47.40/24`, gateway `192.168.47.2` protegidos; IPAM validado (3 sedes, 9 VLAN, 2 WAN, estado `draft`).

## 2. Prueba de routing inter-VLAN y servicios HTTP (B2_L2_05, 19:14:14)

- Topología local HQ: un cliente `10.70.10.10/24` en VLAN110; servidor `10.70.20.20/24` en VLAN120; dos switches Linux bridge con puertos access y troncal `tr-ab/tr-ba` etiquetados VID110/120, y segundo trunk `tr-ar` hacia router aislado.
- El router en su propia namespace creó `eth0.110=10.70.10.1/24` y `eth0.120=10.70.20.1/24`, con `net.ipv4.ip_forward=1` **dentro del router, no en el host**.
- Dos servidores Python HTTP realmente escuchando en `10.70.20.20:8080` y `:8081`. Desde cliente VLAN110, antes de ACL, ambos devolvieron `NETLAB360_HTTP_SERVICIO_HQ_VLAN120_OK`: `BASELINE_HTTP_8080=OK`, `BASELINE_HTTP_8081=OK`.

## 3. ACL funcional nftables (B2_L2_06, 19:14:15)

- Tabla `inet nl360_acl`, chain `forward`, política `drop`, `ct state established,related accept`.
- Regla **allow** `iif eth0.110 oif eth0.120 ip saddr 10.70.10.0/24 ip daddr 10.70.20.0/24 tcp dport 8080`: cliente obtuvo `NETLAB360_HTTP_SERVICIO_HQ_VLAN120_OK`, `ACL_HTTP_8080_PERMITIDO=OK`.
- Servidor `:8081` corroborado activo desde su propia namespace: `SERVICIO_8081_EN_VLAN120=ACTIVO`; petición del cliente `:8081` devolvió `curl (28) Connection timed out after 2015 milliseconds` y `ACL_HTTP_8081_DENEGADO=OK`. Timeout corresponde a acción `drop`, no a servicio inactivo.
- Contadores nftables: regla `accept 8080` **1 paquete/60 bytes**, regla `drop 8081` **2 paquetes/120 bytes**, tráfico `established,related` 11 paquetes/883 bytes. `ACL_ROUTER_NAMESPACE=OK`. Este par de pruebas demuestra diferencia observable antes/después de política.

## 4. Limpieza y continuidad (B2_L2_07, 19:15:56)

- `RESULTADO_B2_L2_ACL_HTTP=0` y `RESULTADO_EJECUCION_ACL_HTTP=0`, `RED_GESTION_INTACTA=SI`.
- Docker y `ip netns list` sin residuos. `ens33 UP 192.168.47.40/24` y default `192.168.47.2 dev ens33` intactos. `systemctl is-active docker ssh open-vm-tools` -> tres `active`. Git `## main...origin/main`, `GIT_SINCRONIZADO: SI` en commit `89c2541` antes de actualizaciones documentales.
- Log real guardado localmente en `~/netlab360-bootstrap/evidencias/b2-l2-acl-http-20261013-191413.log`. **NO se ha subido físicamente al repositorio**.
- Capturas `B2_L2_05_Routing_y_HTTP_Sin_ACL.png`, `B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` y `B2_L2_07_Postcheck_ACL_HTTP.png` **se presumen tomadas según instrucción explícita del operador**, pero no se han recibido, inspeccionado ni incorporado físicamente a GitHub.

## 5. Valor probatorio y trabajo pendiente

**Probado:** trunk 802.1Q intra-HQ, router-on-a-stick, routing inter-VLAN, acceso HTTP TCP real y ACL nftables en router aislado (con positivo y negativo controlado), preservación de red de administración. **No probado:** cliente y servicio entre HQ-S1, failover de aplicación real, LACP dual-NIC, SoT/IaC desplegada, integración de esa política a la topología FRRouting, Alertmanager, IA/OVA.

**Matriz interna S01:** B2-L2 **5→8 de 10**, total **55→58% estimado** (+3) por enrutamiento/servicio/ACL verificables, sujeto a la rúbrica docente. No atribuir resultados nuevos al script de siguiente fase no ejecutado.

**Próxima etapa:** integrar dos clientes/servidores Linux realmente direccionados detrás de los routers FRR ya probados, sin cambiar las rutas ni las VLAN de gestión. Preservar `ens33`/VMnet8 y realizar prueba de HTTP por WAN-P, durante WAN-B y tras WAN-P restore con postcheck. No repetir solo ping de interfaces dummy.
