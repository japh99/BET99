@echo off
echo Organizando proyecto de una sola vez: venv, dependencias, verificación y app...
cd /d D:\Proyecto_Futbol

echo 1. Eliminando venv anterior...
rmdir /s /q venv

echo 2. Creando nuevo venv...
python -m venv venv

echo 3. Activando venv...
call venv\Scripts\activate

echo 4. Actualizando pip...
python -m pip install --upgrade pip

echo 5. Instalando dependencias precompiladas (sin C++)...
pip install wheel
pip install streamlit==1.35.0 requests==2.31.0 joblib==1.4.2 pyyaml==6.0.1 --only-binary :all:
pip install numpy==1.26.4 --only-binary :all:
pip install pandas==2.2.3 --only-binary :all:

echo 6. Verificando dependencias...
pip list

echo 7. Verificando modelos ML (>70% precisión)...
if not exist 01_MODELOS\btts\modelo_btts_ensemble.joblib (
    echo ADVERTENCIA: Copia modelo_btts_ensemble.joblib a 01_MODELOS\btts
)
if not exist 01_MODELOS\over_under\modelo_over_under_optimizado.joblib (
    echo ADVERTENCIA: Copia modelo_over_under_optimizado.joblib a 01_MODELOS\over_under
)

echo 8. Verificando config.yaml (APIs)...
if not exist 05_CONFIGURACION\config.yaml (
    echo ERROR: Crea 05_CONFIGURACION\config.yaml con claves API-Football y The Odds API
    pause
    exit /b 1
)

echo 9. Ejecutando app...
streamlit run 02_CODIGO/app.py

pause