SELECT
    u.id AS mentor_id,
    u.nom,
    u.prenom,
    u.filiere,
    COUNT(c.matiere) AS matieres_en_commun
FROM utilisateurs u
JOIN competences c ON c.utilisateur_id = u.id
WHERE c.type = 'force'
AND c.matiere IN (
    SELECT matiere FROM competences
    WHERE utilisateur_id = :id_mentore
    AND type = 'lacune'
)
AND u.id != :id_mentore
GROUP BY u.id, u.nom, u.prenom, u.filiere
ORDER BY matieres_en_commun DESC;

SELECT
    u.id,
    u.nom,
    u.prenom,
    d1.jour,
    d1.heure_debut,
    d1.heure_fin
FROM utilisateurs u
JOIN disponibilites d1 ON d1.utilisateur_id = u.id
WHERE EXISTS (
    SELECT 1 FROM disponibilites d2
    WHERE d2.utilisateur_id = :id_mentore
    AND d2.jour = d1.jour
    AND d2.heure_debut < d1.heure_fin
    AND d2.heure_fin > d1.heure_debut
)
AND u.id != :id_mentore;