import os
import json
import yaml
from datetime import datetime
from fpdf import FPDF
from PIL import Image, ImageDraw, ImageFont
from rich import print as rprint

IDENTITY_PATH = "reflection/identity_state.yaml"
HISTORY_PATH = "reflection/cycle_history.json"
EXPORT_IMG_DIR = "exports/identities"
EXPORT_PDF_DIR = "exports/reports"
ALERT_LOG = "logs/alerts.log"

def load_identity():
    with open(IDENTITY_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

def load_history():
    with open(HISTORY_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def draw_image(agent_name, data):
    img = Image.new("RGB", (400, 250), color=(245, 245, 245))
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    draw.text((10, 10), f"🧠 {agent_name}", fill=(0, 0, 0), font=font)
    draw.text((10, 40), f"Padrão: {data.get('predominant_pattern')}", fill=(0, 0, 0), font=font)
    draw.text((10, 60), f"Consistência: {data.get('consistency_level')}", fill=(0, 0, 0), font=font)
    draw.text((10, 80), f"Última adaptação: {data.get('last_adaptation')}", fill=(0, 0, 0), font=font)
    draw.text((10, 100), f"Traços: {', '.join(data.get('traits', []))}", fill=(0, 0, 0), font=font)
    hint = data.get("adaptive_hint", "Nenhum")
    draw.text((10, 140), f"⚠️ Recomendações: {hint}", fill=(100, 0, 0), font=font)

    img_path = os.path.join(EXPORT_IMG_DIR, f"{agent_name}.png")
    img.save(img_path)

def generate_pdf(identity, history):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for agent, data in identity.items():
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Agente: {agent}", ln=True)
        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 10, f"Padrão predominante: {data.get('predominant_pattern')}", ln=True)
        pdf.cell(0, 10, f"Consistência: {data.get('consistency_level')}", ln=True)
        pdf.cell(0, 10, f"Última adaptação: {data.get('last_adaptation')}", ln=True)
        pdf.cell(0, 10, f"Traços: {', '.join(data.get('traits', []))}", ln=True)
        pdf.cell(0, 10, f"Recomendação simbólica: {data.get('adaptive_hint')}", ln=True)

        pdf.cell(0, 10, "Histórico recente:", ln=True)
        for i, p in enumerate(reversed(history.get(agent, [])[-5:]), 1):
            pdf.cell(0, 10, f"{i}. {p}", ln=True)

    filename = os.path.join(EXPORT_PDF_DIR, f"snapshot_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.pdf")
    pdf.output(filename)

def check_alerts(identity):
    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        for agent, data in identity.items():
            hint = data.get("adaptive_hint", "")
            if "anomalia" in hint.lower():
                message = f"[{datetime.now()}] ALERTA: {agent} com padrão anômalo persistente"
                rprint(f"[bold red]{message}[/bold red]")
                f.write(message + "\n")

def main():
    identity = load_identity()
    history = load_history()

    for agent, data in identity.items():
        draw_image(agent, data)

    generate_pdf(identity, history)
    check_alerts(identity)
    rprint("[bold green]✅ Relatórios gerados com sucesso![/bold green]")

if __name__ == "__main__":
    main()