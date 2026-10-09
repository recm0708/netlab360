# NETLAB360 — Guía 01: Ubuntu Desktop y acceso SSH desde Windows

**Estado:** procedimiento autorizado y en ejecución; comandos aún no verificados sobre el invitado.

**VM:** `NETLAB360-Ubuntu-Desktop`; VMware Workstation Pro 26H1u1; 8 vCPU observadas en VMware, 16 GB RAM, 160 GB SCSI, NAT VMnet8.

## 1. Identificadores

| Campo | Valor |
|---|---|
| Ubuntu Desktop | 26.04.1 LTS (Resolute Raccoon), verificar `/etc/os-release` |
| Hostname | `netlab360-lab` |
| Usuario | `ruben` |
| Zona horaria | `America/Panama` |
| VM networking | NAT por VMware Workstation (VMnet8) |
| SSH | TCP 22, solo red autorizada |
| Credenciales | Crear localmente, no compartir ni subir a Git |

Instalar Ubuntu solo sobre el disco virtual SCSI de 160 GB. No activar inicio de sesión automático. Si se instala con idioma español, los comandos del sistema siguen iguales.

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

## 4. Desde PowerShell 7 Windows

Averiguar la interfaz VMnet8, no inferir su dirección:

```powershell
Get-NetAdapter | Where-Object Name -match 'VMnet8'
Get-NetIPAddress -AddressFamily IPv4 | Where-Object InterfaceAlias -match 'VMnet8' | Select-Object InterfaceAlias,IPAddress,PrefixLength
Test-NetConnection -ComputerName <IP_UBUNTU> -Port 22
ssh ruben@<IP_UBUNTU>
```

`<IP_UBUNTU>` es marcador de posición y debe sustituirse por la IP mostrada en Ubuntu.

## 5. Acceso por llave desde PowerShell

```powershell
$Clave = Join-Path $HOME '.ssh\netlab360_ed25519'
New-Item -ItemType Directory -Force (Split-Path $Clave) | Out-Null
if (-not (Test-Path $Clave)) {
  ssh-keygen -t ed25519 -f $Clave -C 'netlab360-windows'
}
Get-Content "$Clave.pub" | ssh ruben@<IP_UBUNTU> "umask 077; mkdir -p ~/.ssh; cat >> ~/.ssh/authorized_keys"
ssh -i $Clave ruben@<IP_UBUNTU>
```

No copiar la clave privada a Ubuntu ni al repositorio, solo la pública. No deshabilitar autenticación por contraseña hasta que se haya verificado que un inicio de sesión remoto con llave funciona y existe un mecanismo local de recuperación.

## 6. Pendientes para cerrar #38

- [ ] Capturar SO invitado, IP, router default, hostname, 8 vCPU, memoria y disco.
- [ ] Comprobar instalación sin errores, servicio `ssh` operativo y herramientas VMware.
- [ ] Verificar desde Windows conexión TCP 22 y sesión SSH con llave Ed25519.
- [ ] Regenerar inventario y registrar la versión real de Ubuntu.
- [ ] Actualizar los tres entregables: informe académico, bitácora técnica y manual.

## 7. Documentación oficial

- https://ubuntu.com/download/desktop
- https://ubuntu.com/server/docs/how-to/security/openssh-server/
- https://en.releases.ubuntu.com/releases/26.04/

**No copiar salidas con secretos, tokens ni claves privadas a GitHub.**
