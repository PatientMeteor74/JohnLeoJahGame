import math
import time
import random
from ast import Index
from math import floor
from random import randint
from time import sleep
from turtledemo.forest import randomize, start

#-----------------------------------------------------------------------------------#

player_health = 100
player_max_health = 100
player_armor = 0
player_dodge = 0.05
player_damage_multiplier = 1.0
player_effect_damage_multiplier = 1.0
player_effect_damage_taken_multiplier = 1.0
player_crit = 0.01
player_crit_mult = 2.0

player_vitality = 0
player_strength = 0
player_dexterity = 0
player_intelligence = 0

player_level = 1
xp = 0
xp_needed = 15

room_number = 0
floor_rooms = 0

delta = 0
player_turn = False

active_enemies = []
dead_enemies = []
player_gold = 0

player_max_energy = 10
player_energy = player_max_energy
rested = 0

player_stunned = False
player_active_effects = []

reward_due = False
is_boss_fight = False


#-----------------------------------------------------------------------------------

stat_gold_earned = 0
stat_rooms_explored = 0
stat_damage_dealt = 0
stat_enemies_killed = 0
stat_damage_taken = 0
stat_damage_avoided = 0
stat_energy_used = 0
depth = 0

#-----------------------------------------------------------------------------------

class Enemy:
    def __init__(self, name, size, health, armor, dodge, attacks, average_gold, average_xp, keywords):
        self.name = name
        self.size = size
        self.health = health
        self.damage_multiplier = 1.0
        self.damage_taken_multiplier = 1.0
        self.attacks = attacks
        self.average_gold = average_gold
        self.average_xp = average_xp
        self.max_health = health
        self.armor = armor
        self.dodge = dodge
        self.keywords = keywords
        self.enemy_effects = []
        self.attacks_in_turn = 1
        self.one_cd = []



    def attack(self):
        global player_stunned
        global player_active_effects
        global player_gold
        global exhaust

        for attack in self.one_cd:
           self.attacks.append(attack)
        self.one_cd.clear()
        for one_attack in range (0, self.attacks_in_turn):

            hit = True

            hits = 1

            time.sleep(0.5)

            attack_id = random.randint(0 , (len(self.attacks)-1))
            attack = self.attacks[attack_id]

            if len(self.attacks[attack_id].keywords) > 0:
                for keyword in self.attacks[attack_id].keywords:
                    match keyword:
                        case "Triple Strike":
                            hits *= 3
                        case "Double Strike":
                            hits *= 2
                        case "Self Harm":
                            self.health -= int(self.max_health / 10)
                            print(f"💥 The {self.name} inflicted {int(attack.damage / 2)} damage onto itself! [❤️{self.health}/{self.max_health}3]")
                            if self.health < 1:
                                self.die()



            print(f"\nThe {self.name} {self.attacks[attack_id].message}")

            for strike in range(0,hits):
                result = damage_player(int(self.attacks[attack_id].damage * self.damage_multiplier))

                if result == "dodge" or result == "block":
                    hit = False
                #Keywords
                if hit:
                    if len(self.attacks[attack_id].keywords) > 0:
                        for keyword in self.attacks[attack_id].keywords:
                            match keyword:
                                case "Stun":
                                    if random.random() < .4:
                                        player_stunned = True
                                case "Steal":
                                        time.sleep(1)
                                        if player_gold > 0:
                                            steal_amt = min(player_gold,random.randint(3, 5))
                                            player_gold -= steal_amt
                                            print(f"It grabbed {steal_amt}🪙!")
                                        else:
                                            print("You felt some grubby fingers touch yo dingaling through yo pocket")
                                            wait(2,3)
                                case "Daze":
                                    apply_effect(daze, player_active_effects, player_health, "player", 2, 1)
                                case "Ignite":
                                    apply_effect(burn, player_active_effects, player_health, "player", 4, 1)
                                case "strength":
                                    apply_effect(strength,self.enemy_effects,self.health,self.name,2,1)
                                case "Stun":
                                    if random.random()<.40:
                                        apply_effect(stun, player_active_effects, player_health, "player", 1, 1)
                                case "Infectious 1":
                                    apply_effect(infection, player_active_effects, player_health, "player", 2, 1)
                                case "frog_summon":
                                    if len(active_enemies) ==1:
                                        active_enemies.insert(0, create_enemy(r_toad))
                                        active_enemies.append(create_enemy(r_toad))
                                    elif active_enemies[2] == gigatoad and len(active_enemies) ==2:
                                        active_enemies.append(create_enemy(r_toad))
                                    elif active_enemies[1] == gigatoad and len(active_enemies) ==2:
                                        active_enemies.insert(0,create_enemy(r_toad))
                                    else:
                                        print("His froggies are already with him")



                                case "brittle":
                                    apply_effect(brittle, player_active_effects, player_health, "player", 2, 1)
                                case "Exhaust":
                                    apply_effect(exhaust,player_active_effects,player_health,"player",1,1)
                if len(self.attacks[attack_id].keywords) > 0:
                    for keyword in self.attacks[attack_id].keywords:
                        match keyword:
                            case "cd_1":
                                self.attacks.remove(attack)
                                self.one_cd.append(attack)




    def damage(self, amount):
        crit = False
        global stat_damage_dealt

        result = "hit"

        damage_taken = max(0, (amount - (random.randint(0, self.armor)))) * self.damage_taken_multiplier

        if random.random() <= player_crit:
            crit = True
            damage_taken = int((damage_taken * player_crit_mult) - self.armor)

        damage_taken = int(damage_taken)
        stat_damage_dealt += int(damage_taken)

        if self.health<0:
            self.health = 0

        if self.dodge > random.random():
            print(f"💨 Your attack misses the {self.name}, dealing no damage.")
            result = "dodge"
        elif amount <= 0:
            result = "hit"
        elif damage_taken <= 0:
            print(f"🛡️ Your attack bounces off the {self.name}, dealing no damage.")
            result = "block"
        elif crit == False:
            self.health -= damage_taken
            print(f"💥 You strike the {self.name} dealing {damage_taken} damage! [❤️{self.health}/{self.max_health}]")
            result = "hit"
        else:
            self.health -= damage_taken
            print(f"🎯💥 You critically strike the {self.name} dealing {damage_taken} damage! [❤️{self.health}/{self.max_health}]")
            result = "crit"

        if self.health <= 0:
            self.die()
        time.sleep(.05)
        return result

    def die(self):
        time.sleep(0.5)
        global player_gold
        global xp
        global stat_enemies_killed
        global dead_enemies

        stat_enemies_killed+=1
        self.enemy_debuffs = []

        reward_gold = int(self.average_gold * random.uniform(0.3, 1.7))
        reward_xp = int(self.average_xp * random.uniform(0.7, 1.3))

        print(f"☠️ It died, giving you {gain_gold(reward_gold)} and {gain_xp(reward_xp)}\n")

        if len(self.keywords) > 0:
            for keyword in self.keywords:
                match keyword:
                    case "Weapon Drop":
                        add_weapon(loot_weapons[random.randint(0,len(loot_weapons) - 1)])



        dead_enemies.append(self)
        time.sleep(0.5)

#-----------------------------------------------------------------------------------#

class Boss(Enemy):
    def __init__(self, name, size, health, armor, dodge, attacks, average_gold, average_xp, keywords, start_message, death_message):
        super().__init__(name, size, health, armor, dodge, attacks, average_gold, average_xp, keywords)
        self.death_message = death_message
        self.start_message = start_message

    enraged = False

    def enrage(self):
        if self.enraged == False:
            print(f"💢 {self.name} has enraged!\n")
            self.attacks_in_turn = 2
            self.enraged = True

    def damage(self, amount):
        super().damage(amount)
        if self.health <= self.max_health / 3 and self.health>0:
            self.enrage()

    def die(self):
        time.sleep(0.5)
        print(f"🪦 {self.death_message}")
        wait(1.5,3)
        super().die()

#-----------------------------------------------------------------------------------#

class PlayerAttack:
    def __init__(self, name, message, damage, energy, keywords, rarity):
        self.name = ""
        self.message = message
        self.damage = damage
        self.energy = energy
        self.keywords = keywords
        self.rarity = rarity

        for star in range(0,rarity):
            self.name += "★"

        self.name += f" {name}"

#-----------------------------------------------------------------------------------#

class EnemyAttack:
    def __init__(self, name, message, damage, keywords):
        self.name = name
        self.message = message
        self.damage = damage
        self.keywords = keywords

#-----------------------------------------------------------------------------------#

class Room:
    def __init__(self, description, name, spawn_chance, stumble_message):
        self.description = description
        self.name = name
        self.spawn_chance = spawn_chance
        self.stumble_message = stumble_message
    def enter(self):
        global player_turn
        global active_enemies
        global stat_rooms_explored
        global room_number
        global reward_due
        global is_boss_fight
        room_number += 1
        stat_rooms_explored += 1

        match self.name:
            case "combat":
                add_active_enemies(2, 3)
                random.shuffle(active_enemies)
                player_turn = True
                if random.random() < .1:
                    reward_due = True
                print("You turn a corner and are faced with a small group of foes...")
                fight(active_enemies)
            case "shop":
                print("You enter a shop. The shopkeeper grumbles something about 'Those damned Goblins...'")
                open_shop()
                choose_path()
            case "elite_combat":
                add_active_enemies(5, 7)
                random.shuffle(active_enemies)
                player_turn = True
                reward_due = True
                print("You open the door and what you see inside makes your pants a shade browner... ")
                fight(active_enemies)
            case "rest":
                print("You set up a small camp to recover health and energy")
                rested = 10
                heal_player((player_max_health - player_health) * random.uniform(0.5,1.0))
                choose_path()
            case "loot":
                print("You drool a little at the sight of:")
                find_loot()
                choose_path()
            case "mystery":
                print("You walk blindly through the fog..")
                #chance = random.
                mystery_encounter()
                choose_path()
            case "boss":
                # chance = random.
                is_boss_fight = True
                boss_fight()
                fight(active_enemies)
                choose_path()

#-----------------------------------------------------------------------------------#

class StatusEffect:
    def __init__(self, name, icon, description, duration, max_stacks):
        self.name = name
        self.icon = icon
        self.description = description
        self.max_stacks = max_stacks
        self.duration = duration
        self.target_name = ""

        stacks = 1

    def tick(self):
        self.duration -= 1
        if (self.duration < 1):
            self.expire_msg()

    def expire_msg(self):
        print(f"{self.icon} The {self.name} on {self.target_name} has expired.")


#-----------------------------------------------------------------------------------

class Item:
    def __init__(self, name, description, item_type, effect_amount, value):
        #Item rarity calculated based on value
        self.name = name
        self.description = description
        self.item_type = item_type
        self.effect_amount = effect_amount
        self.value = value
    def use(self):
        global player_health
        global player_energy
        global xp_needed
        global player_active_effects
        match self.item_type:
            case "health":
                heal_player(self.effect_amount)
            case "energy":
                add_energy(self.effect_amount, False)
                for effect in player_active_effects:
                    if effect == "Exhaust":
                        player_active_effects.remove(effect)


            case "experience":
                gain_xp(self.effect_amount+(xp_needed*.3))
                if not active_enemies:
                    test_for_level_up()
        print(f"You used your {self.name}")
        item_inventory.remove(self)

#---------------------------------Consumables------------------------------------------#

health_potion = Item("Health Potion", "Restores a small amount of health.", "health", 20, 30)
large_health_potion = Item("Large Health Potion", "Heals a substantial amount of health", "health", 50, 75)
enormous_health_potion = Item("Enormous Health Potion", "Heals you to full health", "health", 110, 110)
energy_potion = Item("Energy Potion", "Gain .", "energy", player_max_energy, 10)
tome_o_knoledge = Item("Tome of Knoledge","Grants you XP","experience",30,45)

items = [health_potion, large_health_potion, enormous_health_potion, energy_potion, tome_o_knoledge]

#------------------------------------Rooms---------------------------------------------#
combat_room = Room("♢ A path with the chatters and growls of enemies emanating from within.", "combat", .5, "You stumble into another room full of enemies!")
shop_room = Room("♢ A well-lit corridor with a sign hanging labelled 'The Shop (NO GOBLINS ALLOWED)'", "shop", .2, "You stumble into a shop!")
elite_room = Room("♢ A heavily fortified door with ominous shadows visible in the light peeking through below.", "elite_combat", .2, "You stumbled into a massively dangerous room!")
rest_room = Room("♢ An abandoned campsite which appears safe for resting.", "rest", .1, "You stumble into an abandoned campsite...")
loot_room = Room("♢ A dark room with a promising glimmer in the center.", "loot", .1, "You stumble into a room with loot!")
encounter_room = Room("♢ A shrouded room, you can barely glimpse a silhouette in the fog.", "mystery", 100.1, "You stumble into a foggy, mysterious room.")
boss_room = Room("⛋ A huge doorway dirtied with old blood. Prepare yourself.", "boss", .005, "You stumble into something even worse...")

rooms = [combat_room, shop_room, elite_room, rest_room, loot_room, encounter_room, boss_room]

#-------------------------------------Wait------------------------------------#

def wait(total_time, periods):
    for i in range(0, periods):
        time.sleep(total_time / periods)
        print(".",end="")
    time.sleep(total_time/periods)
    print("")

#-------------------------------------Room Logic------------------------------------#

def spawn_rooms():

    possible_rooms = []
    while not (1 <= len(possible_rooms) <= 4):
        possible_rooms = [room for room in rooms if random.random() <= room.spawn_chance]
    return possible_rooms

def choose_path():

    global room_number
    global floor_rooms

    #Erry other room
    if room_number < floor_rooms - 1:

        spawned_rooms = spawn_rooms()

    #Shop before boss
    elif room_number == floor_rooms - 1:
        spawned_rooms = [shop_room]

    #Boss
    else:

        spawned_rooms = [boss_room]

    chosen = False

    time.sleep(1)

    while not chosen:
        print("\nYou are presented with a number of branching doorways...\n")

        for i,room in enumerate(spawned_rooms):
            print(f"[{i + 1}]: {room.description}")

        print(f"[{len(spawned_rooms) + 1}]: 🔎 Pause for introspection and deep thought.")
        try:
            choice = int(input("\nInput your choice:\n"))
        except ValueError:
            continue
        global player_turn

        if 1 <=choice <= len(spawned_rooms):
            chosen = True
            selected_room = spawned_rooms[choice - 1]
            selected_room.enter()



        elif choice == len(spawned_rooms) + 1:
            print(f"[1]: 📊 See Stats\n"
                  f"[2]: 🗡️ Examine Gear\n"
                  f"[3]: 🧰 Use Item\n"
                  f"[4]: ◀ Back")
            c_choice = int(input("Input your choice:\n"))
            match c_choice:
                case 1:
                    see_stats()
                case 2:
                    examine_gear()
                case 3:
                    for i, item in enumerate(item_inventory):
                        print(f"[{i + 1}]: Use {item.name}")
                    item_choice = int(input("Choose an item to use:"))
                    try:
                        item_inventory[item_choice - 1].use()
                    except:
                        print("youre foolish!")

                case 4:
                    continue
                case _:
                    print("youre foolish!")

def randomize_floor_rooms():
    global floor_rooms
    global room_number

    room_number = 0
    floor_rooms = random.randint(10,12)#8,12

def go_deeper():
    global depth
    depth += 1
    plural = "s" if depth > 1 else ""
    print(f"..you've made it {depth} floor{plural} in, with an unknowable number to go...")
    randomize_floor_rooms()
    choose_path()

#--------------------------------------------------------------------------------------#

def open_shop():
    global player_gold
    global loot_weapons
    global items
    global item_inventory
    print("Welcome to the shop pal, either buy something or get outta here!")
    shop_items = random.sample(items, k=min(len(items), 2))
    shop_weapons = random.sample(loot_weapons, k=min(len(loot_weapons), 2))

    in_shop = True
    while in_shop:
        print(f"\nYou have 🪙{player_gold} left...\n")
        for i,item in enumerate(shop_items):
            print(f"[{i + 1}]: {item.name} (🪙{item.value})")
        for j,weapon in enumerate(shop_weapons):
            print(f"[{len(shop_items) + j + 1}]: {weapon.name} (🪙{int((weapon.rarity ** 1.5) * 20)})")
        print(f"[{len(shop_items) + len(shop_weapons) + 1}]: Leave the shop")
        try:
            choice = int(input("\nWhaddya wanna buy? Make it quick, bub.")) - 1
            if 0 <= choice < len(shop_items):
                selected_item = shop_items[choice]
                if player_gold >= selected_item.value:
                    player_gold -= selected_item.value
                    item_inventory.append(selected_item)
                    shop_items.remove(selected_item)
                    print(f"Purchased: {selected_item.name}")
                else:
                    print("Not enough gold, stop wasting my time and pick somethin else!")
            elif len(shop_items) <= choice < len(shop_items) + len(shop_weapons):
                weapon_choice = choice - len(shop_items)
                selected_weapon = shop_weapons[weapon_choice]
                weapon_price = int((selected_weapon.rarity ** 1.5) * 20)
                if player_gold >= weapon_price:
                    player_gold -= weapon_price
                    add_weapon(selected_weapon)
                    shop_weapons.remove(selected_weapon)
                else:
                    print("Not enough gold. Maybe save up, bub.")
            elif choice == len(shop_items) + len(shop_weapons):
                print("Get outta here!\n")
                in_shop = False
            else:
                print("How about you pick a real option and stop loitering!")
        except ValueError:
            print("Enter a valid number.")

#--------------------------------------------------------------------------------------#

def find_loot():
    global player_gold
    loot = ["pile_gold","treasure_chest"]
    found_loot = random.choice(loot)
    time.sleep(.5)
    wait(1.5,3)
    print("")
    match found_loot:
        case "pile_gold":
            print("A Pile of gold!")
            time.sleep(1)
            found_gold = random.randint(15, 35)
            found_gold += 3*player_level
            print(f"you collect it all and get  {gain_gold(found_gold)}!")
        case "treasure_chest":
            found_gold = random.randint(5, 15)
            found_gold += 2*player_level
            print(f"A treasure chest with {gain_gold(found_gold)}!")
            time.sleep(1)
            print("you rummage through the gold and find")
            wait(1.5,3)
            print("\n")
            t_loot_list = ["weapon","gold","tome"]
            t_loot = random.choice(t_loot_list)
            match t_loot:
                case "weapon":
                    print("A weapon!")
                    time.sleep(1)
                    add_weapon(loot_weapons[random.randint(0, len(loot_weapons) - 1)])
                case "gold":
                    print("More gold!")
                    time.sleep(1)
                    found_gold = random.randint(10, 20)
                    found_gold += 2 * player_level
                    print(f"+{gain_gold(found_gold)}")
                case "tome":
                    print("A Tome of Knowledge!")
                    time.sleep(1)
                    item_inventory.append(tome_o_knoledge)

#--------------------------------------------------------------------------------------#

def mystery_encounter():
    global player_gold
    global player_health
    global player_max_health
    wait(2,3)
    encounters = ["Molten Gold", "The Gambler", "Cursed Library", "Goblin Gym"]
    encounter = random.choice(encounters)

#---------------------------------THE GAMBLER FUNCTIONS--------------------------------#
    def create_deck():
        deck = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] * 4  # 4 suits
        random.shuffle(deck)
        return deck

    def calculate_hand(hand):
        hand = [int(card) for card in hand if isinstance(card, int) or card.isdigit()]
        total = sum(hand)
        if total > 21 and 11 in hand:
            hand[hand.index(11)] = 1  # Treat an Ace as 1 if over 21
            total = sum(hand)
        return total

    def display_hand(player, hand):
        print(f"{player} hand: {hand} (total: {calculate_hand(hand)})")
        time.sleep(1)


    # -----------------------------------ENCOUNTER CALLS--------------------------------#

    match encounter:
        case "Molten Gold":
            print("You find a churning crucible of molten gold...\n")
            print("[1]: Reach in...\n"
                  "[2]: Ignore it")
            choice = int(input("Input your choice:"))

            gold_increase = 0
            try:
                while choice == 1:
                    damage = int(player_max_health * random.uniform(0.09,0.15))
                    player_health -= damage
                    print(f"You scoop some out and grit your teeth as it burns away your skin... +{gain_gold((20 + gold_increase) * random.uniform(0.8,1.2))}")
                    print(f"💔 You take {damage} damage [❤️{player_health}/{player_max_health}]")

                    gold_increase += 4
                    if player_health < 0:
                        game_over()

                    print("...\n")
                    print("[1]: More... Gold...\n"
                          "[2]: Leave")
                    choice = int(input("Input your choice:"))

                else:
                    if gold_increase == 0:
                        print("You decide its not worth it and move on")
                    else:
                        print("You look at your burned hand and decide against your greed")
                    return
            except ValueError:
                print("glongugs")
                return

        case "Cursed Library":
            print("The small doorway opens up into a library with walls and ceiling extending out of sight. A mysterious book catches your eye, already open...\n")
            print("[1]: Open the book...\n"
                  "[2]: Try to find a way through")
            choice = input("Input your choice:")
            in_library = True

            hp_price = 1

            while in_library == True:

                if choice == "1":
                    print(f"The book feeds your mind with knowledge from beyond, +{gain_xp(random.randint(6,8) * player_level)}.\n")

                elif random.random()< 0.66:
                    print("You run past countless aisles of bookshelves, but feel you are exactly where you were before...\n")
                else:
                    print("You see what looks to be an exit")
                    test_for_level_up()
                    in_library = False
                    break

                print("[1]: Read more\n"
                      "[2]: Try to find a way though...")
                choice = input("Input your choice:")


                print(f"You feel a small piece of yourself fade away into the abyss around you...")
                player_max_health -= hp_price
                if player_health > player_max_health:
                    player_health = player_max_health

                print(f"💔 You lost {hp_price} max HP [❤️{player_health}/{player_max_health}]")

                hp_price += 1

                if player_health < 0:
                    game_over()

            else:
                print("You manage to make it out...\n")
                test_for_level_up()

        case "Goblin Gym":
            print("You find yourself in a broken down goblin gym...\n")
            print("[1]: Hit a goblish workout\n"
                  "[2]: Stay small...")
            choice = int(input("Input your choice:"))

            if choice == 1:
                print("\nYou go crazy on the weights...")
                wait(1.5,3)
                if random.random() < 0.66:
                    print("You finish the workout and get a nasty pump!")
                    increase_strength(1)
                else:
                    print("The improvised equipment snaps mid-bench, and a plate falls toward you head. bummer...")
                    damage_player(random.randint(5,10))
            else:
                print("You remember today is leg day...")


        case "The Gambler":
            play_bj = False
            print("\nYou find a man waiting at a table surrounded by gold...")
            print('Dealer: "A game of blackjack?"\n')
            time.sleep(1.5)
            choice = 3
            while choice != 1 or choice != 2:
                try:
                    bet = max(10, int(player_gold * 0.25))
                    print(f"Current Gold: 🪙{player_gold}")
                    print(f"[1] Of course! (Bet: 🪙{bet})\n"
                          "[2] No, thanks")

                    choice = int(input("Choose option: "))

                    if choice != 1 and choice != 2:
                        raise ValueError  # Raise an error if the input is not 1 or 2
                except ValueError:
                    print("Enter a valid option: 1 or 2")
            match choice:
                case 1:
                    if player_gold >= bet:
                        play_bj = True
                    else:
                        print('Dealer: "No money, no game"')
                case 2:
                    print('"Dealer: Youre missing out..."')
            while choice == 1 or 2:


                # Player turn
                if play_bj:
                    play_bj = False
                    player_gold -= 10
                    deck = create_deck()
                    player_hand = [deck.pop(), deck.pop()]
                    dealer_hand = [deck.pop(), deck.pop()]

                    display_hand("You", player_hand)
                    time.sleep(1)
                    display_hand("Dealer", [dealer_hand[0], "?"])
                    time.sleep(1)
                    while calculate_hand(player_hand) < 21:
                        action = int(input("[1] Hit \n"
                                       "[2] Stand"))
                        if action == 1:
                            player_hand.append(deck.pop())
                            time.sleep(1)
                            display_hand("You", player_hand)
                            if calculate_hand(player_hand) > 21:
                                print("You busted! Dealer wins.")
                                print('Dealer: (counting his pile of coins) "Better luck next time"')
                        elif action == 2:
                            break
                        else:
                            print("Not available action")
                    # Dealer turn
                    while calculate_hand(dealer_hand) < 17 and calculate_hand(player_hand)<22:
                        dealer_hand.append(deck.pop())

                    display_hand("Dealer", dealer_hand)

                    # Determine winner
                    player_total = calculate_hand(player_hand)
                    dealer_total = calculate_hand(dealer_hand)

                    if dealer_total > 21:
                        time.sleep(1)
                        print("Dealer busted! You win.")
                        print(f'Dealer: "Here is you prize..." +{gain_gold(bet*2)}')
                    elif player_total > dealer_total and player_total<22:
                        time.sleep(1)
                        print("You win!")
                        print(f'Dealer: "Here is you prize..." +{gain_gold(bet*2)}')
                    elif player_total == dealer_total:
                        time.sleep(1)
                        print("It's a tie!")
                        print(f'Dealer: "Here is your money back..." +{gain_gold(bet)}')
                    else:
                        time.sleep(1)
                        print("Dealer wins.")
                        print('Dealer: (counting his pile of coins) "Better luck next time"')
                    time.sleep(1)
                    if random.random()<.15:
                        print('Dealer:(Starts counting massive pile of coins)')
                        for i in range(1,4):
                            time.sleep(1)
                            print(f'Dealer:"{i}..."')
                        time.sleep(2)
                        print("You get bored and decide to leave")
                        break
                    print("You feel a sudden urge to play again\n")
                    time.sleep(1.5)

                    bet = max(10, player_gold * .25)

                    print(f"Current Gold: 🪙{player_gold}")
                    print(f"[1] Give in.(Bet: 🪙{bet})\n"
                          "[2] Cower from opportunity")
                    choice1 = int(input("Choose option:"))
                    match choice1:
                        case 1:
                            continue
                        case 2:
                            print('Dealer: "Youre missing out..."')
                            time.sleep(1)
                            break
                        case _:
                            print("You stumble on your words\n"
                                  'Dealer: "Again it is..."')



#--------------------------------------------------------------------------------------#

def boss_fight():
    global depth

    floor_bosses = boss_lists[depth]

    base_boss = floor_bosses[random.randint(0, len(floor_bosses) - 1)]

    new_boss = Boss(
        base_boss.name,
        base_boss.size,
        base_boss.health,
        base_boss.armor,
        base_boss.dodge,
        base_boss.attacks,
        base_boss.average_gold,
        base_boss.average_xp,
        base_boss.keywords,
        base_boss.start_message,
        base_boss.death_message
    )

    print(f"\n👿 {new_boss.start_message}")
    active_enemies.append(new_boss)

def add_active_enemies(min_weight,max_weight):
    global depth
    global enemies

    floor_enemies = enemy_lists[depth]

    total_weight = random.randint(min_weight,max_weight)

    large_enemy_favor = 1 + (depth * 0.25)

    while total_weight > 0:

        affordable_enemies = []

        for enemy in floor_enemies:
            if enemy.size <= total_weight:
                affordable_enemies.append(enemy)

        weights = [min(1, (1 / (enemy.size / large_enemy_favor))) for enemy in affordable_enemies]
        normalized_weights = [weight / sum(weights) for weight in weights]

        chosen_enemy = random.choices(affordable_enemies, weights=normalized_weights, k=1)
        base_enemy = chosen_enemy[0]

        total_weight -= base_enemy.size

        new_enemy = Enemy(
            base_enemy.name,
            base_enemy.size,
            base_enemy.health,
            base_enemy.armor,
            base_enemy.dodge,
            base_enemy.attacks,
            base_enemy.average_gold,
            base_enemy.average_xp,
            base_enemy.keywords,
            )

        active_enemies.append(new_enemy)
#--------------------------------------------------------------------------------------#
def create_enemy(base_enemy):
    new_enemy = Enemy(
        base_enemy.name,
        base_enemy.size,
        base_enemy.health,
        base_enemy.armor,
        base_enemy.dodge,
        base_enemy.attacks,
        base_enemy.average_gold,
        base_enemy.average_xp,
        base_enemy.keywords,
    )
    return new_enemy
#--------------------------------------------------------------------------------------#
def game_init():
    print("Welcome to freaky text dungeon, mmm..........")
    print("[1]: Enter the Dungeon...\n"
          "[2]: Turn back")
    choice = int(input("Input your choice: \n"))
    if choice == 1:
        print("You enter the dungeon, your heart filled with dread...")
        randomize_floor_rooms()
        choose_path()
    elif choice == 2:
        return
    else:
        print("Please pick 1 or 2")
        game_init()


#=====================================ENEMY ATTACKS=======================================#
slomp = EnemyAttack("Slomp Attack", "attempts to gludgeon you with its slomp...",5,  ["Daze"])
spit = EnemyAttack("Spit", "Spits moldy goop at your eye...",0,  ["Infectious 1"])
stab = EnemyAttack("Stab"," lunges forward to stab you...",4,  ["Exhaust"])
d_slash = EnemyAttack("Dagger Slash","quickly slashes towards your chest with a dagger...",5,  [])
body_slam = EnemyAttack("Body Slam","throws itself toward you with great force...", 4,  ["Stun"])
b_rage = EnemyAttack("Blind Rage", "attacks you in a blind rage...",2, ["Double Strike"])
expl_cask = EnemyAttack("Explosive Cask", "throws an explosive cask at you...", 7, [])
b_roll = EnemyAttack("Barrel Roll", "whirls a cask your feet...", 4,  [])
scream = EnemyAttack("Scream", "unleashes a piercing shriek...", 0, ["Daze"])
bite = EnemyAttack("Bite", "attempts to bite you...", 4, [])
s_slam = EnemyAttack("Shovel Slam","tries to smash your head with a shovel...",6,["Stun"])
poo_throw = EnemyAttack("Poo Throw","throws some poo at you...",0,[])
pick_pock = EnemyAttack("Pick Pocket","lunges for your pockets...",0,["Steal"])
smash = EnemyAttack("Smash","prepares to slam down on you...",6,["Stun"])
dice = EnemyAttack("Dice","prepares to chop you to pieces...",2,["Triple Strike"])
slice = EnemyAttack("Slice","attempts to slice into you...",6,[])
f_blast = EnemyAttack("Fire Blast","unleashes a burst of fire towards you...",4,["Ignite"])
m_blast = EnemyAttack("Magic Blast","blasts a wave of magical energy at you...",5,[])
tongue = EnemyAttack("Tongue Swipe","flicks its tongue at you...", 2,  ["Infectious 1"])
d_curse = EnemyAttack("Death Curse","channels the power of the death realm...",9,["Self Harm"])
f_ravage = EnemyAttack("Fly Ravage","casts a swarm of flies toward you...",1,["Triple Strike", "Infectious 1"])
s_slash = EnemyAttack("Sword Slash","swings its sword...",5,[])
rage = EnemyAttack("Rage","enters a rage...",0,["Strength"])
chomp = EnemyAttack("Chomp","chomps down on you...",12,[])
snipe = EnemyAttack("Snipe","takes the shot...",17,["cd_1"])
scope = EnemyAttack("Scope","steadies it's aim...",0,[])

enemy_attacks = [slomp, stab, d_slash, body_slam, b_rage, expl_cask, b_roll, scream, bite,s_slam, poo_throw, pick_pock, smash, dice, slice, f_blast, m_blast]
#--------------------------------------BOSS ATTACKS---------------------------------------#
#--Giga Toad--#2

frog_call = EnemyAttack("Frog Call","unleashes a froggie cronie call...",0,["frog_summon"])
leap = EnemyAttack("Leap","leaps above you, smashing down...",10,["Stun"])
mega_tongue = EnemyAttack("Mega Tongue","lashes it tongue at your face...",5,["Infectious 2"])
#-------------#

#-Slomp Emperor#
mega_slomp = EnemyAttack("Mega slomp","casts a glorg of slomp at you...",8,["Exhaust"])
#-------------#

#=========================================================================================#

#=====================================FLOOR 1 ENEMIES=======================================#
goblin = Enemy("🔺Grouchy Goblin",               1, 18, 2, 0.1,[stab,d_slash, bite], 2,8,[])
skele = Enemy("🔺Skeleton Solider",              1, 22,4, 0.05,[stab,b_rage],1,12,[])
slomp_monster = Enemy("🔺Slompster",             2, 60, 0, 0,[slomp, bite],10,20,[])
grogus = Enemy("🔺Grogus",                       3, 90, 0, 0.05, [body_slam,expl_cask,body_slam,b_rage],20,25,[])
living_ore = Enemy("🔺Living Ore",               2, 24, 10,0, [body_slam, scream],20,8,[])
clkwrk_gremlin = Enemy("🔺Clockwork Gremlin",    1, 6, 10, 0.1, [bite],2,8,[])
wailing_wisp = Enemy("🔺Wailing Wisp",           1, 2, 0, 0.66, [scream,m_blast],0,12,[])
lost_serf = Enemy("🔺Lost Serf",                 1, 18,0,.05,[b_rage,s_slam,poo_throw],8,6,[])
rob_goblin = Enemy("🔺Goblin Robber",            1, 13,2,.25,[stab,pick_pock],15,4,[])
angry_weapons = Enemy("🔺Pile of Angry Weapons", 2, 13, 6, 0.25,[slice, dice], 0,10,["Weapon Drop"])
goblin_mech = Enemy("🔺Goblin Mech",             3, 60, 8, 0,[f_blast, smash], 20,15,[])
m_frog = Enemy("🔺Mutant Frog",                  1, 13,0,.2,[tongue,bite,spit],5,6,[])
r_toad = Enemy("🔺Royal Toad",                   1, 14,4,.1,[bite,s_slash,rage,poo_throw],0,0,[]) #Boss exclusive enemy

enemies_floor_1 = [goblin, skele, slomp_monster,living_ore,clkwrk_gremlin,wailing_wisp,lost_serf,rob_goblin,angry_weapons]

#=====================================FLOOR 2 ENEMIES=======================================#
ghoulem = Enemy("🔺Gravestone Ghoulem",           4,150,2,0,[stab,smash, m_blast],35,45,[])
s_bandit = Enemy("🔺Shrouded Bandit",             2,24,0,.2,[slice,pick_pock,dice],18,8,[])
l_prisoner = Enemy("🔺Lost Prisoner",             1,36,0,.05,[b_rage,body_slam],10,12,[])
clkwrk_wizard = Enemy("🔺Clockwork Wizard",       2,24,10,.1,[m_blast,d_curse],14,22,[])
flies_man = Enemy("🔺Flies Man",                  3,30,0,.1,[bite,poo_throw,f_ravage],20,35,[])
c_markman = Enemy("🔺Cloaked Marksman",           2,20,0,.3,[snipe,scope],8,12,[])

enemies_floor_2 = [clkwrk_gremlin, wailing_wisp, rob_goblin,angry_weapons, ghoulem, goblin_mech, grogus,s_bandit,clkwrk_wizard,l_prisoner,flies_man,c_markman]

#=====================================FLOOR 3 ENEMIES=======================================#

enemies_floor_3 = [slomp_monster,living_ore, clkwrk_gremlin, wailing_wisp, rob_goblin, angry_weapons, ghoulem, goblin_mech, grogus,clkwrk_wizard,s_bandit]

#===================================================================================#

#=====================================FLOOR 4 ENEMIES=======================================#

enemies_floor_4 = [ghoulem,flies_man,goblin_mech,grogus]

#===================================================================================#

enemies = [goblin, skele, slomp_monster, grogus, living_ore, clkwrk_gremlin, wailing_wisp, lost_serf, rob_goblin, ghoulem, angry_weapons, goblin_mech,m_frog]
enemy_lists = [enemies_floor_1,enemies_floor_2,enemies_floor_3,enemies_floor_4]

#=====================================BOSSES=======================================#

slomperor = Boss("👹Slomp Emperor", 10, 250, 0, 0.05,[slomp, spit, smash,chomp,mega_slomp], 50,100,[], "I vow the whole world will be one day slomped... starting with YOU!!!", "Argh... At least I never ran a... democracy... ")
gigagoblin = Boss("👹Goblin Juggernaut", 10, 150, 3, .01, [poo_throw, smash, scream, bite, body_slam, pick_pock, stab], 50, 100, [], "GGRGRRRRAAAAAAAAAAAAAAAAGHHHHHH", "mrrrrrrhhhhh...gulk..")

gigatoad = Boss("👹Irradiated Toad", 10, 200, 0, .20, [frog_call,leap,mega_tongue,chomp],50,100,[],"*stomp* *stomp* Stay away from my marsh, ribbit","glaaagalgaa")
c_monstrosity = Boss("👹Clockwork Monstrosity", 10, 60, 32, .05, [scream, smash, f_blast, m_blast],50,100,[],"(Loud ticking and clanging noises)","(tick tock tick.. tock.... tick......")

bosses = [gigatoad]#c_monstrosity,slomperor, gigagoblin

bosses_floor_1 = [gigatoad]#slomperor, gigagoblin

bosses_floor_2 = [gigatoad]#, c_monstrosity

bosses_floor_3 = [gigatoad]# c_monstrosity

bosses_floor_4 = [gigatoad, c_monstrosity]

boss_lists = [bosses_floor_1,bosses_floor_2,bosses_floor_3,bosses_floor_4]

#===================================================================================#

#=====================================PLAYER ATTACKS======================================#
shortsword = PlayerAttack("Simple Shortsword", "You swing your sword...", 6, 3, [], 1)
greatsword = PlayerAttack("Greatsword","You have heave your greatsword",10,6,["Splash 1"],1)
stick = PlayerAttack("Whacking Stick", "You whack that fella head smoove off...", 2, 1, [], 1)
iron_battleaxe = PlayerAttack("Battleaxe", "You forcefully swing your battleaxe...", 14, 8, [], 1)

g_dagger = PlayerAttack("Goblin Dagger", "You slash twice with your dagger...", 4, 2, ["Double Strike"], 1)
anvil_staff = PlayerAttack("Anvil Staff", "You conjure an anvil high in the air...", 24, 8, ["Stun"], 2)
glock = PlayerAttack("Goblin Glock ", "You unload your clip...", 4, 7, ["Double Strike","Triple Strike"], 3)
uzi = PlayerAttack("Enchanted Uzi", "You spray and pray...", 4, 10, ["Decuple Attack","Aimless"], 3)
boomerang = PlayerAttack("Boomerang", "You chuck your boomerang at they noggin, HARD...", 4, 2, ["Return"], 1)
monk_staff = PlayerAttack("Monk Staff", "You smach that fella head smoove off with focus...", 4, 0, [], 2)
f_bucket = PlayerAttack("Fire Bucket", "You dump a torrent of fire towards the enemies...", 0, 8, ["Ignite","Splash 2"], 3)
torch = PlayerAttack("Old Torch", "You somehow relight the torch and swing...",4,5,["Ignite"], 1)
r_scythe = PlayerAttack("Reaping Scythe","You take a wide swipe with your scythe...",10,7,["Omni Strike","Aimless"], 3)
tp_hammer = PlayerAttack("1001LB Hammer","With tremendous effort, you wildly swing the immense hammer...",60,18,["Aimless"], 3)
l_staff = PlayerAttack("Light Staff", "You raise the staff high into the air, producing a blinding light ...",0,6,["Daze","Omni Strike","Aimless"], 3)
flare_gun = PlayerAttack("Flare Gun", "You fire off a blinding flare ...",0,2,["Daze"], 2)
g_launcher = PlayerAttack("Gob-omb Launcher", "A sizzling bomb flies through the air...",10,5,["Splash 2","Aimless"], 2)
rapier = PlayerAttack("Rapier","You send out a flurry of attacks...",6,5,["Triple Strike"],1)
fly_jar = PlayerAttack("Jar of Flies", "You release the flies upon your foes...",2,8,["Infectious 1","Triple Attack","Aimless"], 3)
g_amoeba = PlayerAttack("Giant Amoeba", "You goopily swing the giant microbe...",2,3,["Infectious 2"], 2)


weapons = [shortsword,iron_battleaxe,g_dagger,stick,anvil_staff,glock,uzi,boomerang,monk_staff,f_bucket,torch,r_scythe,tp_hammer,g_launcher,greatsword,rapier,l_staff,flare_gun,fly_jar,g_amoeba]

#=========================================================================================#

loot_weapons = [g_dagger,anvil_staff,glock,uzi,boomerang,monk_staff,f_bucket,torch,r_scythe,tp_hammer,g_launcher,rapier,l_staff,flare_gun,fly_jar,g_amoeba]

#=========================================================================================#

burn = StatusEffect("Burn", "🔥", "set ablaze!", 1, 1)
infection = StatusEffect("Infection", "🦠", "infected!", 2, 99)
daze = StatusEffect("Daze", "🌀", "dazed!", 2, 1)
strength = StatusEffect("Strength", "🦾", "strengthened!", 2, 1)
stun = StatusEffect("Stun","💫","stunned!",1,1)
brittle = StatusEffect("Brittle","⛓️‍💥","embrittled!",1,1)
exhaust = StatusEffect("Exhaust","💤","ehxausted!",1,99)

#========================================Debuff Ticking==========================================#

def apply_effect(effect, target_list, target_hp, target_name, effect_duration, effect_stacks):

    new_effect = StatusEffect(
        effect.name,
        effect.icon,
        effect.description,
        effect_duration,
        effect.max_stacks
    )

    new_effect.stacks = effect_stacks
    new_effect.target_name = target_name

    reapply = False
    effect_to_refresh = new_effect

    for status_effect in target_list:
        if status_effect.name == effect.name:
            reapply = True
            effect_to_refresh = status_effect

    if target_hp > 0:
        # Effect not on target
        if reapply == False:
            target_list.append(new_effect)

            stack_text = ""
            if effect_stacks > 1:
                stack_text = f" (x{effect_stacks})"

            print(f"{effect.icon} The {target_name} was {effect.description}{stack_text}")

        elif effect_to_refresh.max_stacks == 1:
            #Effect on target but lower duration/stacks
            if effect_to_refresh.duration < effect_duration:
                effect_to_refresh.duration = effect_duration
                print(f"{effect.icon} The {target_name} had its {effect.name} refreshed.")

                # Debuff already on target
            else:
                        print(f"The {target_name} already had {effect.name}.")
        else:
            if effect_to_refresh.duration < effect_duration:
                effect_to_refresh.duration = effect_duration
            effect_to_refresh.stacks = min(effect_to_refresh.max_stacks, effect_to_refresh.stacks + effect_stacks)

            print(f"{effect.icon} The {target_name} was {effect.description} (x{effect_to_refresh.stacks})")


def enemy_effect_tick(enemy):

    enemy.damage_multiplier = 1.0
    enemy.damage_taken_multiplier = 1.0

    for active_effect in enemy.enemy_effects:

        match active_effect.name:
            case "Burn":
                damage = int(4 * active_effect.stacks)
                if enemy.health > 0:
                    enemy.health -= damage
                    print(f"{active_effect.icon} The {enemy.name} takes {damage} damage from {active_effect.name}. [❤️{enemy.health}/{enemy.max_health}]")
                    if enemy.health <= 0:
                        enemy.die()
            case "Daze":
                if active_effect.duration > 1:
                    enemy.damage_multiplier *= (0.66 ** active_effect.stacks)
            case "Strength":
                if active_effect.duration > 1:
                    enemy.damage_multiplier *= (1.5 * active_effect.stacks)
            case "Infection":
                damage = int(1 * active_effect.stacks)
                if enemy.health > 0:
                    enemy.health -= damage
                    print(f"{active_effect.icon} The {enemy.name} takes {damage} damage from {active_effect.name}. [❤️{enemy.health}/{enemy.max_health}]")

                    active_effect.stacks = math.ceil(min(active_effect.max_stacks,active_effect.stacks * 1.5))
                    print(f"{active_effect.icon} The {enemy.name}'s infection is increasing (x{active_effect.stacks})")

                    if enemy.health <= 0:
                        enemy.die()
            case "Brittle":
                if active_effect.duration > 1:
                    enemy.damage_taken_multiplier *= (1.5 * active_effect.stacks)


        active_effect.tick()
        if (active_effect.duration < 1):
            enemy.enemy_effects.remove(active_effect)

def player_effect_tick():
    global player_effect_damage_multiplier
    global player_effect_damage_taken_multiplier
    global player_health

    player_effect_damage_multiplier = 1.0
    player_effect_damage_taken_multiplier = 1.0

    for active_effect in player_active_effects:

        match active_effect.name:
            case "Burn":
                damage = int(4 * active_effect.stacks)
                if player_health > 0:
                    player_health -= damage
                    print(f"{active_effect.icon} You take {damage} damage from {active_effect.name}. [❤️{player_health}/{player_max_health}]")
                    if player_health <= 0:
                        game_over()
            case "Daze":
                if active_effect.duration > 1:
                    player_effect_damage_multiplier *= (0.66 ** active_effect.stacks)
            case "Strength":
                if active_effect.duration > 1:
                    player_effect_damage_multiplier *= (1.5 * active_effect.stacks)
            case "Infection":
                damage = int(1 * active_effect.stacks)

                if player_health > 0:
                    player_health -= damage
                    print(f"{active_effect.icon} You take {damage} damage from {active_effect.name}. [❤️{player_health}/{player_max_health}]")

                    active_effect.stacks = math.ceil(min(active_effect.max_stacks,active_effect.stacks * 1.5))
                    print(f"{active_effect.icon} Your infection is increasing (x{active_effect.stacks})")

                    #Test death
                    if player_health <= 0:
                        game_over()

            case "Brittle":
                if active_effect.duration > 1:
                    player_effect_damage_taken_multiplier *= (1.5 * active_effect.stacks)
            case "Stun":
                player_stunned = True


        active_effect.tick()
        if (active_effect.duration < 1):
            player_active_effects.remove(active_effect)


#==========================================================#

#Player Inventory

player_weapons = [shortsword,iron_battleaxe,stick,greatsword]

active_weapons = []
player_max_weapons = 3.5
player_accessories = []
item_inventory = []

#----------------------------------Affect-Player-Stats---------------------------------#

def damage_player(amount):
    global player_health
    global player_armor
    global stat_damage_avoided
    global stat_damage_taken
    global player_effect_damage_taken_multiplier

    result = "hit"

    damage_taken = int(max(0, (amount - (random.randint(0,player_armor)))) * player_effect_damage_taken_multiplier)

    if random.random() <= player_dodge:
        print(f"💨 You dodge out of the way, unaffected!")
        result = "dodge"
        stat_damage_avoided += int(amount)
    elif amount == 0:
        result = "hit"
    elif damage_taken <= 0:
        print(f"🛡️ The attack is deflected by your armor, dealing no damage!")
        result = "block"
        stat_damage_avoided += int(amount)
    else:
        player_health -= damage_taken
        print(f"💔 You take {damage_taken} damage. [❤️{player_health}/{player_max_health}]")
        stat_damage_avoided += int(amount - damage_taken)
        stat_damage_taken += damage_taken


    if player_health <= 0:
        game_over()

    return result
        
def heal_player(amount):
    global player_health
    global player_intelligence

    healing_taken = int(amount)

    inspiration = 1

    if random.random() < 0.05 + (player_intelligence * 0.05):
        inspiration = 2

    healing_taken *= inspiration
    healing_taken = min(healing_taken, player_max_health - player_health)
    player_health += healing_taken

    if inspiration == 1:
        print(f"💞 You restore {healing_taken} health [❤️{player_health}/{player_max_health}]")
    else:
        print(f"💞💞 Eureka! You restore {healing_taken} health [❤️{player_health}/{player_max_health}]")

def add_energy(amount, respect_max):
    global player_energy
    global player_max_energy
    global player_intelligence

    inspiration = False

    if respect_max == True and (player_energy + amount) > player_max_energy:
        amount = (player_max_energy - player_energy)

    if random.random() < 0.05 + (player_intelligence * 0.05):
        inspiration = True
        respect_max = False
        amount *= 2

    if amount > 0:

        player_energy += amount

        if inspiration:
            print(f"Eureka! you gained⚡️{amount} energy [⚡️{player_energy}/{player_max_energy}]")
        else:
            print(f"you gained⚡️{amount} energy [⚡️{player_energy}/{player_max_energy}]")
    else:
        print(f"you gained no energy {player_energy}/{player_max_energy}]")


def recharge_energy():
    global player_energy
    global player_max_energy
    global rested
    global exhaust

    player_energy = player_max_energy
    for effect in player_active_effects:
        if "Exhaust" in player_active_effects:
            lost_energy = 0
            if player_energy-3*effect.stacks>=0:
                player_energy -= 3
                lost_energy += 3
            else:
                lost_energy += math.abs(player_energy)
                player_energy = 0

            exhaust -= 1
        #print(f"You're exhausted and lose ⚡️{lost_energy}")

    if rested > 0:
        print(f"You are well rested...")
        add_energy(rested, False)
        rested = 0


def gain_gold(amount):
    global player_gold
    global stat_gold_earned

    stat_gold_earned += int(amount)

    gained_amount = int(amount)
    player_gold += gained_amount
    return f"🪙{gained_amount}"

def gain_xp(amount):
    global xp


    inspiration = 1
    """
    if random.random() < 0.05 + (player_intelligence * 0.025):
        inspiration = 2
    """

    gained_amount = int(amount * (1 + (player_intelligence * .05)))
    xp += gained_amount
    if inspiration == 1:
        return f"💠{gained_amount}"
    else:
        return f"💠{int(gained_amount/2)} and eureka! An additional 💠{int(gained_amount/2)}"

#---------------------------------Fighting-Enemy-------------------------------------#
combat_actions = ["Attack", "Rest", "Run Away", "Use Item"]
def fight(enemies: list[Enemy]):
    global player_turn
    global combat_actions
    global player_attacks
    global enemy_attacks
    global active_enemies
    global dead_enemies
    global player_stunned
    global player_max_energy
    global player_energy
    global rooms
    global item_inventory
    global player_active_effects
    global player_effect_damage_multiplier
    global reward_due
    global rested
    global active_weapons
    time.sleep(1)
    print("\nIt's time to fight\n"
          "You're facing...")
    for i in range(0,len(enemies)):
        print(f"[ A {enemies[i].name} with ❤️{enemies[i].health} ]")
    time.sleep(1)
    while dispose_corpses(enemies) > 0 and player_health > 0:

        if player_turn: #Player Turn Start
            print("\n------------------- Your Turn -------------------\n")
            player_effect_tick()
            recharge_energy()
            shuffle_weapons()
            while player_turn and dispose_corpses(enemies) > 0: #Player Action Loop

                if player_stunned: # Check for if player is stunned
                    print("You are stunned and cannot act this turn!")
                    for i in range(0,3):
                        time.sleep(.66)
                        print(".",end="")
                    time.sleep(.66)
                    player_stunned = False  # Reset stun status
                    player_turn = False  # End player's turn
                    for weapon in active_weapons:
                        player_weapons.append(weapon)
                    continue
                print(f"\nHealth: [❤️{player_health}/{player_max_health}]") #Start of player turn
                for i in range(len(combat_actions)):

                    if combat_actions[i] == "Use Item":
                        if len(item_inventory) > 0:
                            print(f"[{i + 1}]: {combat_actions[i]}")  # Printing Combat actions
                        else:
                            print()
                            #continue
                    else:
                        print(f"[{i + 1}]: {combat_actions[i]}")  # Printing Combat actions

                try:
                    print(f"Current Energy:⚡️{player_energy}")
                    chosen_action = int(input("\nChoose an action:")) - 1 #Promt to choose action
                except ValueError:
                    print("blud, you gotta enter an int")
                    continue
                try: #tests if combat_actions[chosen_action] will result in an error
                    test = combat_actions[chosen_action]
                except IndexError or ValueError:
                    print("That's not an available action, try again.")
                    continue
                if combat_actions[chosen_action] == "Run Away": #----------Run away action
                    if player_energy >= math.floor(player_max_energy/3):
                        print(f"-⚡️{math.floor(player_max_energy / 3)}")
                        print("You pee your pants a little and sprint towards the first escape you see...")
                        time.sleep(1.0)
                        player_energy -= math.floor(player_max_energy / 3)
                        if random.random() <.65 and not is_boss_fight:
                            active_enemies = []
                            reward_due = False
                            escape_room = rooms[random.randint(0, len(rooms)) - 1]
                            print(escape_room.stumble_message)
                            for weapon in active_weapons:
                                player_weapons.append(weapon)
                            test_for_level_up()
                            escape_room.enter()
                        elif is_boss_fight:
                            print("Theres is no escape")
                            for weapon in active_weapons:
                                player_weapons.append(weapon)
                        else:
                            print("The opps block yo path, you cooked, blud")
                            player_turn=False
                    else:
                        print("You're too exhausted to run away!")

                elif combat_actions[chosen_action] == "Attack":#--------------Attack action
                    if len(active_weapons)>0:
                        print("")
                        for i in range(len(active_weapons)):
                            weapon = active_weapons[i]

                            if weapon.damage > 0 and len(weapon.keywords) == 0:
                                print(f"[{i + 1}]: {weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier * player_effect_damage_multiplier)}]")
                            elif len(weapon.keywords) > 0 and weapon.damage > 0:
                                print(f"[{i + 1}]: {weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier * player_effect_damage_multiplier)}] ❇")
                            elif len(weapon.keywords) > 0:
                                print(
                                    f"[{i + 1}]: {weapon.name} [⚡️{weapon.energy}] ❇")


                        print(f"[{len(active_weapons) + 1}]: Cancel action")
                        try:
                            chosen_attack = int(input("\n Choose an attack:"))
                            if chosen_attack == (len(active_weapons) + 1):
                                continue
                            test = active_weapons[chosen_attack - 1].energy
                        except (IndexError, ValueError):
                            print("invalid choice, try again")
                            continue
                        if player_energy-active_weapons[chosen_attack-1].energy < 0:
                            print("You don't have enough energy for that attack :(")
                            print()
                        else:
                            if len(enemies) > 1 and "Aimless" not in active_weapons[(chosen_attack-1)].keywords:
                                for i in range(len(enemies)):
                                    print(f"[{i + 1}]: attack {enemies[i].name} ❤️[{enemies[i].health}/{enemies[i].max_health}]")
                                try:
                                    chosen_enemy = int(input("Choose an enemy to attack:"))
                                    test = player_attack(active_weapons[(chosen_attack-1)], enemies[(chosen_enemy-1)])
                                except (IndexError, ValueError):
                                    #continue
                                    print()
                            else:
                                player_attack(active_weapons[(chosen_attack-1)], enemies[0])
                                if player_energy>0:
                                    #continue
                                    print()
                    else:
                        print("you got no wepon")
                elif combat_actions[chosen_action] == "Rest":
                    if player_energy > 1:
                        print(f"You reserve your remaining energy for later....")
                        rested = int(player_energy / 2)
                    time.sleep(1.0)
                    player_turn = False
                    for weapon in active_weapons:
                        player_weapons.append(weapon)
                    #shuffle_weapons()
                elif combat_actions[chosen_action] == "Use Item": #------Use Item action
                    for i,item in enumerate(item_inventory):
                        print(f"[{i+1}]: Use {item.name}")
                    item_choice = int(input("Choose an item to use:"))
                    try:
                        item_inventory[item_choice - 1].use()
                    except IndexError:
                        print("Not an available action")
                        #continue
                else: #-------------Input # other that options
                    print("That's not an available action, try again.")
                    #continue

            if dispose_corpses(enemies) > 0:
                time.sleep(1)
                print("\n------------------- Enemy Turn -------------------\n")
        else: #Enemy Turn

            for enemy in enemies:
                enemy_effect_tick(enemy)
                if enemy.health > 0:
                    enemy.attack()

            player_turn = True

            time.sleep(1)

    else:
        end_fight(player_health)

def shuffle_weapons():
    global player_weapons
    global active_weapons
    global player_max_weapons
    active_weapons = []
    random.shuffle(player_weapons)
    if len(player_weapons) >= math.ceil(player_max_weapons):
        for i in range(0, math.ceil(player_max_weapons)):
            active_weapons.append(player_weapons.pop())
    else:
        for i in range(0, len(player_weapons)):
            active_weapons.append(player_weapons.pop())

def dispose_corpses(enemies: list[Enemy]):
    global dead_enemies

    for enemy in dead_enemies:
        enemies.remove(enemy)

    dead_enemies = []

    return len(enemies)

def end_fight(health):
    global player_max_health
    global reward_due
    global active_weapons
    global is_boss_fight
    for weapon in active_weapons:
        player_weapons.append(weapon)
    if health == player_max_health:
        print("You made it out unscathed!")
    elif health >= player_max_health / 2:
        print("You made it out with a couple scratches.")
    elif health >= player_max_health / 4:
        print("You barely made it out...")
    else:
        print("You barely made it to the exit, let alone lived...")
    for enemy in enemies:
        enemy.enemy_debuffs = []
    if reward_due == True and health>0:
        print("Seems like the enemies were guarding something:")
        reward_due = False
        find_loot()

    test_for_level_up()

    if is_boss_fight:
        print("You see an ominous stairwell, and you have no choice but to descend.")
        is_boss_fight = False
        wait(3,3)
        go_deeper()
    choose_path()

    time.sleep(1.5)
#--------------------------------------------------------------------------------------#

def player_attack(PlayerAttack, Enemy):
    global player_energy
    global stat_energy_used
    global active_enemies

    #Energy
    player_energy -= PlayerAttack.energy
    stat_energy_used += PlayerAttack.energy

    #Attack message
    print(PlayerAttack.message)

    #Hit amount
    hits = 1

    #Attack amount
    attacks = 1

    #Attack Keywords
    for keyword in PlayerAttack.keywords:
        match keyword:
            case "Double Attack":
                attacks *= 2
            case "Triple Attack":
                attacks *= 3
            case "Decuple Attack":
                attacks *= 10

    for a in range (0,attacks):
        targets = []
        initial_target = Enemy

        # Aimless
        if "Aimless" in PlayerAttack.keywords:
                if not targets:
                    if len(active_enemies) > 1:
                        initial_target = active_enemies[random.randint(0, len(active_enemies) - 1)]
                    elif len(active_enemies) == 1:
                        initial_target = active_enemies[0]
                    else:
                        return

        target_id = active_enemies.index(initial_target)

        # Attack Keywords
        for keyword in PlayerAttack.keywords:
            match keyword:
                case "Splash 2":
                    targets.append(active_enemies[target_id])
                    if target_id -1 >= 0:
                        targets.append(active_enemies[target_id-1])
                    if target_id +1 < len(active_enemies):
                        targets.append(active_enemies[target_id+1])
                case "Omni Strike":
                    for enemy in active_enemies:
                        targets.append(enemy)
                case "Splash 1":
                    if target_id - 1 >= 0:
                        active_enemies[target_id-1].damage(int((PlayerAttack.damage * player_damage_multiplier * player_effect_damage_multiplier)/2))
                case "Double Strike":
                    hits *= 2
                case "Triple Strike":
                    hits *= 3
                case "Decuple Strike":
                    hits *= 10


        if not targets:
            targets.append(initial_target)

        # Hit Keywords
        for target in targets:
            for i in range(0,hits):
                if target.health > 0:
                    # Damage Target
                    time.sleep(.15)
                    result = target.damage(int(PlayerAttack.damage * player_damage_multiplier * player_effect_damage_multiplier))
                    if result != "dodge":
                        for keyword in PlayerAttack.keywords:
                            match keyword:
                                case "Ignite":
                                    apply_effect(burn, target.enemy_effects, target.health, target.name,4,1)
                                case "Daze":
                                    apply_effect(daze, target.enemy_effects, target.health, target.name,3,1)
                                case "Splash 1": #this is stupid
                                    if target_id + 1 < len(active_enemies):
                                        active_enemies[target_id + 1].damage(
                                            int((PlayerAttack.damage * player_damage_multiplier * player_effect_damage_multiplier) / 2))
                                case "Infectious 1":
                                    apply_effect(infection, target.enemy_effects, target.health, target.name,2,1)
                                case "Infectious 2":
                                    apply_effect(infection, target.enemy_effects, target.health, target.name,3,1)
                                case "brittle":
                                    apply_effect(brittle, target.enemy_effects, target.health, target.name,3,1)
                    else:#this is stupid
                        for keyword in PlayerAttack.keywords:#this is stupid
                            match keyword:#this is stupid
                                case "Splash 1":#this is stupid
                                    if target_id + 1 < len(active_enemies):#this is stupid
                                        active_enemies[target_id + 1].damage(int((PlayerAttack.damage * player_damage_multiplier * player_effect_damage_multiplier) / 2))#this is stupid
            dispose_corpses(active_enemies)
    for keyword in PlayerAttack.keywords:
        match keyword:
            case "Return":
                print(f"Your {PlayerAttack.name} returned!")
                break
            case _:
                player_weapons.append(PlayerAttack)
                active_weapons.remove(PlayerAttack)
                break
    else:
        player_weapons.append(PlayerAttack)
        active_weapons.remove(PlayerAttack)
    time.sleep(1.5)

#-----------------------------------------------------------------------------------#

def add_weapon(weapon_to_add):
    global player_weapons
    print(f"You got a new weapon: '{weapon_to_add.name}'")
    choice = input(f"[1]: Take the weapon\n"
                   f"[2]: Leave the weapon\n")
    if choice == "1":
        if len(player_weapons) <= 40:
            player_weapons.append(weapon_to_add)
            print(f"You gain a weapon: '{weapon_to_add.name}'")
        else:
            print((f"Your weapon bag is already full, choose a weapon to replace:\n"))

            for i in range(len(player_weapons)):
                weapon = player_weapons[i]
                print(f"[{i + 1}]: replace {weapon.name}")
            print("")

            replace_choice = input()
            replace_choice = int(replace_choice) - 1

            if replace_choice >= 1 & replace_choice <= player_max_weapons:
                print(f"You replaced your '{player_weapons[replace_choice].name}' with '{weapon_to_add.name}'")
                player_weapons[replace_choice] = weapon_to_add

            elif choice == 0:
                print("You discard the new weapon")

            else:
                print("you a idiot")

    else:
        print("You discard the new weapon")




#------------------------------Level-Up-System-----------------------------------------#

def level_up():
    global xp
    global xp_needed
    global player_level
    global player_health
    global player_vitality
    global player_energy

    xp -= xp_needed
    xp_needed = int(xp_needed ** 1.1)

    player_level += 1
    print(f"\n ⭐ You leveled up to level {player_level} ️⭐\n")

    player_health += min(randint(5+(player_vitality*2),10+(player_vitality*3)),player_max_health-player_health)

    level_up_options = ["Level up 💢Strength", "Level up 💚Vitality", "Level up ⚜️Dexterity","Level up 🧿Intelligence"]

    for i,option in enumerate(level_up_options):
        print(f"[{i + 1}]: {option}")
    choice = int(input("\nChoose a stat to increase\n"))
    match choice:
        case 1:
            increase_strength(1)
        case 2: #those who knQw
            increase_vitality(1)
        case 3:
            increase_dexterity(1)
        case 4:
            increase_intelligence(1)

    player_energy = player_max_energy

def test_for_level_up():
    global xp
    global xp_needed
    global player_level

    if xp >= xp_needed:
        level_up()
        test_for_level_up()

#------------------------------Stat-Increase-System-----------------------------------------#

def increase_strength(amount):
    global player_damage_multiplier
    global player_strength
    global player_max_weapons

    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    player_strength += amount
    dmg_increase = .10 * amount
    weapon_increase = .5 * amount

    player_damage_multiplier += dmg_increase
    player_max_weapons += weapon_increase
    if inspiration == 1:
        print(f"⏏️ Your Strength raised from 💢[{player_strength - amount}] to 💢[{player_strength}]")
    else:
        print(f"⏏️⏏️ Eureka! Your Strength raised from 💢[{(player_strength - amount)}] to 💢[{player_strength}]")
    if math.floor(player_max_weapons) != player_max_weapons:
        time.sleep(1)
        print("\nYou are now strong enough to carry more weapons!")
        time.sleep(1)

def increase_dexterity(amount):
    global player_dexterity
    global player_crit
    global player_dodge
    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    crit_increase = .1 * amount
    dodge_increase =(.05*amount)

    player_dexterity += amount
    player_crit += crit_increase
    player_dodge += dodge_increase
    if inspiration == 1:
        print(f"⏏️ Your Dexterity was increased from ⚜️{player_dexterity-amount} to ⚜️{player_dexterity}.")
    else:
        print(f"⏏️⏏️ Eureka! Your Dexterity raised from ⚜️{player_dexterity-amount} to ⚜️{player_dexterity}!")

def increase_vitality(amount):
    global player_vitality
    global player_max_health
    global player_max_energy

    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    energy_increase = 1 * amount
    health_increase = 15 * amount

    player_vitality += amount
    player_max_health  += health_increase
    player_max_energy += energy_increase
    if inspiration == 1:
        print(f"⏏️ Your Vitality was raised from 💚{player_vitality - amount} to 💚{player_vitality}.")
    else:
        print(f"⏏️⏏️ Eureka! Your Vitality raised from 💚{player_vitality - amount} to 💚{player_vitality}!")

def increase_intelligence(amount):
    global player_intelligence

    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    player_intelligence += amount

    if inspiration == 1:
        print(f"⏏️ Your Intelligence raised from 🧿[{player_intelligence - amount}] to 🧿[{player_intelligence}]")
    else:
        print(f"⏏️⏏️ Eureka! Your Intelligence raised from 🧿[{(player_intelligence - amount)}] to 🧿[{player_intelligence}]")


#-----------------------------------------------------------------------------------#

def see_stats():
    global xp
    global xp_needed
    divisor = xp_needed/10
    xp_progress = int(xp / divisor)
    print(f"---- STATS ----\n"
        f"\nCurrent Level: ⭐ {player_level} ⭐\n"
        f"Strength: 💢{player_strength}\n"
        f"Vitality: 💚{player_vitality}\n"
        f"Dexterity: ⚜️{player_dexterity}\n"
        f"Intelligence: 🧿{player_intelligence}\n"
        f"------------------------\n"
        f"Gold: 🪙{player_gold}\n"
        f"Health: ❤️{player_health}/{player_max_health}\n"
        f"Damage: ⚔️{player_damage_multiplier*100:.1f}%\n"
        f"Armor: 🛡️{player_armor}\n"
        f"Energy: ⚡️{player_energy}/{player_max_energy}\n"
        f"Dodge Chance: 💨{(player_dodge*100):.1f}%\n"
        f"Crit Chance: 🎯{(player_crit*100):.1f}%\n"
        f"XP: 💠{xp}/{xp_needed}\n")
    for gem in range(0,xp_progress):
        print("💠",end="")
    for bar in range(0,10-xp_progress):
        print("- ",end="")
    print("")

def examine_gear():
    for weapon in player_weapons:
        if weapon.damage > 0 and len(weapon.keywords) == 0:
            print(f"{weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier * player_effect_damage_multiplier)}]")
        elif len(weapon.keywords) > 0 and weapon.damage > 0:
            print(f"{weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier * player_effect_damage_multiplier)}] ", end= "")
        elif len(weapon.keywords) > 0:
            print(
                f"{weapon.name} [⚡️{weapon.energy}] ", end="")
    if len(weapon.keywords) > 0:
        for keyword in weapon.keywords:
            if weapon.keywords.index(keyword) < len(weapon.keywords) - 1:
                print(f"❇ {keyword}, ", end="")
            else:
                print(f"❇ {keyword}")

#-----------------------------------------------------------------------------------#

def game_over():
    global player_level
    global stat_gold_earned
    global stat_rooms_explored
    global stat_damage_dealt
    global stat_enemies_killed
    global stat_damage_taken
    global stat_damage_avoided
    global stat_energy_used
    global depth

    print(f"⚰️ YOU DIED. \n")
    wait(1.5,3)
    print(f"---- STATS ----\n"
          f"\nLevel {player_level}\n"
          f"Earned {stat_gold_earned} gold\n"
          f"Explored {stat_rooms_explored} rooms\n"
          f"Dealt {stat_damage_dealt} damage\n"
          f"Killed {stat_enemies_killed} enemies\n"
          f"Took {stat_damage_taken} damage\n"
          f"Avoided {stat_damage_avoided} damage\n"
          f"Spent {stat_energy_used} energy\n"
          f"Made it {depth} floors deep\n")
    exit()

#-----------------------------------------------------------------------------------#

game_init()