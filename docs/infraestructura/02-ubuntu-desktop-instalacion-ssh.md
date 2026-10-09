# NETLAB360 — Guía 01: Ubuntu Desktop y acceso SSH desde Windows

**Estado (2026-10-09):** Ubuntu 26.04.1 instalado y actualizado; SSH y VMware Tools activos. IPv4 fija `192.168.47.40` **persistente tras reinicio**, acceso SSH desde Windows **validado con clave de cliente Ed25519**, alias `ssh netlab360` funcional.

**VM:** `NETLAB360-Ubuntu-Desktop`; VMware Workstation Pro 26H1u1; 8 vCPU observadas en VMware, 16 GB RAM, 160 GB SCSI, NAT VMnet8.

## 1. Identificadores

| Campo | Valor |
|---|---|
| Ubuntu Desktop | **26.04.1 LTS (Resolute Raccoon)** comprobada con `/etc/os-release` |
| Hostname | **`netlab360-lab`** (confirmado) |
| Usuario | **`rc-aa-ec`** (iniciales de integrantes: Rubén Cañizares, Álvaro Alvarado y Elicier Castillo) |
| Zona horaria | `America/Panama` |
| VM networking | VMnet8 (Windows `192.168.47.1/24`); Ubuntu `ens33` **`192.168.47.40/24` fijo**; gateway `192.168.47.2` |
| SSH | TCP 22, solo red autorizada |
| Credenciales | Crear localmente, no compartir ni subir a Git |

Instalar Ubuntu solo sobre el disco virtual SCSI de 160 GB. No activar inicio de sesión automático. Se instaló con idioma español (España), teclado inglés US, nombre visible `Proyecto Semestral TE2` y zona horaria Panamá; los comandos del sistema siguen iguales.

## 2. Verificación inicial (terminal del invitado)

```bash
hostnamectl
cat /etc/os-release
uname -r
nproc
free -h
df -h /
ip -br a
ip route
```

No asumir que el invitado recibe la IP sugerida por VMware: observar DHCP real.

## 3. Mantenimiento e instalación básica

```bash
sudo timedatectl set-timezone America/Panama
sudo apt update
sudo apt upgrade -y
sudo apt install -y openssh-server open-vm-tools open-vm-tools-desktop git curl ca-certificates jq unzip rsync tree htop python3 python3-venv python3-pip
sudo systemctl enable --now ssh
sudo apt autoremove --purge -y
sudo apt clean
```

Si existe `/var/run/reboot-required`, reiniciar y continuar con comprobaciones. No modificar Hyper-V/VBS ni el hipervisor Windows.

```bash
sudo systemctl is-active ssh
sudo systemctl is-active open-vm-tools
ss -lnt | grep ':22 '
ip -4 -br addr show scope global
ip -4 route show default
resolvectl status
timedatectl status
```

No habilitar ni reconfigurar UFW, firewall, DHCP, Netplan ni SSH password policies hasta verificar enlace remoto.

## 4. IPv4 estática y primer SSH — verificado

- Pool DHCP VMware: `192.168.47.128–254`; el proyecto utiliza `192.168.47.40/24`, fuera del pool y de las reservas declaradas.
- Perfil activo: `netlab360-gestion`; perfil DHCP histórico `netplan-ens33` conservado con autoconnect desactivado.
- Gateway y DNS principal: `192.168.47.2`; DNS secundario `1.1.1.1`.
- `arping` a .40 antes de asignar: 3 probes, sin respuesta.
- `ping` al gateway e Internet: 4/4 respuestas en ambos casos; DNS funcional.
- Huella ED25519 verificada desde consola Ubuntu y comparada con la de Windows; conexión `ssh rc-aa-ec@192.168.47.40` lograda con contraseña. No modificar la entrada histórica .130 en `known_hosts`.

La IP **permanece en 192.168.47.40 después del reinicio completo**; servicio SSH y VMware Tools activos, gateway (3/3 ICMP) y resolución `github.com` comprobados.

## 5. Preparación de la clave SSH (ejecutada y validada)

Desde PowerShell 7, **no desde la sesión remota de Ubuntu**:

```powershell
$Clave = Join-Path $HOME ".ssh\\netlab360_ed25519"
New-Item -ItemType Directory -Force (Split-Path $Clave) | Out-Null
if (-not (Test-Path $Clave)) {
    ssh-keygen -t ed25519 -f $Clave -C "netlab360-windows"
}
Get-Content "$Clave.pub" |
    ssh rc-aa-ec@192.168.47.40 'umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys; chmod 700 ~/.ssh; chmod 600 ~/.ssh/authorized_keys'
ssh -i $Clave -o PreferredAuthentications=publickey -o PasswordAuthentication=no rc-aa-ec@192.168.47.40
```

Verificar `whoami` y `hostname` dentro del invitado. El alias local opcional `netlab360` debe usar `HostName 192.168.47.40`, `User rc-aa-ec` e `IdentityFile ~/.ssh/netlab360_ed25519`.

No almacenar claves privadas ni contraseñas en el repositorio. Rotar cualquier contraseña que haya sido compartida en la conversación. La autenticación por clave está probada. Mantener acceso de recuperación VMware y no cambiar las políticas de `sshd_config` hasta planificar y validar el endurecimiento.

## 6. Pendientes para cerrar #38

- [x] Registrar SO invitado, IP, gateway, hostname, 8 vCPU, memoria y disco (salidas facilitadas por el usuario).
- [x] Comprobar instalación, servicio `ssh` operativo y herramientas VMware.
- [x] Verificar sesión remota SSH desde Windows con contraseña e identidad del servidor comprobada.
- [x] Acceso SSH con llave Ed25519 verificado usando `PasswordAuthentication=no`; requiere únicamente passphrase local de la llave.
- [x] Regenerar inventario y registrar versión real en `01-inventario-host-y-vmware.md`.
- [ ] Integrar esta instalación a los tres entregables académicos definitivos (documentación técnica de GitHub actualizada).

## 7. Documentación oficial

- https://ubuntu.com/download/desktop
- https://ubuntu.com/server/docs/how-to/security/openssh-server/
- https://en.releases.ubuntu.com/releases/26.04/

**No copiar salidas con secretos, tokens ni claves privadas a GitHub.**
