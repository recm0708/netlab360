# Automatización

## Descripción

Utilizamos una fuente declarativa de información,
Ansible y OpenTofu para comprobar y reconciliar
configuraciones dentro del alcance experimental.

## Validación offline

```bash
ansible-playbook --syntax-check ansible/s03/compliance-frr.yml
tofu -chdir=iac/s03 fmt -check
python3 -m unittest discover -s tests -p 'test_s03_*.py' -v
```

## Consulta de cumplimiento operacional

```bash
sudo -v
python3 scripts/validacion/s03_frr_compliance.py
```

El resultado distingue el cumplimiento observado y las
desviaciones de configuración FRRouting.

## Generación de información declarativa

Preparamos la salida en un directorio privado nuevo:

```bash
python3 scripts/automatizacion/s03_generar_sot.py --output-dir "$HOME/netlab360-bootstrap/sot-nuevo"
```

Revisamos previamente que el destino no contenga información
que deba conservarse.

## OpenTofu y reconciliación

- [Preparador del entorno OpenTofu](../../scripts/laboratorio/s03-preparar-opentofu.sh).
- [Declaración de metadatos](../../iac/s03/main.tf).
- [Validador de planificación](../../scripts/validacion/s03_tofu_plan.py).
- [Playbook de cumplimiento](../../ansible/s03/compliance-frr.yml).
- [Detección de drift](../../ansible/s03/detectar-drift-s1b.yml).
- [Reconciliación selectiva](../../ansible/s03/control-drift-s1b.yml).

La aplicación de OpenTofu requiere revisar el plan y conservar
su estado fuera del repositorio. La reconciliación de costos
OSPF requiere una intervención autorizada.

Los 17 objetos locales terraform_data representan metadatos;
no crean por sí mismos la infraestructura de red.

## Documentación relacionada

- [OpenTofu](../../iac/s03/README.md).
- [Ansible](../../ansible/s03/README.md).
- [GitOps y CI](../../docs/evidencias/s03-gitops-ci-regresion.md).
