import telebot
from telebot import types

secret_token_is_hidden_safely_here = "1471895512:AAHJ7vIwWc8Ut5h7xlM2lAx52Sk0dztQsUo"
bot = telebot.TeleBot(secret_token_is_hidden_safely_here)
chats_content = dict()


class Question(object):
    """docstring"""

    def __init__(self, question, answers, right, points: int = 1):
        """Constructor"""
        self.question = question
        self.answers = answers
        self.right_answer = right
        self.points = points

    def answer(self, answer):
        if answer == self.right_answer:
            return self.points
        else:
            return 0


questions = [
    Question("Do you like horror movies?",
             {'a': 'Yes, I am', 'b': 'Yes, I like', 'c': 'Yes, I do'}, 'c'),
    Question("How old are you?",
             {'a': 'I have XX years old', 'b': 'I have XX years', 'c': 'I am XX years old'}, 'c'),
    Question("I usually have English classes ____.",
             {'a': 'in Mondays', 'b': 'at Mondays', 'c': 'on Mondays'}, 'c'),
    Question("There ___ troublemakers at the football match, for a change.",
             {'a': 'were any', 'b': 'were not', 'c': 'were no'}, 'c'),
    Question("She won’t be able to catch the train. There is ____ time!",
             {'a': 'too few', 'b': 'too little', 'c': 'isn’t enough'}, 'b'),
    Question("Have you finished your presentation ____?",
             {'a': 'still', 'b': 'now', 'c': 'yet'}, 'c'),
    Question("If I didn't have to study, I _____ the summer camp.",
             {'a': 'would move to', 'b': 'have moved to', 'c': 'would have moved to'}, 'a'),
    Question("He is _______ to New York tomorrow.",
             {'a': 'going flying', 'b': 'to fly', 'c': 'going to fly'}, 'c'),
    Question("The washing machine can’t be out of order! He _____.",
             {'a': 'is just fixed it', 'b': 'have just fixed it', 'c': 'has just fixed it'}, 'c'),
    Question("That’s the ____ of my worries. I’m sure she’ll never do it.",
             {'a': 'less', 'b': 'last', 'c': 'least'}, 'c'),
    Question("This is the ____ decision I’ve ever made in my life.",
             {'a': 'harder', 'b': 'hardest', 'c': 'more hard'}, 'b'),
    Question("I told her _____ the doctor as soon as possible.",
             {'a': 'to call', 'b': 'she calls', 'c': 'that she calls'}, 'a'),
    Question("Let’s go to the beach right now, _____",
             {'a': 'let us?', 'b': 'shall we?', 'c': 'will we?'}, 'b'),
    Question("He ___ go to the dentist’s yesterday.",
             {'a': 'must', 'b': 'had to', 'c': 'ought to'}, 'b'),
    Question("You _____________ exhausted, everybody told you the route was too tough.",
             {'a': 'should have been', 'b': 'must have been', 'c': 'should be'}, 'b'),
]

CALLBACK_QUESTION_PREFIX = "question_number:"


class User(object):
    """docstring"""

    def __init__(self, user_fio):
        """Constructor"""
        self.fio = user_fio
        self.phone = "n/a"
        self.test_result = TestResult()

    def put_answer(self, question_index: int, question: Question, answer):
        current_points = question.answer(answer)
        self.test_result.answers[question_index] = current_points
        self.test_result.points += current_points

    def __str__(self):
        """Converts to String"""
        return self.fio + "," + self.phone + "," + str(self.test_result)


class TestResult(object):
    """docstring"""

    def __init__(self):
        """Constructor"""
        self.answers = []
        self.points = 0
        self.current_question_index = -1
        self.questions_count = 0

    def reset(self, questions_count: int = 0):
        """reset all fields"""
        self.answers = dict()
        self.points = 0
        self.current_question_index = -1
        self.questions_count = questions_count

    def next(self):
        self.current_question_index += 1
        if self.current_question_index >= self.questions_count:
            self.current_question_index = -1
        return self.current_question_index

    def __str__(self):
        """Converts to String"""
        return str(self.points)


@bot.message_handler(commands=['help'])
def send_help(message):
    bot.reply_to(message, "Это справка.\nнапишите /start, чтобы начать заново")


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id,
                     '''Школа Английского языка приветствует Вас в своём бот чате. \
                     Здесь мы пройдём первые шаги знакомства и пройдём маленький тест для определения Вашего уровня языка!
                     ''')
    markup = types.ForceReply(selective=True)
    bot.send_message(message.chat.id, "Напечатайте Ваше ФИО полностью:", reply_markup=markup)


@bot.message_handler(content_types=['text'], regexp="^\w+\s+\w+\s+\w+\s*$")
def send_phone_request(message):
    bot.reply_to(message, "Приятно познакомиться, " + message.text + "!")
    chats_content[str(message.chat.id)] = User(message.text)
    bot.send_message(message.chat.id,
                     "Для обратной связи поделитесь номером телефона, пожалуйста:",
                     reply_markup=keyboard_get_contact())


@bot.message_handler(content_types=['contact'])
def receive_contact(message):
    chat_id = message.chat.id
    if str(chat_id) not in chats_content:
        chats_content[str(chat_id)] = User(message.contact.last_name + " " + message.contact.first_name)
    chats_content[str(chat_id)].phone = message.contact.phone_number
    print(chat_id, "Result:", str(chats_content[str(chat_id)]))
    bot.send_message(chat_id,
                     "Теперь прошу пройти небольшой тест для определения Вашего уровня английского! Вперед!",
                     reply_markup=keyboard_start_test())


@bot.message_handler(content_types=['text'], func=lambda m: m.text == 'Начать тестирование')
def start_test(message):
    chat_id = message.chat.id
    if str(chat_id) not in chats_content:
        bot.send_message(chat_id,
                         "Вы не указали ФИО или контактный телефон",
                         reply_markup=keyboard_get_contact())
        return
    test_state = chats_content[str(chat_id)].test_result
    if len(questions) == 0:
        bot.reply_to(message, "Тест отсутствует!")
    test_state.reset(len(questions))
    cur_question_index = test_state.next()
    send_question(chat_id, cur_question_index)


@bot.callback_query_handler(func=lambda callback: callback.data.find(CALLBACK_QUESTION_PREFIX) != -1)
def next_question(callback):
    chat_id = callback.message.chat.id
    if str(chat_id) not in chats_content:
        bot.send_message(chat_id,
                         "Вы не указали ФИО или контактный телефон",
                         reply_markup=keyboard_get_contact())
        return
    user = chats_content[str(chat_id)]
    test_state = user.test_result
    prev_index = int(callback.data[len(CALLBACK_QUESTION_PREFIX): callback.data.find(',')])
    prev_index_tmp = test_state.current_question_index
    if prev_index_tmp != prev_index:
        pass
        return
    # здесь начинаем менять состояние объектов
    prev_answer = callback.data[callback.data.find(',') + 1]
    user.put_answer(prev_index, questions[prev_index], prev_answer)
    cur_question_index = test_state.next()
    if cur_question_index == -1:
        """Завершили тест"""
        finish_test(chat_id, user, test_state)
        return
    if cur_question_index != prev_index + 1:
        bot.send_message(chat_id, "Ошибка! Вопросы пошли не по порядку (бага)", reply_markup=keyboard_start_test())
        return
    send_question(chat_id, cur_question_index)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    pass


def finish_test(chat_id: int, user: User, test_state: TestResult):
    bot.send_message(chat_id,
                     "Поздравляю! Вы прошли тест! \n\nВаш результат: \n"
                     + user.fio + " - " + str(test_state.points)
                     + " (" + get_level_name(test_state.points)
                     + "). \n\nWe will contact you later...")
    save_result_to_file(user)


def keyboard_get_contact():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton(text="Поделиться номером телефона", request_contact=True)
    markup.add(btn)
    return markup


def keyboard_start_test():
    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    btn = types.KeyboardButton(text="Начать тестирование")
    markup.add(btn)
    return markup


def send_question(chat_id: int, number: int):
    full_question = questions[number].question
    bot.send_message(chat_id, full_question,
                     reply_markup=keyboard_question(number, questions[number].answers))


def keyboard_question(number: int, answers: {}):
    markup = types.InlineKeyboardMarkup()
    btns = {}
    for answer_key, answer in answers.items():
        btns[answer_key] = types.InlineKeyboardButton(text=answer_key + ') ' + answer,
                                                      callback_data=CALLBACK_QUESTION_PREFIX+str(number)+","+answer_key)
    for btn in btns.values():
        markup.add(btn)
    return markup


def get_level_name(points: int):
    if points < 7:
        return "Низкий"
    elif points <= 12:
        return "Средний"
    elif points > 12:
        return "Высокий"
    else:
        return "Что-то невероятное"


def save_result_to_file(user: User):
    f = open('results.csv', 'a')
    f.write(str(user) + "\n")
    f.flush()
    f.close()


if __name__ == '__main__':
    bot.polling()
