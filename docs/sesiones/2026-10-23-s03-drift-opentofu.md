# NETLAB360 — S03: Ansible drift real validado y OpenTofu S03 preparado

**Corte real registrado:** 23/10/2026 20:54 (-05). Este documento separa operaciones ejecutadas por el estudiante de nuevo código remoto no probado. No convierte las fechas S01–S08 en plazos de la docente.

## Evidencia Ansible real, aprobada
Fuente: salida de terminal de 514 líneas proporcionada por el usuario:
- Git local `1dba348` limpio; compilación 0, tests drift 7/7, sintaxis playbooks 0.
- WAN OSPF 0, LAN 0 y compliance costos FRR 8/8 al comenzar; archivo drift state AUSENTE; gestión `ens33=192.168.47.40/24`, GW `192.168.47.2`.
- Auditoría `inspect` Ansible R-S1/s1b: costo 100, Full 4/2/2, FIB primarias 3/3, `changed=0`, exit 0.
- Inyección R-S1/s1b WAN secundaria **100→150** mediante Ansible: `changed=1`, exit 0, Full/FIB/host intactos. El comando incluyó `snapshot_s03=true` pero la existencia de una nueva instantánea en interfaz VMware **no fue inspeccionada**.
- Detección real con Ansible `NON_COMPLIANT ESPERADO=100 OBSERVADO=150`, 1 desviación, exit 0, `changed=0`. Salida S03_04 a las 20:52:51.
- Primera reconciliación mediante Ansible 150→100 `changed=1`, exit 0; segunda reconciliación `changed=0`, exit 0. Esto **sí** demuestra idempotencia real de configuración. Salida S03_05 a las 20:54:13.
- Auditoría post 8/8 costos COMPLIANT, OSPF 0, LAN 0, tres FRR running, VMnet8 intacta, `drift-s1b-state.json` AUSENTE; 5 logs de operaciones preservados localmente.
- Los comandos de captura S03_04 y S03_05 se ejecutaron y resultaron válidos; **el guardado físico de sus PNG no se ha confirmado explícitamente** en conversación.

## Preparación OpenTofu S03 NO ejecutada todavía
- Módulo `iac/s03/main.tf` representa metadata de 1 guarda gestión, 3 sedes, 4 WAN y 9 VLAN con 17 recursos `terraform_data` del proveedor integrado. **No configura FRR ni enlaces, ni es ownership remoto de contenedores**; titularidad real de FRR sigue delimitada por Ansible/IDs Docker.
- `scripts/laboratorio/s03-preparar-opentofu.sh` prepara workspace fuera de Git sin sobrescribir existente. `s03-tofu-plan.py` exige 17 acciones `create` y solo proveedor integrado; `s03-tofu-manifest.py` valida cardinalidad e integridad hash SoT. Tests `test_s03_opentofu.py` y `test_s03_tofu_plan.py`.
- Workflow `.github/workflows/ci-s03-sot-opentofu.yml` ejecuta solo pruebas offline, `init`, `validate`, `plan`, nunca `apply`. **No hay evidencia de ejecución CI aprobada aún**.
- Objetivo próximo: plan validado, snapshot de metadata local 17 recursos, output JSON cruzado con SoT, segundo plan exit 0 sin diferencias y regresiones OSPF/LAN 0; luego PR GitOps real de prueba. No guardar state/plan/secretos en el repo.

## Documentación académica
Primera revisión institucional del informe único en Teams **30/10/2026**, tema Introducción/Objetivos/Planteamiento; segunda **13/11** Fundamento y Diseño. La operación S03 aporta evidencias técnicas para secciones implementación, pruebas y análisis, pero no sustituye estos cortes. Título docente aún por confirmar.
