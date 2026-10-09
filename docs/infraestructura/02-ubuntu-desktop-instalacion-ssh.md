# NETLAB360 — Guía 01: Ubuntu Desktop y acceso SSH desde Windows

**Estado (2026-10-09):** Ubuntu 26.04.1 instalado y actualizado; SSH y VMware Tools activos; acceso remoto bloqueado por huella antigua de una IP reutilizada. Requiere validación y conexión.

**VM:** `NETLAB360-Ubuntu-Desktop`; VMware Workstation Pro 26H1u1; 8 vCPU observadas en VMware, 16 GB RAM, 160 GB SCSI, NAT VMnet8.

## 1. Identificadores

| Campo | Valor |
|---|---|
| Ubuntu Desktop | **26.04.1 LTS (Resolute Raccoon)** comprobada con `/etc/os-release` |
| Hostname | **`netlab360-lab`** (confirmado) |
| Usuario | **`rc-aa-ec`** (iniciales de integrantes: Rubén Cañizares, Álvaro Alvarado y Elicier Castillo) |
| Zona horaria | `America/Panama` |
| VM networking | VMnet8 (Windows `192.168.47.1/24`), Ubuntu `ens33` `192.168.47.130/24`, gateway `192.168.47.2` |
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

## 4. Diagnóstico y corrección segura de identidad del host SSH

La conexión realizada desde Windows con `ssh root@192.168.47.130` falló **antes de autenticarse** porque existía una huella guardada de otra máquina en esa misma IP (`REMOTE HOST IDENTIFICATION HAS CHANGED`). La VM NAT reutiliza direcciones; no suprimir controles SSH.

**Paso 4.a — En la consola de Ubuntu, vía VMware:**

```bash
sudo ssh-keygen -lf /etc/ssh/ssh_host_ed25519_key.pub -E sha256
sudo systemctl is-active ssh
ip -4 -br addr show ens33
```

Comparar visualmente el fingerprint del servidor con el que informó el cliente Windows. Si no coincide, detenerse.

**Paso 4.b — En PowerShell Windows, tras comparar:**

```powershell
Test-NetConnection 192.168.47.130 -Port 22
ssh-keygen -R 192.168.47.130
ssh rc-aa-ec@192.168.47.130
```

Confirmar la nueva huella solo si coincide con la observada localmente. Introducir contraseña local sin compartirla.

## 5. Acceso mediante clave Ed25519 desde Windows

Ejecutar en PowerShell, tras completar primer acceso normal:

```powershell
$Clave = Join-Path $HOME '.ssh\netlab360_ed25519'
New-Item -ItemType Directory -Force (Split-Path $Clave) | Out-Null
if (-not (Test-Path $Clave)) {
  ssh-keygen -t ed25519 -f $Clave -C 'netlab360-windows'
}
Get-Content "$Clave.pub" | ssh rc-aa-ec@192.168.47.130 "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
ssh -i $Clave rc-aa-ec@192.168.47.130
```

No almacenar clave privada o contraseña en repositorio. Cambiar la contraseña inicial porque fue revelada en chat y no reutilizar la misma en todos los servicios. Solo reforzar `sshd_config` cuando esté confirmada la autenticación por clave y se disponga de acceso local alternativo. El futuro hostname SSH alias será `netlab360` y debe apuntar al usuario correcto `rc-aa-ec`.

## 6. Pendientes para cerrar #38

- [x] Registrar SO invitado, IP, gateway, hostname, 8 vCPU, memoria y disco (salidas facilitadas por el usuario).
- [x] Comprobar instalación, servicio `ssh` operativo y herramientas VMware.
- [ ] Verificar desde Windows conexión TCP 22 y sesión SSH con llave Ed25519.
- [x] Regenerar inventario y registrar versión real en `01-inventario-host-y-vmware.md`.
- [ ] Actualizar los tres entregables: informe académico, bitácora técnica y manual.

## 7. Documentación oficial

- https://ubuntu.com/download/desktop
- https://ubuntu.com/server/docs/how-to/security/openssh-server/
- https://en.releases.ubuntu.com/releases/26.04/

**No copiar salidas con secretos, tokens ni claves privadas a GitHub.**
