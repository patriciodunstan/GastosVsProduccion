# Informe de Ejecución y Análisis del Proyecto

**Fecha:** 23 de enero 2026  
**Cliente:** Harcha Maquinaria SPA  
**Estado:** Ejecución completada con problemas detectados

---

## 1. Ejecución del Proyecto

### Comando Ejecutado
```bash
python main.py
```

### Resultado de la Ejecución
```
============================================================
SISTEMA DE INFORMES - PRODUCCIÓN VS GASTOS
Trimestre Q4 2025 (Octubre, Noviembre, Diciembre)
============================================================

Costo fijo por hora de trabajo: $35.000 CLP

Obteniendo valor de la UF...
  Valor UF utilizado: $38,000 CLP
  (Nota: Si necesitas actualizar el valor, edita config_uf.json o proporciona el valor manualmente)

Leyendo datos de producción...
  - Año detectado automáticamente: 2025
  - 5127 registros de producción leídos
Leyendo datos de horas hombre...
  - 630 registros de horas hombre leídos
Leyendo datos de repuestos (DATABODEGA)...
  - 2915 registros de repuestos leídos
Leyendo datos de leasing...
  - 26 registros de leasing leídos
Leyendo datos de gastos operacionales (reportes contables)...
  - 5914 registros de gastos operacionales leídos

Generando informe Excel...
  - Archivo Excel generado: c:\Users\patricio dunstan sae\GastosVsProduccion\informe_produccion_gastos.xlsx

Generando informe HTML...
  - Archivo HTML generado: c:\Users\patricio dunstan sae\GastosVsProduccion\informe_produccion_gastos.html

[OK] Informes generados exitosamente!
```

---

## 2. Problema Identificado: Valores en 0

### Descripción del Problema

El informe HTML generado muestra **valores en 0** para:
- Total Producción (MT3): 0
- Total Gastos Op.: $0
- Total Combustibles: $0
- Total Reparaciones: $0
- Total Producción Real: $0

### Causa Raíz

**PROBLEMA CRÍTICO: Desfase de años entre datos de producción y período de análisis**

Los datos de producción en el archivo `Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv` son de **enero 2026**:
- 30/01/2026
- 28/01/2026

Pero el sistema está configurado para analizar **Q4 2025** (octubre, noviembre, diciembre de 2025).

**Evidencia del problema:**
```csv
ESTADO_CONTRATO,CONTRATO_TXT,MAQUINA_FULL,CLIENTE_TXT,OBRA,OPERADOR,RUT OPERADOR,ID REPORTE,FECHA REPORTE,vc_Tipo_Unidad,vc_Precio_Unidades,vc_Unidades
Vigente,CT00626KmDia,CI-02 GGHD72 - FREIGHTLINER - GGHD72,Familia Constructora Spa (FAMCO),"DV06 LAS HUELLAS, QUIMAN",Abel Enrique Riquelme Sáez,11.295.322-1,21370,30/01/2026,Dia,290000,1
Vigente,CT00846Hr,RC-01 DBFS56 - CATERPILLAR - CS 533 EICH,DV08 TRAMO 1 CHOSHUENCO,Jaime Perez,9.519.609-8,21440,28/01/2026,Hr,25000,1
Vigente,CT00986Km,"C-39 SRPL60 - MAXUS - T60 DX 4X4 CABSIM 2,8CC",CONSORCIO,DV010 RUPUMEICA,Patricio Américo Coronado Coronado,10.958.079-0,21172,23/01/2026,Km,1400,176
```

### Impacto del Problema

1. **Filtrado incorrecto de producción:** El sistema filtra por Q4 2025 (oct, nov, dic 2025), pero los datos de producción son de enero 2026
2. **Registros de producción leídos:** 5,127 registros (pero estos registros no corresponden al período Q4 2025)
3. **Valores en 0:** Como no hay datos de producción para Q4 2025, el total de MT3 es 0
4. **Gastos operacionales:** Los gastos sí se están calculando correctamente (5,914 registros de Q4 2025)

---

## 3. Análisis de la Estructura del Informe

### 3.1 Informe Excel (`informe_produccion_gastos.xlsx`)

**Tamaño:** 454 KB  
**Hojas generadas:** 6

| Hoja | Contenido |
|------|-----------|
| Resumen Trimestral Completo | Producción vs gastos por máquina (trimestral) |
| Detalle Producción Completo | Desglose mensual de producción |
| Detalle Gastos Completo | Desglose mensual de gastos con 27 categorías |
| Desglose Repuestos | Lista completa de repuestos |
| Desglose Horas Hombre | Lista completa de horas hombre |
| Desglose Gastos por Tipo | Gastos operacionales por tipo y máquina |

### 3.2 Informe HTML (`informe_produccion_gastos.html`)

**Tamaño:** 288 KB  
**Características:**
- Dashboard interactivo con Chart.js
- Tarjetas de resumen ejecutivo
- Gráficos de gastos por categoría (horizontal)
- Gráficos de gastos operacionales por mes
- Tablas con filtros por máquina y mes
- Diseño responsive

**Estructura del HTML:**
```html
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Producción vs Gastos Completo - Q4 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        /* Estilos CSS para el dashboard */
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Informe Producción vs Gastos Completo</h1>
        <p class="subtitle">Trimestre Q4 2025 - Con todos los gastos operacionales</p>
        
        <div class="summary-cards">
            <!-- 5 tarjetas de resumen -->
        </div>
        
        <div class="chart-container">
            <canvas id="chartGastos"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="chartProduccion"></canvas>
        </div>
        
        <h2>Detalle por Máquina y Mes</h2>
        <table>
            <!-- Tabla de detalles -->
        </table>
    </div>
    
    <script>
        const datos = { /* Objeto JSON con datos */ };
        
        // Cálculo de totales
        Object.values(datos).forEach(item => {
            totalMT3 += parseFloat(item.produccion.mt3 || 0);
            totalGastosOp += parseFloat(item.gastos.total_gastos_operacionales || 0);
            // ...
        });
        
        // Generación de gráficos
        new Chart(...)
        
        // Llenado de tablas
    </script>
</body>
</html>
```

### 3.3 Datos en el HTML

**Objeto `datos` en JavaScript:**
```javascript
const datos = {
    "CT37,12": {
        "produccion": {
            "mt3": 0.0,
            "horas_trabajadas": 0.0,
            "kilometros": 0.0,
            "vueltas": 0.0
        },
        "gastos": {
            "repuestos": 0.0,
            "combustibles": 0.0,
            "reparaciones": 0.0,
            "seguros": 0.0,
            "honorarios": 0.0,
            "epp": 0.0,
            "peajes": 0.0,
            "remuneraciones": 0.0,
            "permisos": 0.0,
            "alimentacion": 0.0,
            "pasajes": 0.0,
            "correspondencia": 0.0,
            "gastos_legales": 0.0,
            "multas": 0.0,
            "otros_gastos": 0.0,
            "total_gastos_operacionales": 0.0
        },
        "produccion_real": {
            "valor_monetario": -12627373.109243697
        }
    },
    // ... más máquinas
};
```

**Observaciones:**
1. La mayoría de las máquinas tienen `mt3: 0.0` (producción en metros cúbicos)
2. Los gastos operacionales sí se están calculando correctamente
3. La producción real es negativa cuando no hay producción (solo gastos)

---

## 4. Análisis de los Datos Procesados

### 4.1 Datos de Producción

**Archivo:** `Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv`  
**Registros leídos:** 5,127  
**Año detectado:** 2025 (automático)  
**Problema:** Los datos son de enero 2026, no de Q4 2025

### 4.2 Datos de Horas Hombre

**Archivo:** `_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv`  
**Registros leídos:** 630  
**Costo fijo:** $35,000 CLP por hora

### 4.3 Datos de Repuestos (DATABODEGA)

**Archivo:** `DATABODEGA.csv`  
**Registros leídos:** 2,915  
**Total Q4 2025:** $171,189,015 CLP

### 4.4 Datos de Leasing

**Archivo:** `Leasing Credito HMAQ.csv`  
**Registros leídos:** 26

### 4.5 Datos de Gastos Operacionales (Construit)

**Archivos:** 16 archivos CSV (camiones.csv, vehiculos.csv, taller.csv, etc.)  
**Registros leídos:** 5,914  
**Total gastos Q4 2025:** $700,806,451 CLP

---

## 5. Conclusiones y Recomendaciones

### 5.1 Problemas Identificados

1. **CRÍTICO: Desfase de años**
   - Los datos de producción son de enero 2026
   - El sistema está configurado para Q4 2025
   - Esto causa que la producción sea 0

2. **Hardcoding del período de análisis**
   - Meses de filtro: [10, 11, 12] (hardcoded en varios archivos)
   - Año de filtro: 2025 (hardcoded en ReportesContablesReader.py)

3. **Falta de validación de datos**
   - El sistema no valida si hay datos de producción para el período seleccionado
   - No muestra advertencias cuando los datos están vacíos

4. **Error de JavaScript en informe_v2.html**
   - El informe `informe_produccion_gastos_v2.html` tiene un error de sintaxis JavaScript
   - Error: "SyntaxError: Unexpected number"

### 5.2 Recomendaciones

#### Prioridad Alta

1. **Corregir el desfase de años**
   - Actualizar el archivo de producción para que tenga datos de Q4 2025
   - O hacer configurable el período de análisis

2. **Parametrizar el período de análisis**
   - Crear un archivo `config.json` para configurar:
     - Año de análisis
     - Meses a incluir
     - Ruta de archivos de datos

3. **Agregar validación de datos**
   - Verificar si hay datos de producción para el período seleccionado
   - Mostrar advertencias cuando los datos estén vacíos

4. **Corregir el error de JavaScript en informe_v2.html**
   - Revisar la línea 162 del archivo HTML
   - Corregir la sintaxis del objeto JSON

#### Prioridad Media

1. **Mejorar el informe HTML**
   - Agregar indicadores visuales cuando no hay datos
   - Mostrar mensaje de advertencia cuando los valores son 0
   - Agregar opción para seleccionar el período de análisis

2. **Agregar logs de depuración**
   - Mostrar qué registros se están filtrando
   - Mostrar qué registros se están excluyendo
   - Ayudar a identificar problemas de datos

#### Prioridad Baja

1. **Documentar el proceso de actualización de datos**
   - Crear guía para actualizar los archivos CSV
   - Documentar el formato esperado de los archivos
   - Agregar ejemplos de archivos válidos

---

## 6. Arquitectura del Sistema

### 6.1 Capas del Sistema

```
┌─────────────────────────────────────────────┐
│           Application               │  ← Orquestación
│         (InformeService)            │
├─────────────────────────────────────────────┤
│             Domain                  │  ← Lógica de negocio
│  (Entities, Services, Repositories) │
├─────────────────────────────────────────────┤
│          Infrastructure             │  ← Acceso a datos
│      (CSV Readers, Exporters)       │
└─────────────────────────────────────────────┘
```

### 6.2 Componentes Principales

| Componente | Archivo | Responsabilidad |
|-----------|----------|----------------|
| Punto de entrada | `main.py` | Ejecutar el proceso completo |
| Servicio de aplicación | `InformeService.py` | Orquestar lectura y exportación |
| Entidades de dominio | `src/domain/entities/` | Representar datos del negocio |
| Servicios de dominio | `src/domain/services/` | Calcular producción y gastos |
| Lectores CSV | `src/infrastructure/csv/` | Leer archivos CSV |
| Exportadores | `src/infrastructure/export/` | Generar Excel y HTML |

---

## 7. Flujo de Datos

```
Archivos CSV
     ↓
InformeService.leer_datos()
     ↓
┌─────────────────────────────────────────┐
│  ProduccionCSVReader              │
│  HorasHombreCSVReader            │
│  RepuestosCSVReader              │
│  LeasingCSVReader                 │
│  ReportesContablesReader         │
└─────────────────────────────────────────┘
     ↓
Entidades de Dominio
     ↓
┌─────────────────────────────────────────┐
│  CalculadorProduccionReal          │
│  CalculadorGastos                 │
└─────────────────────────────────────────┘
     ↓
Datos Combinados
     ↓
┌─────────────────────────────────────────┐
│  ExcelExporter.exportar_completo() │
│  HTMLExporter.exportar_completo()  │
└─────────────────────────────────────────┘
     ↓
Archivos de Salida
  - informe_produccion_gastos.xlsx
  - informe_produccion_gastos.html
```

---

## 8. Resumen Ejecutivo

| Aspecto | Estado |
|----------|--------|
| Ejecución del proyecto | ✅ Completada |
| Lectura de datos | ✅ Completada |
| Generación de informes | ✅ Completada |
| Valores de producción | ❌ En 0 (desfase de años) |
| Valores de gastos | ✅ Calculados correctamente |
| Informe HTML | ⚠️ Muestra valores en 0 |
| Informe Excel | ✅ Generado correctamente |

---

**Fin del Informe de Ejecución**
