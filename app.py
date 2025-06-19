#Importação de bibliotecas
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS #Permite com que a API aceite requisições vindas de outros domínios

#app seria uma váriavel que irá receber uma instância da classe Flask
#Dentro do parentêses foi passado uma variável, cujo nome é "name"
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ecommerce.db' #Linha de configuração do banco de dados

db = SQLAlchemy(app) #Essa linha seria para a conexão com o banco de dados passando o parâmetro do app Flask
CORS(app)

#Modelagem 
#Para realizar a modelagem do database seria necessário definir uma classe, nesse caso a primeira classe seria de produto
class Product(db.Model): #Model vai servir de molde para a classe produto
    id = db.Column(db.Integer, primary_key=True) #ID do tipo inteiro (Integer), e uma chave primária para não ser repetido.
    name = db.Column(db.String(120), nullable=False) #Definimos a string, quantidade de dados e o mesmo não pode ser nulo (nullable)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=True)#.Text não teria limitação de caracteres igual o string, opcional.


@app.route('/api/products/add', methods=["POST"]) #Na documentação, foi definido que o modelo de adicionar seria apenas com o método POST
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