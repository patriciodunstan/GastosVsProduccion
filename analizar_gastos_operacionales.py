from src.infrastructure.csv.ReportesContablesReader import ReportesContablesReader

# Leer datos de gastos operacionales
reader = ReportesContablesReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos')
gastos = reader.leer_todos_filtrados()

print(f'Total de gastos operacionales leídos (Q4 2025): {len(gastos)}')

# Contar por tipo
tipos = {}
for g in gastos:
    tipo = g.tipo_gasto
    if tipo not in tipos:
        tipos[tipo] = {'count': 0, 'total': g.monto}
    else:
        tipos[tipo]['count'] += 1
        tipos[tipo]['total'] += g.monto

print(f'\nTipos de gastos únicos: {len(tipos)}')
print('\n=== GASTOS POR TIPO ===')
for tipo, data in sorted(tipos.items(), key=lambda x: x[1]['total'], reverse=True):
    print(f'  {tipo:40} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# Calcular total general
total_general = sum(g.monto for g in gastos)
print(f'\nTOTAL GENERAL DE GASTOS OPERACIONALES (Q4 2025): ${total_general:,.0f}')

# Mostrar distribución por mes
from collections import defaultdict
por_mes = defaultdict(lambda: {'count': 0, 'total': 0})
meses = {10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
for g in gastos:
    mes = g.mes
    por_mes[mes]['count'] += 1
    por_mes[mes]['total'] += g.monto

print('\n=== DISTRIBUCIÓN POR MES ===')
for mes in sorted(por_mes.keys()):
    print(f'  {meses[mes]}: {por_mes[mes]["count"]:5} registros | ${por_mes[mes]["total"]:,.0f}')

# Contar por máquina
maquinas = {}
for g in gastos:
    if g.codigo_maquina not in maquinas:
        maquinas[g.codigo_maquina] = {'count': 0, 'total': g.monto}
    else:
        maquinas[g.codigo_maquina]['count'] += 1
        maquinas[g.codigo_maquina]['total'] += g.monto

print(f'\n=== MÁQUINAS CON GASTOS OPERACIONALES ===')
print(f'Total de máquinas: {len(maquinas)}')
print('\nTOP 10 MÁQUINAS POR MONTO TOTAL DE GASTOS:')
sorted_maquinas = sorted(maquinas.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
for maquina, data in sorted_maquinas:
    print(f'  {maquina:50} | {data["count"]:4} registros | ${data["total"]:,.0f}')
