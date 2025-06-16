from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.secret_key = 'segredo_super_secreto'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///loja.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    senha = db.Column(db.String(200))

class Produto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100))
    descricao = db.Column(db.Text)
    preco = db.Column(db.Float)
    imagem_url = db.Column(db.String(200))

@app.route('/')
def home():
    produtos = Produto.query.all()
    return render_template('home.html', produtos=produtos)

@app.route('/produto/<int:id>')
def produto(id):
    produto = Produto.query.get_or_404(id)
    return render_template('produto.html', produto=produto)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        senha = request.form['senha']
        usuario = Usuario.query.filter_by(email=email).first()
        if usuario and check_password_hash(usuario.senha, senha):
            session['usuario_id'] = usuario.id
            return redirect(url_for('home'))
        return 'Login inválido'
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = generate_password_hash(request.form['senha'])
        novo = Usuario(nome=nome, email=email, senha=senha)
        db.session.add(novo)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.pop('usuario_id', None)
    return redirect(url_for('home'))

@app.route('/carrinho')
def carrinho():
    carrinho = session.get('carrinho', [])
    produtos = Produto.query.filter(Produto.id.in_(carrinho)).all() if carrinho else []
    return render_template('carrinho.html', produtos=produtos)

@app.route('/adicionar_carrinho/<int:id>')
def adicionar_carrinho(id):
    carrinho = session.get('carrinho', [])
    carrinho.append(id)
    session['carrinho'] = carrinho
    return redirect(url_for('carrinho'))

@app.route('/remover_carrinho/<int:id>')
def remover_carrinho(id):
    carrinho = session.get('carrinho', [])
    if id in carrinho:
        carrinho.remove(id)
        session['carrinho'] = carrinho
    return redirect(url_for('carrinho'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)
