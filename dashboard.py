from rich.console import Console
from rich.panel import Panel
from rich.table import Table
import yaml
import json
from datetime import datetime

console = Console()

def load_identity():
    try:
        with open("reflection/identity_state.yaml", "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except Exception as e:
        console.print(f"[bold red]Erro ao carregar identidade simbólica:[/bold red] {e}")
        return {}

def load_history():
    try:
        with open("reflection/cycle_history.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        console.print(f"[bold red]Erro ao carregar histórico de ciclos:[/bold red] {e}")
        return {}

def render_agent_panel(agent_name, data):
    table = Table.grid(padding=1)
    table.add_column(justify="left")
    table.add_column(justify="left")

    table.add_row("🧠 [bold]Agente[/bold]", f"[cyan]{agent_name}[/cyan]")
    table.add_row("📌 [bold]Padrão[/bold]", f"{data.get('predominant_pattern', '-')}")
    table.add_row("📈 [bold]Consistência[/bold]", f"{data.get('consistency_level', '-')}")
    table.add_row("🕒 [bold]Última adaptação[/bold]", f"{data.get('last_adaptation', '-')}")
    table.add_row("🔖 [bold]Traços[/bold]", ", ".join(data.get("traits", []) or ["-"]))
    hint = data.get("adaptive_hint", "Nenhuma")
    table.add_row("🧭 [bold]Sinal adaptativo[/bold]", f"[yellow]{hint}[/yellow]")

    return Panel(table, title=f"🤖 Identidade simbólica — {agent_name}", border_style="green")

def main():
    identity = load_identity()
    history = load_history()

    console.rule("[bold magenta]Painel de Identidade Simbólica dos Agentes[/bold magenta]")

    for agent, data in identity.items():
        panel = render_agent_panel(agent, data)
        console.print(panel)

    console.rule("[dim]Última atualização: {}[/dim]".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

if __name__ == "__main__":
    main()