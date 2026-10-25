# NETLAB360 — Reanudación técnica y documental

**Corte de trabajo: 25 de octubre de 2026.** Este es el punto de partida vigente; las bitácoras y commits anteriores se conservan como historial verificable. La documentación utiliza la [voz editorial del proyecto](convenciones/01-redaccion-y-nomenclatura.md).

## Estado de la máquina de laboratorio

- Ubuntu Desktop 26.04.1 LTS sobre VMware Workstation; administración por `ens33=192.168.47.40/24`, puerta de enlace `192.168.47.2`, SSH y Docker activos.
- Los routers, enlaces y namespaces de la **fase 2 quedaron desmontados intencionalmente** después de superar los ensayos y guardar configuraciones, estados históricos y registros. No volver a desplegarlos únicamente para repetir capturas.
- OpenTofu de la fase 3 tiene **17 recursos `terraform_data` de metadatos**, aplicados realmente. Su state se conserva **fuera de Git**, bajo `~/netlab360-bootstrap/iac/s03/work/`; no ejecutar otra vez `tofu apply` ni el preparador del workspace. El segundo plan terminó sin cambios.
- Ansible verificó los ocho costos de FRRouting, detectó la desviación controlada `100→150`, restauró `150→100` y comprobó idempotencia. Las pruebas offline posteriores no representan una nueva alteración de FRR.
- Última regresión registrada en Ubuntu: **29/29** pruebas específicas de la fase 2 y **87/87** pruebas generales, sin cambios administrativos.

## Git y control de cambios

- [PR #49](https://github.com/recm0708/netlab360/pull/49): corrección de rutas portables, fusionado. [CI general](https://github.com/recm0708/netlab360/actions/runs/40233355346) y [CI OpenTofu](https://github.com/recm0708/netlab360/actions/runs/40233355350) completadas satisfactoriamente.
- [PR #50](https://github.com/recm0708/netlab360/pull/50): reorganización de **86 PNG de la fase 1** sin modificar bytes; [CI posterior](https://github.com/recm0708/netlab360/actions/runs/40236374576) satisfactoria.
- [Issue #51](https://github.com/recm0708/netlab360/issues/51): auditoría de 111 capturas cerrada con **21 imágenes aprobadas publicadas** (4 complementarias fase1, 9 finales fase2 y 8 finales fase3), y cuatro preliminares excluidas. La auditoría [se documentó aquí](evidencias/09-auditoria-zip-fases1-2-3-2026-10-25.md).
- [PR #53](https://github.com/recm0708/netlab360/pull/53) fusionado: **107 capturas PNG** en `main` (90/9/8), manifestadas y verificadas por SHA-256. La [regresión GitHub Actions posterior a la fusión](https://github.com/recm0708/netlab360/actions/runs/40241580823) fue satisfactoria. No repetir el importador ni volver a subir las fotografías.
- La administración de GitHub, pull requests, issues y Actions queda centralizada en el mantenimiento del repositorio. Los comandos locales se limitan a operaciones de laboratorio o transferencia controlada de archivos, sin requerir revisión manual de PR en navegador.

## Limpieza de ramas e issues — 25/10/2026

- [Limpieza controlada de ramas fusionadas](https://github.com/recm0708/netlab360/actions/runs/40242595670) terminada con resultado SUCCESS: cinco ramas eliminadas tras comprobar PR y SHA; **única rama permanente `main`**.
- Se retiró el workflow temporal y se instaló `.github/workflows/limpiar-rama-tras-merge.yml` para que, en futuros PR fusionados, la rama de origen se elimine después de comprobar que sigue apuntando al SHA incluido en el merge.
- Se cerraron por alcance técnico verificado las issues #10, #11, #12, #13, #14, #18, #19 y #30. Se consolidaron #9→#36 y #37→#29, sin perder sus pendientes futuros.
- Permanecen abiertas las **tres issues generales #1, #2 y #3** únicamente hasta superar sus puertas explícitas. Las funciones de NOC S04, LACP S05 y entrega S08 dejaron de figurar como exigencias del cierre funcional de S02.
- [Puertas de cierre S01–S03](control/07-puertas-cierre-fases1-a-3-2026-10-25.md): **S01** requiere verificación/decisión SSH y compatibilidad fundacional; **S02** figura 1 + revisión/aceptación del escrito; **S03** formalización del contrato SoT y alcance OpenTofu, más incorporación académica en 5.5/6/7/8. No repetir pruebas completas para completar capturas.

## Indicadores de avance

| Fase | Corte actual | Pendiente para aceptación |
|---|---:|---|
| 1 | 72 % histórico | Decidir el cierre administrativo de la línea base sin atribuir las fases posteriores a esta fase |
| 2 | ≈90 % | Evidencias publicadas; resta aceptación documental y Figura 1 del informe |
| 3 | ≈90 % | Evidencias publicadas; delimitar OpenTofu metadata-only e integrar resultados al informe |
| 4–8 | 0 % de aceptación formal | Implementación, pruebas y entregables propios de cada fase |

[Tablero completo de criterios](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md). Las funciones experimentales de fases previas no se contabilizan como aceptación formal de fases posteriores.

## Informe académico y entregables

- Última exportación revisada: `1457-Proyecto Semestral_borrador3.pdf`, **79 páginas**. Falta incorporar la fase 3 al apartado 5.5, actualizar pruebas en 6, análisis en 7 y conclusiones en 8; mantener los capítulos 1–8 coherentes.
- Corregir en Word el marcador de la **Figura 1** y las referencias narrativas residuales a anexos o a `S01`/`S02` cuando estos códigos no formen parte de archivos.
- Según la modalidad docente registrada, la entrega académica termina en **Referencias**, **sin capítulo de anexos**. El código, YAML/JSON, pruebas y evidencias seleccionadas se entregarán en un **archivo `.tar` externo**.
- Revisiones docentes: 30/10 (introducción, objetivos y planteamiento) y 13/11 (fundamento y diseño). Confirmar sus resultados reales antes de registrar aprobación.
- No incluir credenciales, claves SSH privadas, planes/state OpenTofu o archivos de clase en el TAR.

## Siguiente secuencia

1. Mantener la rama única `main`, el inventario de **107 capturas** y los manifiestos SHA-256 ya verificados.
2. Resolver la aceptación fundacional de la fase 1 sin alterar FRRouting: SSH seguro con rollback y notas de compatibilidad.
3. Completar la Figura 1 y corregir el corte escrito de fase 2, registrando su aceptación.
4. Incorporar la fase 3 al Word (5.5, 6, 7, 8), delimitar SoT/OpenTofu y registrar su aceptación.
5. Preparar el corte académico 30/10 y continuar las fases 4–8 por sus propios hitos.

**Conservación histórica:** las sesiones detalladas permanecen en [`docs/sesiones/`](sesiones/), las decisiones en [`docs/academico/`](academico/) y los resultados de auditoría en [`docs/evidencias/`](evidencias/). Los registros cronológicos anteriores también son recuperables mediante el historial Git, sin duplicarlos en este punto de reanudación.
