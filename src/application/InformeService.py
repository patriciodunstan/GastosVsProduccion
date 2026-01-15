"""
Servicio de aplicación: InformeService

Orquesta el proceso completo de generación de informes.
Sigue el principio de responsabilidad única (SRP) y separación de concerns.
"""

from typing import List, Optional
from decimal import Decimal

from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.infrastructure.csv.ProduccionCSVReader import ProduccionCSVReader
from src.infrastructure.csv.HorasHombreCSVReader import HorasHombreCSVReader
from src.infrastructure.csv.RepuestosCSVReader import RepuestosCSVReader
from src.infrastructure.csv.LeasingCSVReader import LeasingCSVReader
from src.infrastructure.export.ExcelExporter import ExcelExporter
from src.infrastructure.export.HTMLExporter import HTMLExporter


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
        valor_uf: Optional[Decimal] = None
    ):
        """
        Inicializa el servicio con las rutas de los archivos.
        
        Args:
            ruta_produccion: Ruta al archivo CSV de producción
            ruta_horas_hombre: Ruta al archivo CSV de horas hombre
            ruta_repuestos: Ruta al archivo CSV de repuestos
            ruta_leasing: Ruta al archivo CSV de leasing (opcional)
            valor_uf: Valor de la UF en pesos chilenos (opcional)
        """
        self.ruta_produccion = ruta_produccion
        self.ruta_horas_hombre = ruta_horas_hombre
        self.ruta_repuestos = ruta_repuestos
        self.ruta_leasing = ruta_leasing
        self.valor_uf = valor_uf
    
    def leer_datos(self) -> tuple[List[Produccion], List[HorasHombre], List[Repuesto], List[Leasing]]:
        """
        Lee todos los datos de los archivos CSV.
        
        Returns:
            Tupla con (producciones, horas_hombre, repuestos, leasing)
        """
        print("Leyendo datos de producción...")
        reader_prod = ProduccionCSVReader(self.ruta_produccion, valor_uf=self.valor_uf)
        producciones = reader_prod.leer()
        print(f"  - {len(producciones)} registros de producción leídos")
        
        print("Leyendo datos de horas hombre...")
        reader_hh = HorasHombreCSVReader(self.ruta_horas_hombre)
        horas_hombre = reader_hh.leer()
        print(f"  - {len(horas_hombre)} registros de horas hombre leídos")
        
        print("Leyendo datos de repuestos...")
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
                leasing = []
        else:
            print("  - No se proporcionó ruta de leasing, se omitirá este gasto")
        
        return producciones, horas_hombre, repuestos, leasing
    
    def generar_informes(
        self,
        ruta_excel: str,
        ruta_html: str,
        producciones: List[Produccion] = None,
        horas_hombre: List[HorasHombre] = None,
        repuestos: List[Repuesto] = None,
        leasing: List[Leasing] = None
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
        """
        # Leer datos si no se proporcionan
        if producciones is None or horas_hombre is None or repuestos is None or leasing is None:
            producciones, horas_hombre, repuestos, leasing = self.leer_datos()
        
        # Generar Excel
        print("\nGenerando informe Excel...")
        excel_exporter = ExcelExporter(ruta_excel)
        excel_exporter.exportar(producciones, repuestos, horas_hombre, leasing)
        print(f"  - Archivo Excel generado: {ruta_excel}")
        
        # Generar HTML
        print("\nGenerando informe HTML...")
        html_exporter = HTMLExporter(ruta_html)
        html_exporter.exportar(producciones, repuestos, horas_hombre, leasing)
        print(f"  - Archivo HTML generado: {ruta_html}")
        
        print("\n[OK] Informes generados exitosamente!")
