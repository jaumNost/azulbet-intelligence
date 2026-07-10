import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone

st.set_page_config(
    page_title="AzulBet Intelligence",
    page_icon="🔵",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #081120;
        color: white;
    }

    h1, h2, h3, p, label {
        color: white;
    }

    .stDataFrame {
        background-color: #0f1f38;
    }

    .card {
        background-color: #0f1f38;
        padding: 18px;
        border-radius: 14px;
        border: 1px solid #1e3a5f;
        margin-bottom: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

API_BASE = "https://api.the-odds-api.com/v4"


def get_api_key():
    try:
        return st.secrets["ODDS_API_KEY"]
    except Exception:
        return ""


@st.cache_data(ttl=1800)
def get_sports(api_key):
    url = f"{API_BASE}/sports/"
    params = {
        "apiKey": api_key
    }

    response = requests.get(url, params=params, timeout=20)

    if response.status_code != 200:
        return []

    return response.json()


@st.cache_data(ttl=300)
def get_odds(api_key, sport_key, regions):
    url = f"{API_BASE}/sports/{sport_key}/odds"

    params = {
        "apiKey": api_key,
        "regions": regions,
        "markets": "h2h,totals",
        "oddsFormat": "decimal",
        "dateFormat": "iso"
    }

    response = requests.get(url, params=params, timeout=25)

    if response.status_code != 200:
        return []

    return response.json()


def parse_datetime(value):
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def format_datetime_br(value):
    dt = parse_datetime(value)

    if dt is None:
        return value

    local_dt = dt.astimezone()
    return local_dt.strftime("%d/%m/%Y %H:%M")


def best_price_for_outcome(bookmakers, market_key, outcome_name=None):
    best = None
    best_bookmaker = None
    line = None

    for bookmaker in bookmakers:
        bookmaker_title = bookmaker.get("title", "")

        for market in bookmaker.get("markets", []):
            if market.get("key") != market_key:
                continue

            for outcome in market.get("outcomes", []):
                if outcome_name is not None and outcome.get("name") != outcome_name:
                    continue

                price = outcome.get("price")

                if price is None:
                    continue

                if best is None or price > best:
                    best = price
                    best_bookmaker = bookmaker_title
                    line = outcome.get("point")

    return best, best_bookmaker, line


def average_price_for_outcome(bookmakers, market_key, outcome_name):
    prices = []

    for bookmaker in bookmakers:
        for market in bookmaker.get("markets", []):
            if market.get("key") != market_key:
                continue

            for outcome in market.get("outcomes", []):
                if outcome.get("name") == outcome_name and outcome.get("price") is not None:
                    prices.append(outcome.get("price"))

    if not prices:
        return None

    return sum(prices) / len(prices)


def build_suggestion(event):
    bookmakers = event.get("bookmakers", [])

    if not bookmakers:
        return None

    home = event.get("home_team")
    away = event.get("away_team")

    candidates = []

    home_best, home_book, _ = best_price_for_outcome(bookmakers, "h2h", home)
    away_best, away_book, _ = best_price_for_outcome(bookmakers, "h2h", away)
    draw_best, draw_book, _ = best_price_for_outcome(bookmakers, "h2h", "Draw")

    home_avg = average_price_for_outcome(bookmakers, "h2h", home)
    away_avg = average_price_for_outcome(bookmakers, "h2h", away)

    if home_best:
        candidates.append({
            "mercado": f"{home} vence",
            "odd": home_best,
            "casa": home_book,
            "tipo": "h2h",
            "media": home_avg,
            "justificativa": f"O mercado coloca {home} como opção forte pela odd média baixa. Melhor preço encontrado em {home_book}."
        })

    if away_best:
        candidates.append({
            "mercado": f"{away} vence",
            "odd": away_best,
            "casa": away_book,
            "tipo": "h2h",
            "media": away_avg,
            "justificativa": f"O mercado coloca {away} como opção forte pela odd média baixa. Melhor preço encontrado em {away_book}."
        })

    if draw_best:
        candidates.append({
            "mercado": "Empate",
            "odd": draw_best,
            "casa": draw_book,
            "tipo": "h2h",
            "media": None,
            "justificativa": f"Empate localizado como mercado disponível. Melhor preço encontrado em {draw_book}."
        })

    totals_candidates = []

    for bookmaker in bookmakers:
        bookmaker_title = bookmaker.get("title", "")

        for market in bookmaker.get("markets", []):
            if market.get("key") != "totals":
                continue

            for outcome in market.get("outcomes", []):
                name = outcome.get("name")
                price = outcome.get("price")
                point = outcome.get("point")

                if price is None or point is None:
                    continue

                totals_candidates.append({
                    "mercado": f"{name} {point} gols",
                    "odd": price,
                    "casa": bookmaker_title,
                    "tipo": "totals",
                    "media": None,
                    "justificativa": f"Mercado de gols disponível na linha {point}. Preço próximo do alvo encontrado em {bookmaker_title}."
                })

    candidates.extend(totals_candidates)

    valid_candidates = [
        item for item in candidates
        if item["odd"] is not None and 1.25 <= float(item["odd"]) <= 1.70
    ]

    if not valid_candidates:
        return None

    chosen = sorted(
        valid_candidates,
        key=lambda item: abs(float(item["odd"]) - 1.50)
    )[0]

    return chosen


def build_events_dataframe(events):
    rows = []

    now = datetime.now(timezone.utc)

    for event in events:
        commence = parse_datetime(event.get("commence_time", ""))

        if commence is None:
            continue

        if commence <= now:
            continue

        bookmakers = event.get("bookmakers", [])

        if not bookmakers:
            continue

        home = event.get("home_team", "")
        away = event.get("away_team", "")

        home_best, home_book, _ = best_price_for_outcome(bookmakers, "h2h", home)
        away_best, away_book, _ = best_price_for_outcome(bookmakers, "h2h", away)
        draw_best, draw_book, _ = best_price_for_outcome(bookmakers, "h2h", "Draw")

        suggestion = build_suggestion(event)

        rows.append({
            "id": event.get("id"),
            "Data": format_datetime_br(event.get("commence_time")),
            "Liga": event.get("sport_title"),
            "Jogo": f"{home} x {away}",
            "Casa": home,
            "Fora": away,
            "Odd Casa": home_best,
            "Book Casa": home_book,
            "Odd Empate": draw_best,
            "Book Empate": draw_book,
            "Odd Fora": away_best,
            "Book Fora": away_book,
            "Sugestão": suggestion["mercado"] if suggestion else "",
            "Odd Sugerida": suggestion["odd"] if suggestion else None,
            "Casa da Odd": suggestion["casa"] if suggestion else "",
            "Justificativa": suggestion["justificativa"] if suggestion else "Sem mercado próximo de 1.50 encontrado."
        })

    return pd.DataFrame(rows)


if "apostas" not in st.session_state:
    st.session_state.apostas = []

st.title("🔵 AzulBet Intelligence")
st.write("Jogos reais, odds reais e controle pessoal de apostas.")

st.warning(
    "Aviso: o app é informativo. Odds mudam rapidamente e não garantem resultado. Aposte com responsabilidade."
)

api_key = get_api_key()

if not api_key:
    st.error("Você ainda não configurou a chave ODDS_API_KEY no Streamlit Secrets.")
    st.stop()

sports = get_sports(api_key)

if not sports:
    st.error("Não consegui buscar os esportes disponíveis na API. Confira sua chave da The Odds API.")
    st.stop()

soccer_sports = [
    sport for sport in sports
    if sport.get("group") == "Soccer" and sport.get("active") is True
]

if not soccer_sports:
    st.error("A API não retornou ligas de futebol ativas no momento.")
    st.stop()

sport_options = {
    f"{sport.get('title')} - {sport.get('key')}": sport.get("key")
    for sport in soccer_sports
}

aba_jogos, aba_favoritos, aba_apostas = st.tabs(
    ["Jogos Reais", "Favoritos Fortes", "Minhas Apostas"]
)

with st.sidebar:
    st.header("Filtros")

    selected_sports_labels = st.multiselect(
        "Competições",
        list(sport_options.keys()),
        default=list(sport_options.keys())[:5]
    )

    regions = st.multiselect(
        "Regiões de odds",
        ["us", "uk", "eu", "au"],
        default=["eu", "uk", "us"]
    )

    st.caption("Quanto mais ligas selecionadas, mais requisições da API são usadas.")

    if st.button("Atualizar dados"):
        st.cache_data.clear()
        st.rerun()

selected_sport_keys = [
    sport_options[label]
    for label in selected_sports_labels
]

region_string = ",".join(regions)

all_events = []

for sport_key in selected_sport_keys:
    odds_data = get_odds(api_key, sport_key, region_string)

    if odds_data:
        all_events.extend(odds_data)

df = build_events_dataframe(all_events)

with aba_jogos:
    st.subheader("Jogos reais por vir")

    if df.empty:
        st.info("Nenhum jogo futuro com odds disponível para os filtros selecionados.")
    else:
        busca = st.text_input("Buscar time ou competição")

        df_view = df.copy()

        if busca:
            df_view = df_view[
                df_view.apply(
                    lambda row: busca.lower() in str(row).lower(),
                    axis=1
                )
            ]

        st.dataframe(
            df_view[
                [
                    "Data",
                    "Liga",
                    "Jogo",
                    "Odd Casa",
                    "Odd Empate",
                    "Odd Fora",
                    "Sugestão",
                    "Odd Sugerida",
                    "Casa da Odd",
                    "Justificativa"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

with aba_favoritos:
    st.subheader("Mercados próximos de odd 1.50")

    if df.empty:
        st.info("Nenhum jogo encontrado.")
    else:
        favoritos = df[
            df["Odd Sugerida"].notna()
        ].copy()

        favoritos = favoritos.sort_values(
            by="Odd Sugerida",
            key=lambda col: abs(col - 1.50)
        )

        if favoritos.empty:
            st.info("Nenhuma aposta próxima de 1.50 encontrada nos jogos carregados.")
        else:
            for _, jogo in favoritos.iterrows():
                st.markdown(
                    f"""
                    <div class="card">
                        <h3>{jogo["Jogo"]}</h3>
                        <p><b>Liga:</b> {jogo["Liga"]}</p>
                        <p><b>Data:</b> {jogo["Data"]}</p>
                        <p><b>Sugestão informativa:</b> {jogo["Sugestão"]} @ {jogo["Odd Sugerida"]}</p>
                        <p><b>Casa da odd:</b> {jogo["Casa da Odd"]}</p>
                        <p><b>Justificativa:</b> {jogo["Justificativa"]}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

with aba_apostas:
    st.subheader("Minhas apostas")

    total_apostado = sum(aposta["valor"] for aposta in st.session_state.apostas)

    lucro_realizado = 0

    for aposta in st.session_state.apostas:
        if aposta["status"] == "Ganha":
            lucro_realizado += aposta["valor"] * aposta["odd"] - aposta["valor"]
        elif aposta["status"] == "Perdida":
            lucro_realizado -= aposta["valor"]

    retorno_potencial = sum(
        aposta["valor"] * aposta["odd"]
        for aposta in st.session_state.apostas
        if aposta["status"] == "Aberta"
    )

    col1, col2, col3 = st.columns(3)

    col1.metric("Total apostado", f"R$ {total_apostado:.2f}")
    col2.metric("Lucro / Prejuízo", f"R$ {lucro_realizado:.2f}")
    col3.metric("Retorno potencial aberto", f"R$ {retorno_potencial:.2f}")

    st.markdown("---")
    st.subheader("Registrar nova aposta")

    if df.empty:
        st.info("Carregue jogos reais para registrar uma aposta baseada nos dados da API.")
    else:
        opcoes_jogos = df["Jogo"].tolist()

        jogo_escolhido = st.selectbox(
            "Jogo",
            opcoes_jogos
        )

        jogo_linha = df[df["Jogo"] == jogo_escolhido].iloc[0]

        sugestao_padrao = jogo_linha["Sugestão"] if jogo_linha["Sugestão"] else ""
        odd_padrao = float(jogo_linha["Odd Sugerida"]) if pd.notna(jogo_linha["Odd Sugerida"]) else 1.50

        mercado = st.text_input(
            "Mercado apostado",
            value=sugestao_padrao
        )

        valor = st.number_input(
            "Valor apostado",
            min_value=0.0,
            value=0.0,
            step=10.0
        )

        odd = st.number_input(
            "Odd",
            min_value=1.0,
            value=odd_padrao,
            step=0.01
        )

        status = st.selectbox(
            "Status da aposta",
            ["Aberta", "Ganha", "Perdida"]
        )

        justificativa = st.text_area(
            "Justificativa",
            value=jogo_linha["Justificativa"],
            height=80
        )

        if st.button("Salvar aposta"):
            nova_aposta = {
                "jogo": jogo_escolhido,
                "mercado": mercado,
                "valor": valor,
                "odd": odd,
                "status": status,
                "justificativa": justificativa
            }

            st.session_state.apostas.append(nova_aposta)

            st.success("Aposta salva com sucesso.")

    st.markdown("---")
    st.subheader("Histórico de apostas")

    if len(st.session_state.apostas) == 0:
        st.write("Nenhuma aposta registrada ainda.")
    else:
        historico = pd.DataFrame(st.session_state.apostas)

        historico["retorno_potencial"] = historico["valor"] * historico["odd"]

        def calcular_resultado(row):
            if row["status"] == "Ganha":
                return row["valor"] * row["odd"] - row["valor"]
            if row["status"] == "Perdida":
                return -row["valor"]
            return 0

        historico["resultado"] = historico.apply(calcular_resultado, axis=1)

        st.dataframe(
            historico,
            use_container_width=True,
            hide_index=True
        )

        if st.button("Limpar histórico"):
            st.session_state.apostas = []
            st.rerun()

st.markdown("---")
st.caption("AzulBet Intelligence - dados via The Odds API")
