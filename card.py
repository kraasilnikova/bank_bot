# -*- coding: utf-8 -*-

import random
import os.path
import json
import time

def new_card_num():
    return ' '.join([str(i) for i in [random.randint(1000, 9999) for i in range(4)]])

def new_card(bot, telegram_id, amount, currency, card_num=''):
    try:
        if not card_num:
            card_num = ' '.join([str(i) for i in [random.randint(1000, 9999) for i in range(4)]])

        card = {f'{card_num}': {'currency': currency,
                                'amount': amount
                                }
                }

        file_client = f'.\\storage\\{telegram_id}.json'

        if os.path.exists(file_client):
            with open(file_client, 'r') as file:
                client = json.load(file)
        else:
            client = {'telegram_id': telegram_id,
                      'cards': {}}

        client['cards'].update(card)

        with open(file_client, 'w') as file:
            json.dump(client, file, indent=4, sort_keys=True)

        result = {'card_num': card_num,
                  'currency': currency,
                  'amount': amount
                  }
        return result
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)

def get_cards(bot, telegram_id):
    file_client = f'.\\storage\\{telegram_id}.json'
    try:
        if os.path.exists(file_client):
            with open(file_client) as file:
                client = json.load(file)
            cards = client['cards']
            msg = 'Ваши карты: \n\n'
            for item in cards.items():
                msg += f"{item[0]} \nОстаток: {item[1]['amount']} {item[1]['currency']} \n\n"
        else:
            msg = 'У вас нет карт. Заведите новую.'
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'

    bot.send_message(telegram_id, msg)

def subtracting_from_card(bot, telegram_id, number, amount):
    file_client = f'.\\storage\\{telegram_id}.json'
    try:
        with open(file_client) as file:
            client = json.load(file)
            cards = client['cards']
            for item in cards.items():
                if number == item[0]:
                    item[1]['amount'] -= int(amount)
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)

    try:
        with open(file_client, 'w') as file:
            json.dump(client, file, indent=4, sort_keys=True)
            for item in cards.items():
                result = {'card_num': item[0],
                          'currency': item[1]['currency'],
                          'amount': item[1]['amount']
                          }
            return result
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)


def save(bot, telegram_id, card, amount, payment_type, payment_number, date_time):
    try:
        file_client = f'.\\pay\\{telegram_id}.json'
        pay = {f'{date_time}': {'card': card,
                                'amount': amount,
                                'payment_type': payment_type,
                                'payment_number': payment_number
                                }
               }
        if os.path.exists(file_client):
            with open(file_client, 'r') as file:
                client = json.load(file)
        else:
            client = {'telegram_id': telegram_id,
                      'date': {}
                      }
        client['date'].update(pay)
        with open(file_client, 'w') as file:
            json.dump(client, file, indent=4, sort_keys=True)

        result = {'card': card,
                  'date': date_time,
                  'payment_type': payment_type,
                  'payment_number': payment_number
                  }
        return result
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)


def get_pay(bot, telegram_id):
    try:
        file_client = f'.\\pay\\{telegram_id}.json'
        if os.path.exists(file_client):
            with open(file_client, 'r') as file:
                client = json.load(file)

            date = client['date']
            msg = 'История платежей: \n\n'
            for item in date.items():
                msg += f"{item[0]} \nОплата за {item[1]['payment_type']} по номеру {item[1]['payment_number']}\nКарта: {item[1]['card']}\nСумма: {item[1]['amount']} руб.\n\n"
        else:
            msg = 'К сожалению, пока у Вас нет истории платежей.'
        bot.send_message(telegram_id, msg)
    except Exception:
        msg = 'Извините! Что-то пошло не так. Обратитесь позже.'
        bot.send_message(telegram_id, msg)
