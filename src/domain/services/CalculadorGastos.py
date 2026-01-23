"""
Servicio de dominio: CalculadorGastos

Calcula los gastos totales por máquina y mes con desglose detallado por tipo.
Sigue el principio de responsabilidad única (SRP).
"""

from collections import defaultdict
from decimal import Decimal
from typing import Dict, Tuple, Optional, List

from src.domain.entities.HorasHombre import HorasHombre
from src.domain.entities.Repuesto import Repuesto
from src.domain.entities.Leasing import Leasing
from src.domain.entities.GastoOperacional import GastoOperacional, TipoGasto


class CalculadorGastos:
    """
    Calcula los gastos agregados por máquina y mes con categorización completa.
    
    Incluye:
    - Gastos en repuestos (DATABODEGA.csv)
    - Gastos operacionales por tipo (reportes contables)
    - Costo de horas hombre (horas × $35.000)
    - Leasing mensual (cuota de leasing por mes)
    - Total de gastos con desglose por categoría
    """
    
    COSTO_HORA_FIJO = Decimal('35000')  # $35.000 CLP por hora
    
    @classmethod
    def calcular_por_maquina_mes(
        cls,
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        leasing: Optional[List[Leasing]] = None
    ) -> Dict[Tuple[str, int], Dict[str, Decimal]]:
        """
        Calcula los gastos básicos por máquina y mes (repuestos, HH, leasing).
        
        Args:
            repuestos: Lista de entidades Repuesto (DATABODEGA)
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
        
        # Agregar gastos de repuestos (DATABODEGA)
        for repuesto in repuestos:
            clave = (repuesto.codigo_maquina, repuesto.fecha_salida.month)
            resultado[clave]['repuestos'] += repuesto.total
        
        # Agregar horas hombre y calcular costo
        for hh in horas_hombre:
            clave = (hh.codigo_maquina, hh.fecha.month)
            resultado[clave]['horas_hombre'] += hh.horas
            resultado[clave]['costo_hh'] += hh.horas * cls.COSTO_HORA_FIJO
        
        # Agregar leasing mensual
        if leasing:
            meses_trimestre = [10, 11, 12]
            for lease in leasing:
                for mes in meses_trimestre:
                    clave = (lease.codigo_maquina, mes)
                    resultado[clave]['leasing'] += lease.monto_cuota
        
        # Calcular total
        for clave in resultado:
            resultado[clave]['total'] = (
                resultado[clave]['repuestos'] +
                resultado[clave]['costo_hh'] +
                resultado[clave]['leasing']
            )
        
        return dict(resultado)
    
    @classmethod
    def calcular_por_maquina_mes_completo(
        cls,
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        gastos_operacionales: List[GastoOperacional],
        leasing: Optional[List[Leasing]] = None
    ) -> Dict[Tuple[str, int], Dict[str, Decimal]]:
        """
        Calcula los gastos agregados por máquina y mes con desglose completo.
        
        Args:
            repuestos: Lista de entidades Repuesto (DATABODEGA)
            horas_hombre: Lista de entidades HorasHombre
            gastos_operacionales: Lista de gastos de reportes contables
            leasing: Lista de entidades Leasing (opcional)
             
        Returns:
            Diccionario con clave (codigo_maquina, mes) y valor:
            {
                'repuestos': Decimal,
                'horas_hombre': Decimal,
                'costo_hh': Decimal,
                'leasing': Decimal,
                'combustibles': Decimal,
                'reparaciones': Decimal,
                'seguros': Decimal,
                'honorarios': Decimal,
                'epp': Decimal,
                'peajes': Decimal,
                'remuneraciones': Decimal,
                'permisos': Decimal,
                'alimentacion': Decimal,
                'pasajes': Decimal,
                'correspondencia': Decimal,
                'gastos_legales': Decimal,
                'multas': Decimal,
                'otros_gastos': Decimal,
                'total_gastos_operacionales': Decimal,
                'total': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'repuestos': Decimal('0'),
            'horas_hombre': Decimal('0'),
            'costo_hh': Decimal('0'),
            'leasing': Decimal('0'),
            'combustibles': Decimal('0'),
            'reparaciones': Decimal('0'),
            'seguros': Decimal('0'),
            'honorarios': Decimal('0'),
            'epp': Decimal('0'),
            'peajes': Decimal('0'),
            'remuneraciones': Decimal('0'),
            'permisos': Decimal('0'),
            'alimentacion': Decimal('0'),
            'pasajes': Decimal('0'),
            'correspondencia': Decimal('0'),
            'gastos_legales': Decimal('0'),
            'multas': Decimal('0'),
            'otros_gastos': Decimal('0'),
            'total_gastos_operacionales': Decimal('0'),
            'total': Decimal('0')
        })
        
        # Agregar gastos de repuestos (DATABODEGA)
        for repuesto in repuestos:
            clave = (repuesto.codigo_maquina, repuesto.fecha_salida.month)
            resultado[clave]['repuestos'] += repuesto.total
        
        # Agregar horas hombre y calcular costo
        for hh in horas_hombre:
            clave = (hh.codigo_maquina, hh.fecha.month)
            resultado[clave]['horas_hombre'] += hh.horas
            resultado[clave]['costo_hh'] += hh.horas * cls.COSTO_HORA_FIJO
        
        # Agregar leasing mensual
        if leasing:
            meses_trimestre = [10, 11, 12]
            for lease in leasing:
                for mes in meses_trimestre:
                    clave = (lease.codigo_maquina, mes)
                    resultado[clave]['leasing'] += lease.monto_cuota
        
        # Agregar gastos operacionales por tipo
        for gasto in gastos_operacionales:
            if gasto.es_ingreso:
                continue
            
            clave = (gasto.codigo_maquina, gasto.mes)
            
            # Clasificar por tipo de gasto
            if gasto.tipo_gasto == TipoGasto.COMBUSTIBLES.value:
                resultado[clave]['combustibles'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REPARACIONES.value:
                resultado[clave]['reparaciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SEGUROS.value:
                resultado[clave]['seguros'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.HONORARIOS.value:
                resultado[clave]['honorarios'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.EPP.value:
                resultado[clave]['epp'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PEAJES.value:
                resultado[clave]['peajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REMUNERACIONES.value:
                resultado[clave]['remuneraciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PERMISOS.value:
                resultado[clave]['permisos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ALIMENTACION.value:
                resultado[clave]['alimentacion'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PASAJES.value:
                resultado[clave]['pasajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.CORRESPONDENCIA.value:
                resultado[clave]['correspondencia'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.GASTOS_LEGALES.value:
                resultado[clave]['gastos_legales'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.MULTAS.value:
                resultado[clave]['multas'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTROS_GASTOS.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            # Agregar nuevos tipos de gasto
            elif gasto.tipo_gasto == TipoGasto.REVISION_TECNICA.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.VARIOS.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.MANTENCION_VARIOS.value:
                resultado[clave]['reparaciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTRO_GASTO_TALLER.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ALQUILER_MAQUINARIA.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SERVICIOS_EXTERNOS.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ELECTRICIDAD.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.AGUA.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTRO_GASTO_OPERACIONAL.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SUMINISTROS.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTROS_SUMINISTROS.value:
                resultado[clave]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto.startswith('401'):
                # Cualquier código 401 que no esté mapeado se clasifica como "otros_gastos"
                resultado[clave]['otros_gastos'] += gasto.monto
        
        # Calcular totales
        for clave in resultado:
            # Total de gastos operacionales (sin repuestos, ni HH, ni leasing)
            resultado[clave]['total_gastos_operacionales'] = (
                resultado[clave]['combustibles'] +
                resultado[clave]['reparaciones'] +
                resultado[clave]['seguros'] +
                resultado[clave]['honorarios'] +
                resultado[clave]['epp'] +
                resultado[clave]['peajes'] +
                resultado[clave]['remuneraciones'] +
                resultado[clave]['permisos'] +
                resultado[clave]['alimentacion'] +
                resultado[clave]['pasajes'] +
                resultado[clave]['correspondencia'] +
                resultado[clave]['gastos_legales'] +
                resultado[clave]['multas'] +
                resultado[clave]['otros_gastos']
            )
            
            # Total general
            resultado[clave]['total'] = (
                resultado[clave]['repuestos'] +
                resultado[clave]['costo_hh'] +
                resultado[clave]['leasing'] +
                resultado[clave]['total_gastos_operacionales']
            )
        
        return dict(resultado)
    
    @classmethod
    def calcular_total_por_maquina_completo(
        cls,
        repuestos: List[Repuesto],
        horas_hombre: List[HorasHombre],
        gastos_operacionales: List[GastoOperacional],
        leasing: Optional[List[Leasing]] = None
    ) -> Dict[str, Dict[str, Decimal]]:
        """
        Calcula los gastos totales por máquina con desglose completo.
        
        Args:
            repuestos: Lista de entidades Repuesto (DATABODEGA)
            horas_hombre: Lista de entidades HorasHombre
            gastos_operacionales: Lista de gastos de reportes contables
            leasing: Lista de entidades Leasing (opcional)
             
        Returns:
            Diccionario con clave codigo_maquina y valor:
            {
                'repuestos': Decimal,
                'horas_hombre': Decimal,
                'costo_hh': Decimal,
                'leasing': Decimal,
                'combustibles': Decimal,
                'reparaciones': Decimal,
                'seguros': Decimal,
                'honorarios': Decimal,
                'epp': Decimal,
                'peajes': Decimal,
                'remuneraciones': Decimal,
                'permisos': Decimal,
                'alimentacion': Decimal,
                'pasajes': Decimal,
                'correspondencia': Decimal,
                'gastos_legales': Decimal,
                'multas': Decimal,
                'otros_gastos': Decimal,
                'total_gastos_operacionales': Decimal,
                'total': Decimal
            }
        """
        resultado = defaultdict(lambda: {
            'repuestos': Decimal('0'),
            'horas_hombre': Decimal('0'),
            'costo_hh': Decimal('0'),
            'leasing': Decimal('0'),
            'combustibles': Decimal('0'),
            'reparaciones': Decimal('0'),
            'seguros': Decimal('0'),
            'honorarios': Decimal('0'),
            'epp': Decimal('0'),
            'peajes': Decimal('0'),
            'remuneraciones': Decimal('0'),
            'permisos': Decimal('0'),
            'alimentacion': Decimal('0'),
            'pasajes': Decimal('0'),
            'correspondencia': Decimal('0'),
            'gastos_legales': Decimal('0'),
            'multas': Decimal('0'),
            'otros_gastos': Decimal('0'),
            'total_gastos_operacionales': Decimal('0'),
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
        
        # Agregar leasing (3 meses del trimestre)
        if leasing:
            for lease in leasing:
                codigo = lease.codigo_maquina
                resultado[codigo]['leasing'] += lease.monto_cuota * Decimal('3')
        
        # Agregar gastos operacionales por tipo
        for gasto in gastos_operacionales:
            if gasto.es_ingreso:
                continue
            
            codigo = gasto.codigo_maquina
            
            if gasto.tipo_gasto == TipoGasto.COMBUSTIBLES.value:
                resultado[codigo]['combustibles'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REPARACIONES.value:
                resultado[codigo]['reparaciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SEGUROS.value:
                resultado[codigo]['seguros'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.HONORARIOS.value:
                resultado[codigo]['honorarios'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.EPP.value:
                resultado[codigo]['epp'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PEAJES.value:
                resultado[codigo]['peajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.REMUNERACIONES.value:
                resultado[codigo]['remuneraciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PERMISOS.value:
                resultado[codigo]['permisos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ALIMENTACION.value:
                resultado[codigo]['alimentacion'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.PASAJES.value:
                resultado[codigo]['pasajes'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.CORRESPONDENCIA.value:
                resultado[codigo]['correspondencia'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.GASTOS_LEGALES.value:
                resultado[codigo]['gastos_legales'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.MULTAS.value:
                resultado[codigo]['multas'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTROS_GASTOS.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            # Agregar nuevos tipos de gasto
            elif gasto.tipo_gasto == TipoGasto.REVISION_TECNICA.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.VARIOS.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.MANTENCION_VARIOS.value:
                resultado[codigo]['reparaciones'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTRO_GASTO_TALLER.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ALQUILER_MAQUINARIA.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SERVICIOS_EXTERNOS.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.ELECTRICIDAD.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.AGUA.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTRO_GASTO_OPERACIONAL.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.SUMINISTROS.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
            elif gasto.tipo_gasto == TipoGasto.OTROS_SUMINISTROS.value:
                resultado[codigo]['otros_gastos'] += gasto.monto
        
        # Calcular totales
        for codigo in resultado:
            resultado[codigo]['total_gastos_operacionales'] = (
                resultado[codigo]['combustibles'] +
                resultado[codigo]['reparaciones'] +
                resultado[codigo]['seguros'] +
                resultado[codigo]['honorarios'] +
                resultado[codigo]['epp'] +
                resultado[codigo]['peajes'] +
                resultado[codigo]['remuneraciones'] +
                resultado[codigo]['permisos'] +
                resultado[codigo]['alimentacion'] +
                resultado[codigo]['pasajes'] +
                resultado[codigo]['correspondencia'] +
                resultado[codigo]['gastos_legales'] +
                resultado[codigo]['multas'] +
                resultado[codigo]['otros_gastos']
            )
            
            resultado[codigo]['total'] = (
                resultado[codigo]['repuestos'] +
                resultado[codigo]['costo_hh'] +
                resultado[codigo]['leasing'] +
                resultado[codigo]['total_gastos_operacionales']
            )
        
        return dict(resultado)
