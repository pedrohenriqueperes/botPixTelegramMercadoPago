import mercadopago
import helpers

credentials = helpers.get_credentials()
transaction_store = {}  # Usar um dicionário simples para armazenamento em memória (substitua por um banco de dados em produção)

def get_payment(price, description):
    sdk = mercadopago.SDK(credentials['access_token'])
    payment_data = {
        "transaction_amount": float(price),
        "description": str(description),
        "payment_method_id": "pix",
        "payer": {
            "email": "test@test.com",
            "first_name": "User",
            "last_name": "Example",
            "identification": {
                "type": "CPF",
                "number": ""
            },
            "address": {
                "zip_code": "06233-200",
                "street_name": "Av. das Nações Unidas",
                "street_number": "3003",
                "neighborhood": "Bonfim",
                "city": "Osasco",
                "federal_unit": "SP"
            }
        }
    }
    payment_response = sdk.payment().create(payment_data)
    payment = payment_response["response"]
    data = payment['point_of_interaction']['transaction_data']
    return {'clipboard': str(data['qr_code']), 'qrcode': 'data:image/jpeg;base64,{}'.format(data['qr_code_base64']), 'id': payment['id']}

def verify_payment(payment_id):
    sdk = mercadopago.SDK(credentials['access_token'])
    payment_response = sdk.payment().get(int(payment_id))
    payment = payment_response["response"]
    status = payment['status']
    detail = payment['status_detail']
    return {'id': payment_id, 'status': status, 'status_detail': detail}

def store_transaction_id(chat_id, transaction_id):
    transaction_store[chat_id] = transaction_id

def get_transaction_id(chat_id):
    return transaction_store.get(chat_id)
