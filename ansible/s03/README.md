# NETLAB360 S03 — Ansible sobre tres FRRouting LIVE, auditoría read-only

Estado a 23/10/2026: **código publicado, aún no ejecutado en Ubuntu por estudiante**. Baseline previo observado real S03_02 sí verificado: 3 loopbacks, 9 VLAN, 8 interfaces WAN, OSPF Full 4+2+2 y dos lecturas idénticas.

## Objetivos
El SoT sigue como `candidate`, derivado exclusivamente de `inventario/ipam/topologia-s02.yaml`; inventario operativo generado en `$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml`. Este playbook **no edita ni reconcilia** routers. Lee el `show running-config` real de FRRouting 10.7.1 y verifica que las 8 interfaces WAN mantengan sus costos OSPF (10 primaria/100 respaldo), junto a vecindades Full. El verificador limita pertenencia mediante Docker ID previamente guardado en `wan-links-state.json`, etiqueta Compose, estado running y `network_mode:none`. Verifica ens33 `.40/24` y gateway `.2`.

## Ejecución y gates

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
python3 -m py_compile scripts/validacion/s03-frr-compliance.py tests/test_s03_frr_compliance.py
python3 -m unittest discover -s tests -p 'test_s03_frr_compliance.py' -v
ansible-playbook -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/compliance-frr.yml --syntax-check
sudo -v
sudo -n true
python3 scripts/validacion/s03-frr-compliance.py
# El playbook usa become SOLO en la tarea de consulta de FRR;
# --ask-become-pass abre el prompt interactivo de Ansible.
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/compliance-frr.yml
```

**Éxito estricto:** primer script `S03_COSTOS_WAN_COMPLIANT=8/8`, `S03_COMPLIANCE_RESULTADO=COMPLIANT`, y Ansible recap con `changed=0`, `failed=0` y `unreachable=0` para R-HQ, R-S1 y R-S2. Repetir read-only para verificar estabilidad; `changed=0` **no constituye idempotencia de configuración**, porque no hay `apply`. Nunca declarar reconciliación o drift live comprobados antes de probarlos.

## Próxima evolución
Planificar drift controlado exclusivamente de **un costo OSPF de enlace de respaldo** y su reconciliación de `100` mediante Ansible con precheck estado (4+2+2 Full, seis FIB principales y protección ens33). Exigir snapshots VMware, una ventana de recuperación y un guard de propiedad de la interfaz. Ningún `tofu apply` contra recursos S02 activos ni `vtysh configure terminal` sin prueba aprobada. En paralelo IaC OpenTofu con state/lifecycle y revisión de PR/CI.

El corte de documento único 30/10 Teams y el de 13/11 permanecen prioritarios.


## Incidente real de autenticacion (23/10/2026, ~20:26 -05)

Se ejecutaron correctamente la compilación y **5/5 tests offline**, el inventario/syntax-check y la auditoría directa `s03-frr-compliance.py` (**8/8 costos COMPLIANT**, exit 0). Las **dos** ejecuciones del playbook Ansible original fallaron (exit 2, `failed=1` por router) porque los forks `ansible.builtin.command` invocaban `sudo -n docker inspect` sin compartir caché `sudo -v` de la terminal; código `sudo: interactive authentication is required`. Los tres routers/gestión permanecieron intactos según precheck; Ansible no modificó FRR porque la tarea fallida era de solo lectura. **NO capturar esas salidas como compliance Ansible exitoso, ni continuar a drift.**

**Corrección publicada, sin prueba real Ubuntu aún:** la tarea de consulta utiliza `become: true`, `become_method: sudo`, `environment.HOME` del controlador normal para que el script encuentre `~/netlab360-bootstrap` en lugar de `/root`, `changed_when: false`, con autenticación `--ask-become-pass`. No se habilita contraseña permanente ni NOPASSWD, no se toca Docker socket, sólo un proceso read-only del auditor. El playbook fija intérprete local `/usr/bin/python3` y se añade test de alcance/elevación `tests/test_s03_ansible_compliance.py`.

**Puerta de control:** nuevo git pull, py_compile/test nuevo (4/4), syntax-check, `sudo -v`, auditoría directa 8/8, playbook corregido en **dos ejecuciones** con `--ask-become-pass`, esperar `changed=0`, `failed=0`, `unreachable=0` en los tres. Si falla, detener avance con logs. **No ejecutar la prueba drift/reconciliación hasta esto.**

## Problema real con sudo-rs (23/10/2026, segunda correccion)

Dos ejecuciones previas con `become:true` y `--ask-become-pass` llegaron a fallar (`RESULTADO_ANSIBLE_CORREGIDO_1=4`; 3 routers `unreachable=1`) con:

```text
Timed out waiting for become success or become password prompt.
[sudo: [sudo via ansible, key=...] password:] Contraseña:
```

**Causa técnica confirmada por documentación Ubuntu y bug de Ansible**: en Ubuntu 26.04 `sudo-rs` es el proveedor predeterminado de `sudo`; su prefijo adicional al prompt impide que el módulo `become` de la versión instalada de Ansible reconozca la solicitud. Esto es distinto del problema inicial de credenciales de los workers y no lo arregla ejecutar `sudo -v`. La referencia Ubuntu permite expresamente usar `/usr/bin/sudo.ws`, la implementación clásica, manteniendo `sudo-rs` como predeterminada.

**Solución de alcance mínimo publicada pero sin ejecución Ubuntu aún:** dentro de la tarea read-only `Verificar costos OSPF reales contra fuente de verdad`, `vars.ansible_become_exe=/usr/bin/sudo.ws`; el resto del playbook no adquiere privilegios. Se conserva `--ask-become-pass`, `HOME` de la cuenta operativa para el SoT, sin editar `/etc/sudoers` ni `update-alternatives` del host. Actualizado test `test_s03_ansible_compliance.py` para comprobar este alcance. **Antes de ejecutar** confirmar `test -x /usr/bin/sudo.ws` y `sudo.ws --version`; si falta, detener y diagnosticar, NO cambiar el proveedor global por anticipado.

Referencias: https://ubuntu.com/server/docs/security-users/ ; https://ubuntu.com/server/docs/reference/other-tools/sudo-rs/ ; https://bugs.launchpad.net/bugs/2122414


## Experimento S03: drift controlado de un enlace de RESPALDO (preparado, SIN ejecutar aún)

### Línea base REAL acreditada 23/10/2026 20:42 -05

- Ubuntu `sudo-rs` sigue predeterminado; `/usr/bin/sudo.ws` 1.9.17p2 disponible sin cambiar alternativas.
- Commit VM `bc32964`; `test_s03_ansible_compliance.py` 4/4, syntax-check 0; audit directo 8/8 OSPF COMPLIANT.
- Ansible R-HQ individual éxito; dos ejecuciones de los 3 routers con recap **ok=3 changed=0 failed=0 unreachable=0** en HQ/S1/S2, salida exit 0.
- OSPF y LAN postcheck exit 0, 3 routers corriendo, gestión VMnet8 `ens33 .40/24`, gateway `.2`.
- Captura `S03_03` comandos ejecutados, **PNG guardado aún no confirmado**.

### Diseño nuevo (solo código GitHub; requiere prueba local antes de cambios)

Archivos: `scripts/laboratorio/s03-drift-s1b.py`, `ansible/s03/control-drift-s1b.yml`, `ansible/s03/detectar-drift-s1b.yml` y `tests/test_s03_drift_s1b.py`.

1. **Solo R-S1, interfaz s1b (WAN RESPALDO)**. Baseline declarado 100; desviación controlada 150; primaria s1p sigue 10. La modificación es SOLO running-config FRR por `vtysh`; **NO ejecuta `write memory`**, no altera enlaces ni direcciones de host.
2. `inspect` solo lee WAN/LAN state, SoT y ocho costos FRR, verifica IDs/etiquetas de los 3 contenedores, OSPF Full4+2+2, tres rutas primarias FIB, ens33 y rutas del host.
3. `inject` requiere `snapshot_s03=true` y preflight de ocho costos conformes, guarda un state de propiedad `~/netlab360-bootstrap/s03/drift-s1b-state.json` ANTES de escribir costo 150; valida resto de costos, FIB, vecinos y host. Si falla intenta volver a 100 y conserva state si la restauración no se valida.
4. `detectar-drift-s1b.yml` consulta `s03-frr-compliance.py --router R-S1` sin editar y acepta rc=2 solo si muestra explícitamente `NON_COMPLIANT ESPERADO=100 OBSERVADO=150`; la tarea no marca changed.
5. `reconcile` dentro de playbook Ansible usa SoT esperado 100, revisa ownership y state, aplica una sola actualización `150→100` si corresponde y valida ruta/FULL/host; `changed=1`. Segunda ejecución `reconcile` con costo ya 100 no reconfigura ni cambia: `changed=0` (idempotencia REAL de apply). Si aparece costo desconocido, contenedor reemplazado o state ajeno, rechaza intervenir.
6. `become` con `sudo.ws` SOLO en tarea que consulta o modifica FRR, `HOME` de la cuenta operativa preservado; contraseña por `--ask-become-pass`. NO configurar `NOPASSWD` ni editar `/etc/sudoers`.
7. **NUEVO SNAPSHOT VMWARE** obligatorio antes de ejecutar `inject`; scripts con `--syntax-check` y pruebas offline 7/7 en 0; baseline live 8/8 COMPLIANT y FRR rutas/vecinos aptos.

Comandos de operación (su ejecución real debe demostrarse primero en VM):

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
python3 -m py_compile scripts/laboratorio/s03-drift-s1b.py tests/test_s03_drift_s1b.py
python3 -m unittest discover -s tests -p 'test_s03_drift_s1b.py' -v
ansible-playbook -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/control-drift-s1b.yml --syntax-check
ansible-playbook -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/detectar-drift-s1b.yml --syntax-check
# snapshot VMware creado/confirmado; precheck del host y compliance baselines
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/control-drift-s1b.yml -e operacion_s03=inspect
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/control-drift-s1b.yml -e operacion_s03=inject -e snapshot_s03=true
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/detectar-drift-s1b.yml
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/control-drift-s1b.yml -e operacion_s03=reconcile
ansible-playbook --ask-become-pass -i "$HOME/netlab360-bootstrap/s03/rendered/inventory-s03.yml" ansible/s03/control-drift-s1b.yml -e operacion_s03=reconcile
```

**STOP si cualquier comando de modificación/report falla**, NO reinyectar sobre drift existente. Si se interrumpe entre inyección y reconciliación, el comando `reconcile` es el mecanismo acotado de recuperación, incluso después de error de detección, pero solamente cuando la comprobación de propiedad siga siendo válida. Si estado/direcciones no coinciden, preservar logs/estado y diagnosticar, no eliminar tablas o contenedores. Validar siempre `validar-ospf-s02.py`, `validar-lan-s02.py` y auditoría directa 8/8 después de recuperar.
