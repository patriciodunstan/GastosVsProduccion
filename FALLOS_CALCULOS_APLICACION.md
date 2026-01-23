# Fallos de Cálculos Identificados en la Aplicación GastosVsProducción

## Contexto

El usuario ha identificado múltiples fallos de cálculo en el informe generado:
1. Total Producción Neta: $1.209.613.760
2. Total Gastos: $1.348.320.713
3. Total Producción Real: $562.099.499

Matemáticamente: $1.209.613.760 - $1.348.320.713 = -$138.706.953

Pero el valor mostrado es $562.099.499, lo cual es inconsistente.

## Flujo de Cálculo en la Aplicación

### 1. Lectura de Datos (InformeService.leer_datos)

```python
producciones = ProduccionCSVReader(ruta_produccion, valor_uf=valor_uf)
horas_hombre = HorasHombreCSVReader(ruta_horas_hombre)
repuestos = RepuestosCSVReader(ruta_repuestos)
leasing = LeasingCSVReader(ruta_leasing)  # opcional
gastos_operacionales = ReportesContablesReader(ruta_gastos)  # opcional
```

### 2. Generación de Informe HTML (InformeService.generar_informes)

```python
html_exporter = HTMLExporter(ruta_html)
html_exporter.exportar_completo(
    producciones,
    repuestos,
    horas_hombre,
    gastos_operacionales,
    leasing
)
```

### 3. Cálculo de Producción Real (CalculadorProduccionReal.calcular_por_maquina_mes)

```python
# En CalculadorProduccionReal.calcular_por_maquina_mes:
prod_por_mes = CalculadorProduccion.calcular_por_maquina_mes(producciones)
gastos_por_mes = CalculadorGastos.calcular_por_maquina_mes(repuestos, horas_hombre, leasing)

# Combinar resultados
for clave in todas_las_claves:
    prod = prod_por_mes.get(clave, {...})
    gastos = gastos_por_mes.get(clave, {...})
    
    # Calcular producción neta
    produccion_neta = prod.get('valor_monetario', Decimal('0'))
    
    # Calcular producción real
    produccion_real = produccion_neta - gastos['total']
```

## Fallos de Cálculo Identificados

### Fallo 1: Inconsistencia en el cálculo de Producción Real

**Ubicación**: [`CalculadorProduccionReal.calcular_por_maquina_mes`](src/domain/services/CalculadorProduccionReal.py:98)

**Descripción**: 
- El cálculo de producción real usa `gastos['total']` de `CalculadorGastos.calcular_por_maquina_mes`
- Este `total` solo incluye repuestos + costo_hh + leasing
- NO incluye los gastos operacionales (combustibles, reparaciones, seguros, etc.)
- Esto causa que la producción real esté sobreestimada positivamente

**Impacto**: 
- La producción real mostrada no refleja la realidad financiera del negocio
- Los gastos operacionales (combustibles, reparaciones, seguros, etc.) no se están considerando en el cálculo de la producción real

**Corrección Necesaria**:
- Modificar `CalculadorProduccionReal.calcular_por_maquina_mes` para aceptar un parámetro opcional `gastos_completos`
- Cuando se proporciona `gastos_completos`, usar estos datos para calcular la producción real
- Cuando no se proporciona `gastos_completos`, usar `CalculadorGastos.calcular_por_maquina_mes_completo` que incluye todos los gastos

### Fallo 2: Error de Acceso a Clave Inexistente

**Ubicación**: [`HTMLExporter._generar_filas_resumen`](src/infrastructure/export/HTMLExporter.py:722), [`HTMLExporter._generar_filas_gastos`](src/infrastructure/export/HTMLExporter.py:812)

**Descripción**: 
- El código intenta acceder a `gastos['total']` que no existe cuando se incluyen gastos operacionales
- Cuando `incluir_gastos_operacionales=True`, el diccionario `gastos` tiene la clave `'total_gastos_operacionales'` en lugar de `'total'`
- Pero el código sigue intentando acceder a `gastos['total']` en múltiples lugares

**Impacto**: 
- Error de ejecución al generar las tablas de resumen y gastos por mes
- El HTML no se genera correctamente

**Corrección Necesaria**:
- En `_generar_filas_resumen`, cambiar `gastos['total']` por `gastos.get('total', Decimal('0'))`
- En `_generar_filas_gastos`, cambiar `gastos.get('total', Decimal('0'))` por `gastos.get('total_gastos_operacionales', Decimal('0'))` cuando `incluir_gastos_operacionales=True`
- O usar una lógica condicional para detectar cuál clave usar

### Fallo 3: Falta de Información en el HTML

**Ubicación**: [`HTMLExporter._generar_html_estatico`](src/infrastructure/export/HTMLExporter.py:325)

**Descripción**: 
- El HTML generado solo tiene 3 tarjetas de resumen:
  1. Total Gastos
  2. Total Producción Neta
  3. Total Producción Real
- Falta la tarjeta "Total Producción (MT3)" que estaba en la versión anterior

**Impacto**: 
- El usuario no puede ver el total de producción en MT3
- Falta información importante para el análisis

**Corrección Necesaria**:
- Agregar la tarjeta "Total Producción (MT3)" al HTML generado
- Calcular y mostrar `total_mt3` y `total_horas` en las tarjetas de resumen

### Fallo 4: Total Horas Trabajadas siempre muestra 0

**Ubicación**: [`HTMLExporter._generar_html_estatico`](src/infrastructure/export/HTMLExporter.py:298)

**Descripción**: 
- En `_generar_html_completo`, se establece explícitamente `total_horas=Decimal('0')`
- Esto hace que siempre se muestre 0 en la tarjeta de resumen

**Impacto**: 
- El usuario no puede ver el total de horas trabajadas

**Corrección Necesaria**:
- Calcular correctamente `total_horas` sumando `valores['produccion']['horas_trabajadas']`
- En `_generar_html_estatico`, cambiar `total_horas=Decimal('0')` por `total_horas` calculado

## Prioridad de Correcciones

### Prioridad 1: Corregir cálculo de Producción Real (CRÍTICO)

1. Modificar `CalculadorProduccionReal.calcular_por_maquina_mes` para aceptar parámetro `gastos_completos`
2. Implementar lógica para usar `gastos_completos` cuando se proporciona
3. Calcular producción real usando `total_gastos_completo` que incluye todos los gastos

### Prioridad 2: Corregir acceso a claves inexistentes (ALTO)

1. Modificar `_generar_filas_resumen` y `_generar_filas_gastos` para usar la clave correcta según el contexto
2. Implementar lógica condicional para detectar cuál clave usar

### Prioridad 3: Agregar tarjetas faltantes al HTML (MEDIA)

1. Agregar tarjeta "Total Producción (MT3)" al HTML generado
2. Calcular y mostrar `total_mt3` y `total_horas` en las tarjetas de resumen
3. Calcular y mostrar `total_horas` correctamente

## Notas para Implementación

1. **Importante**: El cambio debe ser consistente con el flujo de cálculo existente
2. **Testing**: Verificar que los cálculos sean correctos con los datos reales
3. **Documentación**: Actualizar la documentación del proyecto para reflejar los cambios
4. **Validación**: Comparar los resultados con los datos esperados por el usuario

## Conclusión

El sistema de cálculo tiene múltiples problemas de consistencia que deben ser corregidos para que el informe refleje la realidad financiera del negocio. Las correcciones deben implementarse de manera prioritaria, comenzando por la corrección más crítica: el cálculo de Producción Real para incluir todos los gastos operacionales.
