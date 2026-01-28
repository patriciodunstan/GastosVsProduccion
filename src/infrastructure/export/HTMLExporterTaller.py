"""
Exportador de datos a HTML para TALLER.

Genera un archivo HTML con dashboard de gastos de taller.
El taller no tiene producción, solo control de gastos.
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, List, Optional
from collections import defaultdict
import json

from src.domain.entities.GastoOperacional import GastoOperacional, TipoGasto
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.HorasHombre import HorasHombre


class HTMLExporterTaller:
    """
    Exporta los datos de gastos de TALLER a un archivo HTML.
    
    Crea un dashboard con:
    - Resumen de gastos totales
    - Desglose por categoría de gasto
    - Detalle mensual
    - Identificación de gastos imputables a máquinas
    """
    
    MESES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    def __init__(self, ruta_salida: str):
        """
        Inicializa el exportador.
        
        Args:
            ruta_salida: Ruta donde se guardará el archivo HTML
        """
        self.ruta_salida = Path(ruta_salida)
    
    def _formatear_moneda(self, valor: Decimal) -> str:
        """Formatea un valor como moneda chilena."""
        return f"${valor:,.0f}".replace(',', '.')
    
    def _formatear_numero(self, valor: Decimal, decimales: int = 2) -> str:
        """Formatea un número con decimales."""
        return f"{valor:,.{decimales}f}".replace(',', '.')
    
    def _get_clase_valor(self, valor: Decimal) -> str:
        """Obtiene la clase CSS para un valor."""
        if valor > 0:
            return 'negative'  # Gastos son negativos para el negocio
        return ''
    
    def exportar(
        self,
        gastos_taller: List[GastoOperacional],
        repuestos_taller: Optional[List[Repuesto]] = None,
        horas_hombre_taller: Optional[List[HorasHombre]] = None
    ):
        """
        Exporta los gastos de taller a HTML.

        Args:
            gastos_taller: Lista de gastos operacionales de taller
            repuestos_taller: Lista de repuestos usados en taller (opcional)
            horas_hombre_taller: Lista de horas hombre de taller (opcional)
        """
        # Calcular datos agregados
        datos = self._calcular_datos(
            gastos_taller,
            repuestos_taller or [],
            horas_hombre_taller or []
        )

        # Generar HTML
        html = self._generar_html(datos, gastos_taller)

        # Guardar archivo
        with open(self.ruta_salida, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _calcular_datos(
        self,
        gastos: List[GastoOperacional],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre]
    ) -> Dict:
        """Calcula los datos agregados para el informe."""
        
        # Totales generales
        total_gastos_op = Decimal('0')
        total_repuestos = Decimal('0')
        total_horas_hombre = Decimal('0')
        total_costo_hh = Decimal('0')
        
        # Por mes
        gastos_por_mes: Dict[int, Dict[str, Decimal]] = defaultdict(lambda: {
            'repuestos': Decimal('0'),
            'horas_hombre': Decimal('0'),
            'costo_hh': Decimal('0'),
            'combustibles': Decimal('0'),
            'reparaciones': Decimal('0'),
            'seguros': Decimal('0'),
            'honorarios': Decimal('0'),
            'epp': Decimal('0'),
            'peajes': Decimal('0'),
            'remuneraciones': Decimal('0'),
            'permisos': Decimal('0'),
            'alimentacion': Decimal('0'),
            'pasajes': Decimal('0'),
            'correspondencia': Decimal('0'),
            'gastos_legales': Decimal('0'),
            'multas': Decimal('0'),
            'otros_gastos': Decimal('0'),
            'total': Decimal('0')
        })
        
        # Por categoría
        gastos_por_categoria: Dict[str, Decimal] = defaultdict(Decimal)
        
        # Gastos con comentarios que mencionan máquinas (potencialmente imputables)
        gastos_imputables: List[Dict] = []
        
        COSTO_HORA = Decimal('35000')
        
        # Procesar gastos operacionales
        for gasto in gastos:
            if gasto.es_ingreso:
                continue
            
            mes = gasto.mes
            total_gastos_op += gasto.monto
            
            # Clasificar por tipo
            nombre_tipo = gasto.nombre_tipo_gasto
            gastos_por_categoria[nombre_tipo] += gasto.monto
            
            # Clasificar por mes y tipo
            if gasto.tipo_gasto == TipoGasto.COMBUSTIBLES.value:
                gastos_por_mes[mes]['combustibles'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REPARACIONES.value:
                gastos_por_mes[mes]['reparaciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SEGUROS.value:
                gastos_por_mes[mes]['seguros'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.HONORARIOS.value:
                gastos_por_mes[mes]['honorarios'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.EPP.value:
                gastos_por_mes[mes]['epp'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PEAJES.value:
                gastos_por_mes[mes]['peajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REMUNERACIONES.value:
                gastos_por_mes[mes]['remuneraciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PERMISOS.value:
                gastos_por_mes[mes]['permisos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ALIMENTACION.value:
                gastos_por_mes[mes]['alimentacion'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PASAJES.value:
                gastos_por_mes[mes]['pasajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.CORRESPONDENCIA.value:
                gastos_por_mes[mes]['correspondencia'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.GASTOS_LEGALES.value:
                gastos_por_mes[mes]['gastos_legales'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.MULTAS.value:
                gastos_por_mes[mes]['multas'] += gasto.monto
            else:
                gastos_por_mes[mes]['otros_gastos'] += gasto.monto
            
            gastos_por_mes[mes]['total'] += gasto.monto
            
            # Detectar gastos potencialmente imputables (glosa menciona código de máquina)
            glosa_upper = gasto.glosa.upper()
            # Patrones comunes de códigos de máquina: CT-XX, EX-XX, RX-XX, etc.
            import re
            patron_maquina = re.compile(r'[A-Z]{2,3}-\d{1,2}')
            match = patron_maquina.search(glosa_upper)
            if match:
                gastos_imputables.append({
                    'fecha': gasto.fecha,
                    'mes': mes,
                    'tipo': nombre_tipo,
                    'glosa': gasto.glosa,
                    'monto': gasto.monto,
                    'maquina_detectada': match.group(0),
                    'origen': gasto.origen
                })
        
        # Procesar repuestos de taller
        for repuesto in repuestos:
            mes = repuesto.fecha_salida.month
            total_repuestos += repuesto.total
            gastos_por_mes[mes]['repuestos'] += repuesto.total
            gastos_por_mes[mes]['total'] += repuesto.total
            gastos_por_categoria['Repuestos'] += repuesto.total
        
        # Procesar horas hombre de taller
        for hh in horas_hombre:
            mes = hh.fecha.month
            costo = hh.horas * COSTO_HORA
            total_horas_hombre += hh.horas
            total_costo_hh += costo
            gastos_por_mes[mes]['horas_hombre'] += hh.horas
            gastos_por_mes[mes]['costo_hh'] += costo
            gastos_por_mes[mes]['total'] += costo
            gastos_por_categoria['Horas Hombre'] += costo
        
        # Total general
        total_general = total_gastos_op + total_repuestos + total_costo_hh
        
        return {
            'total_general': total_general,
            'total_gastos_op': total_gastos_op,
            'total_repuestos': total_repuestos,
            'total_horas_hombre': total_horas_hombre,
            'total_costo_hh': total_costo_hh,
            'gastos_por_mes': dict(gastos_por_mes),
            'gastos_por_categoria': dict(gastos_por_categoria),
            'gastos_imputables': gastos_imputables,
            'cantidad_gastos': len(gastos),
            'cantidad_imputables': len(gastos_imputables)
        }
    
    def _generar_html(self, datos: Dict, gastos: List[GastoOperacional]) -> str:
        """Genera el contenido HTML completo."""

        # Generar filas de tablas por mes (para sub-tabs)
        filas_resumen_oct = self._generar_filas_resumen_mensual_por_mes(datos['gastos_por_mes'], 10)
        filas_resumen_nov = self._generar_filas_resumen_mensual_por_mes(datos['gastos_por_mes'], 11)
        filas_resumen_dic = self._generar_filas_resumen_mensual_por_mes(datos['gastos_por_mes'], 12)
        filas_resumen_trimestral = self._generar_filas_resumen_trimestral_ordenado(datos['gastos_por_mes'])

        # Generar filas de gastos imputables por mes (para sub-tabs)
        filas_imputables_oct = self._generar_filas_imputables_por_mes(datos['gastos_imputables'], 10)
        filas_imputables_nov = self._generar_filas_imputables_por_mes(datos['gastos_imputables'], 11)
        filas_imputables_dic = self._generar_filas_imputables_por_mes(datos['gastos_imputables'], 12)
        filas_imputables_trimestral = self._generar_filas_imputables_ordenado(datos['gastos_imputables'])

        filas_detalle = self._generar_filas_detalle(gastos)
        
        # Datos para gráficos
        datos_grafico_categorias = json.dumps({
            k: float(v) for k, v in datos['gastos_por_categoria'].items()
        })
        
        datos_grafico_meses = {}
        for mes, valores in datos['gastos_por_mes'].items():
            datos_grafico_meses[self.MESES[mes]] = float(valores['total'])
        datos_grafico_meses_json = json.dumps(datos_grafico_meses)
        
        # Calcular porcentaje de imputables
        porcentaje_imputables = Decimal('0')
        total_imputables = sum(g['monto'] for g in datos['gastos_imputables'])
        if datos['total_general'] > 0:
            porcentaje_imputables = (total_imputables / datos['total_general']) * 100
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe de Gastos TALLER - Q4 2025</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            padding: 20px;
            min-height: 100vh;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 10px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.2);
            padding: 30px;
        }}
        
        h1 {{
            color: #333;
            text-align: center;
            margin-bottom: 10px;
            font-size: 2.2em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.1em;
        }}
        
        .alerta {{
            background: #fff3cd;
            border: 1px solid #ffeaa7;
            color: #856404;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
        }}
        
        .alerta-importante {{
            background: #f8d7da;
            border: 1px solid #f5c6cb;
            color: #721c24;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
            text-align: center;
            font-weight: bold;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
            gap: 15px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}
        
        .card.repuestos {{
            background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
        }}
        
        .card.horas {{
            background: linear-gradient(135deg, #9b59b6 0%, #8e44ad 100%);
        }}
        
        .card.operacionales {{
            background: linear-gradient(135deg, #e67e22 0%, #d35400 100%);
        }}
        
        .card.imputables {{
            background: linear-gradient(135deg, #27ae60 0%, #219a52 100%);
        }}
        
        .card h3 {{
            font-size: 0.85em;
            opacity: 0.9;
            margin-bottom: 8px;
        }}
        
        .card .value {{
            font-size: 1.4em;
            font-weight: bold;
        }}
        
        .card .detail {{
            font-size: 0.75em;
            opacity: 0.8;
            margin-top: 5px;
        }}
        
        .section {{
            margin-bottom: 40px;
        }}
        
        .section h2 {{
            color: #c0392b;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e74c3c;
        }}
        
        .chart-container {{
            position: relative;
            height: 350px;
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }}
        
        .charts-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .table-responsive {{
            width: 100%;
            overflow-x: auto;
            -webkit-overflow-scrolling: touch;
            margin-bottom: 20px;
        }}
        
        th {{
            background: #e74c3c;
            color: white;
            padding: 12px 10px;
            text-align: left;
            font-weight: 600;
            white-space: nowrap;
            font-size: 0.85em;
        }}
        
        th.imputables {{
            background: #27ae60;
        }}
        
        td {{
            padding: 10px;
            border-bottom: 1px solid #eee;
            font-size: 0.9em;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .negative {{
            color: #e74c3c;
            font-weight: bold;
        }}
        
        .positive {{
            color: #27ae60;
            font-weight: bold;
        }}
        
        .imputable-row {{
            background: #e8f5e9;
            border-left: 4px solid #27ae60;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e74c3c;
            padding-bottom: 10px;
            flex-wrap: wrap;
        }}
        
        .tab {{
            padding: 10px 20px;
            background: #f0f0f0;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1em;
            font-weight: 600;
            transition: all 0.3s ease;
        }}
        
        .tab:hover {{
            background: #e0e0e0;
        }}
        
        .tab.active {{
            background: #e74c3c;
            color: white;
        }}
        
        .sub-tab-content {{
            display: none;
        }}

        .sub-tab-content.active {{
            display: block;
        }}

        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        .comentario {{
            font-style: italic;
            color: #666;
            font-size: 0.85em;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        .maquina-badge {{
            background: #27ae60;
            color: white;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔧 Informe de Gastos - TALLER</h1>
        <p class="subtitle">Trimestre Q4 2025 - Control de Gastos Operacionales</p>
        
        <div class="alerta">
            📋 <strong>Nota:</strong> El TALLER no genera producción directa. Este informe permite controlar y analizar los gastos operacionales del taller.
        </div>
        
        {f'''<div class="alerta-importante">
            ⚠️ <strong>ATENCIÓN:</strong> Se detectaron {datos['cantidad_imputables']} gastos ({self._formatear_moneda(total_imputables)}) 
            que mencionan códigos de máquinas en su descripción y podrían ser imputables a equipos específicos.
        </div>''' if datos['cantidad_imputables'] > 0 else ''}
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Gastos TALLER</h3>
                <div class="value">{self._formatear_moneda(datos['total_general'])}</div>
                <div class="detail">Trimestre Q4 2025</div>
            </div>
            <div class="card operacionales">
                <h3>Gastos Operacionales</h3>
                <div class="value">{self._formatear_moneda(datos['total_gastos_op'])}</div>
                <div class="detail">Reportes contables</div>
            </div>
            <div class="card repuestos">
                <h3>Repuestos</h3>
                <div class="value">{self._formatear_moneda(datos['total_repuestos'])}</div>
                <div class="detail">DATABODEGA</div>
            </div>
            <div class="card horas">
                <h3>Horas Hombre</h3>
                <div class="value">{self._formatear_numero(datos['total_horas_hombre'], 0)} H</div>
                <div class="detail">{self._formatear_moneda(datos['total_costo_hh'])} ($35.000/h)</div>
            </div>
            <div class="card imputables">
                <h3>Potencialmente Imputables</h3>
                <div class="value">{self._formatear_moneda(total_imputables)}</div>
                <div class="detail">{datos['cantidad_imputables']} operaciones ({self._formatear_numero(porcentaje_imputables, 1)}%)</div>
            </div>
            <div class="card">
                <h3>Total Operaciones</h3>
                <div class="value">{datos['cantidad_gastos']}</div>
                <div class="detail">Registros procesados</div>
            </div>
        </div>
        
        <div class="tabs">
            <button class="tab active" onclick="mostrarTab('resumen')">📊 Resumen Mensual</button>
            <button class="tab" onclick="mostrarTab('categorias')">📈 Por Categoría</button>
            <button class="tab" onclick="mostrarTab('detalle')">📋 Detalle Completo</button>
            <button class="tab" onclick="mostrarTab('imputables')">🎯 Gastos Imputables</button>
        </div>
        
        <!-- Tab: Resumen Mensual -->
        <div id="tab-resumen" class="tab-content active">
            <div class="section">
                <h2>📊 Resumen de Gastos por Mes</h2>
                <div class="tabs">
                    <button class="tab active" onclick="mostrarSubTab('tab-resumen-oct')">Octubre 2025</button>
                    <button class="tab" onclick="mostrarSubTab('tab-resumen-nov')">Noviembre 2025</button>
                    <button class="tab" onclick="mostrarSubTab('tab-resumen-dic')">Diciembre 2025</button>
                    <button class="tab" onclick="mostrarSubTab('tab-resumen-trimestral')">Resumen Trimestral</button>
                </div>

                <div id="tab-resumen-oct" class="sub-tab-content active">
                    <h3 style="margin-top: 20px; color: #333;">Octubre 2025 - Desglose de Gastos por Categoría</h3>
                    <div class="table-responsive">
                        <table id="tabla-resumen-oct" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th>Categoría</th>
                                    <th>Monto</th>
                                    <th>% del Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_resumen_oct}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-resumen-nov" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Noviembre 2025 - Desglose de Gastos por Categoría</h3>
                    <div class="table-responsive">
                        <table id="tabla-resumen-nov" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th>Categoría</th>
                                    <th>Monto</th>
                                    <th>% del Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_resumen_nov}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-resumen-dic" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Diciembre 2025 - Desglose de Gastos por Categoría</h3>
                    <div class="table-responsive">
                        <table id="tabla-resumen-dic" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th>Categoría</th>
                                    <th>Monto</th>
                                    <th>% del Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_resumen_dic}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-resumen-trimestral" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Resumen Trimestral - Consolidado Q4 2025</h3>
                    <div class="table-responsive">
                        <table id="tabla-resumen-trimestral">
                            <thead>
                                <tr>
                                    <th>Categoría</th>
                                    <th>Octubre</th>
                                    <th>Noviembre</th>
                                    <th>Diciembre</th>
                                    <th>Total Trimestral</th>
                                    <th>% del Total</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_resumen_trimestral}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Por Categoría -->
        <div id="tab-categorias" class="tab-content">
            <div class="section">
                <h2>📈 Distribución por Categoría</h2>
                <div class="charts-grid">
                    <div class="chart-container">
                        <canvas id="chartCategorias"></canvas>
                    </div>
                    <div class="chart-container">
                        <canvas id="chartCategoriasBar"></canvas>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Tab: Detalle Completo -->
        <div id="tab-detalle" class="tab-content">
            <div class="section">
                <h2>📋 Detalle de Todos los Gastos</h2>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Fecha</th>
                                <th>Mes</th>
                                <th>Tipo Gasto</th>
                                <th>Descripción</th>
                                <th>Monto</th>
                                <th>Origen</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filas_detalle}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Tab: Gastos Imputables -->
        <div id="tab-imputables" class="tab-content">
            <div class="section">
                <h2>🎯 Gastos Potencialmente Imputables a Máquinas</h2>
                <p style="color: #666; margin-bottom: 20px;">
                    Estos gastos mencionan códigos de máquinas en su descripción y podrían reasignarse
                    para un mejor control de costos por equipo.
                </p>
                <div class="tabs">
                    <button class="tab active" onclick="mostrarSubTabImputables('tab-imputables-oct')">Octubre 2025</button>
                    <button class="tab" onclick="mostrarSubTabImputables('tab-imputables-nov')">Noviembre 2025</button>
                    <button class="tab" onclick="mostrarSubTabImputables('tab-imputables-dic')">Diciembre 2025</button>
                    <button class="tab" onclick="mostrarSubTabImputables('tab-imputables-trimestral')">Resumen Trimestral</button>
                </div>

                <div id="tab-imputables-oct" class="sub-tab-content active">
                    <h3 style="margin-top: 20px; color: #333;">Octubre 2025 - Gastos Imputables</h3>
                    <div class="table-responsive">
                        <table id="tabla-imputables-oct" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th class="imputables">Fecha</th>
                                    <th class="imputables">Tipo</th>
                                    <th class="imputables">Máquina Detectada</th>
                                    <th class="imputables">Descripción</th>
                                    <th class="imputables">Monto</th>
                                    <th class="imputables">Origen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_imputables_oct}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-imputables-nov" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Noviembre 2025 - Gastos Imputables</h3>
                    <div class="table-responsive">
                        <table id="tabla-imputables-nov" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th class="imputables">Fecha</th>
                                    <th class="imputables">Tipo</th>
                                    <th class="imputables">Máquina Detectada</th>
                                    <th class="imputables">Descripción</th>
                                    <th class="imputables">Monto</th>
                                    <th class="imputables">Origen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_imputables_nov}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-imputables-dic" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Diciembre 2025 - Gastos Imputables</h3>
                    <div class="table-responsive">
                        <table id="tabla-imputables-dic" class="tabla-mensual">
                            <thead>
                                <tr>
                                    <th class="imputables">Fecha</th>
                                    <th class="imputables">Tipo</th>
                                    <th class="imputables">Máquina Detectada</th>
                                    <th class="imputables">Descripción</th>
                                    <th class="imputables">Monto</th>
                                    <th class="imputables">Origen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_imputables_dic}
                            </tbody>
                        </table>
                    </div>
                </div>

                <div id="tab-imputables-trimestral" class="sub-tab-content">
                    <h3 style="margin-top: 20px; color: #333;">Resumen Trimestral - Todos los Gastos Imputables</h3>
                    <div class="table-responsive">
                        <table id="tabla-imputables-trimestral">
                            <thead>
                                <tr>
                                    <th class="imputables">Fecha</th>
                                    <th class="imputables">Mes</th>
                                    <th class="imputables">Tipo</th>
                                    <th class="imputables">Máquina Detectada</th>
                                    <th class="imputables">Descripción</th>
                                    <th class="imputables">Monto</th>
                                    <th class="imputables">Origen</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filas_imputables_trimestral}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Datos para gráficos
        const datosCategorias = {datos_grafico_categorias};
        const datosMeses = {datos_grafico_meses_json};
        
        // Gráfico de barras mensual
        new Chart(document.getElementById('chartMensual'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(datosMeses),
                datasets: [{{
                    label: 'Total Gastos por Mes',
                    data: Object.values(datosMeses),
                    backgroundColor: 'rgba(231, 76, 60, 0.7)',
                    borderColor: 'rgba(192, 57, 43, 1)',
                    borderWidth: 1
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Gastos Mensuales TALLER (CLP)',
                        font: {{ size: 16 }}
                    }}
                }},
                scales: {{
                    y: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString('es-CL');
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Gráfico de dona por categoría
        const coloresCategorias = [
            '#e74c3c', '#3498db', '#9b59b6', '#e67e22', '#27ae60',
            '#f39c12', '#1abc9c', '#34495e', '#95a5a6', '#d35400',
            '#c0392b', '#2980b9', '#8e44ad', '#16a085', '#2c3e50'
        ];
        
        new Chart(document.getElementById('chartCategorias'), {{
            type: 'doughnut',
            data: {{
                labels: Object.keys(datosCategorias),
                datasets: [{{
                    data: Object.values(datosCategorias),
                    backgroundColor: coloresCategorias
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Distribución por Categoría',
                        font: {{ size: 16 }}
                    }},
                    legend: {{
                        position: 'right',
                        labels: {{
                            font: {{ size: 11 }}
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const value = context.parsed;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return context.label + ': $' + value.toLocaleString('es-CL') + ' (' + percentage + '%)';
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Gráfico de barras horizontales por categoría
        new Chart(document.getElementById('chartCategoriasBar'), {{
            type: 'bar',
            data: {{
                labels: Object.keys(datosCategorias),
                datasets: [{{
                    label: 'Monto por Categoría',
                    data: Object.values(datosCategorias),
                    backgroundColor: coloresCategorias
                }}]
            }},
            options: {{
                indexAxis: 'y',
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Gastos por Categoría (CLP)',
                        font: {{ size: 16 }}
                    }},
                    legend: {{
                        display: false
                    }}
                }},
                scales: {{
                    x: {{
                        beginAtZero: true,
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString('es-CL');
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Navegación de tabs principales
        function mostrarTab(tabId) {{
            // Ocultar solo los tabs principales (hijos directos del contenedor principal)
            const mainTabIds = ['resumen', 'categorias', 'detalle', 'imputables'];
            mainTabIds.forEach(id => {{
                const tabContent = document.getElementById('tab-' + id);
                if (tabContent) tabContent.classList.remove('active');
            }});
            document.querySelectorAll('.container > .tabs > .tab').forEach(tab => {{
                tab.classList.remove('active');
            }});

            // Mostrar el tab seleccionado
            const selectedTab = document.getElementById('tab-' + tabId);
            if (selectedTab) selectedTab.classList.add('active');
            event.target.classList.add('active');

            // Al cambiar a un tab con subtabs, activar el primero
            if (tabId === 'resumen') {{
                // Activar el primer sub-tab y su botón
                document.querySelectorAll('#tab-resumen .sub-tab-content[id^="tab-resumen-"]').forEach(c => c.classList.remove('active'));
                document.querySelectorAll('#tab-resumen > .section > .tabs > .tab').forEach(t => t.classList.remove('active'));

                const firstSubTab = document.getElementById('tab-resumen-oct');
                const firstSubTabBtn = document.querySelector('#tab-resumen > .section > .tabs > .tab');
                if (firstSubTab) firstSubTab.classList.add('active');
                if (firstSubTabBtn) firstSubTabBtn.classList.add('active');
            }}
            if (tabId === 'imputables') {{
                // Activar el primer sub-tab y su botón
                document.querySelectorAll('#tab-imputables .sub-tab-content[id^="tab-imputables-"]').forEach(c => c.classList.remove('active'));
                document.querySelectorAll('#tab-imputables > .section > .tabs > .tab').forEach(t => t.classList.remove('active'));

                const firstSubTab = document.getElementById('tab-imputables-oct');
                const firstSubTabBtn = document.querySelector('#tab-imputables > .section > .tabs > .tab');
                if (firstSubTab) firstSubTab.classList.add('active');
                if (firstSubTabBtn) firstSubTabBtn.classList.add('active');
            }}
        }}

        // Navegación de sub-tabs de Resumen
        function mostrarSubTab(subTabId) {{
            // Solo afectar los subtabs dentro de #tab-resumen
            const subContents = document.querySelectorAll('#tab-resumen .sub-tab-content[id^="tab-resumen-"]');
            const subTabs = document.querySelectorAll('#tab-resumen > .section > .tabs > .tab');

            subContents.forEach(c => {{
                if (c.id && c.id.startsWith('tab-resumen-')) {{
                    c.classList.remove('active');
                }}
            }});
            subTabs.forEach(t => t.classList.remove('active'));

            const targetTab = document.getElementById(subTabId);
            if (targetTab) targetTab.classList.add('active');
            if (event.target) event.target.classList.add('active');
        }}

        // Navegación de sub-tabs de Imputables
        function mostrarSubTabImputables(subTabId) {{
            // Solo afectar los subtabs dentro de #tab-imputables
            const subContents = document.querySelectorAll('#tab-imputables .sub-tab-content[id^="tab-imputables-"]');
            const subTabs = document.querySelectorAll('#tab-imputables > .section > .tabs > .tab');

            subContents.forEach(c => {{
                if (c.id && c.id.startsWith('tab-imputables-')) {{
                    c.classList.remove('active');
                }}
            }});
            subTabs.forEach(t => t.classList.remove('active'));

            const targetTab = document.getElementById(subTabId);
            if (targetTab) targetTab.classList.add('active');
            if (event.target) event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _generar_filas_resumen_mensual(self, gastos_por_mes: Dict[int, Dict]) -> str:
        """Genera las filas de la tabla de resumen mensual."""
        filas = []
        
        for mes in sorted(gastos_por_mes.keys()):
            g = gastos_por_mes[mes]
            otros = (
                g.get('peajes', Decimal('0')) +
                g.get('remuneraciones', Decimal('0')) +
                g.get('permisos', Decimal('0')) +
                g.get('alimentacion', Decimal('0')) +
                g.get('pasajes', Decimal('0')) +
                g.get('correspondencia', Decimal('0')) +
                g.get('gastos_legales', Decimal('0')) +
                g.get('multas', Decimal('0')) +
                g.get('otros_gastos', Decimal('0'))
            )
            
            fila = f"""<tr>
                <td><strong>{self.MESES[mes]}</strong></td>
                <td>{self._formatear_moneda(g.get('repuestos', Decimal('0')))}</td>
                <td>{self._formatear_numero(g.get('horas_hombre', Decimal('0')), 0)}</td>
                <td>{self._formatear_moneda(g.get('costo_hh', Decimal('0')))}</td>
                <td>{self._formatear_moneda(g.get('combustibles', Decimal('0')))}</td>
                <td>{self._formatear_moneda(g.get('reparaciones', Decimal('0')))}</td>
                <td>{self._formatear_moneda(g.get('seguros', Decimal('0')))}</td>
                <td>{self._formatear_moneda(g.get('honorarios', Decimal('0')))}</td>
                <td>{self._formatear_moneda(g.get('epp', Decimal('0')))}</td>
                <td>{self._formatear_moneda(otros)}</td>
                <td class="negative"><strong>{self._formatear_moneda(g.get('total', Decimal('0')))}</strong></td>
            </tr>"""
            filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_filas_detalle(self, gastos: List[GastoOperacional]) -> str:
        """Genera las filas de la tabla de detalle."""
        filas = []
        
        # Ordenar por fecha
        gastos_ordenados = sorted(gastos, key=lambda g: g.fecha)
        
        for gasto in gastos_ordenados:
            if gasto.es_ingreso:
                continue
            
            glosa_truncada = gasto.glosa[:50] + '...' if len(gasto.glosa) > 50 else gasto.glosa
            
            fila = f"""<tr>
                <td>{gasto.fecha.strftime('%d/%m/%Y')}</td>
                <td>{self.MESES[gasto.mes]}</td>
                <td>{gasto.nombre_tipo_gasto}</td>
                <td class="comentario" title="{gasto.glosa}">{glosa_truncada}</td>
                <td class="negative">{self._formatear_moneda(gasto.monto)}</td>
                <td>{gasto.origen}</td>
            </tr>"""
            filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_filas_imputables(self, gastos_imputables: List[Dict]) -> str:
        """Genera las filas de la tabla de gastos imputables."""
        if not gastos_imputables:
            return '<tr><td colspan="7" style="text-align: center; color: #666;">No se detectaron gastos imputables a máquinas específicas</td></tr>'
        
        filas = []
        
        # Ordenar por máquina detectada
        gastos_ordenados = sorted(gastos_imputables, key=lambda g: (g['maquina_detectada'], g['fecha']))
        
        for gasto in gastos_ordenados:
            glosa_truncada = gasto['glosa'][:40] + '...' if len(gasto['glosa']) > 40 else gasto['glosa']
            
            fila = f"""<tr class="imputable-row">
                <td>{gasto['fecha'].strftime('%d/%m/%Y')}</td>
                <td>{self.MESES[gasto['mes']]}</td>
                <td>{gasto['tipo']}</td>
                <td><span class="maquina-badge">{gasto['maquina_detectada']}</span></td>
                <td class="comentario" title="{gasto['glosa']}">{glosa_truncada}</td>
                <td class="positive"><strong>{self._formatear_moneda(gasto['monto'])}</strong></td>
                <td>{gasto['origen']}</td>
            </tr>"""
            filas.append(fila)

        return '\n'.join(filas)

    def _generar_filas_resumen_mensual_por_mes(self, gastos_por_mes: Dict[int, Dict], mes: int) -> str:
        """Genera las filas de la tabla de resumen para un mes específico, ordenadas por monto descendente."""
        if mes not in gastos_por_mes:
            return '<tr><td colspan="3" style="text-align: center; color: #666;">No hay datos para este mes</td></tr>'

        g = gastos_por_mes[mes]
        total_mes = g.get('total', Decimal('0'))

        # Crear lista de categorías con sus montos
        categorias = [
            ('Repuestos', g.get('repuestos', Decimal('0'))),
            ('Horas Hombre', g.get('costo_hh', Decimal('0'))),
            ('Combustibles', g.get('combustibles', Decimal('0'))),
            ('Reparaciones', g.get('reparaciones', Decimal('0'))),
            ('Seguros', g.get('seguros', Decimal('0'))),
            ('Honorarios', g.get('honorarios', Decimal('0'))),
            ('EPP', g.get('epp', Decimal('0'))),
            ('Peajes', g.get('peajes', Decimal('0'))),
            ('Remuneraciones', g.get('remuneraciones', Decimal('0'))),
            ('Permisos', g.get('permisos', Decimal('0'))),
            ('Alimentación', g.get('alimentacion', Decimal('0'))),
            ('Pasajes', g.get('pasajes', Decimal('0'))),
            ('Correspondencia', g.get('correspondencia', Decimal('0'))),
            ('Gastos Legales', g.get('gastos_legales', Decimal('0'))),
            ('Multas', g.get('multas', Decimal('0'))),
            ('Otros Gastos', g.get('otros_gastos', Decimal('0')))
        ]

        # Filtrar categorías con monto > 0 y ordenar por monto descendente
        categorias_con_monto = [(cat, monto) for cat, monto in categorias if monto > 0]
        categorias_con_monto.sort(key=lambda x: x[1], reverse=True)

        if not categorias_con_monto:
            return '<tr><td colspan="3" style="text-align: center; color: #666;">No hay gastos registrados para este mes</td></tr>'

        filas = []
        for categoria, monto in categorias_con_monto:
            porcentaje = (monto / total_mes * 100) if total_mes > 0 else Decimal('0')
            fila = f"""<tr>
                <td><strong>{categoria}</strong></td>
                <td class="negative">{self._formatear_moneda(monto)}</td>
                <td>{self._formatear_numero(porcentaje, 1)}%</td>
            </tr>"""
            filas.append(fila)

        # Agregar fila del total
        filas.append(f"""<tr style="background: #f8f9fa; font-weight: bold;">
            <td>TOTAL {self.MESES[mes].upper()}</td>
            <td class="negative">{self._formatear_moneda(total_mes)}</td>
            <td>100.0%</td>
        </tr>""")

        return '\n'.join(filas)

    def _generar_filas_resumen_trimestral_ordenado(self, gastos_por_mes: Dict[int, Dict]) -> str:
        """Genera las filas del resumen trimestral, ordenadas por total trimestral descendente."""
        # Definir categorías
        categorias = [
            'Repuestos', 'Horas Hombre', 'Combustibles', 'Reparaciones', 'Seguros',
            'Honorarios', 'EPP', 'Peajes', 'Remuneraciones', 'Permisos',
            'Alimentación', 'Pasajes', 'Correspondencia', 'Gastos Legales',
            'Multas', 'Otros Gastos'
        ]

        # Mapeo de categorías a claves en el diccionario
        claves_categoria = {
            'Repuestos': 'repuestos',
            'Horas Hombre': 'costo_hh',
            'Combustibles': 'combustibles',
            'Reparaciones': 'reparaciones',
            'Seguros': 'seguros',
            'Honorarios': 'honorarios',
            'EPP': 'epp',
            'Peajes': 'peajes',
            'Remuneraciones': 'remuneraciones',
            'Permisos': 'permisos',
            'Alimentación': 'alimentacion',
            'Pasajes': 'pasajes',
            'Correspondencia': 'correspondencia',
            'Gastos Legales': 'gastos_legales',
            'Multas': 'multas',
            'Otros Gastos': 'otros_gastos'
        }

        # Calcular totales trimestrales por categoría
        totales_trimestral = {}
        for categoria in categorias:
            totales_trimestral[categoria] = Decimal('0')

        for mes in [10, 11, 12]:
            if mes in gastos_por_mes:
                g = gastos_por_mes[mes]
                for categoria in categorias:
                    clave = claves_categoria[categoria]
                    totales_trimestral[categoria] += g.get(clave, Decimal('0'))

        # Calcular total general del trimestre
        total_general_trimestral = sum(totales_trimestral.values())

        # Crear lista de categorías con sus totales y ordenar por monto descendente
        categorias_con_total = [(cat, totales_trimestral[cat]) for cat in categorias]
        categorias_con_total.sort(key=lambda x: x[1], reverse=True)

        # Filtrar solo categorías con monto > 0
        categorias_con_total = [(cat, monto) for cat, monto in categorias_con_total if monto > 0]

        if not categorias_con_total:
            return '<tr><td colspan="6" style="text-align: center; color: #666;">No hay gastos registrados en el trimestre</td></tr>'

        filas = []
        for categoria, total_cat in categorias_con_total:
            clave = claves_categoria[categoria]
            monto_oct = gastos_por_mes.get(10, {}).get(clave, Decimal('0'))
            monto_nov = gastos_por_mes.get(11, {}).get(clave, Decimal('0'))
            monto_dic = gastos_por_mes.get(12, {}).get(clave, Decimal('0'))
            porcentaje = (total_cat / total_general_trimestral * 100) if total_general_trimestral > 0 else Decimal('0')

            fila = f"""<tr>
                <td><strong>{categoria}</strong></td>
                <td>{self._formatear_moneda(monto_oct) if monto_oct > 0 else '-'}</td>
                <td>{self._formatear_moneda(monto_nov) if monto_nov > 0 else '-'}</td>
                <td>{self._formatear_moneda(monto_dic) if monto_dic > 0 else '-'}</td>
                <td class="negative"><strong>{self._formatear_moneda(total_cat)}</strong></td>
                <td>{self._formatear_numero(porcentaje, 1)}%</td>
            </tr>"""
            filas.append(fila)

        # Agregar fila del total general
        total_oct = Decimal(sum(gastos_por_mes.get(10, {}).get(claves_categoria[cat], Decimal('0')) for cat in categorias))
        total_nov = Decimal(sum(gastos_por_mes.get(11, {}).get(claves_categoria[cat], Decimal('0')) for cat in categorias))
        total_dic = Decimal(sum(gastos_por_mes.get(12, {}).get(claves_categoria[cat], Decimal('0')) for cat in categorias))

        filas.append(f"""<tr style="background: #f8f9fa; font-weight: bold;">
            <td>TOTAL TRIMESTRAL</td>
            <td>{self._formatear_moneda(total_oct) if total_oct > 0 else '-'}</td>
            <td>{self._formatear_moneda(total_nov) if total_nov > 0 else '-'}</td>
            <td>{self._formatear_moneda(total_dic) if total_dic > 0 else '-'}</td>
            <td class="negative">{self._formatear_moneda(total_general_trimestral)}</td>
            <td>100.0%</td>
        </tr>""")

        return '\n'.join(filas)

    def _generar_filas_imputables_por_mes(self, gastos_imputables: List[Dict], mes: int) -> str:
        """Genera las filas de gastos imputables para un mes específico, ordenadas por monto descendente."""
        # Filtrar por mes
        gastos_del_mes = [g for g in gastos_imputables if g['mes'] == mes]

        if not gastos_del_mes:
            return f'<tr><td colspan="6" style="text-align: center; color: #666;">No hay gastos imputables para {self.MESES[mes]}</td></tr>'

        # Ordenar por monto descendente
        gastos_del_mes.sort(key=lambda g: g['monto'], reverse=True)

        filas = []
        for gasto in gastos_del_mes:
            glosa_truncada = gasto['glosa'][:40] + '...' if len(gasto['glosa']) > 40 else gasto['glosa']

            fila = f"""<tr class="imputable-row">
                <td>{gasto['fecha'].strftime('%d/%m/%Y')}</td>
                <td>{gasto['tipo']}</td>
                <td><span class="maquina-badge">{gasto['maquina_detectada']}</span></td>
                <td class="comentario" title="{gasto['glosa']}">{glosa_truncada}</td>
                <td class="positive"><strong>{self._formatear_moneda(gasto['monto'])}</strong></td>
                <td>{gasto['origen']}</td>
            </tr>"""
            filas.append(fila)

        return '\n'.join(filas)

    def _generar_filas_imputables_ordenado(self, gastos_imputables: List[Dict]) -> str:
        """Genera todas las filas de gastos imputables ordenadas por monto descendente."""
        if not gastos_imputables:
            return '<tr><td colspan="7" style="text-align: center; color: #666;">No se detectaron gastos imputables a máquinas específicas</td></tr>'

        # Ordenar por monto descendente
        gastos_ordenados = sorted(gastos_imputables, key=lambda g: g['monto'], reverse=True)

        filas = []
        for gasto in gastos_ordenados:
            glosa_truncada = gasto['glosa'][:40] + '...' if len(gasto['glosa']) > 40 else gasto['glosa']

            fila = f"""<tr class="imputable-row">
                <td>{gasto['fecha'].strftime('%d/%m/%Y')}</td>
                <td>{self.MESES[gasto['mes']]}</td>
                <td>{gasto['tipo']}</td>
                <td><span class="maquina-badge">{gasto['maquina_detectada']}</span></td>
                <td class="comentario" title="{gasto['glosa']}">{glosa_truncada}</td>
                <td class="positive"><strong>{self._formatear_moneda(gasto['monto'])}</strong></td>
                <td>{gasto['origen']}</td>
            </tr>"""
            filas.append(fila)

        return '\n'.join(filas)