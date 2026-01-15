"""
Lector CSV para datos de leasing.

Lee el archivo de leasing y convierte los datos en entidades de dominio.
Sigue el principio de inversión de dependencias (DIP).
"""

import csv
from decimal import Decimal
from typing import List
from pathlib import Path

from src.domain.entities.Leasing import Leasing
from src.domain.services.NormalizadorMaquinas import NormalizadorMaquinas


class LeasingCSVReader:
    """
    Lector de archivos CSV de leasing.
    
    Lee el archivo de leasing y extrae los datos de cuotas mensuales.
    """
    
    def __init__(self, ruta_archivo: str):
        """
        Inicializa el lector con la ruta del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo CSV de leasing
        """
        self.ruta_archivo = Path(ruta_archivo)
        if not self.ruta_archivo.exists():
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
    
    def _parsear_monto(self, monto_str: str) -> Decimal:
        """
        Parsea un monto removiendo símbolos de moneda y espacios.
        
        Args:
            monto_str: String con el monto (ej: "$5.751.445" o " $5.751.445 ")
            
        Returns:
            Decimal con el monto parseado o 0 si no es válido
        """
        if not monto_str or monto_str.strip() == '':
            return Decimal('0')
        
        try:
            # Remover símbolos de moneda, espacios y puntos de miles
            monto_limpio = monto_str.strip().replace('$', '').replace(' ', '')
            # Reemplazar punto de miles por nada, y coma decimal por punto
            monto_limpio = monto_limpio.replace('.', '').replace(',', '.')
            return Decimal(monto_limpio)
        except (ValueError, TypeError):
            return Decimal('0')
    
    def _normalizar_codigo_maquina(self, codigo_str: str) -> str:
        """
        Normaliza el código de máquina usando el normalizador.
        
        Args:
            codigo_str: String con el código de máquina (ej: "MN03", "EX16")
            
        Returns:
            Código de máquina normalizado o cadena vacía si no es válido
        """
        if not codigo_str or codigo_str.strip() == '':
            return ''
        
        codigo_limpio = codigo_str.strip()
        
        # Intentar normalizar directamente
        codigo_normalizado = NormalizadorMaquinas.normalizar(codigo_limpio)
        if codigo_normalizado:
            return codigo_normalizado
        
        # Si no funciona, devolver el código limpio
        return codigo_limpio
    
    def leer(self) -> List[Leasing]:
        """
        Lee el archivo CSV y retorna una lista de entidades Leasing.
        
        Solo incluye los leasing con estado VIGENTE.
        
        Returns:
            Lista de entidades Leasing vigentes
        """
        leasing_list = []
        
        with open(self.ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo, delimiter=';')
            
            for fila in lector:
                # Verificar que el estado sea VIGENTE
                estado = fila.get('ESTADO LEASSING', '').strip().upper()
                if estado != 'VIGENTE':
                    continue
                
                # Extraer código de máquina
                codigo_int = fila.get('CODIGO INT', '').strip()
                if not codigo_int or codigo_int == 'X':
                    continue
                
                codigo_maquina = self._normalizar_codigo_maquina(codigo_int)
                if not codigo_maquina:
                    continue
                
                # Parsear monto de cuota
                monto_str = fila.get('MONTO cuota Leasing', '').strip()
                monto_cuota_con_iva = self._parsear_monto(monto_str)
                
                if monto_cuota_con_iva <= 0:
                    continue
                
                # Descontar IVA (19%): El archivo tiene valores con IVA, necesitamos el valor neto
                # Valor neto = Valor con IVA / 1.19
                monto_cuota = monto_cuota_con_iva / Decimal('1.19')
                
                # Extraer banco
                banco = fila.get('BANCO', '').strip()
                
                # Crear entidad
                try:
                    leasing = Leasing(
                        codigo_maquina=codigo_maquina,
                        monto_cuota=monto_cuota,
                        banco=banco,
                        estado=estado
                    )
                    leasing_list.append(leasing)
                except ValueError as e:
                    # Si hay error de validación, continuar con el siguiente
                    print(f"  [WARNING] Error al procesar leasing para {codigo_int}: {e}")
                    continue
        
        return leasing_list
