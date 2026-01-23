"""
Lector CSV para datos de reportes contables.

Lee todos los archivos CSV de reportes contables (camiones.csv, vehiculos.csv, etc.)
y consolida los gastos operacionales por tipo y máquina.
"""

import csv
from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional
from pathlib import Path
import re

from src.domain.entities.GastoOperacional import GastoOperacional, TipoGasto
from src.domain.services.NormalizadorMaquinas import NormalizadorMaquinas


class ReportesContablesReader:
    """
    Lector consolidado de archivos CSV de reportes contables.
    
    Lee todos los archivos CSV de la carpeta gastos/ que corresponden a reportes contables
    y consolida los gastos por tipo, mes y máquina.
    """
    
    MESES_FILTRO = [10, 11, 12]  # Octubre, Noviembre, Diciembre
    ANIO_FILTRO = 2025
    
    # Mapeo de meses en español
    MESES_MAP = {
        'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4,
        'mayo': 5, 'junio': 6, 'julio': 7, 'agosto': 8,
        'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
    }
    
    # Archivos a excluir (no son reportes contables)
    ARCHIVOS_EXCLUIDOS = {
        'DATABODEGA.csv',
        '_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv',
        'Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv',
        'Leasing Credito HMAQ.csv'
    }
    
    def __init__(self, carpeta_gastos: str):
        """
        Inicializa el lector con la ruta de la carpeta de gastos.
        
        Args:
            carpeta_gastos: Ruta a la carpeta que contiene los CSV de gastos
        """
        self.carpeta_gastos = Path(carpeta_gastos)
        if not self.carpeta_gastos.exists():
            raise FileNotFoundError(f"La carpeta no existe: {carpeta_gastos}")
    
    def _parsear_fecha(self, dia: int, mes: int) -> Optional[date]:
        """Crea un objeto datetime a partir de día y mes."""
        try:
            return datetime(self.ANIO_FILTRO, mes, dia).date()
        except (ValueError, TypeError):
            return None
    
    def _parsear_monto(self, monto_str: str) -> Decimal:
        """Parsea un monto con formato chileno."""
        if not monto_str or monto_str.strip() == '':
            return Decimal('0')
        
        try:
            monto_limpio = monto_str.strip().replace(' ', '')
            
            # Formato chileno: puntos como separadores de miles, coma como decimal
            # Ejemplos: 2.700.000 (dos millones setecientos mil), 78.384 (setenta y ocho mil trescientos ochenta y cuatro)
            
            # Si hay coma, es el separador decimal
            if ',' in monto_limpio:
                monto_limpio = monto_limpio.replace('.', '').replace(',', '.')
            else:
                # Si no hay coma, los puntos son separadores de miles
                monto_limpio = monto_limpio.replace('.', '')
            
            # Verificar que sea un número válido
            if not monto_limpio.replace('.', '', 1).isdigit():
                return Decimal('0')
            
            return Decimal(monto_limpio)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _leer_archivo_contable(self, ruta_archivo: Path) -> List[GastoOperacional]:
        """Lee un archivo CSV individual de reporte contable."""
        gastos = []
        
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
                    for campo in campos[1:]:
                        if campo.strip():
                            centro_costo_actual = campo.strip()
                            codigo_maquina_actual = NormalizadorMaquinas.normalizar(centro_costo_actual) or ""
                            break
                    continue
                
                # Detectar línea de Cuenta
                if campos and 'Cuenta' in campos[0]:
                    for campo in campos[1:]:
                        if campo.strip():
                            cuenta_actual = campo.strip()
                            match = re.match(r'(\d+)', cuenta_actual)
                            if match:       
                                codigo_cuenta_actual = match.group(1)
                            break
                    continue
                
                # Detectar línea de datos (tiene Día y Mes)
                if len(campos) > 5:
                    dia_str = campos[0].strip()
                    mes_str = ""
                    
                    for i, campo in enumerate(campos[1:8], 1):
                        if campo.strip().lower() in self.MESES_MAP:
                            mes_str = campo.strip().lower()
                            break
                    
                    if dia_str.isdigit() and mes_str in self.MESES_MAP:
                        dia = int(dia_str)
                        mes = self.MESES_MAP[mes_str]
                        
                        fecha = self._parsear_fecha(dia, mes)
                        if not fecha:
                            continue
                        
                        glosa = ""
                        for campo in campos[9:14]:
                            if campo.strip() and not campo.strip().replace('.', '').replace(',', '').replace('-', '').isdigit():
                                glosa = campo.strip()
                                break
                        
                        perdida = Decimal('0')
                        ganancia = Decimal('0')
                        
                        for i, campo in enumerate(campos[10:]):
                            monto = self._parsear_monto(campo)
                            if monto > 0:
                                if perdida == 0:
                                    perdida = monto
                                elif ganancia == 0:
                                    ganancia = monto
                                    break
                        
                        if perdida > 0:
                            gastos.append(GastoOperacional(
                                codigo_maquina=codigo_maquina_actual or centro_costo_actual,
                                fecha=fecha,
                                tipo_gasto=codigo_cuenta_actual,
                                glosa=glosa,
                                monto=perdida,
                                es_ingreso=False,
                                origen=ruta_archivo.name
                            ))
                        
                        if ganancia > 0:
                            gastos.append(GastoOperacional(
                                codigo_maquina=codigo_maquina_actual or centro_costo_actual,
                                fecha=fecha,
                                tipo_gasto=codigo_cuenta_actual,
                                glosa=glosa,
                                monto=ganancia,
                                es_ingreso=True,
                                origen=ruta_archivo.name
                            ))
            
            return gastos
        
        except Exception as e:
            print(f"[ERROR] Error leyendo {ruta_archivo.name}: {e}")
            return []
    
    def leer_todos(self) -> List[GastoOperacional]:
        """
        Lee todos los archivos CSV de reportes contables.
        
        Returns:
            Lista consolidada de todos los gastos operacionales
        """
        todos_gastos = []
        
        archivos_csv = [f for f in self.carpeta_gastos.glob("*.csv") 
                        if f.name not in self.ARCHIVOS_EXCLUIDOS]
        
        for ruta_archivo in sorted(archivos_csv):
            gastos_archivo = self._leer_archivo_contable(ruta_archivo)
            todos_gastos.extend(gastos_archivo)
        
        return todos_gastos
    
    def leer_todos_filtrados(self) -> List[GastoOperacional]:
        """
        Lee todos los gastos y filtra por período (Q4 2025).
        
        Returns:
            Lista de gastos filtrados por mes
        """
        todos_gastos = self.leer_todos()
        
        # Filtrar por mes
        gastos_filtrados = [g for g in todos_gastos if g.mes in self.MESES_FILTRO]
        
        return gastos_filtrados
