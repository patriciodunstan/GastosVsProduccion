"""
Servicio de dominio: ValorUFService

Obtiene el valor actual de la UF (Unidad de Fomento) de Chile.
Sigue el principio de responsabilidad única (SRP).
"""

import json
from decimal import Decimal
from datetime import datetime
from typing import Optional
from pathlib import Path
import urllib.request
import urllib.error


class ValorUFService:
    """
    Servicio para obtener el valor de la UF.
    
    Intenta obtener el valor desde una API pública, y si falla,
    usa un valor por defecto o lo lee de un archivo de configuración.
    """
    
    # API pública de la UF (usando mindicador.cl)
    API_UF_URL = "https://mindicador.cl/api/uf"
    
    # Valor por defecto de la UF (aproximado para diciembre 2025)
    # Este valor debería actualizarse o obtenerse dinámicamente
    UF_DEFAULT = Decimal('38000')  # Valor aproximado
    
    def __init__(self, valor_uf_manual: Optional[Decimal] = None):
        """
        Inicializa el servicio.
        
        Args:
            valor_uf_manual: Valor manual de la UF si se proporciona
        """
        self.valor_uf_manual = valor_uf_manual
        self._valor_uf_cache = None
    
    def obtener_valor_uf(self, fecha: Optional[datetime] = None) -> Decimal:
        """
        Obtiene el valor de la UF para una fecha específica.
        
        Args:
            fecha: Fecha para la cual obtener la UF (opcional, usa hoy si no se proporciona)
            
        Returns:
            Valor de la UF en pesos chilenos
        """
        # Si hay un valor manual, usarlo
        if self.valor_uf_manual:
            return self.valor_uf_manual
        
        # Si hay un valor en caché, usarlo
        if self._valor_uf_cache:
            return self._valor_uf_cache
        
        # Intentar obtener desde API
        try:
            valor = self._obtener_desde_api(fecha)
            if valor:
                self._valor_uf_cache = valor
                return valor
        except Exception:
            # Si falla la API, continuar con otras opciones
            pass
        
        # Intentar leer desde archivo de configuración
        try:
            valor = self._obtener_desde_archivo()
            if valor:
                self._valor_uf_cache = valor
                return valor
        except Exception:
            pass
        
        # Usar valor por defecto
        return self.UF_DEFAULT
    
    def _obtener_desde_api(self, fecha: Optional[datetime] = None) -> Optional[Decimal]:
        """
        Obtiene el valor de la UF desde la API pública.
        
        Args:
            fecha: Fecha para la cual obtener la UF
            
        Returns:
            Valor de la UF o None si falla
        """
        try:
            url = self.API_UF_URL
            if fecha:
                # Formato: YYYY-MM-DD
                fecha_str = fecha.strftime('%Y-%m-%d')
                url = f"{self.API_UF_URL}/{fecha_str}"
            
            with urllib.request.urlopen(url, timeout=5) as response:
                data = json.loads(response.read().decode())
                
                # La API retorna: {"uf": {"codigo": "uf", "nombre": "Unidad de Fomento", "unidad_medida": "Pesos", "fecha": "...", "valor": 38000.XX}}
                if 'uf' in data and 'valor' in data['uf']:
                    return Decimal(str(data['uf']['valor']))
                
                # Si es un array (para fechas específicas)
                if isinstance(data, list) and len(data) > 0:
                    if 'valor' in data[0]:
                        return Decimal(str(data[0]['valor']))
        except (urllib.error.URLError, urllib.error.HTTPError, KeyError, ValueError, Exception):
            return None
        
        return None
    
    def _obtener_desde_archivo(self) -> Optional[Decimal]:
        """
        Lee el valor de la UF desde un archivo de configuración.
        
        Returns:
            Valor de la UF o None si no existe el archivo
        """
        archivo_config = Path('config_uf.json')
        
        if not archivo_config.exists():
            return None
        
        try:
            with open(archivo_config, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'valor_uf' in config:
                    return Decimal(str(config['valor_uf']))
        except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
            return None
        
        return None
    
    def establecer_valor_uf(self, valor: Decimal):
        """
        Establece manualmente el valor de la UF.
        
        Args:
            valor: Valor de la UF en pesos chilenos
        """
        self.valor_uf_manual = valor
        self._valor_uf_cache = valor
