import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="AzulBet Intelligence",
    layout="wide"
)

st.markdown(
    """
    <style>
    .stApp {
        background-color:#081120;
        color:white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🔵 AzulBet Intelligence")

aba1, aba2, aba3 = st.tabs(
    [
        "Jogos",
        "Favoritos Fortes",
        "Minhas Apostas"
    ]
)

jogos = pd.DataFrame(
    [
        {
            "Competição":"Copa do Mundo",
            "Jogo":"Espanha x Bélgica",
            "Odd Casa":1.62,
            "Odd Empate":3.90,
            "Odd Fora":5.10
        },
        {
            "Competição":"Brasileirão",
            "Jogo":"Flamengo x Botafogo-SP",
            "Odd Casa":1.35,
            "Odd Empate":4.60,
            "Odd Fora":8.80
        },
        {
            "Competição":"Champions League",
            "Jogo":"Manchester City x Porto",
            "Odd Casa":1.48,
            "Odd Empate":4.20,
            "Odd Fora":6.40
        }
    ]
)

with aba1:

    st.subheader("Jogos do Dia")

    st.dataframe(
        jogos,
        use_container_width=True
    )

with aba2:

    st.subheader("Favoritos Fortes")

    st.success(
        "Mercados apenas informativos."
    )

    st.write(
        """
        ✅ Flamengo ou empate @1.30
        
        ✅ França vence @1.28
        
        ✅ Mais de 1.5 gols City x Porto @1.44
        
        ✅ Espanha ou empate @1.24
        """
    )

with aba3:

    st.subheader("Registrar aposta")

    aposta = st.text_input(
        "Mercado"
    )

    valor = st.number_input(
        "Valor Apostado",
        min_value=0.0
    )

    odd = st.number_input(
        "Odd",
        min_value=1.0,
        value=1.50
    )

    if st.button("Calcular"):

        retorno = valor * odd

        st.metric(
            "Retorno Potencial",
            f"R$ {retorno:,.2f}"
        )
``
