from flask import Flask, render_template, request, url_for, flash, redirect, session
import pyodbc
import datetime
import re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SECRET_KEY'] = 'clés_flash'
DSN = 'Driver={SQL Server};Server=y_muhamad\\SQLEXPRESS;Database=zorodb;'


@app.route("/", methods=["GET", "POST"])
def accueil():
    if 'loggedin' in session:
        return render_template("/connexion/accueil.html", username=session['username'], title="accueil")
    return redirect(url_for('connexion'))


@app.route("/inscription", methods=["GET", "POST"])
def inscription():
    if request.method == 'POST':
        user = request.form["nomuser"]
        email = request.form["mail"]
        password = request.form["password"]
        hashed_password = generate_password_hash(password)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE NomUser = ? OR Email = ?', (user, email))
        users = cursor.fetchall()
        if users:
            flash("ce compte existe déjà !", 'info')
        elif not re.match(r'[a-zA-Z0-9]+$', user):
            flash("Le nom d'utilisateur ne doit contenir que des lettres et des chiffres !", 'info')
            return redirect(url_for('inscription'))
        elif not re.match(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash("Email Invalid !", 'info')
            return redirect(url_for('inscription'))
        else:
            conn = pyodbc.connect(DSN)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Users (NomUser, Email, Password)
                VALUES ( ?, ?, ?)
             ''', (user, email, hashed_password))
            conn.commit()
            conn.close()
            flash("Votre compte a été enregistré avec succès !", 'info')
            return redirect(url_for('connexion'))
    return render_template("/connexion/inscription.html")


@app.route("/connexion", methods=["GET", "POST"])
def connexion():
    if request.method == 'POST':
        user = request.form["identifiant"]
        password = request.form["password"]
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Users WHERE NomUser = ? OR Email = ?', (user, user))
        users = cursor.fetchone()
        if users:
            user_pswd = users[3]
            if check_password_hash(user_pswd, password):
                session['loggedin'] = True
                session['Id'] = users[0]
                session['username'] = users[1]
                return redirect(url_for('accueil'))
            else:
                flash("Mot de passe incorrect !", 'info')
                return redirect(url_for('connexion'))
        else:
            flash("Identifiant incorrect !", 'info')
            return redirect(url_for('connexion'))
    return render_template("/connexion/connexion.html")


@app.route("/afficherproduit")
def afficherproduit():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produit")
        data = cursor.fetchall()
        conn.close()
        return render_template("/produit/afficher_produit.html", data=data, title="Produits")
    return redirect(url_for('connexion'))


@app.route("/ajouterproduit", methods=["GET", "POST"])
def ajouterproduit():
    if 'loggedin' in session:
        if request.method == 'POST':
            nom = request.form["nom"]
            categorie = request.form["categorie"]
            prixunitaire = request.form["prixunitaire"]
            conn = pyodbc.connect(DSN)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO Produit (NomProduit, CatProduit, PrixUnitaire)
                VALUES ( ?, ?, ?)
             ''', (nom, categorie, prixunitaire))
            conn.commit()
            conn.close()
            flash("Votre produit a été enregistré avec succès !", 'info')
            return redirect(url_for('afficherproduit'))
        data = ''
        return render_template("/produit/ajouter_produit.html", data=data, title="Produits")
    return redirect(url_for('connexion'))


@app.route("/confirmsupproduit/<int:item_id>", methods=['GET', 'POST'])
def confirmsupproduit(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Produit WHERE IdProduit = ?', item_id)
        data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("/produit/confirm_sup_produit.html", data=data, title="Produits")
    return redirect(url_for('connexion'))


@app.route('/supprimerproduit/<int:item_id>', methods=['GET', 'POST'])
def supprimerproduit(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Produit WHERE IdProduit = ?', item_id)
        conn.commit()
        conn.close()
        flash(f'Le produit numéro {item_id} a été supprimé avec succès !', 'info')
        return redirect(url_for('afficherproduit'))
    return redirect(url_for('connexion'))


@app.route('/modifierproduit/<int:item_id>', methods=['GET', 'POST'])
def modifierproduit(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM produit WHERE IdProduit = ?', item_id)
        data = cursor.fetchone()
        if request.method == 'POST':
            nom = request.form['nom']
            categorie = request.form['categorie']
            prixunitaire = request.form['prixunitaire']
            cursor.execute('''
                UPDATE produit
                SET NomProduit = ?, CatProduit = ?, PrixUnitaire = ?
                WHERE IdProduit = ?
            ''', (nom, categorie, prixunitaire, item_id))
            conn.commit()
            conn.close()
            flash(f'Le produit numéro {item_id} a été modifié avec succès !', 'info')
            return redirect(url_for('afficherproduit'))
        return render_template('/produit/modifier_produit.html', data=data, title="Produits")
    return redirect(url_for('connexion'))


@app.route("/affichermagasin")
def affichermagasin():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Magasin")
        data = cursor.fetchall()
        conn.close()
        return render_template("/magasin/afficher_magasin.html", data=data, title="Magasins")
    return redirect(url_for('connexion'))


@app.route("/ajoutermagasin", methods=["GET", "POST"])
def ajoutermagasin():
    if 'loggedin' in session:
        if request.method == 'POST':
            nom = request.form["nom"]
            adresse = request.form["adresse"]
            telephone = request.form["telephone"]
            email = request.form["email"]
            conn = pyodbc.connect(DSN)
            cursor = conn.cursor()
            cursor.execute('''
                        INSERT INTO Magasin (NomMagasin, AdresseMagasin, Telephone, Mail)
                        VALUES ( ?, ?, ?, ?)
                     ''', (nom, adresse, telephone, email))
            conn.commit()
            conn.close()
            flash("Votre magasin a été enregistré avec succès !", 'info')
            return redirect(url_for('affichermagasin'))
        data = ''
        return render_template("/magasin/ajouter_magasin.html", data=data, title="Magasins")
    return redirect(url_for('connexion'))


@app.route("/confirmsupmagasin/<int:item_id>", methods=['GET', 'POST'])
def confirmsupmagasin(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Magasin WHERE IdMagasin = ?', item_id)
        data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("/magasin/confirm_sup_magasin.html", data=data, title="Magasins")
    return redirect(url_for('connexion'))


@app.route('/supprimermagasin/<int:item_id>', methods=['GET', 'POST'])
def supprimermagasin(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Magasin WHERE IdMagasin = ?', item_id)
        conn.commit()
        conn.close()
        flash(f'Le magasin numéro {item_id} a été supprimé avec succès !', 'info')
        return redirect(url_for('affichermagasin'))
    return redirect(url_for('connexion'))


@app.route('/modifiermagasin/<int:item_id>', methods=['GET', 'POST'])
def modifiermagasin(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Magasin WHERE IdMagasin = ?', item_id)
        data = cursor.fetchone()
        if request.method == 'POST':
            nom = request.form["nom"]
            adresse = request.form["adresse"]
            telephone = request.form["telephone"]
            email = request.form["email"]
            cursor.execute('''
                            UPDATE Magasin
                            SET NomMagasin = ?, AdresseMagasin = ?, Telephone = ?, Mail = ?
                            WHERE IdMagasin = ?
                        ''', (nom, adresse, telephone, email, item_id))
            conn.commit()
            conn.close()
            flash(f'Le magasin numéro {item_id} a été modifié avec succès !', 'info')
            return redirect(url_for('affichermagasin'))
        return render_template('/magasin/modifier_magasin.html', data=data, title="Magasins")
    return redirect(url_for('connexion'))


@app.route("/afficherstock")
def afficherstock():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT Stock.Idstock, Produit.NomProduit, Magasin.NomMagasin, Stock.Quantitestock
            FROM Stock
            INNER JOIN Produit ON Produit.IdProduit=Stock.IdProduit
            INNER JOIN Magasin ON Magasin.IdMagasin=Stock.IdMagasin
        """)
        data = cursor.fetchall()
        conn.close()
        return render_template("/stock/afficher_stock.html", data=data, title="Stock")
    return redirect(url_for('connexion'))


@app.route("/ajouterstock", methods=["GET", "POST"])
def ajouterstock():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produit")
        prods = cursor.fetchall()
        cursor.execute('SELECT * FROM Magasin')
        mags = cursor.fetchall()
        if request.method == 'POST':
            nomproduit = request.form["nomproduit"]
            nommagasin = request.form["nommagasin"]
            quantite = request.form["quantite"]
            cursor.execute("""
                SELECT * FROM Stock
                WHERE IdProduit = ? AND IdMagasin = ?
                """, (nomproduit, nommagasin))
            existing = cursor.fetchone()
            if existing:
                quantite = int(quantite) + int(existing[1])
                cursor.execute('''
                       UPDATE Stock
                       SET Quantitestock = ?, IdProduit = ?, IdMagasin = ?
                       WHERE Idstock = ?
                   ''', (quantite, nomproduit, nommagasin, existing[0]))
            else:
                cursor.execute('''
                        INSERT INTO Stock (Quantitestock, IdProduit, IdMagasin)
                        VALUES ( ?, ?, ?)
                     ''', (quantite, nomproduit, nommagasin))
            conn.commit()
            conn.close()
            flash("Votre stock a été enregistré avec succès !", 'info')
            return redirect(url_for('afficherstock'))
        return render_template("/stock/ajouter_stock.html", mags=mags, prods=prods, title="Stock")
    return redirect(url_for('connexion'))


@app.route("/confirmsupstock/<int:item_id>", methods=['GET', 'POST'])
def confirmsupstock(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Stock WHERE Idstock = ?', item_id)
        data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("/stock/confirm_sup_stock.html", data=data, title="Stock")
    return redirect(url_for('connexion'))


@app.route('/supprimerstock/<int:item_id>', methods=['GET', 'POST'])
def supprimerstock(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM Stock WHERE Idstock = ?', item_id)
        conn.commit()
        conn.close()
        flash(f'Le stock numéro {item_id} a été supprimé avec succès !', 'info')
        return redirect(url_for('afficherstock'))
    return redirect(url_for('connexion'))


@app.route('/modifierstock/<int:item_id>', methods=['GET', 'POST'])
def modifierstock(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produit")
        prods = cursor.fetchall()
        cursor.execute('SELECT * FROM Magasin')
        mags = cursor.fetchall()
        cursor.execute('SELECT * FROM Stock WHERE Idstock = ?', item_id)
        data = cursor.fetchone()
        if request.method == 'POST':
            nomproduit = request.form["nomproduit"]
            nommagasin = request.form["nommagasin"]
            quantite = request.form["quantite"]
            cursor.execute('''
                               UPDATE Stock
                               SET Quantitestock = ?, IdProduit = ?, IdMagasin = ?
                               WHERE Idstock = ?
                           ''', (quantite, nomproduit, nommagasin, item_id))
            conn.commit()
            conn.close()
            flash(f'Le stock numéro {item_id} a été modifié avec succès !', 'info')
            return redirect(url_for('afficherstock'))
        return render_template('/stock/modifier_stock.html', prods=prods, mags=mags, data=data, title="Stock")
    return redirect(url_for('connexion'))


@app.route("/affichervente")
def affichervente():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
        Vente.IdVente, Produit.NomProduit, Magasin.NomMagasin, Vente.Quantitevendu, Vente.Prixtotal, Vente.Datevente
        FROM Vente
        INNER JOIN Produit ON Produit.IdProduit=Vente.IdProduit
        INNER JOIN Magasin ON Magasin.IdMagasin=Vente.IdMagasin
        """)
        data = cursor.fetchall()
        conn.close()
        return render_template("/vente/afficher_vente.html", data=data, title="Vente")
    return redirect(url_for('connexion'))


@app.route("/ajoutervente", methods=["GET", "POST"])
def ajoutervente():
    if 'loggedin' in session:
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produit")
        prods = cursor.fetchall()
        cursor.execute('SELECT * FROM Magasin')
        mags = cursor.fetchall()
        if request.method == 'POST':
            nomproduit = request.form["nomproduit"]
            nommagasin = request.form["nommagasin"]
            quantite = request.form["quantite"]
            datevente = request.form["datevente"]
            cursor.execute("""
                SELECT Stock.Quantitestock FROM Stock
                WHERE IdProduit = ? AND IdMagasin = ?
                """, (nomproduit, nommagasin))
            quantitestock = cursor.fetchone()
            if quantitestock:
                if int(quantitestock[0]) >= int(quantite) > 0:
                    today = datetime.datetime.now()
                    if datevente < str(today):
                        cursor.execute('''
                                SELECT Produit.PrixUnitaire FROM Produit WHERE Produit.IdProduit = ?
                                ''', nomproduit)
                        prixunitaire = cursor.fetchone()
                        prixtotal = int(quantite) * int(prixunitaire[0])
                        cursor.execute('''
                                    INSERT INTO Vente (Quantitevendu, IdProduit, IdMagasin, Datevente, Prixtotal)
                                    VALUES ( ?, ?, ?, ?, ?)
                                 ''', (quantite, nomproduit, nommagasin, datevente, prixtotal))
                        cursor.execute("""
                                    SELECT Stock.Quantitestock FROM Stock
                                    WHERE IdProduit = ? AND IdMagasin = ?
                                    """, (nomproduit, nommagasin))
                        quantitestock = cursor.fetchone()
                        quantitestock = int(quantitestock[0]) - int(quantite)
                        cursor.execute('''
                               UPDATE Stock
                               SET Quantitestock = ?, IdProduit = ?, IdMagasin = ? 
                               WHERE IdProduit = ? AND IdMagasin = ? 
                           ''', (quantitestock, nomproduit, nommagasin, nomproduit, nommagasin))
                    else:
                        flash("La date entrée est incorrecte !", 'info')
                        return redirect(url_for('ajoutervente'))
                    """elif int(quantite) == 0:
                        flash("Impossible d'enregistrer une vente avec 0 quantité vendue !", 'info')
                       return redirect(url_for('ajoutervente'))"""
                else:
                    flash("La quantité entrée est supérieur à la quantité en stock !", 'info')
                    return redirect(url_for('ajoutervente'))
            else:
                flash("Le magasin choisi choisi n'a ce produit en stock !", 'info')
                return redirect(url_for('ajoutervente'))
            conn.commit()
            conn.close()
            flash("Votre vente a été enregistré avec succès !", 'info')
            return redirect(url_for('affichervente'))
        return render_template("/vente/ajouter_vente.html", mags=mags, prods=prods, title="Vente")
    return redirect(url_for('connexion'))


@app.route("/confirmsupvente/<int:item_id>", methods=['GET', 'POST'])
def confirmsupvente(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Vente WHERE IdVente = ?', item_id)
        data = cursor.fetchone()
        conn.commit()
        conn.close()
        return render_template("/vente/confirm_sup_vente.html", data=data, title="Vente")
    return redirect(url_for('connexion'))


@app.route('/supprimervente/<int:item_id>', methods=['GET', 'POST'])
def supprimervente(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Vente WHERE IdVente = ?', item_id)
        vente = cursor.fetchone()
        cursor.execute('DELETE FROM Vente WHERE IdVente = ?', item_id)
        cursor.execute("""
                            SELECT Stock.Quantitestock FROM Stock
                            WHERE IdProduit = ? AND IdMagasin = ?
                            """, (vente[4], vente[5]))
        quantitestock = cursor.fetchone()
        quantitestock = int(quantitestock[0]) + int(vente[1])
        cursor.execute('''
                           UPDATE Stock
                           SET Quantitestock = ?
                           WHERE IdProduit = ? AND IdMagasin = ? 
                       ''', (quantitestock, vente[4], vente[5]))
        conn.commit()
        conn.close()
        flash(f'La vente numéro {item_id} a été supprimée avec succès !', 'info')
        return redirect(url_for('affichervente'))
    return redirect(url_for('connexion'))


@app.route('/modifiervente/<int:item_id>', methods=['GET', 'POST'])
def modifiervente(item_id):
    if 'loggedin' in session:
        item_id = int(item_id)
        conn = pyodbc.connect(DSN)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Produit")
        prods = cursor.fetchall()
        cursor.execute('SELECT * FROM Magasin')
        mags = cursor.fetchall()
        cursor.execute('SELECT * FROM Vente WHERE IdVente = ?', item_id)
        data = cursor.fetchone()
        if request.method == 'POST':
            nomproduit = request.form["nomproduit"]
            nommagasin = request.form["nommagasin"]
            quantite = request.form["quantite"]
            datevente = request.form["datevente"]
            cursor.execute("""
                        SELECT Stock.Quantitestock FROM Stock
                        WHERE IdProduit = ? AND IdMagasin = ?
                        """, (nomproduit, nommagasin))
            quantitestock = cursor.fetchone()
            if quantitestock:
                if int(quantitestock[0]) >= int(quantite) > 0:
                    today = datetime.datetime.now()
                    if datevente < str(today):
                        cursor.execute('''
                                        SELECT Produit.PrixUnitaire FROM Produit WHERE Produit.IdProduit = ?
                                        ''', nomproduit)
                        prixunitaire = cursor.fetchone()
                        prixtotal = int(quantite) * int(prixunitaire[0])
                        cursor.execute('''
                                       UPDATE Vente
                                       SET Quantitevendu = ?, IdProduit = ?, IdMagasin = ?, Datevente = ?, Prixtotal = ?
                                       WHERE IdVente = ?
                                   ''', (quantite, nomproduit, nommagasin, datevente, prixtotal, item_id))
                        cursor.execute("""
                                            SELECT Stock.Quantitestock FROM Stock
                                            WHERE IdProduit = ? AND IdMagasin = ?
                                            """, (nomproduit, nommagasin))
                        quantitestock = cursor.fetchone()
                        quantitestock = int(quantitestock[0]) - int(quantite)
                        cursor.execute('''
                                       UPDATE Stock
                                       SET Quantitestock = ?, IdProduit = ?, IdMagasin = ? 
                                       WHERE IdProduit = ? AND IdMagasin = ? 
                                   ''', (quantitestock, nomproduit, nommagasin, nomproduit, nommagasin))
                    else:
                        flash("La date entrée est incorrecte !", 'info')
                        return redirect(url_for('modifiervente', item_id=item_id))
                    """elif int(quantite) == 0:
                    flash("Impossible d'enregistrer une vente avec 0 quantité vendue !", 'info')
                    return redirect(url_for('modifiervente', item_id=item_id))"""
                else:
                    flash("La quantité entrée est supérieur à la quantité en stock !", 'info')
                    return redirect(url_for('modifiervente', item_id=item_id))
            else:
                flash("Le magasin choisi choisi n'a ce produit en stock !", 'info')
                return redirect(url_for('modifiervente', item_id=item_id))
            conn.commit()
            conn.close()
            flash(f'La vente numéro {item_id} a été modifiée avec succès !', 'info')
            return redirect(url_for('affichervente'))
        return render_template('/vente/modifier_vente.html', prods=prods, mags=mags, data=data, title="Vente")
    return redirect(url_for('connexion'))


@app.route("/deconnexion")
def deconnexion():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    return redirect(url_for('connexion'))


if __name__ == '__main__':
    app.run(debug=True)
