# -*- coding: utf-8 -*-

import random
import os.path
import json

def new_card_num():
    return ' '.join([str(i) for i in [random.randint(1000, 9999) for i in range(4)]])

def new_card(telegram_id, amount, currency, card_num=''):
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
    
def get_cards(bot, telegram_id):
    file_client = f'.\\storage\\{telegram_id}.json'
    if os.path.exists(file_client):
        with open(file_client, 'r') as file:
            client = json.load(file)
        msg = 'Ваши карты: '
        bot.send_message(telegram_id, msg)
        cards = client['cards']
        msg = ''
        for item in cards.items():
            msg += f"{item[0]} \nОстаток: {item[1]['amount']} {item[1]['currency']} \n\n"
    else:
        msg = 'У вас нет карт. Заведите новую.'

    bot.send_message(telegram_id, msg)
        
    

