import streamlit as st
import pandas as pd
import re
import statistics
from collections import defaultdict

# Lecture et nettoyage
def parse_match_line(line):
    match = re.search(r"(.+?) vs (.+?):?(\d+)[-–:](\d+)", line, re.IGNORECASE)
    if match:
        return match.group(1).strip().lower(), match.group(2).strip().lower(), int(match.group(3)), int(match.group(4))
    return None

def load_matches(file_path):
    matches = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            parsed = parse_match_line(line)
            if parsed:
                matches.append(parsed)
    return pd.DataFrame(matches, columns=['team1', 'team2', 'score1', 'score2'])

def team_stats(df):
    stats = defaultdict(lambda: {'scored': [], 'conceded': []})
    for _, row in df.iterrows():
        stats[row['team1']]['scored'].append(row['score1'])
        stats[row['team1']]['conceded'].append(row['score2'])
        stats[row['team2']]['scored'].append(row['score2'])
        stats[row['team2']]['conceded'].append(row['score1'])
    return stats

def predict_match(df, team1, team2, stats):
    team1 = team1.lower()
    team2 = team2.lower()
    h2h = df[((df['team1'] == team1) & (df['team2'] == team2)) |
             ((df['team1'] == team2) & (df['team2'] == team1))]
    if not h2h.empty:
        team1_scores = []
        team2_scores = []
        for _, row in h2h.iterrows():
            if row['team1'] == team1:
                team1_scores.append(row['score1'])
                team2_scores.append(row['score2'])
            else:
                team1_scores.append(row['score2'])
                team2_scores.append(row['score1'])
        avg1 = round(statistics.mean(team1_scores), 1)
        avg2 = round(statistics.mean(team2_scores), 1)
    else:
        avg1 = round(statistics.mean(stats[team1]['scored']), 1)
        avg2 = round(statistics.mean(stats[team2]['scored']), 1)

    if avg1 > avg2:
        outcome = f"🏆 Victoire probable : {team1.title()}"
    elif avg2 > avg1:
        outcome = f"🏆 Victoire probable : {team2.title()}"
    else:
        outcome = "🤝 Match nul probable"

    return f"🔢 Score probable : {team1.title()} {int(round(avg1))} - {int(round(avg2))} {team2.title()}\n\n{outcome}"

# === Interface Streamlit ===
st.set_page_config(page_title="Prédicteur FIFA", layout="centered")
st.title("⚽ Prédicteur de Match FIFA")

uploaded_file = st.file_uploader("📄 Charge ton fichier de base de données (.txt)", type="txt")
if uploaded_file is not None:
    df = load_matches(uploaded_file)
    stats = team_stats(df)
    teams = sorted(set(df['team1']).union(set(df['team2'])))

    team1 = st.selectbox("Équipe 1", teams)
    team2 = st.selectbox("Équipe 2", teams)

    if team1 != team2 and st.button("🔮 Prédire le match"):
        result = predict_match(df, team1, team2, stats)
        st.success(result)
