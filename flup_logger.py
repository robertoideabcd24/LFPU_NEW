import json
import os
from datetime import datetime
import sys
import traceback
from typing import Optional, Dict, Any, List, Union
from pathlib import Path
import uuid

class BasicFlupLogger:
    def __init__(self, log_dir: str = "flup_logs", max_log_size: int = 5):
        """
        Logger mejorado para FLUP con rotación de archivos.
        
        Args:
            log_dir: Directorio para logs (relativo al home del usuario)
            max_log_size: Tamaño máximo en MB antes de rotar archivos
        """
        self.log_dir = self._setup_log_dir(log_dir)
        self.max_log_size = max_log_size * 1024 * 1024  # Convertir a bytes
        self.session_id = self._generate_session_id()
        self.current_log_file = self._get_current_log_file()
        
    def _setup_log_dir(self, log_dir: str) -> str:
        """Configura el directorio de logs"""
        log_path = Path.home() / log_dir
        log_path.mkdir(exist_ok=True, parents=True)
        return str(log_path)
    
    def log_execution(
        self,
        source_code: str,
        output: Optional[Union[str, List, Dict]] = None,
        error: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        command_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Registra una ejecución con mejor manejo de tipos complejos.
        
        Args:
            source_code: Código ejecutado
            output: Salida generada (puede ser str, lista o dict)
            error: Información de error
            metadata: Metadatos adicionales
            command_type: Tipo de comando (print, assign, class, etc.)
        """
        log_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "session_id": self.session_id,
            "command": source_code,
            "type": command_type or "execution",
            "output": output,
            "error": self._format_error(error) if error else None,
            "metadata": metadata or {},
            "system": self._get_system_info()
        }
        
        self._write_log(log_entry)
        return log_entry
    
    def log_error(self, source_code: str, exception: Exception) -> Dict[str, Any]:
        """Registra errores con stack trace completo"""
        exc_type = type(exception).__name__
        
        return self.log_execution(
            source_code=source_code,
            error={
                "type": exc_type,
                "message": str(exception),
                "traceback": traceback.format_exc()
            },
            metadata={"success": False},
            command_type="error"
        )
    
    def _write_log(self, entry: Dict[str, Any]):
        # No mostrar en terminal
        if os.path.exists(self.current_log_file):
            file_size = os.path.getsize(self.current_log_file)
            if file_size >= self.max_log_size:
                self._rotate_log_file()
        
        with open(self.current_log_file, 'a', encoding='utf-8') as f:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')

    
    def _rotate_log_file(self):
        """Rota el archivo de log cuando alcanza el tamaño máximo"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        new_name = f"flup_{timestamp}_{uuid.uuid4().hex[:6]}.json"
        os.rename(self.current_log_file, os.path.join(self.log_dir, new_name))
        self.current_log_file = self._get_current_log_file()
    
    def _get_current_log_file(self) -> str:
        """Obtiene el archivo de log actual basado en la fecha"""
        return os.path.join(
            self.log_dir,
            f"flup_{datetime.now().strftime('%Y%m%d')}.json"
        )
    
    def _generate_session_id(self) -> str:
        """Genera un ID de sesión único"""
        return f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}"
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Obtiene información del sistema"""
        return {
            "python": sys.version,
            "platform": sys.platform,
            "cwd": os.getcwd(),
            "user": self._get_current_user()
        }
    
    def _get_current_user(self) -> str:
        """Obtiene el usuario actual"""
        return os.getenv('USER') or os.getenv('USERNAME') or "unknown"
    
    def _format_error(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la información de error"""
        return {
            "type": error.get("type"),
            "message": error.get("message"),
            "traceback": error.get("traceback", "").splitlines()
        }