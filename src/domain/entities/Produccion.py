"""
Entidad de dominio: Produccion

Representa los datos de producción de una máquina en un período específico.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from decimal import Decimal


@dataclass(frozen=True)
class Produccion:
    """
    Entidad inmutable que representa la producción de una máquina.

    Attributes:
        codigo_maquina: Código de la máquina
        fecha: Fecha del reporte de producción
        mt3: Metros cúbicos producidos (None o 0 si no hay datos)
        horas_trabajadas: Horas trabajadas (None o 0 si no hay datos)
        kilometros: Kilómetros recorridos (None o 0 si no hay datos)
        vueltas: Número de vueltas (None o 0 si no hay datos)
        precio_unidad: Precio por unidad según el tipo (MT3, Hr, Km, etc.)
        valor_monetario: Valor monetario total de la producción (unidades × precio_unidad)

        Nuevos campos para contratos híbridos:
        contrato_id: ID del contrato (ej: CT00052KmHr)
        es_hibrido: True si el contrato tiene múltiples precios
        precios_usados: Lista de (tipo, valor) usados en el cálculo
        desglose_precios: Dict con el valor de cada unidad
        contrato_tiene_precio: False si el contrato no tiene NINGÚN precio
    """
    codigo_maquina: str
    fecha: datetime
    mt3: Decimal = Decimal('0')
    horas_trabajadas: Decimal = Decimal('0')
    kilometros: Decimal = Decimal('0')
    vueltas: Decimal = Decimal('0')
    precio_unidad: Decimal = Decimal('0')
    valor_monetario: Decimal = Decimal('0')
    tipo_unidad_original: str = ''  # Tipo original del CSV: MT3, Hr, H, Km, Dia, Vueltas, ?, UF

    # Campos para contratos híbridos
    contrato_id: str = ''  # ID del contrato de precios
    es_hibrido: bool = False  # True si el contrato tiene múltiples precios
    precios_usados: Tuple[Tuple[str, Decimal], ...] = field(default_factory=tuple)  # (tipo, valor) usados
    desglose_precios: Dict[str, Decimal] = field(default_factory=dict)  # {hora: valor, km: valor}
    contrato_tiene_precio: bool = True  # False si el contrato no tiene NINGÚN precio

    def __post_init__(self):
        """Valida y normaliza los valores."""
        # Asegurar que todos los valores sean Decimal y no negativos
        object.__setattr__(self, 'mt3', max(Decimal('0'), Decimal(str(self.mt3))))
        object.__setattr__(self, 'horas_trabajadas', max(Decimal('0'), Decimal(str(self.horas_trabajadas))))
        object.__setattr__(self, 'kilometros', max(Decimal('0'), Decimal(str(self.kilometros))))
        object.__setattr__(self, 'vueltas', max(Decimal('0'), Decimal(str(self.vueltas))))

        # Normalizar desglose_precios a dict inmutable
        if self.desglose_precios and not isinstance(self.desglose_precios, dict):
            object.__setattr__(self, 'desglose_precios', dict(self.desglose_precios))
