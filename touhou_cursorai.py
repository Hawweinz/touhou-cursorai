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
# player configs
PLAYER_HP = 5
PLAYER_SPEED_NORMAL = 6
PLAYER_SPEED_SLOW = 3
PLAYER_SHOOT_COOLDOWN = 5
PLAYER_HIT_COOLDOWN = 20

class Player:
    def __init__(self, canvas, x, y):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.hp = PLAYER_HP
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
    def __init__(self, canvas, x, y, init_shoot_dir=0, angular_speed=0.1):
        super().__init__(canvas, x, y)
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

class GameScene:
    def __init__(self, master):
        self.master = master
        self.canvas = tk.Canvas(master, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.canvas.configure(bg=BACKGROUND_COLOR)
        self.player = Player(self.canvas, WIDTH / 2, HEIGHT / 2)
        self.enemies = [Enemy(self.canvas, random.randint(0, WIDTH - 10), random.randint(0, HEIGHT // 3 - 10)) for _ in range(5)]
        self.bullets = []
        self.master.bind("<KeyPress>", self.key_press)
        self.master.bind("<KeyRelease>", self.key_release)
        self.keys = set()
        self.game_over = False
        self.pause = False
        self.enemy_limit = 8

        # Display player's score and HP at the bottom-left corner of the game
        self.score_text = self.canvas.create_text(5, HEIGHT - 22, text=f"Score: {self.player.score:09d}", anchor="w", fill="white")
        self.hp_text = self.canvas.create_text(5, HEIGHT - 7, text="Player: " + self.player.hp * "★ ", anchor="w", fill="red")
        
        self.run_game()

    
    def key_press(self, event):
        if event.keysym == "space":
            self.keys.add("space")
        elif event.keysym.isalpha():
            self.keys.add(event.keysym.upper())
        else:
            self.keys.add(event.keysym)
            
        if event.keysym.upper() == "P":  # Add this line to handle pause/resume
            self.pause = not self.pause
            if self.pause:
                self.pause_text = self.canvas.create_text(WIDTH / 2, HEIGHT / 2, text="Press P to Resume", font=("Arial", 16), fill="white")
            else:
                self.canvas.delete(self.pause_text)
        
    
    def key_release(self, event):
        if event.keysym == "space":
            self.keys.discard("space")
        elif event.keysym.isalpha():
            self.keys.discard(event.keysym.upper())
        else:
            self.keys.discard(event.keysym)
    
    
    def shoot_enemy_bullets(self):
        for enemy in self.enemies:
            if enemy.cooldown_counter <= 0:
                self.bullets.append(enemy.shoot_bullet())
                enemy.cooldown_counter = enemy.cooldown
            else:
                enemy.cooldown_counter -= 1

    
    def generate_enemy(self):
        if len(self.enemies) >= self.enemy_limit:
            return
        enemy_type = random.random()
        x = random.randint(0, WIDTH - 10)
        if enemy_type < 0.8:
            rotate_direction = 2 * random.randint(0,1) - 1
            self.enemies.append(RotatingEnemy(self.canvas, x, 0, 5, rotate_direction * 0.1))
        else:
            self.enemies.append(Enemy(self.canvas, x, 0, 20))

    
    def check_bullets(self):
        for enemy in self.enemies:
            # Set enemy color to red
            self.canvas.itemconfig(enemy.shape, fill=ENEMY_COLOR)
        self.canvas.itemconfig(self.player.shape, fill=PLAYER_COLOR)
        for bullet in self.bullets:
            if bullet.from_ == 0:  # Bullet from player
                for enemy in self.enemies:
                    if self.check_collision(bullet, enemy):
                        enemy.hp -= 1
                        self.canvas.itemconfig(enemy.shape, fill=ENEMY_COLOR_HIT)
                        if enemy.hp <= 0:
                            self.canvas.delete(enemy.shape)
                            self.enemies.remove(enemy)
                            self.player.score += 100
                        self.canvas.delete(bullet.shape)
                        self.bullets.remove(bullet)
                        break
            elif bullet.from_ == 1:  # Bullet from enemy
                if self.check_collision(bullet, self.player):
                    # elf.canvas.itemconfig(self.player.shape, fill=PLAYER_COLOR_HIT)
                    self.player.apply_damage()
                    self.canvas.delete(bullet.shape)
                    self.bullets.remove(bullet)
                    break

    
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
                self.apply_damage()
                break
                
    
    def update(self):
        if not self.pause:
            if "A" in self.keys and self.player.x > 0:
                self.player.move(-1, 0)
            if "D" in self.keys and self.player.x < WIDTH:
                self.player.move(1, 0)
            if "W" in self.keys and self.player.y > 0:
                self.player.move(0, -1)
            if "S" in self.keys and self.player.y < HEIGHT:
                self.player.move(0, 1)
    
            if "Shift_L" in self.keys:
                self.canvas.delete(self.player.shape)
                self.player.shape = self.canvas.create_rectangle(self.player.x + 2, self.player.y + 2, self.player.x + 9, self.player.y + 9, fill=PLAYER_COLOR)
                self.player.speed = PLAYER_SPEED_SLOW
            else:
                self.canvas.delete(self.player.shape)
                self.player.shape = self.canvas.create_rectangle(self.player.x, self.player.y, self.player.x + 10, self.player.y + 10, fill=PLAYER_COLOR)
                self.player.speed = PLAYER_SPEED_NORMAL
            
            if "space" in self.keys and self.player.shoot_cooldown_counter <= 0:
                self.bullets.append(self.player.shoot_bullet())
                self.player.shoot_cooldown_counter = self.player.shoot_cooldown  # Set cool-down to 0.5 seconds (10 * 50ms)
    
            if self.player.shoot_cooldown_counter > 0:
                self.player.shoot_cooldown_counter -= 1
    
            if self.player.hit_cooldown_counter > 0:
                self.player.hit_cooldown_counter -= 1
    
            self.shoot_enemy_bullets()
            if random.random() < 0.1:
                self.generate_enemy()
    
            for bullet in self.bullets:
                bullet.move(0, 1)
                # Remove bullets that are out of screen
                if bullet.y < 0 or bullet.y > 1.5 * HEIGHT:
                    self.canvas.delete(bullet.shape)
                    self.bullets.remove(bullet)
            self.check_bullets()
    
            # Move enemies downward slowly
            for enemy in self.enemies:
                enemy.move(0, 1)
                # Remove enemies that are out of screen
                if enemy.y > HEIGHT:
                    self.canvas.delete(enemy.shape)
                    self.enemies.remove(enemy)
    
            if self.player.hp <= 0:
                self.check_game_over()
    
            # Update player's score and HP text
            self.canvas.itemconfig(self.score_text, text=f"Score: {self.player.score:09d}")
            self.canvas.itemconfig(self.hp_text, text="Player: " + self.player.hp * "★ ",)

        if not self.game_over:
            self.master.after(50, self.update)
        
    
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
        
if __name__ == "__main__":
    root = tk.Tk()
    root.title("Touhou Cursorai ~ Algorithmic Spellcasters' Banquet")
    game = GameScene(root)
