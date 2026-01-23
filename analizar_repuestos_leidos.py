from src.infrastructure.csv.RepuestosCSVReader import RepuestosCSVReader

# Leer datos de repuestos
reader = RepuestosCSVReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos\DATABODEGA.csv')
repuestos = reader.leer()

print(f'Total de repuestos leídos (Q4 2025): {len(repuestos)}')

# Contar por máquina
maquinas = {}
for rep in repuestos:
    if rep.codigo_maquina not in maquinas:
        maquinas[rep.codigo_maquina] = {'count': 0, 'total': rep.total}
    else:
        maquinas[rep.codigo_maquina]['count'] += 1
        maquinas[rep.codigo_maquina]['total'] += rep.total

print(f'\nMáquinas únicas con repuestos: {len(maquinas)}')
print('\nTOP 10 MÁQUINAS POR MONTO TOTAL:')
sorted_maquinas = sorted(maquinas.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
for maquina, data in sorted_maquinas:
    print(f'  {maquina:40} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# Calcular total general
total_general = sum(rep.total for rep in repuestos)
print(f'\nTOTAL GENERAL DE REPUESTOS (Q4 2025): ${total_general:,.0f}')

# Mostrar distribución por mes
from collections import defaultdict
por_mes = defaultdict(lambda: {'count': 0, 'total': 0})
for rep in repuestos:
    mes = rep.fecha_salida.month
    por_mes[mes]['count'] += 1
    por_mes[mes]['total'] += rep.total

print('\n=== DISTRIBUCIÓN POR MES ===')
meses = {10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}
for mes in sorted(por_mes.keys()):
    print(f'  {meses[mes]}: {por_mes[mes]["count"]:5} registros | ${por_mes[mes]["total"]:,.0f}')
