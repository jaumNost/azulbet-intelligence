import streamlit as st
import pandas as pd

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

    .metric-card {
        background-color: #0f1f38;
        padding: 20px;
        border-radius: 15px;
        border: 1px solid #1e3a5f;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔵 AzulBet Intelligence")
st.write("Plataforma simples para acompanhar jogos, odds e controlar suas apostas.")

st.warning(
    "Aviso: este app é apenas informativo. Apostas envolvem risco e nenhum resultado é garantido."
)

jogos = pd.DataFrame(
    [
        {
            "Competição": "Copa do Mundo",
            "Jogo": "Espanha x Bélgica",
            "Favorito": "Espanha",
            "Análise": "Melhor defesa, controle de posse e campanha mais sólida.",
            "Odd Casa": 1.62,
            "Odd Empate": 3.90,
            "Odd Fora": 5.10,
            "Sugestão Informativa": "Espanha ou empate",
            "Odd Sugerida": 1.24
        },
        {
            "Competição": "Brasileirão",
            "Jogo": "Flamengo x Botafogo-SP",
            "Favorito": "Flamengo",
            "Análise": "Diferença grande de elenco, orçamento e profundidade.",
            "Odd Casa": 1.35,
            "Odd Empate": 4.60,
            "Odd Fora": 8.80,
            "Sugestão Informativa": "Mais de 1.5 gols",
            "Odd Sugerida": 1.50
        },
        {
            "Competição": "Amistoso Internacional",
            "Jogo": "França x Nova Zelândia",
            "Favorito": "França",
            "Análise": "Favoritismo técnico muito alto, mas amistosos têm rotação.",
            "Odd Casa": 1.28,
            "Odd Empate": 5.20,
            "Odd Fora": 10.50,
            "Sugestão Informativa": "França vence",
            "Odd Sugerida": 1.28
        },
        {
            "Competição": "Champions League",
            "Jogo": "Manchester City x Porto",
            "Favorito": "Manchester City",
            "Análise": "Mandante mais forte, elenco superior e maior volume ofensivo.",
            "Odd Casa": 1.48,
            "Odd Empate": 4.20,
            "Odd Fora": 6.40,
            "Sugestão Informativa": "Mais de 1.5 gols",
            "Odd Sugerida": 1.44
        },
        {
            "Competição": "Libertadores",
            "Jogo": "Palmeiras x Boca Juniors",
            "Favorito": "Palmeiras",
            "Análise": "Mandante forte, mas confronto equilibrado e tradicionalmente difícil.",
            "Odd Casa": 1.92,
            "Odd Empate": 3.15,
            "Odd Fora": 4.25,
            "Sugestão Informativa": "Palmeiras ou empate",
            "Odd Sugerida": 1.31
        }
    ]
)

if "apostas" not in st.session_state:
    st.session_state.apostas = []

aba_jogos, aba_favoritos, aba_apostas = st.tabs(
    ["Jogos", "Favoritos Fortes", "Minhas Apostas"]
)

with aba_jogos:
    st.subheader("Principais jogos e odds")

    filtro = st.text_input("Buscar jogo ou competição")

    if filtro:
        jogos_filtrados = jogos[
            jogos.apply(
                lambda linha: filtro.lower() in str(linha).lower(),
                axis=1
            )
        ]
    else:
        jogos_filtrados = jogos

    st.dataframe(
        jogos_filtrados,
        use_container_width=True,
        hide_index=True
    )

with aba_favoritos:
    st.subheader("Jogos com favorito forte")

    st.info(
        "Esta aba mostra jogos em que existe um favorito claro ou um mercado mais conservador perto de odd 1.50."
    )

    favoritos = jogos[jogos["Odd Sugerida"] <= 1.55]

    for index, jogo in favoritos.iterrows():
        st.markdown("---")
        st.markdown(f"### {jogo['Jogo']}")
        st.write(f"**Competição:** {jogo['Competição']}")
        st.write(f"**Favorito:** {jogo['Favorito']}")
        st.write(f"**Análise:** {jogo['Análise']}")
        st.success(
            f"Sugestão informativa: {jogo['Sugestão Informativa']} @ {jogo['Odd Sugerida']}"
        )

with aba_apostas:
    st.subheader("Minhas apostas")

    col1, col2, col3 = st.columns(3)

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

    col1.metric("Total apostado", f"R$ {total_apostado:.2f}")
    col2.metric("Lucro / Prejuízo", f"R$ {lucro_realizado:.2f}")
    col3.metric("Retorno potencial aberto", f"R$ {retorno_potencial:.2f}")

    st.markdown("---")
    st.subheader("Registrar nova aposta")

    jogo_escolhido = st.selectbox(
        "Jogo",
        jogos["Jogo"].tolist()
    )

    mercado = st.text_input(
        "Mercado apostado",
        placeholder="Exemplo: Espanha vence, Mais de 1.5 gols, Flamengo ou empate"
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
        value=1.50,
        step=0.01
    )

    status = st.selectbox(
        "Status da aposta",
        ["Aberta", "Ganha", "Perdida"]
    )

    if st.button("Salvar aposta"):
        nova_aposta = {
            "jogo": jogo_escolhido,
            "mercado": mercado,
            "valor": valor,
            "odd": odd,
            "status": status
        }

        st.session_state.apostas.append(nova_aposta)

        st.success("Aposta salva com sucesso!")

    st.markdown("---")
    st.subheader("Histórico de apostas")

    if len(st.session_state.apostas) == 0:
        st.write("Nenhuma aposta registrada ainda.")
    else:
        historico = pd.DataFrame(st.session_state.apostas)

        historico["retorno_potencial"] = historico["valor"] * historico["odd"]

        def calcular_resultado(linha):
            if linha["status"] == "Ganha":
                return linha["valor"] * linha["odd"] - linha["valor"]
            if linha["status"] == "Perdida":
                return -linha["valor"]
            return 0

        historico["resultado"] = historico.apply(calcular_resultado, axis=1)

        st.dataframe(
            historico,
            use_container_width=True,
            hide_index=True
        )

        if st.button("Limpar histórico"):
            st.session_state.apostas = []
            st.success("Histórico apagado. Atualize a página.")

st.markdown("---")
st.caption("AzulBet Intelligence - Streamlit Edition")
