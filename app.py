from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash 
import mercadopago



# Inicializa o app Flask
app = Flask(__name__)


# Configuração do banco de dados (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SECRET_KEY'] = 'mysecretkey'  # Usado para sessões
db = SQLAlchemy(app)

# Modelo do banco de dados para os usuários
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)

class Paciente(db.Model):
    id_pac = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(150), unique=True, nullable=False)
    idade = db.Column(db.Integer, nullable=False)
    endereco = db.Column(db.String(500), nullable=False)
    telefone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    historico = db.Column(db.String(15000), nullable=False)
    


class Medico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    especialidade = db.Column(db.String(100))
    crm = db.Column(db.String(20), unique=True, nullable=False)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(100))
    horarios_atendimento = db.Column(db.Text)

class Medicamento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text, nullable=False)
    fabricante = db.Column(db.String(100), nullable=False)
    validade = db.Column(db.String, nullable=False)

class Internacao(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_paciente = db.Column(db.Integer, db.ForeignKey('paciente.id_pac'), nullable=False)
    id_medico = db.Column(db.Integer, db.ForeignKey('medico.id'), nullable=False)
    data_inicio = db.Column(db.Text, nullable=False)
    data_fim = db.Column(db.Text, nullable=False)
    observacoes = db.Column(db.Text, nullable=True)
    
    # Relacionamentos
    paciente = db.relationship('Paciente', backref=db.backref('internacoes', lazy=True))
    medico = db.relationship('Medico', backref=db.backref('internacoes', lazy=True))

    def __repr__(self):
        return f'<Internacao {self.id}>'


class Consulta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome_paciente = db.Column(db.String(150), db.ForeignKey('paciente.nome'), nullable=False)  # Chave estrangeira para 'nome' de Paciente
    data = db.Column(db.String(100), nullable=False)
    hora = db.Column(db.String(100), nullable=False)
    
    # Relacionamento com a tabela Paciente
    paciente = db.relationship('Paciente', backref=db.backref('consultas', lazy=True))

    def __repr__(self):
        return f'<Consulta {self.id}>'





with app.app_context():
    db.create_all()



def check_permissions(role_required):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if 'username' not in session or session.get('username') != role_required:
                flash("Acesso negado. Faça login com as credenciais apropriadas.", 'danger')
                return redirect(url_for('login'))
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Rota de login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar se o usuário existe
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            flash("Login bem-sucedido!", 'success')
            return redirect(url_for('index'))
        else:
            flash("Usuário ou senha incorretos.", 'danger')
            return redirect(url_for('login'))

    return render_template('index.html')

# Rota de logout
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    flash("Você foi desconectado.", 'info')
    return redirect(url_for('index'))



#rota para o index.hmtl
@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html')
#rota para exemplo.html
@app.route('/exemplo', methods=['GET', 'POST'])
def exemplo():
    return render_template('especialidades.html')
#rota para registro_pac.html
@app.route('/pac', methods=['GET', 'POST'])
@check_permissions('recepção')
def pac():
    return render_template('registro_pac.html')

#rota para registro_rem.html
@app.route('/rem', methods=['GET', 'POST'])
@check_permissions('tecnico')
def rem():
    return render_template('registro_rem.html')

#rota para registro_doc.html
@app.route('/doc', methods=['GET', 'POST'])
@check_permissions('tecnico')
def doc():
    return render_template('registro_doc.html')

@app.route('/inter', methods=['GET', 'POST'])
@check_permissions('tecnico')
def inter():
    return render_template('registro_internacoes.html')

#rota para o registro de usuarios
@app.route('/cad', methods=['GET', 'POST'])
def cad():
    return render_template('registro_usuario.html')

#rota para o registro de consultas
@app.route('/con', methods=['GET', 'POST'])
@check_permissions('recepção')
def con():
    return render_template('registro_consulta.html')

#rota para editar consultas
@app.route('/editarcon')
@check_permissions('tecnico')
def editarcon():
    return render_template('editar_consultas')




#rota de cadastro de pacientes 
@app.route('/registropaciente', methods=['GET', 'POST'])
@check_permissions('recepção')
def registro_paciente():
    if request.method == 'POST':
        nome = request.form['nome']
        idade = request.form['idade']
        endereco = request.form['endereco']
        telefone = request.form['telefone']
        email = request.form['email']
        historico = request.form['historico']

        novo_paciente = Paciente(nome = nome, idade = idade, endereco = endereco, telefone = telefone, email = email, historico = historico)
        db.session.add(novo_paciente)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro_pac.html')


#rota para a página que mostra os pacientes
@app.route('/listar_pacientes')
@check_permissions('recepção')
def listar_pacientes():
    pacientes = Paciente.query.all()  # Certifique-se de que a classe Paciente está sendo referenciada corretamente
    return render_template('listar_pacientes.html', pacientes=pacientes)

# Rota para deletar um paciente
@app.route('/deletar_paciente/<int:id_pac>', methods=['POST'])
@check_permissions('recepção')
def deletar_paciente(id_pac):
    paciente = Paciente.query.get(id_pac)  
    if paciente:
        nome = request.form['nome']
         # Deletar consultas associadas ao paciente
        Consulta.query.filter_by(nome_paciente=nome).delete()
        #deletar as internações do paciente
        Internacao.query.filter_by(id_paciente=id_pac).delete()
        db.session.delete(paciente)
        db.session.commit()
        return redirect(url_for('listar_pacientes'))


# Rota para exibir a página de edição de um paciente
@app.route('/editar_paciente/<int:id_pac>', methods=['GET'])
@check_permissions('recepção')
def editar_paciente(id_pac):
    paciente = Paciente.query.get(id_pac)
    if not paciente:
        flash('Paciente não encontrado.', 'danger')
        return redirect(url_for('listar_pacientes'))
    return render_template('editar_paciente.html', paciente=paciente)

# Rota para atualizar os dados do paciente
@app.route('/atualizar_paciente/<int:id_pac>', methods=['POST'])
@check_permissions('recepção')
def atualizar_paciente(id_pac):
    paciente = Paciente.query.get(id_pac)
    if not paciente:
        flash('Paciente não encontrado.', 'danger')
        return redirect(url_for('listar_pacientes'))

    paciente.nome = request.form['nome']
    paciente.idade = request.form['idade']
    paciente.endereco = request.form['endereco']
    paciente.telefone = request.form['telefone']
    paciente.email = request.form['email']
    paciente.historico = request.form['historico']

    try:
        db.session.commit()
        flash('Dados do paciente atualizados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar os dados. Tente novamente.', 'danger')

    return redirect(url_for('listar_pacientes'))




@app.route('/registrar_medicamento', methods=['GET', 'POST'])
@check_permissions('tecnico')
def registrar_medicamentos():
    if request.method == 'POST':

        nome = request.form['nome']
        descricao = request.form['descricao']
        fabricante = request.form['fabricante']
        validade = request.form['validade']

        medicamento = Medicamento(nome = nome, descricao = descricao, fabricante = fabricante, validade = validade)
        db.session.add(medicamento)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro_pac.html')

#rota para listar os medicamentos
@app.route('/listar_medicamentos')
@check_permissions('tecnico')
def listar_medicamentos():
    medicamentos = Medicamento.query.all()  # Recupera todos os medicamentos do banco de dados
    return render_template('listar_medicamentos.html', medicamentos=medicamentos)

@app.route('/deletar_medicamento/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def deletar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    if medicamento:
        try:
            db.session.delete(medicamento)
            db.session.commit()
            flash('Medicamento deletado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao deletar medicamento. Tente novamente.', 'danger')
    return redirect(url_for('listar_medicamentos'))


@app.route('/editar_medicamento/<int:id>', methods=['GET'])
@check_permissions('tecnico')
def editar_medicamento(id):
    medicamento = Medicamento.query.get(id)
    return render_template('editar_medicamento.html', medicamento=medicamento)

@app.route('/atualizar_medicamento/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def atualizar_medicamento(id):
    # Busca o medicamento pelo ID
    medicamento = Medicamento.query.get_or_404(id)
    
    # Atualiza os campos com os dados do formulário
    medicamento.nome = request.form['nome']
    medicamento.descricao = request.form['descricao']
    medicamento.fabricante = request.form['fabricante']
    medicamento.validade = request.form['validade']
    
    # Salva as alterações no banco de dados
    db.session.commit()
    flash('Medicamento atualizado com sucesso!', 'success')
    
    return redirect(url_for('listar_medicamentos'))


@app.route('/registrar_medico', methods=['GET', 'POST'])
@check_permissions('tecnico')
def registrar_medico():
    if request.method == 'POST':
        nome = request.form['nome']
        especialidade = request.form['especialidade']
        crm = request.form['crm']
        telefone = request.form['telefone']
        email = request.form['email']
        horarios_atendimento = request.form['horarios_atendimento']

        medico = Medico(nome=nome, especialidade=especialidade, crm=crm, telefone=telefone, email=email, horarios_atendimento=horarios_atendimento,)
        db.session.add(medico)
        db.session.commit()
        flash('Médico registrado com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('registro_doc.html')

@app.route('/listar_medicos')
@check_permissions('tecnico')
def listar_medicos():
    medicos = Medico.query.all()
    return render_template('listar_medicos.html', medicos=medicos)


@app.route('/deletar_medico/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def deletar_medico(id):
    medico = Medico.query.get(id)
    if medico:
        try:
            db.session.delete(medico)
            db.session.commit()
            flash('Médico deletado com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao deletar médico. Tente novamente.', 'danger')
    return redirect(url_for('listar_medicos'))



# Rota para exibir a página de edição de um médico
@app.route('/editar_medico/<int:id>', methods=['GET'])
@check_permissions('tecnico')
def editar_medico(id):
    medico = Medico.query.get(id)
    if not medico:
        flash('Médico não encontrado.', 'danger')
        return redirect(url_for('listar_medicos'))
    return render_template('editar_medico.html', medico=medico)

# Rota para atualizar os dados de um médico
@app.route('/atualizar_medico/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def atualizar_medico(id):
    medico = Medico.query.get(id)
    if not medico:
        flash('Médico não encontrado.', 'danger')
        return redirect(url_for('listar_medicos'))

    # Atualizar os dados do médico com base nos inputs do formulário
    medico.nome = request.form['nome']
    medico.especialidade = request.form['especialidade']
    medico.crm = request.form['crm']
    medico.telefone = request.form['telefone']
    medico.email = request.form['email']
    medico.horarios_atendimento = request.form['horarios_atendimento']

    try:
        db.session.commit()
        flash('Dados do médico atualizados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar os dados. Tente novamente.', 'danger')
    return redirect(url_for('listar_medicos'))



@app.route('/registrar_internacao', methods=['GET', 'POST'])
@check_permissions('tecnico')
def registrar_internacao():
    if request.method == 'POST':
        id_paciente = request.form['id_paciente']
        id_medico = request.form['id_medico']
        data_inicio = request.form['data_inicio']
        data_fim = request.form['data_fim']
        observacoes = request.form['observacoes']

        internacao = Internacao(
            id_paciente=id_paciente,
            id_medico=id_medico,
            data_inicio=data_inicio,
            data_fim=data_fim,
            observacoes=observacoes
        )
        
        db.session.add(internacao)
        db.session.commit()
        flash('Internação registrada com sucesso!', 'success')
        return redirect(url_for('index'))
    return render_template('registro_internacao.html')


@app.route('/editar_internacao/<int:id>', methods=['GET'])
@check_permissions('tecnico')
def editar_internacao(id):
    internacao = Internacao.query.get(id)
    if not internacao:
        flash('Internação não encontrada.', 'danger')
        return redirect(url_for('listar_internacoes'))
    return render_template('editar_internacoes.html', internacao=internacao)


@app.route('/atualizar_internacao/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def atualizar_internacao(id):
    internacao = Internacao.query.get(id)
    if not internacao:
        flash('Internação não encontrada.', 'danger')
        return redirect(url_for('listar_internacoes'))

    # Atualizar os dados da internação com base nos inputs do formulário
    internacao.id_pac = request.form['id_pac']
    internacao.id_medico= request.form['id_medico']
    internacao.data_inicio= request.form['data_inicio']
    internacao.data_fim = request.form['data_fim']
    internacao.observacoes = request.form['observacoes']

    try:
        db.session.commit()
        flash('Dados da internação atualizados com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar os dados da internação. Tente novamente.', 'danger')
    return redirect(url_for('listar_internacoes'))


@app.route('/deletar_internacao/<int:id>', methods=['POST'])
@check_permissions('tecnico')
def deletar_internacao(id):
    internacao = Internacao.query.get(id)
    if internacao:
        try:
            db.session.delete(internacao)
            db.session.commit()
            flash('Internação deletada com sucesso!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Erro ao deletar internação. Tente novamente.', 'danger')
    return redirect(url_for('listar_internacoes'))



# Rota para listar as internações
@app.route('/listar_internacoes')
@check_permissions('tecnico')
def listar_internacoes():
    internacoes = Internacao.query.all()  # Pega todas as internações do banco de dados
    return render_template('listar_internacoes.html', internacoes=internacoes)




#rota de cadastro de consultas 
@app.route('/registrar_consulta', methods=['GET', 'POST'])
@check_permissions('recepção')
def registar_consulta():
    if request.method == 'POST':
        nome_paciente = request.form['nome']
        data = request.form['data']
        hora = request.form['hora']

        nova_consulta = Consulta(data = data, hora = hora, nome_paciente=nome_paciente)
        db.session.add(nova_consulta)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('registro_consulta.html')

@app.route('/listar_consultas')
@check_permissions('recepção')
def listar_consultas():
    consultas = Consulta.query.all()  # Obtém todas as consultas
    return render_template('listar_consultas.html', consultas=consultas)

@app.route('/deletar_consulta/<int:id>', methods=['POST'])
@check_permissions('recepção')
def deletar_consulta(id):
    consulta = Consulta.query.get(id)
    if consulta:
        db.session.delete(consulta)
        db.session.commit()
    return redirect(url_for('listar_consultas'))

@app.route('/editar_consulta/<int:id>', methods=['GET', 'POST'])
@check_permissions('recepção')
def editar_consulta(id):
    consulta = Consulta.query.get_or_404(id)  # Buscar a consulta pelo ID
    if request.method == 'POST':
        consulta.nome_paciente = request.form['nome']
        consulta.data = request.form['data']  # Atualize os dados conforme necessário
        consulta.hora = request.form['hora']
        db.session.commit()  # Salve as alterações no banco de dados
        return redirect(url_for('listar_consultas'))  # Redireciona para a lista de consultas
    return render_template('editar_consultas.html', consulta=consulta)


@app.route('/atualizar_consulta/<int:id>', methods=['POST'])
@check_permissions('recepção')
def atualizar_consulta(id):
    consulta = Consulta.query.get(id)
    if not consulta:
        flash('Consulta não encontrada.', 'danger')
        return redirect(url_for('listar_consultas'))

    consulta.nome_paciente = request.form['nome']
    consulta.data = request.form['data']
    consulta.hora = request.form['hora']

    try:
        db.session.commit()
        flash('Consulta atualizada com sucesso!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Erro ao atualizar a consulta. Tente novamente.', 'danger')

    return redirect(url_for('listar_consultas'))





# Rota de cadastro de usuário
@app.route('/registrousuario', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        # Verificar se o usuário já existe
        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash("Usuário já existe. Tente outro nome.", 'danger')
            return redirect(url_for('register'))

        # Criar novo usuário
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Cadastro realizado com sucesso!")
        return redirect(url_for('index'))
    return render_template('registro_usuario.html')





# Configurando a SDK do Mercado Pago com a chave de autenticação
sdk = mercadopago.SDK("APP_USR-1039031589021141-083016-42e7088c9468867a9864f5b93b03892a-1968082587")

# Função para gerar o link de pagamento
def gerar_link_pagamento(titulo, preco):
    payment_data = {
        "items": [
            {
                "id": "1",
                "title": titulo,
                "quantity": 1,
                "currency_id": "BRL",
                "unit_price": float(preco)
            }
        ],
        "back_urls": {
            "success": "http://127.0.0.1:5000/compracerta",
            "failure": "http://127.0.0.1:5000/compraerrada",
            "pending": "http://127.0.0.1:5000/compraerrada",
        },
        "auto_return": "all"
    }
    result = sdk.preference().create(payment_data)
    payment = result["response"]
    link_iniciar_pagamento = payment["init_point"]
    return link_iniciar_pagamento



@app.route('/exames')
def exames():
    exames_disponiveis = [
        {"nome": "Hemograma Completo", "descricao": "Análise completa do sangue", "preco": 80.00},
        {"nome": "Raio-X", "descricao": "Imagem radiológica de alta precisão", "preco": 120.00},
        {"nome": "Ultrassonografia", "descricao": "Exame de imagem com ultrassom", "preco": 200.00},
        {"nome": "Ressonância Magnética", "descricao": "Exame de imagem por ressonância", "preco": 800.00},
        {"nome": "Eletrocardiograma", "descricao": "Monitoramento da atividade elétrica do coração", "preco": 150.00},
        {"nome": "Tomografia Computadorizada", "descricao": "Imagem detalhada por cortes do corpo", "preco": 700.00},
        {"nome": "Teste de Glicemia", "descricao": "Medição do nível de açúcar no sangue", "preco": 30.00},
        {"nome": "Exame de Urina", "descricao": "Análise bioquímica da urina", "preco": 40.00},
        {"nome": "Exame de Colesterol", "descricao": "Verificação dos níveis de colesterol", "preco": 50.00},
        {"nome": "Papanicolau", "descricao": "Detecção precoce de câncer cervical", "preco": 90.00},
        {"nome": "Triglicerídeos", "descricao": "Avaliação dos níveis de gordura no sangue", "preco": 90.00},
        {"nome": "Insulina", "descricao": "Análise de níveis de insulina no sangue", "preco": 110.00},
        {"nome": "Transaminases (TGO e TGP)", "descricao": "Avaliação da função hepática", "preco": 120.00},
        {"nome": "Hormônios da tireoide (TSH e T4 livre)", "descricao": "Monitoramento da saúde da tireoide", "preco": 130.00},
        {"nome": "Ureia e creatinina", "descricao": "Avaliação da função renal", "preco": 100.00},
        {"nome": "Exame de fezes", "descricao": "Detecção de parasitas e outros problemas digestivos", "preco": 65.00}
    ]
    return render_template("exames.html", exames=exames_disponiveis)

@app.route('/pagar/<nome_exame>/<preco>')
def pagar(nome_exame, preco):
    link = gerar_link_pagamento(nome_exame, preco)
    return redirect(link)

@app.route('/compracerta')
def compracerta():
    return render_template('compracerta.html')

@app.route('/compraerrada')
def compraerrada():
    return render_template('compraerrada.html')




if __name__ == '__main__':
    app.run(debug=True)
