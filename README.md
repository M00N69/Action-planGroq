# Action-planGroq
Application Streamlit pour Plan d'Actions IFS Food 8
Introduction
Cette application Streamlit est conçue pour assister les utilisateurs dans la gestion des plans d'action liés à l'IFS Food version 8. Elle permet de charger un plan d'action sous forme de fichier Excel, de générer des recommandations d'actions correctives basées sur des non-conformités, et de télécharger ces recommandations dans divers formats (CSV, texte, DOCX).

Conception de l'application
Structure Générale
L'application est structurée en plusieurs fonctions principales, chacune ayant un rôle spécifique dans le processus global de gestion du plan d'action :

Interface Utilisateur et CSS Personnalisé :

add_css_styles(): Ajoute des styles CSS personnalisés pour améliorer l'esthétique et la présentation de l'application.
Gestion des Données :

load_action_plan(uploaded_file): Charge et nettoie le fichier Excel contenant le plan d'action. Il s'assure que les colonnes attendues sont présentes et retourne un DataFrame Pandas.
get_guide_info(num_exigence, guide_df): Extrait les informations pertinentes du guide IFSv8 pour une exigence spécifique.
Génération des Recommandations :

get_groq_client(): Initialise et retourne un client Groq, nécessaire pour la génération des recommandations via l'API.
generate_ai_recommendation_groq(non_conformity, guide_row): Génère une recommandation basée sur une non-conformité spécifique et les informations du guide IFSv8.
display_recommendations(recommendations_df): Affiche les recommandations générées sur l'interface Streamlit.
Export des Recommandations :

generate_text_file(recommendations_df): Crée un fichier texte contenant les recommandations.
generate_docx_file(recommendations_df): Crée un document Word (DOCX) avec les recommandations.
generate_pdf_file(recommendations_df): Crée un fichier PDF des recommandations.
Fonctionnalité Principale
L'application permet aux utilisateurs de :

Télécharger un plan d'action sous format Excel.
Sélectionner un numéro d'exigence spécifique.
Générer des recommandations d'actions correctives à l'aide de l'API Groq.
Visualiser les recommandations générées directement sur l'application.
Télécharger les recommandations dans divers formats (CSV, texte, DOCX).
Utilisation de l'API Groq
L'API Groq est utilisée pour générer des recommandations structurées basées sur des prompts spécifiques liés aux non-conformités. Cette approche permet de fournir des recommandations personnalisées et pertinentes pour chaque exigence.

Formats de Sortie
Les recommandations peuvent être téléchargées dans plusieurs formats :

CSV : Un fichier simple qui peut être ouvert dans Excel ou tout autre logiciel de tableur.
Texte : Un fichier texte brut pour une lecture rapide.
DOCX : Un document Word pour un formatage plus sophistiqué et une utilisation dans des rapports officiels.
Fonctionnement
1. Lancer l'application sur Streamlit Cloud
Pour lancer l'application sur Streamlit Cloud, suivez les étapes ci-dessous :

Créez un compte sur Streamlit Cloud.
Déployez l'application en liant votre dépôt GitHub contenant le code de l'application. Streamlit Cloud se chargera automatiquement d'exécuter le script Python.
Configurer les secrets :
Accédez aux Settings de votre application sur Streamlit Cloud.
Ajoutez les secrets nécessaires, notamment GROQ_API_KEY pour l'accès à l'API Groq.
2. Utilisation de l'interface sur Streamlit Cloud
Téléchargement du fichier Excel :

Cliquez sur le bouton pour télécharger le fichier Excel contenant le plan d'action.
L'application affichera un tableau contenant les données du plan d'action.
Sélection du numéro d'exigence :

Utilisez le menu déroulant pour sélectionner un numéro d'exigence spécifique pour lequel vous souhaitez générer une recommandation.
Génération des recommandations :

Cliquez sur le bouton "Générer Recommandations". L'application enverra une requête à l'API Groq pour obtenir la recommandation.
La recommandation sera affichée sous forme de texte structuré.
Téléchargement des recommandations :

Les recommandations générées peuvent être téléchargées dans différents formats via les boutons de téléchargement.
Conseils pour Streamlit Cloud
Optimisation des performances : Assurez-vous que les fichiers téléchargés ne sont pas trop volumineux pour éviter des ralentissements ou des limitations de mémoire sur Streamlit Cloud.
Vérification des erreurs : Si l'application ne génère pas de recommandations, vérifiez les secrets API et assurez-vous que l'API Groq est correctement configurée.
Dépendances
L'application nécessite les bibliothèques suivantes :

streamlit
pandas
groq
docx (de python-docx)
fpdf
Ces dépendances seront automatiquement installées sur Streamlit Cloud à partir du fichier requirements.txt dans votre dépôt GitHub.

Conclusion
Cette application est un outil puissant pour automatiser la génération de recommandations correctives dans le cadre des audits IFS Food 8. En combinant une interface utilisateur simple avec l'intelligence artificielle, elle permet de gagner du temps et d'améliorer la précision des recommandations d'actions correctives.
