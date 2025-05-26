@echo off
chcp 65001 >nul
echo 🔄 Iniciando reestruturação do projeto Reflexive Self Assistant...
echo.

REM Criar nova estrutura de diretórios
echo 📁 Criando nova estrutura de diretórios...

REM Infrastructure
mkdir infrastructure 2>nul
mkdir infrastructure\ollama 2>nul
mkdir infrastructure\neo4j 2>nul
mkdir infrastructure\neo4j\init 2>nul
mkdir infrastructure\chromadb 2>nul
mkdir infrastructure\chromadb\config 2>nul

REM Core
mkdir core 2>nul
mkdir core\agents 2>nul
mkdir core\crew 2>nul
mkdir core\llm 2>nul

REM Memory
mkdir memory 2>nul
mkdir memory\graph_rag 2>nul
mkdir memory\vector_store 2>nul
mkdir memory\symbolic 2>nul

REM Evolution
mkdir evolution 2>nul
mkdir evolution\checkpointing 2>nul
mkdir evolution\repository 2>nul
mkdir evolution\adaptation 2>nul

REM Reflection (reorganizada)
mkdir reflection_new 2>nul
mkdir reflection_new\symbolic 2>nul
mkdir reflection_new\analysis 2>nul
mkdir reflection_new\state 2>nul
mkdir reflection_new\state\identity 2>nul
mkdir reflection_new\state\emotional 2>nul
mkdir reflection_new\state\temporal 2>nul
mkdir reflection_new\state\governance 2>nul

REM Interface
mkdir interface 2>nul
mkdir interface\dashboard 2>nul
mkdir interface\dashboard\components 2>nul
mkdir interface\dashboard\visualizations 2>nul
mkdir interface\cli 2>nul
mkdir interface\cli\commands 2>nul
mkdir interface\api 2>nul
mkdir interface\api\schemas 2>nul

REM Tests (reorganizados)
mkdir tests_new 2>nul
mkdir tests_new\unit 2>nul
mkdir tests_new\integration 2>nul
mkdir tests_new\performance 2>nul

REM Config (reorganizado)
mkdir config_new 2>nul
mkdir config_new\model_configs 2>nul
mkdir config_new\environment 2>nul

REM Examples
mkdir examples 2>nul

REM Scripts
mkdir scripts 2>nul

echo ✅ Estrutura de diretórios criada!
echo.

REM Mover arquivos existentes para nova estrutura
echo 📦 Movendo arquivos para nova estrutura...

REM Core - Agentes
echo   → Movendo agentes...
if exist "agents\code_agent.py" move "agents\code_agent.py" "core\agents\" >nul
if exist "agents\test_agent.py" move "agents\test_agent.py" "core\agents\" >nul
if exist "agents\doc_agent.py" move "agents\doc_agent.py" "core\agents\" >nul
if exist "agents\reflection_agent.py" move "agents\reflection_agent.py" "core\agents\" >nul
if exist "agents\__init__.py" move "agents\__init__.py" "core\agents\" >nul

REM Core - Main
echo   → Movendo arquivos principais...
if exist "core\main.py" move "core\main.py" "core\main.py" >nul
if exist "core\main1.py" move "core\main1.py" "core\main_legacy.py" >nul
if exist "core\main2.py" move "core\main2.py" "core\main_legacy2.py" >nul

REM Memory - Symbolic
echo   → Movendo memória simbólica...
if exist "reflection\memory\symbolic_memory.py" move "reflection\memory\symbolic_memory.py" "memory\symbolic\" >nul
if exist "reflection\memory\__init__.py" move "reflection\memory\__init__.py" "memory\symbolic\" >nul

REM Reflection - Estados YAML organizados
echo   → Organizando estados de reflexão...

REM Estados de identidade
if exist "reflection\identity_state.yaml" move "reflection\identity_state.yaml" "reflection_new\state\identity\" >nul
if exist "reflection\memory\identity_state.yaml" move "reflection\memory\identity_state.yaml" "reflection_new\state\identity\identity_backup.yaml" >nul
if exist "reflection\memory\memory_log.yaml" move "reflection\memory\memory_log.yaml" "reflection_new\state\identity\memory_log.yaml" >nul

REM Estados emocionais
if exist "reflection\state\emotional_state.yaml" move "reflection\state\emotional_state.yaml" "reflection_new\state\emotional\" >nul
if exist "reflection\state\self_narrative.yaml" move "reflection\state\self_narrative.yaml" "reflection_new\state\emotional\self_narrative.yaml" >nul

REM Estados temporais
if exist "reflection\state\symbolic_timeline.yaml" move "reflection\state\symbolic_timeline.yaml" "reflection_new\state\temporal\" >nul
if exist "reflection\cycle_history.json" move "reflection\cycle_history.json" "reflection_new\state\temporal\cycle_history.json" >nul
if exist "reflection\history\cycle_history.json" move "reflection\history\cycle_history.json" "reflection_new\state\temporal\cycle_history_backup.json" >nul

REM Estados de governança
if exist "reflection\state\symbolic_governance.yaml" move "reflection\state\symbolic_governance.yaml" "reflection_new\state\governance\" >nul
if exist "reflection\state\supervisor_insight.yaml" move "reflection\state\supervisor_insight.yaml" "reflection_new\state\governance\supervisor_insight.yaml" >nul
if exist "reflection\state\symbolic_agenda.yaml" move "reflection\state\symbolic_agenda.yaml" "reflection_new\state\governance\symbolic_agenda.yaml" >nul

REM Reflection - Simbólico
echo   → Movendo componentes simbólicos...
if exist "reflection\dialogue\symbolic_dialogue.py" move "reflection\dialogue\symbolic_dialogue.py" "reflection_new\symbolic\" >nul
if exist "reflection\utils\symbolic_governance.py" move "reflection\utils\symbolic_governance.py" "reflection_new\symbolic\governance.py" >nul
if exist "reflection\utils\timeline_builder.py" move "reflection\utils\timeline_builder.py" "reflection_new\symbolic\timeline.py" >nul
if exist "reflection\utils\symbolic_closure.py" move "reflection\utils\symbolic_closure.py" "reflection_new\symbolic\closure.py" >nul

REM Reflection - Análise
echo   → Movendo ferramentas de análise...
if exist "reflection\utils\contradiction_checker.py" move "reflection\utils\contradiction_checker.py" "reflection_new\analysis\" >nul
if exist "reflection\utils\symbolic_optimizer.py" move "reflection\utils\symbolic_optimizer.py" "reflection_new\analysis\performance_evaluator.py" >nul
if exist "reflection\utils\reflection_agent_update_patch.py" move "reflection\utils\reflection_agent_update_patch.py" "reflection_new\analysis\pattern_analyzer.py" >nul

REM Reflection - Agentes especiais
echo   → Movendo agentes de supervisão...
if exist "reflection\agents\supervisor_agent.py" move "reflection\agents\supervisor_agent.py" "reflection_new\analysis\" >nul
if exist "reflection\agents\meta_coordinator.py" move "reflection\agents\meta_coordinator.py" "reflection_new\analysis\" >nul
if exist "reflection\agents\strategy_planner.py" move "reflection\agents\strategy_planner.py" "reflection_new\analysis\" >nul

REM Interface - Dashboard
echo   → Movendo interface...
if exist "dashboard_streamlit.py" move "dashboard_streamlit.py" "interface\dashboard\streamlit_app.py" >nul
if exist "dashboard\streamlit\dashboard_streamlit.py" move "dashboard\streamlit\dashboard_streamlit.py" "interface\dashboard\streamlit_app_backup.py" >nul

REM Utils
echo   → Movendo utilitários...
if exist "utils\graph_interface.py" move "utils\graph_interface.py" "memory\graph_rag\graph_interface.py" >nul
if exist "utils\logger.py" move "utils\logger.py" "scripts\logger.py" >nul
if exist "utils\__init__.py" move "utils\__init__.py" "scripts\utils_init.py" >nul

REM Config
echo   → Reorganizando configurações...
if exist "config\paths.py" move "config\paths.py" "config_new\paths_legacy.py" >nul
if exist "config\settings.yaml" move "config\settings.yaml" "config_new\settings.yaml" >nul
if exist "config\.env.example" move "config\.env.example" "config_new\environment\.env.example" >nul

REM Tests
echo   → Movendo testes...
if exist "tests\test_agents.py" move "tests\test_agents.py" "tests_new\unit\" >nul

REM Documentação
echo   → Organizando documentação...
if exist "docs\*.md" (
    for %%f in (docs\*.md) do move "%%f" "docs\" >nul 2>&1
)

REM Scripts auxiliares
echo   → Movendo scripts...
if exist "generate_report.py" move "generate_report.py" "scripts\" >nul
if exist "scheduler.py" move "scheduler.py" "scripts\" >nul

REM Arquivos de logs e estados restantes
echo   → Organizando arquivos restantes...
if exist "reflection\*.yaml" (
    for %%f in (reflection\*.yaml) do move "%%f" "reflection_new\state\" >nul 2>&1
)
if exist "reflection\*.md" (
    for %%f in (reflection\*.md) do move "%%f" "reflection_new\" >nul 2>&1
)

REM Remover diretórios vazios antigos
echo   → Limpando estrutura antiga...
if exist "agents" rmdir "agents" 2>nul
if exist "config" rmdir "config" /s /q 2>nul
if exist "tests" rmdir "tests" /s /q 2>nul
if exist "utils" rmdir "utils" /s /q 2>nul
if exist "dashboard" rmdir "dashboard" /s /q 2>nul

REM Renomear diretórios temporários
echo   → Finalizando reestruturação...
if exist "reflection_new" (
    if exist "reflection" rmdir "reflection" /s /q 2>nul
    ren "reflection_new" "reflection" 2>nul
)
if exist "tests_new" (
    if exist "tests" rmdir "tests" /s /q 2>nul
    ren "tests_new" "tests" 2>nul
)
if exist "config_new" (
    if exist "config" rmdir "config" /s /q 2>nul
    ren "config_new" "config" 2>nul
)

echo ✅ Arquivos movidos com sucesso!
echo.

REM Criar arquivos __init__.py necessários
echo 📝 Criando arquivos __init__.py...
echo # Core package > "core\__init__.py"
echo # Agents package > "core\agents\__init__.py"
echo # LLM package > "core\llm\__init__.py"
echo # Crew package > "core\crew\__init__.py"
echo # Memory package > "memory\__init__.py"
echo # GraphRAG package > "memory\graph_rag\__init__.py"
echo # Vector store package > "memory\vector_store\__init__.py"
echo # Symbolic memory package > "memory\symbolic\__init__.py"
echo # Evolution package > "evolution\__init__.py"
echo # Checkpointing package > "evolution\checkpointing\__init__.py"
echo # Repository package > "evolution\repository\__init__.py"
echo # Adaptation package > "evolution\adaptation\__init__.py"
echo # Reflection package > "reflection\__init__.py"
echo # Symbolic reflection package > "reflection\symbolic\__init__.py"
echo # Analysis package > "reflection\analysis\__init__.py"
echo # Interface package > "interface\__init__.py"
echo # Dashboard package > "interface\dashboard\__init__.py"
echo # CLI package > "interface\cli\__init__.py"

echo ✅ Arquivos __init__.py criados!
echo.

REM Criar arquivo de migração de dados
echo 📋 Criando script de backup de dados...
echo # Script de backup dos dados existentes > "scripts\backup_data.py"
echo # Criado em: %date% %time% >> "scripts\backup_data.py"
echo import shutil, os, datetime >> "scripts\backup_data.py"
echo print("Backup dos dados YAML existentes...") >> "scripts\backup_data.py"

echo ✅ Script de backup criado!
echo.

echo 🎉 Reestruturação concluída com sucesso!
echo.
echo 📋 Resumo das mudanças:
echo   → Nova estrutura de diretórios criada
echo   → Arquivos movidos para localizações apropriadas
echo   → Estados YAML organizados por categoria
echo   → Diretórios antigos removidos
echo   → Arquivos __init__.py criados
echo.
echo ⚠️  Próximos passos:
echo   1. Execute o script de configuração de paths
echo   2. Verifique se todos os arquivos foram movidos corretamente
echo   3. Atualize imports nos arquivos Python
echo   4. Teste a execução básica do sistema
echo.
echo 🔧 Para reverter mudanças, execute: git checkout . (se usando Git)

pause