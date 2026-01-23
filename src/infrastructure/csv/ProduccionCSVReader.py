"""
Lector CSV para datos de producción.

Lee el archivo de producción y convierte los datos en entidades de dominio.
Sigue el principio de inversión de dependencias (DIP).
"""

import csv
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pathlib import Path

from src.domain.entities.Produccion import Produccion
from src.domain.services.NormalizadorMaquinas import NormalizadorMaquinas
from src.domain.services.ValorUFService import ValorUFService


class ProduccionCSVReader:
    """
    Lector de archivos CSV de producción.
    
    Lee el archivo 'Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv'
    y extrae los datos de producción por máquina.
    """
    
    MESES_FILTRO = [10, 11, 12]  # Octubre, Noviembre, Diciembre
    ANIO_FILTRO = None  # Se detectará automáticamente desde los datos
    
    def __init__(self, ruta_archivo: str, valor_uf: Optional[Decimal] = None):
        """
        Inicializa el lector con la ruta del archivo.
        
        Args:
            ruta_archivo: Ruta al archivo CSV de producción
            valor_uf: Valor de la UF en pesos chilenos (opcional)
        """
        self.ruta_archivo = Path(ruta_archivo)
        if not self.ruta_archivo.exists():
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")
        
        # Inicializar servicio de UF
        self.uf_service = ValorUFService(valor_uf_manual=valor_uf)
    
    def _parsear_fecha(self, fecha_str: str) -> Optional[datetime]:
        """
        Parsea una fecha en formato dd/mm/yyyy.
        
        Args:
            fecha_str: String con la fecha en formato dd/mm/yyyy
            
        Returns:
            Objeto datetime o None si no se puede parsear
        """
        try:
            return datetime.strptime(fecha_str.strip(), '%d/%m/%Y')
        except (ValueError, AttributeError):
            return None
    
    def _parsear_decimal(self, valor: str) -> Decimal:
        """
        Parsea un valor a Decimal, manejando "No hay datos" como 0.
        
        Args:
            valor: String con el valor numérico
            
        Returns:
            Decimal con el valor parseado o 0 si es "No hay datos"
        """
        if not valor or valor.strip().lower() in ['no hay datos', '', 'nan']:
            return Decimal('0')
        
        try:
            # Remover espacios y convertir a decimal
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
            True si la fecha está en los meses filtrados del año filtrado
        """
        if self.ANIO_FILTRO is None:
            return False
        return (fecha.year == self.ANIO_FILTRO and 
                fecha.month in self.MESES_FILTRO)
    
    def leer(self) -> List[Produccion]:
        """
        Lee el archivo CSV y retorna una lista de entidades Produccion.
        
        Returns:
            Lista de entidades Produccion filtradas por mes
        """
        producciones = []
        
        # Primera pasada: detectar el año más común
        anos_contados: dict[int, int] = {}
        with open(self.ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            for fila in lector:
                fecha_str = fila.get('FECHA REPORTE', '').strip()
                fecha = self._parsear_fecha(fecha_str)
                if fecha:
                    ano = fecha.year
                    anos_contados[ano] = anos_contados.get(ano, 0) + 1
        
        # Establecer el año con más registros
        if anos_contados:
            self.ANIO_FILTRO = max(anos_contados.keys(), key=lambda k: anos_contados[k])
            print(f"  - Año detectado automáticamente: {self.ANIO_FILTRO}")
        else:
            print("  - [WARNING] No se detectaron fechas válidas en el archivo")
            return []
        
        # Segunda pasada: procesar los datos con el filtro establecido
        with open(self.ruta_archivo, 'r', encoding='utf-8-sig') as archivo:
            lector = csv.DictReader(archivo)
            
            for fila in lector:
                # Parsear fecha
                fecha_str = fila.get('FECHA REPORTE', '').strip()
                fecha = self._parsear_fecha(fecha_str)
                
                if not fecha or not self._filtrar_por_mes(fecha):
                    continue
                
                # Normalizar código de máquina
                maquina_full = fila.get('MAQUINA_FULL', '').strip()
                codigo_maquina = NormalizadorMaquinas.normalizar(maquina_full)
                
                if not codigo_maquina:
                    continue
                
                # Extraer tipo de unidad, cantidad y precio
                tipo_unidad = fila.get('vc_Tipo_Unidad', '').strip()
                contrato_txt = fila.get('CONTRATO_TXT', '').strip()
                unidades = self._parsear_decimal(fila.get('vc_Unidades', '0'))
                precio_unidad = self._parsear_decimal(fila.get('vc_Precio_Unidades', '0'))
                
                # Inicializar valores según el tipo de unidad
                mt3 = Decimal('0')
                horas = Decimal('0')
                km = Decimal('0')
                vueltas = Decimal('0')
                valor_monetario = Decimal('0')
                
                # Mapear tipo de unidad a las columnas correspondientes
                tipo_unidad_upper = tipo_unidad.upper() if tipo_unidad else ''
                
                # Si el tipo de unidad es "?" o está vacío, inferir desde el nombre del contrato
                if tipo_unidad_upper == '?' or not tipo_unidad:
                    contrato_upper = contrato_txt.upper()
                    if 'MT3' in contrato_upper:
                        tipo_unidad_upper = 'MT3'
                    elif 'HR' in contrato_upper or 'HORAS' in contrato_upper:
                        tipo_unidad_upper = 'HR'
                    elif 'KM' in contrato_upper and 'MT3' not in contrato_upper:
                        tipo_unidad_upper = 'KM'
                    elif 'DIA' in contrato_upper:
                        tipo_unidad_upper = 'DIA'
                
                if tipo_unidad_upper == 'MT3' or tipo_unidad_upper == 'M3' or tipo_unidad_upper == 'M³' or tipo_unidad_upper == 'MT3':
                    mt3 = unidades
                    valor_monetario = unidades * precio_unidad
                elif tipo_unidad_upper == 'HR' or tipo_unidad_upper == 'H':
                    horas = unidades
                    valor_monetario = unidades * precio_unidad
                elif tipo_unidad_upper == 'KM' or tipo_unidad_upper == 'K':
                    km = unidades
                    valor_monetario = unidades * precio_unidad
                elif tipo_unidad_upper == 'DIA':
                    # Los días se pueden considerar como horas (1 día = 8 horas típicamente)
                    horas = unidades * Decimal('8')  # Asumiendo 8 horas por día
                    valor_monetario = unidades * precio_unidad  # El precio ya es por día
                elif tipo_unidad == '?' or tipo_unidad.upper() == 'UF':
                    # Es UF (Unidad de Fomento) - Siempre usar 0.9 UF
                    valor_uf = self.uf_service.obtener_valor_uf(fecha)
                    unidades_uf = Decimal('0.9')  # Siempre 0.9 UF según especificación
                    
                    # Calcular el valor en pesos: 0.9 UF × valor_uf_actual
                    valor_monetario = unidades_uf * valor_uf
                    
                    # Calcular horas equivalentes basado en el valor en pesos
                    # Usamos el precio por unidad si está disponible, sino $35,000
                    if precio_unidad > 0:
                        horas = valor_monetario / precio_unidad
                    else:
                        precio_hora_estimado = Decimal('35000')
                        horas = valor_monetario / precio_hora_estimado
                
                # Crear entidad
                produccion = Produccion(
                    codigo_maquina=codigo_maquina,
                    fecha=fecha,
                    mt3=mt3,
                    horas_trabajadas=horas,
                    kilometros=km,
                    vueltas=vueltas,
                    precio_unidad=precio_unidad,
                    valor_monetario=valor_monetario,
                    tipo_unidad_original=tipo_unidad.upper()  # Guardar tipo original
                )
                
                producciones.append(produccion)
        
        return producciones
