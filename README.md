# Python library for steem monsters!

Steem monsters is a fully decentralized trading card game on the steem blockchain.

## Installation
```
pip install beem termcolor colorama
```


## Commands
The steem monsters shell can be started with
```
python steemmonsters.py
```

```
sm> stream
```
This command shows the current battles and which player are participating

```
sm> play deck_name
```
`deck_name` is one of the stored decks defined in `config.json`.


```
sm> play random 
```
selects randomly a deck.

```
sm> show_deck deck_name 
```
shows deck `deck_name`.

## Setup the beem wallet
Create a new wallet, when not already done.
```
beempy createwallet
```
Add the posting key of the player by:
```
beempy addkey
```


## Configuration
```
{
    "wallet_password": "123",
    "account": "holger80",
    "mana_cap": 23,
    "ruleset": "Standard",
    "match_type": "Ranked",
    "decks": {
                "death1": ["Zintar Mortalis", "Haunted Spirit", "Skeleton Assassin", "Twisted Jester", "Haunted Spider", "Screaming Banshee", "Undead Priest"],
                "water1": ["Alric Stormbringer", "Naga Warrior", "Medusa", "Mischievous Mermaid", "Pirate Captain", "Crustacean King"],
                "fire1": ["Malric Inferno", "Serpentine Soldier", "Elemental Phoenix", "Goblin Shaman", "Fire Demon"],
    },
    "play_counter": 1
}
```

* `wallet_password` is the `beempy` wallet password
* `account`: steem user name of the player
* `mana_cap`: current mana cap
* `ruleset`: current rule set
* `match_type`: match type
* `decks` contains the different pre defined decks. There is no mana_cap check
* `play_counter` diffens how often a deck is played