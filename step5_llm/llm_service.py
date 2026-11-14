import os
import json
from typing import Optional

from .rag_agronomy import (
    retrieve_agronomic_knowledge,
    format_rag_context_for_prompt,
    generate_grounded_agronomic_advice
)

try:
    import google.generativeai as genai
except Exception as exc:
    genai = None
    _GENAI_IMPORT_ERROR = exc
else:
    _GENAI_IMPORT_ERROR = None

# Configurer l'API de Gemini avec la clé d'API
api_key = os.environ.get("GEMINI_API_KEY")
os.environ["GEMINI_API_KEY"] = api_key or ""
if api_key and genai is not None:
    genai.configure(api_key=api_key)

def ask_agronomist(question: str, context: dict) -> str:
    """
    Pose une question agricole à l'agronome virtuel en s'appuyant sur le RAG agronomique
    (INRA Maroc, FAO, ICARDA) et Gemini (si disponible).
    """
    crop_name = context.get('crop_type', 'blé')
    rag_chunks = retrieve_agronomic_knowledge(question, target_crop=crop_name, top_k=2)
    rag_context_text = format_rag_context_for_prompt(rag_chunks)

    if not os.environ.get("GEMINI_API_KEY") or genai is None:
        advice_res = generate_grounded_agronomic_advice(question, context, lang="ar")
        return advice_res["response"]

    prompt = f"""
    Tu es un conseiller agronome marocain expérimenté de l'INRA et de l'ONCA. Tu t'adresses à un agriculteur local du Saïss / Meknès.
    Ton rôle est d'analyser les données physiques de sa parcelle et de lui prodiguer des conseils scientifiques rigoureux
    fondés sur les connaissances agronomiques officielles ci-dessous.
    Réponds en Darija marocaine (en alphabet latin "arabizi" ou en français si l'agriculteur pose sa question en français).

    === CONNAISSANCES AGRONOMIQUES OFFICIELLES (RAG INRA MAROC / FAO / ICARDA) ===
    {rag_context_text}
    =============================================================================

    Données physiques et diagnostics de la parcelle :
    - Culture actuelle / précédente : {context.get('crop_type', 'Non spécifiée')}
    - Rendement estimé (WOFOST) : {context.get('yield_estimate')} kg/ha
    - Maladie détectée : {context.get('disease', 'aucune maladie détectée')}
    - Indice NDVI (Santé végétative par satellite) : {context.get('ndvi', 'Non disponible')}
    - Caractéristiques du sol :
      * pH : {context.get('soil_ph', 'Non disponible')}
      * Argile : {context.get('clay_pct', 'Non disponible')}%
      * Sable : {context.get('sand_pct', 'Non disponible')}%

    Question de l'agriculteur : "{question}"

    Consignes impératives :
    1. Réponds en Darija marocaine claire et bienveillante (style conversationnel d'agronome de terrain).
    2. Cite explicitement la source scientifique (ex: "7asab ab7at INRA Maroc..." ou "Directive FAO-33...").
    3. Explique les bénéfices physiques (fixation d'azote kg/ha, économie d'eau m³/ha, santé durable du sol).
    """

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        advice_res = generate_grounded_agronomic_advice(question, context, lang="ar")
        return advice_res["response"]


def ask_agronomist_interactive(question: str, history: list, current_form: dict, context: Optional[dict] = None) -> dict:
    """
    Mode conversationnel interactif.
    Permet de guider l'agriculteur à remplir sa parcelle et d'extraire les paramètres (crop, sowing_date, location, etc.).
    Retourne un dictionnaire:
    {
       "response": "Le message à afficher à l'utilisateur",
       "extracted_data": {
           "crop_type": "wheat" | "barley" | "olive" | "potato" | "tomato" | null,
           "sowing_date": "YYYY-MM-DD" | null,
           "location": "Nom de ville ou région au Maroc" | null,
           "historical_yields": [{"year": int, "yield": float}] | null
       }
    }
    """
    def normalize_crop(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        text = text.lower()
        if any(keyword in text for keyword in ['blé', 'ble', 'qam7', 'qamh', 'wheat', 'kam7']):
            return 'wheat'
        if any(keyword in text for keyword in ['orge', 'barley', 'ch3ir']):
            return 'barley'
        if any(keyword in text for keyword in ['olive', 'zitoun', 'zitoune']):
            return 'olive'
        if any(keyword in text for keyword in ['pomme de terre', 'batata', 'potato', 'batat', 'patate']):
            return 'potato'
        if any(keyword in text for keyword in ['tomate', 'tomato', 'tamata']):
            return 'tomato'
        return None

    def parse_date(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        normalized = text.lower().replace('/', '-').replace('.', '-').replace(',', ' ')
        tokens = normalized.split()
        for token in tokens:
            if '-' in token:
                parts = token.split('-')
                if len(parts) == 3:
                    try:
                        day, month, year = int(parts[0]), int(parts[1]), int(parts[2])
                        if 1 <= day <= 31 and 1 <= month <= 12 and year > 1900:
                            return f"{year:04d}-{month:02d}-{day:02d}"
                    except Exception:
                        continue
        months = {
            'janvier': '01', 'février': '02', 'fevrier': '02', 'mars': '03', 'avril': '04', 'mai': '05', 'juin': '06',
            'juillet': '07', 'août': '08', 'aout': '08', 'septembre': '09', 'octobre': '10', 'novembre': '11', 'décembre': '12'
        }
        words = [w.strip('.,') for w in normalized.split()]
        for word in words:
            if word in months:
                day = None
                year = None
                for token in words:
                    if token.isdigit() and 1 <= int(token) <= 31 and day is None:
                        day = int(token)
                    if token.isdigit() and len(token) == 4:
                        year = int(token)
                if day and year:
                    return f"{year:04d}-{int(months[word]):02d}-{day:02d}"
        return None

    def parse_location(text: Optional[str]) -> Optional[str]:
        if not text:
            return None
        lower = text.lower()
        places = {
            'beni mellal': 'Beni Mellal',
            'بني ملال': 'Beni Mellal',
            'casablanca': 'Casablanca',
            'الدار البيضاء': 'Casablanca',
            'rabat': 'Rabat',
            'الرباط': 'Rabat',
            'marrakech': 'Marrakech',
            'مراكش': 'Marrakech',
            'fes': 'Fes',
            'fès': 'Fes',
            'فاس': 'Fes'
        }
        for key, value in places.items():
            if key in lower:
                return value
        return None

    def parse_historical(text: Optional[str]):
        if not text:
            return None
        tokens = [token.strip('.,') for token in text.replace('/', ' ').split()]
        results = []
        for idx, token in enumerate(tokens):
            if token.isdigit() and len(token) == 4:
                year = int(token)
                if idx + 1 < len(tokens) and tokens[idx + 1].replace('.', '', 1).isdigit():
                    results.append({'year': year, 'yield': float(tokens[idx + 1])})
        return results if results else None

    def build_response(message: str, extracted: dict) -> dict:
        return {
            'response': message,
            'extracted_data': extracted
        }

    extracted_data = {
        'crop_type': None,
        'sowing_date': None,
        'location': None,
        'historical_yields': None
    }

    if not os.environ.get("GEMINI_API_KEY") or genai is None:
        advice = generate_grounded_agronomic_advice(question, context=current_form, lang="ar")
        return build_response(advice["response"], extracted_data)

    crop_type = normalize_crop(current_form.get('crop_type'))
    sowing_date = current_form.get('sowing_date')
    location = current_form.get('location')
    historical_yields = current_form.get('historical_yields')
    photo_uploaded = bool(current_form.get('photo_uploaded'))

    if not crop_type:
        extracted_data['crop_type'] = normalize_crop(question)
    if not sowing_date:
        extracted_data['sowing_date'] = parse_date(question)
    if not location:
        extracted_data['location'] = parse_location(question)
    if not historical_yields:
        extracted_data['historical_yields'] = parse_historical(question)

    if any(extracted_data.values()):
        response_parts = []
        if extracted_data['crop_type']:
            response_parts.append(f"Très bien, je note {extracted_data['crop_type']} comme culture.")
        if extracted_data['sowing_date']:
            response_parts.append(f"Date de semis enregistrée : {extracted_data['sowing_date']}.")
        if extracted_data['location']:
            response_parts.append(f"Localisation capturée : {extracted_data['location']}.")
        if extracted_data['historical_yields']:
            response_parts.append("Historique de rendement ajouté.")
        response_parts.append("Je peux maintenant continuer avec la suite du formulaire.")
        return build_response(' '.join(response_parts), extracted_data)

    missing_fields = []
    if not crop_type:
        missing_fields.append("le type de culture")
    if not photo_uploaded:
        missing_fields.append("la photo de la feuille")
    if not location:
        missing_fields.append("la localisation")
    if not sowing_date:
        missing_fields.append("la date de semis")

    # Mettre à jour les variables avec ce qui a été extrait localement de la question courante
    if extracted_data['crop_type']:
        crop_type = extracted_data['crop_type']
        if "le type de culture" in missing_fields:
            missing_fields.remove("le type de culture")
    if extracted_data['sowing_date']:
        sowing_date = extracted_data['sowing_date']
        if "la date de semis" in missing_fields:
            missing_fields.remove("la date de semis")
    if extracted_data['location']:
        location = extracted_data['location']
        if "la localisation" in missing_fields:
            missing_fields.remove("la localisation")

    # Récupération RAG pour enrichir la réponse conversationnelle
    rag_chunks = retrieve_agronomic_knowledge(question, target_crop=crop_type, top_k=2)
    rag_context_text = format_rag_context_for_prompt(rag_chunks)

    prompt = f"""
    Tu es un conseiller agronome marocain virtuel (INRA / ONCA Meknès).
    Réponds de manière pragmatique et rassurante en Darija marocaine (lettres latines / arabizi ou français selon l'interlocuteur).
    Adosse tes conseils aux recommandations officielles ci-dessous :

    === CONNAISSANCES AGRONOMIQUES OFFICIELLES (RAG INRA / FAO) ===
    {rag_context_text}
    ================================================================
    
    Ton objectif est d'aider l'agriculteur sur ses questions agricoles générales ou spécifiques (rotation, azote, eau, maladies),
    tout en l'accompagnant à compléter les informations de sa parcelle.

    Voici les informations de la parcelle actuellement connues :
    - Culture : {crop_type or 'Non spécifiée'}
    - Date de semis : {sowing_date or 'Non spécifiée'}
    - Localisation : {location or 'Non spécifiée'}
    - Historique de rendement : {historical_yields or 'Aucun historique renseigné'}
    - Photo de la feuille téléchargée : {'Oui' if photo_uploaded else 'Non'}

    Voici les informations manquantes prioritaires pour exécuter la simulation et la fusion de rendement :
    {", ".join(missing_fields) if missing_fields else "Aucune, toutes les informations clés sont prêtes !"}

    Message / Question de l'agriculteur : "{question}"

    Instructions de réponse :
    1. Réponds précisément à la question de l'agriculteur en t'appuyant sur les connaissances RAG et cite la source (INRA Maroc ou FAO).
    2. À la fin de ta réponse, si des informations clés sont manquantes, rappelle-lui de manière amicale de les renseigner.
    3. Si le message contenait de nouvelles informations pour le formulaire, extrais-les.
    4. Retourne TOUJOURS un JSON strict ayant exactement ce format :
    {{
      "response": "Ta réponse d'agronome avec citation scientifique suivie du rappel amical",
      "extracted_data": {{
         "crop_type": "wheat" ou "barley" ou "olive" ou "potato" ou "tomato" ou null,
         "sowing_date": "YYYY-MM-DD" ou null,
         "location": "Nom de la ville/région au Maroc" ou null,
         "historical_yields": [ {{"year": 2024, "yield": 4500.0}} ] ou null
      }}
    }}
    """

    try:
        model = genai.GenerativeModel('gemini-flash-latest')
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        text = response.text.strip()
        res_data = json.loads(text)
        if not isinstance(res_data, dict):
            raise ValueError('Format JSON invalide')
        
        # Combiner les données extraites localement et via Gemini
        gemini_extracted = res_data.get('extracted_data', {}) or {}
        final_extracted = {
            'crop_type': extracted_data['crop_type'] or gemini_extracted.get('crop_type'),
            'sowing_date': extracted_data['sowing_date'] or gemini_extracted.get('sowing_date'),
            'location': extracted_data['location'] or gemini_extracted.get('location'),
            'historical_yields': extracted_data['historical_yields'] or gemini_extracted.get('historical_yields')
        }
        
        return {
            'response': res_data.get('response', "Je n'ai pas compris, peux-tu reformuler ?"),
            'extracted_data': final_extracted
        }
    except Exception as e:
        print(f"Erreur ask_agronomist_interactive: {e}")
        return build_response(
            "J'ai rencontré un problème technique avec Gemini. Je continue en mode dégradé.",
            extracted_data
        )
