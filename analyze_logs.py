import json
import re
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter, defaultdict
import pytz
from pathlib import Path

class FLUPAnalyzer:
    def __init__(self, logs):
        self.logs = logs
        self.TIMEZONE = pytz.timezone('America/Mexico_City')
        self.REPORT_DIR = Path("flup_analysis")
        self.REPORT_DIR.mkdir(exist_ok=True)
        
        # Patrones para análisis léxico
        self.syntax_patterns = {
            'asignacion': r':=',
            'impresion': r'Prt\(',
            'condicional': r'if\s*\(',
            'operacion_binaria': r'OperacionBinaria\(',
            'cadena': r'Cadena\(',
            'variable': r'Variable\(',
            'clase': r'class\s+',
            'instancia': r':=\s*\w+\s*\('
        }

    def analyze_errors(self):
        """Analiza errores de sintaxis y ejecución"""
        errors = []
        
        for log in self.logs:
            if log.get('error'):
                error_data = {
                    'type': log['error'].get('type', 'Desconocido'),
                    'message': log['error'].get('message', ''),
                    'timestamp': log['timestamp'],
                    'session': log.get('session_id', ''),
                    'command': log.get('command', '')[:100]  # Primeros 100 caracteres
                }
                errors.append(error_data)
        
        if not errors:
            print("✅ No se encontraron errores en los logs")
            return
        
        # Análisis de errores
        df_errors = pd.DataFrame(errors)
        
        # Top errores por tipo
        error_counts = df_errors['type'].value_counts()
        plt.figure(figsize=(10, 6))
        error_counts.plot(kind='bar', color='coral')
        plt.title('Errores más comunes por tipo')
        plt.xlabel('Tipo de error')
        plt.ylabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(self.REPORT_DIR / 'errores_comunes.png')
        
        # Guardar detalles
        df_errors.to_csv(self.REPORT_DIR / 'detalle_errores.csv', index=False)
        print(f"📊 Reporte de errores guardado en {self.REPORT_DIR}")

    def analyze_syntax_usage(self):
        """Analiza frecuencia de estructuras sintácticas"""
        syntax_stats = defaultdict(int)
        
        for log in self.logs:
            if not log.get('command'):
                continue
                
            for pattern_name, pattern in self.syntax_patterns.items():
                if re.search(pattern, log['command']):
                    syntax_stats[pattern_name] += 1
        
        # Gráfico de uso de sintaxis
        df_syntax = pd.DataFrame.from_dict(syntax_stats, orient='index', columns=['count'])
        df_syntax.sort_values('count', ascending=False, inplace=True)
        
        plt.figure(figsize=(10, 6))
        df_syntax.plot(kind='barh', legend=False, color='teal')
        plt.title('Uso de estructuras sintácticas')
        plt.xlabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(self.REPORT_DIR / 'uso_sintaxis.png')
        
        df_syntax.to_csv(self.REPORT_DIR / 'frecuencia_sintaxis.csv')
        print(f"📊 Análisis sintáctico guardado en {self.REPORT_DIR}")

    def analyze_variables(self):
        """Analiza uso de variables y tipos de datos"""
        var_usage = Counter()
        var_types = defaultdict(set)
        
        for log in self.logs:
            if not log.get('metadata', {}).get('memory_snapshot'):
                continue
                
            memory = log['metadata']['memory_snapshot']
            for var, value in memory.items():
                var_usage[var] += 1
                var_types[var].add(self.detect_type(value))
        
        if not var_usage:
            print("⚠️ No se encontró información de variables en los logs")
            return
        
        # Procesar datos
        df_vars = pd.DataFrame.from_dict(var_usage, orient='index', columns=['count'])
        df_vars['types'] = df_vars.index.map(lambda x: ', '.join(var_types[x]))
        df_vars.sort_values('count', ascending=False, inplace=True)
        
        # Gráfico de variables más usadas
        plt.figure(figsize=(10, 6))
        df_vars.head(15)['count'].plot(kind='barh', color='lightgreen')
        plt.title('Variables más utilizadas')
        plt.xlabel('Frecuencia')
        plt.tight_layout()
        plt.savefig(self.REPORT_DIR / 'variables_comunes.png')
        
        df_vars.to_csv(self.REPORT_DIR / 'uso_variables.csv')
        print(f"📊 Análisis de variables guardado en {self.REPORT_DIR}")

    def detect_type(self, value):
        """Detecta el tipo de dato de un valor"""
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif value is None:
            return 'None'
        return 'unknown'

    def analyze_temporal_patterns(self):
        """Analiza patrones temporales de uso"""
        timestamps = []
        command_types = []
        
        for log in self.logs:
            try:
                dt = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
                dt = dt.astimezone(self.TIMEZONE)
                timestamps.append(dt)
                
                # Clasificar tipo de comando
                cmd_type = 'other'
                if log.get('error'):
                    cmd_type = 'error'
                elif 'Prt(' in log.get('command', ''):
                    cmd_type = 'print'
                elif ':=' in log.get('command', ''):
                    cmd_type = 'assignment'
                elif 'if(' in log.get('command', ''):
                    cmd_type = 'conditional'
                    
                command_types.append(cmd_type)
            except (ValueError, KeyError):
                continue
        
        if not timestamps:
            print("⚠️ No se encontraron timestamps válidos")
            return
        
        # Crear DataFrame temporal
        df_time = pd.DataFrame({
            'timestamp': timestamps,
            'hour': [t.hour for t in timestamps],
            'weekday': [t.strftime('%A') for t in timestamps],
            'command_type': command_types
        })
        
        # Uso por hora del día
        plt.figure(figsize=(12, 6))
        df_time.groupby('hour').size().plot(kind='bar', color='purple')
        plt.title('Uso del lenguaje por hora del día')
        plt.xlabel('Hora del día')
        plt.ylabel('Comandos ejecutados')
        plt.tight_layout()
        plt.savefig(self.REPORT_DIR / 'uso_por_hora.png')
        
        # Guardar datos temporales
        df_time.to_csv(self.REPORT_DIR / 'datos_temporales.csv', index=False)
        print(f"📊 Análisis temporal guardado en {self.REPORT_DIR}")

    def generate_full_report(self):
        """Genera reporte completo con todos los análisis"""
        print("\n🔍 Iniciando análisis completo de FLUP...")
        
        self.analyze_errors()
        self.analyze_syntax_usage()
        self.analyze_variables()
        self.analyze_temporal_patterns()
        
        print("\n✅ Análisis completado. Resultados en:", self.REPORT_DIR)

def load_logs_from_dir(log_dir):
    """Carga logs desde un directorio"""
    log_files = list(Path(log_dir).glob('flup_*.json'))
    if not log_files:
        raise FileNotFoundError(f"No se encontraron archivos de log en {log_dir}")
    
    logs = []
    for file in sorted(log_files):
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    logs.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return logs

if __name__ == "__main__":
    # Configuración
    LOG_DIR = Path.home() / "flup_logs"
    
    try:
        print(f"📂 Cargando logs desde {LOG_DIR}...")
        logs = load_logs_from_dir(LOG_DIR)
        
        analyzer = FLUPAnalyzer(logs)
        analyzer.generate_full_report()
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")