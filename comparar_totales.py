"""
Script para comparar los totales que deberían capturarse vs lo que se captura
"""

from src.infrastructure.csv.ProduccionCSVReader import ProduccionCSVReader
from src.infrastructure.csv.RepuestosCSVReader import RepuestosCSVReader
from src.infrastructure.csv.HorasHombreCSVReader import HorasHombreCSVReader
from src.domain.services.CalculadorProduccion import CalculadorProduccion
from src.domain.services.CalculadorGastos import CalculadorGastos
from src.domain.services.ValorUFService import ValorUFService
from decimal import Decimal

print("=" * 80)
print("COMPARACIÓN DE TOTALES: ESPERADO vs CAPTURADO")
print("=" * 80)

# Obtener valor UF
uf_service = ValorUFService()
valor_uf = uf_service.obtener_valor_uf()

print(f"\nValor UF: ${valor_uf:,.0f} CLP\n")

# Leer datos
print("Leyendo datos de producción...")
produccion_reader = ProduccionCSVReader(
    'Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv',
    valor_uf=valor_uf
)
producciones = produccion_reader.leer()

print("Leyendo datos de repuestos...")
repuestos_reader = RepuestosCSVReader('DATABODEGA.csv')
repuestos = repuestos_reader.leer()

print("Leyendo datos de horas hombre...")
hh_reader = HorasHombreCSVReader('_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv')
horas_hombre = hh_reader.leer()

print(f"\nRegistros leídos:")
print(f"  Producciones: {len(producciones):,}")
print(f"  Repuestos: {len(repuestos):,}")
print(f"  Horas Hombre: {len(horas_hombre):,}")

# Calcular producción
prod_por_mes = CalculadorProduccion.calcular_por_maquina_mes(producciones)

# Calcular gastos
gastos_por_mes = CalculadorGastos.calcular_por_maquina_mes(repuestos, horas_hombre)

# Sumar totales
total_produccion_neta = Decimal('0')
total_gastos = Decimal('0')

for clave, datos in prod_por_mes.items():
    mes = clave[1]
    if mes in [10, 11, 12]:
        total_produccion_neta += datos.get('valor_monetario', Decimal('0'))

for clave, datos in gastos_por_mes.items():
    mes = clave[1]
    if mes in [10, 11, 12]:
        total_gastos += datos.get('total', Decimal('0'))

print("\n" + "=" * 80)
print("TOTALES CAPTURADOS POR EL SISTEMA (Oct/Nov/Dic 2025)")
print("=" * 80)
print(f"Producción Neta Total: ${total_produccion_neta:,.0f}")
print(f"Gastos Totales: ${total_gastos:,.0f}")
print(f"Producción Real: ${total_produccion_neta - total_gastos:,.0f}")

# Desglose por mes
print("\n" + "=" * 80)
print("DESGLOSE POR MES")
print("=" * 80)

for mes in [10, 11, 12]:
    nombre_mes = {10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'}[mes]
    
    prod_mes = Decimal('0')
    gastos_mes = Decimal('0')
    
    for clave, datos in prod_por_mes.items():
        if clave[1] == mes:
            prod_mes += datos.get('valor_monetario', Decimal('0'))
    
    for clave, datos in gastos_por_mes.items():
        if clave[1] == mes:
            gastos_mes += datos.get('total', Decimal('0'))
    
    prod_real_mes = prod_mes - gastos_mes
    
    print(f"\n{nombre_mes}:")
    print(f"  Producción Neta: ${prod_mes:,.0f}")
    print(f"  Gastos: ${gastos_mes:,.0f}")
    print(f"  Producción Real: ${prod_real_mes:,.0f}")

# Desglose de gastos
print("\n" + "=" * 80)
print("DESGLOSE DE GASTOS")
print("=" * 80)

total_repuestos = Decimal('0')
total_hh = Decimal('0')
total_costo_hh = Decimal('0')

for clave, datos in gastos_por_mes.items():
    mes = clave[1]
    if mes in [10, 11, 12]:
        total_repuestos += datos.get('repuestos', Decimal('0'))
        total_hh += datos.get('horas_hombre', Decimal('0'))
        total_costo_hh += datos.get('costo_hh', Decimal('0'))

print(f"Repuestos: ${total_repuestos:,.0f}")
print(f"Horas Hombre (HH): {total_hh:.2f} horas")
print(f"Costo HH (HH × $35,000): ${total_costo_hh:,.0f}")
print(f"Total Gastos: ${total_gastos:,.0f}")

# Comparar con valores esperados del diagnóstico
print("\n" + "=" * 80)
print("COMPARACIÓN CON DIAGNÓSTICO")
print("=" * 80)
print("\nSegún el diagnóstico de producción:")
print("  Total esperado (Oct/Nov/Dic): $1,238,581,160")
print(f"  Total capturado: ${total_produccion_neta:,.0f}")
diferencia_prod = Decimal('1238581160') - total_produccion_neta
print(f"  Diferencia: ${diferencia_prod:,.0f} ({diferencia_prod/Decimal('1238581160')*100:.2f}%)")

print("\nSegún el diagnóstico de bodega:")
print("  Total esperado (Oct/Nov/Dic): $218,904,568")
print("  Total con máquina válida: $171,189,015")
print(f"  Total capturado: ${total_repuestos:,.0f}")
diferencia_rep = Decimal('171189015') - total_repuestos
print(f"  Diferencia: ${diferencia_rep:,.0f} ({diferencia_rep/Decimal('171189015')*100:.2f}%)")

print("\n" + "=" * 80)
print("ANÁLISIS COMPLETADO")
print("=" * 80)
