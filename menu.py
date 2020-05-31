# -*- coding: utf-8 -*-

from telebot import types
import json

def main_menu(bot, chat_id):
    main_menu_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    currency_button = types.KeyboardButton('Курсы валют')
    payments_button = types.KeyboardButton('Платежи')
    my_cards_button = types.KeyboardButton('Мои карты')
    new_card_button = types.KeyboardButton('Новая карта')
    my_payments_button = types.KeyboardButton('История платежей')
    
    main_menu_buttons.add(currency_button, payments_button, my_cards_button, new_card_button, my_payments_button)
    bot.send_message(chat_id, 'Выберите операцию', reply_markup=main_menu_buttons)


def payment_menu(bot, chat_id):
    payment_menu_buttons = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)

    mobile_payment = types.KeyboardButton('Мобильный телефон')
    internet_payment = types.KeyboardButton('Домашний интернет')
    main_menu_button = types.KeyboardButton('Главное меню')

    payment_menu_buttons.add(mobile_payment, internet_payment, main_menu_button)
    bot.send_message(chat_id, 'Выберите платеж', reply_markup=payment_menu_buttons)
    
def currency_menu (bot, chat_id):
    payment_menu_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    
    by_payment = types.KeyboardButton('BY')
    usd_payment = types.KeyboardButton('USD')
    eur_payment = types.KeyboardButton('EUR')
    rub_payment = types.KeyboardButton('RUB')
    main_menu_button = types.KeyboardButton('Главное меню')

    payment_menu_buttons.add(by_payment, usd_payment, eur_payment, rub_payment, main_menu_button)
    return bot.send_message(chat_id, 'Выберите валюту', reply_markup=payment_menu_buttons)

def card_menu(bot, telegram_id, card_sum):
    payment_menu_buttons = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    try:
        file_client = f'.\\storage\\{telegram_id}.json'
        with open(file_client, 'r') as file:
            client = json.load(file)
        cards = client['cards']
        for item in cards.items():
            if int(item[1]['amount']) >= card_sum:
                tmp_card = types.KeyboardButton(f"{item[0]}: {item[1]['amount']} {item[1]['currency']}")
                payment_menu_buttons.add(tmp_card)

        main_menu_button = types.KeyboardButton('Главное меню')
        payment_menu_buttons.add(main_menu_button)

        msg_out = bot.send_message(telegram_id, 'Выберите номер катры, которой хотите оплатить', reply_markup=payment_menu_buttons)
        return msg_out
    except Exception:
        msg = 'Извините!Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)


