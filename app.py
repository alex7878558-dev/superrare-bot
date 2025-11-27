import os
import requests
import datetime
import time
import threading
import random
import json
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)

# ==================== КОНФИГ ====================
BOT_TOKEN = "8583960432:AAFnqFYa9iHn-08KM1HQnJpLG3qQ3zUdPdY"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# Инициализация Firebase
try:
    # Создаем credentials из переменных окружения
    firebase_config = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.environ.get('FIREBASE_CLIENT_EMAIL', '').replace('@', '%40')}",
        "universe_domain": "googleapis.com"
    }
    
    # Проверяем что все переменные есть
    if not all([firebase_config['project_id'], firebase_config['private_key'], firebase_config['client_email']]):
        raise Exception("Не все Firebase переменные окружения установлены")
    
    cred = credentials.Certificate(firebase_config)
    firebase_admin.initialize_app(cred)
    db = firestore.client()
    print("✅ Firebase инициализирован!")
except Exception as e:
    print(f"❌ Ошибка Firebase: {e}")
    db = None

# ==================== ФУНКЦИЯ САМОПРОБУЖДЕНИЯ ====================
def keep_alive():
    """Функция для поддержания бота активным на Render"""
    while True:
        try:
            app_url = os.environ.get('RENDER_EXTERNAL_URL')
            if app_url:
                response = requests.get(f"{app_url}/", timeout=10)
                print(f"✅ Самопробуждение: {response.status_code} - {datetime.datetime.now().strftime('%H:%M:%S')}")
        except Exception as e:
            print(f"❌ Ошибка самопробуждения: {e}")
        time.sleep(600)

# Запускаем самопробуждение в отдельном потоке
if os.environ.get('RENDER'):
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()

# ==================== ТЕКСТЫ ====================
TEXTS = {
    "ru": {
        "choose_currency": "Выберите валюту",
        "main_menu": "Главное меню",
        "personal_account": "Личный кабинет",
        "nft": "NFT",
        "info": "Инфо",
        "support": "Тех. Поддержка",
        "in_development": "Раздел в разработке",
        "deposit_methods": "Выберите удобный для вас метод пополнения.",
        "enter_amount": "Введите сумму пополнения от {min_amount} {currency}",
        "payment_created": "Создана заявка на оплату\n\nДля пополнения переведите указанную сумму по номеру карты.\n\n---\n\n✅ Карта: {card_number}\n✅ Сумма: {amount} {currency}\n\n---\n\n**Реквизиты действительны 10 минут.**",
        "send_receipt": "Просим направить фотографию квитанции об оплате.\n\nОбращаем внимание: отправка допускается исключительно в переписке с ботом.",
        "payment_cancelled": "Заявка на оплату отменена.",
        "payment_received": "✅ Спасибо! Ваша заявка принята в обработку. Ожидайте подтверждения оплаты.",
        "withdrawal_minimum": "Минимальная сумма для вывода: {min_withdrawal} {currency}\n\nВаш баланс: {balance} {currency}, {message}",
        "enter_withdrawal_amount": "Введите сумму для вывода (от {min_withdrawal} {currency}):",
        "insufficient_funds": "недостаточно средств для вывода!",
        "sufficient_funds": "можно вывести средства",
        "enter_card_details": "Введите номер банковской карты для получения средств:",
        "withdrawal_success": "✅ Заявка на вывод создана!\n\n💳 Карта: {card_number}\n💵 Сумма: {amount} {currency}\n\n⏰ Деньги поступят в течение 24 часов.\n\nСпасибо, что пользуетесь нашим сервисом!",
        "invalid_card": "❌ Неверный номер карты. Пожалуйста, введите корректный номер банковской карты:",
        "invalid_withdrawal_amount": "❌ Неверная сумма. Минимальная сумма для вывода: {min_withdrawal} {currency}. Максимальная: {balance} {currency}",
        "personal_account_text": """**SuperRare | NFT Market**

---

## Личный кабинет

Баланс: {balance} {currency}
На выводе: {withdrawal_balance} {currency}

Оборот транзакций: {turnover} {currency}

Верификация: {verification_status}
Ваш айди: {user_id}

Дата и время: {current_time}
---""",
        "settings": "⚙️ Настройки",
        "settings_text": """**SuperRare | NFT Market**

---

## Настройки

Язык: {language}
Валюта: {currency}

---""",
        "language": "Язык",
        "currency_setting": "Валюта",
        "back": "Вернуться"
    },
    "en": {
        "choose_currency": "Choose currency",
        "main_menu": "Main menu",
        "personal_account": "Personal account",
        "nft": "NFT",
        "info": "Info",
        "support": "Support",
        "in_development": "Section in development",
        "deposit_methods": "Choose a convenient deposit method for you.",
        "enter_amount": "Enter deposit amount from {min_amount} {currency}",
        "payment_created": "Payment request created\n\nTo top up, transfer the specified amount to the card number.\n\n---\n\n✅ Card: {card_number}\n✅ Amount: {amount} {currency}\n\n---\n\n**Details are valid for 10 minutes.**",
        "send_receipt": "Please send a photo of the payment receipt.\n\nPlease note: sending is allowed only in correspondence with the bot.",
        "payment_cancelled": "Payment request cancelled.",
        "payment_received": "✅ Thank you! Your application has been accepted for processing. Please wait for payment confirmation.",
        "withdrawal_minimum": "Minimum withdrawal amount: {min_withdrawal} {currency}\n\nYour balance: {balance} {currency}, {message}",
        "enter_withdrawal_amount": "Enter withdrawal amount (from {min_withdrawal} {currency}):",
        "insufficient_funds": "insufficient funds for withdrawal!",
        "sufficient_funds": "you can withdraw funds",
        "enter_card_details": "Enter bank card number to receive funds:",
        "withdrawal_success": "✅ Withdrawal request created!\n\n💳 Card: {card_number}\n💵 Amount: {amount} {currency}\n\n⏰ Money will arrive within 24 hours.\n\nThank you for using our service!",
        "invalid_card": "❌ Invalid card number. Please enter correct bank card number:",
        "invalid_withdrawal_amount": "❌ Invalid amount. Minimum withdrawal amount: {min_withdrawal} {currency}. Maximum: {balance} {currency}",
        "personal_account_text": """**SuperRare | NFT Market**

---

## Personal Account

Balance: {balance} {currency}
On withdrawal: {withdrawal_balance} {currency}

Transaction turnover: {turnover} {currency}

Verification: {verification_status}
Your ID: {user_id}

Date and time: {current_time}
---""",
        "settings": "⚙️ Settings",
        "settings_text": """**SuperRare | NFT Market**

---

## Settings

Language: {language}
Currency: {currency}

---""",
        "language": "Language",
        "currency_setting": "Currency",
        "back": "Back"
    }
}

# ==================== КЛАВИАТУРЫ ====================
def agreement_keyboard(lang='ru'):
    text = "✅ Принять" if lang == 'ru' else "✅ Accept"
    return {"keyboard": [[{"text": text}]], "resize_keyboard": True}

def language_keyboard():
    return {"keyboard": [[{"text": "Русский"}], [{"text": "English"}]], "resize_keyboard": True}

def currency_keyboard():
    return {"keyboard": [[{"text": "RUB"}, {"text": "UAH"}, {"text": "KZT"}], [{"text": "BYN"}, {"text": "EUR"}, {"text": "USD"}]], "resize_keyboard": True}

def main_menu_keyboard(lang='ru'):
    personal_text = TEXTS[lang]["personal_account"]
    nft_text = TEXTS[lang]["nft"]
    info_text = TEXTS[lang]["info"]
    support_text = TEXTS[lang]["support"]
    return {"keyboard": [[{"text": "📊 " + personal_text}], [{"text": "💎 " + nft_text}], [{"text": "ℹ️ " + info_text}], [{"text": "🆘 " + support_text}]], "resize_keyboard": True}

def personal_account_keyboard(lang='ru'):
    deposit_text = "Пополнить" if lang == 'ru' else "Deposit"
    withdraw_text = "Вывести" if lang == 'ru' else "Withdraw"
    transactions_text = "Транзакции" if lang == 'ru' else "Transactions"
    verification_text = "Верификация" if lang == 'ru' else "Verification"
    favorites_text = "Избранное" if lang == 'ru' else "Favorites"
    my_nft_text = "Мои NFT" if lang == 'ru' else "My NFT"
    create_nft_text = "Создать NFT" if lang == 'ru' else "Create NFT"
    settings_text = TEXTS[lang]["settings"]
    menu_text = "Меню" if lang == 'ru' else "Menu"
    return {"keyboard": [[{"text": deposit_text}, {"text": withdraw_text}], [{"text": transactions_text}, {"text": verification_text}], [{"text": favorites_text}, {"text": my_nft_text}], [{"text": create_nft_text}], [{"text": settings_text}, {"text": menu_text}]], "resize_keyboard": True}

def settings_keyboard(lang='ru'):
    language_text = TEXTS[lang]["language"]
    currency_text = TEXTS[lang]["currency_setting"]
    back_text = TEXTS[lang]["back"]
    return {"keyboard": [[{"text": language_text}], [{"text": currency_text}], [{"text": back_text}]], "resize_keyboard": True}

def deposit_methods_keyboard(lang='ru'):
    bank_card_text = "Пополнить через банковскую карту" if lang == 'ru' else "Deposit by bank card"
    promocode_text = "Промокод" if lang == 'ru' else "Promocode"
    back_text = "Назад" if lang == 'ru' else "Back"
    return {"keyboard": [[{"text": bank_card_text}], [{"text": promocode_text}], [{"text": back_text}]], "resize_keyboard": True}

def payment_confirmation_keyboard(lang='ru'):
    paid_text = "Я оплатил(а) ✅" if lang == 'ru' else "I paid ✅"
    cancel_text = "Отменить" if lang == 'ru' else "Cancel"
    return {"keyboard": [[{"text": paid_text}], [{"text": cancel_text}]], "resize_keyboard": True}

def withdrawal_cancel_keyboard(lang='ru'):
    cancel_text = "Отменить" if lang == 'ru' else "Cancel"
    return {"keyboard": [[{"text": cancel_text}]], "resize_keyboard": True}

def back_keyboard(lang='ru'):
    back_text = TEXTS[lang]["back"]
    return {"keyboard": [[{"text": back_text}]], "resize_keyboard": True}

# ==================== ФУНКЦИИ FIREBASE ====================
def get_user_data(user_id):
    """Получает данные пользователя из Firestore"""
    if not db:
        return None
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        print(f"❌ Ошибка получения пользователя {user_id}: {e}")
        return None

def create_user(user_id, user_data):
    """Создает нового пользователя в Firestore"""
    if not db:
        return False
    try:
        user_data['user_id'] = user_id
        user_data['created_at'] = firestore.SERVER_TIMESTAMP
        user_data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref = db.collection('users').document(str(user_id))
        doc_ref.set(user_data)
        return True
    except Exception as e:
        print(f"❌ Ошибка создания пользователя {user_id}: {e}")
        return False

def update_user_data(user_id, data):
    """Обновляет данные пользователя в Firestore"""
    if not db:
        return False
    try:
        data['updated_at'] = firestore.SERVER_TIMESTAMP
        doc_ref = db.collection('users').document(str(user_id))
        doc_ref.set(data, merge=True)
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления пользователя {user_id}: {e}")
        return False

def update_user_field(user_id, field, value):
    """Обновляет конкретное поле пользователя"""
    if not db:
        return False
    try:
        doc_ref = db.collection('users').document(str(user_id))
        doc_ref.update({
            field: value,
            'updated_at': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"❌ Ошибка обновления поля {field} для {user_id}: {e}")
        return False

def create_payment(user_id, amount, currency):
    """Создает запись о платеже"""
    if not db:
        return None, None
    try:
        card_number = '2200' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
        payment_data = {
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'card_number': card_number,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = db.collection('payments').document()
        doc_ref.set(payment_data)
        return doc_ref.id, card_number
    except Exception as e:
        print(f"❌ Ошибка создания платежа: {e}")
        return None, None

def create_withdrawal(user_id, amount, currency, card_number):
    """Создает запись о выводе средств"""
    if not db:
        return None
    try:
        withdrawal_data = {
            'user_id': user_id,
            'amount': amount,
            'currency': currency,
            'card_number': card_number,
            'status': 'pending',
            'created_at': firestore.SERVER_TIMESTAMP
        }
        doc_ref = db.collection('withdrawals').document()
        doc_ref.set(withdrawal_data)
        return doc_ref.id
    except Exception as e:
        print(f"❌ Ошибка создания вывода: {e}")
        return None

def get_last_payment(user_id):
    """Получает последний платеж пользователя"""
    if not db:
        return None
    try:
        payments_ref = db.collection('payments').where('user_id', '==', user_id).order_by('created_at', direction=firestore.Query.DESCENDING).limit(1)
        docs = payments_ref.stream()
        for doc in docs:
            payment = doc.to_dict()
            payment['id'] = doc.id
            return payment
        return None
    except Exception as e:
        print(f"❌ Ошибка получения платежа: {e}")
        return None

def save_temporary_data(user_id, key, value):
    """Сохраняет временные данные"""
    if not db:
        return False
    try:
        doc_ref = db.collection('temporary_data').document(f"{user_id}_{key}")
        doc_ref.set({
            'user_id': user_id,
            'key': key,
            'value': value,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения временных данных: {e}")
        return False

def get_temporary_data(user_id, key):
    """Получает временные данные"""
    if not db:
        return None
    try:
        doc_ref = db.collection('temporary_data').document(f"{user_id}_{key}")
        doc = doc_ref.get()
        if doc.exists:
            return doc.to_dict().get('value')
        return None
    except Exception as e:
        print(f"❌ Ошибка получения временных данных: {e}")
        return None

def delete_temporary_data(user_id, key):
    """Удаляет временные данные"""
    if not db:
        return False
    try:
        doc_ref = db.collection('temporary_data').document(f"{user_id}_{key}")
        doc_ref.delete()
        return True
    except Exception as e:
        print(f"❌ Ошибка удаления временных данных: {e}")
        return False

def is_valid_card(card_number):
    """Проверяет номер карты"""
    card_number = card_number.replace(' ', '')
    return card_number.isdigit() and 16 <= len(card_number) <= 19

# ==================== ОТПРАВКА СООБЩЕНИЙ ====================
def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    if parse_mode: data["parse_mode"] = parse_mode
    if reply_markup: data["reply_markup"] = reply_markup

    for attempt in range(3):
        try:
            response = requests.post(url, json=data, timeout=10)
            if response.status_code == 200: return response.json()
        except Exception as e:
            print(f"❌ Ошибка отправки: {e}")
        time.sleep(2)
    return None

# ==================== WEBHOOK ОБРАБОТЧИКИ ====================
@app.route('/')
def home():
    return "🤖 Бот работает! " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@app.route('/db_status')
def db_status():
    try:
        if not db:
            return "❌ Firebase не инициализирован"
        
        # Проверяем количество пользователей
        users_ref = db.collection('users')
        users_count = len(list(users_ref.limit(100).stream()))
        
        status_info = {
            "status": "✅ Firebase Firestore работает",
            "total_users": users_count,
            "database": "Cloud Firestore"
        }
        
        return json.dumps(status_info, ensure_ascii=False, indent=2)
        
    except Exception as e:
        return f"❌ Ошибка БД: {str(e)}"

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        
        if 'message' in update:
            message = update['message']
            user_id = message["from"]["id"]
            text = message.get("text", "")
            username = message["from"].get("username", "")
            first_name = message["from"].get("first_name", "")
            
            # Проверяем, есть ли фото
            photo = message.get('photo')
            if photo:
                handle_photo(user_id, photo, message.get('caption', ''))
                return 'ok'

            user_data = get_user_data(user_id)

            if not user_data:
                # Создаем нового пользователя
                user_info = {
                    'username': username,
                    'full_name': first_name,
                    'language': 'ru',
                    'currency': 'RUB',
                    'balance': 0.0,
                    'withdrawal_balance': 0.0,
                    'turnover': 0.0,
                    'verified': False,
                    'agreed': False,
                    'state': 'agreement'
                }
                create_user(user_id, user_info)

                display_name = f"@{username}" if username else first_name
                agreement_text = f"Привет, **{display_name}!**\n\nПолитика и условия пользования данным ботом.\n\nСпасибо за понимание, Ваш **SuperRare | NFT Market**"
                send_message(user_id, agreement_text, agreement_keyboard())

            else:
                state = user_data.get('state', 'agreement')
                lang = user_data.get('language', 'ru')
                curr = user_data.get('currency', 'RUB')
                balance = user_data.get('balance', 0.0)

                # Обработка состояний
                if state == 'agreement':
                    accept_text = "✅ Принять" if lang == 'ru' else "✅ Accept"
                    if text == accept_text:
                        update_user_field(user_id, 'state', 'language')
                        send_message(user_id, "Выберите язык", language_keyboard())

                elif state == 'language':
                    if text == "Русский":
                        update_user_field(user_id, 'language', 'ru')
                        update_user_field(user_id, 'state', 'currency')
                        send_message(user_id, "Выберите валюту", currency_keyboard())
                    elif text == "English":
                        update_user_field(user_id, 'language', 'en')
                        update_user_field(user_id, 'state', 'currency')
                        send_message(user_id, "Choose currency", currency_keyboard())

                elif state == 'currency':
                    if text in ["RUB", "UAH", "KZT", "BYN", "EUR", "USD"]:
                        update_user_field(user_id, 'currency', text)
                        update_user_field(user_id, 'state', 'main_menu')
                        send_message(user_id, TEXTS[lang]["main_menu"], main_menu_keyboard(lang))

                elif state == 'main_menu':
                    text_obj = TEXTS[lang]
                    if text == "📊 " + text_obj["personal_account"]:
                        user_data = get_user_data(user_id)
                        if user_data:
                            balance = user_data.get('balance', 0.0)
                            withdrawal_balance = user_data.get('withdrawal_balance', 0.0)
                            turnover = user_data.get('turnover', 0.0)
                            verified = user_data.get('verified', False)
                            currency = user_data.get('currency', 'RUB')
                            
                            verification_status = "✅ Верифицирован" if verified else "💬 Не верифицирован"
                            if lang == 'en': verification_status = "✅ Verified" if verified else "💬 Not verified"
                            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                            account_text = text_obj["personal_account_text"].format(
                                balance=balance, withdrawal_balance=withdrawal_balance, turnover=turnover,
                                verification_status=verification_status, user_id=user_id, current_time=current_time, currency=currency
                            )
                            send_message(user_id, account_text, personal_account_keyboard(lang))
                            update_user_field(user_id, 'state', 'personal_account')

                    elif text in ["💎 " + text_obj["nft"], "ℹ️ " + text_obj["info"], "🆘 " + text_obj["support"]]:
                        send_message(user_id, text_obj["in_development"])

                elif state == 'personal_account':
                    text_obj = TEXTS[lang]
                    deposit_text = "Пополнить" if lang == 'ru' else "Deposit"
                    withdraw_text = "Вывести" if lang == 'ru' else "Withdraw"
                    transactions_text = "Транзакции" if lang == 'ru' else "Transactions"
                    verification_text = "Верификация" if lang == 'ru' else "Verification"
                    favorites_text = "Избранное" if lang == 'ru' else "Favorites"
                    my_nft_text = "Мои NFT" if lang == 'ru' else "My NFT"
                    create_nft_text = "Создать NFT" if lang == 'ru' else "Create NFT"
                    settings_text = text_obj["settings"]
                    menu_text = "Меню" if lang == 'ru' else "Menu"

                    if text == deposit_text:
                        update_user_field(user_id, 'state', 'deposit_methods')
                        send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))
                    elif text == withdraw_text:
                        min_withdrawal = 5000.0 if curr == 'RUB' else 100.0
                        user_balance = balance
                        
                        if user_balance >= min_withdrawal:
                            update_user_field(user_id, 'state', 'enter_withdrawal_amount')
                            send_message(user_id, text_obj["enter_withdrawal_amount"].format(min_withdrawal=min_withdrawal, currency=curr), withdrawal_cancel_keyboard(lang))
                        else:
                            message_text = text_obj["insufficient_funds"] if user_balance < min_withdrawal else text_obj["sufficient_funds"]
                            withdrawal_text = text_obj["withdrawal_minimum"].format(
                                min_withdrawal=min_withdrawal, 
                                balance=user_balance, 
                                currency=curr, 
                                message=message_text
                            )
                            send_message(user_id, withdrawal_text, personal_account_keyboard(lang))
                    
                    elif text in [transactions_text, verification_text, favorites_text, my_nft_text, create_nft_text]:
                        send_message(user_id, text_obj["in_development"])
                    elif text == settings_text:
                        user_data = get_user_data(user_id)
                        if user_data:
                            user_language = "Русский" if user_data.get('language') == 'ru' else "English"
                            user_currency = user_data.get('currency', 'RUB')
                            settings_message = text_obj["settings_text"].format(language=user_language, currency=user_currency)
                            send_message(user_id, settings_message, settings_keyboard(lang))
                            update_user_field(user_id, 'state', 'settings')
                    elif text == menu_text:
                        update_user_field(user_id, 'state', 'main_menu')
                        send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))

                elif state == 'settings':
                    text_obj = TEXTS[lang]
                    if text == text_obj["language"]:
                        update_user_field(user_id, 'state', 'change_language')
                        send_message(user_id, "Выберите язык:", language_keyboard())
                    elif text == text_obj["currency_setting"]:
                        update_user_field(user_id, 'state', 'change_currency')
                        send_message(user_id, "Выберите валюту:", currency_keyboard())
                    elif text == text_obj["back"]:
                        update_user_field(user_id, 'state', 'personal_account')
                        user_data = get_user_data(user_id)
                        if user_data:
                            balance = user_data.get('balance', 0.0)
                            withdrawal_balance = user_data.get('withdrawal_balance', 0.0)
                            turnover = user_data.get('turnover', 0.0)
                            verified = user_data.get('verified', False)
                            currency = user_data.get('currency', 'RUB')
                            verification_status = "✅ Верифицирован" if verified else "💬 Не верифицирован"
                            if lang == 'en': verification_status = "✅ Verified" if verified else "💬 Not verified"
                            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                            account_text = text_obj["personal_account_text"].format(
                                balance=balance, withdrawal_balance=withdrawal_balance, turnover=turnover,
                                verification_status=verification_status, user_id=user_id, current_time=current_time, currency=currency
                            )
                            send_message(user_id, account_text, personal_account_keyboard(lang))

                elif state == 'change_language':
                    if text == "Русский":
                        update_user_field(user_id, 'language', 'ru')
                        update_user_field(user_id, 'state', 'settings')
                        send_message(user_id, "Язык изменен на Русский", settings_keyboard('ru'))
                    elif text == "English":
                        update_user_field(user_id, 'language', 'en')
                        update_user_field(user_id, 'state', 'settings')
                        send_message(user_id, "Language changed to English", settings_keyboard('en'))

                elif state == 'change_currency':
                    if text in ["RUB", "UAH", "KZT", "BYN", "EUR", "USD"]:
                        update_user_field(user_id, 'currency', text)
                        update_user_field(user_id, 'state', 'settings')
                        user_data = get_user_data(user_id)
                        lang = user_data.get('language', 'ru')
                        currency_name = "Рубль" if text == "RUB" else text
                        if lang == 'en': currency_name = "Ruble" if text == "RUB" else text
                        send_message(user_id, f"Валюта изменена на {currency_name}", settings_keyboard(lang))

                elif state == 'deposit_methods':
                    text_obj = TEXTS[lang]
                    bank_card_text = "Пополнить через банковскую карту" if lang == 'ru' else "Deposit by bank card"
                    back_text = "Назад" if lang == 'ru' else "Back"

                    if text == bank_card_text:
                        update_user_field(user_id, 'state', 'enter_amount')
                        min_amount = 2500.0 if curr == 'RUB' else 50.0
                        send_message(user_id, text_obj["enter_amount"].format(min_amount=min_amount, currency=curr), back_keyboard(lang))
                    elif text == back_text:
                        update_user_field(user_id, 'state', 'personal_account')
                        send_message(user_id, TEXTS[lang]["personal_account"], personal_account_keyboard(lang))

                elif state == 'enter_amount':
                    text_obj = TEXTS[lang]
                    back_text = "Назад" if lang == 'ru' else "Back"

                    if text == back_text:
                        update_user_field(user_id, 'state', 'deposit_methods')
                        send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))
                    else:
                        try:
                            amount = float(text)
                            min_amount = 2500.0 if curr == 'RUB' else 50.0
                            if amount >= min_amount:
                                payment_id, card_number = create_payment(user_id, amount, curr)
                                payment_text = text_obj["payment_created"].format(card_number=card_number, amount=amount, currency=curr)
                                update_user_field(user_id, 'state', 'payment_confirmation')
                                send_message(user_id, payment_text, payment_confirmation_keyboard(lang))
                            else:
                                send_message(user_id, f"Минимальная сумма: {min_amount} {curr}")
                        except ValueError:
                            send_message(user_id, "Пожалуйста, введите число")

                elif state == 'payment_confirmation':
                    text_obj = TEXTS[lang]
                    paid_text = "Я оплатил(а) ✅" if lang == 'ru' else "I paid ✅"
                    cancel_text = "Отменить" if lang == 'ru' else "Cancel"

                    if text == paid_text:
                        update_user_field(user_id, 'state', 'waiting_receipt')
                        send_message(user_id, text_obj["send_receipt"])
                    elif text == cancel_text:
                        update_user_field(user_id, 'state', 'personal_account')
                        send_message(user_id, text_obj["payment_cancelled"], personal_account_keyboard(lang))

                elif state == 'waiting_receipt':
                    if text:
                        send_message(user_id, "Пожалуйста, отправьте фотографию квитанции об оплате")

                elif state == 'enter_withdrawal_amount':
                    text_obj = TEXTS[lang]
                    cancel_text = "Отменить" if lang == 'ru' else "Cancel"

                    if text == cancel_text:
                        update_user_field(user_id, 'state', 'personal_account')
                        send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                    else:
                        try:
                            amount = float(text)
                            min_withdrawal = 5000.0 if curr == 'RUB' else 100.0
                            user_balance = balance
                            
                            if amount >= min_withdrawal and amount <= user_balance:
                                save_temporary_data(user_id, 'withdrawal_amount', str(amount))
                                update_user_field(user_id, 'state', 'enter_withdrawal_card')
                                send_message(user_id, text_obj["enter_card_details"], withdrawal_cancel_keyboard(lang))
                            else:
                                send_message(user_id, text_obj["invalid_withdrawal_amount"].format(
                                    min_withdrawal=min_withdrawal, balance=user_balance, currency=curr
                                ), withdrawal_cancel_keyboard(lang))
                        except ValueError:
                            send_message(user_id, "Пожалуйста, введите число", withdrawal_cancel_keyboard(lang))

                elif state == 'enter_withdrawal_card':
                    text_obj = TEXTS[lang]
                    cancel_text = "Отменить" if lang == 'ru' else "Cancel"

                    if text == cancel_text:
                        update_user_field(user_id, 'state', 'personal_account')
                        send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                    else:
                        if is_valid_card(text):
                            amount_str = get_temporary_data(user_id, 'withdrawal_amount')
                            
                            if amount_str:
                                amount = float(amount_str)
                                withdrawal_id = create_withdrawal(user_id, amount, curr, text)
                                
                                # Обновляем баланс пользователя
                                new_balance = user_data.get('balance', 0.0) - amount
                                new_withdrawal_balance = user_data.get('withdrawal_balance', 0.0) + amount
                                
                                update_user_data(user_id, {
                                    'balance': new_balance,
                                    'withdrawal_balance': new_withdrawal_balance
                                })
                                
                                delete_temporary_data(user_id, 'withdrawal_amount')
                                
                                success_text = text_obj["withdrawal_success"].format(
                                    card_number=text, amount=amount, currency=curr
                                )
                                update_user_field(user_id, 'state', 'personal_account')
                                send_message(user_id, success_text, personal_account_keyboard(lang))
                            else:
                                send_message(user_id, "❌ Ошибка: не найдена информация о сумме вывода", personal_account_keyboard(lang))
                        else:
                            send_message(user_id, text_obj["invalid_card"], withdrawal_cancel_keyboard(lang))

                else:
                    update_user_field(user_id, 'state', 'main_menu')
                    send_message(user_id, TEXTS[lang]["main_menu"], main_menu_keyboard(lang))

        return 'ok'
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        return 'error', 500

def handle_photo(user_id, photo, caption=''):
    """Обработка фотографии квитанции"""
    try:
        user_data = get_user_data(user_id)
        if user_data:
            state = user_data.get('state', '')
            lang = user_data.get('language', 'ru')
            text_obj = TEXTS[lang]
            
            if state == 'waiting_receipt':
                last_payment = get_last_payment(user_id)
                if last_payment:
                    # Обновляем статус платежа
                    payment_ref = db.collection('payments').document(last_payment['id'])
                    payment_ref.update({'status': 'completed'})
                    
                    # Добавляем средства на баланс
                    amount = last_payment['amount']
                    new_balance = user_data.get('balance', 0.0) + amount
                    new_turnover = user_data.get('turnover', 0.0) + amount
                    
                    update_user_data(user_id, {
                        'balance': new_balance,
                        'turnover': new_turnover
                    })
                    
                    send_message(user_id, text_obj["payment_received"])
                    update_user_field(user_id, 'state', 'personal_account')
                    send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                else:
                    send_message(user_id, "Ошибка: не найдена информация о платеже")
            else:
                send_message(user_id, "Пожалуйста, следуйте инструкциям бота")
    except Exception as e:
        print(f"❌ Ошибка обработки фото: {e}")

def set_webhook():
    try:
        webhook_url = f"{os.environ.get('RENDER_EXTERNAL_URL')}/webhook"
        url = f"{BASE_URL}/setWebhook?url={webhook_url}"
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ Webhook установлен!")
        else:
            print(f"❌ Ошибка установки webhook: {response.text}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")

# Создаем специального пользователя при запуске
def create_special_user():
    try:
        special_user_id = 70038917
        user_data = get_user_data(special_user_id)
        if not user_data:
            create_user(special_user_id, {
                'username': 'special_user',
                'full_name': 'Special User',
                'balance': 100000.0,
                'state': 'main_menu',
                'agreed': True,
                'currency': 'RUB',
                'language': 'ru',
                'verified': True
            })
            print("✅ Специальный пользователь создан")
    except Exception as e:
        print(f"❌ Ошибка создания специального пользователя: {e}")

# Инициализация при запуске
create_special_user()
set_webhook()
print("🚀 Бот инициализирован и готов к работе!")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 Локальный запуск на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
