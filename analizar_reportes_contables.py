"""
Script para analizar CORRECTAMENTE los archivos CSV de reportes contables.

Estos archivos contienen información que NO está en DATABODEGA.csv:
- COMBUSTIBLES (401010101)
- REPUESTOS Y ACCESORIOS (401010102)
- REPARACIONES Y MANTENCION (401010103)
- ELEMENTOS DE PROTECCION PERSONAL (401010104)
- SERVICIO TRANSPORTES (401010106)
- HONORARIOS (401010109)
- POLIZA DE SEGURO (401010115)
- OTROS GASTOS (401030107)
- INGRESOS (301010101, 301010104)
"""

import csv
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from collections import defaultdict
import re

CARPETA_GASTOS = Path("gastos")
CARPETA_ANALISIS = Path("analisis_gastos")
CARPETA_ANALISIS.mkdir(exist_ok=True)

# Mapeo de meses en español
MESES_MAP = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
    'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
    'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}


def normalizar_codigo_maquina(texto: str) -> str:
    """Extrae código de máquina del texto.
    
    Formatos soportados:
    - [BA-01 BARREDORA LAYMOR] → BA-01
    - 2020100001 CT-06 CAMIÓN FREIGHTLINER → CT-06
    - EX-09 EXCAVADORA KOMATSU → EX-09
    """
    if not texto:
        return ""
    
    texto_upper = texto.upper()
    
    # Mapeo de centros de costo conocidos sin código estándar en el nombre
    MAPEO_CENTROS_COSTO = {
        'TRACTOR CASE PUMA 155': 'T-06',
        'TRACTOR CASE PUMA': 'T-06',
        '2010800003': 'T-06',
        'CAMIONETA RAPTOR VGKX-71': 'C-53',
        'RAPTOR VGKX-71': 'C-53',
        'VGKX-71': 'C-53',
        '3010100017': 'C-53',
        'CAMIONETA JMC RWRH-49': 'C-29',
        'RWRH-49': 'C-29',
        '3010100015': 'C-29',
        'CAMIONETA JMC RXKR-45': 'C-30',  # Otro JMC sin código
        'RXKR-45': 'C-30',
        '3010100014': 'C-30',
        'CAMIONETA JMC VIGUS RWRH-53': 'C-31',  # JMC Vigus
        'RWRH-53': 'C-31',
        '2030100048': 'C-31',
        'TRACTOR CASE GWSV65': 'T-05',  # Otro tractor
        'GWSV65': 'T-05',
        '2010800001': 'T-05',
    }
    
    # Primero buscar en el mapeo de centros conocidos
    for patron, codigo in MAPEO_CENTROS_COSTO.items():
        if patron.upper() in texto_upper:
            return codigo
    
    # Buscar patrón [XX-NN ...] primero (formato con corchetes)
    match = re.search(r'\[([A-Za-z]+-\d+)', texto_upper)
    if match:
        return match.group(1).upper()
    
    # Buscar códigos específicos de maquinaria: CT-XX, EX-XX, CF-XX, RX-XX, etc.
    # Patrones conocidos: BA, BD, C, CF, CG, CK, CM, CP, CT, EX, GR, MA, MC, MN, RD, RX, T, TC
    patrones_maquinaria = [
        r'\b(CT-\d+)\b',      # Camiones tolva
        r'\b(EX-\d+)\b',      # Excavadoras
        r'\b(CF-\d+)\b',      # Cargadores frontales
        r'\b(RX-\d+)\b',      # Retroexcavadoras
        r'\b(MN-\d+)\b',      # Motoniveladoras
        r'\b(RD-\d+)\b',      # Rodillos
        r'\b(BD-\d+)\b',      # Bulldozers
        r'\b(GR-\d+)\b',      # Grúas
        r'\b(TC-\d+)\b',      # Tracto camiones
        r'\b(BA-\d+)\b',      # Barredoras
        r'\b(MA-\d+)\b',      # Maquinaria asfáltica
        r'\b(CG-\d+)\b',      # Camiones ganaderos
        r'\b(CM-\d+)\b',      # Camiones mixer
        r'\b(CP-\d+)\b',      # Camiones pluma
        r'\b(CK-\d+)\b',      # Camiones varios
        r'\b(MC-\d+)\b',      # Minicargadores
        r'\b(T-\d+)\b',       # Tractores (diferente a TC tracto camiones)
        r'\b(C-\d+)\b',       # Vehículos livianos (al final porque es más genérico)
    ]
    
    for patron in patrones_maquinaria:
        match = re.search(patron, texto, re.IGNORECASE)
        if match:
            return match.group(1).upper()
    
    # Buscar cualquier patrón XX-NN (2-3 letras, guion, 1-2 números)
    match = re.search(r'\b([A-Za-z]{1,3}-\d{1,2})\b', texto)
    if match:
        return match.group(1).upper()
    
    # Buscar patrón con espacio en lugar de guion: "EX 16", "CT 06"
    match = re.search(r'\b([A-Za-z]{2})\s+(\d{1,2})\b', texto)
    if match:
        return f"{match.group(1).upper()}-{match.group(2)}"
    
    return ""


def parsear_monto(monto_str: str) -> Decimal:
    """Parsea monto con formato chileno."""
    if not monto_str or monto_str.strip() == '':
        return Decimal('0')
    
    try:
        # Limpiar el string
        monto_str = monto_str.strip().replace(' ', '')
        
        # Remover puntos de miles y convertir coma decimal
        if '.' in monto_str and ',' not in monto_str:
            # Puede ser separador de miles
            monto_str = monto_str.replace('.', '')
        elif ',' in monto_str:
            monto_str = monto_str.replace('.', '').replace(',', '.')
        
        return Decimal(monto_str)
    except:
        return Decimal('0')


def leer_reporte_contable(ruta_archivo: Path) -> dict:
    """Lee un archivo CSV de reporte contable y extrae toda la información."""
    
    resultado = {
        'archivo': ruta_archivo.name,
        'centros_costo': [],
        'cuentas': defaultdict(list),
        'totales_por_cuenta': defaultdict(lambda: {'perdida': Decimal('0'), 'ganancia': Decimal('0')}),
        'totales_por_maquina': defaultdict(lambda: {'perdida': Decimal('0'), 'ganancia': Decimal('0')}),
        'registros': []
    }
    
    try:
        with open(ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            lineas = archivo.readlines()
        
        centro_costo_actual = ""
        codigo_maquina_actual = ""
        cuenta_actual = ""
        codigo_cuenta_actual = ""
        
        for linea in lineas:
            campos = linea.split(';')
            
            # Detectar línea de Centro de Costo
            if campos and 'C.Costo' in campos[0]:
                # Extraer el valor después de C.Costo (en la columna 5 aproximadamente)
                for campo in campos[1:]:
                    if campo.strip():
                        centro_costo_actual = campo.strip()
                        codigo_maquina_actual = normalizar_codigo_maquina(centro_costo_actual)
                        if centro_costo_actual and centro_costo_actual not in resultado['centros_costo']:
                            resultado['centros_costo'].append(centro_costo_actual)
                        break
                continue
            
            # Detectar línea de Cuenta
            if campos and 'Cuenta' in campos[0]:
                for campo in campos[1:]:
                    if campo.strip():
                        cuenta_actual = campo.strip()
                        # Extraer código de cuenta (ej: 401010101)
                        match = re.match(r'(\d+)', cuenta_actual)
                        if match:
                            codigo_cuenta_actual = match.group(1)
                        break
                continue
            
            # Detectar línea de datos (tiene Día y Mes)
            if len(campos) > 5:
                dia_str = campos[0].strip()
                mes_str = ""
                
                # Buscar el mes en los campos
                for i, campo in enumerate(campos[1:8], 1):
                    if campo.strip().lower() in MESES_MAP:
                        mes_str = campo.strip().lower()
                        break
                
                # Si encontramos día y mes válidos
                if dia_str.isdigit() and mes_str in MESES_MAP:
                    dia = int(dia_str)
                    mes = MESES_MAP[mes_str]
                    
                    try:
                        fecha = datetime(2025, mes, dia).date()
                    except:
                        continue
                    
                    # Extraer glosa (descripción) - generalmente alrededor de la posición 10
                    glosa = ""
                    for campo in campos[9:14]:
                        if campo.strip() and not campo.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
                            glosa = campo.strip()
                            break
                    
                    # Extraer Perdida y Ganancia
                    # Los montos suelen estar alrededor de las posiciones 13-17
                    perdida = Decimal('0')
                    ganancia = Decimal('0')
                    
                    # Buscar valores numéricos en los campos
                    for i, campo in enumerate(campos[10:]):
                        monto = parsear_monto(campo)
                        if monto > 0:
                            # Si es la primera cantidad encontrada, probablemente es perdida
                            # Si es la segunda, probablemente es ganancia
                            if perdida == 0:
                                perdida = monto
                            elif ganancia == 0:
                                ganancia = monto
                                break
                    
                    # Registrar el movimiento
                    registro = {
                        'fecha': fecha,
                        'centro_costo': centro_costo_actual,
                        'codigo_maquina': codigo_maquina_actual,
                        'cuenta': cuenta_actual,
                        'codigo_cuenta': codigo_cuenta_actual,
                        'glosa': glosa,
                        'perdida': perdida,
                        'ganancia': ganancia
                    }
                    
                    resultado['registros'].append(registro)
                    resultado['cuentas'][codigo_cuenta_actual].append(registro)
                    resultado['totales_por_cuenta'][codigo_cuenta_actual]['perdida'] += perdida
                    resultado['totales_por_cuenta'][codigo_cuenta_actual]['ganancia'] += ganancia
                    resultado['totales_por_maquina'][codigo_maquina_actual or centro_costo_actual]['perdida'] += perdida
                    resultado['totales_por_maquina'][codigo_maquina_actual or centro_costo_actual]['ganancia'] += ganancia
        
        return resultado
    
    except Exception as e:
        print(f"  [ERROR] Error leyendo {ruta_archivo.name}: {e}")
        import traceback
        traceback.print_exc()
        return resultado


def analizar_todos_los_archivos():
    """Analiza todos los archivos CSV de reportes contables."""
    
    print("=" * 70)
    print("ANÁLISIS DE ARCHIVOS CSV DE REPORTES CONTABLES")
    print("=" * 70)
    print()
    
    # Archivos a excluir (no son reportes contables)
    archivos_excluidos = {
        'DATABODEGA.csv',
        '_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv',
        'Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv',
        'Leasing Credito HMAQ.csv'
    }
    
    # Encontrar archivos CSV
    archivos_csv = [f for f in CARPETA_GASTOS.glob("*.csv") if f.name not in archivos_excluidos]
    
    # Estructura para consolidar resultados
    consolidado = {
        'por_cuenta': defaultdict(lambda: {'perdida': Decimal('0'), 'ganancia': Decimal('0'), 'archivos': set()}),
        'por_maquina': defaultdict(lambda: {'perdida': Decimal('0'), 'ganancia': Decimal('0')}),
        'por_archivo': {},
        'todos_registros': []
    }
    
    # Mapeo de códigos de cuenta a nombres
    CUENTAS_NOMBRES = {
        '301010101': 'INGRESOS ARRIENDO MAQUINARIA',
        '301010104': 'INGRESOS SERVICIOS TRANSPORTES',
        '401010101': 'COMBUSTIBLES',
        '401010102': 'REPUESTOS Y ACCESORIOS',
        '401010103': 'REPARACIONES Y MANTENCION',
        '401010104': 'ELEMENTOS DE PROTECCION PERSONAL',
        '401010106': 'SERVICIO TRANSPORTES',
        '401010109': 'HONORARIOS',
        '401010115': 'POLIZA DE SEGURO',
        '401030107': 'OTROS GASTOS'
    }
    
    for ruta_archivo in sorted(archivos_csv):
        print(f"\nProcesando: {ruta_archivo.name}")
        resultado = leer_reporte_contable(ruta_archivo)
        
        n_registros = len(resultado['registros'])
        print(f"  - Registros encontrados: {n_registros}")
        
        if n_registros > 0:
            consolidado['por_archivo'][ruta_archivo.name] = resultado
            consolidado['todos_registros'].extend(resultado['registros'])
            
            # Consolidar por cuenta
            for codigo, totales in resultado['totales_por_cuenta'].items():
                consolidado['por_cuenta'][codigo]['perdida'] += totales['perdida']
                consolidado['por_cuenta'][codigo]['ganancia'] += totales['ganancia']
                consolidado['por_cuenta'][codigo]['archivos'].add(ruta_archivo.name)
            
            # Consolidar por máquina
            for maquina, totales in resultado['totales_por_maquina'].items():
                consolidado['por_maquina'][maquina]['perdida'] += totales['perdida']
                consolidado['por_maquina'][maquina]['ganancia'] += totales['ganancia']
            
            # Mostrar cuentas encontradas
            for codigo, totales in resultado['totales_por_cuenta'].items():
                nombre_cuenta = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
                print(f"    - {nombre_cuenta}: Gastos ${totales['perdida']:,.0f} / Ingresos ${totales['ganancia']:,.0f}")
    
    # Generar resumen consolidado
    print("\n" + "=" * 70)
    print("RESUMEN CONSOLIDADO POR TIPO DE CUENTA")
    print("=" * 70)
    
    total_gastos = Decimal('0')
    total_ingresos = Decimal('0')
    
    for codigo in sorted(consolidado['por_cuenta'].keys()):
        totales = consolidado['por_cuenta'][codigo]
        nombre_cuenta = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
        
        if totales['perdida'] > 0 or totales['ganancia'] > 0:
            print(f"\n{nombre_cuenta} ({codigo}):")
            if totales['perdida'] > 0:
                print(f"  GASTOS: ${totales['perdida']:,.0f}")
                total_gastos += totales['perdida']
            if totales['ganancia'] > 0:
                print(f"  INGRESOS: ${totales['ganancia']:,.0f}")
                total_ingresos += totales['ganancia']
    
    print("\n" + "=" * 70)
    print("TOTALES GENERALES")
    print("=" * 70)
    print(f"  TOTAL GASTOS: ${total_gastos:,.0f}")
    print(f"  TOTAL INGRESOS: ${total_ingresos:,.0f}")
    print(f"  RESULTADO NETO: ${total_ingresos - total_gastos:,.0f}")
    
    # Desglose de gastos
    print("\n" + "=" * 70)
    print("DESGLOSE DE GASTOS POR CATEGORIA (Q4 2025)")
    print("=" * 70)
    
    # Categorías específicas
    combustibles = consolidado['por_cuenta'].get('401010101', {}).get('perdida', Decimal('0'))
    repuestos = consolidado['por_cuenta'].get('401010102', {}).get('perdida', Decimal('0'))
    reparaciones = consolidado['por_cuenta'].get('401010103', {}).get('perdida', Decimal('0'))
    epp = consolidado['por_cuenta'].get('401010104', {}).get('perdida', Decimal('0'))
    transporte = consolidado['por_cuenta'].get('401010106', {}).get('perdida', Decimal('0'))
    honorarios = consolidado['por_cuenta'].get('401010109', {}).get('perdida', Decimal('0'))
    seguros = consolidado['por_cuenta'].get('401010115', {}).get('perdida', Decimal('0'))
    otros = consolidado['por_cuenta'].get('401030107', {}).get('perdida', Decimal('0'))
    
    # Cuentas adicionales importantes
    cuenta_108 = consolidado['por_cuenta'].get('401010108', {}).get('perdida', Decimal('0'))
    cuenta_119 = consolidado['por_cuenta'].get('401010119', {}).get('perdida', Decimal('0'))
    
    print(f"  [COMB] COMBUSTIBLES:       ${combustibles:>15,.0f}")
    print(f"  [REPU] REPUESTOS:          ${repuestos:>15,.0f}")
    print(f"  [REPA] REPARACIONES:       ${reparaciones:>15,.0f}")
    print(f"  [EPP]  PROTECCION PERS:    ${epp:>15,.0f}")
    print(f"  [TRAN] TRANSPORTE:         ${transporte:>15,.0f}")
    print(f"  [HONO] HONORARIOS:         ${honorarios:>15,.0f}")
    print(f"  [SEGU] SEGUROS:            ${seguros:>15,.0f}")
    print(f"  [OTRO] OTROS:              ${otros:>15,.0f}")
    print(f"  [108]  CUENTA 401010108:   ${cuenta_108:>15,.0f}")
    print(f"  [119]  CUENTA 401010119:   ${cuenta_119:>15,.0f}")
    print(f"  {'-' * 40}")
    print(f"  [TOT]  TOTAL GASTOS:       ${total_gastos:>15,.0f}")
    
    print("\n" + "=" * 70)
    print("DESGLOSE DE INGRESOS POR CATEGORIA (Q4 2025)")
    print("=" * 70)
    
    ingresos_arriendo = consolidado['por_cuenta'].get('301010101', {}).get('ganancia', Decimal('0'))
    ingresos_transporte = consolidado['por_cuenta'].get('301010104', {}).get('ganancia', Decimal('0'))
    ingresos_otros = total_ingresos - ingresos_arriendo - ingresos_transporte
    
    print(f"  [ARR]  ARRIENDO MAQUINARIA: ${ingresos_arriendo:>15,.0f}")
    print(f"  [SVC]  SERVICIOS TRANSPORTE:${ingresos_transporte:>15,.0f}")
    print(f"  [OTR]  OTROS INGRESOS:      ${ingresos_otros:>15,.0f}")
    print(f"  {'-' * 40}")
    print(f"  [TOT]  TOTAL INGRESOS:      ${total_ingresos:>15,.0f}")
    
    # Guardar reporte detallado
    guardar_reportes(consolidado, CUENTAS_NOMBRES)
    
    return consolidado


def guardar_reportes(consolidado, CUENTAS_NOMBRES):
    """Guarda reportes detallados en archivos CSV."""
    
    print("\n" + "=" * 70)
    print("GUARDANDO REPORTES")
    print("=" * 70)
    
    # 1. Reporte por tipo de cuenta
    ruta_cuentas = CARPETA_ANALISIS / "reportes_por_cuenta.csv"
    with open(ruta_cuentas, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Código Cuenta', 'Nombre Cuenta', 'Total Gastos', 'Total Ingresos', 'Archivos'])
        
        for codigo in sorted(consolidado['por_cuenta'].keys()):
            totales = consolidado['por_cuenta'][codigo]
            nombre = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
            archivos = ', '.join(sorted(totales['archivos']))
            writer.writerow([
                codigo, 
                nombre, 
                f"${totales['perdida']:,.0f}", 
                f"${totales['ganancia']:,.0f}",
                archivos
            ])
    print(f"  - Guardado: {ruta_cuentas.name}")
    
    # 2. Reporte por máquina
    ruta_maquinas = CARPETA_ANALISIS / "reportes_por_maquina.csv"
    with open(ruta_maquinas, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Código/Centro', 'Total Gastos', 'Total Ingresos', 'Resultado'])
        
        for maquina in sorted(consolidado['por_maquina'].keys()):
            totales = consolidado['por_maquina'][maquina]
            resultado = totales['ganancia'] - totales['perdida']
            writer.writerow([
                maquina,
                f"${totales['perdida']:,.0f}",
                f"${totales['ganancia']:,.0f}",
                f"${resultado:,.0f}"
            ])
    print(f"  - Guardado: {ruta_maquinas.name}")
    
    # 3. Reporte detallado de todos los movimientos
    ruta_detalle = CARPETA_ANALISIS / "reportes_detalle_movimientos.csv"
    with open(ruta_detalle, 'w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Fecha', 'Código Máquina', 'Centro Costo', 'Código Cuenta', 'Cuenta', 'Glosa', 'Gasto', 'Ingreso'])
        
        for reg in sorted(consolidado['todos_registros'], key=lambda x: (x['fecha'], x['codigo_maquina'])):
            writer.writerow([
                reg['fecha'].strftime('%d-%m-%Y'),
                reg['codigo_maquina'],
                reg['centro_costo'][:50],
                reg['codigo_cuenta'],
                CUENTAS_NOMBRES.get(reg['codigo_cuenta'], reg['cuenta'][:30]),
                reg['glosa'][:50],
                f"${reg['perdida']:,.0f}" if reg['perdida'] > 0 else "",
                f"${reg['ganancia']:,.0f}" if reg['ganancia'] > 0 else ""
            ])
    print(f"  - Guardado: {ruta_detalle.name}")
    
    # 4. Reporte de COMBUSTIBLES específico
    combustibles = [r for r in consolidado['todos_registros'] if r['codigo_cuenta'] == '401010101']
    if combustibles:
        ruta_combustibles = CARPETA_ANALISIS / "reportes_combustibles.csv"
        with open(ruta_combustibles, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['Fecha', 'Código Máquina', 'Centro Costo', 'Glosa', 'Monto'])
            
            for reg in sorted(combustibles, key=lambda x: (x['fecha'], x['codigo_maquina'])):
                writer.writerow([
                    reg['fecha'].strftime('%d-%m-%Y'),
                    reg['codigo_maquina'],
                    reg['centro_costo'][:50],
                    reg['glosa'],
                    f"${reg['perdida']:,.0f}"
                ])
        print(f"  - Guardado: {ruta_combustibles.name}")
    
    # 5. Resumen ejecutivo
    ruta_resumen = CARPETA_ANALISIS / "RESUMEN_REPORTES_CONTABLES.txt"
    with open(ruta_resumen, 'w', encoding='utf-8') as f:
        total_gastos = sum(v['perdida'] for v in consolidado['por_cuenta'].values())
        total_ingresos = sum(v['ganancia'] for v in consolidado['por_cuenta'].values())
        
        f.write("=" * 70 + "\n")
        f.write("RESUMEN EJECUTIVO - REPORTES CONTABLES Q4 2025\n")
        f.write("=" * 70 + "\n\n")
        
        f.write("GASTOS POR CATEGORÍA:\n")
        f.write("-" * 50 + "\n")
        for codigo in sorted(consolidado['por_cuenta'].keys()):
            totales = consolidado['por_cuenta'][codigo]
            if totales['perdida'] > 0:
                nombre = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
                f.write(f"  {nombre}: ${totales['perdida']:,.0f}\n")
        
        f.write(f"\n  TOTAL GASTOS: ${total_gastos:,.0f}\n")
        
        f.write("\n\nINGRESOS POR CATEGORÍA:\n")
        f.write("-" * 50 + "\n")
        for codigo in sorted(consolidado['por_cuenta'].keys()):
            totales = consolidado['por_cuenta'][codigo]
            if totales['ganancia'] > 0:
                nombre = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
                f.write(f"  {nombre}: ${totales['ganancia']:,.0f}\n")
        
        f.write(f"\n  TOTAL INGRESOS: ${total_ingresos:,.0f}\n")
        f.write(f"\n  RESULTADO NETO: ${total_ingresos - total_gastos:,.0f}\n")
        
        f.write("\n\n" + "=" * 70 + "\n")
        f.write("COMPARACIÓN CON DATABODEGA.CSV\n")
        f.write("=" * 70 + "\n\n")
        
        combustibles = consolidado['por_cuenta'].get('401010101', {}).get('perdida', Decimal('0'))
        reparaciones = consolidado['por_cuenta'].get('401010103', {}).get('perdida', Decimal('0'))
        honorarios = consolidado['por_cuenta'].get('401010109', {}).get('perdida', Decimal('0'))
        seguros = consolidado['por_cuenta'].get('401010115', {}).get('perdida', Decimal('0'))
        
        f.write("GASTOS NO CAPTURADOS EN DATABODEGA.CSV:\n")
        f.write(f"  - COMBUSTIBLES:   ${combustibles:,.0f}\n")
        f.write(f"  - REPARACIONES:   ${reparaciones:,.0f}\n")
        f.write(f"  - HONORARIOS:     ${honorarios:,.0f}\n")
        f.write(f"  - SEGUROS:        ${seguros:,.0f}\n")
        f.write(f"  - OTROS:\n")
        
        for codigo in sorted(consolidado['por_cuenta'].keys()):
            if codigo not in ['401010101', '401010102', '401010103', '401010104', '401010109', '401010115', '301010101', '301010104']:
                totales = consolidado['por_cuenta'][codigo]
                if totales['perdida'] > 0:
                    nombre = CUENTAS_NOMBRES.get(codigo, f"CUENTA {codigo}")
                    f.write(f"      - {nombre}: ${totales['perdida']:,.0f}\n")
        
        total_no_capturado = combustibles + reparaciones + honorarios + seguros
        f.write(f"\n  TOTAL NO CAPTURADO EN DATABODEGA: ${total_no_capturado:,.0f}\n")
        
        f.write("\n\nRECOMENDACIONES:\n")
        f.write("-" * 50 + "\n")
        if combustibles > 0:
            f.write(f"1. INTEGRAR COMBUSTIBLES (${combustibles:,.0f}) - Este es un costo operacional mayor\n")
        if total_ingresos > 0:
            f.write(f"2. USAR INGRESOS REALES (${total_ingresos:,.0f}) para comparar con gastos\n")
        f.write("3. Los reportes contables son la fuente más completa de información\n")
    
    print(f"  - Guardado: {ruta_resumen.name}")


if __name__ == "__main__":
    analizar_todos_los_archivos()
