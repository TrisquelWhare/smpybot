from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
import sys
from datetime import datetime, timedelta, date
import time
import io
import json
import requests
from timeit import default_timer as timer
import logging



class Api(object):
    """ Access the steemmonsters API
    """
    __url__ = 'https://steemmonsters.com/'

    def get_card_details(self):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:        
            response = requests.get(self.__url__ + "cards/get_details")
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1            
        return response.json()

    def find_cards(self, card_ids):
        if isinstance(card_ids, list):
            card_ids_str = ','.join(card_ids)
        else:
            card_ids_str = card_ids
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "/cards/find?ids=%s" % card_ids_str)
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()

    def get_collection(self, player):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "cards/collection/%s" % player)
            cnt2 += 1
        return response.json()

    def get_player_details(self, player):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "players/details?name=%s" % player)
            cnt2 += 1
        return response.json()

    def get_for_sale(self):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:        
            response = requests.get(self.__url__ + "market/for_sale")
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1            
        return response.json()

    def get_purchases_settings(self):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:        
            response = requests.get(self.__url__ + "purchases/settings")
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1            
        return response.json()

    def get_from_block(self, block_num):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "transactions/history?from_block=%d" % block_num)
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()

    def get_transaction(self, trx):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "transactions/lookup?trx_id=%s" % trx)
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()

    def get_cards_stats(self):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "cards/stats")
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()

    def get_market_status(self, market_id):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 10:
            response = requests.get(self.__url__ + "market/status?id=%s" % market_id)
            if str(response) != '<Response [200]>':
                time.sleep(2)
            cnt2 += 1
        return response.json()

    def get_battle_result(self, ids):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 20:
            response = requests.get(self.__url__ + "battle/result?id=%s" % ids)
            if str(response) != '<Response [200]>':
                time.sleep(1)
            cnt2 += 1
        return response.json()

    def get_battle_status(self, ids):
        response = ""
        cnt2 = 0
        while str(response) != '<Response [200]>' and cnt2 < 20:
            response = requests.get(self.__url__ + "battle/status?id=%s" % ids)
            if str(response) != '<Response [200]>':
                time.sleep(1)
            cnt2 += 1
        return response.json()
