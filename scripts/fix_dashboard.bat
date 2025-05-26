@echo off
echo 🔧 Corrigindo localização dos arquivos...

REM Criar diretórios necessários
mkdir interface\dashboard 2>nul

REM Procurar e mover dashboard
if exist "dashboard_streamlit.py" (
    echo   → Movendo dashboard_streamlit.py...
    move "dashboard_streamlit.py" "interface\dashboard\streamlit_app.py"
    echo   ✅ Dashboard movido com sucesso!
) else (
    echo   ⚠️ dashboard_streamlit.py não encontrado na raiz
)

REM Verificar se existe na pasta dashboard
if exist "dashboard\streamlit\dashboard_streamlit.py" (
    echo   → Movendo de dashboard\streamlit\...
    move "dashboard\streamlit\dashboard_streamlit.py" "interface\dashboard\streamlit_app.py"
    echo   ✅ Dashboard movido com sucesso!
)

REM Verificar outros locais possíveis
if exist "interface\dashboard\streamlit_app_backup.py" (
    echo   → Renomeando backup...
    ren "interface\dashboard\streamlit_app_backup.py" "streamlit_app.py"
    echo   ✅ Dashboard restaurado do backup!
)

echo.
echo 📁 Estrutura de arquivos corrigida!
pause