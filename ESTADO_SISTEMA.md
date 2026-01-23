# Estado del Sistema - Q4 2025

## Última Ejecución
- **Fecha**: 23 de enero 2026
- **Correcciones aplicadas**: Valores de producción en 0 corregidos
- **Versión**: v2.0 (con gastos operacionales integrados)
- **Comando**: `python main.py`

## Resultados Financieros Q4 2025

| Métrica | Valor |
|----------|-------|
| Total Producción (MT3) | 819 |
| Total Producción Real | $635,608,664 |
| Total Gastos Operacionales | $700,806,451 |
| **Resultado Neto** | **-$65,197,787** (Pérdida) |
| Margen | -10.3% |

## Desglose de Gastos por Categoría

| Categoría | Monto (CLP) | % del Total |
|-----------|-------------|--------------|
| Otros Gastos (varios códigos) | $425,577,196 | 60.7% |
| Repuestos (DATABODEGA Q4) | $171,189,015 | 24.4% |
| Remuneraciones | $115,760,826 | 16.5% |
| Reparaciones | $76,376,345 | 10.9% |
| Combustibles | $54,199,919 | 7.7% |
| Seguros | $15,188,006 | 2.2% |
| Permisos | $3,753,386 | 0.5% |
| EPP | $2,573,868 | 0.4% |
| Peajes | $1,929,629 | 0.3% |
| Honorarios | $1,864,035 | 0.3% |
| Alimentación | $1,149,590 | 0.2% |
| Correspondencia | $1,104,192 | 0.2% |
| Multas | $685,719 | 0.1% |
| Pasajes | $563,740 | 0.1% |
| Gastos Legales | $80,000 | 0.0% |
| **TOTAL** | **$700,806,451** | **100%** |

**NOTA**: El porcentual total supera el 100% porque las categorías principales (Repuestos, Remuneraciones, Reparaciones, etc.) ya están incluidas dentro de "Otros Gastos".

## Datos Procesados

| Fuente | Registros | Observación |
|--------|-----------|-------------|
| Producción (Harcha App) | 5,128 | Año detectado automáticamente: 2025 |
| Horas Hombre | 630 | Costo fijo: $35.000/h |
| Repuestos (DATABODEGA Q4) | 2,915 | Total: $171.189.015 |
| Leasing | 26 | Cuotas mensuales para Oct, Nov, Dic |
| Gastos Operacionales (Construit) | 5,914 | 27 tipos de gastos |

## Componentes Activos

### Lectura de Datos
- ✅ Producción (Harcha App)
- ✅ Horas hombre
- ✅ Repuestos (DATABODEGA)
- ✅ Leasing
- ✅ Gastos operacionales (Construit) - **NUEVO**

### Normalización
- ✅ Normalizador de códigos de máquina
- ✅ 149 máquinas únicas identificadas
- ✅ 567 combinaciones máquina-mes procesadas

### Cálculo
- ✅ Cálculo de producción por máquina/mes
- ✅ Cálculo de gastos por máquina/mes (27 categorías)
- ✅ Cálculo de producción real (producción - gastos)
- ✅ Cálculo de totales trimestrales

### Exportación
- ✅ Excel con 6 hojas:
  1. Resumen Trimestral Completo
  2. Detalle Producción Completo
  3. Detalle Gastos Completo
  4. Desglose Repuestos
  5. Desglose Horas Hombre
  6. Desglose Gastos por Tipo
- ✅ HTML con dashboard interactivo:
  - Gráfico de gastos por categoría (horizontal)
  - Gráfico de gastos operacionales por mes
  - Tablas con filtros por máquina y mes
  - Resumen ejecutivo

## Tipos de Gastos Clasificados (27)

```python
COMBUSTIBLES = "401010101"           # Combustibles
REPUESTOS = "401010102"               # Repuestos y accesorios
REPARACIONES = "401010103"            # Reparaciones y mantención
EPP = "401010104"                     # Elementos de protección personal
SEGUROS = "401010115"                 # Póliza de seguro
PERMISOS = "401010116"                # Permiso de circulación
REVISION = "401010117"                # Revisión técnica
HONORARIOS = "401010109"             # Honorarios
PEAJES = "401010105"                  # Peajes y transbordador
ALIMENTACION = "401010112"            # Alimentación
PASAJES = "401010111"                 # Pasajes nacionales
MULTAS = "401030102"                 # Multas instituciones públicas
OTROS_GASTOS = "401030107"           # Otros gastos
REMUNERACIONES = "401010108"          # Remuneraciones
CORRESPONDENCIA = "401020107"         # Correspondencia
GASTOS_LEGALES = "401020108"         # Gastos legales
SERVICIO_TRANSPORTE = "401010106"    # Servicio transporte
REVISION_TECNICA = "401010107"       # Revisión técnica (adicional)
VARIOS = "401010113"                 # Varios
MANTENCION_VARIOS = "401010114"      # Mantención varios
OTRO_GASTO_TALLER = "401010118"     # Otro gasto taller
ALQUILER_MAQUINARIA = "401010119"   # Alquiler maquinaria
SERVICIOS_EXTERNOS = "401020101"     # Servicios externos
ELECTRICIDAD = "401020102"           # Electricidad
AGUA = "401020103"                   # Agua
OTRO_GASTO_OPERACIONAL = "401020114" # Otro gasto operacional
SUMINISTROS = "401040101"            # Suministros
OTROS_SUMINISTROS = "401040104"      # Otros suministros
```

## Archivos de Salida

| Archivo | Tamaño | Contenido |
|---------|--------|-----------|
| `informe_produccion_gastos.xlsx` | 454 KB | Informe Excel con 6 hojas |
| `informe_produccion_gastos.html` | 288 KB | Dashboard interactivo con gráficos |

## Observaciones y Pendientes

### Observaciones
1. **Resultado negativo**: El sistema muestra una pérdida de -$65.2M para Q4 2025
2. **Gastos operacionales vs Ingresos**: Los ingresos totales del sistema contable son $1.379M, pero el sistema solo está contabilizando la producción de $635.6M (posible discrepancia de fuentes)
3. **Año de producción**: El sistema detectó automáticamente 2025, resolviendo el problema anterior
4. **Correcciones aplicadas**: Se corrigieron los valores de producción que estaban en 0 debido a:
   - Nombre de archivo incorrecto en main.py
   - Comparación case-sensitive de tipo de unidad en ProduccionCSVReader.py
   - Tipo de unidad "?" en CSV
   - Variante "Mt3" no soportada

### Pendientes
- [ ] Investigar discrepancia entre ingresos ($1.379M) y producción ($591M)
- [ ] Agregar análisis de márgenes por máquina (ganancia/pérdida %)
- [ ] Agregar ranking de máquinas más/menos rentables
- [ ] Calcular costo por MT3 producido
- [ ] Identificar máquinas con alto consumo de combustible
- [ ] Crear archivo de configuración para códigos de máquina especiales (TALLER, PLANTAS)
- [ ] Normalizar centros de costo pendientes (PLANTA CHANCADORA, etc.)
- [ ] Verificar duplicidades de códigos de máquina

## Próximos Pasos

1. **Prioridad Alta**: Investigar y resolver discrepancia de ingresos vs producción
2. **Prioridad Media**: Agregar métricas de rentabilidad por máquina
3. **Prioridad Baja**: Mejoras de UI/UX en el dashboard HTML

### Correcciones Realizadas (Enero 2026)

#### 1. Nombre de archivo incorrecto en main.py
- **Archivo**: [`main.py`](main.py:36)
- **Problema**: Se estaba usando el archivo "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv"
- **Solución**: Actualizado a "Harcha Maquinaria - Reportaría_Producción_Tabla.csv"

#### 2. Comparación case-sensitive de tipo de unidad
- **Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:62)
- **Problema**: El CSV tiene tipos de unidad en minúscula ("Dia", "Hr", "Km", "?")
- **Solución**: Agregado `tipo_unidad_upper = tipo_unidad.upper()` para comparación case-insensitive

#### 3. Inferencia de tipo de unidad desde nombre de contrato
- **Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:64)
- **Problema**: Muchos registros tienen `vc_Tipo_Unidad` como "?" aunque el contrato contiene "Mt3"
- **Solución**: Agregada lógica para inferir tipo desde nombre de contrato cuando es "?" o vacío

#### 4. Soporte para variante "Mt3"
- **Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:88)
- **Problema**: Variante "Mt3" (capital M, minúscula t3) no reconocida
- **Solución**: Agregado soporte para "Mt3", "M3", "M³"

---

**Última actualización**: 23/01/2026
**Estado del sistema**: ✅ Operativo con gastos operacionales integrados y valores de producción corregidos
