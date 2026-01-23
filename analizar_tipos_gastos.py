from src.infrastructure.csv.ReportesContablesReader import ReportesContablesReader

# Leer datos de gastos operacionales
reader = ReportesContablesReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos')
gastos = reader.leer_todos_filtrados()

print(f'Total de registros leídos: {len(gastos)}')

# Separar por tipo de cuenta (ingresos vs gastos)
ingresos = [g for g in gastos if g.tipo_gasto.startswith('3')]
gastos_reales = [g for g in gastos if g.tipo_gasto.startswith('4')]

print(f'\nRegistros de INGRESOS (cuentas 3xxx): {len(ingresos)}')
print(f'Registros de GASTOS (cuentas 4xxx): {len(gastos_reales)}')

# Ver qué códigos de gastos existen
codigos_gastos = {}
for g in gastos_reales:
    if g.tipo_gasto not in codigos_gastos:
        codigos_gastos[g.tipo_gasto] = {'count': 0, 'total': g.monto}
    else:
        codigos_gastos[g.tipo_gasto]['count'] += 1
        codigos_gastos[g.tipo_gasto]['total'] += g.monto

print(f'\n=== CÓDIGOS DE GASTOS (4xxx) ===')
for codigo, data in sorted(codigos_gastos.items(), key=lambda x: x[1]['total'], reverse=True):
    print(f'  {codigo:15} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# Ver qué códigos de ingresos existen
codigos_ingresos = {}
for g in ingresos:
    if g.tipo_gasto not in codigos_ingresos:
        codigos_ingresos[g.tipo_gasto] = {'count': 0, 'total': g.monto}
    else:
        codigos_ingresos[g.tipo_gasto]['count'] += 1
        codigos_ingresos[g.tipo_gasto]['total'] += g.monto

print(f'\n=== CÓDIGOS DE INGRESOS (3xxx) ===')
for codigo, data in sorted(codigos_ingresos.items(), key=lambda x: x[1]['total'], reverse=True):
    print(f'  {codigo:15} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# Calcular totales
total_ingresos = sum(g.monto for g in ingresos)
total_gastos = sum(g.monto for g in gastos_reales)
print(f'\nTOTAL INGRESOS: ${total_ingresos:,.0f}')
print(f'TOTAL GASTOS: ${total_gastos:,.0f}')
print(f'\nNETO (Gastos - Ingresos): ${total_gastos - total_ingresos:,.0f}')
