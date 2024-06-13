from telebot import TeleBot, types
import os
from dotenv import load_dotenv
import requests
import sqlite3
from datetime import datetime, timedelta
import time
import threading

load_dotenv()

bot = TeleBot(str(os.getenv('BOT_API')))
PRIVATE_CHANNEL_ID = os.getenv('PRIVATE_CHANNEL_ID')
DB_PATH = 'subscriptions.db'


def init_db():
    print("Inicializando banco de dados")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            user_id INTEGER,
            channel_id TEXT,
            start_date TEXT,
            end_date TEXT,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            chat_id INTEGER PRIMARY KEY,
            email TEXT,
            purchased INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()
    print("Banco de dados inicializado")


def update_interaction(chat_id, email=None, purchased=None):
    print(f"Atualizando interação: chat_id={chat_id}, email={email}, purchased={purchased}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    if email is not None:
        cursor.execute("""
            INSERT INTO interactions (chat_id, email) VALUES (?, ?)
            ON CONFLICT(chat_id) DO UPDATE SET email=excluded.email
        """, (chat_id, email))
    if purchased is not None:
        cursor.execute("""
            UPDATE interactions SET purchased = ? WHERE chat_id = ?
        """, (purchased, chat_id))
    conn.commit()
    conn.close()
    print("Interação atualizada")


def add_subscription(user_id, channel_id, duration_days, email):
    print(
        f"Adicionando assinatura: user_id={user_id}, channel_id={channel_id}, duration_days={duration_days}, email={email}")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    start_date = datetime.now()
    end_date = start_date + timedelta(days=duration_days)
    cursor.execute("""
        INSERT INTO subscriptions (user_id, channel_id, start_date, end_date, email)
        VALUES (?, ?, ?, ?, ?)
    """, (user_id, channel_id, start_date.isoformat(), end_date.isoformat(), email))
    conn.commit()
    conn.close()
    print("Assinatura adicionada")


def remove_expired_subscriptions():
    while True:
        print("Verificando assinaturas expiradas")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT user_id FROM subscriptions WHERE end_date <= ?
        """, (datetime.now().isoformat(),))
        expired_users = cursor.fetchall()
        for user_id in expired_users:
            try:
                bot.ban_chat_member(PRIVATE_CHANNEL_ID, user_id[0])
                bot.send_message(user_id[0], "Sua assinatura expirou e você foi removido do canal privado.")
                print(f"Usuário {user_id[0]} removido do canal privado")
            except Exception as e:
                print(f"Erro ao remover usuário {user_id[0]} do canal: {e}")
            cursor.execute("""
                DELETE FROM subscriptions WHERE user_id = ?
            """, (user_id[0],))
        conn.commit()
        conn.close()
        print("Verificação de assinaturas expiradas concluída")
        time.sleep(3600)  # Verifica a cada hora


@bot.message_handler(commands=['start'])
def start(message):
    print("Comando /start recebido")
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Plano 1 - 1 dia - R$5", callback_data='plano_1_1')
    button2 = types.InlineKeyboardButton("Plano 2 - 1 semana - R$10", callback_data='plano_2_7')
    button3 = types.InlineKeyboardButton("Plano 3 - 1 mês - R$35", callback_data='plano_3_30')
    button4 = types.InlineKeyboardButton("Plano 4 - 3 meses - R$100", callback_data='plano_4_90')
    button5 = types.InlineKeyboardButton("Plano 5 - 12 meses - R$500", callback_data='plano_5_365')
    markup.add(button1)
    markup.add(button2)
    markup.add(button3)
    markup.add(button4)
    markup.add(button5)
    bot.send_message(message.chat.id, "Escolha um plano:", reply_markup=markup)
    update_interaction(message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith('plano_'))
def handle_query(call):
    print(f"handle_query callback chamado: {call.data}")
    plan_data = call.data.split('_')
    print(f"Plan data split: {plan_data}")  # Debug
    plan_id = plan_data[1]
    duration_days = int(plan_data[2])

    if plan_id == '1':
        price = 5.0
        description = "Plano 1 - 1 dia"
    elif plan_id == '2':
        price = 10.0
        description = "Plano 2 - 1 semana"
    elif plan_id == '3':
        price = 35.0
        description = "Plano 3 - 1 mês"
    elif plan_id == '4':
        price = 100.0
        description = "Plano 4 - 3 meses"
    elif plan_id == '5':
        price = 500.0
        description = "Plano 5 - 12 meses"
    else:
        return

    # Solicitar email antes de gerar o código PIX
    msg = bot.send_message(call.message.chat.id,
                           "Por favor, insira seu email. Não se preocupe, não enviaremos nenhum email.")
    bot.register_next_step_handler(msg,
                                   lambda m: handle_email(m, call.message.chat.id, price, description, duration_days))


def handle_email(message, chat_id, price, description, duration_days):
    email = message.text
    print(f"Email recebido: {email}")
    update_interaction(chat_id, email=email)
    generate_payment(chat_id, price, description, duration_days)


def generate_payment(chat_id, price, description, duration_days):
    url = "http://127.0.0.1:8000/get_payment"
    payload = {
        "price": price,
        "description": description,
        "chat_id": chat_id
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
            bot.send_message(chat_id, f"Código PIX para pagamento:\n{pix_code}")

            # Adiciona botão para confirmar o pagamento
            markup = types.InlineKeyboardMarkup()
            confirm_button = types.InlineKeyboardButton("Confirmar Pagamento",
                                                        callback_data=f'confirm_payment_{transaction_id}_{duration_days}')
            markup.add(confirm_button)
            bot.send_message(chat_id, "Clique no botão abaixo para confirmar o pagamento:", reply_markup=markup)
            print("Botão de confirmação adicionado")  # Debug
        else:
            bot.send_message(chat_id, "Erro ao gerar o código de pagamento. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Exception occurred during generate_payment: {e}")  # Debug
        bot.send_message(chat_id, "Ocorreu um erro ao gerar o código de pagamento. Tente novamente mais tarde.")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_payment_'))
def confirm_payment(call):
    print("confirm_payment callback chamado")  # Debug
    try:
        print(f"callback_data: {call.data}")  # Debug
        parts = call.data.split('_')
        transaction_id = parts[2]
        duration_days = int(parts[3])
    except ValueError as e:
        print(f"Erro ao dividir a callback_data: {e}")  # Debug
        bot.send_message(call.message.chat.id, "Erro ao confirmar pagamento. Tente novamente mais tarde.")
        return

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
                add_user_to_channel(call.message.chat.id, duration_days)
                update_interaction(call.message.chat.id, purchased=1)
            elif data['status'] == 'pending':
                bot.send_message(call.message.chat.id, "Pagamento pendente. Por favor, aguarde a confirmação.")
            else:
                bot.send_message(call.message.chat.id,
                                 f"Status do pagamento: {data.get('status_detail', 'desconhecido')}")
        else:
            print(f"Erro na verificação do pagamento: {response.status_code} - {response.text}")  # Debug
            bot.send_message(call.message.chat.id, "Erro ao verificar o pagamento. Tente novamente mais tarde.")
    except Exception as e:
        print(f"Exception occurred during confirm_payment: {e}")  # Debug
        bot.send_message(call.message.chat.id, "Ocorreu um erro ao verificar o pagamento. Tente novamente mais tarde.")


def add_user_to_channel(user_id, duration_days):
    print(f"Adicionando usuário ao canal: user_id={user_id}, duration_days={duration_days}")
    try:
        bot.unban_chat_member(PRIVATE_CHANNEL_ID, user_id)  # Unban to add back to channel
        invite_link = bot.export_chat_invite_link(PRIVATE_CHANNEL_ID)
        bot.send_message(user_id, f"Você foi adicionado ao canal privado. Clique no link para entrar: {invite_link}")
        add_subscription(user_id, PRIVATE_CHANNEL_ID, duration_days, None)
    except Exception as e:
        print(f"Exception occurred while adding user to channel: {e}")


if __name__ == "__main__":
    init_db()
    threading.Thread(target=remove_expired_subscriptions).start()
    bot.polling()
