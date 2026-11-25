# Prerregistro y congelación del estudio histórico

## Descripción

S06-049 comprobó en la VM que existen por ruta 60 ventanas NORMAL, 16 DEGRADED y 24 RECOVERY, pero **no** se dispone de un holdout cronológico global. El TEST NORMAL histórico precede a algunas sesiones degradadas usadas en TRAIN; las rutas HQ→S1/HQ→S2 comparten eventos y el fallo probado se limita al retardo fijo de 40 ms. Por tanto, no corresponde volver a evaluar el mismo TEST y presentarlo como validación prospectiva.

**S06-050 es un preregistro anterior a nuevos datos, no una evaluación nueva ni un experimento de degradación.** Congela modelos, reglas, lista de sesiones históricas, features y criterios futuros sin reentrenar, hacer ping o cambiar red. Conserva el resultado del gate S06-049.

## Implementación

`scripts/s06/prerregistrar_estudio_futuro.py` ofrece dos acciones, `--freeze` (creación exclusiva una sola vez) y `--check` (verificación sin sobrescritura). Lee el informe/modelos originales íntegros de S06-044, el reporte privado de S06-049, las fechas de todas las sesiones conocidas y los metadatos de cantidad de paquetes por ventana. Prohíbe congelar el protocolo con fecha anterior a los datos ya usados.

El acta se guarda en `~/netlab360-bootstrap/s06/preregistros/S06_050_Prerregistro_Prospectivo.json` con permisos privados. No se versiona el acta ni los cuatro modelos en Git. Su contenido se vuelve a cotejar con las fuentes mediante `--check`; cambios posteriores en el contrato, modelos o referencia se rechazan. No equivale a un sello externo contra modificaciones deliberadas: la auditoría de Git y las bitácoras son la trazabilidad complementaria.

## Protocolo fijado antes de adquirir datos

- Conservar P95 RTT, IsolationForest y LogisticRegression congelados, sin reentrenamiento ni modificaciones de umbral tras observar las próximas muestras.
- TEST futuro exclusivamente con IDs de sesión **no vistos** y timestamps posteriores al preregistro, con al menos 20 NORMAL por ruta, dos eventos DEGRADED independientes/8 ventanas positivas por ruta, seis RECOVERY por ruta; el plan no obliga a inducir esas degradaciones antes de verificar autorización humana, watchdog y recuperación.
- Preservar etiquetas externas independientes del RTT, selección de características sin fuga, resultados por evento/token y por ruta (sin tratar dos destinos correlacionados como experimentos estadísticos independientes).
- **Condición previa crucial:** verificar el número de paquetes de las ventanas históricas. Si NORMAL y DEGRADED originales difieren de muestreo, el acta señala `BLOCKED_INCOMPATIBLE_SAMPLING`; se debe resolver con un protocolo comparativo separado antes de TEST. Los 3 paquetes de muestras live S06-046 no se consideran ventanas supervisadas intercambiables por defecto.
- Para otro tipo de FAULT, pérdida, congestión variable o perturbación WAN/OSPF/SDN se requiere otro protocolo y autorización: no inventar que el modelo actual generaliza.
- Data drift solo como diagnóstico descriptivo si el muestreo es comparable; concept drift solo con etiquetas futuras. Sin objetivo temporal, horizonte y múltiples eventos genuinos, el pronóstico se declara `NO_EVALUABLE`, no se comunica MAE ni capacidad de alerta temprana ficticia.
- Cualquier estímulo real de red necesitará un procedimiento específico de aprobación y un watchdog root con recuperación verificada **antes** de su ejecución. Este archivo no autoriza acciones sobre FRR, qdisc, OVS, contenedores ni interfaz ens33.

## Validación

Las 12 pruebas específicas pasaron. El comando `--freeze` creó de manera exclusiva `~/netlab360-bootstrap/s06/preregistros/S06_050_Prerregistro_Prospectivo.json`, y `--check` verificó el mismo archivo sin sobrescribirlo. Los cuatro modelos permanecen congelados. Resultado `PAQUETES_ORIGINALES=2,3`, `MUESTREO_COMPATIBLE=NO`, `STATUS=BLOCKED_INCOMPATIBLE_SAMPLING`, `TEST_PROSPECTIVO_EJECUTADO=NO`, `S06-050_PRERREGISTRO_VALIDADO=OK`, `RESULTADO_RC=0`. Bitácora `~/netlab360-bootstrap/s06/validacion-s06-050-20261123_061334/S06_050_Validacion_Completa.txt`.

Postcondiciones: 21 namespaces, cuatro contenedores, gestión `ens33 192.168.47.40/24` vía gateway `.2`, guardia `NONE/BASELINE`, qdisc `noqueue`, NOC con 18 nodos/21 enlaces y LACP/SDN operativos; no hubo cambios de red, entrenamiento ni nueva evaluación de modelos. **S06-050 se acepta como preregistro, no como aprobación de muestreo ni TEST prospectivo**. El acta no se modifica para conseguir `PLAN_READY`. [Auditoría del muestreo histórico](s06-auditoria-muestreo-protocolo-historico.md).
