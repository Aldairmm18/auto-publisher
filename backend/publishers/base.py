"""
Clase base para todos los publishers de redes sociales.
Cada plataforma hereda de esta clase e implementa sus métodos.
"""

from abc import ABC, abstractmethod


class BasePublisher(ABC):
    """Interfaz común para todos los publishers."""
    
    platform: str = "unknown"
    
    @abstractmethod
    async def publish(self, text: str, media_path: str | None = None, **kwargs) -> dict:
        """
        Publica contenido en la plataforma.
        
        Args:
            text: Texto/caption de la publicación
            media_path: Ruta al archivo de video o imagen (opcional)
            **kwargs: Parámetros adicionales específicos de la plataforma
        
        Returns:
            dict con al menos: {"success": bool, "post_id": str, "url": str}
        """
        pass
    
    @abstractmethod
    async def validate_credentials(self) -> bool:
        """Verifica que las credenciales de la plataforma sean válidas."""
        pass
    
    def get_platform_name(self) -> str:
        """Retorna el nombre de la plataforma."""
        return self.platform
