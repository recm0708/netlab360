# NETLAB360 — Manual de usuario S01

**Versión:** V0.1. **Destinatario:** operador autorizado de laboratorio, no entorno productivo. **Advertencia:** no alterar ens33, VMnet8 ni ruta predeterminada durante ensayos; los scripts emplean recursos virtuales aislados.

## 1. Acceder
Abrir VMware Workstation, identificar la VM NETLAB360-Ubuntu-Desktop y validar snapshot de recuperación. Conectar por SSH con credenciales autorizadas. Entrar al clon en ~/proyectos/netlab360. Antes de modificar, ejecutar git status --short --branch y después git pull --ff-only origin main si está limpio.

## 2. Precheck general
Ejecutar:
    ip -4 -br addr show ens33
    ip -4 route show default
    systemctl is-active docker ssh open-vm-tools
    sudo docker ps -a
    sudo ip netns list
    python3 scripts/validacion/validar-ipam.py inventario/ipam/topologia-b1.yaml

Esperado: ens33=192.168.47.40/24, gateway=192.168.47.2, tres servicios active, recursos anteriores ausentes, IPAM OK. Si existen contenedores o estado B2, NO ejecutar otro up.

## 3. Verificar WAN OSPF y recuperación
Desde el repositorio:
    bash scripts/laboratorio/b2-dualwan-ospf.sh precheck
    bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado
    bash scripts/laboratorio/b2-dualwan-ospf.sh status

Las dos rutas WAN y los vecinos Full son indicadores de éxito del plano de control. Solo con permiso explícito para simular incidente:
    bash scripts/laboratorio/b2-dualwan-ospf.sh fail
    bash scripts/laboratorio/b2-dualwan-ospf.sh restore

Esperado: conmutación a wan-b y retorno a wan-p. Al terminar:
    bash scripts/laboratorio/b2-dualwan-ospf.sh down

No eliminar con docker rm -f genérico ni borrar archivos de estado ajenos; conservar logs si aparece un error.

## 4. Usar configuración candidata desde IaC
Si está creado ~/netlab360-bootstrap/iac/s01/rendered:
    python3 scripts/validacion/precheck-iac-b2.py

Para precheck de B2 con archivo generado por Ansible:
    NETLAB360_IAC_CONFIG_DIR="$HOME/netlab360-bootstrap/iac/s01/rendered" bash scripts/laboratorio/b2-dualwan-ospf.sh precheck

El despliegue B2 con esa variable utiliza el candidato Ansible en routers FRRouting, pero OpenTofu no crea el contenedor. Nunca subir terraform.tfstate a GitHub.

## 5. Observabilidad y NOC
Consultar scripts y configuraciones en servicios/observabilidad/ y scripts/observabilidad/. Exportador local usual: 127.0.0.1:9108; Prometheus local usual: 127.0.0.1:9090. Solo intentar un túnel SSH si esos procesos están escuchando. El dashboard y el motor Prometheus ya mostraron alertas WAN firing y resueltas en ensayos; Alertmanager con receptor y portal multisede completo están pendientes.

## 6. Diagnóstico histórico B4
Desde el clon:
    python3 scripts/analitica/b4-auditar-fuentes-reales.py --save
    python3 scripts/analitica/b4-perfil-estadistico-real.py --save
    python3 scripts/analitica/b4-diagnostico-reglas.py --save

Los tres reportes JSON se generan fuera del clon Git, en ~/netlab360-bootstrap/analitica/b4/. No se capturan nuevos paquetes, ni se entrenan modelos de IA. Las 76 muestras actuales corresponden a una sola sesión.

## 7. Integridad y pruebas
    python3 -m unittest discover -s tests -p 'test_*.py' -v
    python3 scripts/validacion/validar-capturas-unificadas.py
    git status --short --branch

En el corte S01 se comprobaron 24 tests y 86 PNG más siete CSV. La CI de GitHub verifica código offline, no conmutaciones reales del laboratorio.

## 8. Cierre seguro
Después de los laboratorios de red, ejecutar el down correspondiente, comprobar Docker y namespaces vacíos, ens33/gateway y tres servicios active. Si la ruta administrativa cambió, detener la operación e investigar; no reconfigurar el host a ciegas. No publicar tokens, contraseñas, llaves privadas, archivos de estado ni volcados con información sensible.

## 9. Funciones pendientes
Topología L2–WAN integral, equipo/servidor redundantes completos, receptores Alertmanager, reconciliación del router en ejecución, IA evaluada, y VM OVA sanitizada y reimportada. No declarar esas funciones disponibles en el manual final sin nuevas pruebas.

## 10. Figuras seleccionadas para edición Word
B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png; IAC_B2_03_OSPF_y_Rutas_IAC.png; B3_08_Dashboard_NOC_En_Vivo.png; B3_12_Alerta_Prometheus_WAN_Down.png; B4_08_Diagnostico_Reglas_Reales.png; LOTE06_Postcheck_Publicacion.png (esta última todavía por publicar).

**Estado de manual:** borrador operativo V0.1; falta portada, capturas insertadas y ensayo de reproducibilidad sobre VM restaurada.
