# Preparación previa a la pausa — NETLAB360

**Fase:** S01. **Issue:** #41. Este archivo explica un instalador de herramientas base. No debe usarse para desplegar los laboratorios ni modificar los adaptadores de red.

## Requisitos previos

- Ubuntu Desktop 26.04.1, hostname netlab360-lab y usuario rc-aa-ec.
- SSH desde Windows: ssh netlab360, IP estática 192.168.47.40.
- Repositorio privado clonado en ~/proyectos/netlab360 y autenticación gh comprobada.
- Tener acceso sudo en el invitado.
- No compartir contraseñas ni credenciales del CLI en evidencias.

## Ejecución

Desde la sesión SSH Ubuntu:

~~~bash
cd ~/proyectos/netlab360
git pull --ff-only origin main
bash -n scripts/bootstrap/preparar-entorno-ubuntu.sh
bash scripts/bootstrap/preparar-entorno-ubuntu.sh
~~~

El instalador valida SO, arquitectura y hostname; realiza mantenimiento de APT e instala utilidades base, GitHub CLI desde repositorio oficial, Docker Engine/Compose/Buildx del repositorio firmado, OpenTofu del repositorio oficial y Node.js 24 LTS desde NodeSource con clave GPG. Ansible y las herramientas de red se instalan desde APT de Ubuntu.

El script **no** añade el usuario al grupo docker (dicho grupo da permisos equivalentes a root), **no** modifica SSH, UFW, Netplan ni interfaces y **no** crea ni despliega topologías. Los comandos Docker se realizan con sudo.

Si un comando falla, detenerse y revisar el log; no apagar ni dar por terminado.

## Evidencias de salida

El script crea un log local en:
~/netlab360-bootstrap/evidencias/02-preparacion-herramientas-AAAAMMDD-HHMMSS.log

Revisar y compartir solo la salida de versiones/estados, sin secretos. Después de ejecutarlo:

~~~bash
cd ~/proyectos/netlab360
git status --short --branch
gh auth status
sudo docker ps -a
sudo docker image ls
systemctl is-active docker ssh open-vm-tools
ip -4 -br address show ens33
df -h /
~~~

No incorporar datos secretos de ~/.config/gh, ~/.ssh o /var/lib/docker al repositorio. No apagar hasta validar y documentar.

## Aplazamientos deliberados

- Containerlab: su script de configuración documenta pruebas hasta Ubuntu 24.04; revisar compatibilidad Ubuntu 26.04 antes de instalar.
- Faucet, Open vSwitch y FRRouting: se desplegarán en escenarios aislados y versionados, no como servicios indiscriminados del anfitrión.
- Prometheus, Alertmanager, APIs FastAPI, dashboard React y analítica IA: imágenes/entornos versionados tras definir la arquitectura.
- La plantilla NETLAB360 v0.2 se importará tras verificar que no sobrescribe documentación reciente.

## Apagado

Cuando pruebas, documentación y repositorio estén revisados:

~~~bash
sync
sudo systemctl poweroff
~~~

El cliente SSH se desconectará. Confirmar en VMware que la VM aparece apagada. No emplear «Power Off» forzado salvo bloqueo real. Para regresar, arrancar VM, conectar por ssh netlab360, comprobar herramientas y continuar con la issue pendiente.

## Fuentes de instalación oficiales

- Docker: https://docs.docker.com/engine/install/ubuntu/
- GitHub CLI: https://github.com/cli/cli/blob/trunk/docs/install_linux.md
- OpenTofu: https://opentofu.org/docs/intro/install/
- Node.js (LTS): https://github.com/nodejs/Release
- NodeSource: https://github.com/nodesource/distributions
