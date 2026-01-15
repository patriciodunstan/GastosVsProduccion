"""
Entidad de dominio: HorasHombre

Representa las horas hombre trabajadas en una máquina.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional


@dataclass(frozen=True)
class HorasHombre:
    """
    Entidad inmutable que representa horas hombre trabajadas.
    
    Attributes:
        codigo_maquina: Código de la máquina
        fecha: Fecha de salida del trabajo
        mecanico: Nombre del mecánico
        tipo_orden: Tipo de orden (Preventivo/Correctivo)
        horas: Cantidad de horas trabajadas
    """
    codigo_maquina: str
    fecha: datetime
    mecanico: str
    tipo_orden: str
    horas: Decimal
    
    def __post_init__(self):
        """Valida que las horas sean positivas."""
        horas_decimal = Decimal(str(self.horas))
        if horas_decimal < 0:
            raise ValueError("Las horas no pueden ser negativas")
        object.__setattr__(self, 'horas', horas_decimal)
