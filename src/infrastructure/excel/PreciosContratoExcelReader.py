"""
Lector Excel para datos de precios de contratos.

Lee el archivo 'Harcha Maquinaria - Reportaría_CON_PRECIOS.xlsx'
y convierte los datos en entidades de dominio PreciosContrato.
Sigue el principio de inversión de dependencias (DIP).
"""

from decimal import Decimal
from typing import Dict, Optional
from pathlib import Path

import pandas as pd

from src.domain.entities.PreciosContrato import PreciosContrato


class PreciosContratoExcelReader:
    """
    Lector de archivos Excel de precios de contratos.

    Lee el archivo que contiene los precios por contrato para todas
    las unidades de medida (Hr, Km, Mt3, Vueltas, Diario).
    """

    # Columnas esperadas en el Excel
    COLUMNAS_PRECIOS = {
        'CONTRATO_TXT': 'contrato_id',
        'TIPO_CONTRATO': 'tipo',
        'PRECIO_HORA': 'precio_hora',
        'PRECIO_KM': 'precio_km',
        'PRECIO_MT3': 'precio_mt3',
        'PRECIO_VUELTA': 'precio_vuelta',
        'PRECIO_DIARIO': 'precio_diario'
    }

    def __init__(self, ruta_archivo: str):
        """
        Inicializa el lector con la ruta del archivo.

        Args:
            ruta_archivo: Ruta al archivo Excel de precios

        Raises:
            FileNotFoundError: Si el archivo no existe
        """
        self.ruta_archivo = Path(ruta_archivo)
        if not self.ruta_archivo.exists():
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")

    def _parsear_decimal(self, valor) -> Decimal:
        """
        Parsea un valor a Decimal, manejando valores nulos.

        Args:
            valor: Valor a parsear (puede ser str, int, float, NaN, etc.)

        Returns:
            Decimal con el valor parseado o 0 si es nulo/inválido
        """
        if pd.isna(valor) or valor is None:
            return Decimal('0')

        try:
            # Convertir a string primero para manejar formatos especiales
            valor_str = str(valor).strip()
            if valor_str.lower() in ['no hay datos', '', 'nan', 'none']:
                return Decimal('0')
            return Decimal(valor_str)
        except (ValueError, TypeError):
            return Decimal('0')

    def leer(self) -> Dict[str, PreciosContrato]:
        """
        Lee el archivo Excel y retorna un diccionario de PreciosContrato.

        Returns:
            Dict con clave CONTRATO_TXT y valor PreciosContrato.
            Si un contrato aparece múltiples veces, se conserva el primer registro
            (se asume que los precios son consistentes para un mismo contrato).
        """
        try:
            df = pd.read_excel(self.ruta_archivo, engine='openpyxl')
        except Exception as e:
            raise IOError(f"Error al leer el archivo Excel: {e}")

        # Verificar columnas necesarias
        columnas_faltantes = [
            col for col in self.COLUMNAS_PRECIOS.keys()
            if col not in df.columns
        ]
        if columnas_faltantes:
            raise ValueError(
                f"Faltan columnas en el Excel: {columnas_faltantes}. "
                f"Columnas encontradas: {list(df.columns)}"
            )

        # Reemplazar 'No hay datos' con NaN
        df = df.replace('No hay datos', pd.NA)

        resultado = {}

        # Agrupar por contrato para manejar duplicados
        agrupado = df.groupby('CONTRATO_TXT', as_index=False).first()

        for _, fila in agrupado.iterrows():
            contrato_id = fila.get('CONTRATO_TXT', '').strip()
            if not contrato_id:
                continue

            tipo_contrato = fila.get('TIPO_CONTRATO', '').strip()

            # Parsear precios
            precio_hora = self._parsear_decimal(fila.get('PRECIO_HORA', 0))
            precio_km = self._parsear_decimal(fila.get('PRECIO_KM', 0))
            precio_mt3 = self._parsear_decimal(fila.get('PRECIO_MT3', 0))
            precio_vuelta = self._parsear_decimal(fila.get('PRECIO_VUELTA', 0))
            precio_diario = self._parsear_decimal(fila.get('PRECIO_DIARIO', 0))

            # Crear entidad
            precios_contrato = PreciosContrato(
                contrato_id=contrato_id,
                tipo=tipo_contrato,
                precio_hora=precio_hora,
                precio_km=precio_km,
                precio_mt3=precio_mt3,
                precio_vuelta=precio_vuelta,
                precio_diario=precio_diario
            )

            resultado[contrato_id] = precios_contrato

        return resultado

    def leer_con_estadisticas(self) -> tuple[Dict[str, PreciosContrato], Dict]:
        """
        Lee el archivo Excel y retorna precios + estadísticas.

        Returns:
            Tuple[Dict[str, PreciosContrato], Dict] donde:
            - Dict de precios por contrato
            - Dict con estadísticas:
                - total_contratos: int
                - contratos_con_precio: int
                - contratos_sin_precio: int
                - contratos_hibridos: int
                - total_registros: int
        """
        try:
            df = pd.read_excel(self.ruta_archivo, engine='openpyxl')
        except Exception as e:
            raise IOError(f"Error al leer el archivo Excel: {e}")

        df = df.replace('No hay datos', pd.NA)

        # Convertir columnas de precio a numérico
        price_cols = ['PRECIO_HORA', 'PRECIO_KM', 'PRECIO_MT3', 'PRECIO_VUELTA', 'PRECIO_DIARIO']
        for col in price_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # Calcular estadísticas
        def count_precios(row):
            return sum([
                row.get('PRECIO_HORA', 0) > 0,
                row.get('PRECIO_KM', 0) > 0,
                row.get('PRECIO_MT3', 0) > 0,
                row.get('PRECIO_VUELTA', 0) > 0,
                row.get('PRECIO_DIARIO', 0) > 0
            ])

        df['num_precios'] = df.apply(count_precios, axis=1)

        total_registros = len(df)
        contratos_sin_precio_count = len(df[df['num_precios'] == 0])
        contratos_con_precio_count = len(df[df['num_precios'] >= 1])
        contratos_hibridos_count = len(df[df['num_precios'] > 1])

        # Leer precios
        precios_dict = self.leer()

        total_contratos = len(precios_dict)
        contratos_sin_precio = sum(1 for p in precios_dict.values() if not p.has_any_precio())
        contratos_hibridos = sum(1 for p in precios_dict.values() if p.is_hibrido())

        estadisticas = {
            'total_contratos': total_contratos,
            'contratos_con_precio': total_contratos - contratos_sin_precio,
            'contratos_sin_precio': contratos_sin_precio,
            'contratos_hibridos': contratos_hibridos,
            'total_registros': total_registros
        }

        return precios_dict, estadisticas
