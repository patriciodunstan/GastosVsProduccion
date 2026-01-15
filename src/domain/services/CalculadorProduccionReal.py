"""
Servicio de dominio: CalculadorProduccionReal

Calcula la producción real (producción - gastos) por máquina y mes.
Sigue el principio de responsabilidad única (SRP).
"""

from decimal import Decimal
from typing import Dict, Tuple

from src.domain.services.CalculadorProduccion import CalculadorProduccion
from src.domain.services.CalculadorGastos import CalculadorGastos
from src.domain.entities.Produccion import Produccion
from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.entities.Repuesto import Repuesto


class CalculadorProduccionReal:
    """
    Calcula la producción real restando los gastos de la producción.
    
    La producción real se calcula como:
    Producción Real = Producción Total - Gastos Totales
    """
    
    @staticmethod
    def calcular_por_maquina_mes(
        producciones: list[Produccion],
        repuestos: list[Repuesto],
        horas_hombre: list[HorasHombre],
        leasing: list[Leasing] = None
    ) -> Dict[Tuple[str, int], Dict[str, Decimal]]:
        """
        Calcula la producción real por máquina y mes.
        
        Args:
            producciones: Lista de entidades Produccion
            repuestos: Lista de entidades Repuesto
            horas_hombre: Lista de entidades HorasHombre
            
        Returns:
            Diccionario con clave (codigo_maquina, mes) y valor:
            {
                'produccion': {
                    'mt3': Decimal,
                    'horas_trabajadas': Decimal,
                    'kilometros': Decimal,
                    'vueltas': Decimal
                },
                'gastos': {
                    'repuestos': Decimal,
                    'costo_hh': Decimal,
                    'total': Decimal
                },
                'produccion_real': {
                    'mt3': Decimal,
                    'horas_trabajadas': Decimal,
                    'kilometros': Decimal,
                    'vueltas': Decimal,
                    'valor_monetario': Decimal  # Producción - Gastos (en CLP)
                }
            }
        """
        # Calcular producción y gastos
        prod_por_mes = CalculadorProduccion.calcular_por_maquina_mes(producciones)
        gastos_por_mes = CalculadorGastos.calcular_por_maquina_mes(repuestos, horas_hombre, leasing)
        
        # Combinar resultados
        resultado = {}
        
        # Procesar todas las máquinas y meses que tienen producción
        todas_las_claves = set(prod_por_mes.keys()) | set(gastos_por_mes.keys())
        
        for clave in todas_las_claves:
            prod = prod_por_mes.get(clave, {
                'mt3': Decimal('0'),
                'horas_trabajadas': Decimal('0'),
                'kilometros': Decimal('0'),
                'vueltas': Decimal('0'),
                'valor_monetario': Decimal('0')
            })
            
            gastos = gastos_por_mes.get(clave, {
                'repuestos': Decimal('0'),
                'horas_hombre': Decimal('0'),
                'costo_hh': Decimal('0'),
                'leasing': Decimal('0'),
                'total': Decimal('0')
            })
            
            # Calcular producción neta usando el valor monetario real del CSV
            # Este valor ya viene calculado como: unidades × precio_unidad (del CSV)
            produccion_neta = prod.get('valor_monetario', Decimal('0'))
            
            # Calcular producción real (producción neta - gastos totales)
            produccion_real = produccion_neta - gastos['total']
            
            resultado[clave] = {
                'produccion': prod,
                'gastos': gastos,
                'produccion_neta': {
                    'mt3': prod['mt3'],
                    'horas_trabajadas': prod['horas_trabajadas'],
                    'kilometros': prod['kilometros'],
                    'vueltas': prod['vueltas'],
                    'valor_monetario': produccion_neta
                },
                'produccion_real': {
                    'mt3': Decimal('0'),
                    'horas_trabajadas': Decimal('0'),
                    'kilometros': Decimal('0'),
                    'vueltas': Decimal('0'),
                    'valor_monetario': produccion_real  # Producción Neta - Gastos Totales
                }
            }
        
        return resultado
    
    @staticmethod
    def calcular_total_por_maquina(
        producciones: list[Produccion],
        repuestos: list[Repuesto],
        horas_hombre: list[HorasHombre],
        leasing: list[Leasing] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calcula la producción real total por máquina (sin separar por mes).
        
        Args:
            producciones: Lista de entidades Produccion
            repuestos: Lista de entidades Repuesto
            horas_hombre: Lista de entidades HorasHombre
            leasing: Lista de entidades Leasing (opcional)
            
        Returns:
            Diccionario con clave codigo_maquina y valor similar a calcular_por_maquina_mes
        """
        # Calcular producción y gastos totales
        prod_total = CalculadorProduccion.calcular_total_por_maquina(producciones)
        gastos_total = CalculadorGastos.calcular_total_por_maquina(repuestos, horas_hombre, leasing)
        
        # Combinar resultados
        resultado = {}
        
        todas_las_maquinas = set(prod_total.keys()) | set(gastos_total.keys())
        
        for codigo in todas_las_maquinas:
            prod = prod_total.get(codigo, {
                'mt3': Decimal('0'),
                'horas_trabajadas': Decimal('0'),
                'kilometros': Decimal('0'),
                'vueltas': Decimal('0'),
                'valor_monetario': Decimal('0')
            })
            
            gastos = gastos_total.get(codigo, {
                'repuestos': Decimal('0'),
                'horas_hombre': Decimal('0'),
                'costo_hh': Decimal('0'),
                'leasing': Decimal('0'),
                'total': Decimal('0')
            })
            
            # Calcular producción neta usando el valor monetario real del CSV
            # Este valor ya viene calculado como: unidades × precio_unidad (del CSV)
            produccion_neta = prod.get('valor_monetario', Decimal('0'))
            
            # Calcular producción real (producción neta - gastos totales)
            produccion_real = produccion_neta - gastos['total']
            
            resultado[codigo] = {
                'produccion': prod,
                'gastos': gastos,
                'produccion_neta': {
                    'mt3': prod['mt3'],
                    'horas_trabajadas': prod['horas_trabajadas'],
                    'kilometros': prod['kilometros'],
                    'vueltas': prod['vueltas'],
                    'valor_monetario': produccion_neta
                },
                'produccion_real': {
                    'mt3': Decimal('0'),
                    'horas_trabajadas': Decimal('0'),
                    'kilometros': Decimal('0'),
                    'vueltas': Decimal('0'),
                    'valor_monetario': produccion_real  # Producción Neta - Gastos Totales
                }
            }
        
        return resultado
