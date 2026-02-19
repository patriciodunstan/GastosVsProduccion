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
from src.infrastructure.export.HTMLExporterTaller import HTMLExporterTaller
from src.domain.services.CalculadorGastos import CalculadorGastos
from src.domain.services.PreciosContratoService import PreciosContratoService
from src.infrastructure.excel.PreciosContratoExcelReader import PreciosContratoExcelReader


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
        valor_uf: Optional[Decimal] = None,
        ruta_precios: Optional[str] = None
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
            ruta_precios: Ruta al archivo Excel de precios de contratos (opcional)
        """
        self.ruta_produccion = ruta_produccion
        self.ruta_horas_hombre = ruta_horas_hombre
        self.ruta_repuestos = ruta_repuestos
        self.ruta_leasing = ruta_leasing
        self.ruta_gastos = ruta_gastos
        self.valor_uf = valor_uf
        self.ruta_precios = ruta_precios

        # Inicializar servicio de precios si se proporciona ruta
        self._precios_service: Optional[PreciosContratoService] = None
        if ruta_precios:
            try:
                precios_reader = PreciosContratoExcelReader(ruta_precios)
                self._precios_service = PreciosContratoService(precios_reader)
                self._precios_service.cargar_precios()
                estadisticas = self._precios_service.get_estadisticas()
                print(f"  - Precios de contratos cargados: {estadisticas['total_contratos']} contratos")
                print(f"    * Con precio: {estadisticas['contratos_con_precio']}")
                print(f"    * Sin precio: {estadisticas['contratos_sin_precio']} (CRÍTICO)")
                print(f"    * Híbridos: {estadisticas['contratos_hibridos']}")
            except Exception as e:
                print(f"  - [WARNING] Error cargando precios de contratos: {e}")
                print(f"    Se usará lógica original (precio único)")
                self._precios_service = None
        else:
            print("  - [INFO] No se proporcionó archivo de precios, se usará lógica original")

        # Almacenar gastos de taller para informe separado
        self._gastos_taller: List[GastoOperacional] = []
        self._repuestos_taller: List[Repuesto] = []
        self._horas_hombre_taller: List[HorasHombre] = []
    
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
    
    def _es_repuesto_taller(self, repuesto: Repuesto) -> bool:
        """
        Determina si un repuesto pertenece a TALLER.
        
        Args:
            repuesto: Repuesto a evaluar
            
        Returns:
            True si el repuesto es de TALLER, False en caso contrario
        """
        if repuesto.codigo_maquina and 'TALLER' in repuesto.codigo_maquina.upper():
            return True
        return False
    
    def _es_hh_taller(self, hh: HorasHombre) -> bool:
        """
        Determina si una hora hombre pertenece a TALLER.
        
        Args:
            hh: Hora hombre a evaluar
            
        Returns:
            True si la HH es de TALLER, False en caso contrario
        """
        if hh.codigo_maquina and 'TALLER' in hh.codigo_maquina.upper():
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
    
    def _filtrar_repuestos_taller(
        self,
        repuestos: List[Repuesto]
    ) -> tuple[List[Repuesto], List[Repuesto]]:
        """
        Filtra los repuestos separando los de TALLER.
        
        Args:
            repuestos: Lista completa de repuestos
            
        Returns:
            Tupla con (repuestos_sin_taller, repuestos_taller)
        """
        repuestos_sin_taller = []
        repuestos_taller = []
        
        for repuesto in repuestos:
            if self._es_repuesto_taller(repuesto):
                repuestos_taller.append(repuesto)
            else:
                repuestos_sin_taller.append(repuesto)
        
        return repuestos_sin_taller, repuestos_taller
    
    def _filtrar_hh_taller(
        self,
        horas_hombre: List[HorasHombre]
    ) -> tuple[List[HorasHombre], List[HorasHombre]]:
        """
        Filtra las horas hombre separando las de TALLER.
        
        Args:
            horas_hombre: Lista completa de horas hombre
            
        Returns:
            Tupla con (hh_sin_taller, hh_taller)
        """
        hh_sin_taller = []
        hh_taller = []
        
        for hh in horas_hombre:
            if self._es_hh_taller(hh):
                hh_taller.append(hh)
            else:
                hh_sin_taller.append(hh)
        
        return hh_sin_taller, hh_taller
    
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
        reader_prod = ProduccionCSVReader(
            self.ruta_produccion,
            valor_uf=self.valor_uf,
            precios_service=self._precios_service  # Pasar servicio de precios
        )
        producciones = reader_prod.leer()
        print(f"  - {len(producciones)} registros de producción leídos")
        
        print("Leyendo datos de horas hombre...")
        reader_hh = HorasHombreCSVReader(self.ruta_horas_hombre)
        horas_hombre_todas = reader_hh.leer()
        print(f"  - {len(horas_hombre_todas)} registros de horas hombre leídos")
        
        # Filtrar HH de TALLER
        horas_hombre, self._horas_hombre_taller = self._filtrar_hh_taller(horas_hombre_todas)
        if self._horas_hombre_taller:
            print(f"  - {len(horas_hombre)} HH para máquinas, {len(self._horas_hombre_taller)} HH para TALLER")
        
        print("Leyendo datos de repuestos (DATABODEGA)...")
        reader_rep = RepuestosCSVReader(self.ruta_repuestos)
        repuestos_todos = reader_rep.leer()
        print(f"  - {len(repuestos_todos)} registros de repuestos leídos")
        
        # Filtrar repuestos de TALLER
        repuestos, self._repuestos_taller = self._filtrar_repuestos_taller(repuestos_todos)
        if self._repuestos_taller:
            total_rep_taller = sum(r.total for r in self._repuestos_taller)
            print(f"  - {len(repuestos)} repuestos para máquinas, {len(self._repuestos_taller)} para TALLER (${total_rep_taller:,.0f})")
        
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
                
                # Filtrar gastos de TALLER
                gastos_operacionales, self._gastos_taller = self._filtrar_taller(gastos_operacionales_todos)
                print(f"  - {len(gastos_operacionales)} registros para máquinas")
                if self._gastos_taller:
                    total_taller = sum(g.monto for g in self._gastos_taller)
                    print(f"  - {len(self._gastos_taller)} registros para TALLER (${total_taller:,.0f})")
            except Exception as e:
                print(f"  - [WARNING] Error leyendo gastos operacionales: {e}")
        else:
            print("  - No se proporcionó ruta de gastos, solo se usarán datos de DATABODEGA")
        
        return producciones, horas_hombre, repuestos, leasing, gastos_operacionales
    
    def generar_informes(
        self,
        ruta_excel: str,
        ruta_html: str,
        ruta_html_taller: Optional[str] = None,
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
            ruta_html: Ruta donde guardar el archivo HTML de máquinas
            ruta_html_taller: Ruta donde guardar el archivo HTML de TALLER (opcional)
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
                gastos_operacionales, self._gastos_taller = self._filtrar_taller(gastos_operacionales)
                if self._gastos_taller:
                    print(f"  - [INFO] Excluidos {len(self._gastos_taller)} registros de TALLER del informe principal")
        
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
        
        # Generar HTML de máquinas
        print("\nGenerando informe HTML de máquinas...")
        html_exporter = HTMLExporter(ruta_html)
        html_exporter.exportar_completo(
            producciones,
            repuestos,
            horas_hombre,
            gastos_operacionales,
            leasing
        )
        print(f"  - Archivo HTML generado: {ruta_html}")
        
        # Generar HTML de TALLER si hay datos
        if ruta_html_taller is None:
            # Generar ruta automática basada en ruta_html
            ruta_base = Path(ruta_html)
            ruta_html_taller = str(ruta_base.parent / f"{ruta_base.stem}_taller{ruta_base.suffix}")
        
        tiene_datos_taller = (
            self._gastos_taller or 
            self._repuestos_taller or 
            self._horas_hombre_taller
        )
        
        if tiene_datos_taller:
            print("\nGenerando informe HTML de TALLER...")
            html_exporter_taller = HTMLExporterTaller(ruta_html_taller)
            html_exporter_taller.exportar(
                self._gastos_taller,
                self._repuestos_taller,
                self._horas_hombre_taller
            )
            print(f"  - Archivo HTML TALLER generado: {ruta_html_taller}")
            
            # Mostrar resumen de taller
            total_gastos_taller = sum(g.monto for g in self._gastos_taller if not g.es_ingreso)
            total_repuestos_taller = sum(r.total for r in self._repuestos_taller)
            total_hh_taller = sum(hh.horas for hh in self._horas_hombre_taller)
            total_costo_hh_taller = total_hh_taller * Decimal('35000')
            total_taller = total_gastos_taller + total_repuestos_taller + total_costo_hh_taller
            
            print(f"\n  === RESUMEN TALLER ===")
            print(f"  - Gastos operacionales: ${total_gastos_taller:,.0f}")
            print(f"  - Repuestos: ${total_repuestos_taller:,.0f}")
            print(f"  - Horas hombre: {total_hh_taller} H (${total_costo_hh_taller:,.0f})")
            print(f"  - TOTAL TALLER: ${total_taller:,.0f}")
        else:
            print("\n  - [INFO] No hay datos de TALLER, no se generará informe separado")
        
        print("\n[OK] Informes generados exitosamente!")