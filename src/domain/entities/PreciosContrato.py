"""
Entidad de dominio: PreciosContrato

Representa los precios de un contrato para todas las unidades de medida.
Sigue el principio de responsabilidad única (SRP).
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Dict, List, Tuple, Optional


@dataclass(frozen=True)
class PreciosContrato:
    """
    Entidad inmutable que representa los precios de un contrato.

    Attributes:
        contrato_id: Identificador del contrato (ej: CT00052KmHr)
        tipo: Tipo de contrato (ej: "Km , Hr", "Mt3", "Hr", etc.)
        precio_hora: Precio por hora trabajada
        precio_km: Precio por kilómetro
        precio_mt3: Precio por metro cúbico
        precio_vuelta: Precio por vuelta
        precio_diario: Precio por día
    """
    contrato_id: str
    tipo: str
    precio_hora: Decimal = Decimal('0')
    precio_km: Decimal = Decimal('0')
    precio_mt3: Decimal = Decimal('0')
    precio_vuelta: Decimal = Decimal('0')
    precio_diario: Decimal = Decimal('0')

    def __post_init__(self):
        """Valida y normaliza los valores."""
        # Asegurar que todos los precios sean Decimal y no negativos
        object.__setattr__(self, 'precio_hora', max(Decimal('0'), Decimal(str(self.precio_hora))))
        object.__setattr__(self, 'precio_km', max(Decimal('0'), Decimal(str(self.precio_km))))
        object.__setattr__(self, 'precio_mt3', max(Decimal('0'), Decimal(str(self.precio_mt3))))
        object.__setattr__(self, 'precio_vuelta', max(Decimal('0'), Decimal(str(self.precio_vuelta))))
        object.__setattr__(self, 'precio_diario', max(Decimal('0'), Decimal(str(self.precio_diario))))

    def has_precio(self, tipo_unidad: str) -> bool:
        """
        Verifica si el contrato tiene precio para una unidad específica.

        Args:
            tipo_unidad: Tipo de unidad ('HORA', 'HR', 'KM', 'MT3', 'VUELTA', 'DIA')

        Returns:
            True si tiene precio > 0 para ese tipo
        """
        tipo_upper = tipo_unidad.upper()
        if tipo_upper in ['HORA', 'HR', 'H']:
            return self.precio_hora > 0
        elif tipo_upper in ['KM', 'K']:
            return self.precio_km > 0
        elif tipo_upper in ['MT3', 'M3', 'M³']:
            return self.precio_mt3 > 0
        elif tipo_upper == 'VUELTA':
            return self.precio_vuelta > 0
        elif tipo_upper in ['DIA', 'DIARIO', 'DAY']:
            return self.precio_diario > 0
        return False

    def get_precio(self, tipo_unidad: str) -> Decimal:
        """
        Obtiene el precio para una unidad específica.

        Args:
            tipo_unidad: Tipo de unidad

        Returns:
            Precio o Decimal('0') si no tiene precio
        """
        tipo_upper = tipo_unidad.upper()
        if tipo_upper in ['HORA', 'HR', 'H']:
            return self.precio_hora
        elif tipo_upper in ['KM', 'K']:
            return self.precio_km
        elif tipo_upper in ['MT3', 'M3', 'M³']:
            return self.precio_mt3
        elif tipo_upper == 'VUELTA':
            return self.precio_vuelta
        elif tipo_upper in ['DIA', 'DIARIO', 'DAY']:
            return self.precio_diario
        return Decimal('0')

    def get_all_active_precios(self) -> Dict[str, Decimal]:
        """
        Retorna un diccionario con todos los precios activos (> 0).

        Returns:
            Dict con clave 'hora', 'km', 'mt3', 'vuelta', 'dia' y sus precios
        """
        precios = {}
        if self.precio_hora > 0:
            precios['hora'] = self.precio_hora
        if self.precio_km > 0:
            precios['km'] = self.precio_km
        if self.precio_mt3 > 0:
            precios['mt3'] = self.precio_mt3
        if self.precio_vuelta > 0:
            precios['vuelta'] = self.precio_vuelta
        if self.precio_diario > 0:
            precios['dia'] = self.precio_diario
        return precios

    def num_precios(self) -> int:
        """
        Retorna la cantidad de precios activos (> 0).

        Returns:
            Número de precios configurados
        """
        return sum([
            self.precio_hora > 0,
            self.precio_km > 0,
            self.precio_mt3 > 0,
            self.precio_vuelta > 0,
            self.precio_diario > 0
        ])

    def is_hibrido(self) -> bool:
        """
        Verifica si el contrato es híbrido (tiene más de un precio).

        Returns:
            True si tiene 2 o más precios activos
        """
        return self.num_precios() > 1

    def has_any_precio(self) -> bool:
        """
        Verifica si el contrato tiene al menos un precio activo.

        Returns:
            True si tiene al menos un precio > 0
        """
        return self.num_precios() > 0

    def calcular_valor_produccion(
        self,
        horas: Decimal = Decimal('0'),
        km: Decimal = Decimal('0'),
        mt3: Decimal = Decimal('0'),
        vueltas: Decimal = Decimal('0'),
        dias: Decimal = Decimal('0')
    ) -> Tuple[Decimal, List[str], Dict[str, Decimal]]:
        """
        Calcula el valor total de producción sumando todas las unidades con precio.

        Para contratos híbridos, suma TODOS los valores correspondientes.

        Args:
            horas: Horas trabajadas
            km: Kilómetros recorridos
            mt3: Metros cúbicos producidos
            vueltas: Número de vueltas
            dias: Días trabajados

        Returns:
            Tuple[valor_total, unidades_usadas, desglose_precios]
            - valor_total: Suma de todas las unidades con precio
            - unidades_usadas: Lista de nombres de unidades usadas
            - desglose_precios: Dict con el valor de cada unidad
        """
        valor_total = Decimal('0')
        unidades_usadas = []
        desglose = {}

        if self.precio_hora > 0 and horas > 0:
            valor = horas * self.precio_hora
            valor_total += valor
            unidades_usadas.append('Horas')
            desglose['horas'] = valor

        if self.precio_km > 0 and km > 0:
            valor = km * self.precio_km
            valor_total += valor
            unidades_usadas.append('Km')
            desglose['km'] = valor

        if self.precio_mt3 > 0 and mt3 > 0:
            valor = mt3 * self.precio_mt3
            valor_total += valor
            unidades_usadas.append('Mt3')
            desglose['mt3'] = valor

        if self.precio_vuelta > 0 and vueltas > 0:
            valor = vueltas * self.precio_vuelta
            valor_total += valor
            unidades_usadas.append('Vueltas')
            desglose['vueltas'] = valor

        if self.precio_diario > 0 and dias > 0:
            valor = dias * self.precio_diario
            valor_total += valor
            unidades_usadas.append('Dias')
            desglose['dias'] = valor

        return valor_total, unidades_usadas, desglose

    def get_resumen_precios(self) -> str:
        """
        Retorna un string con el resumen de precios del contrato.

        Returns:
            String con formato "Hr: $35000, Km: $2500" o "Sin precio"
        """
        partes = []
        if self.precio_hora > 0:
            partes.append(f"Hr: ${int(self.precio_hora):,}")
        if self.precio_km > 0:
            partes.append(f"Km: ${int(self.precio_km):,}")
        if self.precio_mt3 > 0:
            partes.append(f"Mt3: ${int(self.precio_mt3):,}")
        if self.precio_vuelta > 0:
            partes.append(f"Vueltas: ${int(self.precio_vuelta):,}")
        if self.precio_diario > 0:
            partes.append(f"Dia: ${int(self.precio_diario):,}")

        return ", ".join(partes) if partes else "Sin precio"
