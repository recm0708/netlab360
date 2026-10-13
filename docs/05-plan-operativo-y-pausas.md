# Plan operativo NETLAB360 — bloques de trabajo, control de cambios y pausas

## ACTUALIZACIÓN PRIORITARIA — 13/10/2026 11:24 | OSPF/ICMP DUAL-WAN OK, S01 42%

**Consultar primero [docs/REANUDAR-AQUI.md](REANUDAR-AQUI.md).** Actualización más reciente y prevalente: dos routers R-HQ/R-S1 OSPF Full por dos WAN, failover `wan-p`→`wan-b` y retorno; 30/30 ICMP bidireccionales entre IP de LAN simuladas de los routers, cinco por dirección en los estados normal, respaldo y restaurado (0% pérdida **en esos sondeos, no durante la transición**). `up/fail/restore/down` terminaron 0; limpieza dejó sin contenedores ni netns y `ens33 192.168.47.40/24` / GW `192.168.47.2` intactos. [Bitácora](sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md). S01 **42% estimado**, fase #1 abierta, #42 y #12 abiertas para medición transitoria, alarma/dashboard, clientes reales y resto del MVP. Logs en `~/netlab360-bootstrap/evidencias`, NO respaldados automáticamente en Git. Capturas solicitadas se asumen tomadas, revisión visual pendiente #43.

**Cierre obligatorio por salida del usuario el 13/10:** desde las **12:00** no iniciar pruebas; sincronizar repo remoto/local y verificar Git limpio y hashes iguales antes 12:10; `sync; sudo systemctl poweroff`, confirmar VMware Powered Off y apagar Windows antes **12:15**. El apagado no consta confirmado.

---


## ACTUALIZACIÓN OPERATIVA — 12/10/2026 23:57 (prioridad sobre estado inicial)

- **Bloques B0 completados operativamente:** VM Ubuntu, Docker/IaC instalados, acceso SSH GitHub, IP `192.168.47.40/24` y snapshot VMware confirmado; issues #39/#40/#41 cerradas. Otros controles de hardening/documentación en #38 permanecen abiertos.
- **B1 validado como diseño DRAFT:** IPAM YAML y colisiones B1 OK, matriz de interfaces/OSPF; #11 y #16 aún abiertas.
- **B2-L2 completado como subprueba:** VLAN110 conectividad 3/3, aislamiento VLAN120, recuperación 3/3, limpieza, código0; trunks/ACL pendientes.
- **B2-L3 validación de arranque local FRR COMPLETA (nuevo):** smoke v5 FRRouting 10.7.1 con `zebra`, `ospfd`, `vtysh` y OSPF local, `RESULTADO_SMOKE_FRR_V5=0`. Log `14-b2-frr-smoke-v5-20261012-235725.log`; [bitácora](sesiones/2026-10-12-smoke-frr-v5-exitoso.md). **No se han formado vecinos OSPF ni probado WAN/conmutación**.
- **Control actualizado:** S01 **~30% estimado** (ponderación [documentada](control/01-avance-s01.md)), 43 issues: 3 cerradas y 40 abiertas; #1 permanece abierta. [Backlog S01](../backlog/semanas/01-semana-1.md).
- **Próximo bloque que se debe ejecutar, no B0 de nuevo:** conectar R-HQ/R-S1 con WAN-P `10.78.0.0/30` costo10 y WAN-B `10.78.0.4/30` costo100; OSPF área0, rutas, failover/restauración, cleanup y evidencias. Diseñar `up/status/down` con aislamiento de VMnet8/ens33. Luego B3 telemetría/API/alarma NOC y B4 analítica.
- **Evidencias:** todas las capturas solicitadas se consideran tomadas por instrucción del usuario; auditoría visual del lote PNG posterior en [#43](https://github.com/recm0708/netlab360/issues/43). Capturas no implican subida GitHub.
- **El apartado "Siguiente ejecución recomendada" al final de este archivo es histórico del 12/10 temprano**, no repetir mantenimiento/bootstrap ya completado. Priorizar esta actualización y `docs/00-estado-y-continuidad.md`.

---

**Fecha de adopción:** 2026-10-12 (Panamá).  
**Alcance:** propuesta de trabajo incremental a validar con el equipo; no altera por sí sola la fecha oficial de entrega ni cierra una fase.  
**Issues:** #1 (S01), #11 (topología/IPAM), #12 (incidente), #15 (dashboard), #16 (Source of Truth), #41 (preparación).

## Estado de partida confirmado

- VMware Workstation Pro 26H1u1 con VM Ubuntu Desktop 26.04.1 LTS, hostname `netlab360-lab`, usuario `rc-aa-ec`; 8 vCPU, RAM 16 GB, disco SCSI 160 GB.
- Gestión NAT **únicamente** por VMnet8, `ens33 192.168.47.40/24`, gateway `192.168.47.2`; no modificar esa red al crear el laboratorio.
- Administración desde Windows por `ssh netlab360`, clave Ed25519 y passphrase local. GitHub CLI reautenticado como `recm0708`; `gh auth setup-git` y `git pull --ff-only origin main` validados en 2026-10-12. Rama `main...origin/main` limpia en ese momento.
- Herramientas instaladas y verificadas en 2026-10-12: Docker Engine 29.9.0, Compose 5.6.0, Buildx 0.38.0, containerd 2.4.1 (hello-world OK), OpenTofu 1.13.1, Ansible Core 2.20.1, Python 3.14.4, Node 24.21.0, npm 11.19.0, GitHub CLI 2.102.0, Git 2.53.0. Servicios docker/ssh/open-vm-tools activos, 136 GB libres.
- Instalador completado (log local `~/netlab360-bootstrap/evidencias/02-preparacion-herramientas-20261012-083150.log`).
- OAuth fue autorizado nuevamente con navegador de Windows. CLI notificó almacenamiento local de credencial sin cifrar en `~/.config/gh/hosts.yml`; proteger permisos y **revocar/eliminar credenciales antes de exportar OVA**. No publicar contenido ni token.
- **No** se han desplegado redes empresariales, routing, API, dashboard, modelos IA ni simulaciones. Fase S01 sigue abierta.

## Principio: verticales demostrables, no bloques aislados

Cada avance técnico debe conectar, siquiera en nivel mínimo, (a) red/segmentación, (b) automatización/estado deseado, (c) telemetría/observabilidad, (d) dashboard/API, (e) diagnóstico/anomalía y (f) pruebas/documentación. Implementar primero un caso real mínimo y ampliar por iteraciones; no presentar capacidades planeadas como implementadas.

## Bloques en orden de ejecución

### B0 — Congelar línea base del entorno (primer control)

**Resultado:** inventario de versiones, salud APT/red/Docker/Git, matriz de compatibilidad, credenciales protegidas y evidencia de bootstrap. Resolver cualquier actualización pendiente mediante pre-check/post-check. Snapshot VMware `NETLAB360-BASE-HERRAMIENTAS` antes de introducir redes complejas (solo después de validar estado consistente).

**Salida:** inventario y checklist de pruebas; #41 en condición de cierre técnico, dejando aparte la pausa si se continúa hoy.

### B1 — Arquitectura mínima e IPAM multisede (primera actividad de diseño)

**Resultado:** diagrama de alto nivel editable y Source of Truth YAML (validable) con sede central HQ y sucursal S1, más espacio direccionable reservado para S2. VLAN distintas para usuarios/servicios/gestión, enlaces WAN de dos rutas y planeación de redundancia. No mezclar el segmento físico VMnet8 `192.168.47.0/24` con redes simuladas.

**Controles:** presupuesto CPU/RAM de 16 GB, compatibilidad Docker/OVS/FRR por namespaces, sin colisiones IP. Distinguir failover de enrutamiento, LACP en extremos compatibles, redundancia de dispositivo, y redundancia de NIC. En B1 no se aseguran aún LACP, VRRP, OSPF ni failover funcional.

**Issues:** #11, #16, #30, #13.

### B2 — Primer escenario ejecutable y fallo demostrable

**Resultado:** topología reproducible HQ–S1 con VLAN, dos enlaces WAN, FRR/OSPF, un servicio extremo a extremo. Simular corte real, medir convergencia/restauración, dejar sello temporal y evidencia operativa. Prueba de infraestructura declarativa y configuración Ansible mínimas, incluso si las implementaciones avanzadas quedan en otras fases.

**Controles:** salud de VMnet8 independiente; conectividad antes/durante/después; captura de comandos y resultados; script de limpieza/rollback.

**Issues:** #12, #14, #17, #18 y #30.

### B3 — Observabilidad, API y vista NOC mínimas

**Resultado:** eventos derivados de las pruebas reales del B2, estados con timestamp y alarmas; exposición de métricas básicas a Prometheus o exporter; API legible y dashboard funcional, aunque con pocas vistas. No simular datos como si fueran mediciones reales.

**Issues:** #15, #20, #21.

### B4 — Analítica inicial y regresión transversal

**Resultado:** baseline de comportamiento basado en datos observados (por ejemplo latencia, pérdida, estado de rutas) con reglas explícitas y prototipo de anomalía *experimental*, sin afirmar IA validada. Ejecutar regresión, restauración y documentación de limitaciones.

**Issues:** #25, #26 y #28.

### B5 — Cierre de Fase 1 y decisiones

Consolidar entregables: informe académico APA 7, bitácora técnica y manual con capturas, commits y resultados. Revisar cada criterio de #1: marcar solo pruebas verificadas; replanificar pendientes con consentimiento del usuario y rúbrica oficial. Si corresponde, preparar snapshot, exportación OVA de la fase con sanitización y verificación independiente (trabajo adicional considerable). 

**Nota de calendario:** S01 fue planificada para 5–11 oct. y el 12 oct. aún no está completada. Registrar desviación y priorizar recuperación; **no** mover automáticamente fechas de S02–S08.

## Política de pausas y continuidad

- **Sin pausas por microtareas.** Mantener el trabajo por unidades con resultado comprobable; ofrecer pausa tras completar **un bloque funcional sustancial** (p.ej. B0+B1 si solo hay planificación, o B2 cuando exista la primera red con failover) o tras una sesión extensa de aproximadamente 2–4 horas. No interrumpir por cada terminal/captura.
- Antes de **pausa breve con VM encendida**: cerrar editores, parar pruebas destructivas, documentar estado, subir Git, comprobar contenedores y puertos publicados, registrar claramente si los servicios deben seguir activos. No crear simulaciones adicionales mientras el usuario no interactúa.
- Antes de **pausa larga/apagado**: salvar evidencias, actualizar informe/manual, Git commit/push, verificar `git status`, guardar versiones, confirmar ausencia de tareas en curso, cerrar servicios transitorios y apagar con `sudo systemctl poweroff`; comprobar VMware apagada. No forzar apagado.
- **Snapshots estratégicos**, no en cada paso: base limpia, después de primera topología funcional, antes de cambios de red potencialmente disruptivos y al alcanzar fases estables. Se recomienda snapshot de VM apagada para consistencia, con límite de espacio y limpieza planificada; snapshot no sustituye respaldo/OVA.
- Al retomar: `ssh netlab360`, inventario/mantenimiento preventivo, `git pull --ff-only`, salud `docker/ssh/open-vm-tools`, IP, recursos, última issue y evidencia; iniciar solo servicios necesarios.
- La pausa se **propone** al cerrar resultados sustanciales; no se apaga sin decisión del usuario o instrucción explícita.
- Cuando la docente publique la rúbrica/fechas, confrontar y registrar cambios controlados.

## Siguiente ejecución recomendada

1. **B0 read-only + mantenimiento:** estado APT, dpkg, servicios, Git, DNS, imagen Docker, espacio, configuración de firewall.
2. Revisar almacenamiento de token CLI y permisos sin mostrar el token; plan de sanitización de OVA.
3. Documentar B0 y decidir snapshot base. 
4. Iniciar B1 (IPAM/diagrama/YAML) en la misma sesión si hay tiempo. Esta será la primera pausa útil después de producir evidencia concreta.

**Fuentes internas:** [README](../README.md), [estado](00-estado-y-continuidad.md), [issues #1](https://github.com/recm0708/netlab360/issues/1), [#41](https://github.com/recm0708/netlab360/issues/41).
