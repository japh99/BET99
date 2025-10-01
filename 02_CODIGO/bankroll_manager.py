import pandas as pd
import yaml
import os
from datetime import datetime, date

class BankrollManager:
    def __init__(self):
        self.config = self.load_config()
        self.bankroll_file = "03_DATOS/historico/bankroll_cop.csv"
        self.bankroll = self.config["betting"]["bankroll_initial_cop"]
        self.max_daily_bets = self.config["betting"]["max_daily_bets"]
        self.kelly_fraction = self.config["betting"]["kelly_fraction"]
        self.min_edge = self.config["betting"]["min_edge"]
        self.load_bankroll()

    def load_config(self):
        with open("05_CONFIGURACION/config.yaml", "r") as f:
            return yaml.safe_load(f)

    def load_bankroll(self):
        if os.path.exists(self.bankroll_file):
            self.df = pd.read_csv(self.bankroll_file)
            if not self.df.empty:
                self.bankroll = self.df["bankroll_final"].iloc[-1]

    def check_daily_limit(self, bet_date):
        if not os.path.exists(self.bankroll_file):
            return 0
        df = pd.read_csv(self.bankroll_file)
        today_bets = df[df["fecha"] == bet_date].shape[0]
        return today_bets

    def calculate_kelly(self, odds, prob, edge):
        if edge < self.min_edge:
            return 0
        kelly = (odds * prob - 1) / (odds - 1) * self.kelly_fraction
        stake = max(0, min(kelly * self.bankroll, self.bankroll * 0.05))
        return round(stake, 2)

    def register_bet(self, currency, match, market, odds, prob, edge):
        today = date.today().strftime("%Y-%m-%d")
        if self.check_daily_limit(today) >= self.max_daily_bets:
            return {"error": "Límite diario alcanzado"}
        stake = self.calculate_kelly(odds, prob, edge)
        if stake == 0:
            return {"error": "Edge insuficiente"}
        bet_id = pd.read_csv(self.bankroll_file).shape[0] + 1 if os.path.exists(self.bankroll_file) else 1
        bet = {
            "id": bet_id,
            "fecha": today,
            "hora": datetime.now().strftime("%H:%M:%S"),
            "liga": match["league"],
            "partido": f"{match['home']} vs {match['away']}",
            "mercado": market,
            "cuota": odds,
            "probabilidad": prob,
            "edge": edge,
            "kelly": stake / self.bankroll,
            "stake": stake,
            "resultado": "pendiente",
            "ganancia": 0,
            "bankroll_final": self.bankroll,
            "currency": currency
        }
        self.df = pd.concat([self.df, pd.DataFrame([bet])], ignore_index=True) if os.path.exists(self.bankroll_file) else pd.DataFrame([bet])
        self.df.to_csv(self.bankroll_file, index=False)
        return bet
