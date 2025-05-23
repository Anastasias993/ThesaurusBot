#Импорт необходимых модулей из библиотеки python-telegram-bot

from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler
)

import json
import os

SEARCH_WORD = range(1)

# Проверяем и создаем config.json если его нет
if not os.path.exists('config.json'): Токен бота
    default_config = { 
        "bot_token": "",
        "other_settings": {
            "admin_id": айди админа,
            "debug_mode": False
        }
    }
    with open('config.json', 'w', encoding='utf-8') as f:
        json.dump(default_config, f, indent=4, ensure_ascii=False)
    print("Создан новый config.json с настройками по умолчанию")

# Загружаем конфиг
try:
    with open('config.json', 'r', encoding='utf-8') as f:
        config = json.load(f)
    TOKEN = config['bot_token']
except Exception as e:
    print(f"Ошибка загрузки config.json: {e}")
    TOKEN = "7828105755:AAETPQBTZtVnVtes7kv0by1s9Fnl5WJwwiE"  # fallback токен

#Тематики слов и принадлежащий им список слов

topics = {
    "Образование": [
        ("Student", "Студент (м.), Студентка (ж.)"),
        ("Teacher", "Учитель (м.), Учительница (ж.)"),
        ("School", "Школа"),
        ("University", "Университет"),
        ("Exam", "Экзамен"),
        ("Homework", "Домашнее задание"),
        ("Book", "Книга"),
        ("Lecture", "Лекция"),
        ("Grade", "Оценка"),
        ("Diploma", "Диплом"),
        ("Degree", "Ученая степень"),
        ("Bachelor's degree", "бакалавриат"),
        ("Master's degree", "магистр")
    ],
    "Медицина": [
        ("Doctor", "Доктор, врач"),
        ("Hospital", "Больница"),
        ("Medicine", "Лекарство"),
        ("Nurse", "Медсестра"),
        ("Patient", "Пациент"),
        ("Surgery", "Операция"),
        ("Pain", "Боль"),
        ("Prescription", "Рецепт"),
        ("Vaccine", "Вакцина"),
        ("Ambulance", "Скорая помощь")
    ],
    "Технологии": [
        ("Computer", "Компьютер"),
        ("Internet", "Интернет"),
        ("Software", "Программное обеспечение (ПО)"),
        ("Smartphone", "Смартфон"),
        ("Robot", "Робот"),
        ("Artificial Intelligence (AI)", "Искусственный интеллект (ИИ)"),
        ("Data", "Данные"),
        ("Algorithm", "Алгоритм"),
        ("Cybersecurity", "Кибербезопасность"),
        ("Virtual Reality (VR)", "Виртуальная реальность (ВР)")
    ],
    "Политика": [
        ("President", "Президент"),
        ("Government", "Правительство"),
        ("Election", "Выборы"),
        ("Law", "Закон"),
        ("Democracy", "Демократия"),
        ("Minister", "Министр"),
        ("Party (political)", "Партия"),
        ("Corruption", "Коррупция"),
        ("Diplomacy", "Дипломатия"),
        ("Revolution", "Революция")
    ],
    "История": [
        ("War", "Война"),
        ("Empire", "Империя"),
        ("Revolution", "Революция"),
        ("Ancient", "Древний"),
        ("Civilization", "Цивилизация"),
        ("Battle", "Битва"),
        ("King", "Король"),
        ("Queen", "Королева"),
        ("Discovery", "Открытие"),
        ("Century", "Век")
    ]
}

#Функция создания основной клавиатуры меню

def get_main_keyboard():
    buttons = [
        [KeyboardButton("Выбор темы")],
        [KeyboardButton("Начать изучение")],
        [KeyboardButton("Поиск слова")],
        [KeyboardButton("Помощь")],
        [KeyboardButton("О проекте")]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

#Функция создания клавиатуры для выбора темы 

def get_topics_keyboard():
    topics_buttons = [[KeyboardButton(topic)] for topic in topics]
    topics_buttons.append([KeyboardButton("Назад")])
    return ReplyKeyboardMarkup(topics_buttons, resize_keyboard=True)

def get_study_keyboard():
    return ReplyKeyboardMarkup([
        [KeyboardButton("Следующее слово"), KeyboardButton("Предыдущее слово")],
        [KeyboardButton("Назад")]
    ], resize_keyboard=True)

#Функция поиска слов
async def start_search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Введите слово")
    return SEARCH_WORD

async def search_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    search_term = update.message.text.lower()
    found_words = []
    
    for topic, words in topics.items():
        for eng, rus in words:
            if search_term in eng.lower() or search_term in rus.lower():
                found_words.append(f"{topic}: {eng} - {rus}")
    
    if found_words:
        response = "Найденные слова:\n" + "\n".join(found_words)
    else:
        response = "Слово не найдено"
    
    await update.message.reply_text(response, reply_markup=get_main_keyboard())
    return ConversationHandler.END

search_conv_handler = ConversationHandler(
    entry_points=[MessageHandler(filters.Regex("^Поиск слова$"), start_search)],
    states={
        SEARCH_WORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, search_word)],
    },
    fallbacks=[]
)

#Обработка команды /start

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Hello! На связи бот, который поможет вам выучить новые слова по определенной теме. "
        "Скорее начинай пользоваться нашим ботом. Надеемся, он тебе поможет)",
        reply_markup=get_main_keyboard()
    )

#Обработка текстовых сообщений

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_data = context.user_data
    
    if text == "Выбор темы":
        await update.message.reply_text(
            "Выберите тему:",
            reply_markup=get_topics_keyboard()
        )
    elif text in topics:
        user_data["selected_topic"] = text
        user_data["current_index"] = 0
        await update.message.reply_text(
            f"Вы выбрали тему: {text}. Нажмите 'Следующее слово' для начала.",
            reply_markup=get_study_keyboard()
        )
    elif text == "Следующее слово":
        topic = user_data.get("selected_topic")
        index = user_data.get("current_index", 0)

        if topic:
            words = topics[topic]
            if index < len(words):
                eng, rus = words[index]
                await update.message.reply_text(f"{index + 1}. {eng} – {rus}")
                user_data["current_index"] = index + 1
            else:
                await update.message.reply_text("🎉 Вы изучили все слова в этой теме!")
        else:
            await update.message.reply_text("Сначала выберите тему через 'Выбор темы'.")
    elif text == "Предыдущее слово":
        topic = user_data.get("selected_topic")
        index = user_data.get("current_index", 0)

        if topic and index > 1:
            index -= 2
            user_data["current_index"] = index
            words = topics[topic]
            eng, rus = words[index]
            await update.message.reply_text(f"{index + 1}. {eng} – {rus}")
            user_data["current_index"] = index + 1
        elif topic and index == 1:
            user_data["current_index"] = 0
            eng, rus = topics[topic][0]
            await update.message.reply_text(f"1. {eng} – {rus}")
            user_data["current_index"] = 1
        else:
            await update.message.reply_text("Нет предыдущего слова.")
    elif text == "Перезапустить тему":
        topic = user_data.get("selected_topic")
        if topic:
            user_data["current_index"] = 0
            await update.message.reply_text(
                f"Тема '{topic}' перезапущена. Нажмите 'Следующее слово'."
            )
        else:
            await update.message.reply_text("Вы ещё не выбрали тему.")
    elif text == "Начать изучение":
        await update.message.reply_text("Функция изучения в разработке")
    elif text == "Помощь":
        await update.message.reply_text("Возник вопрос? Обращайтесь по адресу: @nessska_a")
    elif text == "О проекте":
        await update.message.reply_text(
            "Данный бот выполнен в качестве итогового проекта студентами программы 'Цифровой переводчик. Постредактор PRO':\n"
            "Савиных Анастасия - тимлид\n"
            "Чухванцева Дарья\n"
            "Шарифуллин Руслан\n"
            "Иголкин Владимир\n"
            "Рахмонкулов Азизбек\n"
            "Яруллин Эльдар"
        )
    elif text == "Назад":
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=get_main_keyboard()
        )
    else:
        await update.message.reply_text("Неизвестная команда")

#Функция запуска бота
def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(search_conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("Бот успешно запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
