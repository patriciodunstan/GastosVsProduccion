"""
Entidad de dominio: Maquina

Representa una máquina con su código normalizado.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Maquina:
    """
    Entidad inmutable que representa una máquina.
    
    Attributes:
        codigo: Código normalizado de la máquina (ej: "CT-10 HKDX21")
        nombre_completo: Nombre completo original de la máquina (opcional)
    """
    codigo: str
    nombre_completo: Optional[str] = None
    
    def __post_init__(self):
        """Valida que el código no esté vacío."""
        if not self.codigo or not self.codigo.strip():
            raise ValueError("El código de máquina no puede estar vacío")
    
    def __str__(self) -> str:
        return self.codigo
