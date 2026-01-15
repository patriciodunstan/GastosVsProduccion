"""
Servicio de dominio: CalculadorGastos

Calcula los gastos totales por máquina y mes.
Sigue el principio de responsabilidad única (SRP).
"""

from collections import defaultdict
from decimal import Decimal
from typing import Dict, Tuple

from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing


class CalculadorGastos:
    """
    Calcula los gastos agregados por máquina y mes.
    
    Incluye:
    - Gastos en repuestos
    - Costo de horas hombre (horas × $35.000)
    - Leasing mensual (cuota de leasing por mes)
    - Total de gastos
    """
    
    COSTO_HORA_FIJO = Decimal('35000')  # $35.000 CLP por hora
    
    @classmethod
    def calcular_por_maquina_mes(
        cls,
        repuestos: list[Repuesto],
        horas_hombre: list[HorasHombre],
        leasing: list[Leasing] = None
    ) -> Dict[Tuple[str, int], Dict[str, Decimal]]:
        """
        Calcula los gastos agregados por máquina y mes.
        
        Args:
            repuestos: Lista de entidades Repuesto
            horas_hombre: Lista de entidades HorasHombre
            leasing: Lista de entidades Leasing (opcional)
            
        Returns:
            Diccionario con clave (codigo_maquina, mes) y valor:
            {
                'repuestos': Decimal,
                'horas_hombre': Decimal,
                'costo_hh': Decimal,
                'leasing': Decimal,
                'total': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'repuestos': Decimal('0'),
            'horas_hombre': Decimal('0'),
            'costo_hh': Decimal('0'),
            'leasing': Decimal('0'),
            'total': Decimal('0')
        })
        
        # Agregar gastos de repuestos
        for repuesto in repuestos:
            clave = (repuesto.codigo_maquina, repuesto.fecha_salida.month)
            resultado[clave]['repuestos'] += repuesto.total
        
        # Agregar horas hombre y calcular costo
        for hh in horas_hombre:
            clave = (hh.codigo_maquina, hh.fecha.month)
            resultado[clave]['horas_hombre'] += hh.horas
            resultado[clave]['costo_hh'] += hh.horas * cls.COSTO_HORA_FIJO
        
        # Agregar leasing mensual (aplicar a todos los meses del trimestre: Oct, Nov, Dic)
        if leasing:
            meses_trimestre = [10, 11, 12]  # Octubre, Noviembre, Diciembre
            for lease in leasing:
                for mes in meses_trimestre:
                    clave = (lease.codigo_maquina, mes)
                    resultado[clave]['leasing'] += lease.monto_cuota
        
        # Calcular totales
        for clave in resultado:
            resultado[clave]['total'] = (
                resultado[clave]['repuestos'] + 
                resultado[clave]['costo_hh'] +
                resultado[clave]['leasing']
            )
        
        return dict(resultado)
    
    @classmethod
    def calcular_total_por_maquina(
        cls,
        repuestos: list[Repuesto],
        horas_hombre: list[HorasHombre],
        leasing: list[Leasing] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calcula los gastos totales por máquina (sin separar por mes).
        
        Args:
            repuestos: Lista de entidades Repuesto
            horas_hombre: Lista de entidades HorasHombre
            leasing: Lista de entidades Leasing (opcional)
            
        Returns:
            Diccionario con clave codigo_maquina y valor:
            {
                'repuestos': Decimal,
                'horas_hombre': Decimal,
                'costo_hh': Decimal,
                'leasing': Decimal,
                'total': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'repuestos': Decimal('0'),
            'horas_hombre': Decimal('0'),
            'costo_hh': Decimal('0'),
            'leasing': Decimal('0'),
            'total': Decimal('0')
        })
        
        # Agregar gastos de repuestos
        for repuesto in repuestos:
            codigo = repuesto.codigo_maquina
            resultado[codigo]['repuestos'] += repuesto.total
        
        # Agregar horas hombre y calcular costo
        for hh in horas_hombre:
            codigo = hh.codigo_maquina
            resultado[codigo]['horas_hombre'] += hh.horas
            resultado[codigo]['costo_hh'] += hh.horas * cls.COSTO_HORA_FIJO
        
        # Agregar leasing (3 meses del trimestre: Oct, Nov, Dic)
        if leasing:
            for lease in leasing:
                codigo = lease.codigo_maquina
                # Leasing trimestral = cuota mensual × 3 meses
                resultado[codigo]['leasing'] += lease.monto_cuota * Decimal('3')
        
        # Calcular totales
        for codigo in resultado:
            resultado[codigo]['total'] = (
                resultado[codigo]['repuestos'] + 
                resultado[codigo]['costo_hh'] +
                resultado[codigo]['leasing']
            )
        
        return dict(resultado)
