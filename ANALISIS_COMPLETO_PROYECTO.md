# Análisis Completo del Proyecto GastosVsProducción

**Fecha**: 23 de enero 2026  
**Cliente**: Harcha Maquinaria SPA  
**Versión**: v2.1 (con correcciones de producción)

---

## Resumen Ejecutivo

El proyecto **GastosVsProducción** es un sistema de análisis financiero para Harcha Maquinaria SPA que compara la producción vs los gastos operacionales de maquinaria pesada. El sistema utiliza una arquitectura limpia con tres capas: Application, Domain e Infrastructure.

### Estado Actual

El sistema se encuentra **operativo** con las siguientes características:
- ✅ Lectura de datos de múltiples fuentes (Harcha Maq App, Construit, DATABODEGA, Leasing)
- ✅ Integración de 27 tipos de gastos operacionales
- ✅ Normalización automática de códigos de máquina
- ✅ Generación de informes en Excel y HTML con gráficos interactivos
- ✅ Correcciones aplicadas para calcular correctamente los valores de producción

---

## Arquitectura del Sistema

### Estructura de Capas

```
┌─────────────────────────────────────┐
│           Application               │  ← Orquestación
│         (InformeService)            │
├─────────────────────────────────────┤
│             Domain                  │  ← Lógica de negocio
│  (Entities, Services, Repositories) │
├─────────────────────────────────────┤
│          Infrastructure             │  ← Acceso a datos
│      (CSV Readers, Exporters)       │
└─────────────────────────────────────┘
```

### Estructura de Directorios

```
GastosVsProduccion/
├── main.py                              # Punto de entrada principal
├── requirements.txt                     # Dependencias Python
├── config_uf.json.example              # Ejemplo de configuración UF
│
├── src/                                # Código fuente
│   ├── application/                    # Capa de aplicación
│   │   └── InformeService.py          # Servicio orquestador
│   │
│   ├── domain/                         # Capa de dominio
│   │   ├── entities/                   # Entidades
│   │   │   ├── HorasHombre.py
│   │   │   ├── Leasing.py
│   │   │   ├── Maquina.py
│   │   │   ├── Produccion.py
│   │   │   ├── Repuesto.py
│   │   │   └── GastoOperacional.py
│   │   │
│   │   ├── repositories/               # Interfaces de repositorios
│   │   │   └── __init__.py
│   │   │
│   │   └── services/                   # Servicios de dominio
│   │       ├── CalculadorGastos.py
│   │       ├── CalculadorProduccion.py
│   │       ├── CalculadorProduccionReal.py
│   │       ├── NormalizadorMaquinas.py
│   │       └── ValorUFService.py
│   │
│   └── infrastructure/                 # Capa de infraestructura
│       ├── csv/                        # Lectores CSV
│       │   ├── HorasHombreCSVReader.py
│       │   ├── LeasingCSVReader.py
│       │   ├── ProduccionCSVReader.py
│       │   ├── RepuestosCSVReader.py
│       │   └── ReportesContablesReader.py
│       │
│       └── export/                     # Exportadores
│           ├── ExcelExporter.py
│           └── HTMLExporter.py
│
├── gastos/                             # Datos CSV/XLS
│   ├── Harcha Maquinaria - Reportaría_Producción_Tabla.csv
│   ├── _Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv
│   ├── DATABODEGA.csv
│   ├── Leasing Credito HMAQ.csv
│   ├── barredora.csv
│   ├── camiones.csv
│   └── ... (otros archivos)
│
├── analisis_gastos/                    # Reportes generados
│
├── informe_produccion_gastos.xlsx      # Reporte Excel
├── informe_produccion_gastos.html      # Dashboard HTML
│
└── Documentación/
    ├── README.md
    ├── CONTEXTO_PROYECTO.md
    ├── ESTADO_SISTEMA.md
    └── ANALISIS_COMPLETO_PROYECTO.md (este archivo)
```

---

## Entidades de Dominio

### 1. Produccion
Representa un registro de producción diaria reportada por operadores.

**Atributos**:
- `fecha`: Fecha del registro
- `maquina_codigo`: Código de la máquina
- `tipo_unidad`: Tipo de unidad (MT3, HR, KM, VUELTAS, DIA, UF)
- `unidades`: Cantidad de unidades producidas
- `contrato_txt`: Nombre del contrato

### 2. GastoOperacional
Representa un gasto operacional del sistema contable (Construit).

**Atributos**:
- `fecha`: Fecha del gasto
- `maquina_codigo`: Código de la máquina
- `tipo_gasto`: Tipo de gasto (enum con 27 categorías)
- `monto`: Monto del gasto
- `descripcion`: Descripción del gasto

**Tipos de Gasto (27 categorías)**:
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
ALQUILER_MAQUINARIA = "401010119"        # Alquiler maquinaria
SERVICIOS_EXTERNOS = "401020101"         # Servicios externos
ELECTRICIDAD = "401020102"                # Electricidad
AGUA = "401020103"                        # Agua
OTRO_GASTO_OPERACIONAL = "401020114"    # Otro gasto operacional
SUMINISTROS = "401040101"                 # Suministros
OTROS_SUMINISTROS = "401040104"           # Otros suministros
```

### 3. HorasHombre
Representa un registro de horas trabajadas por operadores.

**Atributos**:
- `fecha`: Fecha del registro
- `maquina_codigo`: Código de la máquina
- `horas`: Cantidad de horas trabajadas

**Costo fijo**: $35,000 CLP por hora

### 4. Repuesto
Representa una salida de repuesto de bodega (DATABODEGA).

**Atributos**:
- `fecha`: Fecha de la salida
- `maquina_codigo`: Código de la máquina
- `repuesto_codigo`: Código del repuesto
- `descripcion`: Descripción del repuesto
- `monto`: Monto del repuesto

### 5. Leasing
Representa una cuota mensual de leasing de maquinaria.

**Atributos**:
- `maquina_codigo`: Código de la máquina
- `cuota_mensual`: Cuota mensual del leasing

---

## Servicios de Dominio

### 1. NormalizadorMaquinas
Normaliza códigos de máquina desde diferentes formatos.

**Patrón de regex**: `r'\[?([A-Za-z]+-\d+[A-Za-z0-9-]*)\]?'`

**Mapeo especial**:
| Centro de Costo | Código |
|-----------------|--------|
| TRACTOR CASE PUMA 155 | T-06 |
| CAMIONETA RAPTOR VGKX-71 | C-53 |
| CAMIONETA JMC RWRH-49 | C-29 |

### 2. CalculadorGastos
Calcula gastos por máquina y mes.

**Métodos**:
- `calcular_por_maquina_mes()`: Cálculo básico (repuestos + HH + leasing)
- `calcular_por_maquina_mes_completo()`: Incluye todos los tipos de gastos
- `calcular_total_por_maquina_completo()`: Total por máquina del trimestre

### 3. CalculadorProduccion
Calcula producción por máquina y mes.

**Métodos**:
- `calcular_por_maquina_mes()`: Cálculo de producción por máquina y mes
- `calcular_total_por_maquina()`: Total por máquina del trimestre

### 4. CalculadorProduccionReal
Calcula producción real (producción - gastos).

**Métodos**:
- `calcular_por_maquina_mes()`: Cálculo de producción real por máquina y mes
- `calcular_total_por_maquina()`: Total por máquina del trimestre

### 5. ValorUFService
Obtiene y gestiona el valor de la UF.

**Valor actual**: $38,000 CLP

---

## Lectores CSV

### 1. ProduccionCSVReader
Lee datos de producción desde el archivo CSV.

**Archivo**: `Harcha Maquinaria - Reportaría_Producción_Tabla.csv`

**Filtros**:
- Meses: 10, 11, 12 (Octubre, Noviembre, Diciembre)
- Año: Detectado automáticamente (2025)

**Soporta**: MT3, Horas, Km, Vueltas, Días, UF

**Correcciones aplicadas**:
1. Comparación case-insensitive de tipo de unidad
2. Inferencia de tipo de unidad desde nombre de contrato cuando `vc_Tipo_Unidad` es "?"
3. Soporte para variante "Mt3" (capital M, minúscula t3)

### 2. HorasHombreCSVReader
Lee datos de horas hombre desde el archivo CSV.

**Archivo**: `_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv`

**Costo fijo**: $35,000 CLP por hora

### 3. RepuestosCSVReader
Lee datos de repuestos desde el archivo CSV.

**Archivo**: `DATABODEGA.csv`

**Registros**: 2,915 en Q4 2025

**Total**: $171,189,015

### 4. LeasingCSVReader
Lee datos de leasing desde el archivo CSV.

**Archivo**: `Leasing Credito HMAQ.csv`

**Registros**: 26

**Cuota mensual**: Aplicada para octubre, noviembre, diciembre

### 5. ReportesContablesReader
Lee datos de gastos operacionales desde múltiples archivos CSV.

**Archivos**: 16 archivos CSV de reportes contables

**Registros**: 5,914 filtrados (solo gastos 401xxx)

**Total**: $700,962,517

**Filtros**:
- Meses: 10, 11, 12 (Octubre, Noviembre, Diciembre)
- Año: 2025
- Cuentas: Solo gastos 401xxx

---

## Exportadores

### 1. ExcelExporter
Genera informes en formato Excel.

**Métodos**:
- `exportar()`: Generación básica de informes
- `exportar_completo()`: Generación completa con todos los gastos

**Hojas generadas**:
1. Resumen Trimestral Completo
2. Detalle Producción Completo
3. Detalle Gastos Completo
4. Desglose Repuestos
5. Desglose Horas Hombre
6. Desglose Gastos por Tipo

### 2. HTMLExporter
Genera informes en formato HTML con dashboard interactivo.

**Métodos**:
- `exportar()`: Generación básica HTML
- `exportar_completo()`: Generación completa HTML con dashboard interactivo

**Componentes del dashboard**:
- Resumen ejecutivo con totales
- Gráfico de gastos por categoría (horizontal)
- Gráfico de gastos operacionales por mes
- Tabla de detalle por máquina y mes

---

## Correcciones Realizadas (Enero 2026)

### Problema: Valores de producción en 0

**Síntoma**: Los valores de producción (MT3, horas, kilómetros) se mostraban como 0.0 en el informe HTML.

### Causas identificadas

1. **Nombre de archivo incorrecto en main.py**
   - Se estaba usando: `"Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv"`
   - Archivo correcto: `"Harcha Maquinaria - Reportaría_Producción_Tabla.csv"`

2. **Comparación case-sensitive de tipo de unidad en ProduccionCSVReader.py**
   - El CSV tiene tipos de unidad en minúscula: "Dia", "Hr", "Km", "?"
   - El código estaba comparando usando `.upper()` pero no convertía el input primero

3. **Tipo de unidad no especificado en el CSV**
   - Muchos registros tienen `vc_Tipo_Unidad` como "?"
   - El contrato contiene "Mt3" pero no se estaba infiriendo el tipo

4. **Variante "Mt3" no soportada**
   - El CSV tiene "Mt3" (capital M, minúscula t3)
   - El código solo reconocía "MT3" (todo mayúscula)

### Soluciones aplicadas

#### 1. Actualización de nombre de archivo en main.py

**Archivo**: [`main.py`](main.py:36)

```python
# Antes:
archivo_produccion = os.path.join(base_dir, "gastos", "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv")

# Después:
archivo_produccion = os.path.join(base_dir, "gastos", "Harcha Maquinaria - Reportaría_Producción_Tabla.csv")
```

#### 2. Corrección de case-sensitive en ProduccionCSVReader.py

**Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:62)

```python
# Agregado:
tipo_unidad_upper = tipo_unidad.upper()
# Usado para todas las comparaciones
```

#### 3. Inferencia de tipo de unidad desde nombre de contrato

**Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:64)

```python
# Si el tipo de unidad es "?" o está vacío, inferir desde el nombre del contrato
if tipo_unidad_upper == '?' or not tipo_unidad:
    contrato_upper = contrato_txt.upper()
    if 'MT3' in contrato_upper:
        tipo_unidad_upper = 'MT3'
    elif 'HR' in contrato_upper or 'HORAS' in contrato_upper:
        tipo_unidad_upper = 'HR'
    elif 'KM' in contrato_upper and 'MT3' not in contrato_upper:
        tipo_unidad_upper = 'KM'
    elif 'DIA' in contrato_upper:
        tipo_unidad_upper = 'DIA'
```

#### 4. Soporte para variante "Mt3"

**Archivo**: [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:88)

```python
# Agregado soporte para "Mt3" (capital M, minúscula t3)
if tipo_unidad_upper == 'MT3' or tipo_unidad_upper == 'M3' or tipo_unidad_upper == 'M³':
    # Lógica para MT3
```

### Resultado

Los datos de producción se calculan correctamente:
- **CT-10,10**: MT3 = 343.0
- **CT-26,11**: MT3 = 476.0, Horas Trabajadas = 88.0

---

## Resultados Financieros Q4 2025

### Totales

| Métrica | Valor |
|----------|-------|
| Total Producción (MT3) | 819 |
| Total Producción Real | $635,608,664 |
| Total Gastos Operacionales | $700,806,451 |
| **Resultado Neto** | **-$65,197,787** (Pérdida) |
| Margen Promedio | -10.3% |

### Desglose de Gastos por Categoría

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

---

## Archivos Generados

### Informe Excel

**Archivo**: `informe_produccion_gastos.xlsx` (454 KB)

**Hojas**:
1. Resumen Trimestral Completo
2. Detalle Producción Completo
3. Detalle Gastos Completo
4. Desglose Repuestos
5. Desglose Horas Hombre
6. Desglose Gastos por Tipo

### Dashboard HTML

**Archivo**: `informe_produccion_gastos.html` (304 KB)

**Componentes**:
- Resumen ejecutivo con totales
- Gráficos interactivos con Chart.js
- Tablas con filtros por máquina y mes
- Diseño responsive

**Estructura del HTML**:
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <title>Informe Producción vs Gastos Completo - Q4 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* Estilos CSS */
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Informe Producción vs Gastos Completo</h1>
        <p class="subtitle">Trimestre Q4 2025 - Con todos los gastos operacionales</p>
        
        <div class="summary-cards">
            <!-- Tarjetas de resumen -->
            <div class="card">
                <h3>Total Producción (MT3)</h3>
                <div class="value" id="total-mt3">0</div>
            </div>
            <!-- ... más tarjetas -->
        </div>
        
        <div class="chart-container">
            <canvas id="chartGastos"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="chartProduccion"></canvas>
        </div>
        
        <h2>Detalle por Máquina y Mes</h2>
        <table>
            <thead>
                <tr>
                    <th>Máquina</th>
                    <th>Mes</th>
                    <th>Repuestos</th>
                    <th>Combustibles</th>
                    <th>Reparaciones</th>
                    <th>Total Gastos</th>
                </tr>
            </thead>
            <tbody id="tabla-detalles">
                <!-- Filas generadas dinámicamente -->
            </tbody>
        </table>
    </div>
    
    <script>
        const datos = { /* Objeto con datos de producción y gastos */ };
        const meses = ['Octubre', 'Noviembre', 'Diciembre'];
        
        // Cálculo de totales
        // Generación de gráficos
        // Generación de tablas
    </script>
</body>
</html>
```

---

## Tareas Pendientes

### Prioridad 1: Mejoras de Reporting
- [ ] Agregar análisis de márgenes por máquina (ganancia/pérdida %)
- [ ] Agregar ranking de máquinas más/menos rentables
- [ ] Calcular costo por MT3 producido
- [ ] Identificar máquinas con alto consumo de combustible

### Prioridad 2: Optimización de Datos
- [ ] Crear archivo de configuración para códigos de máquina especiales (TALLER, PLANTAS)
- [ ] Normalizar centros de costo pendientes (PLANTA CHANCADORA, etc.)
- [ ] Verificar duplicidades de códigos de máquina

### Prioridad 3: Mejoras al Informe
- [ ] Agregar gráfico de tendencia por mes (Oct-Nov-Dic)
- [ ] Agregar filtros por tipo de máquina (camiones, excavadoras, etc.)
- [ ] Agregar métrica de ROI por máquina
- [ ] Exportar reporte en PDF (opcional)

---

## Comandos Útiles

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

---

## Metodología de Desarrollo

- **Arquitectura Limpia** (Clean Architecture)
- **Código Limpio** (Clean Code)
- **Principios SOLID**
- **TDD** (Test-Driven Development) - Pendiente implementar tests

### Costos Fijos
- Valor UF: $38,000 CLP
- Costo por hora hombre: $35,000 CLP

### Filtros
- Meses: Octubre (10), Noviembre (11), Diciembre (12)
- Año: 2025

---

## Contacto

- **Cliente**: Harcha Maquinaria SPA
- **Proyecto**: Sistema de Informes Producción vs Gastos
- **Período**: Q4 2025

---

**Fin del Análisis Completo del Proyecto**
