import os
from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] =\
    'sqlite:///' + os.path.join(basedir, 'data.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# --- MODELO (Banco de Dados) ---
# Substituimos User/Role por Curso
class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.String(250), nullable=False)

    def __repr__(self):
        return '<Curso %r>' % self.nome

# --- FORMULÁRIO ---
# Substituimos NameForm por CursoForm
class CursoForm(FlaskForm):
    nome = StringField('Qual é o nome do curso?', validators=[DataRequired()])
    # TextAreaField cria a caixa de texto maior, Length limita os caracteres
    descricao = TextAreaField('Descrição (250 caracteres)', validators=[DataRequired(), Length(max=250)])
    submit = SubmitField('Cadastrar')

@app.shell_context_processor
def make_shell_context():
    return dict(db=db, Curso=Curso)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

@app.route('/', methods=['GET', 'POST'])
def index():
    form = CursoForm()
    
    # Lógica de Salvar no Banco
    if form.validate_on_submit():
        # Cria o objeto com os dados do formulário
        novo_curso = Curso(nome=form.nome.data, descricao=form.descricao.data)
        
        # Adiciona e Comita no banco
        db.session.add(novo_curso)
        db.session.commit()
        
        # Redireciona para limpar o formulário (PRG Pattern)
        return redirect(url_for('index'))
    
    # Lógica de Listagem e Ordenação
    # Requiremento da prova: "ordenação do retorno do banco de dados"
    cursos_ordenados = Curso.query.order_by(Curso.nome).all()
    
    return render_template('index.html', form=form, cursos=cursos_ordenados)

if __name__ == '__main__':
    app.run(debug=True)
