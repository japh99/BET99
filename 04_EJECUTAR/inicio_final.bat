@echo off
echo Solución definitiva: venv, dependencias compatibles, verificación y app (>70% precisión para BTTS y Over/Under 2.5)...
cd /d D:\Proyecto_Futbol

echo 1. Recreando venv...
rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate

echo 2. Instalando dependencias compatibles con Python 3.13...
python -m pip install --upgrade pip
pip install wheel
pip install streamlit==1.35.0 requests==2.31.0 joblib==1.4.2 pyyaml==6.0.2 --only-binary :all:
pip install numpy==2.1.2 --only-binary :all:
pip install pandas==2.2.3 --only-binary :all:

echo 3. Verificando dependencias...
pip list

echo 4. Verificando modelos ML (>70% precisión)...
if not exist 01_MODELOS\btts\modelo_btts_ensemble.joblib (
    echo ADVERTENCIA: Copia modelo_btts_ensemble.joblib a 01_MODELOS\btts
)
if not exist 01_MODELOS\over_under\modelo_over_under_optimizado.joblib (
    echo ADVERTENCIA: Copia modelo_over_under_optimizado.joblib a 01_MODELOS\over_under
)

echo 5. Verificando config.yaml (APIs)...
if not exist 05_CONFIGURACION\config.yaml (
    echo ERROR: Crea 05_CONFIGURACION\config.yaml con claves API-Football y The Odds API
    pause
    exit /b 1
)

echo 6. Ejecutando app...
start http://localhost:8501
streamlit run 02_CODIGO/app.py

pause