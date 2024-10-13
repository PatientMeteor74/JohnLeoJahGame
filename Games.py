import time
import random
from ast import Index
from random import randint


#-----------------------------------------------------------------------------------#

class Enemy:
    def __init__(self, name, health, armor, attacks, average_gold, keywords):
        self.name = name
        self.health = health
        self.attacks = attacks
        self.average_gold = average_gold
        self.max_health = health
        self.armor = armor
        self.keywords = keywords

    def attack(self):
        attack_id = random.randint(0 , (len(self.attacks)-1))
        print(f"The {self.name} {self.attacks[attack_id].message}")
        damage_player(self.attacks[attack_id].damage)
        return self.attacks[attack_id].stun_chance

    def damage(self, amount):
        damage_taken = amount - (random.randint(0,self.armor))
        self.health -= damage_taken
        if self.health<0:
            self.health = 0
        print(f"You strike the {self.name} dealing {damage_taken} damage. [❤ {self.health}/{self.max_health}]")
        if self.health <= 0:
            self.die()

    def die(self):
        global player_gold
        reward_gold = self.average_gold * random.uniform(0.0, 2.0)
        player_gold += int(reward_gold)
        print(f"It died and dropped {int(reward_gold)} gold")

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
delta = 0
player_turn = False

active_enemies = []
player_gold = 0
player_max_energy = 10
player_energy = player_max_energy
player_stunned = False
#-----------------------------------------------------------------------------------

 #def update():
  #  global delta
   # delta += 1


#-----------------------------------------------------------------------------------

'''while delta >= 0:
    update()'''

#-----------------------------------------------------------------------------------
def choose_path():
    print("You are presented with a number of branching doorways...\n")

    print("[1]: A doorway with the clatters and growls of enemies emanating from within")
    print("[2]: A well-lit corridor with a sign hanging labelled 'shop'")
    print("[3]: A door with ominous shadows visible through the light peeking below, labelled 'KEEP OUT'")
    print("[4]: A quiet pathway which appears perfect for resting")

    choice = int(input("\nInput your choice: \n"))
    global player_turn

    if choice == 1:
        add_active_enemies(1,2)
        player_turn = True
        print("You turn a corner and are faced with a small group of foes...")
        fight(active_enemies)
    elif choice == 2:
        print("shop")
    elif choice == 3:
        add_active_enemies(3, 4)
        player_turn = True
        fight(active_enemies)
        print("You smash through the door to find a dangerous group of enemies waiting for you on the other side...")
    elif choice == 4:
        print ("rest")
    else:
        print("you a retard")
        choose_path()
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
slomp = EnemyAttack("Slomp Attack", " basically slomps teh frick out of you lil bro",2, .1, [])
stab = EnemyAttack("Stab"," lunges forward and stabs you ",3, 0, [])
d_slash = EnemyAttack("Dagger Slash"," quickly slashes you across the chest with a dagger",2, 0, [])
body_slam = EnemyAttack("Body Slam","slams its massive belly into you", 3, .3, [])
d_rage = EnemyAttack("Drunken Rage", "attacks you in a drunken rage",4, .15, [])
expl_cask = EnemyAttack("Explosive Cask", "It throws an explosive cask at you", 5, .2, [])
b_roll = EnemyAttack("Barrel Roll", " whirls a cask your feet", 2, 0, [])
jumpscare = EnemyAttack("Jumpscare", "screams AAAAAAAAAAA", 1, 0, [])

enemy_attacks = [slomp, stab, d_slash, body_slam, d_rage, expl_cask, b_roll, jumpscare]
#=========================================================================================#

#=====================================ENEMIES=======================================#
goblin = Enemy("Grouchy Goblin", 5, 1,[stab,d_slash], 3,[])
skele = Enemy("Scary Skeleton",7,2,[stab,d_rage],4,[] )
slomp_monster = Enemy("Slompster", 15, 0,[slomp],2,[])
grogus = Enemy("Grogus", 50, 0, [body_slam,expl_cask,body_slam,d_rage],30,[])
living_ore = Enemy("Living Ore", 10, 5, [body_slam, jumpscare],20,[])

enemies = [goblin, skele, slomp_monster, grogus, living_ore]
#===================================================================================#

#=====================================PLAYER ATTACKS======================================#
sword_swing = PlayerAttack("Sword Swing", "You swing your sword.", 3, 4, [])
axe_swing = PlayerAttack("Axe Swing", "You swing your axe.", 7, 6, [])
slap = PlayerAttack("Slap", "You slap that fella head smoove off", 1, 0, [])
player_attacks = [sword_swing, axe_swing, slap]
#=========================================================================================#

#-----------------------------------------------------------------------------------#

def damage_player(amount):
    global player_health
    global player_armor
    damage_taken = amount - (random.randint(0, player_armor))
    player_health -= damage_taken
    print(f"You take {damage_taken} damage [❤ {player_health}/{player_max_health}]")
    if player_health <= 0:
        game_over()

def regain_energy():
    global player_energy
    global player_max_energy
    gain = randint(player_max_energy - player_energy)
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
    print("It's time to fight\n"
          "You're facing...")
    for i in range(0,len(enemies)):
        print(f"[ A {enemies[i].name} with ❤ {enemies[i].health} ]")
    while len(enemies) > 0 and player_health > 0:
        if player_turn:
            if player_stunned:
                print("You are stunned and cannot act this turn!")
                time.sleep(1)
                player_stunned = False  # Reset stun status
                player_turn = False  # End player's turn
                continue

            for i in range(len(attack_actions)):
                print(f"[{i + 1}]: {attack_actions[i]}")
            chosen_action = int(input("Choose an action:"))
            if chosen_action == 1:
                print("You pee your pants a little... This battle is too much for you; your only option is to leave...")
                return
            elif chosen_action == 2:
                for i in range(len(player_attacks)):
                    print(f"[{i + 1}]: {player_attacks[i].name}")
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
                print(f"You rest, regaining {regain_energy()} energy")
            else:
                print("That's not an available action, try again.")
            player_turn = False
        else: #Enemy Turn
            for enemy in enemies:
                if enemy.health > 0:
                    stun_chance = enemy.attack() #this actually runs enemy.attack(), imma delete the enemy.attack() above it for now
                    if random.random() < stun_chance:
                        player_stunned = True
                else:
                    enemies.remove(enemy)
            player_turn = True
    else:
        choose_path()


#--------------------------------------------------------------------------------------#

def player_attack(PlayerAttack, Enemy):
    print(PlayerAttack.message)
    Enemy.damage(PlayerAttack.damage)

#-----------------------------------------------------------------------------------#

def game_over():
    print("u lowk ded bru da huzz prol don een fw u no mo cuh ong u done bru ion kno wut u can do atp yn u js cooked fr")

#-----------------------------------------------------------------------------------#

game_init()