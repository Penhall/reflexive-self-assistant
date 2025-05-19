import yaml
from collections import Counter

SCENARIOS_FILE = "reflection/scenarios.yaml"
DECISION_FILE = "reflection/simulated_decision.yaml"

def evaluate_scenario(scenario):
    score = 0
    diversity = len(set(scenario.values()))
    score += diversity * 2  # Diversidade é valiosa

    if any("fallback" in t.lower() for t in scenario.values()):
        score -= 2

    if any("inovar" in t.lower() or "novo" in t.lower() or "expandir" in t.lower() for t in scenario.values()):
        score += 2

    if len(Counter(scenario.values())) < len(scenario):
        score -= 1  # Tarefas repetidas

    return score

def run_simulation():
    try:
        with open(SCENARIOS_FILE, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        scenarios = data.get("scenarios", [])
        best_score = float("-inf")
        best_scenario = None

        for scenario in scenarios:
            score = evaluate_scenario(scenario)
            if score > best_score:
                best_score = score
                best_scenario = scenario

        decision = {
            "selected_plan": best_scenario,
            "rationale": f"Maior pontuação simbólica: {best_score}"
        }

        with open(DECISION_FILE, "w", encoding="utf-8") as f:
            yaml.safe_dump(decision, f, allow_unicode=True)

        print("✅ Simulação completa. Melhor plano escolhido.")
    except Exception as e:
        print(f"Erro ao simular cenários: {e}")

if __name__ == "__main__":
    run_simulation()