# -*- coding: utf-8 -*-

import telebot
import config
import menu
import card
import json
import time
import os
import requests as res

bot = telebot.TeleBot(config.TOKEN)

user_payment = {}

class Payment:
    def __init__(self, telegram_id, payment_type):
        self.telegram_id = telegram_id
        self.payment_type = payment_type
        self.payment_detail = ''
        self.payment_sum = 0.0
        self.phone_number = 0
        
user_card = {}

class Card:
    def __init__(self, telegram_id, card_num, amount=0.0, currency='BY', number='0000'):
        self.telegram_id = telegram_id
        self.amount = amount
        self.currency = currency
        self.card_num = card_num
        self.number = number

@bot.message_handler(commands=['start'])
def start_handler(message):
    msg = 'Привет!'
    msg_out = bot.send_message(message.chat.id, msg)
    menu.main_menu(bot, message.chat.id)
    
@bot.message_handler(content_types=['text'])
def text_handler(message):

    if message.text == 'Новая карта':
        card_num = card.new_card_num()
        telegram_id = message.chat.id
        new_card = Card(telegram_id, card_num)
        user_card[telegram_id] = new_card
        msg = 'Введите сумму'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_sum)
        
    elif message.text == 'Курсы валют':
        try:
            response = res.get('https://belarusbank.by/api/kursExchange')
            curs = json.loads(response.text)
            usd = curs[0]
            usd_in = usd['USD_in']
            usd_out = usd['USD_out']
            eur_in = usd['EUR_in']
            eur_out = usd['EUR_out']
            rub_in = usd['RUB_in']
            rub_out = usd['RUB_out']
            msg = 'Курсы валют на сегодня:\nПокупка / продажа \nДоллар - ' + usd_in + ' / ' + usd_out + '\nЕвро - '+ eur_in + ' / ' + eur_out + '\nРоссийский рубль - ' + rub_in + ' / ' + rub_out
            msg_out = bot.send_message(message.chat.id, msg)
        except Exception:
            msg = 'Извините! Возникли проблемы с сайтом. Обратитесь позже.'
            bot.send_message(message.chat.id, msg)

    elif message.text == 'Мои карты':
        card.get_cards(bot, message.chat.id)

    elif message.text == 'Платежи':
        try:
            if not os.path.exists(f'.\\storage\\{message.chat.id}.json') or os.stat(
                    f'.\\storage\\{message.chat.id}.json').st_size == 0:
                msg = 'У Вас нет созданных карт, которыми можно было бы оплатить операцию. Создайте новую.'
                msg_out = bot.send_message(message.chat.id, msg)
                menu.main_menu(bot, message.chat.id)
            else:
                menu.payment_menu(bot, message.chat.id)
        except Exception:
            msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
            bot.send_message(message.chat.id, msg)

    elif message.text == 'Главное меню':
        menu.main_menu(bot, message.chat.id)

    elif message.text == 'История платежей':
        telegram_id = message.chat.id
        card.get_pay(bot, telegram_id)

    elif message.text == 'Мобильный телефон' or message.text == 'Домашний интернет':
        if message.text == 'Мобильный телефон':
            msg = 'Введите номер телефона'
        else: 
            msg = 'Введите номер лицевого счёта'
        new_payment = Payment(message.chat.id, message.text)
        user_payment[message.chat.id] = new_payment
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_number)

def ask_sum(message):
    card_amount = message.text
    if not card_amount.isdigit():
        msg = 'Цифрами и целым числом, пожалуйста :)'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_sum)
        return
    user_card[message.chat.id].amount = int(message.text)
    msg_out = menu.currency_menu(bot, message.chat.id)
    bot.register_next_step_handler(msg_out, ask_currency)

def ask_currency(message):
    if not message.text in ('BY', 'USD', 'EUR', 'RUB'):
        msg = 'Выберите валюту из предложенных ниже!'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_currency)
        return
    user_card[message.chat.id].currency = message.text
    new_card = card.new_card(bot, message.chat.id, user_card[message.chat.id].amount, user_card[message.chat.id].currency, user_card[message.chat.id].card_num)
    msg = f"Карта успешно создана \nНомер карты: {new_card['card_num']}\nСумма: {new_card['amount']} {new_card['currency']}"
    msg_out = bot.send_message(message.chat.id, msg)
    menu.main_menu(bot, message.chat.id)

def ask_phone_number(message):
    telegram_id = message.chat.id
    if not message.text.isdigit():
        msg = 'Чувак, перепроверь введённые данные'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_number)
        return
    user_payment[telegram_id].phone_number = message.text
    msg = 'Введите сумму'
    msg_out = bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(msg_out, ask_phone_sum)

def ask_phone_sum(message):
    if not message.text.isdigit():
        msg = 'Сумма должна быть целым числом!'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_sum)
        return
    user_payment[message.chat.id].payment_sum = message.text
    count = 0
    file_client = f'.\\storage\\{message.chat.id}.json'
    with open(file_client) as file:
        client = json.load(file)
        cards = client['cards']
        for item in cards.items():
            if int(item[1]['amount']) >= int(message.text):
                count = 1
        if count == 0:
            msg = 'Извините! У Вас недостаточно средств на карте/картах. Создайте новую карту.'
            msg_out = bot.send_message(message.chat.id, msg)
            menu.main_menu(bot, message.chat.id)
        else:
            msg_out = menu.card_menu(bot, message.chat.id, int(message.text))
            bot.register_next_step_handler(msg_out, ask_card)

def ask_card(message):
    flag = True
    count = 0
    telegram_id = message.chat.id
    payment = user_payment[telegram_id]
    card_num = message.text[: message.text.find(':')]
    payment.card_number = card_num
    file_client = f'.\\storage\\{telegram_id}.json'
    with open(file_client) as file:
        client = json.load(file)
        cards = client['cards']
        for item in cards.items():
            if card_num == item[0]:
                flag = False
                card.subtracting_from_card(bot, message.chat.id, payment.card_number, payment.payment_sum)
                a = time.strftime("%H:%M:%S %d-%m-%Y", time.localtime())
                card.save(bot, telegram_id, card_num, payment.payment_sum, payment.payment_type, payment.phone_number, a)
                msg = f'Спасибо! \nВы заплатили за {payment.payment_type} {payment.payment_sum} руб. по номеру {payment.phone_number} в {a}.'
                msg_out = bot.send_message(message.chat.id, msg)
                menu.main_menu(bot, message.chat.id)
                break
        if flag == True:
            msg = 'Внимательнее! Выберите номер карты, из перечисленных ниже'
            msg_out = bot.send_message(message.chat.id, msg)
            bot.register_next_step_handler(msg_out, ask_card)

bot.polling()

