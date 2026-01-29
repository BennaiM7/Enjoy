DROP TABLE IF EXISTS restaurant CASCADE;
DROP TABLE IF EXISTS client CASCADE;
DROP TABLE IF EXISTS livreur CASCADE;
DROP TABLE IF EXISTS plat CASCADE;
DROP TABLE IF EXISTS carte CASCADE;
DROP TABLE IF EXISTS commande CASCADE;
DROP TABLE IF EXISTS jour CASCADE;
DROP TABLE IF EXISTS motsclefs CASCADE;
DROP TABLE IF EXISTS ville CASCADE;
DROP TABLE IF EXISTS cb CASCADE;
DROP TABLE IF EXISTS fermetureexep CASCADE;
DROP TABLE IF EXISTS compose CASCADE;
DROP TABLE IF EXISTS travaille CASCADE;
DROP TABLE IF EXISTS figure CASCADE;
DROP TABLE IF EXISTS ferme CASCADE;
DROP TABLE IF EXISTS ouvre CASCADE;
DROP TABLE IF EXISTS contient CASCADE;
DROP TABLE IF EXISTS motdepasse CASCADE;
DROP TABLE IF EXISTS compteclient CASCADE;
DROP TABLE IF EXISTS comptelivreur CASCADE;
DROP TABLE IF EXISTS compterestau CASCADE;
DROP TABLE IF EXISTS panier CASCADE;
/*
Requêtes de test : 

-> Afficher tous les restaurants avec leurs informations <- 

SELECT r.nom AS restaurant_nom, r.adresse, r.frais, r.codepostal, j.jour, o.heuredebut, o.heurefin
FROM restaurant r
JOIN ouvre o ON r.idresto = o.idresto
JOIN jour j ON o.jour = j.jour;

-> Afficher les mots-clés de chaque restaurant <-

SELECT r.nom AS restaurant_nom, m.motscles
FROM restaurant r
JOIN contient c ON r.idresto = c.idresto
JOIN motsclefs m ON c.motsclefs = m.motscles;

-> Afficher les livreurs et les villes dans lesquelles ils travaillent <-

SELECT l.nom AS livreur_nom, l.prenom, v.nom AS ville_nom
FROM livreur l
JOIN travaille t ON l.matricule = t.matricule
JOIN ville v ON t.codepostal = v.codepostal;

-> Afficher les commandes en attente de livraison <-

SELECT c.idcommande, c.montant, c.adresse, c.statutlivreur
FROM commande c
WHERE c.statutcommande = 1;

-> Afficher les clients aet les infos par rapport à leur parrain, et leur points de fidélités <-

SELECT c.nom AS client_nom, c.prenom, c.pointfidel, p.nom AS parrain_nom
FROM client c
LEFT JOIN client p ON c.idparrain = p.email;

-> Afficher les informations des cartes bancaires associées aux clients <-

SELECT cb.numcarte, cb.proprietaire, cb.datexp, cb.cvc, c.nom AS client_nom
FROM cb
JOIN client c ON cb.email = c.email;

-> Voir les informations des commandes qui ont étaient fait dans une ville exacte <-
SELECT idcommande, montant
FROM commande
WHERE codepostal = 75001;

-> Voir les jours et heures d'ouvertures des restaurants, on peut ajouter un where pour le nom d'un restaurant précis <-

SELECT r.nom AS restaurant_nom, o.jour, o.heuredebut, o.heurefin
FROM restaurant r
NATURAL JOIN ouvre o;

-> Test pour les fermetures exeptionnels <-

SELECT r.nom AS restaurant_nom, f.motif, fe.heuredebut, fe.heurefin, fe.dateEntier
FROM restaurant r
NATURAL JOIN ferme fe
NATURAL JOIN fermetureexep f;

-> Détails des commandes <-

SELECT c.idcommande, p.nom AS plat_nom, co.quantite
FROM commande c
JOIN compose co ON c.idcommande = co.idcommande
JOIN plat p ON co.idplat = p.idplat;

-> Voir quel client a fait quel commande <-

SELECT c.idcommande, client.nom AS nom, client.prenom AS prenom
FROM commande c
JOIN client ON c.codepostal = client.codepostal;

-> Informations des cartes bancaires des clients (on peut aussi ajouter un WHERE pour l'info d'un client précis si besoin) <-

SELECT c.nom AS nom, cb.numcarte, cb.datexp
FROM client c
JOIN cb ON c.email = cb.email;

*/


/* Vue : Faire statistiques des mot clés les plus commander dans l'application, genre 70% des gens commadnent pizza etc*/

/*
La vue : 

CREATE VIEW motscles_statistiques AS
(
SELECT motsclefs.motscles AS mot_cle,COUNT(compose.idcommande) AS nb_commande, (COUNT(compose.idcommande) * 100 / (SELECT COUNT(*) FROM commande)) AS stat_commande
FROM motsclefs
JOIN contient ON motsclefs.motscles = contient.motsclefs
JOIN restaurant ON contient.idresto = restaurant.idresto
JOIN figure ON restaurant.idcarte = figure.idcarte
JOIN plat ON figure.idplat = plat.idplat
JOIN compose ON plat.idplat = compose.idplat
GROUP BY motsclefs.motscles
ORDER BY stat_commande DESC
);

/* On peut diviser par 100.0 pour avoir le pourcentage exacte */

Pour la tester : SELECT * FROM motscles_statistiques
*/

CREATE TABLE carte(
    idcarte serial primary key
);

CREATE TABLE ville(
    codepostal int primary key,
    nom varchar(25) not null
);

CREATE TABLE plat(
    idplat serial primary key,
    nom varchar(25) not null,
    prix float not null,
    descr text,
    photo bytea
);

CREATE TABLE motsclefs(
    motscles varchar(25) primary key
);

CREATE TABLE restaurant(
    idresto serial primary key,
    nom varchar(25) not null,
    adresse varchar(100) not null,
    frais int not null,
    note int CHECK (note BETWEEN 0 AND 5), /* 0 pour pas de note, et après note de 1 à 5*/
    idcarte int references carte(idcarte),
    codepostal int references ville(codepostal)
);

CREATE TABLE client(
    email varchar(50) primary key,
    nom varchar(25) not null,
    prenom varchar(25) not null,
    numtel int not null,
    pointfidel int,
    idparrain varchar(50) references client(email),
    codepostal int references ville(codepostal)
);

CREATE TABLE livreur(
    matricule serial primary key,
    nom varchar(25) not null,
    prenom varchar(25) not null,
    numPro int not null,
    statutlivreur int CHECK (statutlivreur BETWEEN 0 AND 4), /* 0 pour indispo, 1 pour en service, 2 en attente de commande, 3 en livraison, 4 commande livré*/
    codepostal int references ville(codepostal)
);


CREATE TABLE commande(
    idcommande serial primary key,
    montant float not null,
    adresse varchar(100) not null,
    statutcommande int CHECK (statutcommande BETWEEN 0 AND 3), /* 0 pour indispo, 1 pour en attente, 2 en livraison, 3 livré*/
    note int CHECK (note BETWEEN 0 AND 5), /* 0 pour pas de note, et après note de 1 à 5*/
    codepostal int references ville(codepostal),
    email varchar(50) references client(email),
    matricule serial references livreur(matricule), /* pour savoir quel livreur a livré quel commande et avoir l'historique */
    idresto serial references restaurant(idresto)
);

CREATE TABLE jour(
    jour varchar(10) primary key
);


CREATE TABLE cb(
    numcarte bigint primary key,
    proprietaire varchar(25) not null,
    codesecret int not null,
    datexp date not null,
    cvc int not null,
    email varchar(50) references client(email)
);

CREATE TABLE fermetureexep(
    idferm int primary key,
    motif text 
);

CREATE TABLE compose(
    idplat int references plat(idplat),
    idcommande int references commande(idcommande),
    quantite int not null /* au moins 1 plat dans ce qu'on a choisi */
);

CREATE TABLE travaille(
    matricule int references livreur(matricule),
    codepostal int references ville(codepostal),
    primary key(matricule, codepostal)
);

CREATE TABLE figure(
    idcarte int references carte(idcarte),
    idplat int references plat(idplat),
    primary key(idcarte, idplat)
);

CREATE TABLE ferme(
    idferm int references fermetureexep(idferm),
    idresto int references restaurant(idresto),
    heuredebut time, /* pas obligatoire de mettre une heure pour la fermeture*/ 
    heurefin time,
    dateEntier date not null, /* par contre obligé de mettre une date*/
    primary key(idferm, idresto)
);

CREATE TABLE ouvre(
    jour varchar(15) references jour(jour),
    idresto int references restaurant(idresto),
    heuredebut time not null, /* On doit avoir les heures d'ouvertures*/
    heurefin time not null,
    primary key(jour, idresto)
);

CREATE TABLE contient(
    motsclefs varchar(25) references motsclefs(motscles),
    idresto int references restaurant(idresto),
    primary key(motsclefs, idresto)
);

CREATE TABLE panier(
    email varchar(50) references client(email),
    idplat int references plat(idplat),
    quantite int,
    primary key(email, idplat)
);

CREATE TABLE compteclient(
    email varchar(50) references client(email),
    motdepasse varchar(75) not null,
    primary key(email, motdepasse)
);

CREATE TABLE comptelivreur(
    matricule serial references livreur(matricule),
    motdepasse varchar(75) not null,
    primary key(matricule, motdepasse)
);

CREATE TABLE compterestau(
    idresto serial references restaurant(idresto),
    motdepasse varchar(75) not null,
    primary key(idresto, motdepasse)
);

INSERT INTO carte (idcarte) VALUES
(101),
(102),
(103);


INSERT INTO ville (codepostal, nom) VALUES
(75001, 'Paris 1'),
(75002, 'Paris 2'),
(75003, 'Paris 3');

INSERT INTO restaurant (idresto, nom, adresse, frais, idcarte, codepostal) VALUES
(1, 'Chez Marie', '10 Rue de la Paix', 5, 101, 75001),
(2, 'Le Gourmet', '15 Avenue de la République', 3, 102, 75002),
(3, 'La Bella Italia', '22 Rue du Paradis', 4, 103, 75003);

INSERT INTO client (email, nom, prenom, numtel, pointfidel, idparrain, codepostal) VALUES
('alice@exemple.fr', 'Alice', 'Dupont', 0612345678, 10, NULL, 75001),
('bob@exemple.fr', 'Bob', 'Martin', 0756781234, 5, 'alice@exemple.fr', 75002),
('test@example.fr', 'Charlie', 'Durand', 0145678901, 8, 'alice@exemple.fr', 75003);

INSERT INTO livreur (matricule, nom, prenom, numpro, codepostal) VALUES
(1, 'Smith', 'John', 0689012345, 75001),
(2, 'Doe', 'Jane', 0789123456, 75002),
(3, 'Brown', 'Emily', 0323456789, 75003);

INSERT INTO plat (idplat, nom, prix, descr, photo) VALUES
(1, 'Pates à la crème fraiche', 12.5, 'Pâtes fraiches fait maison, à la crème fraiche', NULL),
(2, 'Pizza', 15.0, 'Pizza faite maison au four à pizza', NULL),
(3, 'Salade', 8.0, 'Salade fraiche fait maison avec des produits locaux', NULL),
(4, 'Burger', 10.0, 'Burger fait maison avec des produits locaux', NULL),
(5, 'Sushi', 20.0, 'Sushi fait maison avec des produits locaux', NULL),
(6, 'Poulet rôti', 18.0, 'Poulet rôti fait maison avec des produits locaux', NULL),
(7, 'Dessert', 5.0, 'Dessert fait maison avec des produits locaux', NULL),
(8, 'Boisson', 2.0, 'Boisson fraiche fait maison avec des produits locaux', NULL);



INSERT INTO commande (idcommande, montant, adresse, statutcommande, note, codepostal, email, matricule, idresto) VALUES
(1, 30.5, '5 Avenue de France', 2, 0,75001, 'test@example.fr', 1, 1),
(2, 25.0, '10 Rue Albert Camus', 2, 0,75002, 'test@example.fr', 1, 2),
(3, 50.0, '18 Boulevard Haussmann', 1, 0, 75003, 'test@example.fr', 3, 3),
(4, 12.99, '5 rue de lespagne', 1, 0, 75001, 'test@example.fr', 1, 2),
(5, 15.49, '10 Rue Jean Camus', 1, 0, 75002, 'test@example.fr', 1, 3),
(6, 4.99, '18 Boulevard Test', 1, 0, 75003, 'test@example.fr', 3, 1);

INSERT INTO jour (jour) VALUES
('lundi'),
('mardi'),
('mercredi'),
('jeudi'),
('vendredi');

INSERT INTO motsclefs (motscles) VALUES
('pizza'),
('poulet'),
('vegan'),
('sushi'),
('burger'),
('dessert'),
('boisson'),
('salade'),
('pâtes'),
('sandwich'),
('bio'),
('fast-food');

INSERT INTO cb (numcarte, proprietaire, codesecret, datexp, cvc, email) VALUES
(1234567890123456, 'Alice Dupont', 1234, '2025-12-31', 123, 'alice@exemple.fr'),
(2345678901234567, 'Bob Martin', 5678, '2026-06-30', 456, 'bob@exemple.fr'),
(3456789012345678, 'Charlie Durand', 9012, '2027-03-31', 789, 'test@example.fr');

INSERT INTO fermetureexep (idferm, motif) VALUES
(1, 'Vacances'),
(2, 'Problème matériel'),
(3, 'Férié');

INSERT INTO compose (idplat, idcommande, quantite) VALUES
(2, 1, 2), --pour pouvoir tester le supprimer plat de profile resto, avec les autres y'aura des soucis
(2, 2, 1), 
(3, 3, 3),
(1, 4, 2),
(2, 5, 1),
(3, 6, 3);

INSERT INTO travaille (matricule, codepostal) VALUES
(1, 75001),
(2, 75002),
(3, 75003);

INSERT INTO figure (idcarte, idplat) VALUES
(101, 1),
(102, 2),
(103, 3),
(101, 4),
(102, 5),
(103, 6),
(101, 7),
(102, 8);

INSERT INTO ferme (idferm, idresto, heuredebut, heurefin, dateEntier) VALUES
(1, 1, '08:00', '20:00', '2024-12-25'),
(2, 2, '10:00', '18:00', '2024-01-01'),
(3, 3, '09:00', '19:00', '2024-07-14');

INSERT INTO ouvre (jour, idresto, heuredebut, heurefin) VALUES
('lundi', 1, '08:00', '22:00'),
('mardi', 2, '09:00', '21:00'),
('mercredi', 3, '10:00', '20:00');

INSERT INTO contient (motsclefs, idresto) VALUES
('pizza', 1),
('pizza', 2),
('poulet', 2),
('fast-food', 3);


INSERT into compteclient(email, motdepasse) VALUES
('test@example.fr','$2b$12$Pjj3iAgTduFymI/MfvJ.Ke.8rb83dgIPboyfsY0Bty/nl23r/qXV.'); -- mot de passe : test --

INSERT into comptelivreur(matricule, motdepasse) VALUES
(1,'$2b$12$Pjj3iAgTduFymI/MfvJ.Ke.8rb83dgIPboyfsY0Bty/nl23r/qXV.'); -- mot de passe : test --

INSERT into compterestau(idresto, motdepasse) VALUES
(1,'$2b$12$Pjj3iAgTduFymI/MfvJ.Ke.8rb83dgIPboyfsY0Bty/nl23r/qXV.'); -- mot de passe : test --

CREATE VIEW motscles_statistiques AS
SELECT motsclefs.motscles AS mot_cle,COUNT(compose.idcommande) AS nb_commande, (COUNT(compose.idcommande) * 100 / (SELECT COUNT(*) FROM commande)) AS stat_commande
FROM motsclefs
JOIN contient ON motsclefs.motscles = contient.motsclefs
JOIN restaurant ON contient.idresto = restaurant.idresto
JOIN figure ON restaurant.idcarte = figure.idcarte
JOIN plat ON figure.idplat = plat.idplat
JOIN compose ON plat.idplat = compose.idplat
GROUP BY motsclefs.motscles
ORDER BY stat_commande DESC;
