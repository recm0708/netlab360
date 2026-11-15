# S05 — Importación verificable de 70 capturas originales Windows

**Fuente aportada:** inventario PowerShell NETLAB360_S05_PNG_20261115-110810.csv, 70 PNG en Pictures/Screenshots, 5 588 763 bytes, 70 SHA256 distintos. Original PNG63 comprobado por SHA frente al archivo recibido (155432 bytes, d3506bdb33d28037f8860bd53bd1bf3bc3c6b33ff7083d58c80e5e377b1cccfe). No se considera importado a GitHub ninguno de los otros 69 por figurar en CSV.

## Fuentes esperadas en Ubuntu

El script s05-importar-png-originales.py lee:

- CSV: ~/netlab360-bootstrap/s05/importacion-png/NETLAB360_S05_PNG_20261115-110810.csv
- ZIP: ~/netlab360-bootstrap/s05/importacion-png/NETLAB360_S05_70PNG_ORIGINALES.zip

Desde PowerShell, comprimir exactamente los 70 archivos declarados en el CSV, preservando sus bytes, transferir CSV y ZIP mediante SCP a la carpeta de la VM; no generar nuevas imágenes ni reenumerar.

- --check: no escribe; exige 70 nombres, tamaños, SHA-256 de bytes, firma PNG y ancla original 63. No confundir el inventario CSV con auditoría visual.
- --import: exige Git limpio; escribe los PNG exclusivamente bajo evidencias/capturas/fase5 por creación de archivos nuevos; rehúsa sobrescribir cualquier imagen preexistente; genera MANIFIESTO_SHA256_S05_PNG_20261115.sha256 y INVENTARIO_S05_PNG_VERIFICADO_20261115.csv (sin rutas personales Windows).
- Después, verificar sha256sum -c de PNG dentro del directorio, revisar contenido sensible/legibilidad, hacer commit en rama de evidencias y PR antes de declarar respaldo versionado.
- Si el proceso falla tras escribir parcialmente, detenerse y auditar; no ejecutar rm ni repetir --import sin revisión de todos los archivos. Mantener ZIP y CSV originales fuera de Git como recuperación temporal hasta verificar destino.

**Seguridad y alcance:** no versionar credenciales, llaves privadas ni tokens visibles en capturas. El repositorio es privado, pero los PNG podrían terminar en entregables. Las pruebas de integridad no prueban por sí solas que las capturas sean legibles y estén correctamente encuadradas.
