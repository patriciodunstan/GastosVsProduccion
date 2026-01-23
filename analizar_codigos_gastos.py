print('=== VERIFICACIÓN DE CÓDIGOS DE GASTOS ===')

# 1. Códigos en el enum TipoGasto
from src.domain.entities.GastoOperacional import TipoGasto

print('\n1. CÓDIGOS EN EL ENUM TipoGasto:')
for tipo in TipoGasto:
    print(f'   {tipo.name:25} | {tipo.value}')

# 2. Códigos reales en los gastos operacionales
from src.infrastructure.csv.ReportesContablesReader import ReportesContablesReader

reader = ReportesContablesReader(r'C:\Users\patricio dunstan sae\GastosVsProduccion\gastos')
gastos = reader.leer_todos_filtrados()

print('\n2. CÓDIGOS REALES EN LOS GASTOS OPERACIONALES (TOP 20):')
from collections import defaultdict

codigos_reales = defaultdict(lambda: {'count': 0, 'total': 0})
for g in gastos:
    if not g.es_ingreso and g.tipo_gasto.startswith('401'):
        codigos_reales[g.tipo_gasto]['count'] += 1
        codigos_reales[g.tipo_gasto]['total'] += g.monto

for codigo, data in sorted(codigos_reales.items(), key=lambda x: x[1]['total'], reverse=True)[:20]:
    print(f'   {codigo:15} | {data["count"]:4} registros | ${data["total"]:,.0f}')

# 3. Comparación
print('\n3. CÓDIGOS DEL ENUM QUE NO ESTÁN EN LOS GASTOS REALES:')
codigos_gastos_reales = set(codigos_reales.keys())
codigos_enum = set(tipo.value for tipo in TipoGasto)

codigos_no_encontrados = codigos_enum - codigos_gastos_reales
for codigo in sorted(codigos_no_encontrados):
    print(f'   {codigo}')

print('\n4. CÓDIGOS REALES QUE NO ESTÁN EN EL ENUM:')
codigos_no_en_enum = codigos_gastos_reales - codigos_enum
for codigo in sorted(codigos_no_en_enum)[:20]:
    nombre_tipo = TipoGasto.obtener_nombre(codigo)
    total = codigos_reales[codigo]['total']
    count = codigos_reales[codigo]['count']
    print(f'   {codigo:15} | {nombre_tipo:30} | {count:4} regs | ${total:,.0f}')

# 5. Impacto financiero
print('\n5. IMPACTO FINANCIERO DE LOS CÓDIGOS NO MAPEADOS:')
total_no_mapeado = sum(codigos_reales[c]['total'] for c in codigos_no_en_enum)
total_mapeado = sum(codigos_reales[c]['total'] for c in codigos_enum if c in codigos_reales)
print(f'   Total mapeado en enum:      ${total_mapeado:,.0f}')
print(f'   Total NO mapeado en enum:   ${total_no_mapeado:,.0f}')
print(f'   Porcentaje NO mapeado:      {total_no_mapeado / (total_mapeado + total_no_mapeado) * 100:.1f}%')
