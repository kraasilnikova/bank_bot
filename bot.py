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
    def __init__(self, amount, currency):
        self.amount = amount
        self.currency = currency


@bot.message_handler(commands=['start'])
def start_handler(message):
    msg = 'Привет!'
    msg_out = bot.send_message(message.chat.id, msg)
    
    menu.main_menu(bot, message.chat.id)
    
@bot.message_handler(content_types=['text'])
def text_handler(message):
    
    if message.text == 'Новая карта':
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
        cards = card.get_cards(message.chat.id)
        msg = ''
        for item in cards.items():
            msg += f"{item[0]} \nОстаток: {item[1]['amount']} {item[1]['currency']} \n\n"
        msg_out = bot.send_message(message.chat.id, msg)

    elif message.text == 'Платежи':
        menu.payment_menu(bot, message.chat.id)
        
    elif message.text == 'Главное меню':
        menu.main_menu(bot, message.chat.id)

    elif message.text == 'Мобильный телефон' or message.text == 'Домашний интернет':
        if message.text == 'Мобильный телефон':
            msg = 'Введите номер телефона'
        else: 
            msg = 'Введите номер лицевого счёта'
        telegram_id = message.chat.id
        payment_type = message.text

        payment = Payment(telegram_id, payment_type)
        user_payment[telegram_id] = payment

        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_phone_number)

def ask_sum(message):
    Card.amount = message.text
    if not Card.amount.isdigit():
        msg = 'Цифрами, пожалуйста!'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_sum)
        return
    Card.amount = message.text
    ask_currency(message)

def ask_currency(message):
    menu.currency_menu(bot, message.chat.id)
    Card.currency = message.text
    if message.text != 'BY' or message.text != 'USD' or message.text != 'EUR' or message.text != 'RUB':
        msg = 'Выберите валюту из предложенных ниже!'
        msg_out = bot.send_message(message.chat.id, msg)
        bot.register_next_step_handler(msg_out, ask_currency)
        return
    Card.currency = message.text
    new_card = card.new_card(message.chat.id, Card.amount, Card.currency)
    msg = f"Карта успешно создана \nНомер карты: {new_card['card_num']}"
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

