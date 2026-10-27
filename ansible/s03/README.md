# NETLAB360 S03 — Ansible y cumplimiento de FRRouting

**Estado comprobado al 27/10/2026: implementación y pruebas S03 ejecutadas sobre FRR activo.** La VM está apagada después del cierre operativo S04.

## Funciones verificadas

Ansible utiliza el SoT derivado de `inventario/ipam/topologia-s02.yaml` y el inventario renderizado en `~/netlab360-bootstrap/s03/rendered/inventory-s03.yml` para evaluar los parámetros de tres routers FRRouting. Comprobó ocho costos OSPF (10 en las WAN principales y 100 en las de respaldo) y vecindades Full HQ/S1/S2 = 4/2/2.

Se realizó una desviación real sobre R-S1/s1b, costo **100→150**, que fue detectada como `NON_COMPLIANT`; la reconciliación selectiva restauró **150→100** y una segunda ejecución produjo `changed=0`. Se validaron el estado final de OSPF, la administración `ens33` y los procedimientos de privilegios.

## Código y seguridad

- `ansible/s03/compliance-frr.yml`: consultas de cumplimiento.
- `ansible/s03/`: roles y procedimientos de reconciliación controlados.
- `scripts/validacion/s03-frr-compliance.py`: validación del estado activo.
- `tests/test_s03_frr_compliance.py`: pruebas offline correspondientes.

Las tareas privilegiadas deben restringirse exclusivamente a los contenedores autorizados y disponer de comprobación previa, copia de estado y reversión. **No volver a desplegar FRR para editar el Word**. Al iniciar S05, consultar [continuidad](../../docs/REANUDAR-AQUI.md) y revalidar el entorno antes de cualquier prueba.

La aceptación formal del SoT `candidate` y los límites de propiedad de los cambios continúan en [issue #16](https://github.com/recm0708/netlab360/issues/16).
