> **S02 17/10/2026, 16:56 (Panamá): PRIMER ARRANQUE FRR INCOMPLETO.** `docker compose config` pasó y 3 bind mounts aislados `network_mode:none` fueron confirmados. **La preparación externa `runtime/` falló** (exit 1 antes de finalizar R-HQ; falta `runtime/R-HQ/frr.conf`), pero `compose up -d` fue ejecutado: R-HQ inicialmente running con errores en `/etc/frr/vtysh.conf` y `frr.conf processing failure: 11`; R-S1/R-S2 `Exited(1)`. `ens33 .40/24` y gateway `.2` intactos, Git limpio. Captura S02_05 tomada **NO ES EVIDENCIA DE ÉXITO**, conservar como registro diagnóstico. **NO repetir up ni iniciar WAN**. Próximo: capturar logs/inspect de los 3 routers y listado `runtime/`, retirar solo el stack S02 vía `docker compose ... down` DESPUÉS de recolectar logs, auditar la plantilla `/etc/frr/daemons` y reparar con puertas de control; snapshot VMware disponible. [Issue #2](https://github.com/recm0708/netlab360/issues/2).

> **S02 17/10, 16:31 -05:** SSH recuperado/reconectado desde Windows, `sshd -t=0`, precheck S02=0, snapshot confirmado. Primera construcción siguiente = **tres contenedores FRR aislados `network_mode: none`** mediante [Compose y README](../topologias/s02-frr/README.md). **AÚN NO ejecutado; NO existen cuatro WAN S02 operativas**. No utilizar el orquestador WAN Bash no publicado. Recolectar evidencia `S02_05_FRR_Tres_Routers_Aislados` solo tras `docker compose up -d` y verificación de host intacto. La issue #38 sigue abierta por hardening de contraseñas, no por conectividad actual.

> **S02 17/10, 16:13 (-05), actualización:** captura S02_03 declarada tomada, FRR 3/3 candidatas con hashes inalterados. OpenSSH escucha por `ssh.socket`, pero `/run/sshd` falta y `sudo sshd -t` devolvió 255. **NO desplegar** hasta revisar/crear únicamente ese directorio temporal si corresponde, validar sintaxis (0), abrir **segunda sesión SSH desde Windows** dejando primera abierta y ejecutar `scripts/diagnostico/precheck-s02.sh`. Instantánea VMware declarada creada por usuario. [Issue #2](https://github.com/recm0708/netlab360/issues/2), [issue #38](https://github.com/recm0708/netlab360/issues/38). El GitHub remoto contiene nuevos commits posteriores al último pull de Ubuntu (`6c35b24`); sincronizar antes de precheck.

> **NUEVO PRECHECK 17/10/2026, 16:08 (-05):** render FRR 3/3 correcto y unit tests 4/4, snapshot VMware confirmado por usuario. SSH.service **inactive** (Docker/open-vm-tools active) pese a sesión SSH ya abierta. Antes del despliegue S02 verificar `ssh.socket`, `sshd -t`, listener y **nueva sesión SSH independiente**. No reiniciar ni cambiar daemon SSH ni modificar ens33 sin consola VMware. [Registro completo](sesiones/2026-10-17-s02-integracion-multisede-plan.md). GitHub avanzado después del commit Ubuntu `6db0fab`: sincronizar antes de siguiente prueba.

# NETLAB360 — REANUDAR AQUÍ (17/10/2026)

## Decisiones y fechas efectivas

**No publicar en GitHub archivos de clase, documentos docentes, grabaciones, transcripciones ni sus SHA256.** Usar solamente [criterios de trabajo resumidos](academico/00-criterios-docentes-y-hitos.md).

**Proyecto final grupal:**
1. **UN informe académico-técnico** (>=40 páginas), 12 apartados: Portada; Introducción; Objetivos; Planteamiento del problema; Fundamento técnico; Diseño; Implementación; Pruebas y validación; Análisis de resultados; Conclusiones y recomendaciones; Referencias; Anexos.
2. **El estudiante confirmó el 17/10 que el título fue enviado al chat Teams**. **La aprobación/revisión docente continúa pendiente**. Consultar al usuario antes de afirmar que se presentó.
3. **30/10/2026**: mostrar en **Teams** el borrador con **introducción, objetivo general/específicos y planteamiento del problema**, mediante **representante del grupo**. No se pide presentación PowerPoint para este corte.
4. **13/11/2026**: mostrar avance con **fundamento técnico y diseño de la solución**, continuidad del mismo documento.
5. **Anexos técnicos en archivo separado permitidos expresamente**, presentados junto con informe. Crear ZIP solo con archivos propios del proyecto y manifiesto SHA256; no confundir autorización de formato con aprobación de un ZIP ya construido.
6. **Presentación PowerPoint y DEMOSTRACIÓN EN VIVO** al final; derivar la presentación del informe, explicar decisiones técnicas, mostrar red, degradación/fallas, recuperación y datos reales. Fecha/duración final no comunicadas en la reunión.
7. Manual técnico independiente #28 **POSPUESTO**, no requerido en las entregas académicas actuales.

**PARCIAL 1**: individual, entrega hasta 25/10/2026, también calificado como Laboratorio 5 en UNA sola carga en espacio del parcial. **Se desarrolla EN OTRO CHAT y no es parte del semestral**. Podrá inspirar ensayos técnicos más exigentes pero no autoriza mezclar evidencias, sistemas ni rúbricas.

## Estado técnico comprobado

- **S01 issue #1 ABIERTA**, por objetivos internos integrales pendientes; **72/100 es únicamente estimación interna histórica**, NO calificación. Las guías docentes ya permiten planificación progresiva; no bloquear S02 por manual ni por completar todas las metas S03/S06/S08 anticipadamente.
- Ubuntu Desktop VMware / VMnet8 gestión `ens33 192.168.47.40/24` GW `.2`; SSH Ed25519 y servicios operativos, **contraseñas SSH habilitadas**, hardening #38 pendiente.
- HQ/S1 ensayos FRR OSPF doble WAN, VLAN HQ/ACL en topología diferente; S2 reservada; LACP virtual y active-backup virtual; IaC OpenTofu/Ansible→FRR, drift **de copias**, exporter/NOC/Prometheus inicial, perfil B4 por reglas **no IA evaluada**.
- **86 PNG y 7 CSV SHA256 de pruebas propias** en GitHub, 24 tests/CI correctas. VM apagada ordenadamente después de Docker/netns vacíos, Git local limpio y ruta de gestión estable.
- El repositorio en GitHub **se modificó desde ese apagado**; al reiniciar el Ubuntu local se debe sincronizar mediante `git pull --ff-only`, **sin borrar cambios locales**.

## Ruta de trabajo inmediata

1. El **título formal ya fue enviado a Teams** (confirmado por el estudiante); esperar observaciones/aprobación de la profesora, sin reenviarlo automáticamente.
2. Congelar los textos del corte académico **30/10** reutilizando el borrador Word del usuario (introducción, objetivos y planteamiento) y verificar encabezados/citas.
3. Continuar integración **S02**: [plan de arquitectura CANDIDATA y precheck de 17/10](sesiones/2026-10-17-s02-integracion-multisede-plan.md). Ubuntu ya fue encendido por el usuario y `git pull --ff-only` confirmó Fast-forward limpio hasta `94339de` antes de los nuevos commits de documentación. **Se debe volver a sincronizar** y ejecutar precheck de solo lectura. S2 permanece `reserved` en IPAM B1; enlaces S2 son propuestas, NO redes ya activas. No modificar `ens33`.
4. Avanzar simultáneamente el contenido técnico de **Fundamento técnico + Diseño** para revisión **13/11**; registrar evidencias de implementación/pruebas para final.
5. Posteriormente completar informe, validar ZIP de código, preparar **PowerPoint extraído del informe y demo EN VIVO**; manual técnico posentrega.

**Índice de informe:** [maestro](entregables/01-proyecto-investigacion-maestro.md) · [mapa Word previo](academico/01-migracion-borrador-a-formato-docente.md) · [cronograma técnico](academico/02-plan-operativo-s02-s08-repriorizado.md).

## Arranque seguro Ubuntu / precheck (VM ya encendida por el usuario 17/10)

```bash
cd ~/proyectos/netlab360
git status --short --branch
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git status --short --branch
ip -4 -br addr show ens33
ip -4 route show default
sudo docker ps -a
sudo ip netns list
systemctl is-active docker ssh open-vm-tools
```

No correr `tofu apply`, scripts de modificación de interfaz o cortes WAN sin precheck, plan, recuperación y autorización. Reproducir pruebas anteriores **solo si hace falta integración funcional**.
