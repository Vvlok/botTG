import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot_logic import gen_pass, gen_emodji, flip_coin, search_images, download_image

TOKEN = "8248660537:AAG0rLl8zUUrPQch4NycLwgdFq-rg3JoutY"
bot = telebot.TeleBot(TOKEN)
user_data = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Привет! Я умею искать картинки. Напиши /find <запрос>\n\nДоступны команды: /hello, /bye, /pass, /emodji, /coin")

@bot.message_handler(commands=['hello'])
def send_hello(message):
    bot.reply_to(message, "Привет! Как дела?")

@bot.message_handler(commands=['bye'])
def send_bye(message):
    bot.reply_to(message, "Пока! Удачи!")

@bot.message_handler(commands=['pass'])
def send_password(message):
    pwd = gen_pass(10)
    bot.reply_to(message, f"🔐 Твой пароль: `{pwd}`", parse_mode="Markdown")

@bot.message_handler(commands=['emodji'])
def send_emodji(message):
    bot.reply_to(message, f"Вот смайлик: {gen_emodji()}")

@bot.message_handler(commands=['coin'])
def send_coin(message):
    result = flip_coin()
    emoji = "🦅" if result == "орёл" else "🪙"
    bot.reply_to(message, f"{emoji} Монетка выпала: {result}")

@bot.message_handler(commands=['find'])
def handle_find(message):
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Укажи запрос, например: /find котики")
        return
    query = parts[1]
    bot.reply_to(message, f"🔍 Ищу картинки по запросу: '{query}'...")

    try:
        images = search_images(query, per_page=3)
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при поиске: {e}")
        return

    if not images:
        bot.reply_to(message, "😕 Ничего не найдено")
        return

    chat_id = message.chat.id
    user_data[chat_id] = {"query": query, "images": images}

    for idx, img in enumerate(images, start=1):
        try:
            file_bytes = download_image(img["url"])
            if file_bytes is None:
                bot.reply_to(message, f"⚠️ Не удалось загрузить вариант {idx}, пропускаем")
                continue
            markup = InlineKeyboardMarkup()
            btn = InlineKeyboardButton(text=f"⬇️ Скачать #{idx}", callback_data=f"dl_{chat_id}_{idx-1}")
            markup.add(btn)
            bot.send_photo(chat_id, photo=file_bytes, caption=f"Вариант {idx}", reply_markup=markup)
        except Exception as e:
            bot.reply_to(message, f"❌ Ошибка загрузки варианта {idx}: {e}")

@bot.callback_query_handler(func=lambda call: call.data.startswith("dl_"))
def handle_download(call):
    try:
        _, chat_id_str, idx_str = call.data.split("_")
        chat_id = int(chat_id_str)
        idx = int(idx_str)
    except ValueError:
        bot.answer_callback_query(call.id, "❌ Неверные параметры")
        return

    data = user_data.get(chat_id)
    if not data or idx >= len(data["images"]):
        bot.answer_callback_query(call.id, "❌ Изображение уже недоступно, попробуйте поискать заново")
        return

    img = data["images"][idx]
    try:
        file_bytes = download_image(img["url"])
        if file_bytes is None:
            bot.answer_callback_query(call.id, "❌ Не удалось скачать файл")
            return
        bot.send_document(chat_id, file_bytes, visible_file_name=f"image_{idx+1}.jpg")
        bot.answer_callback_query(call.id, "✅ Файл отправлен!")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка скачивания: {e}")

if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)