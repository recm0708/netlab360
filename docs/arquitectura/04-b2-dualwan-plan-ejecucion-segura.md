# B2-L3 — Diseño de ejecución FRR R-HQ ↔ R-S1 con dos WAN aisladas

**Fecha de preparación:** 2026-10-13 (Panamá). **Estado:** diseño en preparación, **NO desplegado ni validado en vivo**.  
**Dependencias:** [issue #42](https://github.com/recm0708/netlab360/issues/42), [issue #12](https://github.com/recm0708/netlab360/issues/12), [B1 IPAM](../../inventario/ipam/topologia-b1.yaml) y [smoke FRR v5 exitoso](../sesiones/2026-10-12-smoke-frr-v5-exitoso.md).

## Restricción innegociable

La administración Ubuntu mantiene `ens33=192.168.47.40/24` con puerta de enlace `192.168.47.2` sobre VMware VMnet8 NAT. **Ninguna instrucción de laboratorio debe cambiar ens33, gateway, NetworkManager, iptables/nftables del host ni las redes Docker bridge existentes**. Usar solo contenedores FRR con `--network none` y enlaces veth propios, sin `--network host` ni `--privileged`.

## Mapa de la topología propuesta

| Elemento | R-HQ | R-S1 | Función |
|---|---|---|---|
| loopback lo | 10.79.0.1/32 | 10.79.0.2/32 | Router ID y conectividad de control |
| wan-p | 10.78.0.1/30 | 10.78.0.2/30 | OSPF área 0, costo 10 |
| wan-b | 10.78.0.5/30 | 10.78.0.6/30 | OSPF área 0, costo 100 |
| lan0 (dummy) | 10.70.10.1/24 | 10.71.10.1/24 | Prefijos locales anunciados, sin usuarios aún |
| Contenedor | nl360-b2-r-hq | nl360-b2-r-s1 | Encapsulan FRR; red Docker none |

La implementación final debe usar el diseño IPAM versionado, sin introducir subredes distintas a estas sin registrar una decisión y adaptar el validador.

## Patrón de ejecución propuesto

1. **Pre-check:** validar hostname, IP y rutas del host, IPAM, snapshot confirmado por operador, Docker y herramientas `ip`, `nsenter`, veth. Comprobar si ya existe algún recurso `nl360-b2-`; abortar sin borrar recursos no creados por el mismo proceso.
2. **Provisionamiento aislado:** construir directorios de configuración por router, copiar parámetros del smoke v5 ya comprobado (propietarios `frr:frr` UID100/GID101, `frr.conf` y `vtysh.conf` UID100/GID102, `zebra=yes`, `ospfd=yes`). Montajes tmpfs independientes `/run/frr` y `/var/tmp/frr`; `--network none`, límites de memoria/procesos y capacidades explícitas. `CAP_SYS_ADMIN` tiene alcance elevado: justificarlo solo en VM de laboratorio.
3. **Interfaces:** crear dos pares veth nombrados por el laboratorio; mover los extremos a los **network namespaces de los PID de los contenedores**, renombrar dentro a `wan-p` y `wan-b`, asignar IPv4 /30 y levantar interfaces. Crear `lan0` dummy dentro de cada namespace, asignar /24 y loopback /32. Nunca conectar pares al host `ens33` ni redes de Docker.
4. **Aplicar FRR:** usar candidatas `topologias/b2-frr/configs/R-HQ.frr.conf` y `R-S1.frr.conf`; validar sintaxis y respuesta `vtysh -b` (buscar errores **en texto**, no solo en código de salida). El usuario no debe modificar los `frr.conf` originales sin registrar cambios.
5. **Estado base comprobable:** ambas interfaces WAN arriba, dos vecinos OSPF por router en estado **Full**, prefijo LAN remoto aprendido como `O`, prueba de ping a loopback/prefijo remoto y preferencia del costo 10. Guardar `show ip ospf neighbor`, `show ip route ospf`, `ip route get`, timestamps.
6. **Falla y restauración:** bajar *únicamente* `wan-p` en el namespace de R-HQ, medir tiempos y ruta por WAN-B, restaurar el enlace, verificar retorno por WAN-P. No atribuir convergencia a un simple ping sin corroborar FIB/vecinos.
7. **Rollback:** detener/remover **solo** contenedores y veth del experimento, conservar logs locales, verificar `docker ps -a`, netns, IP/rutas host y servicios; informar resultados y código final. Ante fallo, no repetir hasta analizar los datos.
8. **Trazabilidad:** commit/issue #42 con resultados observados, #12 solo cuando exista falla WAN demostrada. Evidencia con marcadores `INICIO CAPTURA` y `FIN CAPTURA`, nombre PNG y fecha/hostname; se asume tomada por declaración del usuario, pendiente de auditoría visual issue #43.

## Ventana limitada de la sesión (2026-10-13)

- **Hasta 11:45 Panamá:** diseñar y validar fases incrementales, ejecutar solo pruebas con cleanup comprobado y margen suficiente.
- **11:45–12:00:** cerrar un experimento en curso, recopilar logs, documentar y actualizar issues.
- **12:00–12:10:** sincronización completa en GitHub, comprobar que `main` local coincide con remoto y no existen cambios locales por subir, revisar contenedores/netns/red.
- **12:10–12:15:** `sync; sudo systemctl poweroff` y confirmar VMware en `Powered Off` antes de apagar Windows. **12:15 es límite, no hora para comenzar la sincronización**.
- Ninguna prueba ni documentación debe marcarse como realizada si solo se preparó el script. Si una operación falla o demora, priorizar rollback y cierre.

## Criterio para avanzar sin repetir el smoke

**El ensayo v5 ya concluyó satisfactoriamente**: `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`. No repetir versiones v1–v5 ni tratar el smoke como prueba de OSPF entre routers. La siguiente prueba válida debe levantar interfaces y verificar vecinos OSPF Full en dos instancias.
