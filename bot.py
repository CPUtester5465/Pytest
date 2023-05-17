import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, filters
import requests
from bs4 import BeautifulSoup

# Замените <YOUR_BOT_TOKEN> на токен вашего бота Telegram
bot_token = '6140734425:AAE60R_-aNBJJrTrooEw6CC8v_pbaeHpTaE'
# Замените <MANAGER_USERNAME> на username аккаунта менеджера
manager_username = 'timvista'

# Инициализация бота
bot = telegram.Bot(token=bot_token)

class Product:
    """Класс для представления информации о товаре"""
    def __init__(self, name, image_url):
        self.name = name
        self.image_url = image_url

def search_product(user_input):
    """Поиск товара по артикулу или названию на сайте Nike.com"""
    search_url = f'https://www.nike.com/w?q={user_input}'

    # Отправка GET-запроса на страницу поиска
    response = requests.get(search_url)

    if response.status_code == 200:
        # Создание объекта BeautifulSoup для парсинга HTML
        soup = BeautifulSoup(response.content, 'html.parser')

        # Поиск контейнера с товарами
        products_container = soup.find('div', class_='product-grid')

        if products_container:
            # Поиск первого товара в контейнере
            product_element = products_container.find('div', class_='product-card')

            if product_element:
                # Извлечение имени товара и URL изображения
                product_name = product_element.find('div', class_='product-card__title').text.strip()
                image_element = product_element.find('div', class_='product-card__hero-image')
                image_url = image_element.find('img')['src']

                return Product(product_name, image_url)

    # Если товар не найден, возвращаем None
    return None

def start(update, context):
    """Обработчик команды /start"""
    message = "Добро пожаловать! Введите артикул или название товара с сайта Nike.com:"
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def process_input(update, context):
    """Обработка введенного пользователем текста"""
    user_input = update.message.text

    # Поиск товара по артикулу или названию на сайте Nike.com
    product = search_product(user_input)

    if product:
        # Товар найден
        image_url = product.image_url
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=image_url)

        # Запрос размера
        context.user_data['product'] = product
        context.user_data['size'] = True
        message = "Введите размер товара:"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
    else:
        # Товар не найден
        message = "Товар не найден. Введите другой артикул или название товара."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def handle_size(update, context):
    """Обработка введенного размера"""
    size = update.message.text
    product = context.user_data.get('product')

    if product and context.user_data.get('size'):
        # Обработка размера товара
        context.user_data['size'] = size

        # Запрос количества товара
        message = "Введите количество товара:"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        context.user_data['quantity'] = True
    else:
        # Размер не ожидается
        message = "Извините, я не ожидал размера. Пожалуйста, попробуйте снова."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def handle_quantity(update, context):
    """Обработка введенного количества"""
    quantity = update.message.text
    product = context.user_data.get('product')

    if product and context.user_data.get('quantity'):
        # Обработка количества товара
        context.user_data['quantity'] = quantity

        # Запрос адреса доставки
        message = "Введите адрес доставки:"
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)
        context.user_data['address'] = True
    else:
        # Количество не ожидается
        message = "Извините, я не ожидал количество. Пожалуйста, попробуйте снова."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def handle_address(update, context):
    """Обработка введенного адреса"""
    address = update.message.text
    product = context.user_data.get('product')

    if product and context.user_data.get('address'):
        # Обработка адреса доставки
        context.user_data['address'] = address

        # Формирование сообщения с информацией о заказе
        order_info = f"Пользователь @{update.effective_user.username} оформил заказ:\n\n"
        order_info += f"Товар: {product.name}\n"
        order_info += f"Размер: {context.user_data['size']}\n"
        order_info += f"Количество: {context.user_data['quantity']}\n"
        order_info += f"Адрес доставки: {context.user_data['address']}"

        # Отправка сообщения на аккаунт менеджера
        bot.send_message(chat_id=manager_username, text=order_info)

        # Сообщение пользователю об успешном оформлении заказа
        success_message = "Ваш заказ успешно оформлен. Менеджер свяжется с вами для подтверждения."
        context.bot.send_message(chat_id=update.effective_chat.id, text=success_message)

        # Сброс данных пользователя
        context.user_data.clear()
    else:
        # Адрес не ожидается
        message = "Извините, я не ожидал адреса. Пожалуйста, попробуйте снова."
        context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def main():
    """Основная функция для запуска бота"""
    # Инициализация Updater и Dispatcher
    updater = Updater(bot_token, use_context=True)
    dispatcher = updater.dispatcher

    # Обработчики команд и текстовых сообщений
    start_handler = CommandHandler('start', start)
    input_handler = MessageHandler(Filters.text & ~Filters.command, process_input)
    size_handler = MessageHandler(Filters.text & ~Filters.command, handle_size)
    quantity_handler = MessageHandler(Filters.text & ~Filters.command, handle_quantity)
    address_handler = MessageHandler(Filters.text & ~Filters.command, handle_address)

    # Регистрация обработчиков
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(input_handler)
    dispatcher.add_handler(size_handler)
    dispatcher.add_handler(quantity_handler)
    dispatcher.add_handler(address_handler)

    # Запуск бота
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
