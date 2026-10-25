# NETLAB360 S03 — OpenTofu y GitOps sin riesgo para infraestructura viva

**Estado actualizado 25/10/2026:** `init`, `validate`, plan seguro de 17 creaciones y `apply` **17 added, 0 changed, 0 destroyed** verificados realmente en Ubuntu. Manifiesto 3 sedes/4 WAN/9 VLAN y segundo plan **sin cambios (código 0)** también confirmados, conservando `ens33` y la fase 2 pausada. El state permanece fuera del repositorio y no debe incorporarse al TAR. [Sesión verificada](../../docs/sesiones/2026-10-25-s03-opentofu-metadata-ci.md). CI específica S03 y PR #49 de regresión global también comprobados; validar checks de `main` posteriores al merge y confirmar capturas guardadas. Las instrucciones de preparación que siguen son **para un workspace nuevo**, no para volver a aplicar el estado ya creado.

## Alcance exacto

El archivo `iac/s03/main.tf` define exclusivamente **17 recursos `terraform_data` del proveedor integrado**: 1 guarda de red administrativa `ens33 / 192.168.47.40/24 / GW .2`, 3 sedes HQ/S1/S2, 4 WAN OSPF primarias/respaldo y 9 VLAN. Lee `inventario/ipam/topologia-s02.yaml` en estado `candidate` y lo almacena como metadatos declarativos en un archivo de state **fuera del clon Git**. **NO administra contenedores, enlaces veth, FRR, interfaces, VLAN ni firewall live; no ejecuta provisioners ni necesita proveedor Docker/Libvirt.** El componente que maneja FRR real sigue siendo Ansible mediante operaciones protegidas (véase `ansible/s03/README.md`).

OpenTofu `terraform_data` **sí** tiene ciclo de vida de estado (plan, creación, modificaciones, drift del dato declarado) pero **no equivale a aprovisionamiento real de FRR**. Esta distinción debe conservarse en el informe.

Documentación oficial: https://opentofu.org/docs/language/resources/tf-data/

## Reanudación segura si la fase 2 está pausada

**Actualización 25/10/2026:** la infraestructura WAN/LAN de la fase 2 fue **desmontada intencionalmente** después de aprobar sus pruebas y conservar respaldos. Como OpenTofu administra exclusivamente metadatos, no necesita reconstruir esa red para operar.

El preparador `scripts/laboratorio/s03-preparar-opentofu.sh` acepta **dos modos explícitos**: `S03_TOFU_MODO_S02=DESPLEGADA_CON_ESTADOS` (ambos estados WAN/LAN presentes) o `S03_TOFU_MODO_S02=PAUSADA_Y_LIMPIA` (ambos ausentes, sin contenedores FRR S02 ni namespaces S02 detectables). Estados parciales, Docker sin permisos de inspección o residuos detectados detienen la preparación. La rama pausada requiere `sudo -v` en la terminal antes de llamar al preparador, sin modificar sudoers. **No arrancar S02 únicamente para crear los 17 metadatos**.

El preparador rechaza cualquier workspace o plan previo y comprueba la red administrativa. No invocar `tofu init`, `plan` o `apply` hasta verificar la situación real del host y un `git pull --ff-only` limpio. Si ya existiera un directorio `~/netlab360-bootstrap/iac/s03/work` o cualquier state antiguo, **no sobrescribir, mover ni borrar**: diagnosticar primero.

**Regresión OSPF/LAN:** ejecutarla solamente si la topología de la fase 2 está efectivamente desplegada. Cuando está pausada, acreditar el modo limpio y la gestión intacta, sin pretender ejecutar comprobaciones FRR en dispositivos inexistentes.

## Pasos operativos previstos (probar resultados, no asumir)

```bash
cd ~/proyectos/netlab360
git status --short --branch
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
sudo -v
bash -n scripts/laboratorio/s03-preparar-opentofu.sh
python3 -m py_compile scripts/validacion/s03-tofu-manifest.py scripts/validacion/s03-tofu-plan.py
python3 -m unittest discover -s tests -p 'test_s03_opentofu.py' -v
python3 -m unittest discover -s tests -p 'test_s03_tofu_plan.py' -v

ROOT="$HOME/proyectos/netlab360"
ART="$HOME/netlab360-bootstrap/iac/s03"
WORK="$ART/work"
# Verificar ausencia de un state antiguo; NO sobrescribir work ya existente.
bash scripts/laboratorio/s03-preparar-opentofu.sh
# El script anterior genera $WORK/main.tf; no recrear work ni copiar a mano.
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

## Historial de aplicación en la VM

El estado OpenTofu de fase 3 ya existe en `~/netlab360-bootstrap/iac/s03/work`. **NO ejecutar de nuevo** el preparador de inicialización, no sobrescribir ni borrar `terraform.tfstate` y no ejecutar `tofu apply` para repetir las capturas. Para read-only usar `tofu state list`, `tofu output -json s03_manifest` y `tofu plan -detailed-exitcode`, siempre con la variable `sot_path` correcta; las comprobaciones existentes están documentadas en la sesión del 25/10. Mantener los 17 metadatos fuera del paquete TAR final.

## CI/GitOps (solo offline)

Nuevo workflow `.github/workflows/ci-s03-sot-opentofu.yml`, con acceso de solo lectura al repositorio: Python/PyYAML; tests `test_s03_*.py`, OpenTofu 1.13.1, `init`, `validate`, `plan` de 17 metadatos. Se activa en PR, push de los archivos S03 y workflow_dispatch. Nunca ejecuta `tofu apply`, ni SSH/Ansible/FRR sobre una VM. **Estado GitHub Actions por verificar** mediante interfaz o herramienta antes de considerarlo éxito.

## Evidencia

- `S03_06_OpenTofu_Plan_17_Recursos_SoT`: salida del validador del plan previa a cualquier apply.
- `S03_07_OpenTofu_Apply_Manifesto_17_Recursos`: apply 17/17 y cotejo de 3 sedes, 4 WAN y 9 VLAN del manifiesto.
- `S03_08_OpenTofu_Segundo_Plan_Sin_Cambios`: segundo plan con exit 0 y postcheck OSPF/LAN/gateway sin cambios.
- `S03_09_GitOps_CI_Regresion_PullRequest`: únicamente si GitHub Actions muestra ejecución verde real (no simular status).
