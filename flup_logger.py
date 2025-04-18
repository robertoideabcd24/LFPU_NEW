# flup_logger.py
import json
import os
from datetime import datetime
import sys
import traceback
from typing import Optional, Dict, Any
from pathlib import Path

class BasicFlupLogger:
    def __init__(self, log_dir: str = "flup_logs"):
        """
        Logger básico que guarda ejecuciones en archivos JSON.
        
        Args:
            log_dir: Directorio donde se guardarán los logs (por defecto: flup_logs en el home del usuario)
        """
        # Definir la ruta base como el home del usuario
        home_dir = str(Path.home())
        self.log_dir = os.path.join(home_dir, log_dir)
        
        # Asegurarse de que el directorio existe
        os.makedirs(self.log_dir, exist_ok=True)
        
        # Configuración básica
        self.user = self._get_current_user()
        self.session_id = self._generate_session_id()
        
    def log_execution(
        self,
        source_code: str,
        output: Optional[str] = None,
        error: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Registra una ejecución en el log.
        
        Args:
            source_code: Código fuente ejecutado
            output: Salida estándar generada
            error: Mensaje de error (si ocurrió)
            metadata: Metadatos adicionales
            
        Returns:
            Dict con el registro creado
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "user": self.user,
            "session_id": self.session_id,
            "source_code": source_code,
            "output": output,
            "error": self._format_error(error) if error else None,
            "metadata": metadata or {},
            "system": {
                "python_version": sys.version,
                "platform": sys.platform,
                "working_dir": os.getcwd()
            }
        }
        
        # Nombre del archivo basado en la fecha
        log_file = os.path.join(
            self.log_dir,
            f"flup_{datetime.now().strftime('%Y%m%d')}.json"
        )
        
        # Escribir el log (append al archivo)
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            
        return log_entry
    
    def _format_error(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la información de error para el log"""
        return {
            "type": error.get("type"),
            "message": error.get("message"),
            "traceback": error.get("traceback")
        }
    
    def log_error(self, source_code: str, exception: Exception) -> Dict[str, Any]:
        """
        Registra un error en el log.
        
        Args:
            source_code: Código que causó el error
            exception: Excepción capturada
            
        Returns:
            Dict con el registro de error
        """
        error_info = {
            "type": type(exception).__name__,
            "message": str(exception),
            "traceback": traceback.format_exc()
        }
        
        return self.log_execution(
            source_code=source_code,
            error=error_info,
            metadata={"success": False}
        )
    
    def _get_current_user(self) -> str:
        """Obtiene el usuario actual del sistema"""
        try:
            return os.getlogin()
        except:
            try:
                return os.getenv('USER') or os.getenv('USERNAME') or "unknown"
            except:
                return "unknown"
    
    def _generate_session_id(self) -> str:
        """Genera un ID único para la sesión actual"""
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{os.getpid()}"