"""
Entidad de dominio: Repuesto

Representa un repuesto utilizado en una máquina.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass(frozen=True)
class Repuesto:
    """
    Entidad inmutable que representa un repuesto utilizado.
    
    Attributes:
        codigo_maquina: Código de la máquina
        fecha_salida: Fecha de salida del repuesto
        nombre: Nombre del repuesto
        cantidad: Cantidad utilizada
        precio_unitario: Precio unitario del repuesto
        total: Total del repuesto (cantidad × precio_unitario)
        asignado_a: Persona a quien se asignó el repuesto
    """
    codigo_maquina: str
    fecha_salida: datetime
    nombre: str
    cantidad: Decimal
    precio_unitario: Decimal
    total: Decimal
    asignado_a: str
    
    def __post_init__(self):
        """Valida que los valores sean positivos."""
        cantidad_decimal = Decimal(str(self.cantidad))
        precio_decimal = Decimal(str(self.precio_unitario))
        total_decimal = Decimal(str(self.total))
        
        if cantidad_decimal < 0:
            raise ValueError("La cantidad no puede ser negativa")
        if precio_decimal < 0:
            raise ValueError("El precio unitario no puede ser negativo")
        if total_decimal < 0:
            raise ValueError("El total no puede ser negativo")
        
        object.__setattr__(self, 'cantidad', cantidad_decimal)
        object.__setattr__(self, 'precio_unitario', precio_decimal)
        object.__setattr__(self, 'total', total_decimal)
