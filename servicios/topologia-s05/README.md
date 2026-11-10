# NETLAB360 S05 — Topología gráfica multisede

**Estado:** primera versión del visor, API y pruebas offline versionadas 10/11/2026; ejecución en VM y capturas del visor **pendientes**. No equivale a aceptar [issue #64](https://github.com/recm0708/netlab360/issues/64).

## Inventario representado

Deriva de `inventario/ipam/topologia-s02.yaml`, estado `candidate`. Dibuja **HQ, S1 y S2**, 3 routers FRR, 3 switches de prueba, 9 VLAN, 9 hosts de namespaces aislados y 4 WAN (primaria y respaldo de HQ a cada sucursal). Los equipos que aparecen en diseño no se declaran operativos sin evidencia real. Un host VLAN servicios **no es automáticamente un servidor dedicado**. No hay equipos HA/OVS/Faucet adicionales confirmados todavía.

La API recoge el exporter S04 en `127.0.0.1:9110/api/v1/state` con antigüedad de muestra máxima de 15 segundos, identidad y fuente fiables, y consulta `sudo -n ip netns list` para identificar namespaces. Si la fuente no funciona o el usuario no puede consultar namespaces, el estado correspondiente es **UNKNOWN**, no DOWN falso. Si se observa apagado intencional, queda **OFFLINE**.

Las WAN distinguen trazado primario continuo y respaldo discontinuo. `admin-up` exige ambas puntas con `admin_up=1`, pero **no** demuestra vecindad OSPF Full, ruta activa/FIB, servicio HTTP, tráfico ni utilización de backup. Por ello el visor no anima paquetes ni pinta rutas como seleccionadas solo por flags administrativos.

## Instrucciones de ejecución

Terminal Ubuntu SSH:

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s05_topologia.py' -v
python3 servicios/topologia-s05/app.py --check
python3 servicios/topologia-s05/app.py --once
python3 servicios/topologia-s05/app.py --serve --port 9130
```

Otra terminal PowerShell de Windows:

```powershell
ssh -N -L 9130:127.0.0.1:9130 rc-aa-ec@192.168.47.40
```

Abrir **http://127.0.0.1:9130/** en Windows. Todo se sirve en localhost de la VM, sin publicar en VMnet8 ni Internet; los datos viajan por SSH. Actualiza cada 3 segundos, con panel para seleccionar dispositivos y enlaces. Detener con Ctrl+C. No crea ni elimina equipos, modifica interfaces ni lanza FRR/Docker.

## Actualización por fases

El inventario S02 fija el núcleo. En `inventario/topologia-extensiones-s05.json` pueden añadirse **solo equipos que se hayan desplegado y verificado**; exige `schema_version=1` y listas `nodes` y `links`. Un elemento nuevo requiere ID único, sede, tipo, evidencia y `realized=true` para registrarse en el modelo; el estado se marca UNKNOWN hasta que se instrumente telemetría específica.

Ejemplo documental, **NO desplegado** y no incluido en el inventario vigente:

```json
{"id":"SRV-HA-HQ-01","site":"HQ","type":"server",
 "label":"Servidor alterno","detail":"Servicio futuro",
 "realized":false,"evidence":"Issue con prueba real pendiente"}
```

La primera versión tiene **layout visual fijo de las tres sedes**. Aunque el backend ya acepta el registro de nodos verificados de estas sedes, para incorporar más sedes o muchos equipos y enlaces al gráfico visual será necesario ampliar IPAM, posiciones de frontend, pruebas y colectores de estado. No afirmar expansión visual ilimitada ya implementada.

## Pendientes de aceptación

1. Probar visor/API en VM (sin exporter, la topología sigue visible pero UNKNOWN; cero falsos verdes) y auditar capturas S05.
2. Comprobar el visor con exporter activo y S02 levantada mediante los procedimientos protegidos existentes.
3. Instrumentar verificación de selección OSPF/FIB, conectividad entre extremos y tráfico real; diferenciar respaldo standby de respaldo en uso.
4. Mejorar distribución escalable/zoom, visualización de elementos extendidos, accesibilidad y animación únicamente por contadores confiables.
5. Ampliar el inventario y las vistas conforme se incorporen y validen equipos HA, SDN, sedes y servicios posteriores.

**Protecciones:** nunca modificar `ens33 192.168.47.40/24`, gateway `192.168.47.2`, rutas ni servicios de otras materias. Estado de diseño no equivale a descubrimiento real.
