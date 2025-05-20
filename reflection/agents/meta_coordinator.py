import yaml
from datetime import datetime

MEMORY_FILE = "reflection/memory_log.yaml"
SUPERVISOR_FILE = "reflection/supervisor_self_reflection.yaml"
OUTPUT_FILE = "reflection/emotional_state.yaml"

class MetaCoordinator:
    def __init__(self):
        self.memory = self.load_yaml(MEMORY_FILE)
        self.supervisor = self.load_yaml(SUPERVISOR_FILE)

    def load_yaml(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except FileNotFoundError:
            return {}

    def determine_emotion(self):
        ciclo = max([v.get("ciclos_totais", 0) for v in self.memory.values()], default=0)
        all_traits = [t for agent in self.memory.values() for t in agent.get("traços_frequentes", [])]
        consistencias = [c for agent in self.memory.values() for c, n in agent.get("consistencia", {}).items() if n > 0]

        supervisor_diag = self.supervisor.get("reflexão_supervisor", {}).get("diagnóstico_atual", "")
        review = self.supervisor.get("reflexão_supervisor", {}).get("revisão", "")

        emotion = "Curioso"
        reason = "Diversidade simbólica com estabilidade"

        if "anomalia" in review.lower() or "falha" in review.lower():
            emotion = "Cauteloso"
            reason = "Supervisor detectou repetições anômalas"
        elif all(cons == "Alta" for cons in consistencias):
            emotion = "Confiante"
            reason = "Consistência simbólica alta entre agentes"
        elif "repetido" in review.lower() or "estável demais" in review.lower():
            emotion = "Estagnado"
            reason = "Diagnóstico repetitivo com baixa inovação"
        elif len(set(all_traits)) < 2:
            emotion = "Frustrado"
            reason = "Pouca diversidade nos traços predominantes"

        state = {
            "emotional_state": {
                "ciclo": ciclo,
                "status": emotion,
                "razão": reason,
                "sugestão": self.suggestion_from_emotion(emotion),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(state, f, allow_unicode=True)

        self.print_emotion(state["emotional_state"])

    def suggestion_from_emotion(self, emotion):
        return {
            "Cauteloso": "Reduzir complexidade e reforçar traços base",
            "Confiante": "Experimentar variações simbólicas ousadas",
            "Estagnado": "Forçar prompts disruptivos",
            "Curioso": "Acompanhar evolução de padrões",
            "Frustrado": "Reavaliar estratégia e diagnóstico"
        }.get(emotion, "Continuar executando")

    def print_emotion(self, e):
        print("\n🎭 [ESTADO EMOCIONAL SIMBÓLICO]")
        print(f"🌀 Ciclo: {e['ciclo']} | 🕓 {e['timestamp']}")
        print(f"🧠 Estado: {e['status']}")
        print(f"📌 Razão: {e['razão']}")
        print(f"🔧 Sugestão: {e['sugestão']}")