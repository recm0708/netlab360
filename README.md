# NETLAB360

> **ÚNICO CORTE OPERATIVO VIGENTE — S05 145C (15/11/2026):** captura 63 del NOC **recibida, revisada y SHA-256 calculado**; LACP HQ/S1/S2 2/2, Faucet conectado (26 flujos observados en imagen), HTTP HQ principal. 145A y 145B no se repiten. P1/P1B ya tienen interpretación técnica descriptiva. Pendientes: HA de instancia #32, integración y hashes de PNG originales #105, documentación SDN #23, aceptación #5. [Leer corte maestro 145C](docs/gestion/CORTE-MAESTRO-NETLAB360-S05-145C-20261115.md). **Los cortes siguientes en este archivo son antecedentes históricos, no órdenes de ejecución.**


> **CORTE VIGENTE S05 15/11/2026 — 145A/145B COMPLETADOS EN VM**: observador root instalado con respaldo, NOC reiniciado SOLO como servicio y dos muestras reales con FIB principal, HTTP BACKEND_HQ/PRINCIPAL, LACP HQ/S1/S2 2/2, Faucet OpenFlow conectado y 25 flujos; 18 nodos/21 enlaces, warnings=[], seis servicios y gestión estables. **Captura 63 todavía NO tomada**. Leer primero [corte maestro 145B](docs/gestion/CORTE-MAESTRO-NETLAB360-S05-145B-20261115.md) y [auditoría S05–S08 de 24 issues](docs/gestion/AUDITORIA-ISSUES-MILESTONES-S05-S08-145B-20261115.md). Solo avanzar S05, sin ejecutar fases S06/S07/S08. No repetir 145A/B ni fallas WAN/LACP/SDN.

> **CONTINUIDAD 15/11/2026 — S05 L144A/B/C completados, HA HTTP recuperada y verificada con 3 HTTP 200 desde S2.** Avance técnico estimado S05 ~85%, proyecto práctico ~70% (S06/S07 pendientes). [Corte maestro vigente](docs/gestion/CORTE-MAESTRO-NETLAB360-S05-144C-20261115.md) y siguiente implementación real [145A helper seguro](docs/operacion/s05-lote-145a-deploy-helper-seguro-20261115.md) → [145B NOC API](docs/operacion/s05-lote-145b-rollout-noc-api-y-captura-20261115.md). No repetir auditorías 142–144, LACP/SDN ni reiniciar Ubuntu. NOC LACP/SDN **aún no desplegado** hasta confirmar lote 145.

> **ESTADO VIGENTE 15/11/2026 · S05:** [Corte maestro 143A/B/C completados](docs/gestion/CORTE-MAESTRO-NETLAB360-S05-143C-20261115.md). 143A=55/55 pruebas, 143B=6/6 bonds 2/2 + Faucet conectado/25 flujos, 143C=4 tarjetas UI y JS correctos. La API NOC indicó HTTP HA status=offline desde S2 en una muestra válida: diagnosticar con [144A/B/C](docs/operacion/s05-lotes-144a-144c-diagnostico-http-ha-pre-noc-20261115.md). **La extensión NOC LACP/SDN sigue sin instalarse; no reiniciar NOC ni Ubuntu hasta revisar HA.**

> **REANUDAR PROYECTO · 15/11/2026:** [Corte maestro S05, lote 142B detenido](docs/gestion/CORTE-MAESTRO-NETLAB360-S05-142B-20261115.md) · [Procedimiento corregido 143A–143C](docs/operacion/s05-lotes-143a-143c-reparacion-parser-y-continuidad-20261115.md). 142A aprobó 49 pruebas; 142B falló dos veces porque ad_num_ports no aparece en ip JSON (None), 142C no se ejecutó. La ampliación LACP/SDN del NOC existe en GitHub pero **NO se ha desplegado** en la VM. No repetir pruebas LACP/SDN acreditadas ni reiniciar Ubuntu.

**Plataforma virtualizada para la automatización, observabilidad y diagnóstico de redes empresariales multisede.**

Desarrollamos NETLAB360 como proyecto semestral de **Tópicos Especiales II** en la Universidad Tecnológica de Panamá. Integramos tres sedes virtuales (HQ, S1 y S2) para diseñar, validar y documentar conectividad, automatización, supervisión y recuperación de fallos.

## Tecnologías

- **Infraestructura:** VMware Workstation, Ubuntu Desktop, Docker y FRRouting/OSPF.
- **Automatización:** Python, Ansible, OpenTofu y GitHub Actions.
- **Observabilidad:** Prometheus, exportadores propios, NOC web y SQLite.

## Avance verificado — 15/11/2026

| Fase | Alcance | Estado |
|---|---|---|
| S01 | Laboratorio base, conectividad, redundancia y primeros prototipos | **Cerrada** |
| S02 | Topología HQ/S1/S2, cuatro WAN y nueve VLAN | **Cerrada** |
| S03 | SoT candidata, Ansible FRR, 17 metadatos OpenTofu y GitOps | **Cerrada según su alcance real** |
| S04 | NOC multisede, incidente WAN, persistencia y medición SLI | **Cerrada técnicamente** |
| S05 | WAN/HTTP HA y LACP HQ/S1/S2 con fallos 2→1→2 probados; OVS/Faucet aislado y VLAN 410/420 validados, fallo/retorno sdna0 acreditado | **En curso: integrar LACP/SDN al NOC, HA de instancia, evidencias y aceptación** |
| S06–S08 | Diagnóstico IA, integración AIOps y entrega | Pendientes |

No atribuimos al proyecto capacidades aún no implementadas: OpenTofu S03 administra **metadatos locales**, no infraestructura externa. Utilizamos el **99 % como referencia experimental interna** para evaluar el SLI de recolección; la ventana de 60 minutos registró **97,586 %**, por lo que **no cumplió** dicho umbral. No acreditamos notificaciones externas ni un modelo ML entrenado.

La **presentación académica del 30/10/2026 se realizó**. Según la comunicación del equipo, la profesora indicó que el trabajo estaba bien y autorizó continuar con el siguiente entregable. Esto corresponde al avance presentado, no a la evaluación final de S05–S08.

## Documentación y evidencias

- **[Tablero S05 vigente](docs/gestion/s05-tablero-vigente.md)**, [reanudación histórica](docs/REANUDAR-AQUI.md), [auditoría de 50 issues](docs/gestion/auditoria-issues-20261114.md) y [control de fases](docs/control/06-tablero-porcentajes-cierre-fases-2026-10-25.md).
- [Topología multisede](topologias/s02-frr/README.md), [Ansible](ansible/s03/README.md) y [OpenTofu](iac/s03/README.md).
- [Observabilidad](servicios/observabilidad/README.md), [NOC](servicios/noc-s04/README.md) y [capturas](evidencias/capturas/README.md).
- [Issues y próximos entregables](https://github.com/recm0708/netlab360/issues).

Conservamos **122 PNG oficiales** (S01=83, S02=9, S03=8 y S04=22) bajo manifiestos de integridad. El informe unificado de corte es el borrador 4.6, con 113 páginas, 20 figuras y 13 tablas. Para S05, la evidencia de terminal no equivale a PNG original importado: auditoría y SHA-256 binarios están pendientes. Continuaremos sin repetir las fases ya comprobadas.
