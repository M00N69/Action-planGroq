import streamlit as st
import pandas as pd
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
    /* Styles pour la bannière */
    .banner {
        background-image: url('https://github.com/M00N69/BUSCAR/blob/main/logo%2002%20copie.jpg?raw=true');
        background-size: cover;
        height: 200px;
        background-position: center;
        margin-bottom: 20px;
    }
    /* Styles personnalisés pour l'expander */
    .st-emotion-cache-1h9usn1 {
        background-color: #e0f7fa !important; /* Fond bleu clair pour l'expander */
        border: 1px solid #004080 !important; /* Bordure bleu foncé */
        border-radius: 5px;
    }
    .st-emotion-cache-p5msec {
        color: #004080 !important; /* Couleur du texte de l'expander */
    }
    /* Styles personnalisés pour les boutons */
    div.stButton > button {
        background-color: #004080; /* Couleur de fond */
        color: white;
        border-radius: 5px;
        border: none;
        padding: 8px 16px;
        font-weight: bold;
        margin-top: 10px;
    }
    div.stButton > button:hover {
        background-color: #0066cc; /* Couleur de fond au survol */
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# Ajouter la bannière
st.markdown('<div class="banner"></div>', unsafe_allow_html=True)

# Fonction pour configurer le client Groq
def get_groq_client():
    """Initialise et renvoie un client Groq avec la clé API."""
    return Groq(api_key=st.secrets["GROQ_API_KEY"])

# Fonction pour charger le fichier Excel avec le plan d'action
def load_action_plan(uploaded_file):
    try:
        # Load the Excel file starting from row 12 (0-indexed)
        action_plan_df = pd.read_excel(uploaded_file, header=11)

        # Extract only the necessary columns
        action_plan_df = action_plan_df[["requirementNo", "requirementText", "requirementExplanation"]]
        action_plan_df.columns = ["Numéro d'exigence", "Exigence IFS Food 8", "Explication (par l’auditeur/l’évaluateur)"]

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
    - Exigence : {non_conformity['Numéro d\'exigence']}
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

    Faire une conclusion, en français, en se basant sur le Guide IFSv8 en reprenant éventuellement les éléments des questions à poser et également attirer l'attention sur les bonnes pratiques concernant l'exigence en question.
    Pour cette conclusion il faut se limiter strictement aux recommandations et informations issus du guide IFSv8 en particulier {guide_row['Good practice']} et {guide_row['Example questions']}
    """
    
    messages = [
        {"role": "system", "content": "Veuillez générer une recommandation structurée pour la non-conformité suivante :"},
        {"role": "user", "content": prompt}
    ]

    try:
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="meta-llama/llama-4-maverick-17b-128e-instruct"
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        st.error(f"Erreur lors de la génération de la recommandation: {str(e)}")
        return None

# Fonction pour récupérer les informations du guide en fonction du numéro d'exigence
def get_guide_info(num_exigence, guide_df):
    guide_row = guide_df[guide_df['NUM_REQ'].str.contains(num_exigence, na=False)]
    if guide_row.empty:
        st.error(f"Aucune correspondance trouvée pour le numéro d'exigence : {num_exigence}")
        return None
    return guide_row.iloc[0]

# Fonction principale
def main():
    st.markdown(
        """
        <style>
        .main-header {
            font-size: 36px; /* Taille de la police */
            font-weight: bold; /* Gras */
            color: #333333; /* Couleur du texte */
        }
        </style>
        <div class="main-header">Assistant VisiPilot pour Plan d'Actions IFS</div>
        """, 
        unsafe_allow_html=True
    ) 
  # Ajout de la dropdown d'explications
    with st.expander("Comment utiliser cette application"):
        st.write("""
    **Étapes d'utilisation:**
    
    1. **Téléchargez votre plan d'actions IFSv8:** Cliquez sur le bouton "Téléchargez votre plan d'action" et sélectionnez le fichier Excel contenant les non-conformités.
    2. **Sélectionnez un numéro d'exigence:** Après avoir chargé le fichier, choisissez un numéro d'exigence spécifique à partir du menu déroulant.
    3. **Générez des recommandations:** Cliquez sur "Générer Recommandations" pour obtenir des suggestions de correction, preuves et actions correctives pour la non-conformité sélectionnée.
    4. **Affichage des recommandations:** Une fois les recommandations générées, elles apparaîtront dans une fenêtre spécifique située sous la ligne de la non-conformité correspondante. Cette fenêtre possède un fond coloré pour une meilleure visibilité. Vous pouvez l'agrandir ou la rétrécir en utilisant le bouton situé à droite de la fenêtre.

    **Résultat attendu:**
    
    Vous obtiendrez une liste de recommandations personnalisées basées sur les non-conformités identifiées dans votre plan d'action. Ces recommandations incluront des actions correctives, les types de preuves nécessaires, la cause probable, et les corrections immédiates.
""")

    # Initialiser la clé 'recommendation_expanders' si elle n'existe pas
    if 'recommendation_expanders' not in st.session_state:
        st.session_state['recommendation_expanders'] = {}

    # Upload du fichier Excel du plan d'action
    uploaded_file = st.file_uploader("Téléchargez votre plan d'action (fichier Excel)", type=["xlsx"])
    
    if uploaded_file:
        action_plan_df = load_action_plan(uploaded_file)
        if action_plan_df is not None:
            guide_df = pd.read_csv("https://raw.githubusercontent.com/M00N69/Action-planGroq/main/Guide%20Checklist_IFS%20Food%20V%208%20-%20CHECKLIST.csv")
            
            st.write("## Plan d'Action IFS")
            for index, row in action_plan_df.iterrows():
                cols = st.columns([1, 4, 4, 2])
                cols[0].write(row["Numéro d'exigence"])
                cols[1].write(row["Exigence IFS Food 8"])
                cols[2].write(row["Explication (par l’auditeur/l’évaluateur)"])
                cols[3].button(
                    "Générer Recommandation", 
                    key=f"generate_{index}",
                    on_click=generate_recommendation_and_expand,
                    args=(index, row, guide_df)
                )

                # Afficher les recommandations dans un expander s'il est déjà généré
                if index in st.session_state['recommendation_expanders']:
                    expander = st.expander(f"Recommandation pour Numéro d'exigence: {row['Numéro d\'exigence']}", expanded=True)
                    expander.markdown(st.session_state['recommendation_expanders'][index]['text'])

def generate_recommendation_and_expand(index, row, guide_df):
    guide_row = get_guide_info(row["Numéro d'exigence"], guide_df)
    
    if guide_row is not None:
        recommendation_text = generate_ai_recommendation_groq(row, guide_row)
        
        if recommendation_text:
            st.success("Recommandation générée avec succès!")
            st.session_state['recommendation_expanders'][index] = {
                'text': recommendation_text,
            }

if __name__ == "__main__":
    main()
