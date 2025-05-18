import schedule
import time
from datetime import datetime
from core.main import run_project
from pathlib import Path

LOG_PATH = Path("logs/cycle_log.txt")

def log_cycle_start(cycle_num):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    message = f"\n⏰ Ciclo {cycle_num} iniciado às {now}\n"
    print(message.strip())
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write(message)

def run_scheduled_cycle():
    run_scheduled_cycle.counter += 1
    log_cycle_start(run_scheduled_cycle.counter)
    run_project()
    with open(LOG_PATH, "a", encoding="utf-8") as log_file:
        log_file.write("✅ Reflexão completa\n")

run_scheduled_cycle.counter = 0

def main():
    print("🔁 Iniciando modo contínuo de ciclos reflexivos (CTRL+C para parar)")
    schedule.every(1).minutes.do(run_scheduled_cycle)

    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()