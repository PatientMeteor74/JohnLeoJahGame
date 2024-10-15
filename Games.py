import math
import time
import random
from ast import Index
from random import randint
from turtledemo.forest import randomize

#-----------------------------------------------------------------------------------#


player_health = 100
player_max_health = 100
player_armor = 0
player_dodge = 0.05
player_damage_multiplier = 1.0
player_crit = 0.01
player_crit_mult = 2.0

player_vitality = 0
player_strength = 0
player_dexterity = 0
player_intelligence = 0

player_level = 1
xp = 0
xp_needed = 20

delta = 0
player_turn = False

active_enemies = []
player_gold = 0

player_max_energy = 10
player_energy = player_max_energy
player_stunned = False
player_active_debuffs = []
enemy_active_debuffs = []


#-----------------------------------------------------------------------------------

stat_gold_earned = 0
stat_rooms_explored = 0
stat_damage_dealt = 0
stat_enemies_killed = 0
stat_damage_taken = 0
stat_damage_avoided = 0
stat_energy_used = 0

#-----------------------------------------------------------------------------------


class Enemy:
    def __init__(self, name, health, armor, dodge, attacks, average_gold, average_xp, keywords):
        self.name = name
        self.health = health
        self.attacks = attacks
        self.average_gold = average_gold
        self.average_xp = average_xp
        self.max_health = health
        self.armor = armor
        self.dodge = dodge
        self.keywords = keywords

    def attack(self):
        global player_stunned
        global player_gold
        hit = True
        time.sleep(0.5)
        attack_id = random.randint(0 , (len(self.attacks)-1))
        print(f"The {self.name} {self.attacks[attack_id].message}")

        result = damage_player(self.attacks[attack_id].damage)

        if result == "dodge" or result == "block":
            hit = False
        #Keywords
        if hit:
            if len(self.attacks[attack_id].keywords) > 0:
                for keyword in self.attacks[attack_id].keywords:
                    match keyword:
                        case "stun":
                            if random.random() < .4:
                                player_stunned = True
                        case "steal":
                                time.sleep(1)
                                if player_gold > 0:
                                    steal_amt = min(player_gold,random.randint(3, 5))
                                    player_gold -= steal_amt
                                    print(f"It grabbed {steal_amt}🪙!")
                                else:
                                    print("You felt some grubby fingers touch yo dingaling through yo pocket")

    def damage(self, amount):
        crit = False
        global stat_damage_dealt

        result = "hit"

        damage_taken = max(0, (amount - (random.randint(0, self.armor))))

        if random.random() <= player_crit:
            crit = True
            damage_taken = int((damage_taken * player_crit_mult) + self.armor)

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

    def die(self):
        time.sleep(0.5)
        global player_gold
        global xp
        global stat_enemies_killed

        stat_enemies_killed+=1

        reward_gold = self.average_gold * random.uniform(0.3, 1.7)
        reward_xp = self.average_xp * random.uniform(0.8, 1.2)

        print(f"☠️ It died, giving you {gain_gold(reward_gold)} and {gain_xp(reward_xp)}")

        active_enemies.remove(self)
        time.sleep(0.5)

#-----------------------------------------------------------------------------------#

class PlayerAttack:
    def __init__(self, name, message, damage, energy, keywords):
        self.name = name
        self.message = message
        self.damage = damage
        self.energy = energy
        self.keywords = keywords

#-----------------------------------------------------------------------------------#

class EnemyAttack:
    def __init__(self, name, message, damage, stun_chance, keywords):
        self.name = name
        self.message = message
        self.damage = damage
        self.stun_chance = stun_chance
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

        stat_rooms_explored += 1
        print(self.description)
        match self.name:
            case "combat":
                add_active_enemies(1, 2)
                player_turn = True
                print("You turn a corner and are faced with a small group of foes...")
                fight(active_enemies)
            case "shop":
                print("You enter a shop. The shopkeeper grumbles something about 'Those damned Goblins and their large noses stealing all my gold...'")
                open_shop()
                choose_path()
            case "elite_combat":
                add_active_enemies(3, 4)
                player_turn = True
                print("You open the door and what you see inside makes your pants a shade browner... ")
                fight(active_enemies)
            case "rest":
                print("You set up a small camp to recover health and energy")
                regain_energy()
                heal_player((player_max_health - player_health) * random.uniform(0.5,1.0))
                choose_path()
            case "loot":
                print("You drool a little at the sight: A pile of loot!")
                find_loot()
                choose_path()
            case "mystery":
                #chance = random.
                print("")
                choose_path()
#-----------------------------------------------------------------------------------#
class Debuff:
    def __init__(self, name, description, duration, effect_type, effect_value):
        self.name = name
        self.description = description
        self.duration = duration
        self.effect_type = effect_type
        self.effect_value = effect_value
    def apply(self, target):
        self.turns_left = self.duration
        if self.turns_left > 0:
            match self.effect_type:
                case "DOT":
                    self.damage_over_time(target, self.effect_value, self)
                case "Weakness":
                    self.apply_weakness(target, self.effect_value, self)
        return self.turns_left <= 0
    def damage_over_time(self,target, damage, debuff):
        global player_health
        global player_damage_multiplier
        if target == "player":
            player_health -= damage
            print(f"You take [{damage}] damage from {debuff.name}.")
        else:
            target.health -= damage
            print(f"The {target.name} takes [{damage}] damage from {debuff.name}.")
    def apply_weakness(self,target, reduction_percent, debuff):
        if debuff.turns_left == debuff.duration:
            if target == "player":
                player_damage_multiplier *= reduction_percent
                print(f"Your damage output is reduced by [{reduction_percent * 100}%] from {debuff.name}.")
            else:
                target.damage *= reduction_percent
                print(f"The {target.name}'s damage output is reduced by [{reduction_percent * 100}%] from {debuff.name}.")
    def process_debuffs(self, debuffs, target):
        expired_debuffs = []
        for debuff in debuffs:
            expired = debuff.apply(target)
            if expired:
                expired_debuffs.append(debuff)
        for debuff in expired_debuffs:
            debuffs.removed(debuff)
            target_name = "you" if target == "player" else target.name
            print(f"The {debuff.name} effect on {target_name} has expired.")
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
        match self.item_type:
            case "health":
                heal_player(self.effect_amount)
            case "energy":
                regain_energy(self.effect_amount)
        print(f"You used your {self.name}")
#-----------------------------------------------------------------------------------
health_potion = Item("Health Potion", "Restores a small amount of health.", "health", 20, 15)
large_health_potion = Item("Large Health Potion", "Heals a substantial amount of health", "health", 50, 35)
enormous_health_potion = Item("Enormous Health Potion", "Heals you to full health", "health", player_max_health, 80)
energy_potion = Item("Energy Potion", "Restores a small amount of energy.", "energy", player_max_energy, 30)

items = [health_potion, large_health_potion, enormous_health_potion, energy_potion]

#-----------------------------------------------------------------------------------
combat_room = Room("A room filled with the chatters and growls of enemies.", "combat", .5, "You stumble into another room full of enemies!")
shop_room = Room("A well-lit corridor with a sign hanging labelled 'The Shop (NO GOBLINS ALLOWED)'", "shop", .2, "You stumble into a shop!")
elite_room = Room("A door with ominous shadows visible through the light peeking below, labelled 'KEEP OUT!'", "elite_combat", .2, "You stumbled into a massively dangerous room!")
rest_room = Room("An unusually quiet pathway which appears safe for resting.", "rest", .05, "You stumble into a calm, peaceful room...")
loot_room = Room("A dark room with a promising glimmer in the center.", "loot", .1, "You stumble into a room with loot!")

rooms = [combat_room, shop_room, elite_room, rest_room, loot_room]

#-----------------------------------------------------------------------------------

def spawn_rooms():
    possible_rooms = []
    while not (1 <= len(possible_rooms) <= 4):
        possible_rooms = [room for room in rooms if random.random() <= room.spawn_chance]
    return possible_rooms

def choose_path():
    spawned_rooms = spawn_rooms()
    #*********HAS CHANCE TO NOT PROVIDE ANY ROOMS************pls fix
    chosen = False
    time.sleep(1)
    while not chosen:
        print("\nYou are presented with a number of branching doorways...\n")

        for i,room in enumerate(spawned_rooms):
            print(f"[{i + 1}]: {room.description}")

        print(f"[{len(spawned_rooms) + 1}]: Pause for introspection and deep thought.")
        choice = int(input("\nInput your choice:\n"))

        global player_turn

        if 1 <=choice <= len(spawned_rooms):
            selected_room = spawned_rooms[choice - 1]
            selected_room.enter()
            chosen = True

        elif choice == len(spawned_rooms) + 1:
            print(f"[1]:🔎 See Stats\n"
                  f"[2]:⬅️ Back")
            c_choice = int(input("Input your choice:\n"))
            match c_choice:
                case 1:
                    see_stats()
                case 2:
                    choose_path()
                case _:
                    print("youre foolish!")
    else:
        print("you a idot!")
        choose_path()

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
        print(f"\nYou have {player_gold} gold left...\n")
        for i,item in enumerate(shop_items):
            print(f"[{i + 1}]: {item.name} (Cost:[{item.value}]")
        for j,weapon in enumerate(shop_weapons):
            print(f"[{len(shop_items) + j + 1}]: {weapon.name}(Cost: [{int(random.uniform(1,1) * ((weapon.damage - 1 / (weapon.energy + 1)) * 20))}])")
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
                weapon_price = int(random.uniform(1,1) * (selected_weapon.damage - 1 / (selected_weapon.energy + 1)) * 20)
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

def find_loot():
    global player_gold

    found_gold = random.randint(5, 45)
    found_gold += player_level

    print(f"you rummage through the pile and find {gain_gold(found_gold)}")

    add_weapon(loot_weapons[random.randint(0,len(loot_weapons) - 1)])

def display_map():
    '''
        ``````````````
        ``````````[👿]``````
        `````[👹][📍]==[]````
        `````````[💰]``````
        ``````````````
    '''
    print("There aint no maps for where we're going")

#-----------------------------------------------------------------------------------

def add_active_enemies(minenemies,maxenemies):
    for i in range(0, random.randint(minenemies, maxenemies)):
        base_enemy = enemies[random.randint(0, len(enemies) - 1)]

        new_enemy = Enemy(
            base_enemy.name,
            base_enemy.health,
            base_enemy.armor,
            base_enemy.dodge,
            base_enemy.attacks,
            base_enemy.average_gold,
            base_enemy.average_xp,
            base_enemy.keywords
        )

        active_enemies.append(new_enemy)

#-----------------------------------------------------------------------------------
def game_init():
    print("Welcome to freaky text dungeon, mmm..........")
    print("[1]: 👺 Enter the Dungeon 👺\n"
          "[2]: ✖️ Turn back ✖️")
    choice = int(input("Input your choice: \n"))
    if choice == 1:
        print("You enter the dungeon, your heart filled with dread...")
        choose_path()
    elif choice == 2:
        return
    else:
        print("Please pick 1 or 2")
        game_init()

#-----------------------------------------------------------------------------------
#=====================================ENEMY ATTACKS=======================================#
slomp = EnemyAttack("Slomp Attack", "attempts to smash you with its gludge...",5, .1, [])
stab = EnemyAttack("Stab"," lunges forward to stab you...",3, 0, [])
d_slash = EnemyAttack("Dagger Slash","quickly slashes towards your chest with a dagger...",2, 0, [])
body_slam = EnemyAttack("Body Slam","throws itself toward you with great force...", 3, .3, ["stun"])
d_rage = EnemyAttack("Drunken Rage", "attacks you in a drunken rage...",4, .15, [])
expl_cask = EnemyAttack("Explosive Cask", "throws an explosive cask at you...", 5, .2, [])
b_roll = EnemyAttack("Barrel Roll", "whirls a cask your feet...", 2, 0, [])
scream = EnemyAttack("Scream", "screams AAAAAAAAAAA...", 1, 0, ["stun"])
bite = EnemyAttack("Bite", "attempts to bite you...", 4, 0, [])
s_slam = EnemyAttack("Shovel Slam","tries to smash your head with a shovel...",4,.1,["stun"])
poo_throw = EnemyAttack("Poo Throw","throws some poo at you...",0,0,[])
pick_pock = EnemyAttack("Pick Pocket","lunges for your pockets...",0,0,["steal"])

enemy_attacks = [slomp, stab, d_slash, body_slam, d_rage, expl_cask, b_roll, scream, bite,s_slam,poo_throw,pick_pock]
#=========================================================================================#

#=====================================ENEMIES=======================================#
goblin = Enemy("🔸Grouchy Goblin", 5, 1, 0.1,[stab,d_slash, bite], 2,5,[])
skele = Enemy("🔸Scary Skeleton",7,2, 0.05,[stab,d_rage],1,10,[])
slomp_monster = Enemy("🔸Slompster", 15, 0, 0,[slomp, bite],5,15,[])
grogus = Enemy("♦️Grogus", 35, 0, 0.05, [body_slam,expl_cask,body_slam,d_rage],15,25,[])
living_ore = Enemy("🔸Living Ore", 10, 5,0, [body_slam, scream],20,5,[])
clkwrk_gremlin = Enemy("🔸Clockwork Gremlin", 1, 5, 0.1, [bite],2,8,[])
wailing_wisp = Enemy("🔸Wailing Wisp", 1, 0, 0.33, [scream],0,15,[])
lost_serf = Enemy("🔸Lost Serf",8,0,.05,[d_rage,s_slam,poo_throw],8,3,[])
rob_goblin = Enemy("🔸Goblin Robber",5,1,.2,[stab,pick_pock],15,4,[])

enemies = [goblin, skele, slomp_monster, grogus, living_ore, clkwrk_gremlin, wailing_wisp,lost_serf,rob_goblin]
#===================================================================================#

#=====================================PLAYER ATTACKS======================================#
shortsword = PlayerAttack("Simple Shortsword", "You swing your sword...", 4, 2, [])
iron_battleaxe = PlayerAttack("Battleaxe", "You forcefully swing your battleaxe...", 7, 5, [])
dagger = PlayerAttack("Goblin Dagger", "You slash twice with your dagger...", 2, 2, ["double_strike"])
stick = PlayerAttack("Whacking Stick", "You whack that fella head smoove off...", 1, 0, [])
anvil_staff = PlayerAttack("Anvil Staff", "You conjure an anvil high in the air...", 6, 4, ["stun"])
gun = PlayerAttack("Gun", "You unload your clip...", 2, 8, ["7x_strike"])
boomerang = PlayerAttack("Boomerang", "You chuck your boomerang at they noggin, HARD...", 3, 1, [])
spiky_stick = PlayerAttack("Spiky Stick", "You smach that fella head smoove off spikily...", 2, 0, [])
f_bucket = PlayerAttack("Fire Bucket", "You dump a torrent of fire towards the enemies...", 0, 9, ["burn","splash","aimless"])
torch = PlayerAttack("Old Torch", "You somehow relight the torch and swing...",1,3,["burn"])
weapons = [shortsword,iron_battleaxe,dagger,stick,anvil_staff,gun,boomerang,spiky_stick,f_bucket,torch]

#=========================================================================================#

loot_weapons = [dagger,anvil_staff,gun,boomerang,spiky_stick,f_bucket,torch]

#=========================================================================================#

#========================================DEBUFFS==========================================#
fire = Debuff("Fire", "Set alight", 4, "DOT", 1)
fentanyl = Debuff("Fentanyl", "1kg Fent", 10, "Weakness", .5)
    #FOOLS TUTORIAL: aPPLYTING EFFECTS
        # effect.apply(target or "player")     -player must be a string because there is no player class
        #fire.apply("player")
        #fire.apply(Enemy)
#=========================================================================================#
#Player Inventory

player_weapons = [shortsword,iron_battleaxe,stick,f_bucket]
player_max_weapons = 5
player_accessories = []
item_inventory = []
#-----------------------------------------------------------------------------------#

def damage_player(amount):
    global player_health
    global player_armor
    global stat_damage_avoided

    result = "hit"

    damage_taken = max(0, (amount - (random.randint(0,player_armor))))


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
    player_health += healing_taken

    if inspiration == 1:
        print(f"💞 You restore {healing_taken} health [❤️{player_health}/{player_max_health}]")
    else:
        print(f"💞💞 Eureka! You restore {healing_taken} health [❤️{player_health}/{player_max_health}]")

def regain_energy():
    global player_energy
    global player_max_energy
    global player_intelligence

    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * 0.05):
        inspiration = 2

    if player_max_energy - player_energy > 1:
        gain = random.randint(1,(player_max_energy - player_energy)) * inspiration
    else:
        gain = 1
    player_energy += gain
    if inspiration == 1:
        return f"You restore⚡️{gain} energy."
    else:
        return f"In a flash of inspiration, restore⚡️{gain}, energy!"

def gain_gold(amount):
    global player_gold
    global stat_gold_earned

    stat_gold_earned += int(amount)

    gained_amount = int(amount)
    player_gold += gained_amount
    return f"🪙{gained_amount}"

def gain_xp(amount):
    global xp
    gained_amount = int(amount)
    xp += gained_amount
    return f"💠{gained_amount}"

#-----------------------------------------------------------------------------------#
attack_actions = ["Run Away", "Attack", "Rest", "Use Item"]
def fight(enemies: list[Enemy]):
    global player_turn
    global attack_actions
    global player_attacks
    global enemy_attacks
    global active_enemies
    global player_stunned
    global player_max_energy
    global player_energy
    global rooms
    global item_inventory
    print("It's time to fight\n"
          "You're facing...")
    for i in range(0,len(enemies)):
        print(f"[ A {enemies[i].name} with ❤️{enemies[i].health} ]")
    while len(enemies) > 0 and player_health > 0:
        if player_turn:
            if player_stunned:
                print("You are stunned and cannot act this turn!")
                time.sleep(4)
                player_stunned = False  # Reset stun status
                player_turn = False  # End player's turn
                continue

            for i in range(len(attack_actions)):
                print(f"[{i + 1}]: {attack_actions[i]}")
            try:
                print(f"Current Energy:⚡️{player_energy}")
                chosen_action = int(input("Choose an action:"))
            except ValueError:
                print("blud, you gotta enter an int")
                continue
            if chosen_action == 1:
                if player_energy >= math.floor(player_max_energy/10):
                    print("You pee your pants a little and sprint towards the first escape you see")
                    if random.random() <.65:
                        print("escape") #placeholder
                        active_enemies = []
                        escape_room = rooms[random.randint(0, len(rooms)) - 1]
                        print(escape_room.stumble_message)
                        escape_room.enter()
                    else:
                        print("The opps block yo path, you cooked, blud")

            elif chosen_action == 2:
                for i in range(len(player_weapons)):
                    weapon = player_weapons[i]

                    print(f"[{i + 1}]: {weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier)}]")
                chosen_attack = int(input("\n Choose an attack:"))
                if player_energy-player_weapons[chosen_attack-1].energy < 0:
                    print("You don't have enough energy for that attack :(")
                    continue
                else:
                    if len(enemies) > 1 and "aimless" not in player_weapons[(chosen_attack-1)].keywords:
                        for i in range(len(enemies)):
                            print(f"[{i + 1}]: attack {enemies[i].name}")
                        try:
                            chosen_enemy = int(input("Choose an enemy to attack:"))
                            player_attack(player_weapons[(chosen_attack-1)], enemies[(chosen_enemy-1)])
                        except IndexError:
                            continue
                    else:
                        player_attack(player_weapons[(chosen_attack-1)], enemies[0])
            elif chosen_action == 3:
                if player_max_energy != player_energy:
                    print(f"{regain_energy()}")
                else:
                    print("You're already at max energy")
                    time.sleep(1.5)
                    continue
            elif chosen_action == 4 and len(item_inventory) > 0:
                for i,item in enumerate(item_inventory):
                    print(f"[{i+1}]: Use {item}")
                item_choice = int(input("Choose an item to use:"))
                item_inventory[item_choice - 1].use()
            else:
                print("That's not an available action, try again.")
                continue
            player_turn = False

            if len(active_enemies) > 0:
                print("\n------------------- Enemy Turn -------------------\n")
        else: #Enemy Turn
            for enemy in enemies:
                if enemy.health > 0:
                    enemy.attack()
                else:
                    enemies.remove(enemy)
            player_turn = True

            time.sleep(1)
            print("\n------------------- Your Turn -------------------\n")

    else:
        end_fight(player_health)

def end_fight(health):
    global player_max_health

    test_for_level_up()
    choose_path()
    if health == player_max_health:
        print("\nYou made it out unscathed!\n")
    elif health >= player_max_health / 2:
        print("\nYou made it out with a couple scratches...\n")
    elif health >= player_max_health / 4:
        print("\nYou barely made it out...\n")
    else:
        print("\nYou barely made it to the exit, let alone lived...\n")

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

    targets = []

    # Keywords
    for keyword in PlayerAttack.keywords:
        match keyword:
            case "double_strike":
                hits *= 2
            case "triple_strike":
                hits *= 3
            case "7x_strike":
                hits *= 7
            case "splash":
                targets = []
                for enemy in active_enemies:
                    targets.append(enemy)
            case "aimless":
                    if targets == []:
                        if len(active_enemies) > 1:
                            targets.append(active_enemies[random.randint(1,len(active_enemies) - 1)])
                        else:
                            targets.append(active_enemies[0])

    if targets == []:
        targets = [Enemy]

    for target in targets:
        for i in range(0,hits):
            if target.health > 0:
                for keyword in PlayerAttack.keywords:
                    match keyword:
                        case "burn":
                            fire.apply(target)
                #Damage Target
                target.damage(int(PlayerAttack.damage * player_damage_multiplier))
            else:
                targets.remove(target)
    time.sleep(1.5)

#-----------------------------------------------------------------------------------#

def add_weapon(weapon_to_add):
    global player_weapons
    print(f"\nYou got a new weapon: '{weapon_to_add.name}'")
    choice = input(f"[1]: Take the weapon\n"
                   f"[2]: Leave the weapon\n")
    if choice == "1":
        if len(player_weapons) < player_max_weapons:
            player_weapons.append(weapon_to_add)
            print(f"You gain a weapon: '{weapon_to_add.name}'")
        else:
            print((f"Your weapon bag is already full, choose a weapon to replace:"))

            for i in range(len(player_weapons)):
                weapon = player_weapons[i]
                print(f"[{i + 1}]: replace {weapon.name}\n")

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




#-----------------------------------------------------------------------------------#

def test_for_level_up():
    global xp
    global xp_needed
    global player_level

    while xp >= xp_needed:
        xp -= xp_needed
        level_up()

def level_up():
    global xp
    global xp_needed
    global player_level
    global player_health
    global player_vitality

    player_level += 1
    print(f"\n ⭐ You leveled up to level {player_level} ️⭐\n")

    player_health += randint(10+(player_vitality*2),16+(player_vitality*3))

    level_up_options = ["Level up 💢Strength", "Level up 💚Vitality", "Level up ⚜️Dexterity","Level up 🧿Intelligence"]

    for i,option in enumerate(level_up_options):
        print(f"[{i + 1}]: {option}")
    choice = int(input("\nChoose a stat to increase\n"))
    match choice:
        case 1:
            increase_strength(1)
        case 2:
            increase_vitality(1)
        case 3:
            increase_dexterity(1)
        case 4:
            increase_intelligence(1)

    xp_needed += (player_level ** 2 * 5)
    player_energy = player_max_energy

def increase_strength(amount):
    global player_damage_multiplier
    global player_strength
    global player_max_weapons

    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    player_strength += amount
    dmg_increase = .15 * amount
    weapon_increase = .5 * amount

    player_damage_multiplier += dmg_increase
    player_max_weapons += weapon_increase
    if inspiration == 1:
        print(f"⏏️ Your Strength raised from 💢[{player_strength - amount}] to 💢[{player_strength}]")
    else:
        print(f"⏏️⏏️ Eureka! Your Strength raised from 💢[{(player_strength - amount)}] to 💢[{player_strength}]")


def increase_dexterity(amount):
    global player_dexterity
    global player_crit
    global player_dodge
    inspiration = 1
    if random.random() < 0.05 + (player_intelligence * .05):
        inspiration = 2

    amount *= inspiration

    crit_increase = .1 * amount
    dodge_increase =.025*amount

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

    energy_increase = 2 * amount
    health_increase = 10 * amount

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
        print(f"⏏️ Your Intelligence raised from 🧿[{player_intelligence - amount}%] to 🧿[{player_intelligence}%]")
    else:
        print(f"⏏️⏏️ Eureka! Your Intelligence raised from 🧿[{(player_intelligence - amount)}%] to 🧿[{player_intelligence}%]")


#-----------------------------------------------------------------------------------#

def see_stats():
    global xp
    global xp_needed
    divisor = xp_needed/10
    xp_progress = int(xp // divisor)
    print(f"---- STATS ----\n"
        f"\nCurrent Level: ⭐ {player_level} ⭐\n"
        f"Gold: 🪙{player_gold}\n"
        f"Health: ❤️{player_health}/{player_max_health}\n"
        f"Damage: ⚔️{player_damage_multiplier*100}%\n"
        f"Armor: 🛡️{player_armor}\n"
        f"Energy: ⚡️{player_energy}/{player_max_energy}\n"
        f"Dodge Chance: 💨{(player_dodge*100)}%\n"
        f"Crit Chance: 🎯{int(player_crit*100)}%\n"
        f"XP: 💠{xp}/{xp_needed}\n")
    for xp in range(0,xp_progress-1):
        print("💠",end="")
    for bar in range(0,10-xp_progress):
        print("- ",end="")
    print("")

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

    print(f"⚰️ YOU DIED. \n"
          f"---- STATS ----\n"
          f"\nLevel {player_level})\n"
          f"Earned {stat_gold_earned} gold\n"
          f"Explored {stat_rooms_explored} rooms\n"
          f"Dealt {stat_damage_dealt} damage\n"
          f"Killed {stat_enemies_killed} enemies\n"
          f"Took {stat_damage_taken} damage\n"
          f"Avoided {stat_damage_avoided} damage\n"
          f"Spent {stat_energy_used} energy\n")
    exit()

#-----------------------------------------------------------------------------------#

game_init()