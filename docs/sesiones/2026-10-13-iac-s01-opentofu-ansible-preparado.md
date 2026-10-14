# NETLAB360 — S01 IaC vertical mínimamente integrada (preparada, sin ejecutar)

> **EJECUCIÓN POSTERIOR CONFIRMADA 13/10 22:30:** el usuario completó todas las fases: plan/apply 5 terraform_data, manifest validado, Ansible FRR candidatos COMPLIANT, segunda ejecución changed=0, Tofu plan sin cambios (rc0), postcheck intacto. **Este documento se conserva como plan previo; estado vigente en [bitácora](2026-10-13-iac-s01-ejecutado.md).** Puntaje provisional S01 68/100. No ejecutar apply nuevamente para tomar fotografías.


**Corte documental:** 13/10/2026 después de la auditoría de 62 PNG. **Estado:** archivos versionados en GitHub; la VM Ubuntu aún debe verificar/ejecutar por primera vez. **No incrementar 65/100** solo por código.

## Contrato técnico y seguridad

1. Fuente única: `inventario/ipam/topologia-b1.yaml` (status draft, no cambiar para esta primera PoC). Las herramientas revalidan IPAM y prohíben cualquier modificación a `ens33=192.168.47.40/24` y GW `192.168.47.2`. Los 3 sitios se leen, pero **S2 está reserved**, así que solo HQ y S1 generan recursos candidatos.
2. OpenTofu 1.13.1 utiliza **solo `terraform_data` built-in** para registrar 1 recurso de guarda de gestión, 2 sitios y 2 enlaces WAN. No instala providers externos, no gestiona interfaces reales. El `terraform.tfstate` se aloja **fuera del clon** en `~/netlab360-bootstrap/iac/s01/work`; **NO subir estado, planes ni tokens** a GitHub.
3. OpenTofu exporta `netlab360_manifest` en JSON a `~/netlab360-bootstrap/iac/s01/manifest.json`; Ansible 2.20.1 lo consume, verifica topología y genera dos ficheros FRRouting candidatos en `~/netlab360-bootstrap/iac/s01/rendered/` con modo 0600. Solo `localhost` (`connection: local`), no SSH, Docker ni redes reales.
4. Un comparador local confronta la secuencia de comandos FRR de ambas candidatas con `topologias/b2-frr/configs/R-HQ.frr.conf` y `R-S1.frr.conf`. Elimina únicamente comentarios/espacios en blanco y descripciones de interfaz (no compara direcciones configuradas en el kernel, que se asignan fuera de FRR). Identidad de secuencia implica **compliance de configuración candidata**, NO que haya cambios aplicados a equipos.
5. Idempotencia: segundo playbook debe terminar **`changed=0`**, y `tofu plan -detailed-exitcode` debe terminar **0** tras el primer `apply`; nunca confundir `plan` con red desplegada.
6. Drift positivo/negativo: el test `tests/test_iac_frr.py` valida `COMPLIANT` con baseline original y detecta `NON_COMPLIANT` al modificar el costo OSPF en **una copia efímera de prueba**. No altera producción ni los archivos versionados.

## Artefactos versionados

- `iac/s01/main.tf`: lee YAML, guarda cambios de datos (no de sistema), estado local fuera del repo, manifiesto exportable.
- `ansible/s01/render-frr.yml`: validación de guardas y dos templates idempotentes.
- `ansible/s01/templates/frr-router.conf.j2`: candidato FRRouting derivado del manifiesto.
- `scripts/validacion/validar-iac-frr.py`: prueba de compliance candidata vs baseline B2.
- `tests/test_iac_frr.py`: test de no-drift y drift controlado.

## Secuencia de verificación en Ubuntu

**No ejecutar comandos sin comprobar estado limpio de Git y red de administración.** Preparar directorio externo:
```bash
cd ~/proyectos/netlab360
ROOT="$PWD"
ART="$HOME/netlab360-bootstrap/iac/s01"
WORK="$ART/work"
install -d -m 0700 "$ART" "$WORK"
cp "$ROOT/iac/s01/main.tf" "$WORK/main.tf"
tofu -chdir="$WORK" fmt
tofu -chdir="$WORK" init -backend=false -input=false -no-color
tofu -chdir="$WORK" validate -no-color
tofu -chdir="$WORK" plan -input=false -no-color -var="sot_path=$ROOT/inventario/ipam/topologia-b1.yaml" -out="$ART/s01-plan.tfplan"
```

Tras revisar el plan, `tofu -chdir="$WORK" apply -input=false -no-color "$ART/s01-plan.tfplan"`. Debe terminar con 5 recursos añadidos; `tofu -chdir="$WORK" output -json netlab360_manifest > "$ART/manifest.json"`. Validar que el manifiesto tiene HQ/S1, sin S2, WAN primaria y respaldo, y guarda de gestión. Luego:
```bash
ansible-playbook -i 'localhost,' -c local ansible/s01/render-frr.yml -e "manifest_path=$ART/manifest.json output_dir=$ART/rendered"
python3 scripts/validacion/validar-iac-frr.py "$ART/rendered"
ansible-playbook -i 'localhost,' -c local ansible/s01/render-frr.yml -e "manifest_path=$ART/manifest.json output_dir=$ART/rendered"
tofu -chdir="$WORK" plan -input=false -no-color -detailed-exitcode -var="sot_path=$ROOT/inventario/ipam/topologia-b1.yaml"
```
**Solo después de salida real exit0, screenshots recibidos y cleanup verificado** elevar evaluación interna.

## Evidencias propuestas para el próximo bloque

1. `IAC_S01_01_Precheck_IPAM_Herramientas.png`: SoT/IPAM aprobado y comandos `tofu version`/`ansible --version`.
2. `IAC_S01_02_Tofu_Plan.png`: recursos guard, HQ/S1, WAN-P/B propuestos, estado exterior.
3. `IAC_S01_03_Tofu_Apply_Manifest.png`: apply exit0 y manifiesto con S2 solo reserved.
4. `IAC_S01_04_Ansible_Render_Candidato_FRR.png`: dos archivos FRR renderizados.
5. `IAC_S01_05_Compliance_FRR.png`: comparación candidata vs baseline.
6. `IAC_S01_06_Idempotencia.png`: Ansible changed=0 y tofu no-change=0.
7. `IAC_S01_07_Postcheck_Final.png`: Docker/netns vacíos; IP/GW/servicios/Git intactos.

**Pendiente posterior:** integrar el estado deseado en el despliegue B2 (FRR vivo) con una puerta de cambio explícita, ownership de configuración, drift/reconciliación de equipos y observabilidad de impacto; no declarar esta etapa como provisioning real de nodos ni cierre de issues #16/#17/#18.
