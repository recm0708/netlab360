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
