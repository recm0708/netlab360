# NETLAB360 — CHECKPOINT CANÓNICO 16/10/2026

## Cambio principal: guías docentes oficiales recibidas

**Un solo informe final académico-técnico** (mínimo **40 páginas**, 12 apartados oficiales), **un PowerPoint con demostración técnica** después de terminar informe, y anexos técnicos de código/configuración. El **ZIP separado** para anexos es PROPUESTA del usuario, **pendiente de confirmación**; manual técnico 02 se pospone a después de finalizar el proyecto, issue #28 conservada. Los tres PDF oficiales adjuntos están registrados por nombre/fecha/SHA en [normativa oficial](academico/00-requisitos-oficiales-2026-10-16.md) pero **sus binarios no están en GitHub**.

**Índice definitivo que exige el PDF** (en ese orden): 1 Portada, 2 Introducción, 3 Objetivos, 4 Planteamiento del problema (incluye justificación), 5 Fundamento técnico, 6 Diseño, 7 Implementación, 8 Pruebas y validación, 9 Análisis de resultados (problemas reales/mitigación), 10 Conclusiones y recomendaciones, 11 Referencias, 12 Anexos.

El usuario tiene borrador en formato institucional de **65 páginas** (S01) revisado en conversación; requiere reordenamiento y mayor profundidad en implementación/pruebas, no rehacer desde cero. [Mapa de migración](academico/01-migracion-borrador-a-formato-docente.md).

## Estado técnico y estrategia para recuperar una semana de desfase

- S01 original y su matriz de 11 criterios eran objetivos **internos**, no rúbrica docente. 72/100 era ponderación **interna**, NO nota ni cierre. Se mantiene abierta #1 para brechas, pero **NO bloquea la implementación siguiente**, en particular ya no depende de Manual 02.
- Ya comprobados VMware Ubuntu/SSH/VMnet8, IPAM HQ/S1 y S2 reservada, VLAN/ACL intra-HQ, FRR/OSPF+HTTP dual WAN HQ–S1 en escenarios separados, LACP/dualNIC virtual, SoT→OpenTofu→Ansible FRR, exporter/NOC/Prometheus, perfil/reglas B4 (sin ML entrenado). 86 PNG/7 CSV hash, 24 tests/CI exitosos.
- **Próximo paso operativo S02:** encender Ubuntu en VMware, verificar solo lectura Git/Docker/netns/ens33/GW/servicios y luego inspeccionar topologías/scripts existentes para planificar una **topología unificada HQ–S1–S2** con VLAN, dos WAN y servicios. No modificar todavía la red de gestión.
- La VM fue apagada ordenadamente por el usuario el 16/10 tras postcheck limpio y `main...origin/main`; estado GUI Powered Off no confirmado. **Ubuntu no incluye estos nuevos commits** hasta ejecutar `git pull --ff-only` cuando se encienda; no usar `reset --hard`.
- [Plan provisional reordenado S02–S08](academico/02-plan-operativo-s02-s08-repriorizado.md). No asignar nuevas fechas docentes ni renombrar milestones hasta recibir transcripción; el número de semana del curso y «S02» interno NO son intercambiables.

## Entregables/integración en paralelo

- ÚNICO informe: [índice maestro oficial](entregables/01-proyecto-investigacion-maestro.md). Se amplía con **implementación, pruebas y comparación esperado vs observado por escenario**, evidencias contextualizadas, incidentes reales en análisis.
- PPT/DEMO al final: [issue #44](https://github.com/recm0708/netlab360/issues/44).
- ZIP de anexos propuesto: [issue #45](https://github.com/recm0708/netlab360/issues/45), pendiente aceptación docente.
- Manual técnico independiente: [issue #28](https://github.com/recm0708/netlab360/issues/28), posentrega, NO bloquear.
- Guía y dudas: [issue #36](https://github.com/recm0708/netlab360/issues/36), [#9](https://github.com/recm0708/netlab360/issues/9).
- **Transcripción de reunión** y **PDF de parcial usado como ejemplo** anunciados, pero no entregados en el lote actual; analizarlos antes de crear requisitos nuevos o desplazar hitos.
- Si el usuario decide recortar alcance, documentar fielmente lo implementado y contrastar contra rúbrica real, sin disfrazar tareas faltantes como completadas.

## Reanudación mínima de Ubuntu (solo cuando usuario lo indique)

```bash
cd ~/proyectos/netlab360
git status --short --branch
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
echo "=== GESTION ==="
ip -4 -br address show ens33; ip route show default
echo "=== ESTADO ==="
sudo docker ps -a; sudo ip netns list
systemctl is-active docker ssh open-vm-tools
git status --short --branch
```

**No iniciar de nuevo OpenTofu apply, cortes WAN o LACP para recuperar capturas.** Priorizar integración progresiva y demo reproducible.
