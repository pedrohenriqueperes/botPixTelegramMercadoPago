from flask import Flask, jsonify, make_response, request
import payments
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return 'API do MercadoPago está funcionando!'

@app.route('/get_payment', methods=['POST'])
def get_payment_route():
    if request.content_type != 'application/json':
        return make_response('Content-Type must be application/json', 400)
    data = request.json
    print(f"Requisição recebida em /get_payment: {data}")  # Debug para verificar a requisição recebida
    try:
        if data['price'] and data['description']:
            res = payments.get_payment(data['price'], data['description'])
            res['transaction_id'] = res['id']  # Adicione esta linha para incluir o ID da transação na resposta
            payments.store_transaction_id(data['chat_id'], res['id'])  # Armazena o ID da transação
            print(f"Resposta gerada em /get_payment: {res}")  # Debug para verificar a resposta gerada
            return jsonify(res)
    except Exception as e:
        print(f"Erro em /get_payment: {e}")  # Debug para verificar erros
        return make_response('Bad Request: {}'.format(e), 400)

@app.route('/verify_payment', methods=['POST'])
def verify_payment_route():
    if request.content_type != 'application/json':
        return make_response('Content-Type must be application/json', 400)
    data = request.json
    print(f"Requisição recebida em /verify_payment: {data}")  # Debug para verificar a requisição recebida
    try:
        chat_id = data['chat_id']
        transaction_id = payments.get_transaction_id(chat_id)
        if not transaction_id:
            print(f"Transaction ID not found for chat_id: {chat_id}")  # Debug para verificar a falta do ID da transação
            return make_response('Transaction ID not found for given chat_id', 404)
        payment_status = payments.verify_payment(transaction_id)
        print(f"Status do pagamento: {payment_status}")  # Debug para verificar o status do pagamento
        return jsonify({"status": payment_status['status'], "status_detail": payment_status.get('status_detail', 'desconhecido')})
    except Exception as e:
        print(f"Erro em /verify_payment: {e}")  # Debug para verificar erros
        return make_response('Bad Request: {}'.format(e), 400)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
