import math
import time
import random
from ast import Index
from random import randint

#-----------------------------------------------------------------------------------#

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

        time.sleep(0.5)
        attack_id = random.randint(0 , (len(self.attacks)-1))
        print(f"The {self.name} {self.attacks[attack_id].message}")
        damage_player(self.attacks[attack_id].damage)
        if len(self.keywords) > 0:
            for keyword in self.keywords:
                match keyword:
                    case "stun":
                        player_stunned = True

    def damage(self, amount):
        time.sleep(0.2)
        crit = False

        damage_taken = max(0, (amount - (random.randint(0, self.armor))))

        if random.random() <= player_crit:
            crit = True

        damage_taken = int(damage_taken)

        if self.health<0:
            self.health = 0

        if self.dodge > random.random():
            print(f"💨 Your attack misses the {self.name}, dealing no damage.")
        elif damage_taken <= 0:
            print(f"🛡️ Your attack bounces off the {self.name}, dealing no damage.")
        elif crit == False:
            self.health -= damage_taken
            print(f"💥 You strike the {self.name} dealing {damage_taken} damage! [❤️{self.health}/{self.max_health}]")
        else:
            damage_taken = int(damage_taken * player_crit_mult)
            self.health -= damage_taken
            print(f"🎯💥 You critically strike the {self.name} dealing {damage_taken} damage! [❤️{self.health}/{self.max_health}]")
        if self.health <= 0:
            self.die()

    def die(self):
        global player_gold
        global xp

        reward_gold = self.average_gold * random.uniform(0.0, 2.0)
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

player_health = 100
player_max_health = 100
player_armor = 0
player_dodge = 0.05
player_damage_multiplier = 1.0
player_crit = 0.01
player_crit_mult = 2.0

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

#-----------------------------------------------------------------------------------

class Room:
    def __init__(self, description, name, spawn_chance):
        self.description = description
        self.name = name
        self.spawn_chance = spawn_chance
    def enter(self):
        global player_turn
        global active_enemies
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
                
#-----------------------------------------------------------------------------------
combat_room = Room("A room filled with the chatters and growls of enemies.", "combat", .5)
shop_room = Room("A well-lit corridor with a sign hanging labelled 'The Shop (NO GOBLINS ALLOWED)'", "shop", .1)
elite_room = Room("A door with ominous shadows visible through the light peeking below, labelled 'KEEP OUT!'", "elite_combat", .2)
rest_room = Room("An unusually quiet pathway which appears safe for resting.", "rest", .05)
loot_room = Room("A dark room with a promising glimmer in the center.", "loot", .1)

rooms = [combat_room, shop_room, elite_room, rest_room, loot_room]

#-----------------------------------------------------------------------------------

def spawn_rooms():
    possible_rooms = []
    while not (1 <= len(possible_rooms) <= 4):
        possible_rooms = [room for room in rooms if random.random() <= room.spawn_chance]
    return possible_rooms

def choose_path():
    #*********HAS CHANCE TO NOT PROVIDE ANY ROOMS************pls fix
    print("\n You are presented with a number of branching doorways...\n")
    spawned_rooms = spawn_rooms()
    for i,room in enumerate(spawned_rooms):
        print(f"[{i + 1}]: {room.description}")
    choice = int(input("\nChoose a room:\n"))
    global player_turn
    if 1 <=choice <= len(spawned_rooms):
        selected_room = spawned_rooms[choice - 1]
        selected_room.enter()
    else:
        print("you a retard")
        choose_path()

def open_shop():
    print("You see a pile of rubble and a sign that says: 'End yo life boy.'")

def find_loot():
    global player_gold

    found_gold = random.randint(5, 45)
    found_gold += player_level

    print(f"you rummage through the pile and find {gain_gold(found_gold)}")

    add_weapon(loot_weapons[random.randint(0,len(loot_weapons) - 1)])

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
    print("[1]: ENTER THE DUNGEON...\n"
          "[2]: Turn back...")
    choice = int(input("Input your choice: \n"))
    if choice == 1:
        print("enter dungeon success")
        choose_path()
    elif choice == 2:
        return
    else:
        print("Please pick 1 or 2")
        game_init()
#-----------------------------------------------------------------------------------

#=====================================ENEMY ATTACKS=======================================#
slomp = EnemyAttack("Slomp Attack", "attempts to smash you with its gludge...",5, .1, [])
stab = EnemyAttack("Stab"," lunges forward to stab you",3, 0, [])
d_slash = EnemyAttack("Dagger Slash","quickly slashes towards your chest with a dagger...",2, 0, [])
body_slam = EnemyAttack("Body Slam","throws itself toward you with great force...", 3, .3, ["stun"])
d_rage = EnemyAttack("Drunken Rage", "attacks you in a drunken rage...",4, .15, [])
expl_cask = EnemyAttack("Explosive Cask", "throws an explosive cask at you...", 5, .2, [])
b_roll = EnemyAttack("Barrel Roll", "whirls a cask your feet...", 2, 0, [])
scream = EnemyAttack("Scream", "screams AAAAAAAAAAA...", 1, 0, ["stun"])
bite = EnemyAttack("Bite", "attempts to bite you...", 4, 0, [])

enemy_attacks = [slomp, stab, d_slash, body_slam, d_rage, expl_cask, b_roll, scream, bite]
#=========================================================================================#

#=====================================ENEMIES=======================================#
goblin = Enemy("Grouchy Goblin", 5, 1, 0.1,[stab,d_slash, bite], 2,5,[])
skele = Enemy("Scary Skeleton",7,2, 0.05,[stab,d_rage],1,10,[])
slomp_monster = Enemy("Slompster", 15, 0, 0,[slomp, bite],5,15,[])
grogus = Enemy("Grogus", 35, 0, 0.05, [body_slam,expl_cask,body_slam,d_rage],15,25,[])
living_ore = Enemy("Living Ore", 10, 5,0, [body_slam, scream],20,5,[])
clkwrk_gremlin = Enemy("Clockwork Gremlin", 1, 5, 0.1, [bite],2,8,[])
wailing_wisp = Enemy("Wailing Wisp", 1, 0, 0.66, [scream],0,15,[])

enemies = [goblin, skele, slomp_monster, grogus, living_ore, clkwrk_gremlin, wailing_wisp]
#===================================================================================#

#=====================================PLAYER ATTACKS======================================#
shortsword = PlayerAttack("Simple Shortsword", "You swing your sword...", 4, 2, [])
iron_battleaxe = PlayerAttack("Battleaxe", "You forcefully swing your battleaxe...", 7, 5, [])
dagger = PlayerAttack("Goblin Dagger", "You slash twice with your dagger...", 2, 2, ["double_strike"])
stick = PlayerAttack("Whacking Stick", "You whack that fella head smoove off...", 1, 0, [])
anvil_staff = PlayerAttack("Anvil Staff", "You conjure an anvil high in the air...", 6, 4, ["stun"])
gun = PlayerAttack("Gun", "You unload your clip...", 18, 10, [])
boomerang = PlayerAttack("Boomerang", "You chuck your boomerang at they noggin, HARD...", 3, 1, [])
spiky_stick = PlayerAttack("Spiky Stick", "You smach that fella head smoove off spikily...", 2, 0, [])
weapons = [shortsword,iron_battleaxe,dagger,stick,anvil_staff,gun,boomerang,spiky_stick]

#=========================================================================================#

loot_weapons = [dagger,anvil_staff,gun,boomerang,spiky_stick]

#=========================================================================================#

#Player Inventory

player_weapons = [shortsword,iron_battleaxe,stick]
player_max_weapons = 5
player_accessories = []

#-----------------------------------------------------------------------------------#

def damage_player(amount):
    global player_health
    global player_armor
    damage_taken = max(0, (amount - (random.randint(0,player_armor))))

    if random.uniform(0.0,1.0) <= player_dodge:
        print(f"💨 You dodge out of the way, taking no damage!")
    elif damage_taken <= 0:
        print(f"🛡️ The attack is deflected by your armor, dealing no damage!")
    else:
        player_health -= damage_taken
        print(f"💔 You take {damage_taken} damage. [❤️{player_health}/{player_max_health}]")

    if player_health <= 0:
        game_over()

    return(f"{damage_taken}")
        
def heal_player(amount):
    global player_health
    healing_taken = int(amount)

    player_health += healing_taken
    print(f"❤️‍🩹 You restore {healing_taken} health [❤️{player_health}/{player_max_health}]")

def regain_energy():
    global player_energy
    global player_max_energy
    if player_max_energy - player_energy > 1:
        gain = random.randint(1,(player_max_energy - player_energy))
    else:
        gain = 1
    player_energy += gain
    return f"⚡️{gain}"

def gain_gold(amount):
    global player_gold
    gained_amount = int(amount)
    player_gold += gained_amount
    return f"🪙{gained_amount}"

def gain_xp(amount):
    global xp
    gained_amount = int(amount)
    xp += gained_amount
    return f"💠{gained_amount}"

#-----------------------------------------------------------------------------------#
attack_actions = ["Run Away", "Attack", "Rest"]
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
                        rooms[random.randint(0, len(rooms)) - 1].enter()
                    else:
                        print("The opps block yo path, you cooked, blud")

            elif chosen_action == 2:
                for i in range(len(player_weapons)):
                    weapon = player_weapons[i]

                    print(f"[{i + 1}]: {weapon.name} [⚡️{weapon.energy}] [💥{int(weapon.damage * player_damage_multiplier)}]")
                chosen_attack = int(input("\n Choose an attack:"))
                if player_energy-player_weapons[chosen_attack-1].energy < 0:
                    print("You don't hav enough energy for that attack!")
                    continue
                else:
                    if len(enemies) > 1:
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
                    print(f"You rest, regaining {regain_energy()} energy")
                else:
                    print("You're already at max energy")
                    time.sleep(1.5)
                    continue
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
    player_energy -= PlayerAttack.energy
    print(PlayerAttack.message)
    targets = [Enemy]

    for keyword in PlayerAttack.keywords:
        match keyword:
            case "double_strike":
                targets.append(Enemy)

    for target in targets:
        if target.health != 0:
            target.damage(int(PlayerAttack.damage * player_damage_multiplier))
        else:
            targets.remove(target)
    time.sleep(1.5)

#-----------------------------------------------------------------------------------#

def add_weapon(weapon_to_add):
    global player_weapons
    print(f"\nYou found a weapon: '{weapon_to_add.name}'")
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
            replace_choice = int(replace_choice - 1)

            if replace_choice >= 1 & replace_choice <= player_max_weapons:
                print(f"You replaced your '{player_weapons[replace_choice].name}' with '{weapon_to_add.name}'")
                player_weapons[replace_choice] = weapon_to_add

            elif choice == 0:
                print("You discard the new weapon")

            else:
                print("you a retard")

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

    player_level += 1
    print(f"\n ⭐ You leveled up to level {player_level} ️⭐\n")

    increase_health(randint(8,12+player_level))

    level_up_options = ["Level up Damage", "Level up Energy", "Level up Crit"]

    for i,option in enumerate(level_up_options):
        print(f"[{i + 1}]: {option}")
    choice = int(input("\nChoose a stat to increase\n"))
    match choice:
        case 1:
            increase_damage(random.uniform(.05,.15))
        case 2:
            increase_energy(random.randint(1,.3))
        case 3:
            increase_crit(random.uniform(.05,.17))

    xp_needed += (player_level ** 2 * 5)


def increase_damage(amount):
    global player_damage_multiplier
    player_damage_multiplier += amount
    print(f"⏏️ Your damage raised from ⚔️[{(int(player_damage_multiplier - amount)) * 100}%] to ⚔️[{int(player_damage_multiplier * 100)}%]")

def increase_crit(amount):
    global player_crit

    player_crit += amount
    print(f"⏏️ Your crit chance raised from 🎯[{int(((player_crit - amount)*100))}%] to 🎯[{int(((player_crit)*100))}%]")

def increase_energy(amount):
    global player_energy
    global player_max_energy

    player_energy += amount
    player_max_energy += amount

    print(f"⏏️ Your max energy raised from ⚡️{player_max_energy - amount} to ⚡️{player_max_energy}")

def increase_health(amount):
    global player_max_health
    global player_health

    player_max_health += amount
    player_health += amount

    print(f"⏏️ Your maximum health raised from ❤️{player_max_health - amount} to ❤️{player_max_health}")

#-----------------------------------------------------------------------------------#

def game_over():
    print(f"⚰️ You died at level {player_level}")
    exit()

#-----------------------------------------------------------------------------------#

game_init()