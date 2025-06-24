#Importação de bibliotecas
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS #Permite com que a API aceite requisições vindas de outros domínios
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user #Caso segure o Ctrl+Left Mouse, é possível ver as funções que o usermixin possui para esse caso do usuário
#Login_user seria uma biblioteca para realizar a autenticação do usuário, já o Login Manager faria o gerenciamento dos usuários, quais estariam logados e quais não
#Login_required responsável por obrigar o usuário a estar autenticado nas rotas definidas que necessitam estar logado/autenticado


#app seria uma váriavel que irá receber uma instância da classe Flask
#Dentro do parentêses foi passado uma variável, cujo nome é "name"
app = Flask(__name__)
app.config['SECRET_KEY'] = "chave_testeAPI_123"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' #Linha de configuração do banco de dados

login_manager = LoginManager()
db = SQLAlchemy(app) #Essa linha seria para a conexão com o banco de dados passando o parâmetro do app Flask
login_manager.init_app(app) #Responsável por receber a aplicação e inicializa-lá
login_manager.login_view = '/login' #Nesse caso o login view junto do login manager realizariam a autenticação do login e para isso foi passada a rota criada para o login (no caso /login)
CORS(app)

#Modelagem 
#Modelo de Usuário para isso é necessário o (Id, username, password)
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True) 
    username = db.Column(db.String(80), nullable=False, unique=True) #Unique = True, logo o username precisa ser único para cada usuário 
    password = db.Column(db.String(80), nullable=False)
    cart = db.relationship('CartItem', backref='user', lazy=True)

#Para realizar a modelagem do database seria necessário definir uma classe, nesse caso a primeira classe seria de produto
class Product(db.Model): #Model vai servir de molde para a classe produto
    id = db.Column(db.Integer, primary_key=True) #ID do tipo inteiro (Integer), e uma chave primária para não ser repetido.
    name = db.Column(db.String(120), nullable=False) #Definimos a string, quantidade de dados e o mesmo não pode ser nulo (nullable)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)#.Text não teria limitação de caracteres igual o string, opcional.

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) #Referenciando o ID da classe de usuário com uma chave estrangeira.
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'), nullable=False) #Referenciado o ID da classe de produto para que seja possível verificar qual seria o produto que será adicionado/excluído do carrinho

#Autenticação
@login_manager.user_loader #Essa função seria para que toda vez que for realizada uma requisição em uma rota protegida, seria necessário que o Login_required da rota recupere o usuário que está tentando acessar para verificar se é autenticado
def load_user(user_id): #Nesse caso, esse papel seria do load_user, para que seja possível essa recuperação e verificação se o usuário está autenticado.
    return User.query.get(int(user_id)) #Get recuperaria o ID que consta nos cookies para retornar, porém geralmente ele consta no cookies como string, por conta disso seria necessário converter para int

@app.route('/login', methods=["POST"])
def login():
    data = request.json

    user = User.query.filter_by(username=data.get("username")).first()
    #Criada a variável user, utilizando o modelo User e é realizada uma busca através do query com o método filter_by (Filtraria o dado através do username)
    #Username que consta no banco é recuperado e retornaria uma lista porém é utilizado o método first, para que seja retornado apenas o primeiro dessa lista de usuários
    
    #Verificado que consta o usuário no database, logo o usuário existiria seria verificada a senha
    if user and data.get("password") == user.password: #Nesse caso, verificaria a senha que foi enviada pela requisição através do data.get e comparada com a senha que possui no banco de dados
            login_user(user)
            return jsonify({"message": "Logged succesfully"})
    return jsonify({"message": "Unauthorized. Invalid Credentials"}), 401


@app.route('/logout', methods=["POST"]) #Realizar o logout do usuário, só é possível caso o usuário esteja logado por conta disso o login_required
@login_required
def logout():
    logout_user()
    return jsonify({"message": "Logout succesfully"})

@app.route('/api/products/add', methods=["POST"]) #Na documentação, foi definido que o modelo de adicionar seria apenas com o método POST
@login_required #Como essa rota desejamos que o usuário esteja autenticado, seria necessário adicionar essa linha.
def add_products():
    data = request.json #Basicamente irá receber os dados da requisição (request.json), seria o que o cliente informa
    if 'name' in data and 'price' in data: #Verificaria se os dados possuem na requisição, e só adicionaria caso passasse por essa verificação
        product = Product(name=data["name"], price=data["price"], description=data.get("description", ""))
    #Foi definido o produto, no qual puxará as informações da requisição (que seria o que foi informado pelo cliente)
    #O get seria para caso não ache nada no description, retornaria esse valor fixo (No caso, nulo), já o price e name retornaria erro caso não encontre nada
        db.session.add(product)#Seria o rascunho para adição no produto no database, seria efetivamente realizada a adição apenas após o commit
        db.session.commit() #Realizaria a mudança efetivamente no database
        return jsonify({"message": "Product added successfully"})
    return jsonify({"message": "Invalid product data"}), 400 #Método da biblioteca Flask para retornar como JSON
#Definido que caso saia do if, retornaria que os dados do produto está inválido, Ex: sem o price. Além disso, é necessário declarar o código de erro (400 no caso).

@app.route('/api/products/delete/<int:product_id>', methods=["DELETE"]) #Seria com o <> que conseguimos receber parâmetros, nesse caso para realizar a exclusão do produto.
@login_required
def delete_product(product_id): #Neste caso, irá receber essa informação do product_id.
    #Necessário recuperar o produto da base de dados
    #Verificar o produto
    #Caso exista, excluir da base de dados
    #Caso não, retornar a mensagem 404 not found
    product = Product.query.get(product_id) #Recuperaria o produto, pesquisando através do query e resgatando através do método get
    if product: #Nesse caso, o Python já entenderia que seria necessário verificar se possui algum valor válido no database
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"})
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products/<int:product_id>', methods=["GET"])
def product_details_get(product_id):
    product = Product.query.get(product_id)
    if product:
        return jsonify({
            "id": product.id, 
            "name": product.name, 
            "price": product.price, 
            "description": product.description
        })
    return jsonify({"message": "Product not found"}), 404

@app.route('/api/products/update/<int:product_id>', methods=["PUT"])
@login_required
def update_products(product_id):
    product = Product.query.get(product_id) #Retorn seria baseado no product id que foi dado como parâmetro
    if not product: #Nesse caso estaria negando o produto, logo caso não tenha tal produto no database irá retornar 404 Not found
        return jsonify({"message": "Product not found"}), 404
    
    data = request.json
    if 'name' in data:
        product.name = data['name']

    if 'price' in data:
        product.price = data['price']

    if 'description' in data:
        product.description = data['description']

    db.session.commit() #Necessário apenas o commit para gravar no banco, pois o mesmo já estaria cadastrado no database
    return jsonify({"message": "Product updated succesfully"})

@app.route('/api/products', methods=['GET']) #Rota para verificar os produtos que possui listados
def get_products():
    products = Product.query.all() #Já aqui, retornaria todos os produtos cadastrados
    product_list = [] #Criada uma lista vazia para que seja possível apresentar todos os produtos cadastrados
    for product in products: #For para percorrer por todos os produtos, criada a variavel product_data para possuir o que o produto tem
        product_data = {
            "id": product.id, 
            "name": product.name, 
            "price": product.price #Não é adicionada na description para esse caso, para o usuário precisar utilzar a rota de detalhes
        }
        product_list.append(product_data) #Append é um método que recebe valores para adicionar na lista.
    return jsonify(product_list) #Somente agora é possível retornar a lista, pois estaria passando por todos os produtos
#Caso fosse realizado apenas um return do product_data, sem o For, retornaria apenas o primeiro produto.


#Rotas: Definição de uma rota raiz, ou seja, uma página inicial e também uma função que será executada a partir de uma requisição
#Para definir uma rota, é sempre utilizado o @ e o método "route". A raiz por padrão seria uma /, basicamente a página inicial
@app.route('/')
def hello_world(): #Aqui será definido a função dessa rota, no caso o Hello World
    return 'Hello World'

if __name__ == "__main__": #Necessário verificar se o arquivo está sendo executado diretamente
    app.run(debug=True) #Utilizado para realizar a depuração, ser possível requisitar. Geralmente é acompanhado de uma condição