import telebot
from telebot import types
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import random

# Настройки Spotify API
SPOTIFY_CLIENT_ID = "b6d7daefa0c94517b25242ac3c51f2ee"  # Замените на реальные!
SPOTIFY_CLIENT_SECRET = "d97637714c5649abbfb117088f89d283"

# Инициализация Spotify
client_credentials_manager = SpotifyClientCredentials(
    client_id=SPOTIFY_CLIENT_ID,
    client_secret=SPOTIFY_CLIENT_SECRET
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

# Инициализация бота
TOKEN = "7615955330:AAFtfkET02AXFB8W0F9_Fm1kPOX9ocSkJ4w"  # Получите у @BotFather
bot = telebot.TeleBot(TOKEN)


def get_random_artist():
    """Получает случайного популярного исполнителя из Spotify"""
    try:
        results = sp.search(q='year:2020-2023', type='track', limit=50)
        if not results['tracks']['items']:
            return None

        random_track = random.choice(results['tracks']['items'])
        artist = random_track['artists'][0]
        return sp.artist(artist['id'])
    except Exception as e:
        print(f"Ошибка при получении артиста: {e}")
        return None


def send_artist_info(chat_id, artist):
    """Отправляет информацию об исполнителе с кнопками"""
    try:
        name = artist['name']
        genres = ", ".join(artist.get('genres', ['разные жанры']))[:100]
        popularity = artist.get('popularity', 0)
        followers = artist.get('followers', {}).get('total', 0)
        image_url = artist['images'][0]['url'] if artist.get('images') else None

        # Получаем топ-треки и внешние ссылки
        top_tracks = sp.artist_top_tracks(artist['id'])
        best_songs = [track['name'] for track in top_tracks['tracks'][:3]] if top_tracks else ["не найдено"]
        #spotify_url = artist['external_urls']['spotify']

        # Создаем кнопки
        markup = types.InlineKeyboardMarkup()

        # Основные кнопки
        #btn_spotify = types.InlineKeyboardButton(
        #    text="🎧 Открыть в Spotify",
        #    url=spotify_url
        #)
        btn_youtube = types.InlineKeyboardButton(
            text="🎥 Поиск на YouTube",
            url=f"https://www.youtube.com/results?search_query={name.replace(' ', '+')}"
        )
        btn_wiki = types.InlineKeyboardButton(
            text="📖 Википедия",
            url=f"https://ru.wikipedia.org/w/index.php?search={name.replace(' ', '+')}"
        )

        # Кнопки действий
        #btn_like = types.InlineKeyboardButton(
        #    text="👍 Нравится",
        #    callback_data=f"like_{artist['id']}"
        #)
        btn_next = types.InlineKeyboardButton(
            text="➡️ Следующий исполнитель",
            callback_data="next_artist"
        )

        # Добавляем кнопки в меню
        markup.row(btn_youtube)
        markup.row(btn_wiki)
        markup.row(btn_next)

        # Формируем сообщение
        message = (
                f"🎵 <b>Исполнитель дня:</b> <i>{name}</i>\n\n"
                f"🎭 <b>Жанры:</b> {genres}\n"
                f"⭐ <b>Популярность:</b> {popularity}/100\n"
                f"👥 <b>Подписчиков:</b> {followers:,}\n\n"
                f"🎶 <b>Лучшие треки:</b>\n" +
                "\n".join(f"• {song}" for song in best_songs)
        )

        # Отправляем сообщение
        if image_url:
            bot.send_photo(
                chat_id,
                image_url,
                caption=message,
                parse_mode='HTML',
                reply_markup=markup
            )
        else:
            bot.send_message(
                chat_id,
                message,
                parse_mode='HTML',
                reply_markup=markup
            )

    except Exception as e:
        print(f"Ошибка при отправке: {e}")
        bot.send_message(chat_id, "Произошла ошибка при формировании информации 😢")


# Обработчик callback-кнопок
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data == "next_artist":
        bot.answer_callback_query(call.id, "Ищем следующего исполнителя...")
        artist = get_random_artist()
        if artist:
            send_artist_info(call.message.chat.id, artist)
        else:
            bot.send_message(call.message.chat.id, "Не удалось найти исполнителя 😢")
    elif call.data.startswith("like_"):
        artist_id = call.data.split("_")[1]
        bot.answer_callback_query(call.id, "Добавлено в избранное! ❤️")
        # Здесь можно добавить логику сохранения в избранное


# Обработчики команд
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Рандом иностранный сингер💸")
    btn2 = types.KeyboardButton("Чарты VK и поиск песен 🔥")
    btn3 = types.KeyboardButton("Support")
    markup.add(btn1, btn2, btn3)

    bot.send_message(
        message.chat.id,
        "Привет! Я музыкальный бот от //roskoshnyi.hub и вот что я умею:\n\n"
        "• Показывать случайных зарубежных исполнителей\n"
        "• Искать по чартам VK и скачивать треки в кеш для удобного offline прослушивания\n"
        "• Искать информацию о музыке",
        reply_markup=markup
    )


@bot.message_handler(func=lambda m: m.text == "Рандом иностранный сингер💸")
def artist_handler(message):
    bot.send_message(message.chat.id, "Ищу интересного исполнителя...")
    artist = get_random_artist()

    if artist:
        send_artist_info(message.chat.id, artist)
    else:
        bot.send_message(message.chat.id, "К сожалению, не удалось найти исполнителя. Попробуйте позже!")


@bot.message_handler(func=lambda m: m.text == "Чарты VK и поиск песен 🔥")
def favorites_handler(message):
    # Здесь можно реализовать показ избранных исполнителей
    if message.text == 'Чарты VK и поиск песен 🔥':
        bot.send_message(message.from_user.id,'Поиск, просмотр чартов ВК и загрузка music по ' + '[👉тут👈](https://t.me/roskosniyhubbot)',
                     parse_mode='Markdown')


@bot.message_handler(func=lambda m: m.text == "Support")
def settings_handler(message):
    if message.text == 'Support':
        bot.send_message(message.from_user.id,'Если у вас возникли трудности, или хотели бы добавить что то в этом боте. ' + '[Tech support:](https://t.me/RYODAN_Qadery)',
                     parse_mode='Markdown')



# Запуск бота
if __name__ == "__main__":
    print("Бот запущен и готов к работе!")
    bot.polling(none_stop=True)