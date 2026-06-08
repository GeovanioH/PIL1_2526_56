from app.models.user import User


def calculate_matching_score(user: User, other_user: User):
    """
    Calcule le score de compatibilité entre deux   users
    selon :
    - compétences / lacunes
    - disponibilités
    - filière
    - niveau
    """

    # COMPÉTENCES ↔ LACUNES
    user_lacunes = set(user.lacunes or [])
    other_user_competences = set(other_user.competences or [])

    matching_competences = user_lacunes.intersection(
        other_user_competences
    )

    competences_score = 0

    if len(user_lacunes) > 0:
        competences_score = (
            len(matching_competences)
            / len(user_lacunes)
        ) * 100

    # DISPONIBILITÉS
    user_disponibilites = set(user.disponibilites or [])
    other_user_disponibilites = set(
        other_user.disponibilites or []
    )

    common_disponibilites = (
        user_disponibilites.intersection(
            other_user_disponibilites
        )
    )

    horaires_score = 0

    if len(user_disponibilites) > 0:
        horaires_score = (
            len(common_disponibilites)
            / len(user_disponibilites)
        ) * 100

    # FILIÈRE
    filiere_score = 0

    if user.filiere == other_user.filiere:
        filiere_score = 100

    # NIVEAU
    niveau_score = 0

    niveaux = {
        "L1": 1,
        "L2": 2,
        "L3": 3,
        "M1": 4,
        "M2": 5
    }

    user_niveau = niveaux.get(user.niveau, 0)
    other_user_niveau = niveaux.get(
        other_user.niveau,
        0
    )

    difference = abs(
        user_niveau - other_user_niveau
    )

    if difference == 0:
        niveau_score = 100

    elif difference == 1:
        niveau_score = 75

    elif difference == 2:
        niveau_score = 50

    else:
        niveau_score = 25

    # SCORE FINAL
    final_score = (
        (competences_score * 0.40)
        + (horaires_score * 0.35)
        + (filiere_score * 0.15)
        + (niveau_score * 0.10)
    )

    return round(final_score, 2)