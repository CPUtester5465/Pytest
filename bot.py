import telegram
import requests
from bs4 import BeautifulSoup

# Токен бота и username менеджера
TOKEN = '6140734425:AAE60R_-aNBJJrTrooEw6CC8v_pbaeHpTaE'
manager_username = 'timvista'

# Создание объекта бота
bot = telegram.Bot(token=TOKEN)

# Обработч команды /start
def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="3Привет! Введите артикул или название товара с сайта Nike.com")

# Обработчик сообщений
def echo(update, context):
    # Получение текста сообщения
    text = update.message.text

    # Поиск товара на сайте Nike.com
    url = 'https://www.nike.com/w?q=' + text
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    product = soup.find('div', {'class': 'product-card__body'})

    # Если товар не найден, ищем наиболее подходящую позицию
    if not product:
        product = soup.find('div', {'class': 'product-card__body'})

    # Получение ссылки на товар
    product_url = 'https://www.nike.com' + product.find('a')['href']

    # Сохранение ссылки на товар в контексте пользователя
    context.user_data['product_url'] = product_url

    # Отправка ссылки на товар
    context.bot.send_message(chat_id=update.effective_chat.id, text=product_url)

    # Запрос размера
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите размер товара")

    # Ожидание ответа пользователя
    context.user_data['product_size'] = None
    return 'SIZE'

# Обработчик ответа на запрос размера
def size(update, context):
    # Получение ответа пользователя
    size = update.message.text

    # Сохранение ответа в контексте пользователя
    context.user_data['product_size'] = size

    # Получение ссылки на товар из контекста пользователя
    product_url = context.user_data['product_url']

    # Поиск информации о товаре на сайте Nike.com
    response = requests.get(product_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    sizes = soup.find_all('div', {'class': 'size-grid-dropdown__item'})
    price = soup.find('div', {'class': 'product-price__wrapper'}).text.strip()

    # Поиск размера, который ввел пользователь
    size = next((s for s in sizes if context.user_data['product_size'] in s.text), None)

    # Если размер не найден, сообщаем об этом пользователю
    if not size:
        context.bot.send_message(chat_id=update.effective_chat.id, text="Размер не найден. Попробуйте еще раз.")
        return 'SIZE'

    # Получение цены товара
    price = price.split('\n')[0]

    # Формирование сообщения о товаре и его цене
    product_info = f"Товар: {text}\nРазмер: {size.text}\nЦена: {price}"

    # Отправка сообщения о товаре и его цене пользователю
    context.bot.send_message(chat_id=update.effective_chat.id, text=product_info)

    # Запрос количества товара
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите количество товара")

    # Ожидание ответа пользователя
    return 'QUANTITY'

# Обработчик ответа на запрос количества товара
def quantity(update, context):
    # Получение ответа пользователя
    quantity = update.message.text

    # Сохранение ответа в контексте пользователя
    context.user_data['product_quantity'] = quantity

    # Запрос адреса доставки
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите адрес доставки")

    # Ожидание ответа пользователя
    return 'ADDRESS'

# Обработчик ответа на запрос адреса доставки
def address(update, context):
    # Получение ответа пользователя
    address = update.message.text

    # Сохранение ответа в контексте пользователя
    context.user_data['product_address'] = address

    # Формирование сообщения о заказе
    order_info = f"Пользователь @{update.message.from_user.username} заказал товар {text} в количестве {context.user_data['product_quantity']} размера {context.user_data['product_size']} по адресу {context.user_data['product_address']}"

    # Отправка сообщения о заказе на аккаунт менеджера
    context.bot.send_message(chat_id=manager_username, text=order_info)

    # Отправка подтверждения заказа пользователю
    context.bot.send_message(chat_id=update.effective_chat.id, text="Ваш заказ принят. Спасбо!")

    # Очистка контекста пользователя
    context.user_data.clear()

    # Запрос нового товара
    context.bot.send_message(chat_id=update.effective_chat.id, text="Введите артикул или название товара с сайта Nike.com")

    # Ожидание ответа пользователя
    return 'PRODUCT'

# Создание обработчиков команд и сообщений
from telegram.ext import CommandHandler, MessageHandler, Filters, ConversationHandler
start_handler = CommandHandler('start', start)
product_handler = MessageHandler(Filters.text & (~Filters.command), echo)
size_handler = MessageHandler(Filters.text & (~Filters.command), size)
quantity_handler = MessageHandler(Filters.text & (~Filters.command), quantity)
address_handler = MessageHandler(Filters.text & (~Filters.command), address)
conv_handler = ConversationHandler(
    entry_points=[product_handler],
    states={
        'SIZE': [size_handler],
        'QUANTITY': [quantity_handler],
        'ADDRESS': [address_handler],
        'PRODUCT': [product_handler]
    },
    fallbacks=[],
    allow_reentry=True
)

# Добавление обработчиков в диспетчер
from telegram.ext import Updater
updater = Updater(token=TOKEN, use_context=True)
dispatcher = updater.dispatcher
dispatcher.add_handler(start_handler)
dispatcher.add_handler(conv_handler)

# Запуск бота
updater.start_polling()

