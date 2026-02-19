"""Test de verificación de la implementación de precios híbridos."""

from decimal import Decimal
from src.domain.entities.PreciosContrato import PreciosContrato
from src.infrastructure.excel.PreciosContratoExcelReader import PreciosContratoExcelReader
from src.domain.services.PreciosContratoService import PreciosContratoService


def test_precios_contrato():
    """Test básico de la entidad PreciosContrato."""
    print("=== Test PreciosContrato ===")
    precio = PreciosContrato(
        contrato_id='CT00052KmHr',
        tipo='Km , Hr',
        precio_hora=Decimal('35000'),
        precio_km=Decimal('2500')
    )

    print(f"  - Contrato: {precio.contrato_id}")
    print(f"  - Tipo: {precio.tipo}")
    print(f"  - Es hibrido: {precio.is_hibrido()}")
    print(f"  - Tiene precio hora: {precio.has_precio('HORA')}")
    print(f"  - Tiene precio km: {precio.has_precio('KM')}")
    print(f"  - Num precios: {precio.num_precios()}")

    # Test de cálculo de producción híbrida
    valor, unidades, desglose = precio.calcular_valor_produccion(
        horas=Decimal('3'),
        km=Decimal('100'),
        mt3=Decimal('0'),
        vueltas=Decimal('0'),
        dias=Decimal('0')
    )
    print(f"  - Valor produccion (3Hr + 100Km): ${int(valor):,}")
    print(f"  - Unidades usadas: {unidades}")
    print(f"  - Desglose: {desglose}")


def test_servicio_precios():
    """Test del servicio de precios."""
    print("\n=== Test PreciosContratoService ===")

    # Crear algunos precios de prueba
    precios = {
        'CT00052KmHr': PreciosContrato(
            contrato_id='CT00052KmHr',
            tipo='Km , Hr',
            precio_hora=Decimal('35000'),
            precio_km=Decimal('2500')
        ),
        'CT01017Hr': PreciosContrato(
            contrato_id='CT01017Hr',
            tipo='Hr',
            precio_hora=Decimal('30000'),
            precio_km=Decimal('0'),
            precio_mt3=Decimal('0')
        ),
        'CT00306Hr': PreciosContrato(
            contrato_id='CT00306Hr',
            tipo='Hr, Unidades',
            precio_hora=Decimal('0'),
            precio_km=Decimal('0'),
            precio_mt3=Decimal('0')
        )
    }

    servicio = PreciosContratoService()
    servicio.cargar_precios_dict(precios)

    # Test get_precios
    precio = servicio.get_precios('CT00052KmHr')
    print(f"  - Precios CT00052KmHr: {precio.get_resumen_precios()}")

    # Test has_precio
    print(f"  - CT00052KmHr tiene precio HORA: {servicio.has_precio('CT00052KmHr', 'HORA')}")
    print(f"  - CT00052KmHr tiene precio KM: {servicio.has_precio('CT00052KmHr', 'KM')}")

    # Test calcular_valor_produccion
    valor, unidades, desglose, es_hibrido, tiene_precio = servicio.calcular_valor_produccion(
        'CT00052KmHr',
        horas=Decimal('5'),
        km=Decimal('50')
    )
    print(f"  - CT00052KmHr (5Hr + 50Km): ${int(valor):,}, Hibrido: {es_hibrido}, TienePrecio: {tiene_precio}")

    # Test contratos sin precio
    sin_precio = servicio.get_contratos_sin_precio()
    print(f"  - Contratos sin precio: {sin_precio}")

    # Test contratos hibridos
    hibridos = servicio.get_contratos_hibridos()
    print(f"  - Contratos hibridos: {hibridos}")

    # Test estadisticas
    stats = servicio.get_estadisticas()
    print(f"  - Estadisticas: {stats}")


def test_casos_reales():
    """Test con casos reales del Excel."""
    print("\n=== Test Casos Reales ===")

    # Caso 1: Contrato simple (CT01017Hr: 5Hr @ $30000)
    contrato_simple = PreciosContrato('CT01017Hr', 'Hr', precio_hora=Decimal('30000'))
    v1, u1, d1 = contrato_simple.calcular_valor_produccion(horas=Decimal('5'))
    print(f"  - CT01017Hr (5Hr @ $30,000): ${int(v1):,}")

    # Caso 2: Híbrido Km+Hr (CT00052KmHr: 3Hr @ $35,000 + 100Km @ $2,500)
    contrato_hibrido1 = PreciosContrato(
        'CT00052KmHr', 'Km , Hr',
        precio_hora=Decimal('35000'),
        precio_km=Decimal('2500')
    )
    v2, u2, d2 = contrato_hibrido1.calcular_valor_produccion(
        horas=Decimal('3'),
        km=Decimal('100')
    )
    print(f"  - CT00052KmHr (3Hr @ $35,000 + 100Km @ $2,500): ${int(v2):,}")

    # Caso 3: Híbrido Mt3+Km (CT00060Mt3Km: 50Mt3 @ $1,800 + 200Km @ $2,800)
    contrato_hibrido2 = PreciosContrato(
        'CT00060Mt3Km', 'Mt3 , Km',
        precio_mt3=Decimal('1800'),
        precio_km=Decimal('2800')
    )
    v3, u3, d3 = contrato_hibrido2.calcular_valor_produccion(
        mt3=Decimal('50'),
        km=Decimal('200')
    )
    print(f"  - CT00060Mt3Km (50Mt3 @ $1,800 + 200Km @ $2,800): ${int(v3):,}")

    # Caso 4: Sin precio (CT00306Hr)
    contrato_sin_precio = PreciosContrato('CT00306Hr', 'Hr, Unidades')
    v4, u4, d4 = contrato_sin_precio.calcular_valor_produccion(horas=Decimal('4'))
    print(f"  - CT00306Hr (4Hr, sin precio): ${int(v4):,} (DEBERÍA SER 0)")

    # Verificar
    assert v1 == Decimal('150000'), f"Expected 150000, got {v1}"
    assert v2 == Decimal('355000'), f"Expected 355000, got {v2}"  # 3*35000 + 100*2500 = 105000 + 250000
    assert v3 == Decimal('650000'), f"Expected 650000, got {v3}"  # 50*1800 + 200*2800 = 90000 + 560000
    assert v4 == Decimal('0'), f"Expected 0, got {v4}"
    print("\n  Todas las aserciones pasaron!")


if __name__ == '__main__':
    test_precios_contrato()
    test_servicio_precios()
    test_casos_reales()
    print("\n=== TODOS LOS TESTS PASARON ===")
