from decimal import Decimal
from collections import defaultdict
from src.infrastructure.csv.ReportesContablesReader import ReportesContablesReader
from src.infrastructure.csv.RepuestosCSVReader import RepuestosCSVReader

print('=== VERIFICACIÓN DE DUPLICIDAD Y CÁLCULOS ===')

# 1. Verificar que no haya registros duplicados
print('\n1. VERIFICACIÓN DE REGISTROS DUPLICADOS')

# Repuestos
reader_rep = RepuestosCSVReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos\DATABODEGA.csv')
repuestos = reader_rep.leer()

# Buscar duplicados exactos (misma máquina, fecha, nombre, cantidad, total)
from collections import defaultdict

repuestos_keyed = defaultdict(list)
for rep in repuestos:
    key = (rep.codigo_maquina, rep.fecha_salida, rep.nombre, rep.cantidad, rep.total)
    repuestos_keyed[key].append(rep)

duplicados_repuestos = {k: v for k, v in repuestos_keyed.items() if len(v) > 1}

if duplicados_repuestos:
    print(f'   WARNING: {len(duplicados_repuestos)} grupos de repuestos duplicados encontrados')
    for key, reps in list(duplicados_repuestos.items())[:5]:
        print(f'      {key[0][:30]} | {key[1]} | {key[2][:30]} | {reps[0].total} x {len(reps)}')
else:
    print('   ✓ No se encontraron repuestos duplicados')

# Gastos operacionales
reader_gastos = ReportesContablesReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos')
gastos = reader_gastos.leer_todos_filtrados()

gastos_keyed = defaultdict(list)
for g in gastos:
    if not g.es_ingreso:
        key = (g.codigo_maquina, g.fecha, g.tipo_gasto, g.glosa, g.monto)
        gastos_keyed[key].append(g)

duplicados_gastos = {k: v for k, v in gastos_keyed.items() if len(v) > 1}

if duplicados_gastos:
    print(f'   WARNING: {len(duplicados_gastos)} grupos de gastos duplicados encontrados')
    for key, gs in list(duplicados_gastos.items())[:5]:
        print(f'      {key[0][:30]} | {key[1]} | {key[2]} | {key[3][:30]} | {gs[0].monto} x {len(gs)}')
else:
    print('   ✓ No se encontraron gastos duplicados')

# 2. Verificar cálculo por máquina
print('\n2. VERIFICACIÓN DE CÁLCULO POR MÁQUINA')

from src.domain.services.CalculadorGastos import CalculadorGastos

gastos_calculados = CalculadorGastos.calcular_por_maquina_mes_completo(
    repuestos, [], gastos, []
)

print('   Top 5 máquinas por gasto total:')
sorted_maquinas = sorted(
    gastos_calculados.items(),
    key=lambda x: x[1]['total'],
    reverse=True
)[:5]

for (maquina, mes), g in sorted_maquinas:
    print(f'      {maquina:40} ({mes}): ${g["total"]:,.0f}')

# 3. Verificar que el total por categoría coincida
print('\n3. VERIFICACIÓN DE TOTALES POR CATEGORÍA')

# Calcular total por categoría directamente desde los gastos
categorias_directo = defaultdict(lambda: Decimal('0'))
for g in gastos:
    if not g.es_ingreso and g.tipo_gasto.startswith('401'):
        categorias_directo[g.tipo_gasto] += g.monto

# Calcular total por categoría desde el calculador
categorias_calculador = defaultdict(Decimal)
for (maquina, mes), g in gastos_calculados.items():
    for cat in ['combustibles', 'reparaciones', 'seguros', 'honorarios', 
                'epp', 'peajes', 'remuneraciones', 'permisos', 'alimentacion',
                'pasajes', 'correspondencia', 'gastos_legales', 'multas', 'otros_gastos']:
        categorias_calculador[cat] += g[cat]

print('   Comparación totales por categoría (DIRECTO vs CALCULADOR):')
print('   ' + '-' * 80)

# Mapeo de categorias a códigos de cuenta
mapeo = {
    'combustibles': '401010101',
    'reparaciones': '401010102',
    'seguros': '401010115',
    'honorarios': '401010109',
    'epp': '401010104',
    'peajes': '401010105',
    'remuneraciones': '401010108',
    'permisos': '401010116',
    'alimentacion': '401010112',
    'pasajes': '401010111',
    'correspondencia': '401020107',
    'gastos_legales': '401020108',
    'multas': '401030102',
    'otros_gastos': '401030107'
}

diferencias = []
for cat, codigo in mapeo.items():
    total_directo = categorias_directo.get(codigo, Decimal('0'))
    total_calculador = categorias_calculador[cat]
    diferencia = total_directo - total_calculador
    
    if diferencia != 0:
        diferencias.append((cat, total_directo, total_calculador, diferencia))
        print(f'   {cat:20} | Directo: ${total_directo:15,.0f} | Calc: ${total_calculador:15,.0f} | Dif: ${diferencia:15,.0f} X')

if not diferencias:
    print('   ✓ Todas las categorias coinciden correctamente')
else:
    print(f'\n   ERROR: {len(diferencias)} categorias con diferencias encontradas')

# 4. Verificación de integridad total
print('\n4. VERIFICACIÓN DE INTEGRIDAD TOTAL')

# Total directo desde gastos
total_directo_gastos = sum(g.monto for g in gastos if not g.es_ingreso and g.tipo_gasto.startswith('401'))

# Total directo desde repuestos
total_directo_repuestos = sum(rep.total for rep in repuestos)

# Total desde calculador
total_calculador = sum(g['total'] for g in gastos_calculados.values())

print(f'   Total directo gastos (401xxx):        ${total_directo_gastos:,.0f}')
print(f'   Total directo repuestos:               ${total_directo_repuestos:,.0f}')
print(f'   Total calculador (gastos+repuestos):  ${total_calculador:,.0f}')

diferencia_total = (total_directo_gastos + total_directo_repuestos) - total_calculador
if diferencia_total == 0:
    print(f'\n   ✓ TOTAL CORRECTO: Los cálculos son consistentes')
else:
    print(f'\n   X ERROR: Diferencia de ${diferencia_total:,.0f} en el cálculo total')
