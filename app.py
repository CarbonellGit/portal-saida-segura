# app.py - Versão com rota temporária para criar o banco de dados

import os
import requests
import base64 
from dotenv import load_dotenv 
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

load_dotenv()

# --- Leitura e Validação das Variáveis de Ambiente ---
SOPHIA_TENANT = os.environ.get('SOPHIA_TENANT')
SOPHIA_USER = os.environ.get('SOPHIA_USER')
SOPHIA_PASSWORD = os.environ.get('SOPHIA_PASSWORD')
SOPHIA_API_HOSTNAME = os.environ.get('SOPHIA_API_HOSTNAME', 'portal.sophia.com.br')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD') 
SECRET_KEY = os.environ.get('SECRET_KEY')

if not all([SOPHIA_TENANT, SOPHIA_USER, SOPHIA_PASSWORD, ADMIN_PASSWORD, SECRET_KEY]):
    raise ValueError("Erro: Uma ou mais variáveis de ambiente essenciais não foram configuradas.")

# --- Configurações da Aplicação ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['ADMIN_PASSWORD'] = ADMIN_PASSWORD
app.config['SOPHIA_API_BASE_URL'] = f"https://{SOPHIA_API_HOSTNAME}/SophiAWebApi/{SOPHIA_TENANT}"

# --- Configuração do Banco de Dados ---
database_url = os.environ.get('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url.replace("postgres://", "postgresql://", 1)
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'database.db')

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Modelo do Banco de Dados ---
class RegistroSaida(db.Model):
    # (código do modelo do banco de dados permanece o mesmo)
    __tablename__ = 'registros_saida'
    id = db.Column(db.Integer, primary_key=True)
    aluno_nome = db.Column(db.String(200), nullable=False)
    responsavel_nome = db.Column(db.String(200), nullable=False)
    data_hora_saida = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    atendente_nome = db.Column(db.String(100), nullable=False)
    observacoes = db.Column(db.Text, nullable=True)

# ... (todas as outras rotas e funções permanecem as mesmas) ...
def get_sophia_token():
    auth_url = app.config['SOPHIA_API_BASE_URL'] + "/api/v1/Autenticacao"
    auth_data = {"usuario": SOPHIA_USER, "senha": SOPHIA_PASSWORD}
    try:
        response = requests.post(auth_url, json=auth_data, timeout=10)
        response.raise_for_status() 
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Erro de Conexão/HTTP na API ({auth_url}): {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def pagina_inicial():
    alunos_encontrados = []
    if request.method == 'POST':
        nome_aluno = request.form.get('nome_aluno')
        if not nome_aluno:
            flash('Por favor, digite um nome para buscar.', 'warning')
            return redirect(url_for('pagina_inicial'))
        
        token = get_sophia_token()
        if not token:
            flash('Erro de autenticação com o sistema. Verifique as credenciais da API.', 'danger')
            return render_template('index.html', alunos=alunos_encontrados)
        
        search_url = app.config['SOPHIA_API_BASE_URL'] + "/api/v1/Alunos"
        headers = {'token': token, 'Accept': 'application/json'}
        params = {'Nome': nome_aluno}
        try:
            response = requests.get(search_url, headers=headers, params=params, timeout=10)
            response.raise_for_status()
            alunos_encontrados = response.json()
            if not alunos_encontrados:
                flash(f'Nenhum aluno encontrado com o nome "{nome_aluno}".', 'info')
        except (json.JSONDecodeError, requests.exceptions.RequestException) as e:
            flash(f'Erro ao buscar alunos: {e}', 'danger')

    return render_template('index.html', alunos=alunos_encontrados, logged_in=session.get('logged_in'))

@app.route('/aluno/<int:aluno_id>')
def detalhes_aluno(aluno_id):
    token = get_sophia_token()
    if not token:
        flash('Erro de autenticação ao buscar detalhes.', 'danger')
        return redirect(url_for('pagina_inicial'))

    headers = {'token': token, 'Accept': 'application/json'}
    details_url = app.config['SOPHIA_API_BASE_URL'] + f"/api/v1/alunos/{aluno_id}/AutorizacaoRetirada"
    try:
        response_auth = requests.get(details_url, headers=headers, timeout=10)
        response_auth.raise_for_status()
        dados_autorizacao = response_auth.json()
        responsaveis = dados_autorizacao.get('responsaveisAutorizados', [])

        for responsavel in responsaveis:
            responsavel['foto_uri'] = None
            codigo_responsavel = responsavel.get('codigo')
            if codigo_responsavel:
                foto_url = app.config['SOPHIA_API_BASE_URL'] + f"/api/v1/responsaveis/{codigo_responsavel}/fotos"
                try:
                    response_foto = requests.get(foto_url, headers=headers, timeout=5)
                    if response_foto.status_code == 200 and response_foto.text:
                        dados_foto = response_foto.json()
                        responsavel['foto_uri'] = dados_foto.get('foto')
                except (requests.exceptions.RequestException, json.JSONDecodeError) as e:
                    print(f"Não foi possível buscar ou decodificar a foto para o responsável {codigo_responsavel}: {e}")
        
        return render_template('detalhes_aluno.html', autorizados=responsaveis)
    except requests.exceptions.RequestException as e:
        flash(f"Erro ao buscar detalhes do aluno: {e}", "danger")
        return redirect(url_for('pagina_inicial'))

@app.route('/registrar-saida', methods=['GET', 'POST'])
def registrar_saida_form():
    if request.method == 'POST':
        aluno_nome = request.form.get('aluno_nome')
        responsavel_nome = request.form.get('responsavel_nome')
        data_hora_saida = datetime.fromisoformat(request.form.get('data_hora'))
        atendente_nome = request.form.get('atendente_nome')
        observacoes = request.form.get('observacoes')

        novo_registro = RegistroSaida(
            aluno_nome=aluno_nome, responsavel_nome=responsavel_nome,
            data_hora_saida=data_hora_saida, atendente_nome=atendente_nome,
            observacoes=observacoes
        )
        db.session.add(novo_registro)
        db.session.commit()
        flash(f'Saída do aluno {aluno_nome} registrada com sucesso!', 'success')
        return redirect(url_for('pagina_inicial'))

    aluno_id = request.args.get('aluno_id')
    responsavel_nome = request.args.get('responsavel_nome')
    token = get_sophia_token()
    if not token:
        flash('Erro de autenticação', 'danger')
        return redirect(url_for('pagina_inicial'))
    
    aluno_url = app.config['SOPHIA_API_BASE_URL'] + f"/api/v1/Alunos/{aluno_id}"
    headers = {'token': token, 'Accept': 'application/json'}
    response = requests.get(aluno_url, headers=headers)
    aluno = response.json() if response.status_code == 200 else {'nome': 'Não encontrado', 'codigo': aluno_id}
    data_hora_atual = datetime.now().strftime('%Y-%m-%dT%H:%M')

    return render_template('registrar_saida.html', 
        aluno=aluno, responsavel_nome=responsavel_nome,
        data_hora_atual=data_hora_atual
    )

# --- ROTAS DE ADMINISTRAÇÃO ---
@app.route('/login', methods=['GET', 'POST'])
def pagina_login():
    if request.method == 'POST':
        if request.form.get('password') == app.config['ADMIN_PASSWORD']:
            session['logged_in'] = True
            return redirect(url_for('pagina_admin'))
        else:
            flash('Senha incorreta. Tente novamente.', 'danger')
    return render_template('login.html')

@app.route('/logout')
def pagina_logout():
    session.pop('logged_in', None)
    flash('Você foi desconectado.', 'info')
    return redirect(url_for('pagina_inicial'))

@app.route('/admin')
def pagina_admin():
    if not session.get('logged_in'):
        return redirect(url_for('pagina_login'))
    return render_template('admin.html')

@app.route('/historico')
def pagina_historico():
    if not session.get('logged_in'):
        return redirect(url_for('pagina_login'))
    
    nome_aluno_filtro = request.args.get('nome_aluno', '')
    data_filtro = request.args.get('data', '')
    query = RegistroSaida.query

    if nome_aluno_filtro:
        query = query.filter(RegistroSaida.aluno_nome.ilike(f'%{nome_aluno_filtro}%'))
    if data_filtro:
        query = query.filter(db.func.date(RegistroSaida.data_hora_saida) == data_filtro)

    registros = query.order_by(RegistroSaida.data_hora_saida.desc()).all()
    return render_template('historico.html', registros=registros)


# --- INICIALIZAÇÃO DA APLICAÇÃO ---
if __name__ == '__main__':
    app.run()