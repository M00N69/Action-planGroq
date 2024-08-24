import streamlit as st
import pandas as pd
from io import BytesIO
from docx import Document
from fpdf import FPDF
from groq import Groq

# Configuration de la page
st.set_page_config(layout="wide")

# Ajouter les styles CSS personnalisés
st.markdown(
    """
    <style>
    .main-header {
        font-size: 24px;
        font-weight: bold;
        color: #004080;
        text-align: center;
        margin-bottom: 25px;
    }
    .dataframe-container {
        margin-bottom: 20px;
    }
    .banner {
        background-image: url('https://github.com/M00N69/BUSCAR/blob/main/logo%2002%20copie.jpg?raw=true');
        background-size: cover;
        padding: 75px;
        text-align: center;
    }
    .dataframe td {
        white-space: normal !important;
        word-wrap: break-word !important;
    }
    </style>
    <div class="banner"></div>
    """,
    unsafe_allow_html=True
)

# Initialisation des variables d'état pour les expanders
if 'recommendation_expanders' not in st.session_state:
    st.session_state['recommendation_expanders'] = {}

# Fonction pour configurer le client Groq
def get_groq_client():
    """Initialise et renvoie un client Groq avec la clé API."""
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# Fonction pour charger le fichier Excel avec le plan d'action
def load_action_plan(uploaded_file):
    try:
        action_plan_df = pd.read_excel(uploaded_file, header=12)
        expected_columns = ["Numéro d'exigence", "Exigence IFS Food 8", "Notation", "Explication (par l’auditeur/l’évaluateur)"]
        action_plan_df = action_plan_df[expected_columns]
        return action_plan_df
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier: {str(e)}")
        return None

# Fonction pour générer un prompt basé sur une non-conformité
def generate_ai_recommendation_groq(non_conformity, guide_row):
    client = get_groq_client()
    general_context = (
        "En tant qu'expert en IFS Food 8 et dans la gestion des plans d'action, "
        "tu dois me fournir des recommandations structurées pour la correction, "
        "le type de preuve, la cause probable, et les actions correctives."
    )
    prompt = f"""
    {general_context}

    Voici une non-conformité issue d'un audit IFS Food 8 :
    - Exigence : {non_conformity["Numéro d'exigence"]}
    - Description : {non_conformity['Exigence IFS Food 8']}
    - Constat détaillé : {non_conformity['Explication (par l’auditeur/l’évaluateur)']}
    
    Il est impératif que les recommandations prennent en compte les éléments suivants du guide IFSv8 pour cette exigence :
    - Bonnes pratiques à suivre : {guide_row['Good practice']}
    - Éléments à vérifier : {guide_row['Elements to check']}
    - Exemple de question à poser : {guide_row['Example questions']}

    Fournissez une recommandation comprenant :
    - Correction immédiate
    - Type de preuve
    - Cause probable
    - Action corrective

    Faire une conclusion, en français, en se basant sur le Guide IFSv8 en reprenant évnetuellement les éléments des questions à poser et également attirer l'attention sur les bonnes pratiques concernant l'exigence en question.
    Pour cette conclusion il faut se limiter strictement aux recommandations et informations issus du guide IFSv8 en particulier {guide_row['Good practice']} et {guide_row['Example questions']}
    """
    
    messages = [
        {"role": "system", "content": "Veuillez générer une recommandation structurée pour la non-conformité suivante :"},
        {"role": "user", "content": prompt}
    ]

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama-3.1-70b-versatile"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Erreur lors de la génération de la recommandation: {str(e)}")
        return None

# Fonction pour récupérer les informations du guide en fonction du numéro d'exigence
def get_guide_info(num_exigence, guide_df):
    guide_row = guide_df[guide_df['NUM_REQ'] == num_exigence].iloc[0]
    return guide_row

# Fonction principale
def main():
    st.markdown('<div class="main-header">Assistant VisiPilot pour Plan d\'Actions IFS</div>', unsafe_allow_html=True)

    st.write("Téléchargez votre plan d'action et obtenez des recommandations pour les corrections et les actions correctives.")

    # Upload du fichier Excel du plan d'action
    uploaded_file = st.file_uploader("Téléchargez votre plan d'action (fichier Excel)", type=["xlsx"])
    
    if uploaded_file:
        action_plan_df = load_action_plan(uploaded_file)
        if action_plan_df is not None:
            guide_df = pd.read_csv("https://raw.githubusercontent.com/M00N69/Action-planGroq/main/Guide%20Checklist_IFS%20Food%20V%208%20-%20CHECKLIST.csv")

            # Affichage du plan d'action avec les boutons de génération des recommandations
            for index, row in action_plan_df.iterrows():
                cols = st.columns([4, 1])
                cols[0].markdown(f"**Numéro d'exigence:** {row["Numéro d'exigence"]} - {row['Exigence IFS Food 8']}")
                cols[1].button(
                    "Générer Recommandation", 
                    key=f"generate_{index}",
                    on_click=generate_recommendation_and_expand,
                    args=(index, row, guide_df)
                )

                # Afficher les recommandations dans un expander s'il est déjà généré
                if st.session_state['recommendation_expanders'].get(index):
                    st.session_state['recommendation_expanders'][index].markdown(
                        st.session_state['recommendation_expanders'][index]['text']
                    )
                    
def generate_recommendation_and_expand(index, row, guide_df):
    guide_row = get_guide_info(row["Numéro d'exigence"], guide_df)
    recommendation_text = generate_ai_recommendation_groq(row, guide_row)
    
    if recommendation_text:
        st.success("Recommandation générée avec succès!")
        expander = st.expander(f"Recommandation pour Numéro d'exigence: {row["Numéro d'exigence"]}", expanded=True)
        expander.markdown(recommendation_text)
        
        # Sauvegarde de l'expander dans le session_state
        st.session_state['recommendation_expanders'][index] = {
            'text': recommendation_text,
            'expander': expander
        }

if __name__ == "__main__":
    main()
