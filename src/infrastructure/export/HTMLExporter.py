"""
Exportador de datos a HTML.

Genera un archivo HTML con dashboard interactivo y gráficos.
Sigue el principio de responsabilidad única (SRP).
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple, List
import json

from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.services.CalculadorProduccionReal import CalculadorProduccionReal


class HTMLExporter:
    """
    Exporta los datos del informe a un archivo HTML.
    
    Crea un dashboard interactivo con:
    - Resumen ejecutivo
    - Gráficos de producción vs gastos
    - Tablas interactivas con filtros
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
        leasing: List[Leasing] = None
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
            producciones, repuestos, horas_hombre, leasing
        )
        
        # Generar HTML
        html = self._generar_html(datos, producciones, repuestos, horas_hombre)
        
        # Guardar archivo
        with open(self.ruta_salida, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generar_html(
        self,
        datos: Dict[Tuple[str, int], Dict],
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre]
    ) -> str:
        """Genera el contenido HTML completo."""
        
        # Preparar datos para JavaScript
        datos_js = self._preparar_datos_js(datos)
        
        html = f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Producción vs Gastos - Q4 2025</title>
    <!-- Nota: Todos los valores monetarios mostrados son NETOS (sin IVA) -->
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
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
            min-width: 0; /* Permite que el contenido se ajuste */
            overflow: hidden; /* Evita que el contenido se salga */
            word-wrap: break-word; /* Permite que las palabras largas se dividan */
        }}
        
        .card h3 {{
            font-size: 0.9em;
            opacity: 0.9;
            margin-bottom: 10px;
            word-wrap: break-word;
            overflow-wrap: break-word;
        }}
        
        .card .value {{
            font-size: clamp(1.2em, 4vw, 2em); /* Tamaño responsivo */
            font-weight: bold;
            word-wrap: break-word;
            overflow-wrap: break-word;
            line-height: 1.2;
            max-width: 100%;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        /* Media queries para pantallas pequeñas */
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
        
        .filters {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
        }}
        
        .filters label {{
            margin-right: 15px;
            font-weight: 600;
        }}
        
        .filters select {{
            padding: 8px 15px;
            border: 1px solid #ddd;
            border-radius: 5px;
            font-size: 14px;
        }}
        
        .tabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #eee;
        }}
        
        .tab {{
            padding: 10px 20px;
            cursor: pointer;
            background: #f8f9fa;
            border: none;
            border-radius: 5px 5px 0 0;
            font-weight: 600;
            transition: all 0.3s;
        }}
        
        .tab:hover {{
            background: #e9ecef;
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
        
        .subtabs {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #ddd;
        }}
        
        .subtab {{
            padding: 8px 20px;
            cursor: pointer;
            background: #f0f0f0;
            border: none;
            border-radius: 5px 5px 0 0;
            font-weight: 500;
            font-size: 14px;
            transition: all 0.3s;
        }}
        
        .subtab:hover {{
            background: #e0e0e0;
        }}
        
        .subtab.active {{
            background: #4a90e2;
            color: white;
        }}
        
        .subtab-content {{
            display: none;
        }}
        
        .subtab-content.active {{
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
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Producción (MT3)</h3>
                <div class="value" id="total-mt3">0</div>
            </div>
            <div class="card">
                <h3>Total Horas Trabajadas</h3>
                <div class="value" id="total-horas">0</div>
            </div>
            <div class="card">
                <h3>Total Gastos</h3>
                <div class="value" id="total-gastos">$0</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Repuestos (sin IVA) + HH × $35.000 + Leasing (neto, IVA descontado)</p>
            </div>
            <div class="card">
                <h3>Total Producción Neta</h3>
                <div class="value" id="total-prod-neta">$0</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Valores netos (sin IVA)</p>
            </div>
            <div class="card">
                <h3>Total Producción Real</h3>
                <div class="value" id="total-prod-real">$0</div>
                <p style="font-size: 0.7em; margin-top: 5px; opacity: 0.8;">Prod. Neta - Gastos Totales (valores netos)</p>
            </div>
        </div>
        
        <div class="section">
            <h2>📈 Gráficos de Producción vs Gastos</h2>
            <div class="chart-container">
                <canvas id="chartGastos"></canvas>
            </div>
            <div class="chart-container">
                <canvas id="chartProduccion"></canvas>
            </div>
        </div>
        
        <div class="section">
            <div class="tabs">
                <button class="tab active" onclick="mostrarTab('resumen')">Resumen Trimestral</button>
                <button class="tab" onclick="mostrarTab('produccion')">Detalle Producción</button>
                <button class="tab" onclick="mostrarTab('gastos')">Detalle Gastos</button>
            </div>
            
            <div id="tab-resumen" class="tab-content active">
                <div class="filters">
                    <label>Filtrar por máquina:</label>
                    <select id="filtro-maquina-resumen" onchange="filtrarTablasResumen()">
                        <option value="">Todas las máquinas</option>
                    </select>
                </div>
                
                <div class="subtabs" style="margin-top: 20px;">
                    <button class="subtab active" onclick="mostrarSubTab('resumen-oct')">Octubre</button>
                    <button class="subtab" onclick="mostrarSubTab('resumen-nov')">Noviembre</button>
                    <button class="subtab" onclick="mostrarSubTab('resumen-dic')">Diciembre</button>
                    <button class="subtab" onclick="mostrarSubTab('resumen-trimestral')">Trimestral</button>
                </div>
                
                <div id="subtab-resumen-oct" class="subtab-content active">
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
                        <tbody id="tbody-resumen-oct">
                        </tbody>
                    </table>
                </div>
                
                <div id="subtab-resumen-nov" class="subtab-content">
                    <h3 style="margin-top: 20px; color: #333;">Noviembre 2025</h3>
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
                        <tbody id="tbody-resumen-nov">
                        </tbody>
                    </table>
                </div>
                
                <div id="subtab-resumen-dic" class="subtab-content">
                    <h3 style="margin-top: 20px; color: #333;">Diciembre 2025</h3>
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
                        <tbody id="tbody-resumen-dic">
                        </tbody>
                    </table>
                </div>
                
                <div id="subtab-resumen-trimestral" class="subtab-content">
                    <h3 style="margin-top: 20px; color: #333;">Resumen Trimestral (Total)</h3>
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
                        <tbody id="tbody-resumen-trimestral">
                        </tbody>
                    </table>
                </div>
            </div>
            
            <div id="tab-produccion" class="tab-content">
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
                    <tbody id="tbody-produccion">
                    </tbody>
                </table>
            </div>
            
            <div id="tab-gastos" class="tab-content">
                <div class="filters">
                    <label>Filtrar por máquina:</label>
                    <select id="filtro-maquina-gastos" onchange="filtrarTablaGastos()">
                        <option value="">Todas las máquinas</option>
                    </select>
                    <label style="margin-left: 20px;">Filtrar por mes:</label>
                    <select id="filtro-mes-gastos" onchange="filtrarTablaGastos()">
                        <option value="">Todos los meses</option>
                        <option value="10">Octubre</option>
                        <option value="11">Noviembre</option>
                        <option value="12">Diciembre</option>
                    </select>
                </div>
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
                    <tbody id="tbody-gastos">
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    
    <script>
        const datos = {json.dumps(datos_js, ensure_ascii=False)};
        
        // Calcular totales
        let totalMT3 = 0;
        let totalHoras = 0;
        let totalGastos = 0;
        let totalProdNeta = 0;
        let totalProdReal = 0;
        
        Object.values(datos).forEach(item => {{
            totalMT3 += parseFloat(item.produccion.mt3 || 0);
            totalHoras += parseFloat(item.produccion.horas_trabajadas || 0);
            totalGastos += parseFloat(item.gastos.total || 0);
            totalProdNeta += parseFloat(item.produccion_neta?.valor_monetario || 0);
            totalProdReal += parseFloat(item.produccion_real.valor_monetario || 0);
        }});
        
        // Función para ajustar tamaño de fuente si el número es muy largo
        function ajustarTamañoFuente(elementId, valor) {{
            const elemento = document.getElementById(elementId);
            const texto = valor.toString();
            // Si el texto es muy largo, reducir el tamaño de fuente
            if (texto.length > 15) {{
                elemento.style.fontSize = '1.3em';
            }} else if (texto.length > 12) {{
                elemento.style.fontSize = '1.5em';
            }} else {{
                elemento.style.fontSize = '';
            }}
        }}
        
        const totalMT3Str = totalMT3.toLocaleString('es-CL');
        const totalHorasStr = totalHoras.toLocaleString('es-CL');
        const totalGastosStr = '$' + totalGastos.toLocaleString('es-CL');
        const totalProdNetaStr = '$' + totalProdNeta.toLocaleString('es-CL');
        const totalProdRealStr = '$' + totalProdReal.toLocaleString('es-CL');
        
        document.getElementById('total-mt3').textContent = totalMT3Str;
        document.getElementById('total-horas').textContent = totalHorasStr;
        document.getElementById('total-gastos').textContent = totalGastosStr;
        document.getElementById('total-prod-neta').textContent = totalProdNetaStr;
        document.getElementById('total-prod-real').textContent = totalProdRealStr;
        
        // Ajustar tamaños de fuente para números largos
        ajustarTamañoFuente('total-mt3', totalMT3Str);
        ajustarTamañoFuente('total-horas', totalHorasStr);
        ajustarTamañoFuente('total-gastos', totalGastosStr);
        ajustarTamañoFuente('total-prod-neta', totalProdNetaStr);
        ajustarTamañoFuente('total-prod-real', totalProdRealStr);
        
        // Gráfico de gastos por mes
        const meses = ['Octubre', 'Noviembre', 'Diciembre'];
        const gastosPorMes = {{}};
        const repuestosPorMes = {{}};
        const costoHHPorMes = {{}};
        const leasingPorMes = {{}};
        
        Object.entries(datos).forEach(([key, item]) => {{
            const mes = key.split(',')[1];
            const mesNombre = meses[parseInt(mes) - 10];
            
            if (!gastosPorMes[mesNombre]) {{
                gastosPorMes[mesNombre] = 0;
                repuestosPorMes[mesNombre] = 0;
                costoHHPorMes[mesNombre] = 0;
                leasingPorMes[mesNombre] = 0;
            }}
            
            gastosPorMes[mesNombre] += parseFloat(item.gastos.total || 0);
            repuestosPorMes[mesNombre] += parseFloat(item.gastos.repuestos || 0);
            costoHHPorMes[mesNombre] += parseFloat(item.gastos.costo_hh || 0);
            leasingPorMes[mesNombre] += parseFloat(item.gastos.leasing || 0);
        }});
        
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
        
        // Gráfico de producción por mes - Valores monetarios por tipo
        const valorMT3PorMes = {{}};
        const valorHorasPorMes = {{}};
        const valorKmPorMes = {{}};
        const valorDiasPorMes = {{}};
        const valorVueltasPorMes = {{}};
        
        Object.entries(datos).forEach(([key, item]) => {{
            const mes = key.split(',')[1];
            const mesNombre = meses[parseInt(mes) - 10];
            
            if (!valorMT3PorMes[mesNombre]) {{
                valorMT3PorMes[mesNombre] = 0;
                valorHorasPorMes[mesNombre] = 0;
                valorKmPorMes[mesNombre] = 0;
                valorDiasPorMes[mesNombre] = 0;
                valorVueltasPorMes[mesNombre] = 0;
            }}
            
            valorMT3PorMes[mesNombre] += parseFloat(item.produccion.valor_mt3 || 0);
            valorHorasPorMes[mesNombre] += parseFloat(item.produccion.valor_horas || 0);
            valorKmPorMes[mesNombre] += parseFloat(item.produccion.valor_km || 0);
            valorDiasPorMes[mesNombre] += parseFloat(item.produccion.valor_dias || 0);
            valorVueltasPorMes[mesNombre] += parseFloat(item.produccion.valor_vueltas || 0);
        }});
        
        const ctxProduccion = document.getElementById('chartProduccion').getContext('2d');
        
        // Crear datasets solo para tipos que tienen valores
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
        
        if (Object.values(valorDiasPorMes).some(v => v > 0)) {{
            datasets.push({{
                label: 'Días ($)',
                data: meses.map(m => valorDiasPorMes[m] || 0),
                borderColor: 'rgba(255, 159, 64, 1)',
                backgroundColor: 'rgba(255, 159, 64, 0.2)',
                yAxisID: 'y'
            }});
        }}
        
        if (Object.values(valorVueltasPorMes).some(v => v > 0)) {{
            datasets.push({{
                label: 'Vueltas ($)',
                data: meses.map(m => valorVueltasPorMes[m] || 0),
                borderColor: 'rgba(255, 206, 86, 1)',
                backgroundColor: 'rgba(255, 206, 86, 0.2)',
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
        
        // Llenar tablas
        function llenarTablas() {{
            const tbodyResumenOct = document.getElementById('tbody-resumen-oct');
            const tbodyResumenNov = document.getElementById('tbody-resumen-nov');
            const tbodyResumenDic = document.getElementById('tbody-resumen-dic');
            const tbodyResumenTrimestral = document.getElementById('tbody-resumen-trimestral');
            const tbodyProduccion = document.getElementById('tbody-produccion');
            const tbodyGastos = document.getElementById('tbody-gastos');
            const selectMaquinaResumen = document.getElementById('filtro-maquina-resumen');
            const selectMaquinaGastos = document.getElementById('filtro-maquina-gastos');
            
            // Limpiar todas las tablas
            tbodyResumenOct.innerHTML = '';
            tbodyResumenNov.innerHTML = '';
            tbodyResumenDic.innerHTML = '';
            tbodyResumenTrimestral.innerHTML = '';
            tbodyProduccion.innerHTML = '';
            tbodyGastos.innerHTML = '';
            
            const maquinas = new Set();
            const datosPorMaquina = {{}};
            
            Object.entries(datos).forEach(([key, item]) => {{
                const [maquina, mes] = key.split(',');
                maquinas.add(maquina);
                
                if (!datosPorMaquina[maquina]) {{
                    datosPorMaquina[maquina] = {{}};
                }}
                datosPorMaquina[maquina][mes] = item;
            }});
            
            // Llenar selects de máquinas
            Array.from(maquinas).sort().forEach(maq => {{
                const option1 = document.createElement('option');
                option1.value = maq;
                option1.textContent = maq;
                selectMaquinaResumen.appendChild(option1);
                
                const option2 = document.createElement('option');
                option2.value = maq;
                option2.textContent = maq;
                selectMaquinaGastos.appendChild(option2);
            }});
            
            // Función para crear fila de tabla mensual
            function crearFilaMensual(maquina, item) {{
                const prod = item.produccion;
                const prodNeta = item.produccion_neta || {{valor_monetario: 0}};
                const gastos = item.gastos;
                const prodReal = item.produccion_real;
                
                const row = document.createElement('tr');
                row.dataset.maquina = maquina;
                row.innerHTML = `
                    <td>${{maquina}}</td>
                    <td>${{prod.mt3.toFixed(0)}} MT3, ${{prod.horas_trabajadas.toFixed(0)}} H</td>
                    <td>${{parseFloat(prodNeta.valor_monetario || 0).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(gastos.total).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(prodReal.valor_monetario).toLocaleString('es-CL')}}</td>
                `;
                return row;
            }}
            
            // Preparar datos para ordenar por producción real
            const maquinasConDatos = [];
            Array.from(maquinas).forEach(maq => {{
                let totalProdReal = 0;
                [10, 11, 12].forEach(mes => {{
                    const item = datosPorMaquina[maq]?.[mes];
                    if (item) {{
                        totalProdReal += parseFloat(item.produccion_real.valor_monetario);
                    }}
                }});
                maquinasConDatos.push({{maquina: maq, totalProdReal: totalProdReal}});
            }});
            
            // Ordenar por producción real (de menor a mayor)
            maquinasConDatos.sort((a, b) => a.totalProdReal - b.totalProdReal);
            
            // Llenar tablas mensuales
            maquinasConDatos.forEach(({{maquina: maq, totalProdReal}}) => {{
                // Octubre
                if (datosPorMaquina[maq]?.['10']) {{
                    const row = crearFilaMensual(maq, datosPorMaquina[maq]['10']);
                    tbodyResumenOct.appendChild(row);
                }}
                
                // Noviembre
                if (datosPorMaquina[maq]?.['11']) {{
                    const row = crearFilaMensual(maq, datosPorMaquina[maq]['11']);
                    tbodyResumenNov.appendChild(row);
                }}
                
                // Diciembre
                if (datosPorMaquina[maq]?.['12']) {{
                    const row = crearFilaMensual(maq, datosPorMaquina[maq]['12']);
                    tbodyResumenDic.appendChild(row);
                }}
                
                // Calcular totales trimestrales
                let totalProd = {{mt3: 0, horas: 0, km: 0}};
                let totalProdNeta = 0;
                let totalGastos = 0;
                let totalProdRealCalculado = 0;
                
                [10, 11, 12].forEach(mes => {{
                    const item = datosPorMaquina[maq]?.[mes];
                    if (item) {{
                        const prod = item.produccion;
                        const prodNeta = item.produccion_neta || {{valor_monetario: 0}};
                        const gastos = item.gastos;
                        const prodReal = item.produccion_real;
                        
                        totalProd.mt3 += parseFloat(prod.mt3);
                        totalProd.horas += parseFloat(prod.horas_trabajadas);
                        totalProdNeta += parseFloat(prodNeta.valor_monetario || 0);
                        totalGastos += parseFloat(gastos.total);
                        totalProdRealCalculado += parseFloat(prodReal.valor_monetario);
                    }}
                }});
                
                // Crear fila trimestral
                const rowTrimestral = document.createElement('tr');
                rowTrimestral.dataset.maquina = maq;
                rowTrimestral.innerHTML = `
                    <td>${{maq}}</td>
                    <td>${{totalProd.mt3.toFixed(0)}} MT3, ${{totalProd.horas.toFixed(0)}} H</td>
                    <td>${{totalProdNeta.toLocaleString('es-CL')}}</td>
                    <td>${{totalGastos.toLocaleString('es-CL')}}</td>
                    <td>${{totalProdRealCalculado.toLocaleString('es-CL')}}</td>
                `;
                tbodyResumenTrimestral.appendChild(rowTrimestral);
            }});
            
            // Llenar tabla producción
            Object.entries(datos).sort().forEach(([key, item]) => {{
                const [maquina, mes] = key.split(',');
                const row = document.createElement('tr');
                row.dataset.maquina = maquina;
                row.dataset.mes = mes;
                
                const prod = item.produccion;
                row.innerHTML = `
                    <td>${{maquina}}</td>
                    <td>${{meses[parseInt(mes) - 10]}}</td>
                    <td>${{parseFloat(prod.mt3).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(prod.horas_trabajadas).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(prod.kilometros).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(prod.vueltas).toLocaleString('es-CL')}}</td>
                `;
                tbodyProduccion.appendChild(row);
            }});
            
            // Llenar tabla gastos
            Object.entries(datos).sort().forEach(([key, item]) => {{
                const [maquina, mes] = key.split(',');
                const row = document.createElement('tr');
                row.dataset.maquina = maquina;
                row.dataset.mes = mes;
                
                const gastos = item.gastos;
                row.innerHTML = `
                    <td>${{maquina}}</td>
                    <td>${{meses[parseInt(mes) - 10]}}</td>
                    <td>${{parseFloat(gastos.repuestos || 0).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(gastos.horas_hombre || 0).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(gastos.costo_hh || 0).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(gastos.leasing || 0).toLocaleString('es-CL')}}</td>
                    <td>${{parseFloat(gastos.total || 0).toLocaleString('es-CL')}}</td>
                `;
                tbodyGastos.appendChild(row);
            }});
        }}
        
        function mostrarTab(tab) {{
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById('tab-' + tab).classList.add('active');
        }}
        
        function mostrarSubTab(subtab) {{
            document.querySelectorAll('.subtab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.subtab-content').forEach(t => t.classList.remove('active'));
            
            event.target.classList.add('active');
            document.getElementById('subtab-' + subtab).classList.add('active');
        }}
        
        function filtrarTablasResumen() {{
            const filtro = document.getElementById('filtro-maquina-resumen').value;
            const tablas = ['tbody-resumen-oct', 'tbody-resumen-nov', 'tbody-resumen-dic', 'tbody-resumen-trimestral'];
            
            tablas.forEach(tablaId => {{
                const rows = document.querySelectorAll('#' + tablaId + ' tr');
                rows.forEach(row => {{
                    if (!filtro || row.dataset.maquina === filtro) {{
                        row.style.display = '';
                    }} else {{
                        row.style.display = 'none';
                    }}
                }});
            }});
        }}
        
        function filtrarTablaGastos() {{
            const filtroMaquina = document.getElementById('filtro-maquina-gastos').value;
            const filtroMes = document.getElementById('filtro-mes-gastos').value;
            const rows = document.querySelectorAll('#tbody-gastos tr');
            
            rows.forEach(row => {{
                const matchMaquina = !filtroMaquina || row.dataset.maquina === filtroMaquina;
                const matchMes = !filtroMes || row.dataset.mes === filtroMes;
                
                if (matchMaquina && matchMes) {{
                    row.style.display = '';
                }} else {{
                    row.style.display = 'none';
                }}
            }});
        }}
        
        llenarTablas();
    </script>
</body>
</html>
"""
        return html
    
    def _preparar_datos_js(self, datos: Dict[Tuple[str, int], Dict]) -> Dict:
        """Prepara los datos en formato JSON para JavaScript."""
        datos_js = {}
        
        for (maquina, mes), valores in datos.items():
            clave = f"{maquina},{mes}"
            datos_js[clave] = {
                'produccion': {
                    'mt3': float(valores['produccion']['mt3']),
                    'horas_trabajadas': float(valores['produccion']['horas_trabajadas']),
                    'kilometros': float(valores['produccion']['kilometros']),
                    'vueltas': float(valores['produccion']['vueltas']),
                    'valor_mt3': float(valores['produccion'].get('valor_mt3', 0)),
                    'valor_horas': float(valores['produccion'].get('valor_horas', 0)),
                    'valor_km': float(valores['produccion'].get('valor_km', 0)),
                    'valor_dias': float(valores['produccion'].get('valor_dias', 0)),
                    'valor_vueltas': float(valores['produccion'].get('valor_vueltas', 0))
                },
                'gastos': {
                    'repuestos': float(valores['gastos']['repuestos']),
                    'horas_hombre': float(valores['gastos']['horas_hombre']),
                    'costo_hh': float(valores['gastos']['costo_hh']),
                    'leasing': float(valores['gastos'].get('leasing', 0)),
                    'total': float(valores['gastos']['total'])
                },
                'produccion_neta': {
                    'mt3': float(valores['produccion_neta']['mt3']),
                    'horas_trabajadas': float(valores['produccion_neta']['horas_trabajadas']),
                    'kilometros': float(valores['produccion_neta']['kilometros']),
                    'vueltas': float(valores['produccion_neta']['vueltas']),
                    'valor_monetario': float(valores['produccion_neta']['valor_monetario'])
                },
                'produccion_real': {
                    'mt3': float(valores['produccion_real']['mt3']),
                    'horas_trabajadas': float(valores['produccion_real']['horas_trabajadas']),
                    'kilometros': float(valores['produccion_real']['kilometros']),
                    'vueltas': float(valores['produccion_real']['vueltas']),
                    'valor_monetario': float(valores['produccion_real']['valor_monetario'])
                }
            }
        
        return datos_js
