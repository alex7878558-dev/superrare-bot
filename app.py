import sqlite3
import requests
import datetime
import time
import os
import threading
from flask import Flask, request

app = Flask(__name__)

# ==================== КОНФИГ ====================
BOT_TOKEN = "8583960432:AAFnqFYa9iHn-08KM1HQnJpLG3qQ3zUdPdY"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

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

# Запускаем самопробуждение
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

def back_keyboard(lang='ru'):
    back_text = TEXTS[lang]["back"]
    return {"keyboard": [[{"text": back_text}]], "resize_keyboard": True}

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'ru',
            currency TEXT,
            balance REAL DEFAULT 0.0,
            withdrawal_balance REAL DEFAULT 0.0,
            turnover REAL DEFAULT 0.0,
            verified INTEGER DEFAULT 0,
            agreed INTEGER DEFAULT 0,
            state TEXT DEFAULT 'start',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amount REAL,
            currency TEXT,
            card_number TEXT,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (user_id)
        )
    ''')
    conn.commit()
    conn.close()
    print("✅ База данных создана!")

# ==================== УТИЛИТЫ ====================
def get_user_data(user_id):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT state, username, language, currency FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def get_full_user_data(user_id):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_state(user_id, state):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET state = ? WHERE user_id = ?', (state, user_id))
    conn.commit()
    conn.close()

def update_user_language(user_id, language):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()

def update_user_currency(user_id, currency):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET currency = ? WHERE user_id = ?', (currency, user_id))
    conn.commit()
    conn.close()

def create_payment(user_id, amount, currency):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO payments (user_id, amount, currency, card_number) VALUES (?, ?, ?, ?)', (user_id, amount, currency, '[НОМЕР КАРТЫ ДЛЯ ОПЛАТЫ]'))
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id

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

            user_data = get_user_data(user_id)

            if not user_data:
                conn = sqlite3.connect('superrare.db', check_same_thread=False)
                cursor = conn.cursor()
                cursor.execute('INSERT INTO users (user_id, username, full_name, state) VALUES (?, ?, ?, ?)', (user_id, username, first_name, 'agreement'))
                conn.commit()
                conn.close()

                display_name = f"@{username}" if username else first_name
                agreement_text = f"Привет, **{display_name}!**\n\nПолитика и условия пользования данным ботом.\n\nСпасибо за понимание, Ваш **SuperRare | NFT Market**"
                send_message(user_id, agreement_text, agreement_keyboard())

            else:
                state, db_username, language, currency = user_data
                lang = language or 'ru'
                curr = currency or 'RUB'

                # Обработка состояний
                if state == 'agreement':
                    accept_text = "✅ Принять" if lang == 'ru' else "✅ Accept"
                    if text == accept_text:
                        update_user_state(user_id, 'language')
                        send_message(user_id, "Выберите язык", language_keyboard())

                elif state == 'language':
                    if text == "Русский":
                        update_user_language(user_id, 'ru')
                        update_user_state(user_id, 'currency')
                        send_message(user_id, "Выберите валюту", currency_keyboard())
                    elif text == "English":
                        update_user_language(user_id, 'en')
                        update_user_state(user_id, 'currency')
                        send_message(user_id, "Choose currency", currency_keyboard())

                elif state == 'currency':
                    if text in ["RUB", "UAH", "KZT", "BYN", "EUR", "USD"]:
                        update_user_currency(user_id, text)
                        update_user_state(user_id, 'main_menu')
                        user_data = get_user_data(user_id)
                        lang = user_data[2] or 'ru'
                        send_message(user_id, TEXTS[lang]["main_menu"], main_menu_keyboard(lang))

                elif state == 'main_menu':
                    text_obj = TEXTS[lang]
                    if text == "📊 " + text_obj["personal_account"]:
                        conn = sqlite3.connect('superrare.db', check_same_thread=False)
                        cursor = conn.cursor()
                        cursor.execute('SELECT balance, withdrawal_balance, turnover, verified, currency FROM users WHERE user_id = ?', (user_id,))
                        user = cursor.fetchone()
                        conn.close()

                        if user:
                            balance, withdrawal_balance, turnover, verified, currency = user
                            verification_status = "✅ Верифицирован" if verified else "💬 Не верифицирован"
                            if lang == 'en': verification_status = "✅ Verified" if verified else "💬 Not verified"
                            current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                            account_text = text_obj["personal_account_text"].format(
                                balance=balance, withdrawal_balance=withdrawal_balance, turnover=turnover,
                                verification_status=verification_status, user_id=user_id, current_time=current_time, currency=currency
                            )
                            send_message(user_id, account_text, personal_account_keyboard(lang))
                            update_user_state(user_id, 'personal_account')

                    elif text in ["💎 " + text_obj["nft"], "ℹ️ " + text_obj["info"], "🆘 " + text_obj["support"]]:
                        send_message(user_id, text_obj["in_development"])

                elif state == 'personal_account':
                    text_obj = TEXTS[lang]
                    deposit_text = "Пополнить" if lang == 'ru' else "Deposit"
                    menu_text = "Меню" if lang == 'ru' else "Menu"
                    back_text = "Назад" if lang == 'ru' else "Back"
                    settings_text = text_obj["settings"]

                    if text == deposit_text:
                        update_user_state(user_id, 'deposit_methods')
                        send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))
                    elif text == menu_text:
                        update_user_state(user_id, 'main_menu')
                        send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))
                    elif text == back_text:
                        update_user_state(user_id, 'main_menu')
                        send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))
                    elif text == settings_text:
                        full_user_data = get_full_user_data(user_id)
                        if full_user_data:
                            user_language = "Русский" if full_user_data[3] == 'ru' else "English"
                            user_currency = full_user_data[4] or 'RUB'
                            settings_message = text_obj["settings_text"].format(language=user_language, currency=user_currency)
                            send_message(user_id, settings_message, settings_keyboard(lang))
                            update_user_state(user_id, 'settings')

                elif state == 'settings':
                    text_obj = TEXTS[lang]
                    if text == text_obj["language"]:
                        update_user_state(user_id, 'change_language')
                        send_message(user_id, "Выберите язык:", language_keyboard())
                    elif text == text_obj["currency_setting"]:
                        update_user_state(user_id, 'change_currency')
                        send_message(user_id, "Выберите валюту:", currency_keyboard())
                    elif text == text_obj["back"]:
                        update_user_state(user_id, 'personal_account')
                        conn = sqlite3.connect('superrare.db', check_same_thread=False)
                        cursor = conn.cursor()
                        cursor.execute('SELECT balance, withdrawal_balance, turnover, verified, currency FROM users WHERE user_id = ?', (user_id,))
                        user = cursor.fetchone()
                        conn.close()
                        if user:
                            balance, withdrawal_balance, turnover, verified, currency = user
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
                        update_user_language(user_id, 'ru')
                        update_user_state(user_id, 'settings')
                        send_message(user_id, "Язык изменен на Русский", settings_keyboard('ru'))
                    elif text == "English":
                        update_user_language(user_id, 'en')
                        update_user_state(user_id, 'settings')
                        send_message(user_id, "Language changed to English", settings_keyboard('en'))

                elif state == 'change_currency':
                    if text in ["RUB", "UAH", "KZT", "BYN", "EUR", "USD"]:
                        update_user_currency(user_id, text)
                        update_user_state(user_id, 'settings')
                        user_data = get_user_data(user_id)
                        lang = user_data[2] or 'ru'
                        currency_name = "Рубль" if text == "RUB" else text
                        if lang == 'en': currency_name = "Ruble" if text == "RUB" else text
                        send_message(user_id, f"Валюта изменена на {currency_name}", settings_keyboard(lang))

                elif state == 'deposit_methods':
                    text_obj = TEXTS[lang]
                    bank_card_text = "Пополнить через банковскую карту" if lang == 'ru' else "Deposit by bank card"
                    back_text = "Назад" if lang == 'ru' else "Back"

                    if text == bank_card_text:
                        update_user_state(user_id, 'enter_amount')
                        min_amount = 2500.0 if curr == 'RUB' else 50.0
                        send_message(user_id, text_obj["enter_amount"].format(min_amount=min_amount, currency=curr), back_keyboard(lang))
                    elif text == back_text:
                        update_user_state(user_id, 'personal_account')
                        send_message(user_id, TEXTS[lang]["personal_account"], personal_account_keyboard(lang))

                elif state == 'enter_amount':
                    text_obj = TEXTS[lang]
                    back_text = "Назад" if lang == 'ru' else "Back"

                    if text == back_text:
                        update_user_state(user_id, 'deposit_methods')
                        send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))
                    else:
                        try:
                            amount = float(text)
                            min_amount = 2500.0 if curr == 'RUB' else 50.0
                            if amount >= min_amount:
                                create_payment(user_id, amount, curr)
                                payment_text = text_obj["payment_created"].format(card_number="[НОМЕР КАРТЫ ДЛЯ ОПЛАТЫ]", amount=amount, currency=curr)
                                update_user_state(user_id, 'payment_confirmation')
                                send_message(user_id, payment_text, payment_confirmation_keyboard(lang))
                            else:
                                send_message(user_id, f"Минимальная сумма: {min_amount} {curr}")
                        except ValueError:
                            send_message(user_id, "Пожалуйста, введите число")

        return 'ok'
    except Exception as e:
        print(f"❌ Ошибка в webhook: {e}")
        return 'error', 500

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

# ==================== ЗАПУСК ДЛЯ PRODUCTION ====================
def create_app():
    """Функция для Gunicorn"""
    init_db()
    set_webhook()
    return app

# Инициализация при импорте (для Gunicorn)
init_db()
set_webhook()
print("🚀 Бот инициализирован и готов к работе!")

if __name__ == "__main__":
    # Только для локальной разработки
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 Локальный запуск на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
