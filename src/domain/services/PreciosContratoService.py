"""
Servicio de dominio: PreciosContratoService

Proporciona acceso a los precios de contratos y métodos de cálculo
para contratos híbridos. Sigue el principio de responsabilidad única (SRP).
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional

from src.domain.entities.PreciosContrato import PreciosContrato
from src.infrastructure.excel.PreciosContratoExcelReader import PreciosContratoExcelReader


class PreciosContratoService:
    """
    Servicio que gestiona el acceso a los precios de contratos.

    Actúa como un cache/lookup para precios de contratos y proporciona
    métodos de cálculo para producción con contratos híbridos.
    """

    def __init__(self, precios_reader: Optional[PreciosContratoExcelReader] = None):
        """
        Inicializa el servicio.

        Args:
            precios_reader: Lector de precios Excel (opcional, puede cargarse después)
        """
        self._reader = precios_reader
        self._precios: Dict[str, PreciosContrato] = {}
        self._estadisticas: Dict = {}
        self._cargado = False

    def cargar_precios(self) -> None:
        """Carga los precios desde el reader."""
        if self._reader is None:
            raise RuntimeError("No se ha configurado un reader de precios")

        self._precios, self._estadisticas = self._reader.leer_con_estadisticas()
        self._cargado = True

    def cargar_precios_dict(self, precios: Dict[str, PreciosContrato]) -> None:
        """
        Carga precios desde un diccionario (útil para testing).

        Args:
            precios: Dict de contrato_id -> PreciosContrato
        """
        self._precios = precios
        self._estadisticas = {
            'total_contratos': len(precios),
            'contratos_con_precio': sum(1 for p in precios.values() if p.has_any_precio()),
            'contratos_sin_precio': sum(1 for p in precios.values() if not p.has_any_precio()),
            'contratos_hibridos': sum(1 for p in precios.values() if p.is_hibrido()),
            'total_registros': len(precios)
        }
        self._cargado = True

    def get_precios(self, contrato_id: str) -> Optional[PreciosContrato]:
        """
        Obtiene los precios de un contrato.

        Args:
            contrato_id: ID del contrato (ej: CT00052KmHr)

        Returns:
            PreciosContrato o None si no existe
        """
        return self._precios.get(contrato_id)

    def has_precio(self, contrato_id: str, tipo_unidad: str) -> bool:
        """
        Verifica si un contrato tiene precio para una unidad específica.

        Args:
            contrato_id: ID del contrato
            tipo_unidad: Tipo de unidad ('HORA', 'HR', 'KM', 'MT3', etc.)

        Returns:
            True si tiene precio > 0, False en caso contrario
        """
        precios = self.get_precios(contrato_id)
        if precios is None:
            return False
        return precios.has_precio(tipo_unidad)

    def calcular_valor_produccion(
        self,
        contrato_id: str,
        horas: Decimal = Decimal('0'),
        km: Decimal = Decimal('0'),
        mt3: Decimal = Decimal('0'),
        vueltas: Decimal = Decimal('0'),
        dias: Decimal = Decimal('0')
    ) -> Tuple[Decimal, List[str], Dict[str, Decimal], bool, bool]:
        """
        Calcula el valor de producción para un contrato.

        Para contratos híbridos, suma TODOS los precios activos.
        Para contratos sin precio, retorna 0.

        Args:
            contrato_id: ID del contrato
            horas: Horas trabajadas
            km: Kilómetros
            mt3: Metros cúbicos
            vueltas: Vueltas
            dias: Días

        Returns:
            Tuple[valor_total, unidades_usadas, desglose, es_hibrido, tiene_precio]
            - valor_total: Suma de todas las unidades con precio
            - unidades_usadas: Lista de nombres de unidades usadas
            - desglose: Dict con valor de cada unidad
            - es_hibrido: True si el contrato tiene múltiples precios
            - tiene_precio: True si el contrato tiene al menos un precio
        """
        precios = self.get_precios(contrato_id)

        if precios is None:
            # Contrato no encontrado en el catálogo de precios
            return Decimal('0'), [], {}, False, False

        if not precios.has_any_precio():
            # Contrato sin precio
            return Decimal('0'), [], {}, False, False

        # Calcular valor (suma de todas las unidades con precio)
        valor_total, unidades_usadas, desglose = precios.calcular_valor_produccion(
            horas=horas, km=km, mt3=mt3, vueltas=vueltas, dias=dias
        )

        return valor_total, unidades_usadas, desglose, precios.is_hibrido(), True

    def get_contratos_sin_precio(self) -> List[str]:
        """
        Retorna una lista de IDs de contratos sin precio.

        Returns:
            Lista de contrato_id que no tienen ningún precio configurado
        """
        return [
            cid for cid, precios in self._precios.items()
            if not precios.has_any_precio()
        ]

    def get_contratos_hibridos(self) -> List[str]:
        """
        Retorna una lista de IDs de contratos híbridos.

        Returns:
            Lista de contrato_id que tienen múltiples precios
        """
        return [
            cid for cid, precios in self._precios.items()
            if precios.is_hibrido()
        ]

    def get_estadisticas(self) -> Dict:
        """
        Retorna estadísticas sobre los precios cargados.

        Returns:
            Dict con estadísticas:
                - total_contratos: int
                - contratos_con_precio: int
                - contratos_sin_precio: int
                - contratos_hibridos: int
                - total_registros: int
        """
        return self._estadisticas.copy()

    def is_cargado(self) -> bool:
        """Verifica si los precios han sido cargados."""
        return self._cargado

    def get_all_precios(self) -> Dict[str, PreciosContrato]:
        """Retorna todos los precios cargados."""
        return self._precios.copy()

    def get_precio_unidad(self, contrato_id: str, tipo_unidad: str) -> Decimal:
        """
        Obtiene el precio para una unidad específica de un contrato.

        Args:
            contrato_id: ID del contrato
            tipo_unidad: Tipo de unidad ('HORA', 'HR', 'KM', 'MT3', etc.)

        Returns:
            Precio o Decimal('0') si no existe
        """
        precios = self.get_precios(contrato_id)
        if precios is None:
            return Decimal('0')
        return precios.get_precio(tipo_unidad)
