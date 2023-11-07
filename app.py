from flask import Flask, render_template, request, url_for, flash, redirect

app = Flask(__name__)


@app.route("/")
def connexion():
    return render_template("connexion.html")


@app.route("/accueil")
def accueil():
    return render_template("accueil.html", title="accueil")


if __name__ == '__main__':
    app.run(debug=True)
