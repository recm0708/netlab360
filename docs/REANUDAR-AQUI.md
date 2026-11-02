# NETLAB360 — Punto de reanudación

**Corte de trabajo: 01/11/2026.** S01–S04 cerradas por sus criterios de implementación interna, con todas sus issues de milestones completadas. La profesora confirmó en la sesión del **30/10/2026** que el avance estaba bien y que continuáramos con el siguiente entregable, según informó el equipo. El proyecto semestral **aún no está entregado ni aprobado en su totalidad**.

## Estado

| Fase | Resultado | Issue |
|---|---|---|
| S01 | VMware/Ubuntu, red protegida, OSPF, VLAN/ACL, LACP, SSH ED25519 endurecido | [#1](https://github.com/recm0708/netlab360/issues/1) |
| S02 | HQ/S1/S2, 4 WAN, 9 VLAN, OSPF 4/2/2, fallos y recuperación | [#2](https://github.com/recm0708/netlab360/issues/2) |
| S03 | SoT candidate, Ansible FRR 8/8, drift 100→150→100, OpenTofu metadata-only 17/17 y CI | [#3](https://github.com/recm0708/netlab360/issues/3) |
| S04 | Colector/NOC/Prometheus, alertas y eventos, TSDB/SQLite, SLI medidos | [#4](https://github.com/recm0708/netlab360/issues/4) |
| S05 | Redundancia avanzada, SDN OVS/Faucet y visualización de topología | [#5](https://github.com/recm0708/netlab360/issues/5) |

**S03:** OpenTofu no gestionó recursos externos; ampliación reprogramada a [#17](https://github.com/recm0708/netlab360/issues/17) sin darla por implementada. **S04:** SLI 15m 450/450 (100 %) y 60m 1698/1740 (**97,586 %**, 42 fallos). El umbral 99 % se adoptó como referencia interna, incumplida en 60m; no es SLA ni aprobación individual docente del indicador. Avisos únicamente locales.

**Documento:** borrador 4.6, 113 páginas, figuras 1–20 y tablas 1–13. **Evidencias:** 122 PNG oficiales (83/9/8/22) y manifiestos SHA-256. El próximo encuentro docente previsto es **13/11/2026**, con fundamento técnico y diseño [#48](https://github.com/recm0708/netlab360/issues/48). No se ha celebrado aún.

## Reanudar S05 sin repetir S01–S04

1. Encender la **misma VM** `netlab360-lab` solo cuando se retome el trabajo; no clonar ni restaurar snapshots sin necesidad.
2. Comprobar `ens33=192.168.47.40/24`, gateway `192.168.47.2` y acceso por clave ED25519 desde Windows.
3. Ejecutar `git pull --ff-only origin main` después de confirmar un árbol local limpio.
4. Diseñar primero prechecks, fuentes de estado y reversión para LACP multistream, OVS/Faucet, alta disponibilidad y grafo NOC [#64](https://github.com/recm0708/netlab360/issues/64). Sin inventar tráfico ni alterar la interfaz administrativa.
5. Conservar las pruebas y documentación S01–S04 como historial ya aceptado; crear nuevas evidencias solo para funcionalidades realmente implementadas.

El 01/11 la VM estaba **encendida** durante el cierre de S01; su apagado final de sesión se verificará desde VMware antes de apagar el PC. No deducir estado Powered Off de la bitácora anterior de octubre.

[Control de fases](control/06-tablero-porcentajes-cierre-fases-2026-10-25.md) · [Corte académico](academico/s04-guion-de-actualizacion-del-informe.md).
