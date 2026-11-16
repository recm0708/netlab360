# Archivo temporal de continuidad — NETLAB360

Esta carpeta conserva **material interno de seguimiento**, fuera de la documentación técnica que integra el proyecto. Reunimos aquí bitácoras de sesiones, cortes de progreso, planes de trabajo, guiones de redacción, auditorías de seguimiento y pruebas asociadas a procedimientos históricos.

## Situación recuperable

La integración técnica S05 fue comprobada: 21 namespaces, cuatro contenedores, seis unidades activas, OSPF, LACP, OVS/Faucet, NOC y un ciclo de conmutación HTTP HQ→S1→HQ en 17 muestras. Los **77 archivos de evidencias S05** están fusionados en `main` mediante el PR #152 (71 PNG, tres manifiestos, inventario y dos registros HA).

La arquitectura y los resultados verificables permanecen fuera de esta carpeta, en la documentación técnica, el código y `evidencias/`. El desarrollo académico continúa con el **informe único** (issue #27); después corresponde S06 y posteriormente S07/S08. No se declara concluido lo que aún no ha sido comprobado.

## Acceso al histórico

La estructura reproduce las rutas originales añadiendo el prefijo `docs/_temporal_continuidad/`, por ejemplo:

- `docs/REANUDAR-AQUI.md`: puntos de continuación antiguos (pueden estar superados)
- `docs/gestion/`: auditorías de issues, tableros y cortes históricos
- `docs/sesiones/`: bitácoras de operación
- `docs/operacion/`: lotes y procedimientos de ejecución
- `docs/academico/` y `docs/entregables/`: planes de redacción y control de versiones del informe
- `backlog/semanas/`: planificación interna anterior
- `tests/test_s05_lacp_runbook_gates.py`: prueba del runbook archivado, excluida de la CI vigente

Las rutas de enlaces dentro de estos archivos proceden del histórico; algunas dejaron de ser navegables tras la reubicación. La referencia técnica vigente es el repositorio principal, no los avisos antiguos de continuidad.

## Política de eliminación

Este directorio es **temporal y no es un entregable del proyecto**. Una vez terminadas las ocho fases, el informe y la preparación del paquete final, se eliminará del árbol de `main` tras revisar que no contiene evidencias únicas no preservadas. La operación no reescribe el historial de Git. No incluir esta carpeta en el TAR final.

## Conservación de la VM

El cierre de S05 no significa que sea seguro ejecutar `poweroff` sobre Ubuntu. Los 21 namespaces son efímeros; para detener el trabajo conservando el escenario se utiliza **Suspend en VMware Workstation**. La reconstrucción tras reinicio del invitado permanece pendiente en la issue #106.
