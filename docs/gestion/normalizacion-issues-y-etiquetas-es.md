# NETLAB360 — Normalización de issues y etiquetas en español

## Alcance auditado

Inventario GitHub del 23/11/2026: **53 issues reales** (PR excluidos), distribuidas entre las ocho milestones S01–S08. Las issues cerradas carecen de casillas sin marcar; las abiertas conservan requisitos futuros sin completar. **No se cerrará ni reabrirá ninguna issue como resultado de este cambio.** La issue #5 permanece cerrada en S05, cuyo porcentaje el operador ya comprobó visualmente al 100 % tras la reparación del contador. La ejecución previa del reconciliador reportó RC=1 durante la desasignación transitoria de #5, pero se ha verificado que #5 está de nuevo asignada a S05; **no volver a ejecutar `--apply` del script antiguo de milestones**.

## Política de títulos

Se unificaron directamente en GitHub todas las issues bajo el patrón **`[SNN] Descripción concreta de la capacidad, actividad u objetivo`**. El identificador SNN coincide con la milestone asignada; los títulos nunca contienen la indicación administrativa `CERRADA`, `PENDIENTE`, `VALIDADA`, `NO IMPLEMENTADA` o `COMPLETADA`. Se mantienen términos técnicos y marcas propias como FRRouting, OSPF, LACP, NOC, GitOps, OpenTofu, WireGuard, VLAN, CI, TAR y OVA. El estado real pertenece al campo GitHub `open/closed` y el motivo `completed/not_planned/duplicate`, no al título.

## Política de etiquetas

Se utiliza un catálogo reducido con significado concreto, nombre y **descripción completos en español**: exactamente una etiqueta `fase:01`…`fase:08`, una etiqueta temática `tipo:<dominio>`, más solo si aplica **`alcance:opcional`** o **`prioridad:alta`**. No se repite una prioridad por defecto en las 53 issues ni se añade una etiqueta que no describa el trabajo.

Los temas disponibles abarcan infraestructura, enrutamiento, automatización, observabilidad, telemetría, seguridad, disponibilidad, SDN, documentación, datos, inteligencia artificial, entrega, gestión académica, pruebas y visualización. La prioridad alta solo aparece en issues abiertas que bloquean entregables centrales: #6, #7, #8, #25, #26, #27, #43, #44, #45 y #106. Las opcionales son #17, #24, #28, #29 y #37, sin convertirlas en requisito obligatorio.

Aliases históricos: `semana:NN`→`fase:NN`, `tipo:infra`→`tipo:infraestructura`, `tipo:docs`→`tipo:documentación`, `tipo:dashboard`→`tipo:visualización`, `tipo:telemetria`→`tipo:telemetría`, `tipo:ia`→`tipo:inteligencia-artificial` y `tipo:automatizacion`→`tipo:automatización`. Si existen labels predeterminadas en inglés se normalizan (`bug`, `documentation`, `enhancement`, `duplicate`, `invalid`, etc.) sin perder su asignación en PR. Las etiquetas obsoletas solo se eliminan tras comprobar ausencia de referencias, incluidas PR. Las etiquetas desconocidas **bloquean** la aplicación: no se borran ni se renombran mediante inferencia.

## Ejecución

Se integró `scripts/operacion/normalizar_issues_etiquetas.py` con `--check` (read-only) y `--apply` (actualiza exclusivamente definiciones de labels y asignaciones de etiquetas a issues/PR). Necesita `gh api` autenticado en la VM; el conector GitHub no expone creación/renombrado de las definiciones de labels. `--check` valida los 53 IDs, títulos, milestones, estados y casillas, además de inventariar etiquetas desconocidas. `--apply` realiza migración y revisa convergencia completa; solo se deben aplicar cambios si la lista de etiquetas desconocidas está vacía. El comando no edita cuerpos, checkboxes, estados, milestones ni contenido del repositorio.

El script puede actualizar labels de PR *únicamente si conserva un alias obsoleto cuya denominación no se pudo renombrar por colisión*, para evitar perder significado; el resto de sus labels se conserva. Se niega a suprimir cualquier alias todavía referenciado.

## Fase S06 y siguiente hito

El estudio prospectivo V2 de S06 y su auditoría científica read-only están aceptados en VM: TRAIN/VALIDATION/TEST con muestreo uniforme, modelos congelados, F1 TEST P95/IF/LR de 0.941/0.941/1.000 para HQ→S1 y 1.000/0.941/1.000 para HQ→S2, y oportunidad temporal retrospectiva de 1416/1402 ms. Concept drift inferencial y pronóstico/MAE no son evaluables con este corpus; **FAULT independiente aún no verificado**. Mantener las issues #6/#25/#26 abiertas y la estimación de ~90 % técnico, sin confundirla con la barra GitHub. El siguiente procedimiento operativo será comprobar primero el candidato controlado de falla de backend HTTP HQ y verificar vigilancia/rescate antes de ejecutar un ensayo nuevo.

## Validación de la implementación en GitHub (23/11/2026)

Los **53 títulos se actualizaron directamente** mediante el conector GitHub y se comprobó el patrón `[SNN]`; ninguna issue cerrada tiene casillas pendientes. Se verificó de forma independiente la milestone **S05: 6 issues cerradas, 0 abiertas, contador nativo 6/6 = 100 %**, y la issue #5 permanece asociada a S05. PR [#182](https://github.com/recm0708/netlab360/pull/182) fusionado con **874 pruebas CI (873 aprobadas, una omitida)**. La aplicación de nombres/descripciones de **etiquetas** requiere ejecutar `--apply` con la autenticación existente de `gh` en la VM; el conector disponible no expone esa operación. **Las etiquetas no se consideran migradas hasta obtener `NORMALIZACION_ISSUES_COMPLETA=OK` en la VM**.

## Ajuste de las dos etiquetas no catalogadas y títulos de PR (23/11/2026)

La primera ejecución `--apply` se detuvo **antes de modificar etiquetas**, al encontrar `accessibility` y `estado:bloqueado`. Se conservó el inventario: 53 issues reales (37 cerradas, 16 abiertas), las 53 con título correcto y ninguna cerrada con casillas pendientes. El catálogo actualizado mapea `accessibility` a **`tipo:accesibilidad`** con descripción en español, y mantiene **`estado:bloqueado`** como etiqueta nativa en español para una dependencia realmente impeditiva, sin asignarla indiscriminadamente. Sus definiciones no deben borrarse por estar temporalmente sin uso. La aplicación efectiva sigue pendiente de `gh api --apply` validado en VM; **no confundir una CI aprobada con la mutación de etiquetas aplicada**.

Adicionalmente, se normalizaron **directamente en GitHub los 129 pull requests históricos**, todos fusionados y ninguno abierto, con la convención `[SNN] Descripción técnica` o `[GESTIÓN] Descripción de actividades transversales`. Se preservaron términos propios de herramientas como FRRouting, OSPF, VLAN, OpenFlow, Ansible, Docker, ICMP y GitOps, así como todos los estados/commits. La verificación por API devolvió **129 de 129** títulos dentro del patrón y cero títulos fuera del formato; `scripts/operacion/auditar_titulos_prs.py --check` permite auditar nuevas solicitudes antes de cerrarlas.

Los títulos de PR describen el cambio; no incluyen los distintivos administrativos `CERRADA/PENDIENTE`. Si apareciera un PR nuevo, se debe utilizar la misma convención; los PR no se consideran issues de planificación y no deben recibir un nuevo milestone ficticio.

## Estado posterior a las correcciones (23/11/2026)

PR [#183](https://github.com/recm0708/netlab360/pull/183) fusionado como `53d46bb` con 883 pruebas CI (882 OK, una omitida): `accessibility` se interpreta como `tipo:accesibilidad`; `estado:bloqueado` se conserva como definición española con semántica de dependencia. **Aún falta ejecutar `--apply` desde la VM** para efectuar la migración real del catálogo de labels. Tras fusionar el PR del escenario FAULT S06, la consulta directa confirma **131 PR, los 131 fusionados, cero abiertos, cero títulos fuera de `[SNN]`/`[GESTIÓN]`**. La milestone S05 continúa 6 cerradas/0 abiertas, issue #5 correctamente asignada. Nunca repetir el reconciliador antiguo por este motivo.


## Auditoría acumulada de PR tras el arreglo de S06

Tras fusionar [#185](https://github.com/recm0708/netlab360/pull/185), la consulta a GitHub confirmó **132 PR fusionados, cero abiertos y 132 títulos ajustados** al patrón `[SNN]` / `[GESTIÓN]`. Las cifras históricas de 129 y 131 registradas arriba corresponden a cortes anteriores, no al inventario actual. Este dato puede aumentar con futuros PR; validar nuevamente con `scripts/operacion/auditar_titulos_prs.py --check`. La migración del catálogo de etiquetas todavía requiere `--apply` real en VM.

## Reanudación tras la migración parcial de etiquetas (23/11/2026)

La ejecución desde la VM pasó 16 pruebas FAULT aisladas y ocho de gestión de GitHub. Durante `--apply`, GitHub aceptó los renombrados iniciales de etiquetas, pero respondió **HTTP 422** al actualizar `estado:bloqueado`. La descripción original tenía 110 caracteres y excedía el máximo de 100 caracteres que GitHub permite. Esta corrección la acorta sin cambiar su semántica y añade una comprobación preventiva de todas las definiciones antes de cualquier escritura en API, junto con pruebas de regresión.

La migración queda **parcialmente aplicada** hasta que una nueva ejecución en VM complete el `--check`, continúe `--apply` de manera idempotente y verifique que todos los diagnósticos queden vacíos. No se requiere ni se autoriza repetir TRAIN/VALIDATION/TEST ni el experimento FAULT por este error. La bitácora de la reanudación fallida permanece bajo `~/netlab360-bootstrap/s06/reanudacion-fault-20261123_122220/`.

## Normalización real completa — verificación final del 23/11/2026

La VM sincronizó la corrección de descripción de etiquetas y ejecutó la reanudación, con `NORMALIZACION_ISSUES_COMPLETA=OK` y `S06_GITHUB_REANUDACION=OK`, RC=0. La auditoría posterior devolvió **cinco diagnósticos vacíos**: asignaciones incorrectas, etiquetas canónicas faltantes, descripciones desactualizadas, aliases históricos y nombres desconocidos. Quedaron **53 issues reales** (37 cerradas, 16 abiertas), 53 títulos normalizados, ninguna cerrada con casillas pendientes y la milestone S05 cerrada con 6/6 issues. Al cierre de este corte había **133 PR fusionados**, ninguno abierto, todos con títulos conformes. Los números de PR de apartados anteriores son cortes históricos; no representan el inventario posterior.

La migración respetó estados, casillas y milestones y corrigió la colisión `documentation` → `tipo:documentación` sin pérdida de asignaciones. Bitácora privada `~/netlab360-bootstrap/s06/reanudacion-github-20261123T173351Z/S06_Reanudacion_Github.txt`. **No repetir `--apply` por este resultado satisfactorio**. El avance científico S06 se gestiona separadamente del catálogo GitHub.
