# Análisis de Cálculos en la Aplicación GastosVsProduccion

## Contexto

El usuario ha identificado múltiples fallos de cálculo en el informe generado:
1. Total Producción Neta: $1.209.613.760
2. Total Gastos: $1.348.320.713
3. Total Producción Real: $562.099.499

Matemáticamente: $1.209.613.760 - $1.348.320.713 = -$138.706.953

Pero el valor mostrado es $562.099.499, lo cual es inconsistente.

## Flujo de Cálculo en la Aplicación

### 1. Lectura de Datos (InformeService.leer_datos)

```
producciones = ProduccionCSVReader(ruta_produccion, valor_uf=valor_uf)
horas_hombre = HorasHombreCSVReader(ruta_horas_hombre)
repuestos = RepuestosCSVReader(ruta_repuestos)
leasing = LeasingCSVReader(ruta_leasing)  # opcional
gastos_operacionales = ReportesContablesReader(ruta_gastos)  # opcional
```

### 2. Generación de Informe HTML (InformeService.generar_informes)

```
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
    
    resultado[clave] = {
        'produccion': prod,
        'gastos': gastos,
        'produccion_neta': {'valor_monetario': produccion_neta, ...},
        'produccion_real': {'valor_monetario': produccion_real, ...}
    }
```

**PROBLEMA IDENTIFICADO**: 
- `gastos['total']` en `CalculadorGastos.calcular_por_maquina_mes` solo incluye:
  - repuestos
  - costo_hh
  - leasing
- NO incluye gastos operacionales

Pero cuando se calcula la producción real, se usa este `gastos['total']` incompleto.
```

### 4. Cálculo de Gastos Completos (CalculadorGastos.calcular_por_maquina_mes_completo)

```python
# En CalculadorGastos.calcular_por_maquina_mes_completo:
resultado[clave]['total'] = (
    resultado[clave]['repuestos'] +
    resultado[clave]['costo_hh'] +
    resultado[clave]['leasing'] +
    resultado[clave]['total_gastos_operacionales']  # Incluye todos los gastos operacionales
)
```

**PROBLEMA IDENTIFICADO**:
- El `total` en `calcular_por_maquina_mes_completo` incluye todos los gastos correctamente
- Pero este `total` NO se está usando en `CalculadorProduccionReal.calcular_por_maquina_mes`

### 5. Generación de HTML (HTMLExporter._generar_html_completo)

```python
# En HTMLExporter._generar_html_completo:
# Calcular totales
total_mt3 = Decimal('0')
total_gastos_op = Decimal('0')  # Solo gastos operacionales
total_repuestos = Decimal('0')
total_horas_hombre = Decimal('0')
total_costo_hh = Decimal('0')
total_leasing = Decimal('0')
total_combustibles = Decimal('0')
total_reparaciones = Decimal('0')
total_prod_neta = Decimal('0')
total_prod_real = Decimal('0')

# Iterar sobre datos
for (maquina, mes), valores in datos.items():
    total_gastos_op += valores['gastos'].get('total_gastos_operacionales', Decimal('0'))
    total_repuestos += valores['gastos'].get('repuestos', Decimal('0'))
    total_horas_hombre += valores['gastos'].get('horas_hombre', Decimal('0'))
    total_costo_hh += valores['gastos'].get('costo_hh', Decimal('0'))
    total_leasing += valores['gastos'].get('leasing', Decimal('0'))
    total_combustibles += valores['gastos'].get('combustibles', Decimal('0'))
    total_reparaciones += valores['gastos'].get('reparaciones', Decimal('0'))
    total_prod_neta += valores['produccion_neta']['valor_monetario']
    total_prod_real += valores['produccion_real']['valor_monetario']

# Calcular total de gastos completo
total_gastos_completo = (total_repuestos + total_costo_hh + total_leasing + 
                          total_combustibles + total_reparaciones + total_gastos_op)

# Generar HTML con total_gastos_completo
html = self._generar_html_estatico(
    total_mt3=total_mt3,
    total_horas=Decimal('0'),
    total_gastos=total_gastos_completo,  # Usar total_gastos_completo
    total_prod_neta=total_prod_neta,
    total_prod_real=total_prod_real,
    ...
)
```

**PROBLEMA IDENTIFICADO**:
- El `total_gastos_completo` se calcula correctamente incluyendo todos los tipos de gastos
- Pero en el método `_generar_filas_resumen` y `_generar_filas_gastos`, se sigue usando `gastos.get('total', Decimal('0'))` que en el contexto de gastos completos NO existe (se usa `total_gastos_operacionales`)

### 6. Tablas de Resumen en HTML

```python
# En HTMLExporter._generar_filas_resumen:
for maquina, valores in datos_ordenados:
    gastos = valores['gastos']
    fila += f"""<td>{self._formatear_moneda(gastos['total'])}</td>"""
```

**PROBLEMA IDENTIFICADO**:
- Cuando `incluir_gastos_operacionales=True`, el diccionario `gastos` tiene la estructura:
  ```python
  {
      'repuestos': Decimal,
      'horas_hombre': Decimal,
      'costo_hh': Decimal,
      'leasing': Decimal,
      'combustibles': Decimal,
      'reparaciones': Decimal,
      'seguros': Decimal,
      'honorarios': Decimal,
      'epp': Decimal,
      'peajes': Decimal,
      'remuneraciones': Decimal,
      'permisos': Decimal,
      'alimentacion': Decimal,
      'pasajes': Decimal,
      'correspondencia': Decimal,
      'gastos_legales': Decimal,
      'multas': Decimal,
      'otros_gastos': Decimal,
      'total_gastos_operacionales': Decimal,
      'total': Decimal  # Este 'total' NO incluye gastos operacionales
  }
  ```
- Pero el código intenta acceder a `gastos['total']` que NO existe cuando se incluyen gastos operacionales

### 7. Tabla de Gastos por Mes en HTML

```python
# En HTMLExporter._generar_tabla_gastos_mensual:
for mes, datos in datos_por_mes.items():
    for maquina, valores in datos:
        gastos = valores['gastos']
        totales_por_mes[mes]['total'] += gastos.get('total', Decimal('0'))
```

**PROBLEMA IDENTIFICADO**:
- Mismo problema: se intenta acceder a `gastos.get('total', Decimal('0'))` que NO existe cuando se incluyen gastos operacionales

## Fallos de Cálculo Identificados

### Fallo 1: Inconsistencia en el cálculo de Producción Real

**Ubicación**: [`CalculadorProduccionReal.calcular_por_maquina_mes`](src/domain/services/CalculadorProduccionReal.py:98)

**Descripción**: 
- El cálculo de producción real usa `gastos['total']` de `CalculadorGastos.calcular_por_maquina_mes`, que solo incluye repuestos, costo_hh y leasing.
- NO incluye los gastos operacionales (combustibles, reparaciones, seguros, etc.)
- Esto causa que la producción real esté sobreestimada positivamente porque se están restando menos gastos de los que realmente se incurrieron.

**Impacto**: 
- La producción real mostrada no refleja la realidad financiera del negocio
- Los gastos operacionales (combustibles, reparaciones, seguros, etc.) no se están considerando en el cálculo de la producción real

**Corrección Necesaria**:
- Modificar `CalculadorProduccionReal.calcular_por_maquina_mes` para usar `CalculadorGastos.calcular_por_maquina_mes_completo` cuando se proporcionan gastos operacionales
- O alternativamente, calcular la producción real usando el `total_gastos_completo` calculado en el HTMLExporter

### Fallo 2: Acceso a clave inexistente en diccionario de gastos

**Ubicación**: [`HTMLExporter._generar_filas_resumen`](src/infrastructure/export/HTMLExporter.py:722), [`HTMLExporter._generar_filas_gastos`](src/infrastructure/export/HTMLExporter.py:812)

**Descripción**:
- Cuando `incluir_gastos_operacionales=True`, el diccionario `gastos` NO tiene la clave `'total'`
- Tiene una clave `'total_gastos_operacionales'` que representa solo los gastos operacionales
- El código intenta acceder a `gastos['total']` que no existe

**Impacto**:
- Error de ejecución al generar las tablas de resumen y gastos por mes
- El HTML no se genera correctamente

**Corrección Necesaria**:
- Modificar los métodos `_generar_filas_resumen` y `_generar_filas_gastos` para usar la clave correcta según el contexto
- Cuando `incluir_gastos_operacionales=True`, usar `'total_gastos_operacionales'` en lugar de `'total'`
- Cuando `incluir_gastos_operacionales=False`, usar `'total'` que incluye repuestos + costo_hh + leasing

### Fallo 3: Falta de tarjeta "Total Producción (MT3)" en HTML

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
- Mostrar el total de MT3 y total de horas trabajadas

### Fallo 4: Total Horas Trabajadas siempre muestra 0

**Ubicación**: [`HTMLExporter._generar_html_estatico`](src/infrastructure/export/HTMLExporter.py:298)

**Descripción**:
- El HTML generado siempre muestra `total_horas=Decimal('0')` en la tarjeta de resumen
- Esto es porque en `_generar_html_completo` se establece explícitamente `total_horas=Decimal('0')`

**Impacto**:
- El usuario no puede ver el total de horas trabajadas
- Falta información importante para el análisis

**Corrección Necesaria**:
- Calcular correctamente el total de horas trabajadas sumando `valores['produccion']['horas_trabajadas']`
- En `_generar_html_completo`, cambiar `total_horas=Decimal('0') por el cálculo real

## Recomendaciones de Corrección

### Prioridad 1: Corregir el cálculo de Producción Real

1. Modificar `CalculadorProduccionReal.calcular_por_maquina_mes` para aceptar un parámetro opcional `gastos_completos` que incluya todos los gastos (repuestos, costo_hh, leasing, gastos operacionales)
2. Cuando se proporcionan `gastos_completos`, usar estos datos para calcular la producción real
3. Cuando no se proporcionan `gastos_completos`, usar `CalculadorGastos.calcular_por_maquina_mes` como antes

### Prioridad 2: Corregir el acceso a claves inexistentes en gastos

1. Modificar `_generar_filas_resumen` y `_generar_filas_gastos` en `HTMLExporter` para:
   - Detectar si `incluir_gastos_operacionales=True`
   - Si es True, usar `'total_gastos_operacionales'` en lugar de `'total'`
   - Si es False, usar `'total'` que incluye repuestos + costo_hh + leasing

### Prioridad 3: Agregar tarjeta de Producción Física

1. Agregar la tarjeta "Total Producción (MT3)" al HTML generado
2. Calcular `total_mt3` y `total_horas` correctamente
3. Mostrar estos valores en la tarjeta de resumen

## Conclusión

El sistema de cálculo tiene múltiples problemas de consistencia:

1. **Inconsistencia en el cálculo de Producción Real**: Se usan gastos incompletos para calcular la producción real
2. **Error de acceso a claves**: Se intenta acceder a claves que no existen en el diccionario de gastos
3. **Falta de información**: No se muestra el total de producción en MT3 ni el total de horas trabajadas

Estos problemas deben ser corregidos para que el informe refleje la realidad financiera del negocio.


#Se actualizó la lista de tareas pendientes
Implementar corrección en CalculadorProduccionReal.calcular_por_maquina_mes para aceptar gastos_completos
Implementar corrección en CalculadorProduccionReal.calcular_total_por_maquina para aceptar gastos_completos
Implementar corrección en HTMLExporter._generar_html_completo para usar total_gastos_completo
Implementar corrección en HTMLExporter._generar_filas_resumen para usar la clave correcta según el contexto
Implementar corrección en HTMLExporter._generar_filas_gastos para usar la clave correcta según el contexto
Implementar corrección en HTMLExporter._generar_tabla_gastos_mensual para usar la clave correcta según el contexto
Agregar tarjeta "Total Producción (MT3)" al HTML generado
Calcular correctamente total_horas en HTMLExporter._generar_html_estatico
Calcular correctamente total_mt3 en HTMLExporter._generar_html_estatico
Actualizar InformeService para pasar gastos_completos a HTMLExporter cuando se proporcionan
Actualizar HTMLExporter para aceptar el parámetro gastos_completos opcional
Ejecutar el proyecto y verificar que todos los cálculos son correctos
Documentar las correcciones implementadas