---
name: Informe Producción vs Gastos
overview: Crear un sistema que procese datos de producción, horas hombre, repuestos y gastos operacionales para generar informes mensuales y trimestrales en Excel y HTML, calculando la producción real (trabajo realizado - gastos).
todos:
  - id: "1"
    content: Crear entidades de dominio (Maquina, Produccion, HorasHombre, Repuesto)
    status: completed
  - id: "2"
    content: Implementar NormalizadorMaquinas para extraer códigos de máquinas
    status: completed
  - id: "3"
    content: Crear lectores CSV para cada archivo (Produccion, HorasHombre, Repuestos)
    status: completed
    dependencies:
      - "1"
      - "2"
  - id: "4"
    content: Implementar CalculadorProduccion para agregar MT3, horas, km, vueltas por máquina/mes
    status: completed
    dependencies:
      - "1"
  - id: "5"
    content: Implementar CalculadorGastos para sumar repuestos y calcular costo HH (HH × $35.000)
    status: completed
    dependencies:
      - "1"
  - id: "6"
    content: Implementar CalculadorProduccionReal (Producción - Gastos Totales)
    status: completed
    dependencies:
      - "4"
      - "5"
  - id: "7"
    content: Crear ExcelExporter con múltiples hojas (Resumen, Detalle Producción, Detalle Gastos, Desgloses)
    status: completed
    dependencies:
      - "4"
      - "5"
      - "6"
  - id: "8"
    content: Crear HTMLExporter con dashboard interactivo y gráficos
    status: completed
    dependencies:
      - "4"
      - "5"
      - "6"
  - id: "9"
    content: Implementar InformeService como orquestador principal
    status: completed
    dependencies:
      - "3"
      - "4"
      - "5"
      - "6"
      - "7"
      - "8"
  - id: "10"
    content: Crear main.py con costo HH fijo $35.000 y ejecutar proceso
    status: completed
    dependencies:
      - "9"
  - id: "11"
    content: Crear entidad GastoOperacional con 27 tipos de gastos
    status: completed
    dependencies:
      - "1"
  - id: "12"
    content: Crear lector ReportesContablesReader para gastos operacionales
    status: completed
    dependencies:
      - "11"
  - id: "13"
    content: Expandir CalculadorGastos con desglose completo por tipo de gasto
    status: completed
    dependencies:
      - "11"
      - "12"
  - id: "14"
    content: Actualizar InformeService para integrar gastos operacionales
    status: completed
    dependencies:
      - "12"
      - "13"
  - id: "15"
    content: Implementar exportar_completo() en ExcelExporter (6 hojas)
    status: completed
    dependencies:
      - "13"
      - "14"
  - id: "16"
    content: Implementar exportar_completo() en HTMLExporter (dashboard actualizado)
    status: completed
    dependencies:
      - "13"
      - "14"
  - id: "17"
    content: Actualizar main.py para ejecutar exportar_completo()
    status: completed
    dependencies:
      - "15"
      - "16"
---

# Plan: Sistema de Informe Producción vs Gastos

## Objetivo

Generar informes mensuales y trimestrales (octubre, noviembre, diciembre 2025) que muestren por máquina: producción, gastos en repuestos, gastos operacionales (27 tipos), horas hombre, y producción real (trabajo realizado - gastos).

## Arquitectura de la Solución

### Estructura de Archivos

```
src/
├── domain/
│   ├── entities/
│   │   ├── Maquina.py          # Entidad máquina con código normalizado
│   │   ├── Produccion.py       # Entidad producción (MT3, horas, km, vueltas)
│   │   ├── HorasHombre.py      # Entidad horas hombre
│   │   └── Repuesto.py         # Entidad repuesto con costo
│   ├── repositories/
│   │   ├── IProduccionRepository.py
│   │   ├── IHorasHombreRepository.py
│   │   └── IRepuestosRepository.py
│   └── services/
│       ├── NormalizadorMaquinas.py      # Normaliza códigos de máquinas
│       ├── CalculadorProduccion.py      # Calcula producción total (MT3, horas, km, vueltas)
│       ├── CalculadorGastos.py          # Calcula gastos totales (repuestos + HH)
│       ├── CalculadorProduccionReal.py  # Calcula producción real (producción - gastos)
│       └── GeneradorInformes.py         # Genera Excel y HTML
├── infrastructure/
│   ├── csv/
│   │   ├── ProduccionCSVReader.py
│   │   ├── HorasHombreCSVReader.py
│   │   └── RepuestosCSVReader.py
│   └── export/
│       ├── ExcelExporter.py
│       └── HTMLExporter.py
├── application/
│   └── InformeService.py       # Orquestador principal
└── main.py                      # Punto de entrada
```

## Flujo de Procesamiento

```mermaid
flowchart TD
    A[Inicio] --> B[Leer CSV Producción]
    A --> C[Leer CSV Horas Hombre]
    A --> D[Leer CSV Repuestos]
    
    B --> E[Filtrar Oct-Nov-Dic 2025]
    C --> F[Filtrar Oct-Nov-Dic 2025]
    D --> G[Filtrar Oct-Nov-Dic 2025]
    
    E --> H[Normalizar Códigos Máquinas]
    F --> H
    G --> H
    
    H --> I[Agrupar por Máquina y Mes]
    
    I --> J[Calcular Producción Total]
    I --> K[Calcular Horas Hombre]
    I --> L[Calcular Gastos Repuestos]
    
    J --> J1[Agregar MT3, Horas, KM, Vueltas]
    K --> M[Calcular Costo HH = HH × $35.000]
    L --> N[Sumar Total Repuestos]
    
    M --> O[Calcular Gastos Totales]
    N --> O
    
    J1 --> P[Calcular Producción Real]
    O --> P
    P --> P1[Producción Real = Producción - Gastos Totales]
    
    P --> Q[Generar Excel]
    P --> R[Generar HTML]
    
    Q --> S[Fin]
    R --> S
```

## Componentes Principales

### 1. Normalizador de Máquinas (`NormalizadorMaquinas.py`)

- Extrae código de máquina usando regex: `\[?([A-Z]+-\d+[A-Z0-9-]*)\]?`
- Normaliza formatos como:
  - `[CT-10 HKDX21] - FOTON AUMAN 3239 `→ `CT-10 HKDX21`
  - `CT-10 HKDX21 - FOTON - AUMAN 3239` → `CT-10 HKDX21`
  - `CT-10 CAMION FOTON HKDX21` → `CT-10 HKDX21`

### 2. Lectores CSV

- **ProduccionCSVReader**: Lee `Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv`
  - Parsear fecha formato `dd/mm/yyyy`
  - Detectar automáticamente el año
  - Extraer: MT3, HORAS_TRABAJADAS, KILOMETROS, VUELTAS
- **HorasHombreCSVReader**: Lee `_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv`
  - Parsear fecha formato `dd MMM yyyy` (ej: "31 dic 2025")
  - Extraer horas hombre
- **RepuestosCSVReader**: Lee `DATABODEGA.csv`
  - Parsear fecha formato `dd-mm-yyyy`
  - Filtrar por "Centro Costo(Salida)" que contenga código de máquina
  - Extraer total de repuestos
- **LeasingCSVReader**: Lee `Leasing Credito HMAQ.csv`
  - Parsear cuotas de leasing mensual
- **ReportesContablesReader** (NUEVO): Lee 16 archivos CSV de reportes contables
  - Parsea formato de reportes contables
  - Filtra por Q4 2025 automáticamente
  - Extrae 27 tipos de gastos operacionales

### 3. Calculador de Producción (`CalculadorProduccion.py`)

- Agrega producción por máquina/mes:
  - Suma de MT3 (metros cúbicos)
  - Suma de horas trabajadas
  - Suma de kilómetros
  - Suma de vueltas
- Maneja valores "No hay datos" como 0

### 4. Calculador de Gastos (`CalculadorGastos.py`)

- **calcular_por_maquina_mes()**: Cálculo básico
  - Suma gastos de repuestos por máquina/mes
  - Calcula costo HH = horas × $35.000 (costo fijo)
  - Total gastos = repuestos + costo HH + leasing
- **calcular_por_maquina_mes_completo()** (NUEVO): Cálculo con desglose
  - Incluye 27 tipos de gastos operacionales
  - Clasifica por: combustibles, reparaciones, seguros, honorarios, EPP, etc.
  - Total = repuestos + gastos operacionales + HH + leasing
- **calcular_total_por_maquina_completo()** (NUEVO): Totales trimestrales

### 5. Calculador de Producción Real (`CalculadorProduccionReal.py`)

- Calcula producción real = Producción Total - Gastos Totales
- Por cada unidad de producción (MT3, horas, km, vueltas)
- También calcula valor monetario de producción real

### 6. Generadores de Informes

#### Excel (`ExcelExporter.py`)

- `exportar()`: Generación básica (5 hojas)
  - Hoja 1: Resumen Trimestral
  - Hoja 2: Detalle Producción Mensual
  - Hoja 3: Detalle Gastos Mensual
  - Hoja 4: Desglose Repuestos
  - Hoja 5: Desglose Horas Hombre
- `exportar_completo()` (NUEVO): Generación completa (6 hojas)
  - Hoja 1: Resumen Trimestral Completo
  - Hoja 2: Detalle Producción Completo
  - Hoja 3: Detalle Gastos Completo (con 27 categorías)
  - Hoja 4: Desglose Repuestos
  - Hoja 5: Desglose Horas Hombre
  - Hoja 6: Desglose Gastos por Tipo

#### HTML (`HTMLExporter.py`)

- `exportar()`: Dashboard básico
  - Gráficos de gastos por mes
  - Gráficos de producción por mes
  - Tablas interactivas con filtros
  - Resumen ejecutivo
- `exportar_completo()` (NUEVO): Dashboard actualizado
  - Gráfico de gastos por categoría (horizontal)
  - Gráfico de gastos operacionales por mes
  - Tabla de detalle por máquina y mes
  - Resumen ejecutivo con 5 métricas clave

## Datos de Configuración

- **Costo fijo por hora**: $35.000 CLP (fijo para todos los mecánicos)
- **Meses a procesar**: Octubre, Noviembre, Diciembre 2025
- **Formato de fechas**: Múltiples formatos a normalizar

## Archivos a Procesar

1. `_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv`
2. `DATABODEGA.csv`
3. `Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv`

## Salidas Generadas

1. `informe_produccion_gastos.xlsx` - Informe completo en Excel
2. `informe_produccion_gastos.html` - Informe interactivo en HTML

## Consideraciones Técnicas

- Manejo de fechas en múltiples formatos
- Normalización de códigos de máquinas (regex)
- Manejo de valores "No hay datos" en CSV
- Agregación de datos por máquina y mes
- Cálculo de producción real = producción - (repuestos + HH × costo)
- Formato de moneda chilena (CLP) en reportes