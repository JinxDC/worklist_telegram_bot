import telebot
import time
import json

API_TOKEN = "TOKEN"
bot = telebot.TeleBot(API_TOKEN)

BUTTONS = ["Новая задача", "Список задач"]
DAY_LIST = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
TIME_START = 0
TIME_END = 24
TASK_BUTTONS = ["✅","❌","✏️","📅"]

task_list = []
current_reschedule_task_id = None

class Task:
    def __init__(self, title="", day="", task_time=""):
        self.title = title
        self.day = day
        self.time = task_time
        self.task_id = str(time.time())

def task_keyboard(task_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for button in TASK_BUTTONS:
        data = {"a": button, "i": task_id}
        json_str = json.dumps(data, ensure_ascii=False)
        task_button = telebot.types.InlineKeyboardButton(button, callback_data=json_str)
        buttons.append(task_button)
    keyboard.add(*buttons)
    return keyboard


def day_keyboard(task_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=4)
    buttons = []
    for i, day in enumerate(DAY_LIST):
        data = {"a": "d", "d": i, "i": task_id}
        json_str = json.dumps(data, ensure_ascii=False)
        button = telebot.types.InlineKeyboardButton(day, callback_data=json_str)
        buttons.append(button)
    keyboard.add(*buttons)
    return keyboard

def time_keyboard(task_id):
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=6)
    buttons = []
    for hour in range(TIME_START, TIME_END + 1):
        data = {"a": "t", "t": f"{hour}:00", "i": task_id}
        json_str = json.dumps(data, ensure_ascii=False)
        button = telebot.types.InlineKeyboardButton(f"{hour}:00", callback_data=json_str)
        buttons.append(button)
    keyboard.add(*buttons)
    return keyboard


def get_task_by_id(task_id):
    for task in task_list:
        if task.task_id == task_id:
            return task
    return None

def print_list(message):
    if not task_list:
        bot.send_message(message.chat.id, "Список задач пуст.")
    else:
        bot.send_message(message.chat.id, "Список задач:")
        for task in task_list:
            text = f"{task.title}\nДень: {task.day if task.day != '' else 'не выбран'}\nВремя: {task.time if task.time != '' else 'не выбран'}"
            bot.send_message(message.chat.id, text, reply_markup=task_keyboard(task.task_id))

def edit_task_title(message, task):
    task.title = message.text
    bot.send_message(message.chat.id, f"Название обновлено:\n{task.title}")

@bot.message_handler(commands=["start"])
def start(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(*[telebot.types.KeyboardButton(text) for text in BUTTONS])
    bot.send_message(message.chat.id, "Здрасте", reply_markup=markup)

@bot.message_handler(content_types=["text"])
def handle_text(message):
    global current_reschedule_task_id
    if message.text == BUTTONS[0]:
        bot.send_message(message.chat.id, "Введи задачу")
        current_reschedule_task_id = None
    elif message.text == BUTTONS[1]:
        print_list(message)
    else:
        if current_reschedule_task_id is None:
            new_task = Task(message.text)
            task_list.append(new_task)
            current_reschedule_task_id = new_task.task_id
            bot.send_message(message.chat.id, "Выбери день задачи", reply_markup=day_keyboard(new_task.task_id))
            bot.send_message(message.chat.id, "Выберите время начала задачи", reply_markup=time_keyboard(new_task.task_id))


        else:
            for task in task_list:
                if task.task_id == current_reschedule_task_id:
                    task.title = message.text
            current_reschedule_task_id = None

# @bot.callback_query_handler(func=lambda call: call.data in DAY_LIST)
def handle_day(call, task_id):
    task = get_task_by_id(task_id)
    if task:
        task.day = call.data
        bot.edit_message_text(f"📅 День обновлён: {call.data}", call.message.chat.id, call.message.id)
    bot.answer_callback_query(call.id)

# @bot.callback_query_handler(func=lambda call: '"action": "time"' in call.data)
def handle_time(call):
    data = json.loads(call.data)
    task_id = data.get("task_id")
    task = get_task_by_id(task_id)
    if task:
        task.time = data.get("time")
        bot.edit_message_text(f"⏰ Время обновлено: {task.time}", call.message.chat.id, call.message.id)
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: True)
def handle_task_buttons(call):

    global current_reschedule_task_id

    data = json.loads(call.data)
    action = data.get("a")
    task_id = data.get("i")
    task = get_task_by_id(task_id)

    if not task:
        bot.answer_callback_query(call.id, "Задача не найдена")
        return

    if action == "✅":
        bot.edit_message_text(f"✅ Выполнено:\n{task.title}", call.message.chat.id, call.message.id)
        task_list.remove(task)


    elif action == "❌":
        bot.edit_message_text(f"❌ Удалено:\n{task.title}", call.message.chat.id, call.message.id)
        task_list.remove(task)

    elif action == "✏️":
        bot.send_message(call.message.chat.id, "Введи новое название задачи:")
        current_reschedule_task_id = task_id

    elif action == "📅":
        current_reschedule_task_id = task_id
        bot.send_message(call.message.chat.id, "Выбери новый день", reply_markup=day_keyboard(task_id))
        bot.send_message(call.message.chat.id, "Выбери новое время", reply_markup=time_keyboard(task_id))

    elif action == "d":
        day_index = data.get("d")
        task.day = DAY_LIST[day_index]
        bot.edit_message_text(f"📅 День обновлён: {task.day}", call.message.chat.id, call.message.id)

    elif action == "t":
        task.time = data.get("t")
        bot.edit_message_text(f"⏰ Время обновлено: {task.time}", call.message.chat.id, call.message.id)

    bot.answer_callback_query(call.id)

bot.infinity_polling()
