# Sistema de Análisis Producción vs Gastos

**Harcha Maquinaria SPA** - Sistema de análisis financiero para gestión de maquinaria

## Descripción

Sistema para analizar y comparar la producción vs gastos de maquinaria pesada y vehículos. Integra datos de múltiples fuentes:

- **Harcha Maq App**: Producción diaria reportada por operadores
- **Construit**: Sistema contable con facturación y gastos (27 tipos de gastos)
- **DATABODEGA**: Salida de repuestos de bodega
- **Leasing**: Cuotas mensuales de leasing de maquinaria

---

## Índice

1. [Instalación](#instalación)
2. [Archivos de Datos](#archivos-de-datos)
3. [Scripts Disponibles](#scripts-disponibles)
4. [Estructura del Proyecto](#estructura-del-proyecto)
5. [Uso](#uso)
6. [Arquitectura](#arquitectura)
7. [Normalización de Códigos](#normalización-de-códigos)
8. [Reportes Generados](#reportes-generados)

---

## Instalación

### Requisitos
- Python 3.8 o superior
- Windows 10/11

### Pasos

```bash
# 1. Clonar o descargar el proyecto
cd GastosVsProduccion

# 2. Instalar dependencias
pip install -r requirements.txt
```

### Dependencias
- `openpyxl` - Generación de archivos Excel
- `xlrd` - Lectura de archivos XLS antiguos

---

## Archivos de Datos

Todos los archivos de datos deben estar en la carpeta `gastos/`:

### Archivos Principales

| Archivo | Fuente | Contenido |
|---------|--------|-----------|
| `Harcha Maquinaria - Reportaría_Producción_Tabla.csv` | Harcha Maq App | Producción diaria |
| `_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv` | Harcha Maq App | Horas hombre |
| `DATABODEGA.csv` | Bodega | Salida de repuestos |
| `Leasing Credito HMAQ.csv` | Contabilidad | Cuotas de leasing |

### Reportes Contables (Construit)

| Archivo | Tipo de Maquinaria |
|---------|-------------------|
| `barredora.csv` | Barredoras |
| `bulldozer.csv` | Bulldozers |
| `camiones.csv` | Camiones tolva |
| `cargadores.csv` | Cargadores frontales |
| `exc.csv` | Excavadoras |
| `gruas.csv` | Grúas |
| `maquinaria asfaltica.csv` | Maquinaria asfáltica |
| `motoniveladoras.csv` | Motoniveladoras |
| `retros.csv` | Retroexcavadoras |
| `rodillos.csv` | Rodillos |
| `taller.csv` | Taller general |
| `tractores.csv` | Tractores |
| `vehiculos.csv` | Vehículos livianos |
| `vehiculos operaciones.csv` | Vehículos operaciones |

---

## Fuentes de Datos

### Sistema Contable (Construit) - INTEGRADO EN ENE 2026
- **16 archivos CSV** con reportes de gastos/ingresos
- **27 tipos de gastos operacionales** clasificados
- **5,914 registros** procesados en Q4 2025
- **Total gastos Q4 2025**: $700,806,451
- **Total ingresos Q4 2025**: $1,379,494,912
- **Resultado neto**: +$678,688,461 (ganancia positiva)

**Categorías de Gastos:**
- Repuestos y accesorios: $171.2M
- Remuneraciones: $115.8M
- Reparaciones y mantención: $76.4M
- Combustibles: $54.2M
- Seguros: $15.2M
- Otros (peajes, EPP, honorarios, permisos, etc.): $268.0M

### DATABODEGA
- Salidas de repuestos de bodega
- **17,061 registros** históricos (todos los meses)
- **2,915 registros** en Q4 2025
- **Total Q4 2025**: $218,904,568 en repuestos

**NOTA**: DATABODEGA solo captura salidas de repuestos de bodega. Los reportes contables (Construit) capturan TODOS los gastos operacionales (combustibles, reparaciones externas, leasing, seguros, etc.).

---

## Scripts Disponibles

### 1. `main.py` - Sistema Principal

Genera informes completos de producción vs gastos con **todos los gastos operacionales integrados**.

```bash
python main.py
```

**Salida:**
- `informe_produccion_gastos.xlsx` (454 KB) - Informe Excel con 6 hojas:
  1. Resumen Trimestral Completo
  2. Detalle Producción Completo
  3. Detalle Gastos Completo (con 27 categorías de gastos)
  4. Desglose Repuestos
  5. Desglose Horas Hombre
  6. Desglose Gastos por Tipo
- `informe_produccion_gastos.html` (288 KB) - Dashboard interactivo:
  - Resumen ejecutivo con totales
  - Gráfico de gastos por categoría (horizontal)
  - Gráfico de gastos operacionales por mes
  - Tablas con filtros por máquina y mes

### 2. `analizar_reportes_contables.py` - Análisis de Construit

Procesa los CSV de reportes contables y extrae gastos/ingresos por máquina.

```bash
python analizar_reportes_contables.py
```

**Salida en `analisis_gastos/`:**
- `reportes_por_maquina.csv` - Totales por máquina
- `reportes_por_cuenta.csv` - Totales por tipo de gasto
- `reportes_detalle_movimientos.csv` - Detalle completo
- `reportes_combustibles.csv` - Gastos de combustible
- `RESUMEN_REPORTES_CONTABLES.txt` - Resumen ejecutivo

### 3. `comparar_produccion.py` - Comparativa de Fuentes

Compara los ingresos de Harcha Maq App vs Construit.

```bash
python comparar_produccion.py
```

**Salida:**
- `analisis_gastos/comparativa_produccion.csv` - Comparativa por máquina

### 4. `comparar_totales.py` - Verificación de Totales

Verifica que los totales del sistema sean consistentes.

```bash
python comparar_totales.py
```

---

## Estructura del Proyecto

```
GastosVsProduccion/
│
├── main.py                              # Punto de entrada principal
├── analizar_reportes_contables.py       # Análisis de Construit
├── comparar_produccion.py               # Comparativa Harcha App vs Construit
├── comparar_totales.py                  # Verificación de totales
│
├── requirements.txt                     # Dependencias Python
├── config_uf.json.example              # Ejemplo de configuración UF
├── README.md                           # Este archivo
├── INFORME_ANALISIS_GASTOS_Q4_2025.md  # Informe de análisis actual
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
│   │   │   └── Repuesto.py
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
│   ├── DATABODEGA.csv
│   ├── Leasing Credito HMAQ.csv
│   ├── barredora.csv
│   ├── camiones.csv
│   └── ... (otros archivos)
│
├── analisis_gastos/                    # Reportes generados
│   ├── comparativa_produccion.csv
│   ├── reportes_por_maquina.csv
│   ├── reportes_combustibles.csv
│   └── ...
│
├── informe_produccion_gastos.xlsx      # Reporte Excel
└── informe_produccion_gastos.html      # Dashboard HTML
```

---

## Uso

### Flujo Típico de Análisis

```bash
# 1. Generar informe principal
python main.py

# 2. Analizar reportes contables de Construit
python analizar_reportes_contables.py

# 3. Comparar fuentes de producción
python comparar_produccion.py
```

### Actualización de Datos

1. Descargar nuevos CSV de Harcha Maq App y Construit
2. Colocar archivos en carpeta `gastos/`
3. Ejecutar scripts según necesidad

---

## Arquitectura

El sistema sigue **Arquitectura Limpia** y principios **SOLID**:

### Capas

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

### Entidades

| Entidad | Descripción |
|---------|-------------|
| `Maquina` | Representa una máquina/vehículo |
| `Produccion` | Registro de producción diaria |
| `Repuesto` | Salida de repuesto de bodega |
| `HorasHombre` | Registro de horas trabajadas |
| `Leasing` | Cuota de leasing |

### Servicios

| Servicio | Responsabilidad |
|----------|----------------|
| `NormalizadorMaquinas` | Normaliza códigos de máquina |
| `CalculadorProduccion` | Calcula producción por máquina |
| `CalculadorGastos` | Calcula gastos por máquina |
| `CalculadorProduccionReal` | Calcula producción - gastos |
| `ValorUFService` | Obtiene/gestiona valor UF |

---

## Normalización de Códigos

El sistema normaliza automáticamente los códigos de máquinas:

### Patrones Reconocidos

| Prefijo | Tipo | Ejemplos |
|---------|------|----------|
| CT | Camiones Tolva | CT-06, CT-10, CT-18 |
| EX | Excavadoras | EX-03, EX-16, EX-19 |
| CF | Cargadores Frontales | CF-04, CF-05, CF-06 |
| RX | Retroexcavadoras | RX-03, RX-04, RX-09 |
| MN | Motoniveladoras | MN-01, MN-02, MN-03 |
| BD | Bulldozers | BD-02, BD-03 |
| TC | Tracto Camiones | TC-01, TC-02, TC-03 |
| CP | Camiones Pluma | CP-02, CP-08 |
| GM | Grúas Móviles | GM-01, GM-02 |
| BA | Barredoras | BA-01 |
| T | Tractores | T-05, T-06 |
| C | Vehículos Livianos | C-29, C-53 |

### Mapeo Especial

Algunos centros de costo sin código estándar están mapeados:

| Centro de Costo | Código |
|-----------------|--------|
| TRACTOR CASE PUMA 155 | T-06 |
| CAMIONETA RAPTOR VGKX-71 | C-53 |
| CAMIONETA JMC RWRH-49 | C-29 |

---

## Reportes Generados

### Informe Excel (`informe_produccion_gastos.xlsx`)

| Hoja | Contenido |
|------|-----------|
| Resumen Trimestral | Producción vs gastos por máquina |
| Detalle Producción | Desglose mensual de producción |
| Detalle Gastos | Desglose mensual de gastos |
| Desglose Repuestos | Lista completa de repuestos |
| Desglose Horas Hombre | Lista completa de HH |

### Dashboard HTML (`informe_produccion_gastos.html`)

- Resumen ejecutivo con totales
- Gráficos interactivos
- Tablas con filtros
- Diseño responsive

### Reportes de Análisis (`analisis_gastos/`)

| Archivo | Contenido |
|---------|-----------|
| `reportes_por_maquina.csv` | Totales gastos/ingresos por máquina |
| `reportes_por_cuenta.csv` | Totales por tipo de cuenta |
| `reportes_combustibles.csv` | Detalle de combustibles |
| `comparativa_produccion.csv` | Harcha App vs Construit |

---

## Configuración

### Valor UF

El valor de la UF se configura en `config_uf.json`:

```json
{
    "valor_uf": 38500,
    "fecha_actualizacion": "2025-12-01"
}
```

### Costo Hora Hombre

Configurado en `src/domain/services/CalculadorGastos.py`:

```python
COSTO_HORA = Decimal('35000')  # $35.000 CLP
```

### Período de Análisis

Por defecto: **Q4 2025** (Octubre, Noviembre, Diciembre)

---

## Correcciones Realizadas (Enero 2026)

### Problema: Valores de producción en 0

**Síntoma**: Los valores de producción (MT3, horas, kilómetros) se mostraban como 0.0 en el informe HTML.

**Causas identificadas**:
1. Nombre de archivo incorrecto en [`main.py`](main.py:36)
2. Comparación case-sensitive de tipo de unidad en [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py)
3. Tipo de unidad no especificado en el CSV (valor "?")
4. Variante "Mt3" no soportada

**Soluciones aplicadas**:

1. **Actualización de nombre de archivo** en [`main.py`](main.py:36):
   ```python
   # Antes:
   archivo_produccion = os.path.join(base_dir, "gastos", "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv")
   
   # Después:
   archivo_produccion = os.path.join(base_dir, "gastos", "Harcha Maquinaria - Reportaría_Producción_Tabla.csv")
   ```

2. **Corrección de case-sensitive** en [`ProduccionCSVReader.py`](src/infrastructure/csv/ProduccionCSVReader.py:62):
   ```python
   # Agregado:
   tipo_unidad_upper = tipo_unidad.upper()
   # Usado para todas las comparaciones
   ```

3. **Inferencia de tipo de unidad** desde nombre de contrato:
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

4. **Soporte para variante "Mt3"**:
   ```python
   # Agregado soporte para "Mt3" (capital M, minúscula t3)
   if tipo_unidad_upper == 'MT3' or tipo_unidad_upper == 'M3' or tipo_unidad_upper == 'M³':
   ```

**Resultado**: Los datos de producción se calculan correctamente:
- CT-10,10: MT3 = 343.0
- CT-26,11: MT3 = 476.0, Horas Trabajadas = 88.0

---

## Tipos de Gastos Capturados

### Desde DATABODEGA.csv
- Repuestos y accesorios

### Desde Reportes Contables (Construit)
- Combustibles (401010101)
- Repuestos y accesorios (401010102)
- Reparaciones y mantención (401010103)
- EPP (401010104)
- Transporte/fletes (401010106)
- Honorarios (401010109)
- Seguros (401010115)
- Cuotas leasing (401010119)

---

## Mantenimiento

### Agregar Nuevo Código de Máquina

En `analizar_reportes_contables.py`, agregar al diccionario `MAPEO_CENTROS_COSTO`:

```python
MAPEO_CENTROS_COSTO = {
    'NUEVO CENTRO': 'XX-NN',
    # ...
}
```

### Agregar Nuevo Tipo de Cuenta

En `analizar_reportes_contables.py`, agregar al diccionario de mapeo de cuentas:

```python
CUENTAS_NOMBRE = {
    '401010XXX': 'NOMBRE_CUENTA',
    # ...
}
```

---

## Autor

Sistema desarrollado para **Harcha Maquinaria SPA**

## Licencia

Uso interno exclusivo.
