# NETLAB360 — Operación segura y pausas (revisión 16/10)

**Nuevo contrato académico:** un informe final >=40 páginas, PowerPoint+demostración obligatorios, anexos técnicos; ZIP separado pendiente de validación docente. Manual 02 pospuesto. Ver [guías](academico/00-requisitos-oficiales-2026-10-16.md) y [checkpoint](REANUDAR-AQUI.md).

## Estado seguro último
- Ubuntu apagado ordenadamente por comando `sudo systemctl poweroff` tras `docker ps -a` y `ip netns list` vacíos, `ens33 192.168.47.40/24`, gateway `192.168.47.2` y Git `main...origin/main`, 16/10.
- SSH Ed25519 operativa; `sshd -T` mostró `passwordauthentication yes`, por tanto #38 permanece abierta. No endurecer sin consola VMware y rollback probado.
- GUI VMware `Powered Off` no confirmada desde herramientas; no presumir.

## Regla para futuras sesiones integradoras
1. Arrancar solo VM necesaria; verificar consola, host, Git remoto vs local y acceso SSH.
2. Ejecutar `git status --short --branch` **antes** de `git pull --ff-only origin main`; nunca reset --hard ni push --force.
3. Precheck de Docker/netns, ens33, GW y servicios; registrar fecha/hora, commit, entorno.
4. Diseñar topología aislada HQ–S1–S2 con VLAN y doble WAN; **no alterar ens33/VMnet8**. Cada falla tendrá rollback localizado, no borrado global.
5. Medir y documentar **baseline→cambio→esperado/real→restauración**, acompañando evidencia/resultado técnico.
6. Hacer postcheck Docker/netns, servicios, red administrativa, Git y luego commit/push seguro.
7. **No repetir** LACP, Prometheus o `tofu apply` únicamente para capturar imágenes ya auditadas.
8. Actualizar el ÚNICO informe en sus secciones 7–9 con resultados nuevos; generar ZIP solo después de revisión de alcance y secretos.

## Pausa y recuperación
En sesiones largas, detener escenarios temporales, conservar logs/artefactos no secretos, verificar estado y apagar Ubuntu **desde su SO** si el operador lo ordena. No ejecutar `poweroff` automáticamente por indicación general. Reanudar desde [plan S02–S08](academico/02-plan-operativo-s02-s08-repriorizado.md).

**Las fases S01–S08 son hitos internos revisables**; no son calendario oficial confirmado, la transcripción docente está pendiente.
