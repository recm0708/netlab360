# Automatización y cumplimiento FRRouting — S03

Implementamos el flujo de auditoría y reconciliación con Ansible sobre los routers FRRouting de HQ, S1 y S2. Consumimos el inventario candidato [`topologia-s02.yaml`](../../inventario/ipam/topologia-s02.yaml) y el inventario de ejecución generado fuera del repositorio en `~/netlab360-bootstrap/s03/rendered/inventory-s03.yml`.

## Componentes

- [`compliance-frr.yml`](compliance-frr.yml): evaluación de los parámetros de FRR en funcionamiento.
- Roles y tareas de este directorio: reconciliación selectiva de la configuración autorizada.
- [Validador de cumplimiento](../../scripts/validacion/s03-frr-compliance.py) y [pruebas offline](../../tests/test_s03_frr_compliance.py).

## Resultados

Comprobamos **8/8 costos OSPF**, con costos principales de 10 y de respaldo de 100. Introdujimos una desviación controlada en R-S1/s1b (**100→150**), obtuvimos `NON_COMPLIANT`, restablecimos **150→100** y verificamos idempotencia (`changed=0`). Las vecindades OSPF registradas fueron **4/2/2 Full**.

**Alcance:** Ansible administra configuración FRR activa; OpenTofu S03 mantiene exclusivamente metadatos locales. El estado de la SoT sigue siendo `candidate`, válido para el laboratorio y no equivalente a aprobación de producción. No ejecutamos una nueva reconciliación sin un precheck y una necesidad técnica concreta.

[Contrato SoT](../../docs/validacion/s01-s04-resultados.md) · [OpenTofu](../../iac/s03/README.md).
