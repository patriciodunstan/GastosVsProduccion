import csv
from decimal import Decimal

# Leer DATABODEGA.csv
with open(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos\DATABODEGA.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f, delimiter=';')
    rows = list(reader)

print(f'Total de registros en DATABODEGA.csv: {len(rows)}')

# Contar por máquina
maquinas = {}
for row in rows:
    maquina = row.get('CODIGO MAQUINA', '').strip()
    if maquina:
        if maquina not in maquinas:
            maquinas[maquina] = {'count': 0, 'total': Decimal('0')}
        try:
            monto = Decimal(str(row.get('TOTAL', '0')).replace('.', '').replace(',', ''))
        except:
            monto = Decimal('0')
        maquinas[maquina]['count'] += 1
        maquinas[maquina]['total'] += monto

print(f'\nMáquinas únicas con repuestos: {len(maquinas)}')
print('\nTOP 10 MÁQUINAS POR MONTO TOTAL:')
sorted_maquinas = sorted(maquinas.items(), key=lambda x: x[1]['total'], reverse=True)[:10]
for maquina, data in sorted_maquinas:
    print(f'  {maquina:40} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# Calcular total general
total_general = sum(data['total'] for data in maquinas.values())
print(f'\nTOTAL GENERAL DE REPUESTOS: ${total_general:,.0f}')

# Verificar fechas
print('\n=== VERIFICACIÓN DE FECHAS ===')
fechas = {}
for row in rows:
    fecha_str = row.get('FECHA SALIDA', '').strip()
    if fecha_str:
        if fecha_str not in fechas:
            fechas[fecha_str] = 0
        fechas[fecha_str] += 1

print(f'Fechas únicas: {len(fechas)}')
sorted_fechas = sorted(fechas.items())[:10]
for fecha, count in sorted_fechas:
    print(f'  {fecha}: {count} registros')
