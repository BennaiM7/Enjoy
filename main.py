from flask import Flask, render_template, request, redirect, url_for, session
from db import connect
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = Flask(__name__)
app.secret_key = 'clesecrete' #il est en brut ici mais normalement il ne l'est pas



@app.route("/")
def home():
    return render_template('accueil.html')

@app.route("/inscription", methods=["GET","POST"])
def signup():
    if request.method == 'POST':
        inforempli = {"nom": request.form.get('nom'), "prenom": request.form.get('prenom'), "datedenaissance": request.form.get('datedenaissance'), "email": request.form.get('email'),
            "numtel": request.form.get('numtel'), "adresse": request.form.get('adresse'), "codepostal": request.form.get('codepostal'), "ville": request.form.get('ville'), "parrain": request.form.get('parrain'), "genre": request.form.get('genre'),
            "mdp": request.form.get('mdp'), "mdp_repeat": request.form.get('mdp_repeat')
        }
        if inforempli["mdp"] != inforempli["mdp_repeat"]:
            return render_template('inscription.html', erreur = "Mot de passe différent")
        motdepasse_hache = pwd_context.hash(inforempli["mdp"])
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT email FROM compteclient WHERE email=%s", (inforempli["email"],))
            mail_deja_existant = cur.fetchone()
            if mail_deja_existant:
                return render_template('inscription.html', erreur = "E-mail déjà existant")
            cur.execute("SELECT codepostal FROM ville WHERE codepostal = %s", (inforempli["codepostal"],))
            ville_existe = cur.fetchone() #ici on crée les villes que s'il n'est pas déjà présent
            if not ville_existe:
                cur.execute("INSERT INTO ville (codepostal, nom) VALUES (%s, %s)", (inforempli["codepostal"], inforempli["ville"]))
            cur.execute("INSERT INTO client (email, nom, prenom, numtel, codepostal, pointfidel) VALUES (%s, %s, %s, %s, %s, 0)", (
                inforempli["email"],
                inforempli["nom"],
                inforempli["prenom"],
                inforempli["numtel"],
                inforempli["codepostal"]
            ))
            cur.execute("INSERT INTO compteclient (email, motdepasse) VALUES (%s, %s)", (
                inforempli["email"],
                motdepasse_hache
            ))
        conn.commit()
        session['user_id'] = inforempli["email"]
        return redirect(url_for('home_connecte'), code=307) #on redirige vers la page d'accueil connecté quand il est inscrit
    return render_template('inscription.html')

@app.route("/inscriptionrestaurant", methods=["GET","POST"])
def signuprestaurant():
    if request.method == 'POST':
        inforempli = {"idresto" : request.form.get('idresto'), "nom": request.form.get('nom'), "frais": request.form.get('frais'),
            "adresse": request.form.get('adresse'), "codepostal": request.form.get('codepostal'), "ville": request.form.get('ville'),
            "mdp": request.form.get('mdp'), "mdp_repeat": request.form.get('mdp_repeat')
        }
        if inforempli["mdp"] != inforempli["mdp_repeat"]: #si le mot de passe qui est répété est != du mot de passe entré en premier, on retourne à la page d'inscription de base
            return redirect(url_for('inscriptionrestaurant'))
        motdepasse_hache = pwd_context.hash(inforempli["mdp"]) #on hache le mdp pour le mettre après dans la bdd
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT codepostal FROM ville WHERE codepostal = %s", (inforempli["codepostal"],))
            ville_existe = cur.fetchone() #ici on crée les villes qui si il n'est pas déjà présent
            if not ville_existe:
                cur.execute(
                    "INSERT INTO ville (codepostal, nom) VALUES (%s, %s)", 
                    (inforempli["codepostal"], inforempli["ville"])
                )

            cur.execute("INSERT INTO restaurant (idresto, nom, frais, adresse, codepostal) VALUES (%s, %s, %s, %s, %s)", (
                inforempli["idresto"],
                inforempli["nom"],
                inforempli["frais"],
                inforempli["adresse"],
                inforempli["codepostal"]
            ))
            cur.execute("INSERT INTO compterestau (idresto, motdepasse) VALUES (%s, %s)", (
                inforempli["idresto"],
                motdepasse_hache
            ))
        conn.commit()
        session['restau_id'] = inforempli["idresto"]
        return redirect(url_for('home_connecte_restaurant'), code=307) #on redirige vers la page d'accueil connecté quand il est inscrit
    return render_template('inscriptionrestaurant.html')

@app.route("/inscriptionlivreur", methods=["GET","POST"])
def signupdeliver():
    if request.method == 'POST':
        inforempli = {"matricule" : request.form.get('matricule'), "nom": request.form.get('nom'), "prenom": request.form.get('prenom'),
            "numpro": request.form.get('numpro'), "codepostal": request.form.get('codepostal'), "ville": request.form.get('ville'),
            "mdp": request.form.get('mdp'), "mdp_repeat": request.form.get('mdp_repeat')
        }
        if inforempli["mdp"] != inforempli["mdp_repeat"]: #si le mot de passe qui est répété est != du mot de passe entré en premier, on retourne à la page d'inscription de base
            return redirect(url_for('inscriptionlivreur'))
        motdepasse_hache = pwd_context.hash(inforempli["mdp"]) #on hache le mdp pour le mettre après dans la bdd
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT codepostal FROM ville WHERE codepostal = %s", (inforempli["codepostal"],))
            ville_existe = cur.fetchone() #ici on crée les villes qui si il n'est pas déjà présent
            if not ville_existe:
                cur.execute(
                    "INSERT INTO ville (codepostal, nom) VALUES (%s, %s)", 
                    (inforempli["codepostal"], inforempli["ville"])
                )

            cur.execute("INSERT INTO livreur (matricule, nom, prenom, numpro, codepostal) VALUES (%s, %s, %s, %s, %s)", (
                inforempli["matricule"],
                inforempli["nom"],
                inforempli["prenom"],
                inforempli["numpro"],
                inforempli["codepostal"]
            ))
            cur.execute("INSERT INTO comptelivreur (matricule, motdepasse) VALUES (%s, %s)", (
                inforempli["matricule"],
                motdepasse_hache
            ))
        conn.commit()
        session['livreur_id'] = inforempli["matricule"]
        return redirect(url_for('home_connecte_deliver'), code=307) #on redirige vers la page d'accueil connecté quand il est inscrit
    return render_template('inscriptionlivreur.html')

@app.route("/connexion", methods=["GET","POST"])
def login():
    if request.method == 'POST':
        inforempli = {
            "email": request.form.get('email'),
            "mdp": request.form.get('mdp'),
        }
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT motdepasse FROM compteclient WHERE email = %s", (inforempli["email"],))
            res = cur.fetchone()
            if res:
                if pwd_context.verify(inforempli["mdp"], res[0]):
                    session['user_id'] = inforempli["email"]
                    return redirect(url_for('home_connecte'), code=307)
            else:
                return render_template('connexion.html', erreur = "Mot de passe ou e-mail incorrect")
    return render_template('connexion.html')

@app.route("/connexionrestaurant", methods=["GET","POST"])
def login_restaurant():
    if request.method == 'POST':
        inforempli = {
            "idresto": request.form.get('idresto'),
            "mdp": request.form.get('mdp'),
        }
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT motdepasse FROM compterestau WHERE idresto = %s", (inforempli["idresto"],))
            res = cur.fetchone()
            if res:
                if pwd_context.verify(inforempli["mdp"], res[0]):
                    session['resto_id'] = inforempli["idresto"]
                    return redirect(url_for('home_connecte_restaurant'), code=307)
            else:
                return render_template('connexionrestaurant.html', erreur = "Mot de passe ou e-mail incorrect")
    return render_template('connexionrestaurant.html')

@app.route("/connexionlivreur", methods=["GET","POST"])
def logindeliver():
    if request.method == 'POST':
        inforempli = {"matricule": request.form.get('matricule'), "mdp": request.form.get('mdp')}
        conn = connect()
        with conn.cursor() as cur:
            cur.execute("SELECT motdepasse FROM comptelivreur WHERE matricule = %s", (inforempli["matricule"],))
            res = cur.fetchone()
            if res:
                if pwd_context.verify(inforempli["mdp"], res[0]):
                    session['livreur_id'] = inforempli["matricule"]
                    return redirect(url_for('home_connecte_deliver'), code=307)
            else:
                return render_template('connexionlivreur.html', erreur = "Mot de passe ou e-mail incorrect")
    return render_template('connexionlivreur.html')

@app.route("/accueil_connecte", methods = ["POST", "GET"])
def home_connecte():
    if request.method == 'POST':
        return render_template('accueil_connecte.html')
    return redirect(url_for('home'))

@app.route("/accueil_connecte_livreur", methods = ["POST", "GET"])
def home_connecte_deliver():
    if request.method == 'POST':
        return render_template('accueil_connecte_livreur.html')
    return redirect(url_for('home'))

@app.route("/accueil_connecte_restaurant", methods = ["POST", "GET"])
def home_connecte_restaurant():
    if request.method == 'POST':
        return render_template('accueil_connecte_restaurant.html')
    return redirect(url_for('home'))


@app.route("/profile", methods=["POST", "GET"])
def profil():
    if 'user_id' not in session:
        print("Session vide ou expirée.")
        return redirect(url_for('login'))
    email = session['user_id']
    conn = connect()
    if request.method == "POST":
        idcommande = request.form.get("idcommande")
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "annuler":
                cur.execute("DELETE FROM compose WHERE idcommande = %s", (idcommande,))
                cur.execute("DELETE FROM commande WHERE idcommande = %s", (idcommande,))
            conn.commit()
            if action == "noter":
                note = request.form.get("noter")
                cur.execute("SELECT idresto FROM commande WHERE idcommande = %s", (idcommande,))
                idresto = cur.fetchone() #on prend l'id du resto pour pouvoir ajouter la note au restau en question
                cur.execute("UPDATE commande SET note = %s WHERE idcommande = %s", (note, idcommande))
                cur.execute("UPDATE restaurant SET note = %s WHERE idresto = %s", (note, idresto))
                cur.execute("UPDATE client SET pointfidel = pointfidel + 5 WHERE email = %s", (email,)) #on ajoute les points de fidélités quand le client note la commande
    with conn.cursor() as cur:
        cur.execute("SELECT idcommande, montant, statutcommande, note FROM commande WHERE email = %s", (email,))
        commandes = cur.fetchall()
        cur.execute("SELECT pointfidel FROM client WHERE email = %s", (email,))
        points = cur.fetchone()
        points = points[0] #pour ne pas avoir le record
    return render_template('profile.html', commandes=commandes, points=points,)

@app.route("/profilelivreur", methods=["POST", "GET"])
def profildeliver():
    if 'livreur_id' not in session:
        print("Session vide ou expirée.")
        return redirect(url_for('logindeliver'))
    matricule = session['livreur_id']
    conn = connect()
    if request.method == "POST":
        idcommande = request.form.get("idcommande")
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "prendrecommande": #quand un livreur prend une commande on met que le statut de la commande et du livreur est à en livraison (donc 2 et 3)
                cur.execute("UPDATE livreur SET statutlivreur = 3 WHERE matricule = %s", (matricule,))
                cur.execute("UPDATE commande SET statutcommande = 2 WHERE idcommande = %s", (idcommande,))
            if action == "validerlivraison": 
                cur.execute("UPDATE livreur SET statutlivreur = 4 WHERE matricule = %s", (matricule,)) #quand le livreur a livré la commande on met que la commande est finie
                cur.execute("UPDATE commande SET statutcommande = 3 WHERE idcommande = %s", (idcommande,))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT idcommande, statutcommande FROM commande NATURAL JOIN livreur WHERE matricule = %s and commande.codepostal = livreur.codepostal", (matricule,))
        commandes = cur.fetchall()
        cur.execute("SELECT statutlivreur FROM livreur WHERE matricule = %s", (matricule,))
        livreur = cur.fetchone()
    return render_template('profilelivreur.html', commandes=commandes, livreur=livreur)

@app.route("/profilerestaurant", methods=["POST", "GET"])
def profilrestaurant():
    if 'resto_id' not in session:
        return redirect(url_for('login_restaurant'))
    idresto = session['resto_id']
    conn = connect()
    if request.method == "POST":
        idplat = request.form.get("idplat")
        nom = request.form.get("nom")
        prix = request.form.get("prix")
        descr = request.form.get("descr")
        action = request.form.get("action")
        with conn.cursor() as cur:
            if action == "ajouterplat":
                cur.execute("SELECT idcarte FROM restaurant WHERE idresto = %s", (idresto,))
                idcarte = cur.fetchone()
                cur.execute("INSERT INTO plat VALUES(%s, %s, %s, %s)", (idplat, nom, prix, descr))
                cur.execute("INSERT INTO figure VALUES(%s, %s)", (idcarte, idplat))
            if action == "supprimerplat":  
                cur.execute("DELETE FROM figure WHERE idplat = %s", (idplat,))
            conn.commit()
    with conn.cursor() as cur:
        cur.execute("SELECT idcarte FROM restaurant WHERE idresto = %s", (idresto,))
        idcarte = cur.fetchone()
        cur.execute("SELECT idplat FROM figure WHERE idcarte = %s", (idcarte,))
        idplat = cur.fetchall()
        plats = []
        for elem in idplat:
            cur.execute("SELECT idplat, nom, prix, descr FROM plat WHERE idplat = %s", (elem,))
            plats += cur.fetchall()
    return render_template('profilerestaurant.html', idcarte=idcarte, plats=plats, idplat=idplat)

@app.route("/recherche", methods=["POST", "GET"])
def research():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    conn = connect()
    if request.method == 'POST':
        motclef = request.form.get('mot-cle')
        with conn.cursor() as cur:
            cur.execute("SELECT DISTINCT motsclefs FROM contient")
            motsclefs = [res1[0] for res1 in cur.fetchall()]
            cur.execute("SELECT idresto, nom, adresse, codepostal FROM restaurant NATURAL JOIN contient WHERE motsclefs LIKE %s", (motclef,))
            res = cur.fetchall()
            if res:
                return render_template('recherche.html', lst_resto=res, taille=len(res), motsclefs=motsclefs)
            else:
                return render_template('recherche.html', lst_resto=[], taille=0, motsclefs=motsclefs, message="Aucun résultat ne correspond")
    return render_template('recherche.html', motsclefs=motsclefs)

@app.route("/restaurant/<string:nom>_<int:idresto>", methods=["POST", "GET"])
def resto(nom, idresto):
    if 'user_id' not in session:
        return redirect(url_for('home'))
    if request.method == 'POST' or 'user_id' in session:
        conn = connect()
        with conn.cursor() as cur:
            if request.method == 'POST':
                idplat = request.form.get('idplat')
                quantite = request.form.get('quantite')
                if quantite != '':
                    cur.execute("INSERT INTO panier VALUES(%s, %s, %s)", (session['user_id'], idplat, quantite))
                conn.commit()
            cur.execute("SELECT r.nom, r.adresse, r.frais, r.codepostal, v.nom as nomV FROM restaurant as r join ville as v on v.codepostal = r.codepostal WHERE idresto = %s", (idresto,))
            lstville = cur.fetchone()
            cur.execute("SELECT f.idcarte, p.idplat, p.nom, p.prix, p.descr, p.photo FROM figure as f NATURAL JOIN plat as p JOIN restaurant as r on f.idcarte = r.idcarte WHERE r.idresto = %s", (idresto,))
            lstcarte = cur.fetchall()
            cur.execute("SELECT o.jour, o.heuredebut, o.heurefin, f.dateEntier, fm.motif FROM ouvre as o join ferme as f on o.idresto = f.idresto join fermetureexep as fm on fm.idferm = f.idferm WHERE f.idresto = %s", (idresto,))
            lsthoraire = cur.fetchall()
            return render_template("resto.html", lst1=lstville, lst2=lstcarte, lst3=lsthoraire)
    return redirect(url_for('home_connecte'))

@app.route("/panier", methods=["POST", "GET"])
def panier():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    conn = connect()
    with conn.cursor() as cur:
        if request.method == 'POST' and request.form.get('action') == 'commander':
            adresse = request.form.get("adresse")
            codepostal = request.form.get("codepostal")
            #numcarte = request.form.get("numcard")
            #date = request.form.get("datecard")
            #nom = request.form.get("namecard")
            #cvc = request.form.get("cryptocard")
            cur.execute("SELECT plat.nom, plat.prix, quantite, (plat.prix*quantite) AS prixtotal FROM panier NATURAL JOIN plat WHERE email = %s", (session['user_id'], ))
            elempanier = cur.fetchall()
            total = 0
            for elem in elempanier:
                total += elem[3]
            #probleme d'insertion des données dans commande et de la suppression du panier
            cur.execute("INSERT INTO commande VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (total, adresse, 1, 0, codepostal, session['user_id'], -1, -1))
            conn.commit()
            cur.execute("DELETE from panier where email = %s", (session['user_id'],))
            conn.commit()
            return redirect(url_for('commande_valide'))
        cur.execute("SELECT plat.nom, plat.prix, quantite, (plat.prix*quantite) AS prixtotal FROM panier NATURAL JOIN plat WHERE email = %s", (session['user_id'], ))
        elempanier = cur.fetchall()
        total = 0
        for elem in elempanier:
            total += elem[3]
        return render_template("panier.html", elempanier=elempanier, total=total)


@app.route("/validation_commande", methods = ["POST", "GET"])
def commande_valide():
    if 'user_id' not in session:
        return redirect(url_for('home'))
    return render_template("commande_valide.html")


@app.route("/deconnexion", methods = ["POST", "GET"])
def deconnect():
    session['user_id'] = None
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)

