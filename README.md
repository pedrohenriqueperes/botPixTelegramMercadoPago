# Bot de Telegram com Pagamentos PIX e Sistema de Assinaturas

Este é um bot do Telegram que oferece um sistema de assinaturas com pagamentos via PIX, usando a API do MercadoPago para processamento de pagamentos. O bot permite que usuários escolham diferentes planos de assinatura, realizem pagamentos via PIX e ganhem acesso a um canal privado do Telegram.

## Características

- Sistema de assinaturas com planos personalizáveis
- Integração com pagamentos PIX via MercadoPago
- Gerenciamento automático de assinaturas expiradas
- Sistema de banco de dados SQLite para armazenamento de assinaturas
- API Flask para processamento de pagamentos
- Verificação automática de status de pagamento

## Estrutura do Projeto

```
├── .idea/
│   ├── inspectionProfiles/
│   ├── misc.xml
│   ├── modules.xml
│   ├── pix_MercadoPago.iml
│   └── vcs.xml
├── pix_api_mercadopago/
│   ├── __pycache__/
│   ├── app.py                 # API Flask para processamento de pagamentos
│   ├── bot.py                 # Bot principal do Telegram
│   ├── botAddChannel.py       # Gerenciamento de canais
│   ├── helpers.py            # Funções auxiliares
│   ├── payments.py           # Integração com MercadoPago
│   ├── pix.py               # Funções relacionadas ao PIX
│   ├── README.md
│   ├── requirements.txt     # Dependências do projeto
│   └── subscriptions.db     # Banco de dados SQLite
└── .gitignore
```

## Pré-requisitos

- Python 3.7+
- Conta no MercadoPago
- Bot do Telegram criado através do @BotFather
- Canal privado no Telegram

## Dependências

Instale as dependências do projeto executando:

```bash
pip install -r requirements.txt
```

O arquivo requirements.txt contém todas as bibliotecas necessárias para o funcionamento do projeto.

## Configuração

1. Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```env
BOT_API=seu_token_do_bot_telegram
PRIVATE_CHANNEL_ID=id_do_canal_privado
MERCADOPAGO_ACCESS_TOKEN=seu_token_mercadopago
```

2. Certifique-se de que o banco de dados SQLite seja inicializado na primeira execução.

## Módulos do Projeto

### app.py
API Flask que gerencia as requisições de pagamento e verificação. Responsável por:
- Processar requisições de pagamento
- Verificar status de transações
- Integração com serviço de pagamentos

### bot.py
Implementação principal do bot do Telegram, gerenciando:
- Interações com usuários
- Menu de planos
- Processo de pagamento
- Gerenciamento de assinaturas

### botAddChannel.py
Gerencia a adição e remoção de usuários em canais privados, incluindo:
- Adição de usuários após confirmação de pagamento
- Remoção de usuários com assinaturas expiradas
- Geração de links de convite

### helpers.py
Contém funções auxiliares utilizadas em todo o projeto.

### payments.py
Módulo responsável pela integração com a API do MercadoPago:
- Geração de pagamentos
- Verificação de status
- Processamento de callbacks

### pix.py
Implementação específica para geração e processamento de pagamentos PIX.

## Funcionalidades

### Configuração de Planos
O sistema permite configurar planos personalizados conforme sua necessidade. No arquivo `bot.py`, você pode definir os planos modificando o método `start`:

```python
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    # Exemplo de configuração de planos
    # Formato: ("Nome do Plano", preço, duração_em_dias)
    button1 = types.InlineKeyboardButton("Plano 1 - R$X", callback_data='plano_1_N')
    button2 = types.InlineKeyboardButton("Plano 2 - R$Y", callback_data='plano_2_N')
    # Adicione quantos planos desejar
    markup.add(button1)
    markup.add(button2)
```

O formato do `callback_data` segue o padrão: `plano_ID_DIAS`
- ID: identificador único do plano
- DIAS: duração da assinatura em dias

### Fluxo de Compra
1. Usuário inicia o bot com `/start`
2. Escolhe um dos planos configurados
3. Fornece email
4. Recebe código PIX para pagamento
5. Confirma pagamento através do botão
6. Recebe acesso ao canal privado após confirmação

### Sistema de Assinaturas
- Monitoramento automático de assinaturas expiradas
- Remoção automática de usuários do canal após expiração
- Notificação aos usuários sobre expiração

## API Endpoints

### GET /
- Retorna status da API
- Resposta: Mensagem confirmando que a API está funcionando

### POST /get_payment
- Gera código PIX para pagamento
- Parâmetros de entrada:
  ```json
  {
    "price": float,
    "description": string,
    "chat_id": integer
  }
  ```
- Resposta:
  ```json
  {
    "clipboard": string,
    "transaction_id": string
  }
  ```

### POST /verify_payment
- Verifica status do pagamento
- Parâmetros de entrada:
  ```json
  {
    "chat_id": integer
  }
  ```
- Resposta:
  ```json
  {
    "status": string,
    "status_detail": string
  }
  ```

## Banco de Dados

### Tabela subscriptions
- user_id: ID do usuário no Telegram
- channel_id: ID do canal privado
- start_date: Data de início da assinatura
- end_date: Data de término da assinatura
- email: Email do usuário

### Tabela interactions
- chat_id: ID do chat do Telegram
- email: Email do usuário
- purchased: Status da compra (0/1)

## Executando o Projeto

1. Certifique-se de que todas as dependências estão instaladas:
```bash
pip install -r requirements.txt
```

2. Inicie a API Flask:
```bash
python app.py
```

3. Em outro terminal, inicie o bot:
```bash
python bot.py
```

## Tratamento de Erros

O sistema inclui tratamento de erros para:
- Falhas de conexão com MercadoPago
- Timeout em pagamentos
- Erros de acesso ao canal
- Problemas de banco de dados

## Segurança

- Todas as transações são processadas pelo MercadoPago
- Dados sensíveis são armazenados de forma segura
- Verificação de pagamentos em duas etapas
- Proteção contra acessos não autorizados ao canal

## Contribuindo

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## Suporte

Para suporte e dúvidas, abra uma issue no repositório do projeto.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.