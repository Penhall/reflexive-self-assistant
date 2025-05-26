"""
Logger básico para registro de interações e reflexões.
"""

def log(message):
    from datetime import datetime
    print(f"[{datetime.now()}] {message}")