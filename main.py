"""
Punto de entrada principal del sistema de informes.

Ejecuta el proceso completo de generación de informes de producción vs gastos.
"""

import os
from pathlib import Path
from decimal import Decimal
from src.application.InformeService import InformeService
from src.domain.services.ValorUFService import ValorUFService


def main():
    """
    Función principal que ejecuta el proceso de generación de informes.
    """
    print("=" * 60)
    print("SISTEMA DE INFORMES - PRODUCCIÓN VS GASTOS")
    print("Trimestre Q4 2025 (Octubre, Noviembre, Diciembre)")
    print("=" * 60)
    print()
    
    # Rutas de los archivos CSV
    ruta_base = Path(__file__).parent
    ruta_gastos = ruta_base / "gastos"
    
    # Buscar archivos primero en carpeta gastos, luego en raíz
    ruta_produccion = ruta_gastos / "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv"
    if not ruta_produccion.exists():
        ruta_produccion = ruta_base / "Harcha Maquinaria - Reportaría_Reportes_Tabla (3).csv"
    
    ruta_horas_hombre = ruta_gastos / "_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv"
    if not ruta_horas_hombre.exists():
        ruta_horas_hombre = ruta_base / "_Harcha Maquinaria- HH_Copia de MAQVSOTSVSHH_Tabla.csv"
    
    ruta_repuestos = ruta_gastos / "DATABODEGA.csv"
    if not ruta_repuestos.exists():
        ruta_repuestos = ruta_base / "DATABODEGA.csv"
    
    ruta_leasing = ruta_gastos / "Leasing Credito HMAQ.csv"
    if not ruta_leasing.exists():
        ruta_leasing = ruta_base / "Leasing Credito HMAQ.csv"
    
    # Verificar que los archivos existan
    archivos_faltantes = []
    if not ruta_produccion.exists():
        archivos_faltantes.append(str(ruta_produccion))
    if not ruta_horas_hombre.exists():
        archivos_faltantes.append(str(ruta_horas_hombre))
    if not ruta_repuestos.exists():
        archivos_faltantes.append(str(ruta_repuestos))
    # Leasing es opcional, no se agrega a archivos_faltantes
    
    if archivos_faltantes:
        print("[ERROR] Los siguientes archivos no se encontraron:")
        for archivo in archivos_faltantes:
            print(f"   - {archivo}")
        return
    
    # Rutas de salida
    ruta_excel = ruta_base / "informe_produccion_gastos.xlsx"
    ruta_html = ruta_base / "informe_produccion_gastos.html"
    
    print(f"Costo fijo por hora de trabajo: $35.000 CLP")
    print()
    
    # Obtener valor de la UF
    print("Obteniendo valor de la UF...")
    uf_service = ValorUFService()
    valor_uf = uf_service.obtener_valor_uf()
    print(f"  Valor UF utilizado: ${valor_uf:,.0f} CLP")
    print("  (Nota: Si necesitas actualizar el valor, edita config_uf.json o proporciona el valor manualmente)")
    print()
    
    # Crear servicio y generar informes
    try:
        servicio = InformeService(
            ruta_produccion=str(ruta_produccion),
            ruta_horas_hombre=str(ruta_horas_hombre),
            ruta_repuestos=str(ruta_repuestos),
            ruta_leasing=str(ruta_leasing) if ruta_leasing.exists() else None,
            valor_uf=valor_uf
        )
        
        servicio.generar_informes(
            ruta_excel=str(ruta_excel),
            ruta_html=str(ruta_html)
        )
        
        print()
        print("=" * 60)
        print("ARCHIVOS GENERADOS:")
        print(f"  Excel: {ruta_excel}")
        print(f"  HTML: {ruta_html}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n[ERROR] Error durante la ejecucion: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
