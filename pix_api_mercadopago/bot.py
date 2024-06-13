from telebot import TeleBot, types
import os
from dotenv import load_dotenv
import requests

load_dotenv()

bot = TeleBot(str(os.getenv('BOT_API')))

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Plano 1 - R$1", callback_data='plano_1')
    button2 = types.InlineKeyboardButton("Plano 2 - R$2", callback_data='plano_2')
    button3 = types.InlineKeyboardButton("Plano 3 - R$3", callback_data='plano_3')
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    bot.send_message(message.chat.id, "Escolha um plano:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('plano_'))
def handle_query(call):
    print("handle_query callback chamado")  # Debug
    if call.data == 'plano_1':
        price = 1.0
        description = "Plano 1"
    elif call.data == 'plano_2':
        price = 2.0
        description = "Plano 2"
    elif call.data == 'plano_3':
        price = 3.0
        description = "Plano 3"
    else:
        return

    generate_payment(call.message, price, description)

def generate_payment(message, price, description):
    url = "http://127.0.0.1:8000/get_payment"
    payload = {
        "price": price,
        "description": description,
        "chat_id": message.chat.id
    }
    headers = {
        "Content-Type": "application/json"
    }
    print(f"Enviando requisição para {url} com payload: {payload}")  # Debug
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Resposta recebida: {response.status_code} - {response.text}")  # Debug
        if response.status_code == 200:
            data = response.json()
            pix_code = data['clipboard']
            transaction_id = data['transaction_id']
            bot.send_message(message.chat.id, f"Código PIX para pagamento:\n")
            bot.send_message(message.chat.id, f"{pix_code}")

            # Adiciona botão para confirmar o pagamento
            markup = types.InlineKeyboardMarkup()
            confirm_button = types.InlineKeyboardButton("Confirmar Pagamento",
                                                        callback_data=f'confirm_payment_{transaction_id}')
            markup.add(confirm_button)
            bot.send_message(message.chat.id, "Clique no botão abaixo para confirmar o pagamento:", reply_markup=markup)
            print("Botão de confirmação adicionado")  # Debug
        else:
            bot.send_message(message.chat.id, "Erro ao gerar o código de pagamento. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Exception occurred during generate_payment: {e}")  # Debug
        bot.send_message(message.chat.id, "Ocorreu um erro ao gerar o código de pagamento. Tente novamente mais tarde.")

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_payment_'))
def confirm_payment(call):
    print("confirm_payment callback chamado")  # Debug
    payment_id = call.data.split('_')[-1]
    url = "http://127.0.0.1:8000/verify_payment"
    payload = {"chat_id": call.message.chat.id}
    headers = {"Content-Type": "application/json"}
    print(f"Enviando requisição para {url} com payload: {payload}")  # Debug
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Resposta recebida: {response.status_code} - {response.text}")  # Debug
        if response.status_code == 200:
            data = response.json()
            print(f"Resposta do servidor: {data}")  # Debug
            if data['status'] == 'approved':
                bot.send_message(call.message.chat.id, "Pagamento confirmado com sucesso!")
            elif data['status'] == 'pending':
                bot.send_message(call.message.chat.id, "Pagamento pendente. Por favor, aguarde a confirmação.")
            else:
                bot.send_message(call.message.chat.id, f"Status do pagamento: {data.get('status_detail', 'desconhecido')}")
        else:
            print(f"Erro na verificação do pagamento: {response.status_code} - {response.text}")  # Debug
            bot.send_message(call.message.chat.id, "Erro ao verificar o pagamento. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Exception occurred during confirm_payment: {e}")  # Debug
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao verificar o pagamento. Tente novamente mais tarde.")

if __name__ == "__main__":
    bot.polling()
