"""
Exportador de datos a HTML.

Genera un archivo HTML con dashboard interactivo y gráficos.
Sigue el principio de responsabilidad única (SRP).
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple, List, Optional, Any
import json

from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.entities.GastoOperacional import GastoOperacional
from src.domain.services.CalculadorProduccionReal import CalculadorProduccionReal
from src.domain.services.CalculadorGastos import CalculadorGastos


class HTMLExporter:
    """
    Exporta los datos del informe a un archivo HTML.
    
    Crea un dashboard interactivo con:
    - Resumen ejecutivo
    - Gráficos de producción vs gastos
    - Tablas con datos ya incluidos (estático)
    - Tabs y sub-tabs para navegación
    - Detalle por máquina
    """
    
    MESES = {
        10: 'Octubre',
        11: 'Noviembre',
        12: 'Diciembre'
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
    
    def exportar(
        self,
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        leasing: Optional[List[Leasing]] = None
    ):
        """
        Exporta todos los datos a HTML.
        
        Args:
            producciones: Lista de producciones
            repuestos: Lista de repuestos
            horas_hombre: Lista de horas hombre
            leasing: Lista de leasing (opcional)
        """
        # Calcular datos agregados
        datos = CalculadorProduccionReal.calcular_por_maquina_mes(
            producciones, repuestos, horas_hombre, leasing or []
        )
        
        # Generar HTML
        html = self._generar_html(datos, producciones, repuestos, horas_hombre)
        
        # Guardar archivo
        with open(self.ruta_salida, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def exportar_completo(
        self,
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        gastos_operacionales: List[GastoOperacional],
        leasing: Optional[List[Leasing]] = None
    ):
        """
        Exporta todos los datos completos a HTML (producción + gastos operacionales).
        
        Args:
            producciones: Lista de producciones
            repuestos: Lista de repuestos
            horas_hombre: Lista de horas hombre
            gastos_operacionales: Lista de gastos de reportes contables
            leasing: Lista de leasing (opcional)
        """
        from src.domain.entities.GastoOperacional import GastoOperacional
        
        # Calcular datos de producción
        datos_produccion = CalculadorProduccionReal.calcular_por_maquina_mes(
            producciones, repuestos, horas_hombre, leasing or []
        )
        
        # Calcular datos de gastos completos
        datos_gastos = CalculadorGastos.calcular_por_maquina_mes_completo(
            repuestos, horas_hombre, gastos_operacionales, leasing or []
        )
        
        # Combinar ambos conjuntos de datos
        datos = self._combinar_datos_produccion_gastos(datos_produccion, datos_gastos)
        
        # Generar HTML
        html = self._generar_html_completo(datos, producciones, repuestos, horas_hombre, gastos_operacionales)
        
        # Guardar archivo
        with open(self.ruta_salida, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _combinar_datos_produccion_gastos(
        self, 
        datos_produccion: Dict[Tuple[str, int], Dict], 
        datos_gastos: Dict[Tuple[str, int], Dict]
    ) -> Dict[Tuple[str, int], Dict]:
        """Combina datos de producción y gastos en una sola estructura."""
        datos_combinados: Dict[Tuple[str, int], Dict] = {}
        
        # Obtener todas las claves únicas
        todas_claves = set(datos_produccion.keys()) | set(datos_gastos.keys())
        
        for clave in todas_claves:
            datos_combinados[clave] = {}
            
            # Agregar datos de producción si existen
            if clave in datos_produccion:
                datos_combinados[clave]['produccion'] = datos_produccion[clave]['produccion']
                datos_combinados[clave]['produccion_neta'] = datos_produccion[clave]['produccion_neta']
                datos_combinados[clave]['produccion_real'] = datos_produccion[clave]['produccion_real']
            else:
                # Valores por defecto si no hay datos de producción
                datos_combinados[clave]['produccion'] = {
                    'mt3': Decimal('0'),
                    'horas_trabajadas': Decimal('0'),
                    'kilometros': Decimal('0'),
                    'vueltas': Decimal('0'),
                    'valor_mt3': Decimal('0'),
                    'valor_horas': Decimal('0'),
                    'valor_km': Decimal('0'),
                    'valor_dias': Decimal('0'),
                    'valor_vueltas': Decimal('0')
                }
                datos_combinados[clave]['produccion_neta'] = {
                    'mt3': Decimal('0'),
                    'horas_trabajadas': Decimal('0'),
                    'kilometros': Decimal('0'),
                    'vueltas': Decimal('0'),
                    'valor_monetario': Decimal('0')
                }
                datos_combinados[clave]['produccion_real'] = {
                    'mt3': Decimal('0'),
                    'horas_trabajadas': Decimal('0'),
                    'kilometros': Decimal('0'),
                    'vueltas': Decimal('0'),
                    'valor_monetario': Decimal('0')
                }
            
            # Agregar datos de gastos si existen
            if clave in datos_gastos:
                datos_combinados[clave]['gastos'] = datos_gastos[clave]
            else:
                # Valores por defecto si no hay datos de gastos
                datos_combinados[clave]['gastos'] = datos_gastos.get(clave, {
                    'repuestos': Decimal('0'),
                    'horas_hombre': Decimal('0'),
                    'costo_hh': Decimal('0'),
                    'leasing': Decimal('0'),
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
                    'total_gastos_operacionales': Decimal('0'),
                    'total': Decimal('0')
                })
        
        return datos_combinados
    
    def _generar_html(
        self,
        datos: Dict[Tuple[str, int], Dict],
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre]
    ) -> str:
        """Genera el contenido HTML completo estático."""
        
        # Calcular totales
        total_mt3 = Decimal('0')
        total_horas = Decimal('0')
        total_gastos = Decimal('0')
        total_prod_neta = Decimal('0')
        total_prod_real = Decimal('0')
        
        # Datos por mes
        datos_por_mes: Dict[int, List[Tuple[str, Dict]]] = {10: [], 11: [], 12: []}
        datos_por_maquina: Dict[str, Dict[int, Dict]] = {}
        
        for (maquina, mes), valores in datos.items():
            if maquina not in datos_por_maquina:
                datos_por_maquina[maquina] = {}
            datos_por_maquina[maquina][mes] = valores
            datos_por_mes[mes].append((maquina, valores))
            
            total_mt3 += valores['produccion']['mt3']
            total_horas += valores['produccion']['horas_trabajadas']
            total_gastos += valores['gastos']['total']
            total_prod_neta += valores['produccion_neta']['valor_monetario']
            total_prod_real += valores['produccion_real']['valor_monetario']
        
        # Generar HTML
        html = self._generar_html_estatico(
            total_mt3=total_mt3,
            total_horas=total_horas,
            total_gastos=total_gastos,
            total_prod_neta=total_prod_neta,
            total_prod_real=total_prod_real,
            datos_por_mes=datos_por_mes,
            datos_por_maquina=datos_por_maquina,
            incluir_gastos_operacionales=False
        )
        
        return html
    
    def _generar_html_completo(
        self,
        datos: Dict[Tuple[str, int], Dict],
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        gastos_operacionales: List[GastoOperacional]
    ) -> str:
        """Genera el contenido HTML completo con gastos operacionales."""
        
        # Calcular totales
        total_mt3 = Decimal('0')
        total_gastos_op = Decimal('0')
        total_repuestos = Decimal('0')
        total_horas_hombre = Decimal('0')
        total_costo_hh = Decimal('0')
        total_leasing = Decimal('0')
        total_combustibles = Decimal('0')
        total_reparaciones = Decimal('0')
        total_prod_neta = Decimal('0')
        total_prod_real = Decimal('0')
        
        # Datos por mes
        datos_por_mes: Dict[int, List[Tuple[str, Dict]]] = {10: [], 11: [], 12: []}
        datos_por_maquina: Dict[str, Dict[int, Dict]] = {}
        
        for (maquina, mes), valores in datos.items():
            if maquina not in datos_por_maquina:
                datos_por_maquina[maquina] = {}
            datos_por_maquina[maquina][mes] = valores
            datos_por_mes[mes].append((maquina, valores))
            
            total_mt3 += valores['produccion']['mt3']
            total_gastos_op += valores['gastos'].get('total_gastos_operacionales', Decimal('0'))
            total_repuestos += valores['gastos'].get('repuestos', Decimal('0'))
            total_horas_hombre += valores['gastos'].get('horas_hombre', Decimal('0'))
            total_costo_hh += valores['gastos'].get('costo_hh', Decimal('0'))
            total_leasing += valores['gastos'].get('leasing', Decimal('0'))
            total_combustibles += valores['gastos'].get('combustibles', Decimal('0'))
            total_reparaciones += valores['gastos'].get('reparaciones', Decimal('0'))
            total_prod_neta += valores['produccion_neta']['valor_monetario']
            total_prod_real += valores['produccion_real']['valor_monetario']
        
        # Calcular total de gastos completo (todos los tipos)
        total_gastos_completo = (total_repuestos + total_costo_hh + total_leasing +
                                  total_combustibles + total_reparaciones + total_gastos_op)
        
        # Generar HTML
        html = self._generar_html_estatico(
            total_mt3=total_mt3,
            total_horas=Decimal('0'),
            total_gastos=total_gastos_completo,
            total_prod_neta=total_prod_neta,
            total_prod_real=total_prod_real,
            datos_por_mes=datos_por_mes,
            datos_por_maquina=datos_por_maquina,
            incluir_gastos_operacionales=True,
            total_combustibles=total_combustibles,
            total_reparaciones=total_reparaciones
        )
        
        return html
    
    def _generar_html_estatico(
        self,
        total_mt3: Decimal,
        total_horas: Decimal,
        total_gastos: Decimal,
        total_prod_neta: Decimal,
        total_prod_real: Decimal,
        datos_por_mes: Dict[int, List[Tuple[str, Dict]]],
        datos_por_maquina: Dict[str, Dict[int, Dict]],
        incluir_gastos_operacionales: bool = False,
        total_combustibles: Optional[Decimal] = None,
        total_reparaciones: Decimal = Decimal('0')
    ) -> str:
        """Genera el contenido HTML completo estático con datos ya incluidos."""
        
        # Generar filas de las tablas
        filas_resumen_oct = self._generar_filas_resumen(datos_por_mes.get(10, []))
        filas_resumen_nov = self._generar_filas_resumen(datos_por_mes.get(11, []))
        filas_resumen_dic = self._generar_filas_resumen(datos_por_mes.get(12, []))
        filas_resumen_trimestral = self._generar_filas_resumen_trimestral(datos_por_maquina)
        filas_produccion = self._generar_filas_produccion(datos_por_maquina)
        filas_gastos = self._generar_filas_gastos(datos_por_maquina, incluir_gastos_operacionales)
        
        # Generar tabla de resumen de gastos por mes (estático)
        tabla_gastos_mensual = self._generar_tabla_gastos_mensual(datos_por_mes, incluir_gastos_operacionales)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Producción vs Gastos - Q4 2025</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
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
            font-size: 2.5em;
        }}
        
        .subtitle {{
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 1.2em;
        }}
        
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}
        
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
            min-width: 0;
            overflow: hidden;
            word-wrap: break-word;
        }}
        
        .card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .card .value {{
            font-size: clamp(1.2em, 4vw, 2em);
            font-weight: bold;
            word-wrap: break-word;
            overflow-wrap: break-word;
            line-height: 1.2;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        @media (max-width: 768px) {{
            .summary-cards {{
                grid-template-columns: 1fr;
                gap: 15px;
            }}
            
            .card {{
                padding: 15px;
            }}
            
            .card .value {{
                font-size: 1.5em;
            }}
        }}
        
        @media (max-width: 480px) {{
            .card .value {{
                font-size: 1.2em;
            }}
            
            .card h3 {{
                font-size: 0.8em;
            }}
        }}
        
        .section {{
            margin-bottom: 50px;
        }}
        
        .section h2 {{
            color: #333;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #667eea;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 30px;
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
        }}
        
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            background: white;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        th {{
            background: #667eea;
            color: white;
            padding: 15px;
            text-align: left;
            font-weight: 600;
        }}
        
        td {{
            padding: 12px 15px;
            border-bottom: 1px solid #eee;
        }}
        
        tr:hover {{
            background: #f8f9fa;
        }}
        
        .positive {{
            color: #28a745;
            font-weight: bold;
        }}
        
        .negative {{
            color: #dc3545;
            font-weight: bold;
        }}
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
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
            background: #667eea;
            color: white;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Informe Producción vs Gastos</h1>
        <p class="subtitle">Trimestre Q4 2025 - Octubre, Noviembre, Diciembre</p>
        <p style="text-align: center; color: #666; font-size: 0.9em; margin-top: -10px; margin-bottom: 20px; padding: 10px; background: #f0f0f0; border-radius: 5px;">
            <strong>Nota:</strong> Todos los valores monetarios mostrados son <strong>NETOS (sin IVA)</strong>.
            El leasing incluye descuento del 19% de IVA. Los repuestos ya vienen sin IVA.
        </p>
        
        <!-- Tabs de navegación -->
        
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Gastos</h3>
                <div class="value">{self._formatear_moneda(total_gastos)}</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Repuestos (sin IVA) + HH × $35.000 + Leasing (neto, IVA descontado)</p>
            </div>
            <div class="card">
                <h3>Total Producción Neta</h3>
                <div class="value">{self._formatear_moneda(total_prod_neta)}</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Valores netos (sin IVA)</p>
            </div>
            <div class="card">
                <h3>Total Producción Real</h3>
                <div class="value">{self._formatear_moneda(total_prod_real)}</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Prod. Neta - Gastos Totales (valores netos)</p>
            </div>
        </div>

        <div class="tabs">
            <button class="tab active" onclick="mostrarTab('resumen')">📊 Resumen Trimestral</button>
            <button class="tab" onclick="mostrarTab('produccion')">🏭 Detalle Producción</button>
            <button class="tab" onclick="mostrarTab('gastos')">💰 Detalle Gastos</button>
        </div>
        
        <!-- Tab: Resumen Trimestral -->
        <div id="tab-resumen" class="tab-content active">
            <div class="section">
                <h2>📈 Resumen de Gastos por Mes</h2>
                {tabla_gastos_mensual}
            </div>
            
            <div class="section">
                <h2>📊 Resumen Trimestral</h2>
            
            <h3 style="margin-top: 20px; color: #333;">Octubre 2025</h3>
            <table id="tabla-resumen-oct" class="tabla-mensual">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Producción</th>
                        <th>Prod. Neta</th>
                        <th>Gastos</th>
                        <th>Prod. Real</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_resumen_oct}
                </tbody>
            </table>
            
            <h3 style="margin-top: 40px; color: #333;">Noviembre 2025</h3>
            <table id="tabla-resumen-nov" class="tabla-mensual">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Producción</th>
                        <th>Prod. Neta</th>
                        <th>Gastos</th>
                        <th>Prod. Real</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_resumen_nov}
                </tbody>
            </table>
            
            <h3 style="margin-top: 40px; color: #333;">Diciembre 2025</h3>
            <table id="tabla-resumen-dic" class="tabla-mensual">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Producción</th>
                        <th>Prod. Neta</th>
                        <th>Gastos</th>
                        <th>Prod. Real</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_resumen_dic}
                </tbody>
            </table>
            
            <h3 style="margin-top: 40px; color: #333;">Resumen Trimestral (Total)</h3>
            <table id="tabla-resumen-trimestral">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Total Producción</th>
                        <th>Total Prod. Neta</th>
                        <th>Total Gastos</th>
                        <th>Total Prod. Real</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_resumen_trimestral}
                </tbody>
            </table>
            </div>
        </div>
        
        <!-- Tab: Detalle Producción -->
        <div id="tab-produccion" class="tab-content">
            <div class="section">
                <h2>🏭 Detalle Producción</h2>
                <table id="tabla-produccion">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Mes</th>
                        <th>MT3</th>
                        <th>Horas</th>
                        <th>Kilómetros</th>
                        <th>Vueltas</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_produccion}
                </tbody>
            </table>
            </div>
        </div>
        
        <!-- Tab: Detalle Gastos -->
        <div id="tab-gastos" class="tab-content">
            <div class="section">
                <h2>💰 Detalle Gastos</h2>
                <table id="tabla-gastos">
                <thead>
                    <tr>
                        <th>Máquina</th>
                        <th>Mes</th>
                        <th>Repuestos</th>
                        <th>Horas Hombre</th>
                        <th>Costo HH</th>
                        <th>Leasing</th>
                        <th>Total Gastos</th>
                    </tr>
                </thead>
                <tbody>
                    {filas_gastos}
                </tbody>
            </table>
            </div>
        </div>
    </div>
    
    <script>
        function mostrarTab(tabId) {{
            // Ocultar todos los contenidos de tabs
            const tabContents = document.querySelectorAll('.tab-content');
            tabContents.forEach(content => {{
                content.classList.remove('active');
            }});
            
            // Desactivar todos los tabs
            const tabs = document.querySelectorAll('.tab');
            tabs.forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // Mostrar el contenido del tab seleccionado
            document.getElementById('tab-' + tabId).classList.add('active');
            
            // Activar el tab seleccionado
            event.target.classList.add('active');
        }}
    </script>
</body>
</html>
"""
        return html
    
    def _generar_filas_resumen(self, datos: List[Tuple[str, Dict]]) -> str:
        """Genera las filas de la tabla de resumen mensual."""
        filas = []
        
        # Ordenar por producción real
        datos_ordenados = sorted(datos, key=lambda x: x[1]['produccion_real']['valor_monetario'])
        
        for maquina, valores in datos_ordenados:
            prod = valores['produccion']
            prod_neta = valores['produccion_neta']
            gastos = valores['gastos']
            prod_real = valores['produccion_real']
            
            fila = f"""<tr data-maquina="{maquina}">
                    <td>{maquina}</td>
                    <td>{self._formatear_numero(prod['mt3'], 0)} MT3, {self._formatear_numero(prod['horas_trabajadas'], 0)} H</td>
                    <td>{self._formatear_moneda(prod_neta['valor_monetario'])}</td>
                    <td>{self._formatear_moneda(gastos['total'])}</td>
                    <td class="{self._get_clase_prod_real(prod_real['valor_monetario'])}">{self._formatear_moneda(prod_real['valor_monetario'])}</td>
                </tr>"""
            filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_filas_resumen_trimestral(self, datos_por_maquina: Dict[str, Dict[int, Dict]]) -> str:
        """Genera las filas de la tabla de resumen trimestral."""
        filas = []
        
        # Calcular totales por máquina
        totales_por_maquina = {}
        for maquina, datos_por_mes in datos_por_maquina.items():
            total_prod = {'mt3': Decimal('0'), 'horas': Decimal('0')}
            total_prod_neta = Decimal('0')
            total_gastos = Decimal('0')
            total_prod_real = Decimal('0')
            
            for mes, valores in datos_por_mes.items():
                prod = valores['produccion']
                prod_neta = valores['produccion_neta']
                gastos = valores['gastos']
                prod_real = valores['produccion_real']
                
                total_prod['mt3'] += prod['mt3']
                total_prod['horas'] += prod['horas_trabajadas']
                total_prod_neta += prod_neta['valor_monetario']
                total_gastos += gastos['total']
                total_prod_real += prod_real['valor_monetario']
            
            totales_por_maquina[maquina] = {
                'total_prod': total_prod,
                'total_prod_neta': total_prod_neta,
                'total_gastos': total_gastos,
                'total_prod_real': {'valor_monetario': total_prod_real}
            }
        
        # Ordenar por producción real
        maquinas_ordenadas = sorted(totales_por_maquina.keys(), key=lambda m: totales_por_maquina[m]['total_prod_real']['valor_monetario'])  # type: ignore
        
        for maquina in maquinas_ordenadas:
            total = totales_por_maquina[maquina]  # type: Dict[str, Any]
            
            fila = f"""<tr data-maquina="{maquina}">
                    <td>{maquina}</td>
                    <td>{self._formatear_numero(total['total_prod']['mt3'], 0)} MT3, {self._formatear_numero(total['total_prod']['horas'], 0)} H</td>
                    <td>{self._formatear_moneda(total['total_prod_neta'])}</td>
                    <td>{self._formatear_moneda(total['total_gastos'])}</td>
                    <td class="{self._get_clase_prod_real(total['total_prod_real']['valor_monetario'])}">{self._formatear_moneda(total['total_prod_real']['valor_monetario'])}</td>
                </tr>"""
            filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_filas_produccion(self, datos_por_maquina: Dict[str, Dict[int, Dict]]) -> str:
        """Genera las filas de la tabla de producción."""
        filas = []
        
        for maquina, datos_por_mes in datos_por_maquina.items():
            for mes, valores in datos_por_mes.items():
                prod = valores['produccion']
                
                fila = f"""<tr data-maquina="{maquina}" data-mes="{mes}">
                        <td>{maquina}</td>
                        <td>{self.MESES[int(mes)]}</td>
                        <td>{self._formatear_numero(prod['mt3'], 0)}</td>
                        <td>{self._formatear_numero(prod['horas_trabajadas'], 0)}</td>
                        <td>{self._formatear_numero(prod['kilometros'], 0)}</td>
                        <td>{self._formatear_numero(prod['vueltas'], 0)}</td>
                    </tr>"""
                filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_filas_gastos(self, datos_por_maquina: Dict[str, Dict[int, Dict]], incluir_gastos_operacionales: bool) -> str:
        """Genera las filas de la tabla de gastos."""
        filas = []
        
        for maquina, datos_por_mes in datos_por_maquina.items():
            for mes, valores in datos_por_mes.items():
                gastos = valores['gastos']
                
                fila = f"""<tr data-maquina="{maquina}" data-mes="{mes}">
                        <td>{maquina}</td>
                        <td>{self.MESES[int(mes)]}</td>
                        <td>{self._formatear_moneda(gastos.get('repuestos', Decimal('0')))}</td>
                        <td>{self._formatear_numero(gastos.get('horas_hombre', Decimal('0')), 0)}</td>
                        <td>{self._formatear_moneda(gastos.get('costo_hh', Decimal('0')))}</td>
                        <td>{self._formatear_moneda(gastos.get('leasing', Decimal('0')))}</td>
                        <td>{self._formatear_moneda(gastos.get('total', Decimal('0')))}</td>
                    </tr>"""
                filas.append(fila)
        
        return '\n'.join(filas)
    
    def _generar_datos_graficos(self, datos_por_maquina: Dict[str, Dict[int, Dict]], incluir_gastos_operacionales: bool) -> str:
        """Genera el código JavaScript para los gráficos."""
        
        # Calcular datos por mes para gráficos
        gastos_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        repuestos_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        costo_hh_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        leasing_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        
        valor_mt3_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        valor_horas_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        valor_km_por_mes = {10: 0.0, 11: 0.0, 12: 0.0}
        
        for datos_por_mes in datos_por_maquina.values():
            for mes, valores in datos_por_mes.items():
                gastos = valores['gastos']
                prod = valores['produccion']
                
                gastos_por_mes[mes] += float(gastos.get('total', 0))
                repuestos_por_mes[mes] += float(gastos.get('repuestos', 0))
                costo_hh_por_mes[mes] += float(gastos.get('costo_hh', 0))
                leasing_por_mes[mes] += float(gastos.get('leasing', 0))
                
                valor_mt3_por_mes[mes] += float(prod.get('valor_mt3', 0))
                valor_horas_por_mes[mes] += float(prod.get('valor_horas', 0))
                valor_km_por_mes[mes] += float(prod.get('valor_km', 0))
        
        # Generar código JavaScript
        js = f"""
        const gastosPorMes = {json.dumps(gastos_por_mes)};
        const repuestosPorMes = {json.dumps(repuestos_por_mes)};
        const costoHHPorMes = {json.dumps(costo_hh_por_mes)};
        const leasingPorMes = {json.dumps(leasing_por_mes)};
        
        const valorMT3PorMes = {json.dumps(valor_mt3_por_mes)};
        const valorHorasPorMes = {json.dumps(valor_horas_por_mes)};
        const valorKmPorMes = {json.dumps(valor_km_por_mes)};
        
        const ctxGastos = document.getElementById('chartGastos').getContext('2d');
        new Chart(ctxGastos, {{
            type: 'bar',
            data: {{
                labels: meses,
                datasets: [
                    {{
                        label: 'Repuestos',
                        data: meses.map(m => repuestosPorMes[m] || 0),
                        backgroundColor: 'rgba(255, 99, 132, 0.6)'
                    }},
                    {{
                        label: 'Costo Horas Hombre',
                        data: meses.map(m => costoHHPorMes[m] || 0),
                        backgroundColor: 'rgba(54, 162, 235, 0.6)'
                    }},
                    {{
                        label: 'Leasing',
                        data: meses.map(m => leasingPorMes[m] || 0),
                        backgroundColor: 'rgba(255, 206, 86, 0.6)'
                    }}
                ]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Gastos por Mes (CLP)'
                    }},
                    legend: {{
                        display: true
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
        
        const ctxProduccion = document.getElementById('chartProduccion').getContext('2d');
        
        const datasets = [];
        
        if (Object.values(valorMT3PorMes).some(v => v > 0)) {{
            datasets.push({{
                label: 'MT3 ($)',
                data: meses.map(m => valorMT3PorMes[m] || 0),
                borderColor: 'rgba(75, 192, 192, 1)',
                backgroundColor: 'rgba(75, 192, 192, 0.2)',
                yAxisID: 'y'
            }});
        }}
        
        if (Object.values(valorHorasPorMes).some(v => v > 0)) {{
            datasets.push({{
                label: 'Horas ($)',
                data: meses.map(m => valorHorasPorMes[m] || 0),
                borderColor: 'rgba(153, 102, 255, 1)',
                backgroundColor: 'rgba(153, 102, 255, 0.2)',
                yAxisID: 'y'
            }});
        }}
        
        if (Object.values(valorKmPorMes).some(v => v > 0)) {{
            datasets.push({{
                label: 'Km ($)',
                data: meses.map(m => valorKmPorMes[m] || 0),
                borderColor: 'rgba(255, 99, 132, 1)',
                backgroundColor: 'rgba(255, 99, 132, 0.2)',
                yAxisID: 'y'
            }});
        }}
        
        new Chart(ctxProduccion, {{
            type: 'line',
            data: {{
                labels: meses,
                datasets: datasets
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    title: {{
                        display: true,
                        text: 'Producción por Mes (Valores Monetarios)'
                    }}
                }},
                scales: {{
                    y: {{
                        type: 'linear',
                        display: true,
                        position: 'left',
                        beginAtZero: true,
                        title: {{
                            display: true,
                            text: 'Valor ($ CLP)'
                        }},
                        ticks: {{
                            callback: function(value) {{
                                return '$' + value.toLocaleString('es-CL');
                            }}
                        }}
                    }}
                }}
            }}
        }});
"""
        return js
    
    def _get_clase_prod_real(self, valor: Decimal) -> str:
        """Obtiene la clase CSS para el valor de producción real."""
        if valor > 0:
            return 'positive'
        elif valor < 0:
            return 'negative'
        else:
            return ''
    
    def _generar_tabla_gastos_mensual(self, datos_por_mes: Dict[int, List[Tuple[str, Dict]]], incluir_gastos_operacionales: bool) -> str:
        """Genera una tabla HTML estática con el resumen de gastos por mes."""
        
        # Calcular totales por mes
        totales_por_mes = {10: {'repuestos': Decimal('0'), 'horas_hombre': Decimal('0'), 'costo_hh': Decimal('0'), 'leasing': Decimal('0'), 'total': Decimal('0')},
                          11: {'repuestos': Decimal('0'), 'horas_hombre': Decimal('0'), 'costo_hh': Decimal('0'), 'leasing': Decimal('0'), 'total': Decimal('0')},
                          12: {'repuestos': Decimal('0'), 'horas_hombre': Decimal('0'), 'costo_hh': Decimal('0'), 'leasing': Decimal('0'), 'total': Decimal('0')}}
        
        for mes, datos in datos_por_mes.items():
            for maquina, valores in datos:
                gastos = valores['gastos']
                totales_por_mes[mes]['repuestos'] += gastos.get('repuestos', Decimal('0'))
                totales_por_mes[mes]['horas_hombre'] += gastos.get('horas_hombre', Decimal('0'))
                totales_por_mes[mes]['costo_hh'] += gastos.get('costo_hh', Decimal('0'))
                totales_por_mes[mes]['leasing'] += gastos.get('leasing', Decimal('0'))
                totales_por_mes[mes]['total'] += gastos.get('total', Decimal('0'))
        
        # Generar filas de la tabla
        filas = []
        for mes in [10, 11, 12]:
            totales = totales_por_mes[mes]
            fila = f"""<tr>
                    <td>{self.MESES[mes]}</td>
                    <td>{self._formatear_moneda(totales['repuestos'])}</td>
                    <td>{self._formatear_numero(totales['horas_hombre'], 0)}</td>
                    <td>{self._formatear_moneda(totales['costo_hh'])}</td>
                    <td>{self._formatear_moneda(totales['leasing'])}</td>
                    <td>{self._formatear_moneda(totales['total'])}</td>
                </tr>"""
            filas.append(fila)
        
        tabla = f"""<table style="margin-top: 20px;">
            <thead>
                <tr>
                    <th>Mes</th>
                    <th>Repuestos</th>
                    <th>Horas Hombre</th>
                    <th>Costo HH</th>
                    <th>Leasing</th>
                    <th>Total Gastos</th>
                </tr>
            </thead>
            <tbody>
                {''.join(filas)}
            </tbody>
        </table>"""
        
        return tabla
