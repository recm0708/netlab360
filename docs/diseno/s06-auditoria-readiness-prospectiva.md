# Auditoría de preparación prospectiva del corpus histórico — Fase 06

## Descripción

Después de verificar el NOC, LACP y Faucet en S06-048, evaluamos si el corpus histórico S06-041–044 permitía una evaluación predictiva prospectiva. El dictamen fue negativo porque el TEST NORMAL histórico precede a parte de TRAIN DEGRADED, no hay FAULT etiquetado, no existe un segundo TEST etiquetado capturado posteriormente y no se ha establecido horizonte de pronóstico.

No confundir **auditoría exitosa** (`S06_049_AUDITORIA_READONLY=OK`) con **criterio prospectivo cumplido** (`S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE`). No se reutiliza el TEST original para elegir hiperparámetros ni se suman las capturas de tres ICMP en vivo como nuevas ventanas supervisadas.

## Implementación

- `scripts/s06/auditar_gates_prospectivos.py` lee el reporte privado validado de S06-044, comprueba el corpus NORMAL original y los cuatro pares DEGRADED/RECOVERY completos a través de lectores existentes (con verificaciones de integridad y tokens de guardia). Valida no solapamiento entre IDs de sesión TRAIN/TEST y compara la **última fecha TRAIN** contra la **primera fecha TEST**.
- `tests/test_s06_gates_prospectivos.py` cubre cronología frente a separación por sesión, rechazo de duplicados, tamaños de corpus, tokens de evento y negativa a reportar pronóstico/detección de otra clase no demostrada.
- En `~/netlab360-bootstrap/s06/auditorias-prospectivas/` se conserva un JSON privado de resultados (`--save`). No incluye las mediciones crudas ni modelos. No toca red, servicio, interfaz, qdisc, entrenamiento o capturas anteriores.

## Criterios metodológicos

1. **Cronología y exclusión TRAIN/TEST**: reservar sesiones con inicio posterior a todos los datos de calibración y entrenamiento; sin reutilizar las observaciones de decisión ya vistas en S06-044 ni variantes triviales del mismo evento.
2. **Evento positivo futuro comprobable**: documentar previamente el evento/estímulo y su recuperación, con autorización humana específica y watchdog si implica cambiar un recurso real. No utilizar eventos anteriores para afirmar prueba independiente.
3. **Cobertura y honestidad**: la clase FAULT solo se agrega si existe observación propia y fuente de verificación externa; no inferir falla WAN/OSPF/HA/SDN a partir del retardo fijo de 40 ms. Si queda excluida, consignarlo como limitación explícita.
4. **Predicción y deriva**: distinguir *detector del estado presente* de *pronóstico con horizonte futuro*. MAE y alerta temprana requieren objetivo t+h real, ventanas de características sin datos del futuro y suficientes sucesos. Data drift necesita muestreo comparable al entrenamiento; concept drift necesita etiquetas posteriores. Si no hay datos suficientes, registrar `NO_EVALUABLE`, nunca una métrica inventada.
5. **Cierre documental**: comparar resultados por ruta y evento, incorporar falsos positivos/negativos, incertidumbre, seguridad y conclusiones restringidas. Se actualiza el mismo trabajo académico en Word/PDF al concluir las pruebas, no con hipótesis no verificadas.

## Reproducción de la auditoría

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s06_gates_prospectivos.py' -v
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/s06/auditar_gates_prospectivos.py --save
```

El inventario esperado era de 60 NORMAL, 16 DEGRADED, 24 RECOVERY y 0 FAULT **por ruta**, TRAIN/TEST por sesiones sin coincidencias pero sin holdout cronológico global; ninguna prueba prospectiva independiente, ningún pronóstico con horizonte y ninguna deriva validada con ground truth. `S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE` confirma la insuficiencia del conjunto original, **no** que el código haya fallado.

La auditoría no modifica infraestructura ni registros originales.

## Resultados

Obtuvimos `S06-049_AUDITORIA_VALIDADA=OK`, `RESULTADO_RC=0`; las **11 pruebas específicas** pasaron en la VM y se verificó el informe privado `~/netlab360-bootstrap/s06/auditorias-prospectivas/S06_049_20261123T110156Z_5ef7af/auditoria-readiness.json`. Bitácora de respaldo: `~/netlab360-bootstrap/s06/validacion-s06-049-20261123_060155/S06_049_Validacion_Completa.txt`.

Confirmamos **60 NORMAL, 16 DEGRADED y 24 RECOVERY por ruta**, cero FAULT verificadas. Los datos TRAIN/TEST tienen IDs de sesiones separados, **pero NO un holdout cronológico global**; el TEST NORMAL fue observado antes de parte del TRAIN DEGRADED. No hay segundo TEST positivo independiente etiquetado ni variable objetivo para pronóstico futuro ni una deriva prospectiva validada. La recopilación de 3 ICMP en tiempo real de S06-046/047 no tiene equivalencia de muestreo ni ground truth para usarla como un segundo TEST supervisado. El dictamen es `S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE`.

Los 21 namespaces, cuatro contenedores, `ens33 192.168.47.40/24` y gateway `.2`, guardia `NONE/BASELINE`, qdisc `noqueue`, Prometheus READY, NOC 18/21 y fuentes LACP/SDN permanecen sin alteración. Dataset/modelos originales sin modificaciones y Git limpio. La auditoría confirmó la insuficiencia del corpus histórico para una evaluación cronológica prospectiva. El estudio uniforme V2 se realizó como protocolo separado.
