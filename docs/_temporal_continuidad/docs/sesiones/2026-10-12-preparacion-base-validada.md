# NETLAB360 — Ejecución base del 12 de octubre de 2026

**Estado:** instalación terminada; autenticación CLI del repositorio pendiente de renovar; no se ha desplegado una topología.

## Resultados observados en la consola

Durante la reanudación, se verificó el acceso `sudo`. Se canceló el cuadro interactivo de Git sin completar `git pull`. Las órdenes siguientes que ya habían quedado introducidas iniciaron el instalador. Este se ejecutó hasta imprimir **OK: herramientas base instaladas**.

Versiones verificadas:
- Ubuntu Desktop 26.04.1 LTS, kernel 7.0.0-38-generic.
- Docker Engine 29.9.0, Compose 5.6.0, Buildx 0.38.0, containerd 2.4.1; prueba hello-world completada.
- OpenTofu 1.13.1.
- Ansible Core 2.20.1, Ansible paquete 13.1.0.
- Python 3.14.4; Node.js 24.21.0; npm 11.19.0.
- Git 2.53.0; GitHub CLI 2.102.0.
- Servicios docker, ssh y open-vm-tools activos.
- IP estática ens33 192.168.47.40/24, gateway 192.168.47.2.
- Volumen raíz 157 GB, 136 GB disponibles, sin reinicio requerido.
- Sin contenedores activos tras hello-world.

Se actualizaron 19 paquetes y se instalaron 67 paquetes de la primera tanda, además de dependencias Docker/OpenTofu/Node.

## Pendiente antes de apagar

Al terminar, la comprobación de GitHub CLI falló porque las credenciales almacenadas dejaron de ser válidas. Se debe renovar autorización con navegador Windows, comprobar el identificador de cuenta, activar el asistente oficial de credenciales y ejecutar git pull sin peticiones de contraseña. No volver a ejecutar el instalador.

Archivo de evidencia local: `~/netlab360-bootstrap/evidencias/02-preparacion-herramientas-20261012-083150.log`.

Conservar histórico anterior del 9 de octubre: el primer intento se detuvo por sudo; **el nuevo intento del 12 sí terminó**. Siguiente fase técnica todavía pendiente; no dar por completada S01.

En GitHub, este documento no contiene secretos ni códigos temporales.
