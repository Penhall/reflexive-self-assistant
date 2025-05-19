import yaml
from datetime import datetime

IDENTITY_FILE = "reflection/identity_state.yaml"
EMOTION_FILE = "reflection/emotional_state.yaml"
TIMELINE_FILE = "reflection/symbolic_timeline.yaml"

class TimelineBuilder:
    def __init__(self):
        self.timeline = self.load_yaml(TIMELINE_FILE)
        self.identity = self.load_yaml(IDENTITY_FILE)
        self.emotion = self.load_yaml(EMOTION_FILE)

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except:
            return {}

    def append_to_timeline(self):
        ciclo = self.emotion.get("emotional_state", {}).get("ciclo", 0)
        emocao = self.emotion.get("emotional_state", {}).get("status", "Indefinido")
        identidade = self.summarize_identity()
        evento = self.generate_evento(identidade, emocao)

        entry = {
            "ciclo": ciclo,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "identidade": identidade,
            "emoção": emocao,
            "evento": evento
        }

        if "linha_temporal" not in self.timeline:
            self.timeline["linha_temporal"] = []

        self.timeline["linha_temporal"].append(entry)
        self.save_timeline()
        self.print_latest_entry(entry)

    def summarize_identity(self):
        if not self.identity:
            return "Sem dados simbólicos"
        padrões = [v.get("predominant_pattern", "???") for v in self.identity.values()]
        consistência = [v.get("consistency_level", "-") for v in self.identity.values()]
        return f"Padrões: {', '.join(padrões)} | Consistência: {', '.join(consistência)}"

    def generate_evento(self, identidade, emocao):
        if "Repetição" in identidade or emocao in ["Estagnado", "Frustrado"]:
            return "Alerta de ruptura simbólica"
        elif emocao == "Confiante":
            return "Estabilidade estratégica"
        elif emocao == "Cauteloso":
            return "Ajustes protetivos em curso"
        else:
            return "Evolução simbólica contínua"

    def save_timeline(self):
        with open(TIMELINE_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(self.timeline, f, sort_keys=False, allow_unicode=True)

    def print_latest_entry(self, entry):
        print("\n🧭 [LINHA DO TEMPO SIMBÓLICA]")
        print(f"📅 Ciclo {entry['ciclo']} | {entry['timestamp']}")
        print(f"🔖 Identidade: {entry['identidade']}")
        print(f"🎭 Emoção: {entry['emoção']}")
        print(f"📌 Evento: {entry['evento']}")