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

El usuario ejecutó correctamente la compilación y **5/5 tests offline**, el inventario/syntax-check y la auditoría directa `s03-frr-compliance.py` (**8/8 costos COMPLIANT**, exit 0). Las **dos** ejecuciones del playbook Ansible original fallaron (exit 2, `failed=1` por router) porque los forks `ansible.builtin.command` invocaban `sudo -n docker inspect` sin compartir caché `sudo -v` de la terminal; código `sudo: interactive authentication is required`. Los tres routers/gestión permanecieron intactos según precheck; Ansible no modificó FRR porque la tarea fallida era de solo lectura. **NO capturar esas salidas como compliance Ansible exitoso, ni continuar a drift.**

**Corrección publicada, sin prueba real Ubuntu aún:** la tarea de consulta utiliza `become: true`, `become_method: sudo`, `environment.HOME` del controlador normal para que el script encuentre `~/netlab360-bootstrap` en lugar de `/root`, `changed_when: false`, con autenticación `--ask-become-pass`. No se habilita contraseña permanente ni NOPASSWD, no se toca Docker socket, sólo un proceso read-only del auditor. El playbook fija intérprete local `/usr/bin/python3` y se añade test de alcance/elevación `tests/test_s03_ansible_compliance.py`.

**Puerta de control:** nuevo git pull, py_compile/test nuevo (4/4), syntax-check, `sudo -v`, auditoría directa 8/8, playbook corregido en **dos ejecuciones** con `--ask-become-pass`, esperar `changed=0`, `failed=0`, `unreachable=0` en los tres. Si falla, detener avance con logs. **No ejecutar la prueba drift/reconciliación hasta esto.**

## Problema real con sudo-rs (23/10/2026, segunda correccion)

Dos ejecuciones previas con `become:true` y `--ask-become-pass` llegaron a fallar (`RESULTADO_ANSIBLE_CORREGIDO_1=4`; 3 routers `unreachable=1`) con:

```text
Timed out waiting for become success or become password prompt.
[sudo: [sudo via ansible, key=...] password:] Contraseña:
```

**Causa técnica confirmada por documentación Ubuntu y bug de Ansible**: en Ubuntu 26.04 `sudo-rs` es el proveedor predeterminado de `sudo`; su prefijo adicional al prompt impide que el módulo `become` de la versión instalada de Ansible reconozca la solicitud. Esto es distinto del problema inicial de credenciales de los workers y no lo arregla ejecutar `sudo -v`. La referencia Ubuntu permite expresamente usar `/usr/bin/sudo.ws`, la implementación clásica, manteniendo `sudo-rs` como predeterminada.

**Solución de alcance mínimo publicada pero sin ejecución Ubuntu aún:** dentro de la tarea read-only `Verificar costos OSPF reales contra fuente de verdad`, `vars.ansible_become_exe=/usr/bin/sudo.ws`; el resto del playbook no adquiere privilegios. Se conserva `--ask-become-pass`, `HOME` del usuario para el SoT, sin editar `/etc/sudoers` ni `update-alternatives` del host. Actualizado test `test_s03_ansible_compliance.py` para comprobar este alcance. **Antes de ejecutar** confirmar `test -x /usr/bin/sudo.ws` y `sudo.ws --version`; si falta, detener y diagnosticar, NO cambiar el proveedor global por anticipado.

Referencias: https://ubuntu.com/server/docs/security-users/ ; https://ubuntu.com/server/docs/reference/other-tools/sudo-rs/ ; https://bugs.launchpad.net/bugs/2122414
