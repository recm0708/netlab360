# HA, LACP y SDN — Fase 05

## Descripción

Integramos redundancia HTTP, agregación Ethernet
y un dominio SDN separado mediante OVS y Faucet.

## Consulta de disponibilidad y topología

```bash
sudo -v
bash operacion/estado.sh
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9130/healthz
curl --fail --silent --show-error --max-time 5 http://127.0.0.1:9130/api/v1/graph
python3 scripts/laboratorio/s05_ha_red_servicios.py status
```

## Consulta de agregación y SDN

```bash
python3 scripts/laboratorio/s05_lacp_hq_integracion.py status
python3 scripts/laboratorio/s05_lacp_s1_integracion.py status
python3 scripts/laboratorio/s05_lacp_s2_integracion.py status
python3 scripts/laboratorio/s05_sdn_ovs_faucet_aislado.py status
sudo -n ovs-vsctl show
sudo -n /usr/local/libexec/netlab360-observer snapshot
```

## Validación offline

```bash
python3 -m unittest discover -s tests -p 'test_s05_*.py' -v
```

## Construcción y experimentación

La reconstrucción central organiza las redes de servicios,
las dependencias systemd, las tres agregaciones y SDN.

Conservamos los siguientes procedimientos controlados:

- [Conmutación HTTP HA](../../scripts/operacion/s05-lote-ha-instancia-con-watchdog.sh).
- [Falla y retorno LACP HQ](../../scripts/laboratorio/s05_lacp_hq_falla_retorno.py).
- [Falla y retorno LACP S1](../../scripts/laboratorio/s05_lacp_s1_falla_retorno.py).
- [Falla y retorno LACP S2](../../scripts/laboratorio/s05_lacp_s2_falla_retorno.py).
- [Falla y retorno de puerto SDN](../../scripts/laboratorio/s05_sdn_falla_retorno_puerto_a.py).
- [Recuperación selectiva de Faucet](../../scripts/laboratorio/s05_sdn_recuperar_faucet_logs.py).
- [Medición comparativa LACP](../../scripts/laboratorio/s05-lacp-capacidad-comparativa.sh).

No encadenamos estos ensayos automáticamente. Cada uno
exige su propio precheck y verificación de restauración.

## Documentación relacionada

- [Diseño HA](../../docs/diseno/s05-ha-servicios-multisede.md).
- [Diseño LACP](../../docs/diseno/s05-lacp-8023ad-multisede.md).
- [Dominio SDN](../../docs/diseno/s05-dominio-sdn-ovs-faucet.md).
- [NOC integrado](../../servicios/topologia-s05/README.md).
- [Aceptación técnica](../../docs/validacion/s05-integracion-y-aceptacion.md).
