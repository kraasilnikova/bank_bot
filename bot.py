# -*- coding: utf-8 -*-

import telebot
import config
import menu
import card
import json
import time
import requests as res

bot = telebot.TeleBot(config.TOKEN)

user_payment = {}

class Payment:
    def __init__(self, telegram_id, payment_type):
        self.telegram_id = telegram_id
        self.payment_type = payment_type
        self.payment_detail = ''
        self.payment_sum = 0.0
        
user_card = {}

class Card:
    def __init__(self, telegram_id, card_num, amount=0.0, currency='BY'):
        self.telegram_id = telegram_id
        self.amount = amount
        self.currency = currency
        self.card_num = card_num


@bot.message_handler(commands=['start'])
def start_handler(message):
    msg = 'Привет!'
    msg_out = bot.send_message(message.chat.id, msg)
    
    menu.main_menu(bot, message.chat.id)
    
@bot.message_handler(content_types=['text'])
def text_handler(message):
    
    if message.text == 'Новая карта':
        # рассчитать номер для новой карты
        card_num = card.new_card_num()
        # создать новый объек карточки и добавить его в общий список
        telegram_id = message.chat.id
        new_card = Card(telegram_id, card_num)
        user_card[telegram_id] = new_card

        msg = 'Введите сумму'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_sum)
        
    elif message.text == 'Курсы валют': 
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
        
    elif message.text == 'Мои карты':
        card.get_cards(bot, message.chat.id)

    elif message.text == 'Платежи':
        menu.payment_menu(bot, message.chat.id)
        
    elif message.text == 'Главное меню':
        menu.main_menu(bot, message.chat.id)

    elif message.text == 'Мобильный телефон' or message.text == 'Домашний интернет':
        if message.text == 'Мобильный телефон':
            msg = 'Введите номер телефона'
        else: 
            msg = 'Введите номер лицевого счёта'
        msg_out = bot.send_message(message.chat.id, msg)
        telegram_id = message.chat.id
        payment_type = message.text

        payment = Payment(telegram_id, payment_type)
        user_payment[telegram_id] = payment
        bot.register_next_step_handler(msg_out, ask_card)

def ask_card(message):
    menu.card_menu(bot, message.chat.id)
    card.get_cards(bot, message.chat.id)


def ask_sum(message):
    card_amount = message.text
    if not card_amount.isdigit():
        msg = 'Цифрами, пожалуйста! и целым числом'
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

    new_card = card.new_card(message.chat.id, user_card[message.chat.id].amount, user_card[message.chat.id].currency, user_card[message.chat.id].card_num)
    msg = f"Карта успешно создана \nНомер карты: {new_card['card_num']}\nСумма: {new_card['amount']} {new_card['currency']}"
    msg_out = bot.send_message(message.chat.id, msg)    

def ask_phone_number(message):
    phone_number = message.text
    if not phone_number.isdigit():
        msg = 'Чувак, перепроверь введённые данные'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_number)
        return

    telegram_id = message.chat.id
    payment = user_payment[telegram_id]
    payment.payment_detail = phone_number

    msg = 'Введите сумму'
    msg_out = bot.send_message(message.chat.id, msg)
    bot.register_next_step_handler(msg_out, ask_phone_sum)

def ask_phone_sum(message):
    phone_sum = message.text
    if not phone_sum.isdigit():
        msg = 'Сумма должна быть целым числом!'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_sum)
        return
    telegram_id = message.chat.id
    payment = user_payment[telegram_id]
    payment.payment_sum = phone_sum
    a = time.strftime("%d-%m-%Y  %H:%M:%S", time.localtime())
    msg = f'Спасибо! \nПользователь {payment.telegram_id} оплатил за {payment.payment_type} {payment.payment_sum} руб. по номеру {payment.payment_detail}.\n{a}'
    msg_out = bot.send_message(message.chat.id, msg)

    
bot.polling()

