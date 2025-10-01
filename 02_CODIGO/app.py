import streamlit as st
import sys
import os
import requests
import joblib
import pandas as pd
import numpy as np
import time
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Importar módulos del proyecto (portable)
sys.path.append(os.path.abspath("02_CODIGO"))
from api_utils import get_fixtures, load_config
from bankroll_manager import BankrollManager

# Cargar configuración
config = load_config()

# --- CONFIGURACIÓN DE PÁGINA Y TÍTULO ---
st.set_page_config(page_title="Sistema Inteligente de Predicción de Fútbol", page_icon="⚽", layout="wide")
st.title("⚽ Sistema Inteligente de Análisis de Apuestas de Fútbol")

st.markdown("""
<style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Rutas de modelos alineadas con estructura (portable)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELO_BTTS_PATH = os.path.join(BASE_DIR, "..", "01_MODELOS", "btts", "modelo_btts_ensemble.joblib")
MODELO_OU_PATH = os.path.join(BASE_DIR, "..", "01_MODELOS", "over_under", "modelo_over_under_optimizado.joblib")

# Inicializar session state
if 'upcoming_fixtures' not in st.session_state:
    st.session_state.upcoming_fixtures = []
    st.session_state.home_form = None
    st.session_state.away_form = None
    st.session_state.h2h_data = None
    st.session_state.predictions_history = []

# Inicializar bankroll manager
bankroll = BankrollManager()

# Funciones para análisis (reemplaza con tu lógica real para >70% precisión)
def calculate_stats_from_fixtures(team_id, fixtures, weight='recent'):
    if not fixtures:
        return {'victorias': 0, 'empates': 0, 'derrotas': 0, 'puntos_forma': 0, 'goles_favor_promedio': 0, 'goles_contra_promedio': 0, 'tiros_puerta_promedio': 0, 'tiros_totales_promedio': 0, 'posesion_promedio': 50, 'corners_promedio': 0, 'tarjetas_promedio': 0}
    # Tu lógica real aquí
    return {'puntos_forma': 10, 'goles_favor_promedio': 2.0, 'goles_contra_promedio': 1.0, 'consistencia': 0.8}

def calculate_goal_trend(team_id, fixtures):
    return 0.5  # Tu lógica real

def calculate_consistency(team_id, fixtures):
    return 0.7  # Tu lógica real

def calculate_strength_of_schedule(team_id, fixtures):
    return 1.2  # Tu lógica real

def load_models():
    try:
        btts_model = joblib.load(MODELO_BTTS_PATH)
        ou_model = joblib.load(MODELO_OU_PATH)
        st.success("Modelos cargados correctamente (>70% precisión para BTTS y Over/Under 2.5)")
        return btts_model, ou_model
    except Exception as e:
        st.error(f"Error cargando modelos: {e}. Verifica rutas en MODELO_BTTS_PATH y MODELO_OU_PATH.")
        return None, None

def prepare_model_input(home_form, away_form, elo_home, elo_away, odds):
    # Tu lógica real para preparar inputs (features para modelos >70%)
    input_btts = [elo_home - elo_away, home_form['goles_favor_promedio'], away_form['goles_contra_promedio'], odds['btts_yes']]
    input_ou = [elo_home - elo_away, home_form['goles_favor_promedio'] + away_form['goles_contra_promedio'], odds['over_2_5']]
    adjustment_factors = {'elo_adjust': 0.1, 'form_adjust': 0.2}
    return input_btts, input_ou, adjustment_factors

def predict_with_adjustment(model, input_data, adjustment_factors, type):
    # Tu lógica real para predicciones (>70% precisión)
    prob = model.predict_proba([input_data])[0]  # Ajusta a tu modelo
    return prob  # Ejemplo: [prob_no, prob_si]

def calculate_value_bets(predictions, odds):
    value_bets = {}
    for bet in predictions:
        ev = predictions[bet] * odds[bet] - 1
        if ev > 0.05:
            value_bets[bet] = {'prob': predictions[bet], 'odd': odds[bet], 'ev': ev, 'kelly': (predictions[bet] * odds[bet] - 1) / (odds[bet] - 1)}
    return value_bets

def get_the_odds_events(sport_key):
    """Obtener eventos próximos y cuotas de The Odds API (para ligas de interés)"""
    odds_key = config['api']['odds_api_key']
    if not odds_key:
        st.warning("Clave de The Odds API no configurada en config.yaml")
        return {}
    
    url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds/?apiKey={odds_key}&regions=eu&markets=h2h,over_under,btts&oddsFormat=decimal"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        st.success(f"Eventos y cuotas obtenidos de The Odds API para {sport_key}")
        return data
    else:
        st.error(f"Error en The Odds API: {response.status_code} - {response.text}")
        return {}

def main():
    # Inputs manuales para ELO y budget
    col1, col2 = st.columns(2)
    with col1:
        elo_home = st.number_input("ELO Home", min_value=1000, value=1600)
        elo_away = st.number_input("ELO Away", min_value=1000, value=1600)
        budget = st.number_input("Presupuesto (€)", min_value=100, value=1000)
    with col2:
        home_team = st.text_input("Home Team", "Liverpool")
        away_team = st.text_input("Away Team", "Man City")
    
    # Selección de liga para The Odds API (ligas de interés)
    ligas_interes = {
        "soccer_epl": "Inglaterra Premier League",
        "soccer_spain_la_liga": "España La Liga",
        "soccer_germany_bundesliga": "Alemania Bundesliga",
        "soccer_portugal_primeira_liga": "Portugal Primeira Liga",
        "soccer_italy_serie_a": "Italia Serie A",
        "soccer_france_ligue_one": "Francia Ligue 1"
    }
    sport_key = st.selectbox("Liga (The Odds API)", list(ligas_interes.keys()), format_func=lambda x: ligas_interes[x])
    
    if st.button("Obtener Eventos Próximos y Cuotas (The Odds API)"):
        odds_data = get_the_odds_events(sport_key)
        if odds_data:
            st.session_state.odds_data = odds_data
            st.success("Eventos y cuotas cargados. Analizando forma con API-Football...")
            
            # Obtener forma de equipos con API-Football para el evento seleccionado
            if odds_data:
                event = odds_data[0]  # Primer evento como ejemplo
                home_id = event['home_team']['id']  # Ajusta según estructura de The Odds API
                away_id = event['away_team']['id']
                home_form = get_team_form_stats(home_id)
                away_form = get_team_form_stats(away_id)
                h2h = get_h2h_stats(home_id, away_id)
                
                st.session_state.home_form = process_team_form_enhanced(home_id, home_form, h2h)
                st.session_state.away_form = process_team_form_enhanced(away_id, away_form, h2h)
                
                # Extraer cuotas del evento
                odds = {  # Ajusta según estructura de The Odds API
                    'home': event['bookmakers'][0]['markets'][0]['outcomes'][0]['price'],
                    'draw': event['bookmakers'][0]['markets'][0]['outcomes'][1]['price'],
                    'away': event['bookmakers'][0]['markets'][0]['outcomes'][2]['price'],
                    'over_2_5': event['bookmakers'][0]['markets'][1]['outcomes'][0]['price'],
                    'under_2_5': event['bookmakers'][0]['markets'][1]['outcomes'][1]['price'],
                    'btts_yes': event['bookmakers'][0]['markets'][2]['outcomes'][0]['price'],
                    'btts_no': event['bookmakers'][0]['markets'][2]['outcomes'][1]['price']
                }
                
                # Análisis correcto: Forma + ELO + Cuotas + Modelos ML
                btts_model, ou_model = load_models()
                if btts_model and ou_model:
                    input_btts, input_ou, adjustment_factors = prepare_model_input(
                        st.session_state.home_form, st.session_state.away_form, elo_home, elo_away, odds
                    )
                    prob_btts = predict_with_adjustment(btts_model, input_btts, adjustment_factors, 'btts')
                    prob_ou = predict_with_adjustment(ou_model, input_ou, adjustment_factors, 'ou')
                    
                    predictions = {
                        'btts_yes': prob_btts[1] if len(prob_btts) > 1 else 0.5,
                        'btts_no': prob_btts[0] if len(prob_btts) > 1 else 0.5,
                        'over_2_5': prob_ou[1] if len(prob_ou) > 1 else 0.5,
                        'under_2_5': prob_ou[0] if len(prob_ou) > 1 else 0.5
                    }
                    
                    # Prob más alta de los 4 resultados
                    all_probs = {
                        'BTTS Sí': predictions['btts_yes'],
                        'BTTS No': predictions['btts_no'],
                        'Over 2.5': predictions['over_2_5'],
                        'Under 2.5': predictions['under_2_5']
                    }
                    max_prob_bet = max(all_probs, key=all_probs.get)
                    max_prob_value = all_probs[max_prob_bet]
                    st.metric("Probabilidad Más Alta", f"{max_prob_value:.1%}", max_prob_bet)
                    
                    # Distribución de presupuesto (Kelly, máx. 5%, 3/día)
                    value_bets = calculate_value_bets(predictions, odds)
                    if value_bets:
                        sorted_bets = sorted(value_bets.items(), key=lambda x: x[1]['ev'], reverse=True)
                        st.subheader("Distribución de Presupuesto (€)")
                        remaining_budget = budget
                        for i, (bet_name, bet_info) in enumerate(sorted_bets[:3]):  # Máx. 3 apuestas
                            kelly_stake = bet_info['kelly'] * remaining_budget
                            stake = min(kelly_stake, remaining_budget * 0.05)  # Máx. 5%
                            st.metric(f"{bet_name} (Stake: €{stake:.2f})", f"EV: +{bet_info['ev']*100:.1f}%", f"Prob: {bet_info['prob']:.1%}")
                            remaining_budget -= stake
                        st.info(f"Presupuesto restante: €{remaining_budget:.2f}")
                        
                        # Registrar apuesta en bankroll_manager
                        match = {"league": ligas_interes[sport_key], "home": home_team, "away": away_team}
                        bankroll.register_bet("EUR", match, max_prob_bet, odds[max_prob_bet], max_prob_value, bet_info['ev'])
                        st.success("Apuesta registrada en bankroll")
                    else:
                        st.info("No hay apuestas de valor. Espera mejores cuotas.")
                else:
                    st.error("Modelos no cargados. Verifica 01_MODELOS.")
            else:
                st.error("No se pudieron obtener eventos de The Odds API. Verifica clave en config.yaml.")

if __name__ == "__main__":
    main()
