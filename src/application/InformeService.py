"""
Servicio de aplicación: InformeService

Orquesta el proceso completo de generación de informes.
Sigue el principio de responsabilidad única (SRP) y separación de concerns.
"""

from typing import List, Optional
from decimal import Decimal
from pathlib import Path

from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.entities.GastoOperacional import GastoOperacional
from src.infrastructure.csv.ProduccionCSVReader import ProduccionCSVReader
from src.infrastructure.csv.HorasHombreCSVReader import HorasHombreCSVReader
from src.infrastructure.csv.RepuestosCSVReader import RepuestosCSVReader
from src.infrastructure.csv.LeasingCSVReader import LeasingCSVReader
from src.infrastructure.csv.ReportesContablesReader import ReportesContablesReader
from src.infrastructure.export.ExcelExporter import ExcelExporter
from src.infrastructure.export.HTMLExporter import HTMLExporter
from src.domain.services.CalculadorGastos import CalculadorGastos


class InformeService:
    """
    Servicio principal que orquesta la generación de informes.
    
    Coordina la lectura de datos, procesamiento y exportación.
    """
    
    def __init__(
        self,
        ruta_produccion: str,
        ruta_horas_hombre: str,
        ruta_repuestos: str,
        ruta_leasing: Optional[str] = None,
        ruta_gastos: Optional[str] = None,
        valor_uf: Optional[Decimal] = None
    ):
        """
        Inicializa el servicio con las rutas de los archivos.
        
        Args:
            ruta_produccion: Ruta al archivo CSV de producción
            ruta_horas_hombre: Ruta al archivo CSV de horas hombre
            ruta_repuestos: Ruta al archivo CSV de repuestos (DATABODEGA)
            ruta_leasing: Ruta al archivo CSV de leasing (opcional)
            ruta_gastos: Ruta a la carpeta de gastos con reportes contables
            valor_uf: Valor de la UF en pesos chilenos (opcional)
        """
        self.ruta_produccion = ruta_produccion
        self.ruta_horas_hombre = ruta_horas_hombre
        self.ruta_repuestos = ruta_repuestos
        self.ruta_leasing = ruta_leasing
        self.ruta_gastos = ruta_gastos
        self.valor_uf = valor_uf
    
    def _es_gasto_taller(self, gasto: GastoOperacional) -> bool:
        """
        Determina si un gasto operacional pertenece a TALLER.
        
        Args:
            gasto: Gasto operacional a evaluar
            
        Returns:
            True si el gasto es de TALLER, False en caso contrario
        """
        # Criterio 1: Origen es taller.csv
        if gasto.origen.lower() == 'taller.csv':
            return True
        
        # Criterio 2: Código de máquina contiene 'TALLER' (case-insensitive)
        if gasto.codigo_maquina and 'TALLER' in gasto.codigo_maquina.upper():
            return True
        
        return False
    
    def _filtrar_taller(
        self, 
        gastos_operacionales: List[GastoOperacional]
    ) -> tuple[List[GastoOperacional], List[GastoOperacional]]:
        """
        Filtra los gastos operacionales separando los de TALLER.
        
        Args:
            gastos_operacionales: Lista completa de gastos operacionales
            
        Returns:
            Tupla con (gastos_sin_taller, gastos_taller)
        """
        gastos_sin_taller = []
        gastos_taller = []
        
        for gasto in gastos_operacionales:
            if self._es_gasto_taller(gasto):
                gastos_taller.append(gasto)
            else:
                gastos_sin_taller.append(gasto)
        
        return gastos_sin_taller, gastos_taller
    
    def leer_datos(self) -> tuple[
        List[Produccion], 
        List[HorasHombre], 
        List[Repuesto], 
        List[Leasing],
        List[GastoOperacional]
    ]:
        """
        Lee todos los datos de los archivos CSV.
        
        Returns:
            Tupla con (producciones, horas_hombre, repuestos, leasing, gastos_operacionales)
        """
        print("Leyendo datos de producción...")
        reader_prod = ProduccionCSVReader(self.ruta_produccion, valor_uf=self.valor_uf)
        producciones = reader_prod.leer()
        print(f"  - {len(producciones)} registros de producción leídos")
        
        print("Leyendo datos de horas hombre...")
        reader_hh = HorasHombreCSVReader(self.ruta_horas_hombre)
        horas_hombre = reader_hh.leer()
        print(f"  - {len(horas_hombre)} registros de horas hombre leídos")
        
        print("Leyendo datos de repuestos (DATABODEGA)...")
        reader_rep = RepuestosCSVReader(self.ruta_repuestos)
        repuestos = reader_rep.leer()
        print(f"  - {len(repuestos)} registros de repuestos leídos")
        
        leasing = []
        if self.ruta_leasing:
            print("Leyendo datos de leasing...")
            try:
                reader_lease = LeasingCSVReader(self.ruta_leasing)
                leasing = reader_lease.leer()
                print(f"  - {len(leasing)} registros de leasing leídos")
            except FileNotFoundError:
                print(f"  - [WARNING] Archivo de leasing no encontrado: {self.ruta_leasing}")
        else:
            print("  - No se proporcionó ruta de leasing, se omitirá este gasto")
        
        gastos_operacionales = []
        if self.ruta_gastos:
            print("Leyendo datos de gastos operacionales (reportes contables)...")
            try:
                reader_gastos = ReportesContablesReader(self.ruta_gastos)
                gastos_operacionales_todos = reader_gastos.leer_todos_filtrados()
                print(f"  - {len(gastos_operacionales_todos)} registros de gastos operacionales leídos")
                
                # Filtrar gastos de TALLER (excluir del informe principal)
                gastos_operacionales, gastos_taller = self._filtrar_taller(gastos_operacionales_todos)
                print(f"  - {len(gastos_operacionales)} registros incluidos en informe principal (excluidos {len(gastos_taller)} de TALLER)")
                if gastos_taller:
                    total_taller = sum(g.monto for g in gastos_taller)
                    print(f"  - Monto total excluido de TALLER: ${total_taller:,.0f}")
            except Exception as e:
                print(f"  - [WARNING] Error leyendo gastos operacionales: {e}")
        else:
            print("  - No se proporcionó ruta de gastos, solo se usarán datos de DATABODEGA")
        
        return producciones, horas_hombre, repuestos, leasing, gastos_operacionales
    
    def generar_informes(
        self,
        ruta_excel: str,
        ruta_html: str,
        producciones: Optional[List[Produccion]] = None,
        horas_hombre: Optional[List[HorasHombre]] = None,
        repuestos: Optional[List[Repuesto]] = None,
        leasing: Optional[List[Leasing]] = None,
        gastos_operacionales: Optional[List[GastoOperacional]] = None
    ):
        """
        Genera los informes en Excel y HTML.
        
        Args:
            ruta_excel: Ruta donde guardar el archivo Excel
            ruta_html: Ruta donde guardar el archivo HTML
            producciones: Lista de producciones (opcional, se leen si no se proporciona)
            horas_hombre: Lista de horas hombre (opcional, se leen si no se proporciona)
            repuestos: Lista de repuestos (opcional, se leen si no se proporciona)
            leasing: Lista de leasing (opcional, se leen si no se proporciona)
            gastos_operacionales: Lista de gastos operacionales (opcional, se leen si no se proporciona)
        """
        # Leer datos si no se proporcionan
        if producciones is None or horas_hombre is None or repuestos is None or gastos_operacionales is None:
            producciones, horas_hombre, repuestos, leasing, gastos_operacionales = self.leer_datos()
        else:
            # Si se proporcionan gastos operacionales directamente, también filtrar TALLER
            if gastos_operacionales:
                gastos_operacionales, gastos_taller = self._filtrar_taller(gastos_operacionales)
                if gastos_taller:
                    print(f"  - [INFO] Excluidos {len(gastos_taller)} registros de TALLER del informe principal")
        
        # Generar Excel
        print("\nGenerando informe Excel...")
        excel_exporter = ExcelExporter(ruta_excel)
        excel_exporter.exportar_completo(
            producciones, 
            repuestos, 
            horas_hombre, 
            gastos_operacionales,
            leasing
        )
        print(f"  - Archivo Excel generado: {ruta_excel}")
        
        # Generar HTML
        print("\nGenerando informe HTML...")
        html_exporter = HTMLExporter(ruta_html)
        html_exporter.exportar_completo(
            producciones,
            repuestos,
            horas_hombre,
            gastos_operacionales,
            leasing
        )
        print(f"  - Archivo HTML generado: {ruta_html}")
        
        print("\n[OK] Informes generados exitosamente!")
