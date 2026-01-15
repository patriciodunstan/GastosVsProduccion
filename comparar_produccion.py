"""
Comparativa de Producción: Harcha Maq App vs Construit

Este script compara los ingresos reportados desde dos fuentes:
1. Harcha Maq App: gastos/Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv
2. Construit: Ingresos en los CSV de reportes contables (barredora.csv, camiones.csv, etc.)
"""

import csv
import re
from pathlib import Path
from decimal import Decimal
from datetime import datetime
from collections import defaultdict


def normalizar_codigo_maquina(texto: str) -> str:
    """Extrae código de máquina del texto y lo normaliza."""
    if not texto:
        return ""
    
    texto = texto.upper()
    codigo = ""
    
    # Buscar patrón XX-NN al inicio del texto (formato Harcha App)
    match = re.search(r'^([A-Z]+-\d+)', texto)
    if match:
        codigo = match.group(1)
    else:
        # Buscar en cualquier parte
        match = re.search(r'\b([A-Z]{1,3}-\d{1,2})\b', texto)
        if match:
            codigo = match.group(1)
    
    if not codigo:
        return ""
    
    # Normalizar: asegurar que el número tenga 2 dígitos (XX-01, XX-02, etc.)
    match = re.match(r'([A-Z]+)-(\d+)', codigo)
    if match:
        prefijo = match.group(1)
        numero = int(match.group(2))
        # Solo agregar cero si el número es menor a 10 y el prefijo usa 2 dígitos típicamente
        if numero < 10:
            codigo = f"{prefijo}-{numero:02d}"
        else:
            codigo = f"{prefijo}-{numero}"
    
    return codigo


def leer_harcha_app(ruta: Path) -> dict:
    """Lee el archivo de Harcha Maq App y calcula ingresos por máquina."""
    
    ingresos_por_maquina = defaultdict(lambda: {
        'total': Decimal('0'),
        'registros': 0,
        'detalle_por_mes': defaultdict(Decimal),
        'tipos_unidad': set(),
        'clientes': set()
    })
    
    total_registros = 0
    registros_q4 = 0
    
    with open(ruta, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            total_registros += 1
            
            # Parsear fecha
            fecha_str = row.get('FECHA REPORTE', '')
            try:
                fecha = datetime.strptime(fecha_str, '%d/%m/%Y')
            except:
                continue
            
            # Filtrar Q4 2025 (Oct, Nov, Dic)
            if fecha.year != 2025 or fecha.month not in [10, 11, 12]:
                continue
            
            registros_q4 += 1
            
            # Extraer código de máquina
            maquina_full = row.get('MAQUINA_FULL', '')
            codigo = normalizar_codigo_maquina(maquina_full)
            
            if not codigo:
                codigo = "SIN_CODIGO"
            
            # Calcular ingreso (precio * unidades)
            try:
                precio = Decimal(row.get('vc_Precio_Unidades', '0') or '0')
                unidades = Decimal(row.get('vc_Unidades', '0') or '0')
                ingreso = precio * unidades
            except:
                ingreso = Decimal('0')
            
            # Acumular
            mes = fecha.strftime('%Y-%m')
            ingresos_por_maquina[codigo]['total'] += ingreso
            ingresos_por_maquina[codigo]['registros'] += 1
            ingresos_por_maquina[codigo]['detalle_por_mes'][mes] += ingreso
            ingresos_por_maquina[codigo]['tipos_unidad'].add(row.get('vc_Tipo_Unidad', ''))
            ingresos_por_maquina[codigo]['clientes'].add(row.get('CLIENTE_TXT', ''))
    
    print(f"  Harcha App: {total_registros} registros totales, {registros_q4} en Q4 2025")
    
    return dict(ingresos_por_maquina)


def leer_construit(carpeta: Path) -> dict:
    """Lee los CSV de reportes contables y extrae ingresos por máquina."""
    
    ingresos_por_maquina = defaultdict(lambda: {
        'total': Decimal('0'),
        'registros': 0,
        'detalle_por_cuenta': defaultdict(Decimal)
    })
    
    archivos_reporte = [
        'barredora.csv', 'bulldozer.csv', 'camiones.csv', 'cargadores.csv',
        'exc.csv', 'gruas.csv', 'maquinaria asfaltica.csv', 'motoniveladoras.csv',
        'retros.csv', 'rodillos.csv', 'taller.csv', 'tractores.csv',
        'vehiculos operaciones.csv', 'vehiculos.csv'
    ]
    
    # Mapeo de centros conocidos
    MAPEO_CENTROS = {
        'TRACTOR CASE PUMA 155': 'T-06',
        '2010800003': 'T-06',
        'CAMIONETA RAPTOR VGKX-71': 'C-53',
        'VGKX-71': 'C-53',
        '3010100017': 'C-53',
        'CAMIONETA JMC RWRH-49': 'C-29',
        'RWRH-49': 'C-29',
        '3010100015': 'C-29',
    }
    
    def extraer_codigo(texto):
        texto_upper = texto.upper()
        for patron, codigo in MAPEO_CENTROS.items():
            if patron.upper() in texto_upper:
                return codigo
        
        codigo = ""
        match = re.search(r'\[([A-Z]+-\d+)', texto_upper)
        if match:
            codigo = match.group(1)
        else:
            match = re.search(r'\b([A-Z]{1,3}-\d{1,2})\b', texto_upper)
            if match:
                codigo = match.group(1)
        
        if not codigo:
            return ""
        
        # Normalizar: XX-8 -> XX-08
        match = re.match(r'([A-Z]+)-(\d+)', codigo)
        if match:
            prefijo = match.group(1)
            numero = int(match.group(2))
            if numero < 10:
                return f"{prefijo}-{numero:02d}"
            return f"{prefijo}-{numero}"
        
        return codigo
    
    def parsear_monto(monto_str):
        if not monto_str:
            return Decimal('0')
        monto_str = monto_str.strip().replace(' ', '').replace('.', '').replace(',', '.')
        try:
            return Decimal(monto_str)
        except:
            return Decimal('0')
    
    total_registros = 0
    
    for archivo in archivos_reporte:
        ruta = carpeta / archivo
        if not ruta.exists():
            continue
        
        try:
            with open(ruta, 'r', encoding='utf-8-sig') as f:
                lineas = f.readlines()
            
            centro_costo_actual = ""
            codigo_actual = ""
            cuenta_actual = ""
            es_cuenta_ingreso = False
            
            for linea in lineas:
                campos = linea.split(';')
                
                # Detectar centro de costo
                if len(campos) > 0 and 'C.Costo' in campos[0]:
                    for campo in campos:
                        if campo.strip() and campo.strip() != 'C.Costo':
                            centro_costo_actual = campo.strip()
                            codigo_actual = extraer_codigo(centro_costo_actual)
                            break
                    continue
                
                # Detectar línea de cuenta
                if len(campos) > 0 and 'Cuenta' in campos[0]:
                    for campo in campos:
                        if campo.strip() and campo.strip() != 'Cuenta':
                            cuenta_actual = campo.strip()
                            # Las cuentas de ingresos empiezan con 301
                            es_cuenta_ingreso = cuenta_actual.startswith('301')
                            break
                    continue
                
                # Saltear líneas de encabezado
                if len(campos) > 0 and ('Dia' in campos[0] or 'Total' in campos[0] or not campos[0].strip()):
                    continue
                
                # Buscar líneas con datos de ingresos (cuentas 301xxx)
                if es_cuenta_ingreso and len(campos) >= 17:
                    # En líneas de detalle, la ganancia está en la columna 16
                    # Estructura: Dia;;;Mes;;Comp;;Tipo;TipoDoc;Docto;Glosa;;;;;;Ganancia;;;Saldo
                    try:
                        # Buscar el valor de ganancia - está después de varios campos vacíos
                        ganancia = Decimal('0')
                        for i in range(15, min(18, len(campos))):
                            valor = parsear_monto(campos[i])
                            if valor > 0:
                                ganancia = valor
                                break
                        
                        if ganancia > 0:
                            codigo = codigo_actual if codigo_actual else "SIN_CODIGO"
                            ingresos_por_maquina[codigo]['total'] += ganancia
                            ingresos_por_maquina[codigo]['registros'] += 1
                            total_registros += 1
                    except:
                        pass
        except Exception as e:
            print(f"  Error leyendo {archivo}: {e}")
    
    print(f"  Construit: {total_registros} registros de ingresos procesados")
    
    return dict(ingresos_por_maquina)


def generar_comparativa():
    """Genera la comparativa entre ambas fuentes."""
    
    print("=" * 70)
    print("COMPARATIVA DE PRODUCCIÓN: HARCHA MAQ APP vs CONSTRUIT")
    print("=" * 70)
    print()
    
    carpeta_gastos = Path("gastos")
    archivo_harcha = carpeta_gastos / "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv"
    
    print("Leyendo fuentes de datos...")
    
    # Leer ambas fuentes
    harcha_app = leer_harcha_app(archivo_harcha)
    construit = leer_construit(carpeta_gastos)
    
    print()
    print("=" * 70)
    print("TOTALES GENERALES Q4 2025")
    print("=" * 70)
    
    total_harcha = sum(d['total'] for d in harcha_app.values())
    total_construit = sum(d['total'] for d in construit.values())
    diferencia = total_harcha - total_construit
    
    print(f"  HARCHA MAQ APP:  ${total_harcha:>15,.0f}")
    print(f"  CONSTRUIT:       ${total_construit:>15,.0f}")
    print(f"  DIFERENCIA:      ${diferencia:>15,.0f} ({'+' if diferencia >= 0 else ''}{(diferencia/total_construit*100) if total_construit else 0:.1f}%)")
    
    # Obtener todas las máquinas
    todas_maquinas = set(harcha_app.keys()) | set(construit.keys())
    todas_maquinas.discard("SIN_CODIGO")
    
    # Crear comparativa por máquina
    comparativa = []
    
    for codigo in sorted(todas_maquinas):
        harcha_total = harcha_app.get(codigo, {}).get('total', Decimal('0'))
        construit_total = construit.get(codigo, {}).get('total', Decimal('0'))
        diferencia = harcha_total - construit_total
        
        if harcha_total > 0 or construit_total > 0:
            comparativa.append({
                'codigo': codigo,
                'harcha': harcha_total,
                'construit': construit_total,
                'diferencia': diferencia,
                'pct_diferencia': (diferencia / construit_total * 100) if construit_total else (100 if harcha_total else 0)
            })
    
    # Ordenar por diferencia absoluta
    comparativa.sort(key=lambda x: abs(x['diferencia']), reverse=True)
    
    print()
    print("=" * 70)
    print("COMPARATIVA POR MÁQUINA (TOP 30 MAYORES DIFERENCIAS)")
    print("=" * 70)
    print(f"{'Código':<10} {'Harcha App':>15} {'Construit':>15} {'Diferencia':>15} {'%':>8}")
    print("-" * 70)
    
    for item in comparativa[:30]:
        print(f"{item['codigo']:<10} ${item['harcha']:>14,.0f} ${item['construit']:>14,.0f} ${item['diferencia']:>14,.0f} {item['pct_diferencia']:>7.1f}%")
    
    # Máquinas solo en Harcha App
    solo_harcha = [c for c in harcha_app.keys() if c not in construit and c != "SIN_CODIGO"]
    solo_construit = [c for c in construit.keys() if c not in harcha_app and c != "SIN_CODIGO"]
    
    print()
    print("=" * 70)
    print("MÁQUINAS CON DATOS EN UNA SOLA FUENTE")
    print("=" * 70)
    
    if solo_harcha:
        print(f"\n  Solo en HARCHA APP ({len(solo_harcha)} máquinas):")
        for codigo in sorted(solo_harcha)[:15]:
            total = harcha_app[codigo]['total']
            print(f"    {codigo}: ${total:,.0f}")
    
    if solo_construit:
        print(f"\n  Solo en CONSTRUIT ({len(solo_construit)} máquinas):")
        for codigo in sorted(solo_construit)[:15]:
            total = construit[codigo]['total']
            print(f"    {codigo}: ${total:,.0f}")
    
    # Datos sin código
    print()
    print("=" * 70)
    print("INGRESOS SIN CÓDIGO DE MÁQUINA")
    print("=" * 70)
    
    sin_codigo_harcha = harcha_app.get("SIN_CODIGO", {}).get('total', Decimal('0'))
    sin_codigo_construit = construit.get("SIN_CODIGO", {}).get('total', Decimal('0'))
    
    print(f"  HARCHA APP:  ${sin_codigo_harcha:>15,.0f}")
    print(f"  CONSTRUIT:   ${sin_codigo_construit:>15,.0f}")
    
    # Guardar reporte CSV
    output_dir = Path("analisis_gastos")
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / "comparativa_produccion.csv", 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Código Máquina', 'Harcha App ($)', 'Construit ($)', 'Diferencia ($)', 'Diferencia (%)'])
        
        for item in comparativa:
            writer.writerow([
                item['codigo'],
                f"${item['harcha']:,.0f}",
                f"${item['construit']:,.0f}",
                f"${item['diferencia']:,.0f}",
                f"{item['pct_diferencia']:.1f}%"
            ])
        
        # Totales
        writer.writerow([])
        writer.writerow(['TOTAL', f"${total_harcha:,.0f}", f"${total_construit:,.0f}", f"${diferencia:,.0f}", ''])
        writer.writerow(['SIN CÓDIGO', f"${sin_codigo_harcha:,.0f}", f"${sin_codigo_construit:,.0f}", '', ''])
    
    print()
    print("=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)
    print(f"  - analisis_gastos/comparativa_produccion.csv")
    
    return comparativa, total_harcha, total_construit


if __name__ == "__main__":
    generar_comparativa()
