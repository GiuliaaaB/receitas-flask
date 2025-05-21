from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'chave_secreta_para_sessoes'

# Banco de dados
db = SQLAlchemy(app)

# Login Manager
login_manager = LoginManager()
login_manager.login_view = "login"
login_manager.init_app(app)

# Modelos
class Receita(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String, nullable=False)
    tipo = db.Column(db.String, nullable=False)
    origem = db.Column(db.String, nullable=False)
    ingredientes = db.Column(db.String, nullable=False)
    modo_preparo = db.Column(db.String, nullable=False)

    def __init__(self, nome, tipo, origem, ingredientes, modo_preparo):
        self.nome = nome
        self.tipo = tipo
        self.origem = origem
        self.ingredientes = ingredientes
        self.modo_preparo = modo_preparo

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), nullable=False, unique=True)
    password = db.Column(db.String(150))
    is_admin = db.Column(db.Boolean, default=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Criar tabelas
with app.app_context():
    db.create_all()
    if not User.query.filter_by(username="admin").first():
        admin = User(username="admin", password="123", is_admin=True)
        db.session.add(admin)
        db.session.commit()

# 🚨 Rota principal agora faz o login
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form.get("user_type")

        if user_type == "visitor":
            visitor = User.query.filter_by(username="visitante").first()
            if not visitor:
                visitor = User(username="visitante", is_admin=False)
                db.session.add(visitor)
                db.session.commit()
            login_user(visitor)
            return redirect(url_for("lista"))

        elif user_type == "admin":
            username = request.form.get("username")
            password = request.form.get("password")
            user = User.query.filter_by(username=username).first()
            if user and user.password == password and user.is_admin:
                login_user(user)
                return redirect(url_for("lista"))
            else:
                return "Login inválido ou não autorizado."

    return render_template("index.html")  # Sua página de login

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

@app.route("/cadastrar")
@login_required
def cadastrar():
    if not current_user.is_admin:
        return "Acesso restrito"
    return render_template("cadastro.html")

@app.route("/cadastro", methods=["GET", "POST"])
@login_required
def cadastro():
    if not current_user.is_admin:
        return "Acesso restrito"

    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")
        origem = request.form.get("origem")
        ingredientes = request.form.get("ingredientes")
        modo_preparo = request.form.get("modo")

        if nome and tipo and origem and ingredientes and modo_preparo:
            nova_receita = Receita(nome, tipo, origem, ingredientes, modo_preparo)
            db.session.add(nova_receita)
            db.session.commit()
            return redirect(url_for("lista"))

    return render_template("cadastro.html")

@app.route("/lista")
@login_required
def lista():
    receitas = Receita.query.all()
    return render_template("lista.html", receitas=receitas)

@app.route("/excluir/<int:id>")
@login_required
def excluir(id):
    if not current_user.is_admin:
        return "Acesso restrito"
    receita = Receita.query.get(id)
    if receita:
        db.session.delete(receita)
        db.session.commit()
    return redirect(url_for('lista'))

@app.route("/atualizar/<int:id>", methods=['GET', 'POST'])
@login_required
def atualizar(id):
    if not current_user.is_admin:
        return "Acesso restrito"

    receita = Receita.query.get(id)

    if request.method == "POST":
        nome = request.form.get("nome")
        tipo = request.form.get("tipo")
        origem = request.form.get("origem")
        ingredientes = request.form.get("ingredientes")
        modo_preparo = request.form.get("modo")

        if nome and tipo and origem and ingredientes and modo_preparo:
            receita.nome = nome
            receita.tipo = tipo
            receita.origem = origem
            receita.ingredientes = ingredientes
            receita.modo_preparo = modo_preparo
            db.session.commit()
            return redirect(url_for("lista"))

    return render_template("atualizar.html", receita=receita)

if __name__ == "__main__":
    app.run(debug=True)
