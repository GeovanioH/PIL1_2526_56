-- Objectif : Trouver des mentors (force) pour des mentorés (lacune) sur les mêmes matières
SELECT 
    mentor.utilisateurs_id AS mentor_id,
    mentore.utilisateurs_id AS mentore_id,
    COUNT(mentor.nom_matiere) AS nb_correspondances,
    STRING_AGG(mentor.nom_matiere, ', ') AS matieres_communes
FROM 
    competences AS mentor
JOIN 
    competences AS mentore ON mentor.nom_matiere = mentore.nom_matiere
WHERE 
    mentor.type = 'force'             -- Le mentor maîtrise la matière [1]
    AND mentore.type = 'lacune'       -- Le mentoré a besoin d'aide [1]
    AND mentor.utilisateurs_id != mentore.utilisateurs_id -- Éviter l'auto-matching
GROUP BY 
    mentor.utilisateurs_id, mentore.utilisateurs_id
ORDER BY 
    nb_correspondances DESC;          -- Trié par pertinence

