"""
Lector CSV para datos de repuestos.

Lee el archivo DATABODEGA.csv y convierte los datos en entidades de dominio.
Sigue el principio de inversión de dependencias (DIP).
"""

import csv
import re
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pathlib import Path

from src.domain.entities.Repuesto import Repuesto
from src.domain.services.NormalizadorMaquinas import NormalizadorMaquinas


class RepuestosCSVReader:
    """
    Lector de archivos CSV de repuestos.
    
    Lee el archivo 'DATABODEGA.csv' y extrae los datos de repuestos utilizados.
    """
    
    MESES_FILTRO = [10, 11, 12]  # Octubre, Noviembre, Diciembre
    ANIO_FILTRO = 2025
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el lector con la ruta del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo CSV de repuestos
        """
        self.ruta_archivo = Path(ruta_archivo)
        if not self.ruta_archivo.exists():
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """
        Parsea una fecha en formato dd-mm-yyyy.
        
        Args:
            fecha_str: String con la fecha en formato dd-mm-yyyy
            
        Returns:
            Objeto datetime o None si no se puede parsear
        """
        try:
            return datetime.strptime(fecha_str.strip(), '%d-%m-%Y')
        except (ValueError, AttributeError):
            return None
    
    def _parsear_precio(self, precio_str: str) -> Decimal:
        """
        Parsea un precio removiendo símbolos de moneda y espacios.
        
        Args:
            precio_str: String con el precio (ej: "$ 5.380" o "$5.380")
            
        Returns:
            Decimal con el precio parseado o 0 si no es válido
        """
        if not precio_str or precio_str.strip() == '':
            return Decimal('0')
        
        try:
            # Remover símbolos de moneda, espacios y puntos de miles
            precio_limpio = precio_str.strip().replace('$', '').replace(' ', '')
            # Reemplazar punto de miles por nada, y coma decimal por punto
            precio_limpio = precio_limpio.replace('.', '').replace(',', '.')
            return Decimal(precio_limpio)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _parsear_cantidad(self, cantidad_str: str) -> Decimal:
        """
        Parsea una cantidad a Decimal.
        
        Args:
            cantidad_str: String con la cantidad
            
        Returns:
            Decimal con la cantidad parseada o 0 si no es válido
        """
        if not cantidad_str or cantidad_str.strip() == '':
            return Decimal('0')
        
        try:
            cantidad_limpio = cantidad_str.strip().replace(',', '.')
            return Decimal(cantidad_limpio)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _extraer_codigo_maquina(self, centro_costo: str) -> Optional[str]:
        """
        Extrae el código de máquina del centro de costo.
        
        El centro de costo puede tener formatos como:
        - "CT-12 CAMION IVECO TOLVA PDSF74"
        - "RX-06 RETROEXCAVADORA NH"
        
        Args:
            centro_costo: String con el centro de costo
            
        Returns:
            Código de máquina normalizado o None si no se encuentra
        """
        if not centro_costo or centro_costo.strip() == '':
            return None
        
        # Intentar normalizar directamente
        codigo = NormalizadorMaquinas.normalizar(centro_costo)
        if codigo:
            return codigo
        
        # Si no funciona, buscar patrón al inicio
        patron = re.compile(r'^([A-Z]+-\d+[A-Z0-9-]*)')
        match = patron.match(centro_costo.strip())
        if match:
            return match.group(1)
        
        return None
    
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
    
    def leer(self) -> List[Repuesto]:
        """
        Lee el archivo CSV y retorna una lista de entidades Repuesto.
        
        Returns:
            Lista de entidades Repuesto filtradas por mes
        """
        repuestos = []
        
        with open(self.ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            # Leer líneas hasta encontrar el encabezado real
            # (puede haber líneas de encabezado antes)
            lineas = archivo.readlines()
            archivo.seek(0)
            
            # Buscar la línea con el encabezado
            encabezado_encontrado = False
            for i, linea in enumerate(lineas):
                if 'Nombre' in linea and 'Fecha Salida' in linea:
                    # Saltar hasta esta línea
                    for _ in range(i):
                        archivo.readline()
                    encabezado_encontrado = True
                    break
            
            if not encabezado_encontrado:
                archivo.seek(0)
            
            lector = csv.DictReader(archivo, delimiter=';')
            
            for fila in lector:
                # Parsear fecha
                fecha_str = fila.get('Fecha Salida', '').strip()
                fecha = self._parsear_fecha(fecha_str)
                
                if not fecha or not self._filtrar_por_mes(fecha):
                    continue
                
                # Extraer código de máquina del centro de costo
                centro_costo = fila.get('Centro Costo(Salida)', '').strip()
                codigo_maquina = self._extraer_codigo_maquina(centro_costo)
                
                if not codigo_maquina:
                    continue
                
                # Extraer datos del repuesto
                nombre = fila.get('Nombre', '').strip()
                cantidad = self._parsear_cantidad(fila.get('Cantidad', '0'))
                precio_unitario = self._parsear_precio(fila.get(' Precio ', '0'))
                total = self._parsear_precio(fila.get(' Total ', '0'))
                asignado_a = fila.get('Asignado A', '').strip()
                
                # Si el total es 0 pero tenemos cantidad y precio, calcular
                if total == 0 and cantidad > 0 and precio_unitario > 0:
                    total = cantidad * precio_unitario
                
                if total <= 0:
                    continue
                
                # Crear entidad
                repuesto = Repuesto(
                    codigo_maquina=codigo_maquina,
                    fecha_salida=fecha,
                    nombre=nombre,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                    total=total,
                    asignado_a=asignado_a
                )
                
                repuestos.append(repuesto)
        
        return repuestos
