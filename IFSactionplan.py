import streamlit as st
import pandas as pd
import time
from groq import Groq
from io import BytesIO
from docx import Document
from fpdf import FPDF

# Configurer la page de l'application
st.set_page_config(layout="wide")

# Fonction pour ajouter des styles CSS personnalisés
def add_css_styles():
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
        .banner {
            text-align: center;
            margin-bottom: 40px;
        }
        .dataframe-container {
            margin-bottom: 40px;
        }
        .recommendation-container {
            padding: 20px;
            margin-bottom: 30px;
            border: 1px solid #004080;
            border-radius: 5px;
            background-color: #f0f8ff;
        }
        .recommendation-header {
            font-weight: bold;
            font-size: 18px;
            color: #004080;
            margin-bottom: 10px;
        }
        .recommendation-content {
            margin-bottom: 10px;
            font-size: 16px;
            line-height: 1.5;
        }
        .spinner-message {
            font-size: 22px;
            color: red;
            text-align: center;
            margin-top: 20px;
        }
        .warning {
            color: red;
            font-weight: bold;
        }
        .success {
            color: green;
            font-weight: bold;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
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
# Fonction pour extraire les sections d'une recommandation issue du CSV
def extract_sections(recommendation):
    sections = ["Correction immédiate", "Type de preuve", "Cause probable", "Action corrective"]
    result = {}
    for i, section in enumerate(sections):
        start = recommendation.find(section)
        if start != -1:
            end = recommendation.find(sections[i+1], start) if i+1 < len(sections) else len(recommendation)
            result[section] = recommendation[start + len(section) + 1:end].strip()
        else:
            result[section] = ""
    return result

# Fonction pour générer une recommandation avec un tableau structuré
def generate_ai_recommendation_groq(non_conformity, guide_row, csv_df):
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
        base_recommendation = chat_completion.choices[0].message.content

        # Extraire les sections du CSV pour l'exigence correspondante
        csv_recommendation = csv_df[csv_df['Numéro d'exigence'] == non_conformity["Numéro d'exigence"]].iloc[0]
        structured_recommendation = extract_sections(csv_recommendation['Recommandation'])

        # Combiner la recommandation générée avec le contenu structuré du CSV
        final_recommendation = f"""
        {base_recommendation}
        
        ### Recommandation Structurée:
        - **Correction immédiate**: {structured_recommendation["Correction immédiate"]}
        - **Type de preuve**: {structured_recommendation["Type de preuve"]}
        - **Cause probable**: {structured_recommendation["Cause probable"]}
        - **Action corrective**: {structured_recommendation["Action corrective"]}
        """

        return final_recommendation

    except Exception as e:
        st.error(f"Erreur lors de la génération de la recommandation: {str(e)}")
        return None
# Fonction pour extraire les sections d'une recommandation issue du CSV
def extract_sections(recommendation):
    sections = ["Correction immédiate", "Type de preuve", "Cause probable", "Action corrective"]
    result = {}
    for i, section in enumerate(sections):
        start = recommendation.find(section)
        if start != -1:
            end = recommendation.find(sections[i+1], start) if i+1 < len(sections) else len(recommendation)
            result[section] = recommendation[start + len(section) + 1:end].strip()
        else:
            result[section] = ""
    return result

# Fonction pour générer une recommandation avec un tableau structuré
def generate_ai_recommendation_groq(non_conformity, guide_row, csv_df):
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
        base_recommendation = chat_completion.choices[0].message.content

        # Extraire les sections du CSV pour l'exigence correspondante
        csv_recommendation = csv_df[csv_df['Numéro d'exigence'] == non_conformity["Numéro d'exigence"]].iloc[0]
        structured_recommendation = extract_sections(csv_recommendation['Recommandation'])

        # Combiner la recommandation générée avec le contenu structuré du CSV
        final_recommendation = f"""
        {base_recommendation}
        
        ### Recommandation Structurée:
        - **Correction immédiate**: {structured_recommendation["Correction immédiate"]}
        - **Type de preuve**: {structured_recommendation["Type de preuve"]}
        - **Cause probable**: {structured_recommendation["Cause probable"]}
        - **Action corrective**: {structured_recommendation["Action corrective"]}
        """

        return final_recommendation

    except Exception as e:
        st.error(f"Erreur lors de la génération de la recommandation: {str(e)}")
        return None
# Fonction principale
def main():
    add_css_styles()

    st.markdown('<div class="banner"><img src="https://raw.githubusercontent.com/M00N69/Gemini-Knowledge/main/visipilot%20banner.PNG" alt="Banner" width="80%"></div>', unsafe_allow_html=True)
    st.markdown('<div class="main-header">Assistant VisiPilot pour Plan d\'Actions IFS</div>', unsafe_allow_html=True)
    st.write("Téléchargez votre plan d'action et obtenez des recommandations pour les corrections et les actions correctives.")

    # Upload du fichier Excel du plan d'action
    uploaded_file = st.file_uploader("Téléchargez votre plan d'action (fichier Excel)", type=["xlsx"])
    
    if uploaded_file:
        action_plan_df = load_action_plan(uploaded_file)
        if action_plan_df is not None:
            st.markdown('<div class="dataframe-container">' + action_plan_df.to_html(classes='dataframe', index=False) + '</div>', unsafe_allow_html=True)
            
            # Charger le guide IFSv8 depuis le fichier CSV
            guide_df = pd.read_csv("https://raw.githubusercontent.com/M00N69/Action-planGroq/main/Guide%20Checklist_IFS%20Food%20V%208%20-%20CHECKLIST.csv")
            csv_df = pd.read_csv("/path/to/your/csv_file.csv")  # Add the path to your CSV file here

            # Préparation d'une liste pour les recommandations
            recommendations = []

            # Sélection du numéro d'exigence
            selected_exigence = st.selectbox("Sélectionnez un numéro d'exigence pour générer des recommandations :", action_plan_df["Numéro d'exigence"].unique())

            if st.button("Générer Recommandations"):
                # Récupérer la ligne spécifique du guide correspondant à l'exigence sélectionnée
                guide_row = get_guide_info(selected_exigence, guide_df)
                non_conformity = action_plan_df[action_plan_df["Numéro d'exigence"] == selected_exigence].iloc[0]

                # Affichage d'un spinner pendant la génération des recommandations
                with st.spinner('Génération des recommandations en cours...'):
                    recommendation_text = generate_ai_recommendation_groq(non_conformity, guide_row, csv_df)
                    if recommendation_text:
                        st.success("Recommandation générée avec succès!")
                        recommendations.append({
                            "Numéro d'exigence": selected_exigence,
                            "Recommandation": recommendation_text
                        })
                        # Ajouter la recommandation au DataFrame du plan d'action
                        action_plan_df.loc[action_plan_df["Numéro d'exigence"] == selected_exigence, "Recommandation"] = recommendation_text

            if recommendations:
                recommendations_df = pd.DataFrame(recommendations)
                st.subheader("Résumé des Recommandations")
                display_recommendations(recommendations_df)

                # Télécharger au format CSV
                st.download_button(
                    label="Télécharger les recommandations (CSV)",
                    data=recommendations_df.to_csv(index=False),
                    file_name="recommandations_ifs_food.csv",
                    mime="text/csv",
                )

                # Télécharger au format texte
                text_file = generate_text_file(recommendations_df)
                st.download_button(
                    label="Télécharger les recommandations (Texte)",
                    data=text_file,
                    file_name="recommandations_ifs_food.txt",
                    mime="text/plain",
                )

                # Télécharger au format DOCX
                docx_file = generate_docx_file(recommendations_df)
                st.download_button(
                    label="Télécharger les recommandations (DOCX)",
                    data=docx_file,
                    file_name="recommandations_ifs_food.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                )

if __name__ == "__main__":
    main()

