import math
import time
import random
from ast import Index
from random import randint


#-----------------------------------------------------------------------------------#

class Enemy:
    def __init__(self, name, health, armor, attacks, average_gold, average_xp, keywords):
        self.name = name
        self.health = health
        self.attacks = attacks
        self.average_gold = average_gold
        self.average_xp = average_xp
        self.max_health = health
        self.armor = armor
        self.keywords = keywords

    def attack(self):
        global player_stunned
        attack_id = random.randint(0 , (len(self.attacks)-1))
        print(f"The {self.name} {self.attacks[attack_id].message}")
        damage_player(self.attacks[attack_id].damage)
        if len(self.keywords) > 0:
            for keyword in self.keywords:
                match keyword:
                    case "stun":
                        player_stunned = True

    def damage(self, amount):
        crit = 1
        if random.randint(1,20) == 20:
            crit = 2
        damage_taken = max(0, (amount * crit - (random.randint(0,self.armor))))

        self.health -= damage_taken

        if self.health<0:
            self.health = 0
        if crit == 2:
            print(f"💥 You strike the {self.name} dealing {damage_taken} damage. [❤️{self.health}/{self.max_health}]")
        else:
            print(f"💥 You brutally strike the vitals of the {self.name} dealing {damage_taken} damage. [❤️{self.health}/{self.max_health}]")
        if self.health <= 0:
            self.die()

    def die(self):
        global player_gold
        global xp

        reward_gold = self.average_gold * random.uniform(0.0, 2.0)
        reward_xp = self.average_xp * random.uniform(0.0, 2.0)

        player_gold += int(reward_gold)
        xp += int(reward_xp)

        print(f"☠️ It died, you gain: 🪙{int(reward_gold)} gold,💠{int(reward_xp)} XP")

        active_enemies.remove(self)
        time.sleep(1)

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
player_damage_multiplier = 1.0

player_level = 1
xp = 0
xp_needed = 100

delta = 0
player_turn = False

active_enemies = []
player_gold = 0
player_max_energy = 10
player_energy = player_max_energy
player_stunned = False
#-----------------------------------------------------------------------------------

class Room:
    def __init__(self, description, name):
        self.description = description
        self.name = name
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
            case "elite_combat":
                add_active_enemies(3, 4)
                player_turn = True
                print("You open the door and what you see inside makes your pants a shade browner... ")
                fight(active_enemies)
            case "rest":
                print("You find a quiet place to rest and recover")
                regain_energy()
            case "loot":
                print("You drool a little at the sight: A pile of loot!")
                find_loot()
            case "mystery":
                #chance = random.
                print("")
                
#-----------------------------------------------------------------------------------
combat_room = Room("A room filled with the chatters and growls of enemies.", "combat")
shop_room = Room("A well-lit corridor with a sign hanging labelled 'The Shop (NO GOBLINS ALLOWED)'", "shop")
elite_room = Room("A door with ominous shadows visible through the light peeking below, labelled 'KEEP OUT!'", "elite_combat")
rest_room = Room("A quiet pathway which appears perfect for resting.", "rest")
loot_room = Room("A dark room with a promising glimmer in the center.", "loot")

rooms = [combat_room, shop_room, elite_room, rest_room, loot_room]

#-----------------------------------------------------------------------------------
# def update():
#   global delta
#   delta += 1


'''while delta >= 0:
    update()'''

#-----------------------------------------------------------------------------------
def choose_path():
    print("You are presented with a number of branching doorways...\n")
    for i,room in enumerate(rooms):
        print(f"[{i + 1}]: {room.description}")
    choice = int(input("\nChoose a room:\n"))
    global player_turn
    if 1 <=choice <= len(rooms):
        selected_room = rooms[choice - 1]
        selected_room.enter()
    else:
        print("you a retard")
        choose_path()

def open_shop():
    print("You see a pile of rubble and a sign that says: 'End yo life boy.'")

def find_loot():
    global player_gold
    found_gold = random.randint(5, 20)
    player_gold += found_gold
    print(f"You found a pile of {found_gold} gold!")
#-----------------------------------------------------------------------------------

def add_active_enemies(minenemies,maxenemies):
    for i in range(0, random.randint(minenemies, maxenemies)):
        base_enemy = enemies[random.randint(0, len(enemies) - 1)]

        new_enemy = Enemy(
            base_enemy.name,
            base_enemy.health,
            base_enemy.armor,
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
slomp = EnemyAttack("Slomp Attack", "basically slomps teh frick out of you lil bro",2, .1, [])
stab = EnemyAttack("Stab"," lunges forward and stabs you ",3, 0, [])
d_slash = EnemyAttack("Dagger Slash","quickly slashes you across the chest with a dagger",2, 0, [])
body_slam = EnemyAttack("Body Slam","slams itself into you with great force", 3, .3, ["stun "])
d_rage = EnemyAttack("Drunken Rage", "attacks you in a drunken rage",4, .15, [])
expl_cask = EnemyAttack("Explosive Cask", "It throws an explosive cask at you", 5, .2, [])
b_roll = EnemyAttack("Barrel Roll", "whirls a cask your feet", 2, 0, [])
jumpscare = EnemyAttack("Jumpscare", "screams AAAAAAAAAAA", 1, 0, ["stun"])

enemy_attacks = [slomp, stab, d_slash, body_slam, d_rage, expl_cask, b_roll, jumpscare]
#=========================================================================================#

#=====================================ENEMIES=======================================#
goblin = Enemy("Grouchy Goblin", 5, 1,[stab,d_slash], 2,5,[])
skele = Enemy("Scary Skeleton",7,2,[stab,d_rage],1,10,[])
slomp_monster = Enemy("Slompster", 15, 0,[slomp],5,15,[])
grogus = Enemy("Grogus", 50, 0, [body_slam,expl_cask,body_slam,d_rage],30,100,[])
living_ore = Enemy("Living Ore", 10, 5, [body_slam, jumpscare],20,5,[])

enemies = [goblin, skele, slomp_monster, grogus, living_ore]
#===================================================================================#

#=====================================PLAYER ATTACKS======================================#
sword_swing = PlayerAttack("Sword Swing", "You swing your sword.", 3, 2, [])
axe_swing = PlayerAttack("Axe Swing", "You forcefully swing your axe.", 7, 5, [])
dagger = PlayerAttack("Dagger Slashes", "You slash twice with your dagger", 2, 2, ["double_strike"])
slap = PlayerAttack("Slap", "You slap that fella head smoove off", 1, 0, [])
player_attacks = [sword_swing, axe_swing, dagger, slap]
#=========================================================================================#

#-----------------------------------------------------------------------------------#

def damage_player(amount):
    global player_health
    global player_armor
    damage_taken = max(0, (amount - (random.randint(0,player_armor))))
    player_health -= damage_taken
    print(f"💥 You take {damage_taken} damage [❤️{player_health}/{player_max_health}]")
    if player_health <= 0:
        game_over()

def regain_energy():
    global player_energy
    global player_max_energy
    if player_max_energy - player_energy > 1:
        gain = random.randint(1,(player_max_energy - player_energy))
    else:
        gain = 1
    player_energy += gain
    return gain

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
                    return
            elif chosen_action == 2:
                for i in range(len(player_attacks)):
                    print(f"[{i + 1}]: {player_attacks[i].name} [⚡️{player_attacks[i].energy}] [⚔️{int(player_attacks[i].damage * player_damage_multiplier)}]")
                chosen_attack = int(input("Choose an attack:"))
                if len(enemies) > 1:
                    for i in range(len(enemies)):
                        print(f"[{i + 1}]: attack {enemies[i].name}")
                    try:
                        chosen_enemy = int(input("Choose an enemy to attack:"))
                        player_attack(player_attacks[(chosen_attack-1)], enemies[(chosen_enemy-1)])
                    except IndexError:
                        continue
                else:
                    player_attack(player_attacks[(chosen_attack-1)], enemies[0])
            elif chosen_action == 3:
                if player_max_energy != player_energy:
                    print(f"You rest, regaining⚡️{regain_energy()} energy")
                else:
                    print("You're already at max energy")
                    time.sleep(1.5)
                    continue
            else:
                print("That's not an available action, try again.")
                continue
            player_turn = False
        else: #Enemy Turn
            for enemy in enemies:
                if enemy.health > 0:
                    enemy.attack()
                else:
                    enemies.remove(enemy)
            player_turn = True
    else:
        end_fight(player_health)

def end_fight(health):
    global player_max_health

    test_for_level_up()
    choose_path()
    if heath == player_max_health:
        print("\nYou made it out unscathed!\n")
    elif health >= player_max_health / 2:
            print("\nYou made it out with a couple scratches...\n")
    elif health >=
#--------------------------------------------------------------------------------------#

def player_attack(PlayerAttack, Enemy):
    global player_energy
    player_energy -= PlayerAttack.energy
    print(PlayerAttack.message)
    targets = [Enemy]

    for keyword in PlayerAttack.keywords:
        match keyword:
            case "slap":
                print("slap")
            case "double_strike":
                targets.append(Enemy)

    for target in targets:
        target.damage(int(PlayerAttack.damage * player_damage_multiplier))

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
    print(f"⬆You leveled up to level {player_level} ️\n")
    increase_damage(.1)
    increase_health(10)
    xp_needed += (player_level ** 2 * 5)


def increase_damage(amount):
    global player_damage_multiplier
    player_damage_multiplier += amount
    print(f"⬆️ Your damage raised from ⚔️[{(player_damage_multiplier - amount) * 100}%] to ⚔️[{player_damage_multiplier * 100}%]")

def increase_energy(amount):
    global player_energy
    global player_max_energy

    player_previous_energy = player_energy
    player_previous_max_energy = player_max_energy

    player_energy += amount
    player_max_energy += amount

    print(f"⬆️ Your energy raised from ⚡️{player_previous_energy}/{player_previous_max_energy} to ⚡️{player_energy}/{player_max_energy}")

def increase_health(amount):
    global player_health
    global player_max_health

    player_previous_health = player_health
    player_previous_max_health = player_max_health

    player_health += amount
    player_max_health += amount

    print(f"⬆️ Your health raised from 💚{player_previous_health}/{player_previous_max_health} to 💚{player_health}/{player_max_health}")

#-----------------------------------------------------------------------------------#

def game_over():
    print("⚰️R.I.P.")

#-----------------------------------------------------------------------------------#

game_init()