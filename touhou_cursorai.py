import tkinter as tk
import random
import math

# window
HEIGHT = 600
WIDTH = 400
# colors
BACKGROUND_COLOR = "black"
ENEMY_COLOR = "green"
ENEMY_COLOR_HIT = "pink"
PLAYER_COLOR = "red"
PLAYER_COLOR_HIT = "cyan"
ENEMY_BULLET_COLOR = "white"
PLAYER_BULLET_COLOR = "yellow"
LIFE_ITEM_COLOR = "pink"
BOMB_ITEM_COLOR = "light blue"
BOMB_EXPLODE_COLOR = "cyan"
# player configs
PLAYER_HP = 5
INIT_BOMBS = 3
BOMB_RADIUS = 200
PLAYER_SPEED_NORMAL = 6
PLAYER_SPEED_SLOW = 3
PLAYER_SHOOT_COOLDOWN = 5
PLAYER_HIT_COOLDOWN = 20
# enemy configs
DIFFICULTY = 1 # 0: easy, 1: normal, 2: hard, 3: lunatic
DIFFICULTY_TEXT = ["Easy", "Normal", "Hard", "Lunatic"]
ENEMY_COOLDOWN_SHORT = [10, 5, 2, 1] # [easy, normal, hard, lunatic]
ENEMY_COOLDOWN_LONG = [20, 16, 12, 8]
MAX_ENEMY_COUNT = [5, 8, 12, 16]
# ITEM DROP CHANCE
ITEM_DROP_CHANCE = 0.05
ITEM_SPEED = 1.5

class Player:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.hp = PLAYER_HP
        self.bomb = INIT_BOMBS
        self.shape = canvas.create_rectangle(x, y, x + 10, y + 10, fill=PLAYER_COLOR)
        self.speed = PLAYER_SPEED_NORMAL
        self.score = 0
        self.shoot_cooldown = PLAYER_SHOOT_COOLDOWN
        self.hit_cooldown = PLAYER_HIT_COOLDOWN
        self.hit_cooldown_counter = 0
        self.shoot_cooldown_counter = 0

    def move(self, dx, dy):
        dx = self.speed * dx
        dy = self.speed * dy
        self.x += dx
        self.y += dy
        self.canvas.move(self.shape, dx, dy)

    def shoot_bullet(self):
        return Bullet(self.canvas, self.x, self.y, 0, -5, 0)

    def apply_damage(self):
        if self.hit_cooldown_counter <= 0:
            self.hp -= 1
            self.hit_cooldown_counter = PLAYER_HIT_COOLDOWN
            self.canvas.itemconfig(self.shape, fill=PLAYER_COLOR_HIT)

class Enemy:
    def __init__(self, canvas, x, y, cooldown=5):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.hp = 2
        self.speed = 2
        self.shape = canvas.create_rectangle(x, y, x + 15, y + 15, fill=ENEMY_COLOR)
        self.cooldown = cooldown
        self.cooldown_counter = 0

    def shoot_bullet(self, direction=None):
        if direction is None:
            direction = random.uniform(-1, 1)
        dx = self.speed * math.sin(direction * math.pi)
        dy = self.speed * math.cos(direction * math.pi)  # Vertically downward
        bullet = Bullet(self.canvas, self.x, self.y, dx, dy, 1)
        return bullet
    # Add move method to the Enemy class
    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.canvas.move(self.shape, dx, dy)

class RotatingEnemy(Enemy):
    def __init__(self, canvas, x, y, cooldown=3, init_shoot_dir=0, angular_speed=0.1):
        super().__init__(canvas, x, y, cooldown)
        self.curr_shoot_dir = init_shoot_dir
        self.angular_speed = angular_speed

    def shoot_bullet(self, direction=None):
        bullet = super().shoot_bullet(self.curr_shoot_dir)
        self.curr_shoot_dir += self.angular_speed
        return bullet


class Bullet:
    def __init__(self, canvas, x, y, dx, dy, from_):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        if from_ == 0:
            self.shape = canvas.create_rectangle(x + 3, y, x + 7, y + 10, fill=PLAYER_BULLET_COLOR)
        else:
            self.shape = canvas.create_polygon(x, y + 2.5, x + 2.5, y, x + 5, y + 2.5, x + 2.5, y + 5, fill=ENEMY_BULLET_COLOR)
        self.from_ = from_ # 0 for player and 1 for enemy

    def move(self, dx=0, dy=0):
        self.x += self.dx + dx
        self.y += self.dy + dy
        self.canvas.move(self.shape, self.dx, self.dy)

class Item:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.speed = ITEM_SPEED
        # self.shape = canvas.create_rectangle(x, y, x + 10, y + 10, fill="white")

    def move(self):
        self.y += self.speed
        self.canvas.move(self.shape, 0, self.speed)

    def pickup(self):
        pass

class LifeItem(Item):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y)
        self.shape = canvas.create_rectangle(x, y + 5, x + 20, y + 30, fill=LIFE_ITEM_COLOR)
    def pickup(self, player):
        player.hp += 1

class BombItem(Item):
    def __init__(self, canvas, x, y):
        super().__init__(canvas, x, y)
        self.shape = canvas.create_rectangle(x, y + 5, x + 20, y + 30, fill=BOMB_ITEM_COLOR)
    def pickup(self, player):
        player.bomb += 1

class BombExplosion:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = BOMB_RADIUS
        self.shape = canvas.create_oval(x - self.radius, y - self.radius, x + self.radius, y + self.radius, outline=BOMB_EXPLODE_COLOR, width=3)
        self.time_to_vanish = 10

    def update(self):
        if self.time_to_vanish <= 0:
            self.canvas.delete(self.shape)
            return
        self.time_to_vanish -= 1


class GameScene:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.canvas.configure(bg=BACKGROUND_COLOR)
        self.player = Player(self.canvas, WIDTH / 2, HEIGHT / 2)
        self.enemies = [Enemy(self.canvas, random.randint(0, WIDTH - 10), random.randint(0, HEIGHT // 3 - 10), ENEMY_COOLDOWN_LONG[DIFFICULTY]) for _ in range(2)]
        self.bullets = []
        self.items = []
        self.bomb_explosions = []
        self.allow_new_explosion = True
        self.master.bind("<KeyPress>", self.key_press)
        self.master.bind("<KeyRelease>", self.key_release)
        self.keys = set()
        self.game_over = False
        self.pause = False

        # Display player's score and HP at the bottom-left corner of the game
        self.score_text = self.canvas.create_text(5, 7, text=f"Score: {self.player.score:09d}", anchor="w", fill="white")
        self.hp_text = self.canvas.create_text(5, 22, text="Player: " + self.player.hp * "♥ ", anchor="w", fill="red")
        self.bomb_text = self.canvas.create_text(5, 37, text="Bombs: " + self.player.bomb * "★ ", anchor="w", fill="light blue")
        self.difficulty_text = self.canvas.create_text(WIDTH - 5, 5, text=f"Difficulty: {DIFFICULTY_TEXT[DIFFICULTY]}", anchor="ne", fill="white")
        
        self.run_game()

    
    def key_press(self, event):
        self.keys.add(event.keysym.upper())
            
        if event.keysym.upper() == "P":  # Add this line to handle pause/resume
            self.pause = not self.pause
            if self.pause:
                self.pause_text = self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text="Press P to Resume", font=("Arial", 16), fill="white")
            else:
                self.canvas.delete(self.pause_text)
        
    
    def key_release(self, event):
        self.keys.discard(event.keysym.upper())
    
    
    def handle_enemy_shooting(self):
        for enemy in self.enemies:
            if enemy.cooldown_counter <= 0:
                self.bullets.append(enemy.shoot_bullet())
                enemy.cooldown_counter = enemy.cooldown
            else:
                enemy.cooldown_counter -= 1

    def generate_item(self, x, y):
        if random.random() < ITEM_DROP_CHANCE:              
            if random.random() < 0.5:
                life = LifeItem(self.canvas, x, y)
                self.items.append(life)
            else:
                bomb = BombItem(self.canvas, x, y)
                self.items.append(bomb)
    
    def generate_enemy(self):
        if len(self.enemies) >= MAX_ENEMY_COUNT[DIFFICULTY] or random.random() < 0.9:
            return
        enemy_type = random.random()
        x = random.randint(0, WIDTH - 10)
        if enemy_type < 0.8:
            rotate_direction = 2 * random.randint(0,1) - 1
            self.enemies.append(RotatingEnemy(self.canvas, x, 0, ENEMY_COOLDOWN_SHORT[DIFFICULTY], 0, rotate_direction * 0.1))
        else:
            self.enemies.append(Enemy(self.canvas, x, 0, ENEMY_COOLDOWN_LONG[DIFFICULTY]))

    
    def check_bullet_collisions(self):
        self.reset_colors()
        for bullet in self.bullets:
            if bullet.from_ == 0:  # Bullet from player
                self.handle_player_bullet_collision(bullet)
            elif bullet.from_ == 1:  # Bullet from enemy
                self.handle_enemy_bullet_collision(bullet)

    
    def reset_colors(self):
        for enemy in self.enemies:
            self.canvas.itemconfig(enemy.shape, fill=ENEMY_COLOR)
        self.canvas.itemconfig(self.player.shape, fill=PLAYER_COLOR)

    def handle_player_bullet_collision(self, bullet):
        for enemy in self.enemies:
            if self.check_collision(bullet, enemy):
                enemy.hp -= 1
                self.canvas.itemconfig(enemy.shape, fill=ENEMY_COLOR_HIT)
                if enemy.hp <= 0:
                    self.canvas.delete(enemy.shape)
                    self.enemies.remove(enemy)
                    self.player.score += 100
                    self.generate_item(enemy.x, enemy.y)
                self.canvas.delete(bullet.shape)
                self.bullets.remove(bullet)
                break

    
    def handle_enemy_bullet_collision(self, bullet):
        if self.check_collision(bullet, self.player):
            self.player.apply_damage()
            self.canvas.delete(bullet.shape)
            self.bullets.remove(bullet)

    
    def check_collision(self, obj1, obj2):
        obj1_coords = self.canvas.coords(obj1.shape)
        obj2_coords = self.canvas.coords(obj2.shape)
        return (obj1_coords[0] < obj2_coords[2] and obj1_coords[2] > obj2_coords[0] and
                obj1_coords[1] < obj2_coords[3] and obj1_coords[3] > obj2_coords[1])

    def chek_enemy_player_collision(self):
        # Check if enemy hits player, if true, player hp -1
        for enemy in self.enemies:
            if self.check_collision(enemy, self.player):
                # self.canvas.itemconfig(self.player.shape, fill=PLAYER_COLOR_HIT)
                self.player.apply_damage()
                break

    def check_bomb_explosion_collision(self):
        for bomb_explosion in self.bomb_explosions:
            for enemy in self.enemies:
                if math.sqrt((bomb_explosion.x - enemy.x)**2 + (bomb_explosion.y - enemy.y)**2) <= BOMB_RADIUS:
                    self.canvas.delete(enemy.shape)
                    self.enemies.remove(enemy)
                    self.player.score += 100
            for bullet in self.bullets:
                if bullet.from_ == 1 and math.sqrt((bomb_explosion.x - bullet.x)**2 + (bomb_explosion.y - bullet.y)**2) <= BOMB_RADIUS:
                    self.canvas.delete(bullet.shape)
                    self.bullets.remove(bullet)
                    

    def update_bomb_explosions(self):
        for bomb_explosion in self.bomb_explosions:
            bomb_explosion.update()
            if bomb_explosion.time_to_vanish <= 0:
                self.canvas.delete(bomb_explosion.shape)
                self.bomb_explosions.remove(bomb_explosion)

    
    def explode_bomb(self, x, y):
        self.bomb_explosions.append(BombExplosion(self.canvas, x, y))

    
    def handle_bomb(self):
        if self.allow_new_explosion:
            if "X" in self.keys and self.player.bomb > 0:
                self.allow_new_explosion = False
                self.player.bomb -= 1
                self.explode_bomb(self.player.x, self.player.y)
        else:
            self.allow_new_explosion =  ("X" not in self.keys)

    
    def handle_player_movement(self):
        if "LEFT" in self.keys and self.player.x > 0:
            self.player.move(-1, 0)
        if "RIGHT" in self.keys and self.player.x < WIDTH:
            self.player.move(1, 0)
        if "UP" in self.keys and self.player.y > 0:
            self.player.move(0, -1)
        if "DOWN" in self.keys and self.player.y < HEIGHT:
            self.player.move(0, 1)

    def handle_difficulty_change(self):
        global DIFFICULTY
        if "1" in self.keys:
            DIFFICULTY = 0
        if "2" in self.keys:
            DIFFICULTY = 1
        if "3" in self.keys:
            DIFFICULTY = 2
        if "4" in self.keys:
            DIFFICULTY = 3

    def handle_player_shooting(self):
        if "SHIFT_L" in self.keys:
            self.canvas.delete(self.player.shape)
            self.player.shape = self.canvas.create_rectangle(self.player.x + 2, self.player.y + 2, self.player.x + 9, self.player.y + 9, fill=PLAYER_COLOR)
            self.player.speed = PLAYER_SPEED_SLOW
        else:
            self.canvas.delete(self.player.shape)
            self.player.shape = self.canvas.create_rectangle(self.player.x, self.player.y, self.player.x + 10, self.player.y + 10, fill=PLAYER_COLOR)
            self.player.speed = PLAYER_SPEED_NORMAL
        
        if "Z" in self.keys and self.player.shoot_cooldown_counter <= 0:
            self.bullets.append(self.player.shoot_bullet())
            self.player.shoot_cooldown_counter = self.player.shoot_cooldown

    def handle_player_hit_cooldown(self):
        if self.player.shoot_cooldown_counter > 0:
            self.player.shoot_cooldown_counter -= 1

        if self.player.hit_cooldown_counter > 0:
            self.player.hit_cooldown_counter -= 1


    def move_bullets(self):
        for bullet in self.bullets:
            bullet.move(0, 1)
            if bullet.y < 0 or bullet.y > 1.5 * HEIGHT:
                self.canvas.delete(bullet.shape)
                self.bullets.remove(bullet)

    

    def move_enemies(self):
        for enemy in self.enemies:
            enemy.move(0, 1)
            if enemy.y > HEIGHT:
                self.canvas.delete(enemy.shape)
                self.enemies.remove(enemy)

    def move_and_pickup_items(self):
        for item_ in self.items:
            item_.move()
            if self.check_collision(item_, self.player):
                item_.pickup(self.player)
                self.canvas.delete(item_.shape)
                self.items.remove(item_)
            elif item_.y > HEIGHT:
                self.canvas.delete(item_.shape)
                self.items.remove(item_)

    def update_ui(self):
        self.canvas.itemconfig(self.score_text, text=f"Score: {self.player.score:09d}")
        self.canvas.itemconfig(self.hp_text, text="Player: " + self.player.hp * "♥ ",)
        self.canvas.itemconfig(self.bomb_text, text="Bombs: " + self.player.bomb * "★ ")
        self.canvas.itemconfig(self.difficulty_text, text=f"Difficulty: {DIFFICULTY_TEXT[DIFFICULTY]}")
    
    def run_game(self):
        self.update()
        self.master.mainloop()

    def check_game_over(self):
        if self.player.hp <= 0:
            self.game_over = True
            self.master.unbind("<KeyPress>")
            self.master.unbind("<KeyRelease>")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text="Game Over", font=("Arial", 24), fill="white")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 30, text="Press Enter to Restart", font=("Arial", 16), fill="white")
            self.master.bind("<Return>", self.restart_game)

    def restart_game(self, event):
        self.canvas.delete("all")
        self.canvas.pack_forget()  # Add this line to remove the old canvas
        self.__init__(self.master)

    
    def update(self):
        global DIFFICULTY
        
        if not self.pause:
            self.handle_player_movement()
            self.handle_difficulty_change()
            self.handle_player_shooting()
            self.handle_player_hit_cooldown()
            self.handle_enemy_shooting()
            self.generate_enemy()
            self.move_bullets()
            self.move_enemies()
            self.check_bullet_collisions()
            self.chek_enemy_player_collision()
            self.check_bomb_explosion_collision()
            self.update_bomb_explosions()
            self.move_and_pickup_items()
            self.handle_bomb()
            self.check_game_over()
            self.update_ui()

        if not self.game_over:
            self.master.after(50, self.update)

        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Touhou Cursorai ~ Algorithmic Spellcasters' Banquet")
    game = GameScene(root)
