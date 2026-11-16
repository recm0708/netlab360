# NETLAB360 — Checklist S01 después de guía docente oficial (16/10)

**Referencia:** [guía oficial 1457](../../academico/00-criterios-docentes-y-hitos.md). **S01 abierta, avance 72/100 interno**. La política de dos documentos anteriores quedó sustituida.

## Cumplido
- [x] VMware Ubuntu y red administrativa segura para ensayos, con acceso SSH por Ed25519 (endurecimiento del daemon pendiente).
- [x] Inventario IPAM sin solapamientos, HQ/S1 y S2 reservada.
- [x] Pruebas individuales VLAN/ACL, FRR/OSPF WAN, LACP/active-backup virtual.
- [x] IaC metadata→config FRR, Prometheus/alertas y diagnóstico inicial por reglas.
- [x] 86 PNG/7 CSV en GitHub, 24 unit tests y CI verde.
- [x] Guías oficiales recibidas: **un informe de >=40 páginas** y demostración PowerPoint; redactar siguiendo 12 apartados.
- [x] Borrador Word institucional S01 de 65 páginas preexistente, revisado como base a **reordenar**, no a eliminar.
- [x] Manual técnico pospuesto como proyecto posterior, issue #28 conservada.

## Tareas futuras, con issue de fase propia
- [ ] Revisar políticas SSH efectivas/hardening seguro y rollback (#38).
- [ ] Integrar VLAN→WAN→servicio HQ→S1→S2 en una topología (#30/#13).
- [ ] Verificar doble WAN, recuperación y redundancia de dispositivos según diseño final (#14/#31/#32).
- [ ] Configuración/estado IaC live (#17/#18) y NOC integral (#12/#15/#20/#21).
- [ ] Evaluar dataset/ML real (#25/#26) si es alcance confirmado; no equiparar reglas con IA.
- [ ] Cerrar documentación única según [mapa](../../academico/01-migracion-borrador-a-formato-docente.md), después demo (#44) y anexos (#45) tras aprobación formato.
- [ ] Confirmar OVA/fecha final/duración PPT/límites de carga; ZIP externo ya autorizado; cortes académicos 30/10 y 13/11 (#36).

**S01 no requiere «manual 02 terminado» para continuar S02; el usuario autorizó replanificar con la nueva guía.** No dar cierre académico automático a la fase por esta nueva política.
