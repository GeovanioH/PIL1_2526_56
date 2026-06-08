from app.models.user import User


def calculate_matching_score(user: User, other_user: User) -> float:
    """
    Calcule le score de compatibilité entre deux utilisateurs selon :
      - Compétences de l'autre vs lacunes de l'utilisateur (40%)
      - Disponibilités communes (35%)
      - Proximité de filière (15%)
      - Proximité de niveau (10%)
    Retourne un score entre 0 et 100.
    """

    # ── COMPÉTENCES ↔ LACUNES ────────────────────────────────────────
    user_lacunes = set(user.lacunes or [])
    other_competences = set(other_user.competences or [])
    matching_competences = user_lacunes.intersection(other_competences)

    competences_score = 0.0
    if len(user_lacunes) > 0:
        competences_score = (len(matching_competences) / len(user_lacunes)) * 100

    # ── DISPONIBILITÉS ───────────────────────────────────────────────
    user_dispos = set(user.disponibilites or [])
    other_dispos = set(other_user.disponibilites or [])
    common_dispos = user_dispos.intersection(other_dispos)

    horaires_score = 0.0
    if len(user_dispos) > 0:
        horaires_score = (len(common_dispos) / len(user_dispos)) * 100

    # ── FILIÈRE ──────────────────────────────────────────────────────
    filiere_score = 100.0 if user.filiere == other_user.filiere else 0.0

    # ── NIVEAU ───────────────────────────────────────────────────────
    niveaux = {"L1": 1, "L2": 2, "L3": 3, "M1": 4, "M2": 5}
    user_niveau_val = niveaux.get(user.niveau, 0)
    other_niveau_val = niveaux.get(other_user.niveau, 0)
    difference = abs(user_niveau_val - other_niveau_val)

    if difference == 0:
        niveau_score = 100.0
    elif difference == 1:
        niveau_score = 75.0
    elif difference == 2:
        niveau_score = 50.0
    else:
        niveau_score = 25.0

    # ── SCORE FINAL PONDÉRÉ ──────────────────────────────────────────
    final_score = (
        (competences_score * 0.40)
        + (horaires_score * 0.35)
        + (filiere_score * 0.15)
        + (niveau_score * 0.10)
    )

    return round(final_score, 2)


def get_matching_details(user: User, other_user: User) -> dict:
    """
    Retourne les détails de compatibilité entre deux utilisateurs
    pour l'affichage côté frontend (CDC : matières communes, dispo communes).
    """
    user_lacunes = set(user.lacunes or [])
    other_competences = set(other_user.competences or [])
    matieres_communes = list(user_lacunes.intersection(other_competences))

    user_dispos = set(user.disponibilites or [])
    other_dispos = set(other_user.disponibilites or [])
    dispos_communes = list(user_dispos.intersection(other_dispos))

    return {
        "matieres_communes": matieres_communes,
        "disponibilites_communes": dispos_communes,
    }
