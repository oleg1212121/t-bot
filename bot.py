from config import BOT_TOKEN, BOT_TAG
import telebot
import datetime
import db

bot = telebot.TeleBot(BOT_TOKEN)

default_messages = {
    'is_not_admin': 'Команда доступна только администратору',
    'check_help': 'Проверьте корректность ввода /help',
    'is_not_private': 'Перейдите в личные сообщения'
}
users_set = set()
user_appends_counter = 0
users_created_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
messages_parsing_mode = 0


def check_private(message):
    res = False
    if message.chat.type == 'private':
        res = True
    else:
        bot.send_message(message.from_user.id, default_messages['is_not_private'])
    return res and check_is_not_bot(message)


def check_admin(message):
    res = False
    user = db.get_user(message.from_user.id)
    if user and user[3] == 1:
        res = True
    else:
        bot.send_message(message.from_user.id, default_messages['is_not_admin'])
    return res and check_is_not_bot(message)


def check_private_admin(message):
    return check_admin(message) and check_private(message)


def check_is_not_bot(message):
    return not message.from_user.is_bot


@bot.message_handler(content_types=['new_chat_members'])
def greeting(message):
    bot.reply_to(message, text=f'Для верификации обратитесь к боту @{BOT_TAG} *Фраза*')


# @bot_name secret
@bot.inline_handler(func=lambda query: len(query.query) > 2 and len(query.query) < 100)
def query_text(inline_query):
    secrets = [elem[1] for elem in db.get_secrets()]
    if inline_query.query in secrets:
        r = telebot.types.InlineQueryResultArticle('1', 'Подтвердить',
                                                   telebot.types.InputTextMessageContent('Подтверждено'))
        bot.answer_inline_query(inline_query.id, [r])
    else:
        bot.answer_inline_query(inline_query.id, [])


@bot.chosen_inline_handler(func=lambda res: True)
def test_chosen(res):
    created_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
    db.create_or_update_message((
        res.from_user.id,
        res.from_user.first_name,
        res.from_user.username if res.from_user.username else '-',
        res.query,
        created_at))


# /join
@bot.message_handler(commands=['join'])
def message_check(message):
    try:
        created_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
        db.create_or_update_user((
            message.from_user.id,
            message.from_user.first_name,
            message.from_user.username if message.from_user.username else '-',
            False,
            created_at
        ))
        bot.send_message(message.chat.id, 'Пользователь сохранен')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /check 10
@bot.message_handler(commands=['check'], func=check_admin)
def message_check(message):
    try:
        delay = int(message.text.replace('/check', '').strip())
        messages = db.get_messages()
        users = db.get_users()
        secrets = [elem[1] for elem in db.get_secrets()]
        text = 'Ошибки верификации:\n'
        now = datetime.datetime.now()
        delta = datetime.timedelta(minutes=delay)
        new = datetime.datetime.strftime((now - delta), "%Y.%m.%d %H:%M")
        for mess in messages:
            if new > mess[4] or mess[3] not in secrets:
                text += f'{mess[1]} | {mess[4]} | {mess[3]}\n'
        text += f'Всего в базе: {len(users)} пользователей\n'
        bot.send_message(message.from_user.id, text)
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /messages
@bot.message_handler(commands=['messages'], func=check_admin)
def message_messages(message):
    try:
        messages = db.get_messages()
        text = "Список сообщений:\n"
        for item in messages:
            text += f"{item[0]} | {item[1]} | {item[3]} | {item[4]}\n"
        bot.send_message(message.from_user.id, text)
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /message_delete *id*
@bot.message_handler(commands=['message_delete'], func=check_admin)
def message_secret(message):
    try:
        identifier = int(message.text.replace('/message_delete', '').strip())
        db.delete_message(identifier)
        bot.send_message(message.from_user.id, 'Сообщение удалено')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /owner token
@bot.message_handler(commands=['owner'], func=check_private)
def message_owner(message):
    try:
        password = message.text.replace('/owner', '').strip()
        if password == BOT_TOKEN:
            created_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
            db.create_or_update_user((
                message.from_user.id,
                message.from_user.first_name,
                message.from_user.username if message.from_user.username else '-',
                True,
                created_at
            ))
            bot.send_message(message.from_user.id, 'Администратор установлен')
        else:
            bot.send_message(message.from_user.id, default_messages['check_help'])
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /admin_add *id*
@bot.message_handler(commands=['admin_add'], func=check_admin)
def message_secret(message):
    try:
        identifier = int(message.text.replace('/admin_add', '').strip())
        db.admin_add(identifier)
        bot.send_message(message.from_user.id, 'Права администратора добавлены')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /admin_remove *id*
@bot.message_handler(commands=['admin_remove'], func=check_admin)
def message_secret(message):
    try:
        identifier = int(message.text.replace('/admin_remove', '').strip())
        db.admin_remove(identifier)
        bot.send_message(message.from_user.id, 'Права администратора отменены')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /users
@bot.message_handler(commands=['users'], func=check_admin)
def message_users(message):
    try:
        users = db.get_users()
        text = "Список пользователей:\n"
        for item in users:
            text += f"{item[0]} | {item[1]} | { 'Администратор' if item[3] else 'Пользователь' }\n"
        bot.send_message(message.from_user.id, text)

    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /user_delete *id*
@bot.message_handler(commands=['user_delete'], func=check_admin)
def message_secret(message):
    try:
        identifier = int(message.text.replace('/user_delete', '').strip())
        db.delete_user(identifier)
        bot.send_message(message.from_user.id, 'Пользователь удален')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /secret *words*
@bot.message_handler(commands=['secret'], func=check_private_admin)
def message_secret(message):
    try:
        secret = message.text.replace('/secret', '').strip()
        if len(secret) >= 3:
            db.create_or_update_secret((None, secret))
            bot.send_message(message.from_user.id, 'Кодовая фраза установлена')
        else:
            bot.send_message(message.from_user.id, default_messages['check_help'])
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /secret_delete *id*
@bot.message_handler(commands=['secret_delete'], func=check_admin)
def message_secret(message):
    try:
        identifier = int(message.text.replace('/secret_delete', '').strip())
        db.delete_secret(identifier)
        bot.send_message(message.from_user.id, 'Кодовая фраза удалена')
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /secrets
@bot.message_handler(commands=['secrets'], func=check_admin)
def message_secrets(message):
    try:
        secrets = db.get_secrets()
        text = 'Список секретных фраз:\n'
        for item in secrets:
            text += f'{item[0]} | {item[1]}\n'
        bot.send_message(message.from_user.id, text)
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


# /help
@bot.message_handler(commands=['help'])
def message_help(message):
    text = 'Комманды бота:\n' \
           '/help - справочная информация\n' \
           f'@{BOT_TAG} "фраза" - ввод секретной фразы (без кавычек)\n' \
           '/secret "фраза" - сохранение секретной фразы в словарь (админ)\n' \
           '/secret_delete "id" - удаление секретной фразы из словаря по id (админ)\n' \
           '/secrets - список секретных фраз (админ)\n' \
           '/join - попасть в список пользователей\n' \
           '/users - список пользователей (админ)\n' \
           '/user_delete "id" - удаление пользователя из базы по id (админ)\n' \
           '/admin_add "id" - добавление администратора из списка пользователей по id (админ)\n' \
           '/admin_remove "id" - удаление пользователя из списка администраторов по id (админ)\n' \
           '/messages - список сообщений (админ)\n' \
           '/message_delete "id" - удаление сообщения по id (админ)\n' \
           '/check "минуты" - получить список сообщений записанных ранее X минут назад (админ)\n' \
           '/owner "TOKEN" - установка администратора с помощью токена бота\n'\
           '/parsing_on - включение обработки сообщений для сохранения пользователей из чата в базу (админ)\n'\
           '/parsing_off - выключение обработки сообщений (админ)\n'
    bot.send_message(message.chat.id, text)


# /parsing_on, /parsing_off
@bot.message_handler(commands=['parsing_on', 'parsing_off'], func=check_admin)
def message_help(message):
    try:
        global messages_parsing_mode
        global users_set
        on = message.text.find('/parsing_on', 0)
        if on != -1:
            messages_parsing_mode = 1
            text = 'Парсинг сообщений "Включен"'
        else:
            messages_parsing_mode = 0
            users_set = set()
            text = 'Парсинг сообщений "Выключен"'
        bot.send_message(message.chat.id, text)
    except:
        bot.send_message(message.from_user.id, default_messages['check_help'])


@bot.message_handler(content_types=['text'])
def send_text(message):
    global messages_parsing_mode
    if message.chat.type != 'private' and messages_parsing_mode == 1:
        save_user(message)


def save_user(message):
    global users_set
    global user_appends_counter
    global users_created_at
    if len(users_set) >= 10 or user_appends_counter >= 20:
        db_set = users_set
        users_set = set()
        user_appends_counter = 0
        users_created_at = datetime.datetime.now().strftime("%Y.%m.%d %H:%M")
        db.add_users(db_set)
    else:
        user_appends_counter += 1
        users_set.add((message.from_user.id, message.from_user.first_name,
                       message.from_user.username if message.from_user.username else '-', 0,
                       users_created_at))


if __name__ == '__main__':
    db.init_db()
    bot.polling(none_stop=True)
