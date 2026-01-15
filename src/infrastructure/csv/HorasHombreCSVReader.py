"""
Lector CSV para datos de horas hombre.

Lee el archivo de horas hombre y convierte los datos en entidades de dominio.
Sigue el principio de inversión de dependencias (DIP).
"""

import csv
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pathlib import Path
import locale

from src.domain.entities.HorasHombre import HorasHombre
from src.domain.services.NormalizadorMaquinas import NormalizadorMaquinas


class HorasHombreCSVReader:
    """
    Lector de archivos CSV de horas hombre.
    
    Lee el archivo '_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv'
    y extrae los datos de horas hombre trabajadas.
    """
    
    MESES_FILTRO = [10, 11, 12]  # Octubre, Noviembre, Diciembre
    ANIO_FILTRO = 2025
    
    # Mapeo de meses en español a números
    MESES_ESPANOL = {
        'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
        'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
    }
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el lector con la ruta del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo CSV de horas hombre
        """
        self.ruta_archivo = Path(ruta_archivo)
        if not self.ruta_archivo.exists():
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """
        Parsea una fecha en formato "dd MMM yyyy" (ej: "31 dic 2025").
        
        Args:
            fecha_str: String con la fecha en formato español
            
        Returns:
            Objeto datetime o None si no se puede parsear
        """
        try:
            partes = fecha_str.strip().lower().split()
            if len(partes) != 3:
                return None
            
            dia = int(partes[0])
            mes_str = partes[1][:3]  # Primeros 3 caracteres del mes
            anio = int(partes[2])
            
            mes = self.MESES_ESPANOL.get(mes_str)
            if not mes:
                return None
            
            return datetime(anio, mes, dia)
        except (ValueError, IndexError, AttributeError):
            return None
    
    def _parsear_decimal(self, valor: str) -> Decimal:
        """
        Parsea un valor a Decimal.
        
        Args:
            valor: String con el valor numérico
            
        Returns:
            Decimal con el valor parseado o 0 si no es válido
        """
        if not valor or valor.strip() == '':
            return Decimal('0')
        
        try:
            valor_limpio = valor.strip().replace(',', '.')
            return Decimal(valor_limpio)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _filtrar_por_mes(self, fecha: datetime) -> bool:
        """
        Verifica si la fecha está en los meses filtrados.
        
        Args:
            fecha: Fecha a verificar
            
        Returns:
            True si la fecha está en octubre, noviembre o diciembre de 2025
        """
        return (fecha.year == self.ANIO_FILTRO and 
                fecha.month in self.MESES_FILTRO)
    
    def leer(self) -> List[HorasHombre]:
        """
        Lee el archivo CSV y retorna una lista de entidades HorasHombre.
        
        Returns:
            Lista de entidades HorasHombre filtradas por mes
        """
        horas_hombre = []
        
        with open(self.ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            
            for fila in lector:
                # Parsear fecha
                fecha_str = fila.get('FECHA_SALIDA', '').strip()
                fecha = self._parsear_fecha(fecha_str)
                
                if not fecha or not self._filtrar_por_mes(fecha):
                    continue
                
                # Normalizar código de máquina
                maquina = fila.get('MAQUINA', '').strip()
                codigo_maquina = NormalizadorMaquinas.normalizar(maquina)
                
                if not codigo_maquina:
                    continue
                
                # Extraer datos
                mecanico = fila.get('MECANICO', '').strip()
                tipo_orden = fila.get('TIPO_ORDEN', '').strip()
                horas_str = fila.get('HORAS HOMBRE', '0').strip()
                horas = self._parsear_decimal(horas_str)
                
                if horas <= 0:
                    continue
                
                # Crear entidad
                hh = HorasHombre(
                    codigo_maquina=codigo_maquina,
                    fecha=fecha,
                    mecanico=mecanico,
                    tipo_orden=tipo_orden,
                    horas=horas
                )
                
                horas_hombre.append(hh)
        
        return horas_hombre
