# CONTEXTO DEL PROYECTO - GASTOS VS PRODUCCIÓN
# Fecha: 23/01/2026
# Cliente: Harcha Maquinaria SPA

## OBJETIVO DEL PROYECTO
Generar informe trimestral Q4 2025 (octubre, noviembre, diciembre) que compare producción vs gastos del parque de maquinaria.

## ESTADO ACTUAL DEL SISTEMA

### ✅ COMPLETADO

#### 1. LECTURA DE DATOS
- **Producción**: ProduccionCSVReader.py
  - Lee archivo "Harcha Maquinaria - Reportaría_Producción_Tabla.csv"
  - Filtra por meses 10, 11, 12 de 2025
  - Soporta: MT3, Horas, Km, Vueltas, Días, UF

- **Horas Hombre**: HorasHombreCSVReader.py
  - Lee archivo "_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv"
  - Filtra por Q4 2025
  - Costo fijo: $35.000 CLP por hora

- **Repuestos**: RepuestosCSVReader.py
  - Lee archivo "DATABODEGA.csv"
  - 2.915 registros en Q4 2025
  - Total: $171.189.015

- **Leasing**: LeasingCSVReader.py
  - Lee archivo "Leasing Credito HMAQ.csv"
  - 26 registros
  - Aplica cuota mensual para octubre, noviembre, diciembre

- **Gastos Operacionales**: ReportesContablesReader.py
  - Lee todos los CSV de gastos (camiones.csv, vehiculos.csv, taller.csv, etc.)
  - 5.914 registros filtrados (solo gastos 401xxx)
  - Total: $700.962.517
  - Filtra por Q4 2025

#### 2. ENTIDADES DE DOMINIO
- **GastoOperacional**: GastoOperacional.py
  - TipoGasto enum con 27 tipos de gastos
  - Mapeo completo a códigos contables (401010101-401040104)

- **CalculadorGastos**: CalculadorGastos.py
  - `calcular_por_maquina_mes()`: Cálculo básico (repuestos + HH + leasing)
  - `calcular_por_maquina_mes_completo()`: Incluye todos los tipos de gastos
  - `calcular_total_por_maquina_completo()`: Total por máquina del trimestre

#### 3. EXPORTADORES

**ExcelExporter.py**:
- `exportar()`: Generación básica de informes
- `exportar_completo()`: Generación completa con todos los gastos
  - Crea 6 hojas:
    1. Resumen Trimestral Completo
    2. Detalle Producción Completo
    3. Detalle Gastos Completo
    4. Desglose Repuestos
    5. Desglose Horas Hombre
    6. Desglose Gastos por Tipo

**HTMLExporter.py**:
- `exportar()`: Generación básica HTML
- `exportar_completo()`: Generación completa HTML con dashboard interactivo

#### 4. CAPA DE APLICACIÓN
- **InformeService.py**:
  - `leer_datos()`: Lee todos los datos y retorna tupla completa
  - `generar_informes()`: Genera Excel y HTML completos

- **main.py**: Punto de entrada que coordina todo el proceso
  - **Corrección**: Actualizado nombre de archivo de producción a "Harcha Maquinaria - Reportaría_Producción_Tabla.csv"

 ### ✅ ÚLTIMA EJECUCIÓN (23/01/2026)
  
  **DATOS PROCESADOS**:
 - **Registros de producción**: 5,128
- **Registros de horas hombre**: 630
- **Registros de repuestos (DATABODEGA Q4)**: 2,915
- **Registros de leasing**: 26
- **Registros de gastos operacionales (Construit)**: 5,914
- **Año detectado automáticamente**: 2025 (confirmado en ProduccionCSVReader.py)
 
 **ARCHIVOS GENERADOS**:
 - `informe_produccion_gastos.xlsx` (454 KB) - 6 hojas con análisis completo
 - `informe_produccion_gastos.html` (304 KB) - Dashboard interactivo con gráficos

## ANÁLISIS FINANCIERO ACTUAL (Q4 2025)

### TOTALES
- **Total Producción (MT3)**: 819
- **Total Producción Real**: $635,608,664
- **Total Gastos Operacionales**: $700,806,451
- **Resultado Neto**: **-$65,197,787** (PÉRDIDA)
- **Margen Promedio**: **-10.3%**

### DESGLOSE DE GASTOS POR CATEGORÍA
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

**NOTA**: El total porcentual supera el 100% porque las categorías principales (Repuestos, Remuneraciones, Reparaciones, etc.) ya están incluidas dentro de "Otros Gastos".

## CÓDIGOS DE GASTOS MAPEADOS

### Códigos del enum TipoGasto (27 tipos):
```python
COMBUSTIBLES = "401010101"           # Combustibles
REPUESTOS = "401010102"                # Repuestos y accesorios
REPARACIONES = "401010103"             # Reparaciones y mantención
EPP = "401010104"                       # Elementos de protección personal
SEGUROS = "401010115"                   # Póliza de seguro
PERMISOS = "401010116"                  # Permiso de circulación
REVISION = "401010117"                   # Revisión técnica
HONORARIOS = "401010109"                # Honorarios
PEAJES = "401010105"                    # Peajes y transbordador
ALIMENTACION = "401010112"              # Alimentación
PASAJES = "401010111"                   # Pasajes nacionales
MULTAS = "401030102"                    # Multas instituciones públicas
OTROS_GASTOS = "401030107"              # Otros gastos
REMUNERACIONES = "401010108"            # Remuneraciones
CORRESPONDENCIA = "401020107"           # Correspondencia
GASTOS_LEGALES = "401020108"            # Gastos legales
SERVICIO_TRANSPORTE = "401010106"       # Servicio transporte
REVISION_TECNICA = "401010107"          # Revisión técnica (adicional)
VARIOS = "401010113"                      # Varios
MANTENCION_VARIOS = "401010114"           # Mantención varios
OTRO_GASTO_TALLER = "401010118"          # Otro gasto taller
ALQUILER_MAQUINARIA = "401010119"        # Alquiler maquinaria ($257M)
SERVICIOS_EXTERNOS = "401020101"         # Servicios externos
ELECTRICIDAD = "401020102"                # Electricidad
AGUA = "401020103"                        # Agua
OTRO_GASTO_OPERACIONAL = "401020114"    # Otro gasto operacional
SUMINISTROS = "401040101"                 # Suministros
OTROS_SUMINISTROS = "401040104"           # Otros suministros
```

## ARCHIVOS GENERADOS

- **informe_produccion_gastos.xlsx**: 6 hojas con análisis completo
- **informe_produccion_gastos.html**: Dashboard interactivo con gráficos

## CAMBIOS RECIENTES (Enero 2026)

### 🆕 Integración de Gastos Operacionales (Enero 2026)
1. **Nueva Entidad**: `GastoOperacional.py`
   - Enum `TipoGasto` con 27 tipos de gastos clasificados
   - Mapeo completo a códigos contables (401010101-401040104)

2. **Nuevo Lector**: `ReportesContablesReader.py`
   - Lee 16 archivos CSV de reportes contables
   - Procesa 5,914 registros de gastos
   - Filtra automáticamente por Q4 2025
   - Identifica 149 máquinas únicas

3. **Expansión de** `CalculadorGastos.py`:
   - Método `calcular_por_maquina_mes_completo()` con desglose por tipo de gasto
   - Método `calcular_total_por_maquina_completo()` para totales trimestrales
   - Clasificación de 27 tipos de gastos operacionales
   - Corrección en cálculo de totales: `repuestos + gastos operacionales + HH + leasing`

4. **Actualización de** `InformeService.py`:
   - Lee gastos operacionales de carpeta gastos/
   - Combina datos de producción + gastos completos
   - Método `leer_datos()` retorna tupla con 5 elementos

5. **Nuevos Métodos de Exportación**:
   - `ExcelExporter.exportar_completo()`: 6 hojas con desglose completo
     1. Resumen Trimestral Completo
     2. Detalle Producción Completo
     3. Detalle Gastos Completo
     4. Desglose Repuestos
     5. Desglose Horas Hombre
     6. Desglose Gastos por Tipo
   - `HTMLExporter.exportar_completo()`: Dashboard con gastos por categoría
     - Gráfico de gastos por categoría (horizontal)
     - Gráfico de gastos operacionales por mes
     - Tabla de detalle por máquina y mes

6. **Actualización de** `main.py`:
    - Agregada ruta de reportes contables
    - Ejecuta `exportar_completo()` en ambos exportadores
    - **Corrección**: Actualizado nombre de archivo de producción

### 🔧 Correcciones Adicionales (Enero 2026)
7. **Corrección de valores de producción en 0**:
   - Archivo: `ProduccionCSVReader.py`
   - Problema: Comparación case-sensitive de tipo de unidad
   - Solución: Agregado `tipo_unidad_upper = tipo_unidad.upper()`
   
8. **Inferencia de tipo de unidad desde nombre de contrato**:
   - Archivo: `ProduccionCSVReader.py`
   - Problema: Tipo de unidad "?" en CSV
   - Solución: Inferir tipo desde nombre de contrato (MT3, HR, KM, DIA)
   
9. **Soporte para variante "Mt3"**:
   - Archivo: `ProduccionCSVReader.py`
   - Problema: Variante "Mt3" no reconocida
   - Solución: Agregado soporte para "Mt3", "M3", "M³"

### 🔧 Correcciones Anteriores (Diciembre 2025)
1. **Corrección del cálculo de totales en "Detalle Gastos Completo"**:
   - Archivo: `src/infrastructure/export/ExcelExporter.py` línea 298-302

2. **Corrección en CalculadorGastos**:
   - Archivo: `src/domain/services/CalculadorGastos.py` líneas 178-188

## TAREAS PENDIENTES

### 🎯 PRIORIDAD 1: MEJORAS DE REPORTING
- [ ] Agregar análisis de márgenes por máquina (ganancia/pérdida %)
- [ ] Agregar ranking de máquinas más/menos rentables
- [ ] Calcular costo por MT3 producido
- [ ] Identificar máquinas con alto consumo de combustible

### 🎯 PRIORIDAD 2: OPTIMIZACIÓN DE DATOS
- [ ] Crear archivo de configuración para códigos de máquina especiales (TALLER, PLANTAS)
- [ ] Normalizar centros de costo pendientes (PLANTA CHANCADORA, etc.)
- [ ] Verificar duplicidades de códigos de máquina

### 🎯 PRIORIDAD 3: MEJORAS AL INFORME
- [ ] Agregar gráfico de tendencia por mes (Oct-Nov-Dic)
- [ ] Agregar filtros por tipo de máquina (camiones, excavadoras, etc.)
- [ ] Agregar métrica de ROI por máquina
- [ ] Exportar reporte en PDF (opcional)

## COMANDOS ÚTILES

### Ejecutar el sistema:
```bash
cd "C:\Users\patricio dunstan sae\GastosVsProduccion"
python main.py
```

### Verificar sintaxis:
```bash
python -m py_compile src/infrastructure/export/ExcelExporter.py
python -m py_compile src/infrastructure/export/HTMLExporter.py
python -m py_compile src/application/InformeService.py
python -m py_compile src/domain/services/CalculadorGastos.py
```

### Probar imports:
```bash
python -c "from src.infrastructure.export.ExcelExporter import ExcelExporter; print('OK')"
python -c "from src.infrastructure.export.HTMLExporter import HTMLExporter; print('OK')"
python -c "from src.application.InformeService import InformeService; print('OK')"
```

## ESTRUCTURA DEL PROYECTO

```
GastosVsProduccion/
 ├── gastos/                          # Archivos CSV de datos
 │   ├── Harcha Maquinaria - Reportaría_Producción_Tabla.csv
│   ├── _Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv
│   ├── DATABODEGA.csv
│   ├── Leasing Credito HMAQ.csv
│   ├── camiones.csv
│   ├── vehiculos.csv
│   ├── taller.csv
│   └── ... (más archivos de gastos por tipo de máquina)
├── src/
│   ├── domain/
│   │   ├── entities/               # Entidades de dominio
│   │   │   ├── Produccion.py
│   │   │   ├── HorasHombre.py
│   │   │   ├── Repuesto.py
│   │   │   ├── Leasing.py
│   │   │   └── GastoOperacional.py
│   │   └── services/                # Servicios de dominio
│   │       ├── CalculadorProduccionReal.py
│   │       ├── CalculadorGastos.py
│   │       ├── NormalizadorMaquinas.py
│   │       └── ValorUFService.py
│   ├── infrastructure/
│   │   ├── csv/                    # Lectores de CSV
│   │   │   ├── ProduccionCSVReader.py
│   │   │   ├── HorasHombreCSVReader.py
│   │   │   ├── RepuestosCSVReader.py
│   │   │   ├── LeasingCSVReader.py
│   │   │   └── ReportesContablesReader.py
│   │   └── export/                 # Exportadores
│   │       ├── ExcelExporter.py
│   │       └── HTMLExporter.py
│   └── application/                # Capa de aplicación
│       └── InformeService.py
├── main.py                          # Punto de entrada
├── informe_produccion_gastos.xlsx # Salida Excel
├── informe_produccion_gastos.html  # Salida HTML
└── config_uf.json                   # Configuración valor UF
```

## NOTAS DE DESARROLLO

### Metodología
- Arquitectura Limpia (Clean Architecture)
- Código Limpio (Clean Code)
- Principios SOLID
- TDD (Test-Driven Development) - Pendiente implementar tests

### Costos fijos
- Valor UF: $38.000 CLP
- Costo por hora hombre: $35.000 CLP

### Filtros
- Meses: Octubre (10), Noviembre (11), Diciembre (12)
- Año: 2025 (para gastos, producción pendiente de definir)

## CONTACTO
- Cliente: Harcha Maquinaria SPA
- Proyecto: Sistema de Informes Producción vs Gastos
- Período: Q4 2025

---
**FIN DEL CONTEXTO - Para continuar mañana**
