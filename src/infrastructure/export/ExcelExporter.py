"""
Exportador de datos a Excel.

Genera un archivo Excel con múltiples hojas conteniendo los informes.
Sigue el principio de responsabilidad única (SRP).
"""

from decimal import Decimal
from pathlib import Path
from typing import Dict, Tuple, List

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from openpyxl.utils import get_column_letter

from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.services.CalculadorProduccionReal import CalculadorProduccionReal


class ExcelExporter:
    """
    Exporta los datos del informe a un archivo Excel.
    
    Crea un archivo con múltiples hojas:
    - Resumen Trimestral
    - Detalle Producción Mensual
    - Detalle Gastos Mensual
    - Desglose Repuestos
    - Desglose Horas Hombre
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
            ruta_salida: Ruta donde se guardará el archivo Excel
        """
        self.ruta_salida = Path(ruta_salida)
        self.workbook = openpyxl.Workbook()
        self._configurar_estilos()
    
    def _configurar_estilos(self):
        """Configura los estilos que se usarán en el Excel."""
        self.estilo_titulo = Font(bold=True, size=14)
        self.estilo_encabezado = Font(bold=True, size=11)
        self.estilo_moneda = Font(size=10)
        self.estilo_numero = Font(size=10)
        
        self.relleno_encabezado = PatternFill(
            start_color='366092',
            end_color='366092',
            fill_type='solid'
        )
        self.relleno_encabezado_font = Font(bold=True, color='FFFFFF', size=11)
        
        self.borde = Border(
            left=Side(style='thin'),
            right=Side(style='thin'),
            top=Side(style='thin'),
            bottom=Side(style='thin')
        )
    
    def _formatear_moneda(self, valor: Decimal) -> str:
        """Formatea un valor como moneda chilena."""
        return f"${valor:,.0f}".replace(',', '.')
    
    def _formatear_numero(self, valor: Decimal, decimales: int = 2) -> str:
        """Formatea un número con decimales."""
        return f"{valor:,.{decimales}f}".replace(',', '.')
    
    def _aplicar_estilo_encabezado(self, celda):
        """Aplica estilo de encabezado a una celda."""
        celda.font = self.relleno_encabezado_font
        celda.fill = self.relleno_encabezado
        celda.alignment = Alignment(horizontal='center', vertical='center')
        celda.border = self.borde
    
    def _aplicar_borde(self, celda):
        """Aplica borde a una celda."""
        celda.border = self.borde
    
    def exportar(
        self,
        producciones: List[Produccion],
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        leasing: List[Leasing] = None
    ):
        """
        Exporta todos los datos a Excel.
        
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
        
        # Crear hojas
        self._crear_hoja_resumen(datos)
        self._crear_hoja_detalle_produccion(datos)
        self._crear_hoja_detalle_gastos(datos)
        self._crear_hoja_desglose_repuestos(repuestos)
        self._crear_hoja_desglose_horas_hombre(horas_hombre)
        
        # Eliminar hoja por defecto si existe
        if 'Sheet' in self.workbook.sheetnames:
            del self.workbook['Sheet']
        
        # Guardar archivo
        self.workbook.save(self.ruta_salida)
    
    def _crear_hoja_resumen(self, datos: Dict[Tuple[str, int], Dict]):
        """Crea la hoja de resumen trimestral."""
        hoja = self.workbook.create_sheet("Resumen Trimestral")
        
        # Título
        hoja['A1'] = 'INFORME TRIMESTRAL - PRODUCCIÓN VS GASTOS'
        hoja['A1'].font = self.estilo_titulo
        hoja.merge_cells('A1:P1')
        
        # Nota sobre valores netos
        hoja['A2'] = 'NOTA: Todos los valores monetarios son NETOS (sin IVA). Leasing con IVA descontado (19%). Repuestos sin IVA.'
        hoja['A2'].font = Font(size=9, italic=True, color='666666')
        hoja.merge_cells('A2:P2')
        
        # Encabezados
        encabezados = [
            'Máquina', 'Producción Oct', 'Prod. Neta Oct', 'Gastos Oct', 'Prod. Real Oct',
            'Producción Nov', 'Prod. Neta Nov', 'Gastos Nov', 'Prod. Real Nov',
            'Producción Dic', 'Prod. Neta Dic', 'Gastos Dic', 'Prod. Real Dic',
            'Total Producción', 'Total Prod. Neta', 'Total Gastos', 'Total Prod. Real'
        ]
        
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(row=4, column=col)
            celda.value = encabezado
            self._aplicar_estilo_encabezado(celda)
        
        # Obtener todas las máquinas únicas y calcular producción real total por máquina
        maquinas_con_total = []
        for maquina in set(codigo for codigo, _ in datos.keys()):
            total_prod_real = Decimal('0')
            for mes in [10, 11, 12]:
                clave = (maquina, mes)
                if clave in datos:
                    total_prod_real += datos[clave]['produccion_real']['valor_monetario']
            maquinas_con_total.append((maquina, total_prod_real))
        
        # Ordenar por producción real (de menor a mayor)
        maquinas_ordenadas = sorted(maquinas_con_total, key=lambda x: x[1])
        
        fila = 5
        for maquina, _ in maquinas_ordenadas:
            # Calcular totales por máquina
            total_prod = {'mt3': Decimal('0'), 'horas_trabajadas': Decimal('0'),
                         'kilometros': Decimal('0'), 'vueltas': Decimal('0')}
            total_prod_neta = Decimal('0')
            total_gastos = Decimal('0')
            total_prod_real = Decimal('0')
            
            # Datos por mes
            datos_mes = {}
            for mes in [10, 11, 12]:
                clave = (maquina, mes)
                if clave in datos:
                    datos_mes[mes] = datos[clave]
                    prod = datos[clave]['produccion']
                    prod_neta = datos[clave]['produccion_neta']
                    gastos = datos[clave]['gastos']
                    prod_real = datos[clave]['produccion_real']
                    
                    total_prod['mt3'] += prod['mt3']
                    total_prod['horas_trabajadas'] += prod['horas_trabajadas']
                    total_prod['kilometros'] += prod['kilometros']
                    total_prod['vueltas'] += prod['vueltas']
                    total_prod_neta += prod_neta['valor_monetario']
                    total_gastos += gastos['total']
                    total_prod_real += prod_real['valor_monetario']
            
            # Escribir datos
            col = 1
            hoja.cell(row=fila, column=col, value=maquina)
            self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            for mes in [10, 11, 12]:
                col += 1
                if mes in datos_mes:
                    prod = datos_mes[mes]['produccion']
                    prod_str = f"MT3:{prod['mt3']:.0f} H:{prod['horas_trabajadas']:.0f} KM:{prod['kilometros']:.0f}"
                    hoja.cell(row=fila, column=col, value=prod_str)
                else:
                    hoja.cell(row=fila, column=col, value='-')
                self._aplicar_borde(hoja.cell(row=fila, column=col))
                
                col += 1
                if mes in datos_mes:
                    hoja.cell(row=fila, column=col, value=self._formatear_moneda(datos_mes[mes]['produccion_neta']['valor_monetario']))
                else:
                    hoja.cell(row=fila, column=col, value='-')
                self._aplicar_borde(hoja.cell(row=fila, column=col))
                
                col += 1
                if mes in datos_mes:
                    hoja.cell(row=fila, column=col, value=self._formatear_moneda(datos_mes[mes]['gastos']['total']))
                else:
                    hoja.cell(row=fila, column=col, value='-')
                self._aplicar_borde(hoja.cell(row=fila, column=col))
                
                col += 1
                if mes in datos_mes:
                    hoja.cell(row=fila, column=col, value=self._formatear_moneda(datos_mes[mes]['produccion_real']['valor_monetario']))
                else:
                    hoja.cell(row=fila, column=col, value='-')
                self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            # Totales
            col += 1
            total_prod_str = f"MT3:{total_prod['mt3']:.0f} H:{total_prod['horas_trabajadas']:.0f} KM:{total_prod['kilometros']:.0f}"
            hoja.cell(row=fila, column=col, value=total_prod_str)
            self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            col += 1
            hoja.cell(row=fila, column=col, value=self._formatear_moneda(total_prod_neta))
            self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            col += 1
            hoja.cell(row=fila, column=col, value=self._formatear_moneda(total_gastos))
            self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            col += 1
            hoja.cell(row=fila, column=col, value=self._formatear_moneda(total_prod_real))
            self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            fila += 1
        
        # Ajustar ancho de columnas
        hoja.column_dimensions['A'].width = 25
        for col in range(2, 17):
            hoja.column_dimensions[get_column_letter(col)].width = 18
    
    def _crear_hoja_detalle_produccion(self, datos: Dict[Tuple[str, int], Dict]):
        """Crea la hoja de detalle de producción mensual."""
        hoja = self.workbook.create_sheet("Detalle Producción")
        
        # Título
        hoja['A1'] = 'DETALLE PRODUCCIÓN MENSUAL'
        hoja['A1'].font = self.estilo_titulo
        hoja.merge_cells('A1:F1')
        
        # Nota sobre valores netos
        hoja['A2'] = 'NOTA: Valores de producción son NETOS (sin IVA)'
        hoja['A2'].font = Font(size=9, italic=True, color='666666')
        hoja.merge_cells('A2:F2')
        
        # Encabezados
        encabezados = ['Máquina', 'Mes', 'MT3', 'Horas Trabajadas', 'Kilómetros', 'Vueltas']
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(row=4, column=col)
            celda.value = encabezado
            self._aplicar_estilo_encabezado(celda)
        
        fila = 5
        for (maquina, mes), datos_mes in sorted(datos.items()):
            prod = datos_mes['produccion']
            
            hoja.cell(row=fila, column=1, value=maquina)
            hoja.cell(row=fila, column=2, value=self.MESES[mes])
            hoja.cell(row=fila, column=3, value=float(prod['mt3']))
            hoja.cell(row=fila, column=4, value=float(prod['horas_trabajadas']))
            hoja.cell(row=fila, column=5, value=float(prod['kilometros']))
            hoja.cell(row=fila, column=6, value=float(prod['vueltas']))
            
            for col in range(1, 7):
                self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            fila += 1
        
        # Ajustar ancho de columnas
        hoja.column_dimensions['A'].width = 25
        hoja.column_dimensions['B'].width = 15
        for col in range(3, 7):
            hoja.column_dimensions[get_column_letter(col)].width = 18
    
    def _crear_hoja_detalle_gastos(self, datos: Dict[Tuple[str, int], Dict]):
        """Crea la hoja de detalle de gastos mensual."""
        hoja = self.workbook.create_sheet("Detalle Gastos")
        
        # Título
        hoja['A1'] = 'DETALLE GASTOS MENSUAL'
        hoja['A1'].font = self.estilo_titulo
        hoja.merge_cells('A1:G1')
        
        # Nota sobre valores netos
        hoja['A2'] = 'NOTA: Valores NETOS (sin IVA). Leasing: IVA descontado. Repuestos: sin IVA.'
        hoja['A2'].font = Font(size=9, italic=True, color='666666')
        hoja.merge_cells('A2:G2')
        
        # Encabezados
        encabezados = ['Máquina', 'Mes', 'Repuestos', 'Horas Hombre', 'Costo HH', 'Leasing', 'Total Gastos']
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(row=3, column=col)
            celda.value = encabezado
            self._aplicar_estilo_encabezado(celda)
        
        fila = 4
        for (maquina, mes), datos_mes in sorted(datos.items()):
            gastos = datos_mes['gastos']
            
            hoja.cell(row=fila, column=1, value=maquina)
            hoja.cell(row=fila, column=2, value=self.MESES[mes])
            hoja.cell(row=fila, column=3, value=self._formatear_moneda(gastos['repuestos']))
            hoja.cell(row=fila, column=4, value=float(gastos['horas_hombre']))
            hoja.cell(row=fila, column=5, value=self._formatear_moneda(gastos['costo_hh']))
            hoja.cell(row=fila, column=6, value=self._formatear_moneda(gastos.get('leasing', Decimal('0'))))
            hoja.cell(row=fila, column=7, value=self._formatear_moneda(gastos['total']))
            
            for col in range(1, 8):
                self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            fila += 1
        
        # Ajustar ancho de columnas
        hoja.column_dimensions['A'].width = 25
        hoja.column_dimensions['B'].width = 15
        for col in range(3, 7):
            hoja.column_dimensions[get_column_letter(col)].width = 18
    
    def _crear_hoja_desglose_repuestos(self, repuestos: List[Repuesto]):
        """Crea la hoja de desglose de repuestos."""
        hoja = self.workbook.create_sheet("Desglose Repuestos")
        
        # Título
        hoja['A1'] = 'DESGLOSE REPUESTOS'
        hoja['A1'].font = self.estilo_titulo
        hoja.merge_cells('A1:G1')
        
        # Encabezados
        encabezados = ['Máquina', 'Fecha', 'Repuesto', 'Cantidad', 'Precio Unit.', 'Total', 'Asignado A']
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(row=3, column=col)
            celda.value = encabezado
            self._aplicar_estilo_encabezado(celda)
        
        fila = 4
        for repuesto in sorted(repuestos, key=lambda r: (r.codigo_maquina, r.fecha_salida)):
            hoja.cell(row=fila, column=1, value=repuesto.codigo_maquina)
            hoja.cell(row=fila, column=2, value=repuesto.fecha_salida.strftime('%d/%m/%Y'))
            hoja.cell(row=fila, column=3, value=repuesto.nombre)
            hoja.cell(row=fila, column=4, value=float(repuesto.cantidad))
            hoja.cell(row=fila, column=5, value=self._formatear_moneda(repuesto.precio_unitario))
            hoja.cell(row=fila, column=6, value=self._formatear_moneda(repuesto.total))
            hoja.cell(row=fila, column=7, value=repuesto.asignado_a)
            
            for col in range(1, 8):
                self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            fila += 1
        
        # Ajustar ancho de columnas
        hoja.column_dimensions['A'].width = 20
        hoja.column_dimensions['B'].width = 12
        hoja.column_dimensions['C'].width = 40
        for col in range(4, 8):
            hoja.column_dimensions[get_column_letter(col)].width = 15
    
    def _crear_hoja_desglose_horas_hombre(self, horas_hombre: List[HorasHombre]):
        """Crea la hoja de desglose de horas hombre."""
        hoja = self.workbook.create_sheet("Desglose Horas Hombre")
        
        # Título
        hoja['A1'] = 'DESGLOSE HORAS HOMBRE'
        hoja['A1'].font = self.estilo_titulo
        hoja.merge_cells('A1:F1')
        
        # Encabezados
        encabezados = ['Máquina', 'Fecha', 'Mecánico', 'Tipo Orden', 'Horas', 'Costo ($35.000/h)']
        for col, encabezado in enumerate(encabezados, start=1):
            celda = hoja.cell(row=3, column=col)
            celda.value = encabezado
            self._aplicar_estilo_encabezado(celda)
        
        fila = 4
        for hh in sorted(horas_hombre, key=lambda h: (h.codigo_maquina, h.fecha)):
            hoja.cell(row=fila, column=1, value=hh.codigo_maquina)
            hoja.cell(row=fila, column=2, value=hh.fecha.strftime('%d/%m/%Y'))
            hoja.cell(row=fila, column=3, value=hh.mecanico)
            hoja.cell(row=fila, column=4, value=hh.tipo_orden)
            hoja.cell(row=fila, column=5, value=float(hh.horas))
            hoja.cell(row=fila, column=6, value=self._formatear_moneda(hh.horas * Decimal('35000')))
            
            for col in range(1, 7):
                self._aplicar_borde(hoja.cell(row=fila, column=col))
            
            fila += 1
        
        # Ajustar ancho de columnas
        hoja.column_dimensions['A'].width = 20
        hoja.column_dimensions['B'].width = 12
        hoja.column_dimensions['C'].width = 30
        hoja.column_dimensions['D'].width = 15
        for col in range(5, 7):
            hoja.column_dimensions[get_column_letter(col)].width = 18
