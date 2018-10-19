from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import bytes, int, str
from cmd import Cmd
from steemmonsters.api import Api
from steemmonsters.constants import xp_level, max_level_rarity
from steemmonsters.utils import generate_key, generate_team_hash
from beem.blockchain import Blockchain
from beem.nodelist import NodeList
from beem import Steem
from beem.account import Account
import json
import random
import hashlib
from datetime import date, datetime, timedelta
import requests
import logging
import random
import string
import math
import six
from time import sleep

log = logging.getLogger(__name__)

try:
    import colorama
    colorama.init()
except ImportError:
    colorama = None

try:
    from termcolor import colored
except ImportError:
    def colored(text, color):
        return text

def log(string, color, font="slant"):
    six.print_(colored(string, color))


class MyPrompt(Cmd):
    prompt = 'sm> '
    intro = "Welcome! Type ? to list commands"
    account = ""
    wallet_pass = ""
    api = Api()
    max_batch_size = 50
    threading = False
    wss = False
    https = True
    normal = False
    appbase = True
    log = logging.getLogger(__name__)
    verbosity = ["critical", "error", "warn", "info", "debug"][1]
    log.setLevel(getattr(logging, verbosity.upper()))    
    
    with open('config.json', 'r') as f:
        sm_config = json.load(f)

    nodes = NodeList()
    nodes.update_nodes()
    stm = Steem(node=nodes.get_nodes(normal=normal, appbase=appbase, wss=wss, https=https), num_retries=5, call_num_retries=3, timeout=15)
    b = Blockchain(mode='head', steem_instance=stm)
 
    def do_exit(self, inp):
        print("Bye")
        return True
    
    def help_exit(self):
        print('exit the application. Shorthand: x q Ctrl-D.')
 
    def do_set_account(self, inp):
        self.account = inp
        print("setting '{}'".format(inp))

    def do_set_wallet_password(self, inp):
        print("wallet password stored")
        self.wallet_pass = inp

    def do_reload_config(self, inp):
        if inp == "":
            inp = "config.json"
        with open(inp, 'r') as f:
            self.sm_config = json.load(f)

    def do_show_config(self, inp):
        tx = json.dumps(self.sm_config, indent=4)
        print(tx)        
 
    def do_show_cards(self, inp):
        if inp == "":
            cards = self.api.get_collection(self.sm_config["account"])
        else:
            cards = self.api.get_collection(inp)
        tx = json.dumps(cards, indent=4)
        print(tx)
 
    def do_show_deck(self, inp):
        tx = json.dumps(self.sm_config["decks"][inp], indent=4)
        print(tx) 
 
    def do_play(self, inp):
        if inp != "random" and inp not in self.sm_config["decks"]:
            print("%s does not exists" % inp)
        else:
            if inp != "random":
                deck_ids = self.sm_config["decks"][inp]
            else:
                deck_ids_list = list(self.sm_config["decks"].keys())
            statistics = {"won": 0, "battles": 0}
            play_round = 0
            cnt = 0
            self.stm.wallet.unlock(self.sm_config["wallet_password"])
            mana_cap = self.sm_config["mana_cap"]
            ruleset = self.sm_config["ruleset"]
            match_type = self.sm_config["match_type"]
            
            acc = Account(self.sm_config["account"], steem_instance=self.stm)
            
            response = self.api.get_card_details()
            cards = {}
            cards_by_name = {}
            for r in response:
                cards[r["id"]] = r
                cards_by_name[r["name"]] = r
            response = self.api.get_collection(acc["name"])
            mycards = {}
            for r in response["cards"]:
                if r["card_detail_id"] not in mycards:
                    mycards[r["card_detail_id"]] = {"uid": r["uid"], "xp": r["xp"], "name": cards[r["card_detail_id"]]["name"], "edition": r["edition"], "id": r["card_detail_id"]}
                elif r["xp"] > mycards[r["card_detail_id"]]["xp"]:
                    mycards[r["card_detail_id"]] = {"uid": r["uid"], "xp": r["xp"], "name": cards[r["card_detail_id"]]["name"], "edition": r["edition"], "id": r["card_detail_id"]}            
            
            while play_round < self.sm_config["play_counter"]:
                if inp == "random":
                    deck_ids = self.sm_config["decks"][deck_ids_list[random.randint(0, len(deck_ids_list) - 1)]]
                    print("Random mode: play %s" % str(deck_ids))
                play_round += 1
                secret = generate_key(10)
                monsters = []
                summoner = None
                summoner_level = 4
                for ids in deck_ids:
                    if isinstance(ids, str):
                        card_id = cards_by_name[ids]["id"]
                    else:
                        card_id = ids
                        
                    if summoner is None:
                        summoner = mycards[card_id]["uid"]
                        for x in xp_level:
                            if x["edition"] == mycards[card_id]["edition"] and x["rarity"] == cards[card_id]["rarity"]:
                                summoner_level = 0
                                for l in x["xp_level"]:
                                    if mycards[card_id]["xp"] >= x["xp_level"][l]:
                                        summoner_level = l
                        summoner_level = int(math.ceil(summoner_level / max_level_rarity[cards[card_id]["rarity"]] * 4))
                    else:
                        monsters.append(mycards[card_id]["uid"])
        
                deck = {"trx_id": "", "summoner": summoner, "monsters": monsters, "secret": secret}
                
                team_hash = generate_team_hash(deck["summoner"], deck["monsters"], deck["secret"])
                json_data = {"match_type":match_type, "mana_cap":mana_cap,"team_hash":team_hash,"summoner_level":summoner_level,"ruleset":ruleset}
                trx = self.stm.custom_json('sm_find_match', json_data, required_posting_auths=[acc["name"]])

                sleep(1)
                found = False
                for h in self.b.stream(opNames=["custom_json"]):
                    if h["id"] == 'sm_find_match':
                        if json.loads(h['json'])["team_hash"] == team_hash:
                            found = True
                            break
                start_block_find = h["block_num"]
                deck["trx_id"] =  h['trx_id']
                block_num = h["block_num"]
                
                match_cnt = 0
                open_match = []
                reveal_match = []
                while len(open_match) == 0 and match_cnt < 10:
                    match_cnt += 1
                    response = self.api.get_from_block(block_num - 10)
                    
                    for r in response:
                        if r["type"] == "sm_find_match":
                            player = r["player"]
                            if player not in open_match:
                                open_match.append(player)
                        elif r["type"] == "sm_team_reveal":
                            player = r["player"]
                            result = json.loads(r["result"])
                            if player in open_match:
                                open_match.remove(player)
                            if player not in reveal_match:
                                if "status" in result and "Waiting for opponent reveal." in result["status"]:
                                    reveal_match.append(player)
                            else:
                                if "status" in result and "Waiting for opponent reveal." not in result["status"]:
                                    reveal_match.remove(player)
                    # print("open %s" % str(open_match))
                    # print("Waiting %s" % str(reveal_match))
                response = ""
                cnt2 = 0
                trx_found = False
                while not trx_found and cnt2 < 10:
                    response = requests.get("https://steemmonsters.com/transactions/lookup?trx_id=%s" % deck["trx_id"])
                    if str(response) != '<Response [200]>':
                        sleep(2)
                    else:
                        if "trx_info" in response.json() and response.json()["trx_info"]["success"]:
                            trx_found = True
                        elif 'error' in response.json():
                            print(response.json()["error"])
                    cnt2 += 1                
                if 'error' in response.json():
                    print(response.json()["error"])
                    if "The current player is already looking for a match." in response.json()["error"]:
                        trx = self.stm.custom_json('sm_cancel_match', "{}", required_posting_auths=[acc["name"]])
                        sleep(3)
                    break
                else:
                    print("sm_find_match sucessfully broadcasted (%d - %s)" % (block_num, deck["trx_id"]))
                #     print(response.json())
                
                json_data = deck
                trx = self.stm.custom_json('sm_team_reveal', json_data, required_posting_auths=[acc["name"]])

                stop_time = datetime.utcnow()
                stop_block = self.b.get_current_block_num()
                response = ""
                cnt2 = 0
                
                find_match_cnt = 0
                deck_score = {}
                cnt = 0
                
                sleep(1)
                response = ""
                cnt2 = 0
                
                found_match = False
                while not found_match and cnt2 < 40:
                    response = requests.get("https://steemmonsters.com/battle/result?id=%s" % deck["trx_id"])
                    if str(response) != '<Response [200]>':
                        sleep(2)
                    elif 'Error' in response.json():
                        sleep(2)
                    else:
                        found_match = True
                    cnt2 += 1       
                winning_deck = None
                if cnt2 == 40:
                    print("Could not found opponent!")
                    trx = self.stm.custom_json('sm_cancel_match', "{}", required_posting_auths=[acc["name"]])
                    sleep(3)
                    continue
                winner = response.json()["winner"]
                team1_player = response.json()["player_1"]
                team2_player = response.json()["player_2"]
                if team1_player == winner:
                    print("match " + colored(team1_player, "green")+" - " + colored(team2_player, "red"))
                else:
                    print("match " + colored(team2_player, "green")+" - " + colored(team1_player, "red"))                

                if winner == acc["name"]:
                    statistics["won"] += 1

                statistics["battles"] += 1
                print("%d of %d matches won" % (statistics["won"], statistics["battles"]))
                if acc["name"] == response.json()["player_1"]:
                    print("Score %d -> %d" % (response.json()["player_1_rating_initial"], response.json()["player_1_rating_final"]))
                else:
                    print("Score %d -> %d" % (response.json()["player_2_rating_initial"], response.json()["player_2_rating_final"]))
                
 
    def do_stream(self, inp):
        block_num = self.b.get_current_block_num()
        match_cnt = 0
        open_match = []
        reveal_match = []
        try:
            while True:
                match_cnt += 1
                
                response = self.api.get_from_block(block_num)
                for r in response:
                    block_num = r["block_num"]
                    if r["type"] == "sm_find_match":
                        player = r["player"]
                        if player not in open_match:
                            open_match.append(player)
                            log("%s starts searching for a match (%d player searching)" % (player, len(open_match)), color="yellow")
                    elif r["type"] == "sm_team_reveal":
                        result = json.loads(r["result"])
                        player = r["player"]
                        if player in open_match:
                            open_match.remove(player)
                        if player not in reveal_match:
                            if "status" in result and "Waiting for opponent reveal." in result["status"]:
                                reveal_match.append(player)
                                log("%s waits for opponent reveal (%d player waiting)" % (player, len(reveal_match)), color="white")
                        else:
                            if "Waiting for opponent reveal." not in json.loads(r["result"])["status"]:
                                reveal_match.remove(player)
                        
                        if "battle" in result:
                            team1 = [{"id": result["battle"]["details"]["team1"]["summoner"]["card_detail_id"], "level": result["battle"]["details"]["team1"]["summoner"]["level"]}]
                            for m in result["battle"]["details"]["team1"]["monsters"]:
                                team1.append({"id": m["card_detail_id"], "level": m["level"]})
                            team1_player = result["battle"]["details"]["team1"]["player"]
                
                            team2 = [{"id": result["battle"]["details"]["team2"]["summoner"]["card_detail_id"], "level": result["battle"]["details"]["team2"]["summoner"]["level"]}]
                            for m in result["battle"]["details"]["team2"]["monsters"]:
                                team2.append({"id": m["card_detail_id"], "level": m["level"]})
                            team2_player = result["battle"]["details"]["team2"]["player"]
                            winner = result["battle"]["details"]["winner"]
                            if team1_player == winner:
                                print("match " + colored(team1_player, "green")+" - " + colored(team2_player, "red"))
                            else:
                                print("match " + colored(team2_player, "green")+" - " + colored(team1_player, "red"))
                            if team2_player in open_match:
                                open_match.remove(team2_player)
                            if team1_player in open_match:
                                open_match.remove(team1_player)
                            if team2_player in reveal_match:
                                reveal_match.remove(team2_player)
                            if team1_player in reveal_match:
                                reveal_match.remove(team1_player)                             
                            
                                # print("%s finished" % (player, len(reveal_match)))
                #print("open %s" % str(open_match))
                #print("Waiting %s" % str(reveal_match))
        except KeyboardInterrupt:
            print("exit..")
 
    def help_add(self):
        print("Add a new entry to the system.")
 
    def default(self, inp):
        if inp == 'x' or inp == 'q':
            return self.do_exit(inp)
 
        print("Default: {}".format(inp))
 
    do_EOF = do_exit
    help_EOF = help_exit
 
if __name__ == '__main__':
    MyPrompt().cmdloop()
