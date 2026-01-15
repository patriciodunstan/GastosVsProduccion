# INFORME DE ANÁLISIS DE GASTOS Q4 2025
## Harcha Maquinaria SPA

**Fecha de análisis:** 15-01-2026  
**Período analizado:** Octubre - Noviembre - Diciembre 2025  
**Archivos procesados:** 16 CSV de reportes contables

---

## 1. RESUMEN EJECUTIVO

| Concepto | Monto |
|----------|-------|
| **TOTAL INGRESOS Q4 2025** | **$1,379,494,912** |
| **TOTAL GASTOS Q4 2025** | **$1,334,203,382** |
| **RESULTADO NETO** | **$45,291,530** (Positivo) |

### Desglose de Gastos por Tipo

| Tipo de Gasto | Monto | % del Total |
|---------------|-------|-------------|
| Cuotas Leasing | $257,267,556 | 19.3% |
| Repuestos y Accesorios | $148,227,049 | 11.1% |
| Remuneraciones (Taller) | $115,760,826 | 8.7% |
| Reparaciones Externas | $71,866,677 | 5.4% |
| Combustibles | $54,199,919 | 4.1% |
| Seguros | $15,188,006 | 1.1% |
| Transporte/Fletes | $10,125,778 | 0.8% |
| EPP | $2,573,868 | 0.2% |
| Honorarios | $1,864,035 | 0.1% |
| Otros | $657,129,668 | 49.2% |

---

## 2. IDENTIFICACIÓN DE MÁQUINAS

### 2.1 Resumen de Procesamiento

| Métrica | Cantidad |
|---------|----------|
| **Total de registros procesados** | 5,644 |
| **Registros CON código de máquina** | 3,817 (68%) |
| **Registros SIN código (genéricos)** | 1,827 (32%) |
| **Máquinas únicas identificadas** | 149 |

### 2.2 Máquinas Identificadas por Tipo

| Prefijo | Tipo de Maquinaria | Cantidad | Ejemplos |
|---------|-------------------|----------|----------|
| **CT** | Camiones Tolva | 32 | CT-06, CT-07, CT-08, CT-09, CT-10... |
| **C** | Vehículos Livianos | 39 | C-01, C-03, C-04, C-06, C-12... |
| **EX** | Excavadoras | 17 | EX-02, EX-03, EX-06, EX-07, EX-08... |
| **CF** | Cargadores Frontales | 9 | CF-02, CF-03, CF-04, CF-05, CF-06... |
| **RX** | Retroexcavadoras | 8 | RX-02, RX-03, RX-04, RX-05, RX-06... |
| **CP** | Camiones Pluma | 7 | CP-02, CP-03, CP-04, CP-05, CP-06... |
| **MN** | Motoniveladoras | 4 | MN-01, MN-02, MN-03, MN-04 |
| **GM** | Grúas Móviles | 4 | GM-01, GM-02, GM-03, GM-04 |
| **TC** | Tracto Camiones | 3 | TC-01, TC-02, TC-03 |
| **BD** | Bulldozers | 2 | BD-02, BD-03 |
| **MC** | Minicargadores | 3 | MC-01, MC-03, MC-04 |
| **CB** | Camiones Varios | 4 | CB-01, CB-02, CB-03, CB-04 |
| **RC** | Rodillos Compactadores | 2 | RC-01, RC-02 |
| **CI** | Camiones Internacionales | 2 | CI-01, CI-02 |
| **BA** | Barredoras | 1 | BA-01 |
| **Otros** | MX, GV, RL, RN, CA, CS, CK, CM, CG, MB | 12 | Varios |

---

## 3. ⚠️ PROBLEMAS DETECTADOS - DATOS NO NORMALIZADOS

### 3.1 Centros de Costo YA NORMALIZADOS ✅

Los siguientes centros de costo fueron normalizados exitosamente:

| Centro de Costo | Código Asignado | Gastos | Ingresos |
|-----------------|-----------------|--------|----------|
| TRACTOR CASE PUMA 155 | **T-06** | $7,568,961 | $0 |
| CAMIONETA RAPTOR VGKX-71 | **C-53** | $3,367,567 | $4,800,000 |
| CAMIONETA JMC RWRH-49 | **C-29** | $1,419,072 | $1,061,666 |
| CAMIONETA JMC RXKR-45 | C-30 (tentativo) | $1,183,309 | $368,333 |
| CAMIONETA JMC VIGUS RWRH-53 | C-31 (tentativo) | $840,807 | $0 |
| TRACTOR CASE GWSV65 | T-05 (tentativo) | $677,254 | $0 |

### 3.2 Centros de Costo PENDIENTES DE NORMALIZAR ⚠️

| Centro de Costo | Gastos | Ingresos | Acción Requerida |
|-----------------|--------|----------|------------------|
| **1010100002 TALLER** | **$137,265,399** | $161,456 | ⚠️ Decidir tratamiento |
| **2070100001 PLANTA CHANCADORA POWERSCREEN** | **$24,818,736** | $0 | 🔍 Usuario buscará info |
| **2060100001 PLANTA HORMIGON MOVIL** | $448,480 | $0 | Asignar código (ej: PH-01) |
| **2030100046 CUATRIMOTO CF400 THS 071-8** | $148,912 | $0 | Asignar código |
| **2010900001 MAQUINA BARREDORA BROCE BW260** | $96,768 | $0 | ⚠️ ¿Es igual a BA-01? |
| **2030100045 CUATRIMOTO CF400 THS 072-6** | $8,000 | $0 | Asignar código |

**TOTAL GASTOS NO IMPUTABLES:** **$162,786,295** (12.2% del total)

---

### 3.3 Detalle del Centro "TALLER" ($137.3M)

El centro **TALLER** acumula $137.3M en gastos que incluyen:

| Tipo de Gasto en TALLER | Monto Estimado |
|-------------------------|----------------|
| Remuneraciones (sueldos, gratificaciones, SIS) | ~$115.8M |
| Repuestos sin asignar | ~$16.6M |
| Servicios varios | ~$5M |

**PROBLEMA:** Estos gastos deberían distribuirse entre las máquinas o crear un centro de costo específico para gastos generales del taller.

**OPCIONES DE SOLUCIÓN:**
1. Crear código **TA-01** para el taller como centro de costo
2. Distribuir proporcionalmente entre las máquinas activas
3. Separar remuneraciones en un centro aparte (no es gasto de máquina)

---

### 3.4 Patentes/PPU - Estado de Normalización

| Patente | Centro de Costo | Código | Estado |
|---------|-----------------|--------|--------|
| VGKX-71 | CAMIONETA RAPTOR | **C-53** | ✅ Confirmado |
| RWRH-49 | CAMIONETA JMC | **C-29** | ✅ Confirmado |
| RXKR-45 | CAMIONETA JMC | C-30 | ⚠️ Tentativo - Confirmar |
| RWRH-53 | CAMIONETA JMC VIGUS | C-31 | ⚠️ Tentativo - Confirmar |
| GWSV65 | TRACTOR CASE | T-05 | ⚠️ Tentativo - Confirmar |

---

## 4. TOP 20 MÁQUINAS POR GASTO (con código identificado)

| # | Código | Descripción | Gastos Q4 | Ingresos Q4 | Resultado |
|---|--------|-------------|-----------|-------------|-----------|
| 1 | **CT-18** | Camión Mercedes Tolva | $97,800,231 | $96,987,414 | -$812,817 |
| 2 | **MN-03** | Motoniveladora Komatsu | $35,181,210 | $50,156,500 | +$14,975,290 |
| 3 | **TC-03** | Tracto Camión Mercedes | $30,898,462 | $104,592,400 | +$73,693,938 |
| 4 | **EX-12** | Excavadora | $29,184,608 | $28,296,000 | -$888,608 |
| 5 | **EX-16** | Excavadora Komatsu PC-300 | $27,825,381 | $21,672,000 | -$6,153,381 |
| 6 | **CP-8** | Camión Pluma | $27,632,285 | $161,206,250 | +$133,573,965 |
| 7 | **TC-01** | Tracto Camión | $24,703,484 | $79,729,200 | +$55,025,716 |
| 8 | **CF-05** | Cargador Frontal | $23,813,726 | $36,490,960 | +$12,677,234 |
| 9 | **EX-15** | Excavadora | $23,485,540 | $23,075,000 | -$410,540 |
| 10 | **BD-03** | Bulldozer | $21,563,611 | $26,676,000 | +$5,112,389 |
| 11 | **CI-02** | Camión International | $21,049,640 | $10,730,000 | -$10,319,640 |
| 12 | **EX-18** | Excavadora | $20,530,594 | $14,056,000 | -$6,474,594 |
| 13 | **EX-19** | Excavadora Komatsu | $19,249,652 | $9,750,000 | -$9,499,652 |
| 14 | **CT-37** | Camión Tolva | $18,619,536 | $7,000,000 | -$11,619,536 |
| 15 | **RX-09** | Retroexcavadora | $18,228,250 | $18,540,000 | +$311,750 |
| 16 | **CT-35** | Camión Tolva | $17,228,506 | $5,320,000 | -$11,908,506 |
| 17 | **CT-38** | Camión Tolva | $17,193,857 | $5,625,000 | -$11,568,857 |
| 18 | **EX-20** | Excavadora | $16,875,644 | $4,104,000 | -$12,771,644 |
| 19 | **CT-20** | Camión Tolva | $15,645,098 | $25,740,000 | +$10,094,902 |
| 20 | **CT-34** | Camión Tolva | $15,584,227 | $18,790,000 | +$3,205,773 |

---

## 5. COMBUSTIBLES POR MÁQUINA

Se identificaron **666 registros de combustible** con un total de **$54,199,919**.

### Top 10 Máquinas por Consumo de Combustible

| Código | Combustible Q4 |
|--------|----------------|
| CT-18 | ~$5.2M |
| CF-05 | ~$3.8M |
| CT-20 | ~$2.9M |
| TC-03 | ~$2.7M |
| CT-37 | ~$2.4M |
| EX-12 | ~$2.1M |
| CF-06 | ~$1.9M |
| CT-35 | ~$1.8M |
| CT-38 | ~$1.7M |
| EX-16 | ~$1.5M |

---

## 6. COMPARACIÓN CON DATABODEGA.CSV

| Fuente | Gastos Capturados | Observación |
|--------|-------------------|-------------|
| **DATABODEGA.csv** | ~$218M (solo repuestos Q4) | Solo captura salidas de bodega |
| **Reportes Contables** | $1,334M (gastos totales) | Incluye TODO: leasing, combustible, reparaciones, etc. |

### Gastos que DATABODEGA.csv NO captura:

| Tipo de Gasto | Monto | Observación |
|---------------|-------|-------------|
| Cuotas Leasing | $257.3M | Pagos a bancos (BCI, Santander, Itaú, etc.) |
| Reparaciones Externas | $71.9M | Servicios de terceros |
| Combustibles | $54.2M | Diesel, gasolina |
| Seguros | $15.2M | Pólizas de vehículos |
| Transportes/Fletes | $10.1M | Traslado de maquinaria |
| Remuneraciones Taller | $115.8M | Sueldos personal taller |
| Honorarios | $1.9M | Servicios profesionales |

---

## 7. ARCHIVOS GENERADOS

Se generaron los siguientes archivos en la carpeta `analisis_gastos/`:

| Archivo | Contenido | Registros |
|---------|-----------|-----------|
| `reportes_por_maquina.csv` | Totales por máquina/centro de costo | 161 |
| `reportes_combustibles.csv` | Detalle de combustibles por máquina | 666 |
| `reportes_detalle_movimientos.csv` | Todos los movimientos del período | 5,644 |
| `reportes_por_cuenta.csv` | Totales por tipo de gasto | 33 |

---

## 8. ACCIONES REQUERIDAS

### 🔴 URGENTE (Afecta imputación de gastos)

1. **Asignar códigos a centros sin normalizar:**
   - PLANTA CHANCADORA → PC-01
   - PLANTA HORMIGON → PH-01
   - TRACTORES → TC-XX (siguiente disponible)
   - CAMIONETAS sin código → C-XX (siguiente disponible)
   - CUATRIMOTOS → CM-XX

2. **Decidir qué hacer con TALLER ($137M):**
   - ¿Crear código TA-01?
   - ¿Distribuir entre máquinas?
   - ¿Separar remuneraciones?

### 🟡 IMPORTANTE (Mejora la calidad de datos)

3. **Verificar máquinas duplicadas:**
   - BARREDORA BROCE BW260 (sin código) vs BA-01 (con código)
   - ¿Son la misma máquina?

4. **Completar códigos de patentes:**
   - RWRH-53 → C-??
   - RXKR-45 → C-??
   - VGKX-71 → C-??

### 🟢 RECOMENDADO (Futuro)

5. **Integrar reportes contables al sistema principal**
6. **Automatizar la extracción de combustibles por máquina**

---

## 9. RESUMEN DE PROBLEMAS ACTUALIZADOS

### ✅ RESUELTOS (ya normalizados)
| Centro | Código | Gastos Imputados |
|--------|--------|------------------|
| TRACTOR CASE PUMA 155 | T-06 | $7.6M |
| CAMIONETA RAPTOR VGKX-71 | C-53 | $3.4M |
| CAMIONETA JMC RWRH-49 | C-29 | $1.4M |
| Otros (C-30, C-31, T-05) | Tentativos | $2.7M |

### ⚠️ PENDIENTES
| Problema | Impacto | Prioridad |
|----------|---------|-----------|
| TALLER sin código | $137.3M no imputables | 🔴 Alta |
| PLANTA CHANCADORA sin código | $24.8M no imputables | 🔴 Alta - Buscando info |
| PLANTA HORMIGON sin código | $0.4M no imputables | 🟡 Media |
| CUATRIMOTOS sin código | $0.2M no imputables | 🟢 Baja |
| BARREDORA BROCE (¿=BA-01?) | $0.1M | 🟢 Verificar |
| **TOTAL NO IMPUTABLE** | **$162.8M** | - |

---

## 10. COMPARATIVA DE INGRESOS: HARCHA MAQ APP vs CONSTRUIT

Se compararon dos fuentes de datos de producción/ingresos:
- **Harcha Maq App**: Sistema interno de reportes de producción diaria
- **Construit**: Sistema contable (facturas emitidas)

### 10.1 Totales Generales Q4 2025

| Fuente | Total Ingresos | Observación |
|--------|----------------|-------------|
| **Harcha Maq App** | **$1,209,613,760** | Producción reportada |
| **Construit** | **$633,396,931** | Facturado |
| **Diferencia** | **+$576,216,829** | +91% más en App |

⚠️ **La diferencia puede deberse a:**
- Producción reportada pero aún no facturada
- Diferencias en el período de registro
- Errores de codificación de máquinas

### 10.2 Top 10 Máquinas con Mayor Diferencia

| Código | Harcha App | Construit | Diferencia | Observación |
|--------|------------|-----------|------------|-------------|
| **C-38** | $205,506,000 | $5,199,600 | +$200.3M | ⚠️ Revisar |
| **CT-18** | $0 | $96,987,414 | -$97M | ⚠️ No está en App |
| **TC-03** | $47,261,200 | $12,791,400 | +$34.5M | Pendiente facturar |
| **EX-16** | $26,568,000 | $0 | +$26.6M | No facturado |
| **CF-04** | $23,808,000 | $191,505 | +$23.6M | Pendiente facturar |
| **CF-03** | $22,176,000 | $0 | +$22.2M | No facturado |
| **CF-06** | $20,319,400 | $0 | +$20.3M | No facturado |
| **CT-38** | $24,640,000 | $5,205,000 | +$19.4M | Pendiente facturar |
| **CF-07** | $20,665,200 | $1,584,450 | +$19.1M | Pendiente facturar |
| **CF-05** | $0 | $18,813,408 | -$18.8M | ⚠️ No está en App |

### 10.3 Máquinas Solo en Una Fuente

**Solo en Harcha App (no facturadas):**
| Código | Monto | Acción |
|--------|-------|--------|
| EX-16 | $26,568,000 | Verificar facturación |
| CF-03 | $22,176,000 | Verificar facturación |
| CF-06 | $20,319,400 | Verificar facturación |
| EX-03 | $13,227,500 | Verificar facturación |
| RXM-09 | $10,365,000 | Verificar facturación |
| G-03 | $10,368,000 | Verificar facturación |

**Solo en Construit (no en App):**
| Código | Monto | Acción |
|--------|-------|--------|
| CT-18 | $96,987,414 | ⚠️ Verificar en App |
| CF-05 | $18,813,408 | ⚠️ Verificar en App |
| RX-09 | $9,360,000 | ⚠️ Verificar en App |
| C-47 | $2,400,000 | Verificar en App |
| C-53 | $2,400,000 | Verificar en App |
| C-21 | $1,950,000 | Verificar en App |

### 10.4 Archivo Generado

Se generó el archivo `analisis_gastos/comparativa_produccion.csv` con el detalle completo de todas las máquinas.

---

*Informe generado automáticamente por scripts `analizar_reportes_contables.py` y `comparar_produccion.py`*
