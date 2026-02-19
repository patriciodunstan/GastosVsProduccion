"""
Generador de Informe HTML de Auditoría de Precios.
"""

import pandas as pd
from datetime import datetime


def generar_informe_auditoria():
    """Genera un informe HTML detallado de la auditoría de precios."""

    # Cargar datos
    df = pd.read_excel('gastos/Harcha Maquinaria - Reportaría_CON_PRECIOS.xlsx', engine='openpyxl')
    df = df.replace('No hay datos', pd.NA)

    # Convertir columnas de precio a numérico
    price_cols = ['PRECIO_HORA', 'PRECIO_KM', 'PRECIO_MT3', 'PRECIO_VUELTA', 'PRECIO_DIARIO']
    for col in price_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    def count_prices(row):
        return sum([
            row['PRECIO_HORA'] > 0,
            row['PRECIO_KM'] > 0,
            row['PRECIO_MT3'] > 0,
            row['PRECIO_VUELTA'] > 0,
            row['PRECIO_DIARIO'] > 0
        ])

    df['NUM_PRECIOS'] = df.apply(count_prices, axis=1)

    # Estadísticas
    total_registros = len(df)
    sin_precio = df[df['NUM_PRECIOS'] == 0]
    un_precio = df[df['NUM_PRECIOS'] == 1]
    multi_precio = df[df['NUM_PRECIOS'] > 1]

    # Contratos únicos
    contratos_sin_precio = sin_precio['CONTRATO_TXT'].nunique()
    contratos_multi_precio = multi_precio['CONTRATO_TXT'].nunique()

    # Generar HTML
    html_parts = []

    # Header
    html_parts.append('''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Auditoría de Precios - Contratos Harcha Maquinaria</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; padding: 20px; }
        .container { max-width: 1400px; margin: 0 auto; background: white; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); color: white; padding: 30px; border-radius: 8px 8px 0 0; text-align: center; }
        h2 { color: #1e3c72; padding: 20px 20px 10px; border-bottom: 2px solid #2a5298; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; padding: 20px; }
        .stat-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .stat-card.danger { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); }
        .stat-card.success { background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%); }
        .stat-card.warning { background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); }
        .stat-number { font-size: 2.5em; font-weight: bold; }
        .stat-label { font-size: 0.9em; opacity: 0.9; }
        .section { padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 0.85em; }
        th { background: #1e3c72; color: white; padding: 12px; text-align: left; position: sticky; top: 0; }
        td { padding: 10px; border-bottom: 1px solid #ddd; }
        tr:nth-child(even) { background: #f9f9f9; }
        tr:hover { background: #f0f0f0; }
        .badge { display: inline-block; padding: 4px 8px; border-radius: 4px; font-size: 0.75em; font-weight: bold; }
        .badge-danger { background: #dc3545; color: white; }
        .badge-warning { background: #ffc107; color: #333; }
        .badge-success { background: #28a745; color: white; }
        .badge-info { background: #17a2b8; color: white; }
        .summary { background: #f8f9fa; padding: 15px; border-left: 4px solid #2a5298; margin: 20px; border-radius: 4px; }
        .progress-bar { width: 100%; height: 30px; background: #e0e0e0; border-radius: 15px; overflow: hidden; margin: 10px 0; }
        .progress-fill { height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; }
        .footer { background: #1e3c72; color: white; padding: 20px; text-align: center; border-radius: 0 0 8px 8px; }
        .alert-danger { background: #f8d7da; color: #721c24; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .alert-warning { background: #fff3cd; color: #856404; padding: 15px; border-radius: 4px; margin: 10px 0; }
        .alert-success { background: #d4edda; color: #155724; padding: 15px; border-radius: 4px; margin: 10px 0; }
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 AUDITORÍA DE PRECIOS - CONTRATOS HARCHA MAQUINARIA</h1>''')

    # Stats cards
    pct_un_precio = round(len(un_precio) / total_registros * 100, 1)
    pct_multi = round(len(multi_precio) / total_registros * 100, 1)
    pct_sin_precio = round(len(sin_precio) / total_registros * 100, 1)

    html_parts.append(f'''
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-number">{total_registros:,}</div>
                <div class="stat-label">Total Registros</div>
            </div>
            <div class="stat-card success">
                <div class="stat-number">{len(un_precio):,}</div>
                <div class="stat-label">1 Precio ({pct_un_precio}%)</div>
            </div>
            <div class="stat-card warning">
                <div class="stat-number">{len(multi_precio):,}</div>
                <div class="stat-label">Múltiples ({pct_multi}%)</div>
            </div>
            <div class="stat-card danger">
                <div class="stat-number">{len(sin_precio):,}</div>
                <div class="stat-label">Sin Precio ({pct_sin_precio}%)</div>
            </div>
        </div>''')

    # Resumen ejecutivo
    html_parts.append('''
        <h2>1. RESUMEN EJECUTIVO</h2>
        <div class="section">
            <div class="summary">
                <h3>🎯 Hallazgos Principales</h3>''')

    if len(sin_precio) > 0:
        html_parts.append(f'''
                <div class="alert-danger">
                    <strong>⚠️ CRÍTICO:</strong> {len(sin_precio)} registros ({pct_sin_precio}%) NO tienen ningún precio asignado.
                    <br>{contratos_sin_precio} contratos únicos afectados requieren atención inmediata.
                </div>''')

    if len(multi_precio) > 0:
        html_parts.append(f'''
                <div class="alert-warning">
                    <strong>⚡ ATENCIÓN:</strong> {len(multi_precio)} registros ({pct_multi}%) tienen MÚLTIPLES precios.
                    <br>{contratos_multi_precio} contratos híbridos requieren lógica especial de cálculo.
                </div>''')

    html_parts.append(f'''
                <div class="alert-success">
                    <strong>✅ CUMPLEN NORMA:</strong> {len(un_precio)} registros ({pct_un_precio}%) tienen exactamente un precio asignado.
                </div>
            </div>
        </div>''')

    # Distribución
    html_parts.append('''
        <h2>2. DISTRIBUCIÓN DE PRECIOS</h2>
        <div class="section">''')

    html_parts.append(f'''
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pct_un_precio}%; background: #28a745;">
                    1 Precio: {pct_un_precio}%
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pct_multi}%; background: #ffc107;">
                    Múltiples: {pct_multi}%
                </div>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: {pct_sin_precio}%; background: #dc3545;">
                    Sin Precio: {pct_sin_precio}%
                </div>
            </div>
        </div>''')

    # Contratos con múltiples precios
    if len(multi_precio) > 0:
        html_parts.append('''
        <h2>3. CONTRATOS HÍBRIDOS (Múltiples Precios)</h2>
        <div class="section">
            <table>
                <thead>
                    <tr>
                        <th>Contrato</th>
                        <th>Tipo</th>
                        <th>Hora</th>
                        <th>Km</th>
                        <th>Mt3</th>
                        <th>Vuelta</th>
                        <th>Diario</th>
                    </tr>
                </thead>
                <tbody>''')

        multi_unique = multi_precio.groupby('CONTRATO_TXT').agg({
            'TIPO_CONTRATO': 'first',
            'PRECIO_HORA': 'first',
            'PRECIO_KM': 'first',
            'PRECIO_MT3': 'first',
            'PRECIO_VUELTA': 'first',
            'PRECIO_DIARIO': 'first'
        }).reset_index()

        for _, row in multi_unique.iterrows():
            fmt = lambda x: f"${int(x):,}" if x > 0 else "-"
            html_parts.append(f'''
                    <tr>
                        <td><span class="badge badge-info">{row['CONTRATO_TXT']}</span></td>
                        <td>{row['TIPO_CONTRATO']}</td>
                        <td>{fmt(row['PRECIO_HORA'])}</td>
                        <td>{fmt(row['PRECIO_KM'])}</td>
                        <td>{fmt(row['PRECIO_MT3'])}</td>
                        <td>{fmt(row['PRECIO_VUELTA'])}</td>
                        <td>{fmt(row['PRECIO_DIARIO'])}</td>
                    </tr>''')

        html_parts.append('''
                </tbody>
            </table>
        </div>''')

    # Registros sin precio
    if len(sin_precio) > 0:
        html_parts.append('''
        <h2>4. REGISTROS SIN PRECIO (Requieren Atención)</h2>
        <div class="section">''')

        sin_precio_unique = sin_precio.groupby('CONTRATO_TXT').agg({
            'TIPO_CONTRATO': 'first',
            'MAQUINA_FULL': lambda x: ', '.join(x.unique()[:3]),
            'CLIENTE_TXT': 'first'
        }).reset_index()

        html_parts.append(f'<p><strong>{len(sin_precio_unique)} contratos únicos</strong> sin precios asignados</p>')

        html_parts.append('''
            <table>
                <thead>
                    <tr>
                        <th>Contrato</th>
                        <th>Tipo</th>
                        <th>Máquinas</th>
                        <th>Cliente</th>
                        <th>Estado</th>
                    </tr>
                </thead>
                <tbody>''')

        for _, row in sin_precio_unique.iterrows():
            cliente = row['CLIENTE_TXT'] if pd.notna(row['CLIENTE_TXT']) else 'N/A'
            html_parts.append(f'''
                    <tr>
                        <td><span class="badge badge-danger">{row['CONTRATO_TXT']}</span></td>
                        <td>{row['TIPO_CONTRATO']}</td>
                        <td>{row['MAQUINA_FULL']}</td>
                        <td>{cliente}</td>
                        <td><span class="badge badge-danger">SIN PRECIO</span></td>
                    </tr>''')

        html_parts.append('''
                </tbody>
            </table>
        </div>''')

    # Recomendaciones
    html_parts.append('''
        <h2>5. RECOMENDACIONES</h2>
        <div class="section">
            <div class="summary">
                <h3>📋 Plan de Acción</h3>
                <ol style="margin: 10px 0 10px 20px; line-height: 2;">
                    <li><strong>URGENTE:</strong> Asignar precios a los contratos sin precio para permitir cálculo de producción</li>
                    <li><strong>CONTRATOS HÍBRIDOS:</strong> Implementar lógica que sume los valores de todas las unidades con precio</li>
                    <li><strong>VALIDACIÓN:</strong> Crear validación automática en la carga de nuevos contratos</li>
                    <li><strong>REPORTING:</strong> Incluir indicador de estado de precios en los reportes</li>
                </ol>
            </div>
        </div>''')

    # Footer
    html_parts.append(f'''
        <div class="footer">
            <p>Generado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} | Archivo: Harcha Maquinaria - Reportaría_CON_PRECIOS.xlsx</p>
        </div>
    </div>
</body>
</html>''')

    # Escribir archivo
    with open('auditoria_precios.html', 'w', encoding='utf-8') as f:
        f.write(''.join(html_parts))

    print(f'Informe HTML generado: auditoria_precios.html')
    print(f'   - Total registros: {total_registros:,}')
    print(f'   - Registros sin precio: {len(sin_precio):,} ({pct_sin_precio}%)')
    print(f'   - Contratos unicos sin precio: {contratos_sin_precio}')
    print(f'   - Registros con multiples precios: {len(multi_precio):,} ({pct_multi}%)')
    print(f'   - Contratos unicos con multiples precios: {contratos_multi_precio}')


if __name__ == '__main__':
    generar_informe_auditoria()
