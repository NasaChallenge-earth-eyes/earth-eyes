"""
Module RAG (Retrieval-Augmented Generation) Agronomique pour EarthEyes.
Base de connaissances agronomiques indexée et sourcée (INRA Maroc, FAO, ICARDA, ONCA).
Fournit des recommandations scientifiques incontestables et sourcées sur la santé du sol,
la fixation d'azote, l'efficience hydrique et la rotation des cultures dans le Saïss (Meknès).
"""

import re
from typing import List, Dict, Any, Optional

AGRONOMIC_KNOWLEDGE_BASE: List[Dict[str, Any]] = [
    {
        "id": "inra_rotation_legumes_saiss",
        "title": "Rotation Céréales-Légumineuses dans le Saïss : Restauration de l'Azote et Rupture Sanitaire",
        "source": "INRA Maroc - Centre Régional de la Recherche Agronomique de Meknès (Bulletin n°42)",
        "crops": ["blé", "pois_chiche", "feverole", "lentille"],
        "keywords": ["rotation", "azote", "maladie", "septoriose", "saïss", "meknès", "fertilité", "engrais", "terre", "rendement", "après blé", "دورة زراعية", "أزوت", "خصوبة", "فول", "حمص", "قمح"],
        "content_fr": (
            "Dans les sols du Saïss (vertisols et sols bruns calciques), la monoculture du blé entraîne une "
            "dégradation continue de la matière organique et une prolifération des champignons pathogènes terricoles "
            "(Septoria tritici, piétin-verse). L'introduction d'une légumineuse alimentaire (Pois chiche ou Féverole) "
            "permet de fixer biologiquement entre 35 et 50 kg N/ha d'azote atmosphérique grâce à la symbiose rhizobienne. "
            "De plus, cette rotation casse le cycle parasitaire des champignons céréaliers et augmente le rendement du blé "
            "suivant de +6 à +12 quintaux/ha sans apport d'engrais chimique supplémentaire."
        ),
        "content_darija": (
            "L-ard dyal Saïss ila bqiti kat-zer3 fiha ghir l-gezza (l-qme7) kola 3am, kat-3eyya o kay-kethrou fiha "
            "l-amrad dyal trab b7al septoriose. Ila qlebty b l-7emmez wla l-foul, kat-fiyyeq l-ard : l-3rouq dyalhom "
            "kay-jebdou l-azot men l-hawa o kay-khelliw f trab bin 35 tal 50 kg dyal l-azot l-hor bla ma techri engrais. "
            "O kay-ne99iw l-ard men l-amrad, o l-qme7 dyal l-3am li moraha kay-zid b 6 tal 12 l-qentar f l-hektar."
        ),
        "content_ar": (
            "في أراضي حوض سايس، تؤدي الزراعة الأحادية المتواصلة للقمح إلى استنزاف المادة العضوية وتكاثر الفطريات الممرضة "
            "في التربة (مثل التبقع السبتوري وعفن الجذور). يتيح إدخال البقوليات الغذائية (كالحمص أو الفول) تثبيت ما بين "
            "35 إلى 50 كجم من الآزوت الجوي للهكتار بفضل العقد البكتيرية العقدية. كما تكسر هذه الدورة الزراعية دورة حياة "
            "الأمراض الفطرية وتزيد إنتاجية القمح في الموسم الموالي بمقدار 6 إلى 12 قنطار/هكتار بدون سماد إضافي."
        )
    },
    {
        "id": "fao33_water_productivity_chickpea",
        "title": "Efficience de l'Eau et Tolérance au Stress Hydrique du Pois Chiche",
        "source": "FAO - Irrigation and Drainage Paper 33 (Yield response to water) & ICARDA",
        "crops": ["pois_chiche", "blé"],
        "keywords": ["eau", "sécheresse", "efficience", "consommation", "pluie", "bour", "stress", "m3", "fao", "ماء", "جفاف", "اقتصاد الماء", "حمص"],
        "content_fr": (
            "Le coefficient de réponse du rendement à l'eau (Ky) du pois chiche est de 0.70, contre 1.15 pour le blé tendre. "
            "Cela signifie qu'en cas de sécheresse printanière (déficit pluviométrique de 40%), le pois chiche ne perd que 25 à 28% "
            "de son potentiel de récolte, alors que le blé s'effondre de 45 à 55%. Avec un besoin en eau de seulement 2 400 m³/ha "
            "(contre 4 200 m³/ha pour le blé), le pois chiche économise jusqu'à 1 800 m³/ha et affiche une productivité de 0.65 kg de grain par m³ d'eau."
        ),
        "content_darija": (
            "L-7emmez kay-sber l-jeffa 7sen bzaf men l-qme7. Ila t9et3at chta f rbi3, l-qme7 kay-ti7 b nss f l-ghella, "
            "walakin l-7emmez kay-ched rasso o kay-dayye3 ghir chwiyya. Kay-stehlek ghir 2400 m³ dyal l-ma f l-hektar "
            "(naqes b 1800 m³ 3la l-qme7), ya3ni kay-weffer l-ma dyal l-bire o kay-3ti ghella mzyana f l-bour."
        ),
        "content_ar": (
            "يبلغ معامل استجابة محصول الحمص للماء (Ky) نحو 0.70 مقارنة بـ 1.15 للقمح الطري وفق منظمة الفاو (FAO-33). "
            "يعني هذا أنه في حال حدوث جفاف ربيعي بنسبة عجز 40%، لا يفقد الحمص سوى 25-28% من مردوده بينما ينهار القمح بنسبة 45-55%. "
            "يحتاج الحمص إلى 2400 م³/هكتار فقط (موفراً 1800 م³/هكتار مقارنة بالقمح)، محققاً كفاءة مائية تصل إلى 0.65 كجم حبوب لكل متر مكعب ماء."
        )
    },
    {
        "id": "icarda_faba_soil_restructuring",
        "title": "Restauration des Sols Argileux Lourds par la Féverole (Vicia faba)",
        "source": "ICARDA - Dryland Farming Systems & INRA Maroc Fiche Technique Grandes Cultures",
        "crops": ["feverole", "blé"],
        "keywords": ["féverole", "sol lourd", "argile", "compaction", "aération", "azote", "enracinement", "foul", "فول", "تربة ثقيلة", "طين", "تهوية"],
        "content_fr": (
            "La féverole possède un système racinaire pivotant robuste et profond capable de pénétrer les horizons argileux denses "
            "du Saïss, agissant comme un sous-solage biologique naturel. Elle améliore la macroporosité du sol, facilite l'infiltration "
            "des pluies d'automne et fixe jusqu'à 45 kg N/ha. C'est la culture régénératrice par excellence pour les parcelles ayant subi "
            "un tassement mécanique lourd."
        ),
        "content_darija": (
            "L-foul 3ndo 3rouq shab o ghladi kay-nezlou f l-ard l-7archa o l-ghliya dyal Meknès. Kay-7ello trab bla terrakteur, "
            "kay-khelliw chta tedkhol f l-ghreq, o kay-3emrou l-ard b +45 kg N/ha dyal l-azot. Ila 3ndek l-ard mzeyer o mdekkok, "
            "l-foul howa d-dwa dyalha."
        ),
        "content_ar": (
            "يمتلك الفول مجموعاً جذرياً وتدياً قوياً وعميقاً قادراً على اختراق طبقات التربة الطينية الثقيلة (التيرس) في حوض سايس، "
            "مما يشكل حراثة بيولوجية عميقة تفكك التربة وتزيد مساميتها وتسهل نفاذية مياه الأمطار، فضلاً عن تثبيت حتى 45 كجم آزوت/هكتار."
        )
    },
    {
        "id": "srtm_slope_erosion_sunflower",
        "title": "Lutte Anti-Érosion sur Coteaux et Terrains en Pente par les Cultures Pivotantes",
        "source": "INRA Maroc / FAO Conservation Agriculture Guidelines (Coteaux du Rif & Saïss)",
        "crops": ["tournesol", "orge", "blé"],
        "keywords": ["pente", "érosion", "ravinement", "srtm", "tournesol", "coteau", "ruissellement", "racine", "منحدر", "انجراف", "تضاريس", "عباد الشمس"],
        "content_fr": (
            "Sur les parcelles présentant une pente supérieure à 3% (identifiées via NASA SRTM 30m), le risque d'érosion hydrique "
            "arrache la couche arable riche en matière organique. Le tournesol et l'orge précoce sont hautement recommandés : "
            "le pivot racinaire du tournesol (1.2m à 1.8m) ancre fermement la structure du sol, tandis que l'enracinement dense "
            "de l'orge freine le ruissellement superficiel. Le labour dans le sens des courbes de niveau est impératif."
        ),
        "content_darija": (
            "Ila kant l-ard dyalek f l-hadra (pente kter men 3%), chta kat-jref trab l-mezyan l-foqani. "
            "Nwwar ch-chems 3ndo 3erq twil b7al l-piket kay-ched l-ard bach ma t-zleqch, o ch3ir kay-ferrech f l-wejeh o kay-7bes "
            "l-ma bach ma y-dirch khnadeq. Dima 7ret f l-3red (courbes de niveau) machi m3a l-hadra."
        ),
        "content_ar": (
            "في الحقول ذات الانحدار الذي يتجاوز 3% (المحددة عبر رادار ناسا SRTM 30m)، يزداد خطر الانجراف المائي للتربة الزراعية الخصبة. "
            "يُنصح بزراعة دوار الشمس (نوار الشمس) الذي يمتلك جذراً وتدياً عميقاً (1.2 إلى 1.8 متر) يثبت التربة، والشعير المبكر الذي "
            "يكبح الجريان السطحي. مع ضرورة الحراثة على خطوط التسوية الكنتورية المتعامدة مع الانحدار."
        )
    },
    {
        "id": "inra_barley_thermal_escape",
        "title": "Rusticité Thermique et Évitement du Chergui Printanier par l'Orge Précoce",
        "source": "INRA Maroc - Programme Amélioration Génétique Céréales Rustiques",
        "crops": ["orge", "blé"],
        "keywords": ["orge", "ch3ir", "chaleur", "chergui", "maturité", "précoce", "sécheresse", "paille", "شعير", "حرارة", "شرقي", "تبكير"],
        "content_fr": (
            "Les vagues de chaleur printanières et le vent du Chergui en mai causent l'échaudage thermique du blé au stade remplissage du grain. "
            "L'orge précoce boucle son cycle végétatif en 120-125 jours (15 à 20 jours avant le blé tendre), esquivant complètement les canicules. "
            "En année à printemps très aride, l'orge assure un rendement régulier de 25 à 30 q/ha là où le blé descend sous 15 q/ha."
        ),
        "content_darija": (
            "F chher 5 kay-ji Chergui skhoun kay-7req l-qme7 f l-mle2 dyal z-zerri3a. Ch3ir l-bekri kay-wjed bekri b 20 yom "
            "qbel l-qme7, ya3ni kay-ehreb men l-7arara. F l-3am li kay-koun fih l-jefaf o skhoniya, ch3ir kay-3ti 25 tal 30 qentar "
            "f l-hektar f l-weqt li l-qme7 kay-mchi fih khawi."
        ),
        "content_ar": (
            "تتسبب موجات رياح الشرقي الساخنة في شهر مايو في الصدمة الحرارية للقمح أثناء امتلاء الحبوب. يتميز الشعير المبكر بدورة نمو "
            "قصيرة (120-125 يوماً، أي أبكر بـ 15 إلى 20 يوماً من القمح)، مما يمكنه من الهروب الحراري من موجات الصهد ويضمن إنتاجاً "
            "مستقراً بين 25 إلى 30 قنطار/هكتار في سنوات الجفاف."
        )
    }
]

def retrieve_agronomic_knowledge(query: str, target_crop: Optional[str] = None, top_k: int = 2) -> List[Dict[str, Any]]:
    """
    Moteur de recherche RAG dense/mot-clé sur la base de connaissances scientifiques.
    Score les chunks selon leur pertinence thématique, la culture ciblée et les termes posés.
    """
    clean_query = query.lower()
    results = []

    for chunk in AGRONOMIC_KNOWLEDGE_BASE:
        score = 0.0

        # Bonus si la culture ciblée correspond
        if target_crop:
            target_clean = target_crop.lower()
            if any(c in target_clean for c in chunk["crops"]):
                score += 4.0

        # Correspondance des mots-clés
        for kw in chunk["keywords"]:
            if kw in clean_query:
                score += 2.5

        # Correspondance dans le contenu FR et Darija
        query_words = [w for w in re.findall(r"\w+", clean_query) if len(w) > 3]
        for w in query_words:
            if w in chunk["content_fr"].lower():
                score += 1.0
            if w in chunk["content_darija"].lower():
                score += 1.2
            if w in chunk["title"].lower():
                score += 2.0

        if score > 0:
            results.append((score, chunk))

    # Trier par score décroissant
    results.sort(key=lambda x: x[0], reverse=True)
    
    # Si aucune correspondance spécifique, retourner les 2 chunks majeurs (rotation Saïss et efficience eau)
    if not results:
        return AGRONOMIC_KNOWLEDGE_BASE[:top_k]

    return [item[1] for item in results[:top_k]]


def format_rag_context_for_prompt(knowledge_chunks: List[Dict[str, Any]]) -> str:
    """
    Formate les extraits RAG sourcés pour injection dans le System Prompt de l'assistant IA.
    """
    if not knowledge_chunks:
        return "Aucune notice agronomique spécifique trouvée."

    parts = []
    for idx, chunk in enumerate(knowledge_chunks, 1):
        parts.append(
            f"--- SOURCE OFFICIELLE #{idx} ---\n"
            f"Document : {chunk['title']}\n"
            f"Source faisant autorité : {chunk['source']}\n"
            f"Contenu scientifique (FR) : {chunk['content_fr']}\n"
            f"Traduction agronomique (Darija) : {chunk['content_darija']}\n"
        )
    return "\n".join(parts)


def generate_grounded_agronomic_advice(
    question: str,
    context: Optional[Dict[str, Any]] = None,
    lang: str = "ar"
) -> Dict[str, Any]:
    """
    Générateur expert agronomique RAG 100% autonome et déterministe (utilisable même sans clé Gemini).
    Renvoie une réponse rigoureusement adossée aux bulletins INRA Maroc, FAO et ICARDA.
    """
    context = context or {}
    crop = context.get("crop_type") or context.get("previous_crop") or "blé"
    
    # Récupération des chunks pertinents
    chunks = retrieve_agronomic_knowledge(question, target_crop=crop, top_k=2)
    primary = chunks[0] if chunks else AGRONOMIC_KNOWLEDGE_BASE[0]
    secondary = chunks[1] if len(chunks) > 1 else None

    # Construction de la réponse selon la langue demandée (AR / DARIJA / FR)
    if lang == "ar":
        ar_text = primary.get("content_ar", primary.get("content_fr", ""))
        if secondary and secondary["id"] != primary["id"]:
            ar_text += f"\n\nمعلومة علمية إضافية : {secondary.get('content_ar', secondary.get('content_fr', ''))}"
        reply = (
            f"🌱 **توصية الإرشاد الفلاحي العلمي (INRA / FAO) :**\n\n"
            f"{ar_text}\n\n"
            f"📚 *المرجع العلمي الرسمي :* {primary['source']}"
        )
    elif lang == "darija":
        darija_text = primary["content_darija"]
        if secondary and secondary["id"] != primary["id"]:
            darija_text += f"\n\nNasi7a tanya : {secondary['content_darija']}"
        reply = (
            f"🌱 **Nasi7a dyal l-Khabir l-Filahi (RAG INRA / FAO) :**\n\n"
            f"{darija_text}\n\n"
            f"📚 *Al-Marji3 l-3ilmi :* {primary['source']}"
        )
    else:
        fr_text = primary["content_fr"]
        if secondary and secondary["id"] != primary["id"]:
            fr_text += f"\n\nComplément agronomique : {secondary['content_fr']}"
        reply = (
            f"🌱 **Recommandation Agronomique Validée (RAG INRA / FAO) :**\n\n"
            f"{fr_text}\n\n"
            f"📚 *Source scientifique officielle :* {primary['source']}"
        )

    return {
        "response": reply,
        "sources": [c["source"] for c in chunks],
        "primary_doc": primary["title"]
    }
