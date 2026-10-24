# NETLAB360 S03 — OpenTofu y GitOps sin riesgo para infraestructura viva

**Estado:** código preparado y publicado en GitHub el 23/10/2026. **No se ha ejecutado todavía en la VM del estudiante**; no afirmar `tofu plan/apply` aprobado antes de resultados reales.

## Alcance exacto

El archivo `iac/s03/main.tf` define exclusivamente **17 recursos `terraform_data` del proveedor integrado**: 1 guarda de red administrativa `ens33 / 192.168.47.40/24 / GW .2`, 3 sedes HQ/S1/S2, 4 WAN OSPF primarias/respaldo y 9 VLAN. Lee `inventario/ipam/topologia-s02.yaml` en estado `candidate` y lo almacena como metadatos declarativos en un archivo de state **fuera del clon Git**. **NO administra contenedores, enlaces veth, FRR, interfaces, VLAN ni firewall live; no ejecuta provisioners ni necesita proveedor Docker/Libvirt.** El componente que maneja FRR real sigue siendo Ansible mediante operaciones protegidas (véase `ansible/s03/README.md`).

OpenTofu `terraform_data` **sí** tiene ciclo de vida de estado (plan, creación, modificaciones, drift del dato declarado) pero **no equivale a aprovisionamiento real de FRR**. Esta distinción debe conservarse en el informe.

Documentación oficial: https://opentofu.org/docs/language/resources/tf-data/

## Pasos operativos previstos (probar resultados, no asumir)

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
python3 -m py_compile scripts/validacion/s03-tofu-manifest.py scripts/validacion/s03-tofu-plan.py
python3 -m unittest discover -s tests -p 'test_s03_opentofu.py' -v
python3 -m unittest discover -s tests -p 'test_s03_tofu_plan.py' -v

ROOT="$HOME/proyectos/netlab360"
ART="$HOME/netlab360-bootstrap/iac/s03"
WORK="$ART/work"
# Verificar ausencia de un state antiguo; NO sobrescribir work ya existente.
mkdir -p "$WORK"
chmod 700 "$ART" "$WORK"
cp -n "$ROOT/iac/s03/main.tf" "$WORK/main.tf"
tofu -chdir="$WORK" init -backend=false -input=false -no-color
tofu -chdir="$WORK" validate -no-color
tofu -chdir="$WORK" plan -input=false -no-color \
  -var="sot_path=$ROOT/inventario/ipam/topologia-s02.yaml" \
  -out="$ART/s03-plan.tfplan"
tofu -chdir="$WORK" show -json "$ART/s03-plan.tfplan" > "$ART/s03-plan.json"
python3 scripts/validacion/s03-tofu-plan.py "$ART/s03-plan.json"
```

**Puerta de cambio:** comprobar `S03_PLAN_SOLO_TERRAFORM_DATA=17/17` y `S03_PLAN_ACCIONES_EXCLUSIVAS=CREATE` **ANTES** de ejecutar `tofu apply -input=false -no-color "$ART/s03-plan.tfplan"`. Verificar `Apply complete! Resources: 17 added, 0 changed, 0 destroyed.`. Si el plan es diferente, DETENER: no aplicar.

Tras apply, exportar `tofu -chdir="$WORK" output -json s03_manifest > "$ART/s03-manifest.json"` y validar `python3 scripts/validacion/s03-tofu-manifest.py "$ART/s03-manifest.json"`: 3/3 sitios, 4/4 WAN, 9/9 VLAN y estado = 17/17. Repetir `tofu plan -detailed-exitcode` con la misma var; **0 significa sin cambios**, 2 significa cambios planificados (no confundir con error). Nunca destruir estados S01 para completar esta fase.

## CI/GitOps (solo offline)

Nuevo workflow `.github/workflows/ci-s03-sot-opentofu.yml`, con acceso de solo lectura al repositorio: Python/PyYAML; tests `test_s03_*.py`, OpenTofu 1.13.1, `init`, `validate`, `plan` de 17 metadatos. Se activa en PR, push de los archivos S03 y workflow_dispatch. Nunca ejecuta `tofu apply`, ni SSH/Ansible/FRR sobre una VM. **Estado GitHub Actions por verificar** mediante interfaz o herramienta antes de considerarlo éxito.

## Evidencia

- `S03_06_OpenTofu_Plan_17_Recursos_SoT`: salida del validador del plan previa a cualquier apply.
- `S03_07_OpenTofu_Apply_Manifesto_17_Recursos`: apply 17/17 y cotejo de 3 sedes, 4 WAN y 9 VLAN del manifiesto.
- `S03_08_OpenTofu_Segundo_Plan_Sin_Cambios`: segundo plan con exit 0 y postcheck OSPF/LAN/gateway sin cambios.
- `S03_09_GitOps_CI_Regresion_PullRequest`: únicamente si GitHub Actions muestra ejecución verde real (no simular status).
