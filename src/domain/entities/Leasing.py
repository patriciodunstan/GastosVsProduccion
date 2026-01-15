"""
Entidad de dominio: Leasing

Representa un leasing o crédito de una máquina.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Leasing:
    """
    Entidad inmutable que representa un leasing de una máquina.
    
    Attributes:
        codigo_maquina: Código de la máquina
        monto_cuota: Monto mensual de la cuota de leasing
        banco: Banco que otorga el leasing
        estado: Estado del leasing (VIGENTE, etc.)
    """
    codigo_maquina: str
    monto_cuota: Decimal
    banco: str
    estado: str
    
    def __post_init__(self):
        """Valida que el monto sea positivo."""
        monto_decimal = Decimal(str(self.monto_cuota))
        
        if monto_decimal < 0:
            raise ValueError("El monto de la cuota no puede ser negativo")
        
        object.__setattr__(self, 'monto_cuota', monto_decimal)
