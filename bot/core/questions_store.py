from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

# Dossier où sont stockées les questions :
# BOT-TERMINER/data/questions/*.json
QUESTIONS_DIR = Path("data/questions")


def _slugify(name: str) -> str:
    """
    Transforme une catégorie en nom de fichier simple.
    Exemple : "Jeux vidéo" -> "jeux_vidéo" -> "jeux_vidéo"
    (on gère surtout les espaces, toi tu peux déjà utiliser : sport, esport, etc.)
    """
    slug = name.strip().lower().replace(" ", "_")
    if not slug:
        slug = "general"
    return slug


def get_categories() -> List[str]:
    """
    Liste les catégories existantes d'après les fichiers JSON.
    Exemple de retour : ["sport", "esport", "culture", ...]
    """
    if not QUESTIONS_DIR.exists():
        return []
    cats: List[str] = []
    for f in QUESTIONS_DIR.glob("*.json"):
        cats.append(f.stem)
    return sorted(cats)


def _file_for_category(category: str) -> Path:
    slug = _slugify(category)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)
    return QUESTIONS_DIR / f"{slug}.json"


def load_questions(category: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Charge les questions.

    - Si category est donnée -> lit uniquement le fichier de cette catégorie.
    - Sinon -> fusionne tous les fichiers JSON.

    Chaque question reçoit un champ 'category' basé sur le fichier.
    """
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)

    # Mode : une seule catégorie
    if category:
        path = _file_for_category(category)
        if not path.exists():
            return []
        with path.open("r", encoding="utf-8") as f:
            data = json.load(f)
        if not isinstance(data, list):
            raise ValueError(f"{path} doit contenir une liste JSON ([])")
        for q in data:
            q.setdefault("category", path.stem)
        return data

    # Mode : toutes catégories
    all_questions: List[Dict[str, Any]] = []
    for f in QUESTIONS_DIR.glob("*.json"):
        try:
            with f.open("r", encoding="utf-8") as fh:
                data = json.load(fh)
        except json.JSONDecodeError:
            continue
        if not isinstance(data, list):
            continue
        for q in data:
            q.setdefault("category", f.stem)
            all_questions.append(q)
    return all_questions


def save_questions_for_category(category: str, questions: List[Dict[str, Any]]) -> None:
    """
    Écrase le fichier d'une catégorie avec la liste fournie.
    On ne stocke PAS la clé 'category' dans le fichier (elle vient du nom du fichier).
    """
    path = _file_for_category(category)
    QUESTIONS_DIR.mkdir(parents=True, exist_ok=True)

    cleaned: List[Dict[str, Any]] = []
    for q in questions:
        d = dict(q)
        d.pop("category", None)
        cleaned.append(d)

    with path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)


def add_question(
    category: str,
    q: str,
    choices: List[str],
    answer_index: int,
    difficulty: str = "facile",
) -> None:
    """
    Ajoute une question dans le fichier de la catégorie.
    """
    existing = load_questions(category)
    existing.append(
        {
            "q": q,
            "choices": choices,
            "a": answer_index,
            "difficulty": difficulty,
        }
    )
    save_questions_for_category(category, existing)
