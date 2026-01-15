"""
Servicio de dominio: CalculadorProduccion

Calcula y agrega la producción total por máquina y mes.
Sigue el principio de responsabilidad única (SRP).
"""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, Tuple

from src.domain.entities.Produccion import Produccion


class CalculadorProduccion:
    """
    Calcula la producción agregada por máquina y mes.
    
    Agrega los valores de MT3, horas trabajadas, kilómetros y vueltas
    para cada combinación de máquina y mes.
    """
    
    @staticmethod
    def calcular_por_maquina_mes(
        producciones: list[Produccion]
    ) -> Dict[Tuple[str, int], Dict[str, Decimal]]:
        """
        Calcula la producción agregada por máquina y mes.
        
        Args:
            producciones: Lista de entidades Produccion
            
        Returns:
            Diccionario con clave (codigo_maquina, mes) y valor:
            {
                'mt3': Decimal,
                'horas_trabajadas': Decimal,
                'kilometros': Decimal,
                'vueltas': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'mt3': Decimal('0'),
            'horas_trabajadas': Decimal('0'),
            'kilometros': Decimal('0'),
            'vueltas': Decimal('0'),
            'dias': Decimal('0'),  # Días trabajados (tipo DIA)
            'valor_monetario': Decimal('0'),  # Suma de todos los valores monetarios
            'valor_mt3': Decimal('0'),  # Valor monetario solo de MT3
            'valor_horas': Decimal('0'),  # Valor monetario solo de Horas (Hr/H)
            'valor_km': Decimal('0'),  # Valor monetario solo de Km
            'valor_vueltas': Decimal('0'),  # Valor monetario solo de Vueltas
            'valor_dias': Decimal('0')  # Valor monetario solo de Días (Dia)
        })
        
        for produccion in producciones:
            clave = (produccion.codigo_maquina, produccion.fecha.month)
            
            resultado[clave]['mt3'] += produccion.mt3
            resultado[clave]['horas_trabajadas'] += produccion.horas_trabajadas
            resultado[clave]['kilometros'] += produccion.kilometros
            resultado[clave]['vueltas'] += produccion.vueltas
            resultado[clave]['valor_monetario'] += produccion.valor_monetario
            
            # Usar el tipo original para clasificar correctamente el valor monetario
            tipo_original = produccion.tipo_unidad_original.upper()
            
            if produccion.valor_monetario > 0:
                if tipo_original == 'MT3':
                    resultado[clave]['valor_mt3'] += produccion.valor_monetario
                elif tipo_original in ['HR', 'H']:
                    resultado[clave]['valor_horas'] += produccion.valor_monetario
                elif tipo_original in ['KM', 'K']:
                    resultado[clave]['valor_km'] += produccion.valor_monetario
                elif tipo_original == 'DIA':
                    # Los días también se cuentan en horas para compatibilidad
                    # pero el valor monetario va en valor_dias
                    resultado[clave]['dias'] += produccion.horas_trabajadas / Decimal('8')  # Convertir horas a días
                    resultado[clave]['valor_dias'] += produccion.valor_monetario
                elif tipo_original == 'VUELTAS':
                    resultado[clave]['valor_vueltas'] += produccion.valor_monetario
                elif tipo_original in ['?', 'UF']:
                    # UF se cuenta como horas equivalentes, pero el valor va en horas
                    resultado[clave]['valor_horas'] += produccion.valor_monetario
        
        return dict(resultado)
    
    @staticmethod
    def calcular_total_por_maquina(
        producciones: list[Produccion]
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calcula la producción total por máquina (sin separar por mes).
        
        Args:
            producciones: Lista de entidades Produccion
            
        Returns:
            Diccionario con clave codigo_maquina y valor:
            {
                'mt3': Decimal,
                'horas_trabajadas': Decimal,
                'kilometros': Decimal,
                'vueltas': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'mt3': Decimal('0'),
            'horas_trabajadas': Decimal('0'),
            'kilometros': Decimal('0'),
            'vueltas': Decimal('0'),
            'dias': Decimal('0'),
            'valor_monetario': Decimal('0'),  # Suma de todos los valores monetarios
            'valor_mt3': Decimal('0'),  # Valor monetario solo de MT3
            'valor_horas': Decimal('0'),  # Valor monetario solo de Horas
            'valor_km': Decimal('0'),  # Valor monetario solo de Km
            'valor_vueltas': Decimal('0'),  # Valor monetario solo de Vueltas
            'valor_dias': Decimal('0')  # Valor monetario solo de Días
        })
        
        for produccion in producciones:
            codigo = produccion.codigo_maquina
            
            resultado[codigo]['mt3'] += produccion.mt3
            resultado[codigo]['horas_trabajadas'] += produccion.horas_trabajadas
            resultado[codigo]['kilometros'] += produccion.kilometros
            resultado[codigo]['vueltas'] += produccion.vueltas
            resultado[codigo]['valor_monetario'] += produccion.valor_monetario
            
            # Usar el tipo original para clasificar correctamente
            tipo_original = produccion.tipo_unidad_original.strip().upper() if produccion.tipo_unidad_original else ''
            
            if produccion.valor_monetario > 0:
                if tipo_original == 'MT3':
                    resultado[codigo]['valor_mt3'] += produccion.valor_monetario
                elif tipo_original in ['HR', 'H']:
                    resultado[codigo]['valor_horas'] += produccion.valor_monetario
                elif tipo_original in ['KM', 'K']:
                    resultado[codigo]['valor_km'] += produccion.valor_monetario
                elif tipo_original == 'DIA':
                    resultado[codigo]['dias'] += produccion.horas_trabajadas / Decimal('8')
                    resultado[codigo]['valor_dias'] += produccion.valor_monetario
                elif tipo_original == 'VUELTAS':
                    resultado[codigo]['valor_vueltas'] += produccion.valor_monetario
                elif tipo_original in ['?', 'UF']:
                    resultado[codigo]['valor_horas'] += produccion.valor_monetario
                else:
                    # Si no se reconoce el tipo, asignar según las unidades
                    if produccion.mt3 > 0:
                        resultado[codigo]['valor_mt3'] += produccion.valor_monetario
                    elif produccion.kilometros > 0:
                        resultado[codigo]['valor_km'] += produccion.valor_monetario
                    elif produccion.vueltas > 0:
                        resultado[codigo]['valor_vueltas'] += produccion.valor_monetario
                    elif produccion.horas_trabajadas > 0:
                        resultado[codigo]['valor_horas'] += produccion.valor_monetario
        
        return dict(resultado)
