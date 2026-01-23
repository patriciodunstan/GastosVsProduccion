"""
Entidad de dominio: GastoOperacional

Representa un gasto operacional desglosado (combustibles, reparaciones, etc.).
"""


from decimal import Decimal
from datetime import date
from typing import Optional
from enum import Enum


class TipoGasto(Enum):
    """Enum de tipos de gastos operacionales."""
    
    COMBUSTIBLES = "401010101"  # Combustibles
    REPUESTOS = "401010102"  # Repuestos y accesorios
    REPARACIONES = "401010103"  # Reparaciones y mantención
    EPP = "401010104"  # Elementos de protección personal
    SEGUROS = "401010115"  # Póliza de seguro
    PERMISOS = "401010116"  # Permiso de circulación
    REVISION = "401010117"  # Revisión técnica
    HONORARIOS = "401010109"  # Honorarios
    PEAJES = "401010105"  # Peajes y transbordador
    ALIMENTACION = "401010112"  # Alimentación
    PASAJES = "401010111"  # Pasajes nacionales
    MULTAS = "401030102"  # Multas instituciones públicas
    OTROS_GASTOS = "401030107"  # Otros gastos
    REMUNERACIONES = "401010108"  # Remuneraciones
    CORRESPONDENCIA = "401020107"  # Correspondencia
    GASTOS_LEGALES = "401020108"  # Gastos legales
    SERVICIO_TRANSPORTE = "401010106"  # Servicio transporte
    REVISION_TECNICA = "401010107"  # Revisión técnica (código adicional)
    VARIOS = "401010113"  # Varios
    MANTENCION_VARIOS = "401010114"  # Mantención varios
    OTRO_GASTO_TALLER = "401010118"  # Otro gasto taller
    ALQUILER_MAQUINARIA = "401010119"  # Alquiler maquinaria
    SERVICIOS_EXTERNOS = "401020101"  # Servicios externos
    ELECTRICIDAD = "401020102"  # Electricidad
    AGUA = "401020103"  # Agua
    OTRO_GASTO_OPERACIONAL = "401020114"  # Otro gasto operacional
    SUMINISTROS = "401040101"  # Suministros
    OTROS_SUMINISTROS = "401040104"  # Otros suministros
    
    @classmethod
    def obtener_nombre(cls, codigo: str) -> str:
        """Obtiene el nombre legible del tipo de gasto."""
        mapeo = {
            cls.COMBUSTIBLES.value: "Combustibles",
            cls.REPUESTOS.value: "Repuestos y accesorios",
            cls.REPARACIONES.value: "Reparaciones y mantención",
            cls.EPP.value: "EPP (Protección personal)",
            cls.SEGUROS.value: "Seguros",
            cls.PERMISOS.value: "Permisos de circulación",
            cls.REVISION.value: "Revisión técnica",
            cls.HONORARIOS.value: "Honorarios",
            cls.PEAJES.value: "Peajes y transbordador",
            cls.ALIMENTACION.value: "Alimentación",
            cls.PASAJES.value: "Pasajes nacionales",
            cls.MULTAS.value: "Multas",
            cls.OTROS_GASTOS.value: "Otros gastos",
            cls.REMUNERACIONES.value: "Remuneraciones",
            cls.CORRESPONDENCIA.value: "Correspondencia",
            cls.GASTOS_LEGALES.value: "Gastos legales",
            cls.SERVICIO_TRANSPORTE.value: "Servicio transporte",
            cls.REVISION_TECNICA.value: "Revisión técnica",
            cls.VARIOS.value: "Varios",
            cls.MANTENCION_VARIOS.value: "Mantención varios",
            cls.OTRO_GASTO_TALLER.value: "Otro gasto taller",
            cls.ALQUILER_MAQUINARIA.value: "Alquiler maquinaria",
            cls.SERVICIOS_EXTERNOS.value: "Servicios externos",
            cls.ELECTRICIDAD.value: "Electricidad",
            cls.AGUA.value: "Agua",
            cls.OTRO_GASTO_OPERACIONAL.value: "Otro gasto operacional",
            cls.SUMINISTROS.value: "Suministros",
            cls.OTROS_SUMINISTROS.value: "Otros suministros",
        }
        return mapeo.get(codigo, f"Tipo {codigo}")


class GastoOperacional:
    """
    Representa un gasto operacional individual.
    
    Atributos:
        - codigo_maquina: Código normalizado de la máquina
        - fecha: Fecha del gasto
        - tipo_gasto: Tipo de gasto (código de cuenta contable)
        - glosa: Descripción del gasto
        - monto: Monto del gasto (pérdida)
        - es_ingreso: Si es un ingreso en lugar de gasto
        - origen: Archivo de origen
    """
    
    def __init__(
        self,
        codigo_maquina: str,
        fecha: date,
        tipo_gasto: str,
        glosa: str,
        monto: Decimal,
        es_ingreso: bool = False,
        origen: str = ""
    ):
        self.codigo_maquina = codigo_maquina
        self.fecha = fecha
        self.tipo_gasto = tipo_gasto
        self.glosa = glosa
        self.monto = monto
        self.es_ingreso = es_ingreso
        self.origen = origen
    
    @property
    def mes(self) -> int:
        """Mes del gasto (1-12)."""
        return self.fecha.month
    
    @property
    def nombre_tipo_gasto(self) -> str:
        """Nombre legible del tipo de gasto."""
        return TipoGasto.obtener_nombre(self.tipo_gasto)
    
    def to_dict(self) -> dict:
        """Convierte el gasto a diccionario."""
        return {
            'codigo_maquina': self.codigo_maquina,
            'fecha': self.fecha.strftime('%Y-%m-%d'),
            'mes': self.mes,
            'tipo_gasto': self.tipo_gasto,
            'nombre_tipo_gasto': self.nombre_tipo_gasto,
            'glosa': self.glosa,
            'monto': float(self.monto),
            'es_ingreso': self.es_ingreso,
            'origen': self.origen
        }
