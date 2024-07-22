from telebot import types
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import telebot
import os, random
from auth_data import token, admin_id
import sqlite3
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
print("Запуск бота...")
bot = telebot.TeleBot(token)
print("Получение токена...")

questions = [
    'Последнее время меня ничего не радует',
    'Замечаю, что у меня упала работоспособность',
    'Мне сложно сосредоточиться, появилась забывчивость, рассеянность',
    'Меня раздражают коллеги и родные',
    'Нет сил и энергии',
    'Раздражают  любимые дела и хобби',
    'Не вижу смысла и будущего в отношениях',
    'Больше времени провожу в играх и социальных сетях',
    'Больше пью кофе, алкоголя, ем сладкого, курю (что-то из этого)'
]

conn = sqlite3.connect('quiz.db', check_same_thread=False)
cursor = conn.cursor()
print("Подключение к бд...")

def check(user_id):
    status = ['creator', 'administrator', 'member']
    user_status = bot.get_chat_member(chat_id='-1002053959225', user_id=user_id).status
    return user_status in status


@bot.message_handler(commands=['start'])
def send_welcome(message):
    cursor.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (message.from_user.id,))
    conn.commit()

    user_id = message.from_user.id


    bot.send_message(admin_id, f"Пользователь {bot.get_chat(user_id).username, user_id} начал прохождение квиза")
    bot.send_message(user_id, "Добро пожаловать\!" + '\U0001F44B' + "\nЭто чек\-лист от канала «Думай дыши твори»\. Пройдите его и узнайте какой у вас уровень энергии сейчас\, есть ли признаки выгорания\. Ответьте\, пожалуйста\, на 10 вопросов\: выберите да или нет\.", parse_mode="MarkdownV2")
    send_next_question(user_id)


def escape_markdown_v2(text):
    escape_chars = r'\_*[]()~`>#+-=|{}.!'
    return ''.join(f'\\{char}' if char in escape_chars else char for char in text)


def send_next_question(user_id):
    cursor.execute('SELECT current_question FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        current_question = row[0] if row[0] is not None else 0
        if current_question < len(questions):
            question = escape_markdown_v2(questions[current_question])
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text='Да ' + '\U00002705', callback_data='yes'),
                       types.InlineKeyboardButton(text='Нет ' + '\U0000274C', callback_data='no'))
            bot.send_message(user_id, f'*{question}*', parse_mode='MarkdownV2', reply_markup=markup)
        else:

            bot.send_message(user_id, "*Вы прошли тест*", parse_mode='MarkdownV2',
                             reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                 types.InlineKeyboardButton(text="Узнать результат", callback_data='get_result')))


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "get_result":
        if check(call.from_user.id):
            cursor.execute('SELECT score FROM users WHERE user_id = ?', (user_id,))
            score = cursor.fetchone()
            if score:
                score = score[0]
                if 0 <= score <= 3:
                    bot.send_message(user_id,
                                     f"\U0001F605" + "*Вы устали\. Несколько дней отдыха вернут вам вкус и радость жизни*" + '\n \n' + 'Хотите полностью восстановиться и предотвратить выгорание, напишите мне, ' +
                                                                                                                                        'и я пришлю вам *__бесплатный гайд__ _«Как восстановить энергию»_*\. \n\nЧтобы укрепить ' +
                                                                                                                                        'свой внутренний ресурс и узнать больше полезных техник\, *__присоединяйтесь к марафону__ _«Внутренняя сила»_*\. \n\nЕсли вы предпочитаете *__индивидуальный подход__\, заполните форму* и приходите на *бесплатную* консультацию\-знакомство\.',
                                     parse_mode='MarkdownV2',
                                     reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                         types.InlineKeyboardButton(text="Написать мне",
                                                                    url="https://t.me/IrinaSem77"),
                                         types.InlineKeyboardButton(text="Марафон «Внутренняя сила»",
                                                                    url="https://semenova-coaching.ru/inner_strength"),
                                         types.InlineKeyboardButton(text="Запись на индивидуальную сессию",
                                                                    url="https://forms.gle/G9b9ahjs4Rk1FtXK7")))
                elif 4 <= score <= 6:
                    bot.send_message(user_id,
                                     f"\U0001F613" + "*У вас снижен уровень внутренней энергии и высокая вероятность выгорания\. Важно вовремя обратить внимание на своё состояние и принять меры по восстановлению\.*" + '\n \n' +
                                       'Начните с получения моего *__бесплатного гайда__ _«Как восстановить энергию»_*\, напишите мне и я его вам вышлю\. \n\n*__Присоединиться к марафону__ _«Внутренняя сила»_*\, ' +
                                       'узнаете подходы к восстановлению энергии через ваши архетипы\, силу рода и натальную карту\. \n\nДля более глубокой индивидуальной работы с вашим состоянием\, *заполните форму и приходите на __бесплатную консультацию\-знакомство__*\. ',
                                     parse_mode='MarkdownV2',
                                     reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                         types.InlineKeyboardButton(text="Написать мне",
                                                                    url="https://t.me/IrinaSem77"),
                                         types.InlineKeyboardButton(text="Марафон «Внутренняя сила»",
                                                                    url="https://semenova-coaching.ru/inner_strength"),
                                         types.InlineKeyboardButton(text="Запись на индивидуальную сессию",
                                                                    url="https://forms.gle/G9b9ahjs4Rk1FtXK7")))

                elif 7 <= score <= 10:
                    bot.send_message(user_id,
                                     f"\U0001F614" + "*У вас явные признаки снижения внутренней энергии и выгорания\, может привести к депрессии\.*" + '\n \n' + 'Начните своё восстановление прямо сейчас\: напишите мне и получите *__бесплатный гайд__ _«Как восстановить энергию»_*\, ' +
                                                                                                                             'который поможет вам сделать первый шаг к восстановлению\. \n\nЧтобы систематически работать над своим состоянием\, ' +
                                                                                                                             '*__присоединяйтесь к марафону__ _«Внутренняя сила»_*\. Это поможет вам вернуть силы и обрести уверенность\. ' +
                                                                                                                             '\n\nДля индивидуальной поддержки\, *заполните форму и приходите на __бесплатную консультацию\-знакомство__*\.',
                                     parse_mode='MarkdownV2',
                                     reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                         types.InlineKeyboardButton(text="Написать мне",
                                                                    url="https://t.me/IrinaSem77"),
                                         types.InlineKeyboardButton(text="Марафон «Внутренняя сила»",
                                                                    url="https://semenova-coaching.ru/inner_strength"),
                                         types.InlineKeyboardButton(text="Запись на индивидуальную сессию",
                                                                    url="https://forms.gle/G9b9ahjs4Rk1FtXK7")))
                else:
                    bot.send_message(user_id,
                                     f"У вас высокая вероятность выгорания" + '\U0001F613' + '\n \n' + 'Нужно обязательно пройти марафон и обратиться ко мне',
                                     parse_mode='MarkdownV2',
                                     reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                         types.InlineKeyboardButton(text="Написать мне",
                                                                    url="https://t.me/IrinaSem77"),
                                         types.InlineKeyboardButton(text="Марафон «Внутренняя сила»",
                                                                    url="https://semenova-coaching.ru/inner_strength"),
                                         types.InlineKeyboardButton(text="Запись на индивидуальную сессию",
                                                                    url="https://forms.gle/G9b9ahjs4Rk1FtXK7")))

                bot.send_message(admin_id,
                                 f"Пользователь {bot.get_chat(user_id).username, user_id} завершил квиз с {score} ответами 'да'.")
                cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
                conn.commit()
            else:
                bot.send_message(user_id, "Результат уже был получен.")
        else:
            bot.answer_callback_query(call.id, "Пожалуйста, подпишитесь на канал.")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            bot.send_message(user_id, text="Подпишитесь на канал, чтобы узнать ответ",
                             reply_markup=types.InlineKeyboardMarkup(row_width=True).add(
                                 types.InlineKeyboardButton(text="Думай Дыши Твори",
                                                            url="https://t.me/think_breathe_create"),
                                 types.InlineKeyboardButton(text="Узнать результат", callback_data="get_result")))
    if call.data == "yes":
        cursor.execute('SELECT current_question, score FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            current_question = row[0] if row[0] is not None else 0
            score = row[1] if row[1] is not None else 0
            score += 1
            current_question += 1
            cursor.execute('UPDATE users SET current_question = ?, score = ? WHERE user_id = ?',
                           (current_question, score, user_id))
            conn.commit()
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            send_next_question(user_id)


        else:
            bot.send_message(user_id, "Пожалуйста, начните квиз командой /start")

    if call.data == "no":
        cursor.execute('SELECT current_question, score FROM users WHERE user_id = ?', (user_id,))
        row = cursor.fetchone()
        if row:
            current_question = row[0] if row[0] is not None else 0
            score = row[1] if row[1] is not None else 0
            score += 0
            current_question += 1
            cursor.execute('UPDATE users SET current_question = ?, score = ? WHERE user_id = ?',
                           (current_question, score, user_id))
            conn.commit()
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
            send_next_question(user_id)
        else:
            bot.send_message(user_id, "Пожалуйста, начните квиз командой /start")


@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    user_id = message.chat.id
    cursor.execute('SELECT current_question, score FROM users WHERE user_id = ?', (user_id,))
    row = cursor.fetchone()
    if row:
        current_question = row[0] if row[0] is not None else 0
        score = row[1] if row[1] is not None else 0
        if message.text.lower() == 'да':
            score += 1
        current_question += 1
        cursor.execute('UPDATE users SET current_question = ?, score = ? WHERE user_id = ?',
                       (current_question, score, user_id))
        conn.commit()
        send_next_question(user_id)
    else:
        bot.send_message(user_id, "Пожалуйста, начните квиз командой /start")
print("Успешно запушен...")

bot.infinity_polling()
