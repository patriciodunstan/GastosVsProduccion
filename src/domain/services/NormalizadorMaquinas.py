"""
Servicio de dominio: NormalizadorMaquinas

Normaliza los códigos de máquinas desde diferentes formatos.
Sigue el principio de responsabilidad única (SRP) y principio abierto/cerrado (OCP).
"""

import re
from typing import Optional
from src.domain.entities.Maquina import Maquina


class NormalizadorMaquinas:
    """
    Servicio para normalizar códigos de máquinas desde diferentes formatos.
    
    Extrae el código de máquina usando expresiones regulares para manejar
    diferentes formatos de entrada.
    """
    
    # Patrón regex para extraer códigos de máquinas
    # Ejemplos: [CT-10 HKDX21], CT-10 HKDX21, CT-10, EX-15 THYP52, RXm-09
    # Acepta letras mayúsculas y minúsculas en el código
    PATRON_CODIGO = re.compile(r'\[?([A-Za-z]+-\d+[A-Za-z0-9-]*)\]?')
    
    @classmethod
    def normalizar(cls, texto_maquina: str) -> Optional[str]:
        """
        Normaliza un texto de máquina extrayendo su código.
        
        Args:
            texto_maquina: Texto que contiene el nombre/código de la máquina
            
        Returns:
            Código normalizado de la máquina o None si no se encuentra
            
        Examples:
            >>> NormalizadorMaquinas.normalizar("[CT-10 HKDX21] - FOTON AUMAN 3239")
            'CT-10 HKDX21'
            >>> NormalizadorMaquinas.normalizar("CT-10 HKDX21 - FOTON - AUMAN 3239")
            'CT-10 HKDX21'
            >>> NormalizadorMaquinas.normalizar("CT-10 CAMION FOTON HKDX21")
            'CT-10'
        """
        if not texto_maquina or not texto_maquina.strip():
            return None
        
        # Buscar el patrón de código en el texto
        match = cls.PATRON_CODIGO.search(texto_maquina)
        if match:
            return match.group(1).strip()
        
        return None
    
    @classmethod
    def crear_maquina(cls, texto_maquina: str) -> Optional[Maquina]:
        """
        Crea una entidad Maquina desde un texto.
        
        Args:
            texto_maquina: Texto que contiene el nombre/código de la máquina
            
        Returns:
            Instancia de Maquina o None si no se puede normalizar
        """
        codigo = cls.normalizar(texto_maquina)
        if codigo:
            return Maquina(codigo=codigo, nombre_completo=texto_maquina.strip())
        return None
