import pygame
import random
import math
from pygame.math import Vector2
from pathlib import Path

# 初始化 Pygame 和字型
pygame.init()
pygame.font.init()

# 定義遊戲視窗大小與標題
screen_width, screen_height = 700, 750
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("打磚塊")

# 顏色定義
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
MAGENTA = (255, 0, 255)

# 加載並縮放玩家和子彈的圖片
def load_scaled_image(path, scale_factor):
    image = pygame.image.load(path)
    return pygame.transform.scale(image, (int(image.get_width() * scale_factor), int(image.get_height() * scale_factor)))

player_image = load_scaled_image(".\img\player.png", 0.1)
bullet_image = load_scaled_image("./img/bullet_1.png", 0.1)

# 玩家和子彈的設定
player_rect = player_image.get_rect()
player_speed = 5
player_rect.centerx = screen_width // 2
player_rect.centery = 650
bullet_rect = bullet_image.get_rect()
bullet_rect.centerx = player_rect.centerx
bullet_rect.centery = player_rect.centery
x_speed, y_speed = 8, 8
bullets = []

# 方塊的設定
square_collision_counts = []
spuare_pos = [0, 100, 200, 300, 400, 500, 600]
all_square_list = []

# 遊戲狀態和分數的初始化
current_turn = 0
last_turn = 0
continue_game = True


# 定義Score類
class Score:
    def __init__(self):
        self.score = 0
        self.count = 0

    def score_chage(self, turn):
        self.score += self.count * turn

    def draw_text(self):
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(f"score: {self.score}", True, WHITE)
        text_rect = text_surface.get_rect(center=(340, 700))
        screen.blit(text_surface, text_rect)

    def reset(self):
        self.score = 0
        self.count = 0

score = Score()

class Bullet:
    def __init__(self,image,pos_x,pos_y,x_speed,y_speed,start,pos) -> None:
        self.image = image
        self.rect  = self.image.get_rect()
        self.rect.centerx = pos_x
        self.rect.centery = pos_y
        self.x_speed = x_speed
        self.y_speed = y_speed

        self.start = Vector2(start)
        self.target = Vector2(pos)
        self.count = Vector2([pos[0]-self.start[0], -self.start[1]])
        self.count = self.count.normalize()
    

        

        self.target_x = pos[0]
        self.target_y = pos[1]

        self.move_x = 0
        self.move_y = 0

        self.diff_x = self.target_x - self.rect.centerx #X座標差
        self.diff_y = self.target_y - self.rect.centery #Y座標差

        self.canMove = False
        self.moved_distance = 0

    def draw(self):
       
        screen.blit(self.image, self.rect)

    def move(self):
        global squares,all_square_list,square_collision_counts,score,current_turn
        
        # math.sqrt() 平方根，畢氏定理
        distance = math.sqrt(self.diff_x**2 + self.diff_y**2)
        self.move_x = self.diff_x / distance
        self.move_y = self.diff_y / distance  

        x_movement = self.x_speed * self.count.x
        y_movement = self.y_speed * self.count.y

        # 更新移动的距离
        self.rect.centerx += self.move_x*self.x_speed
        self.rect.centery += self.move_y*self.y_speed

        self.moved_distance += abs(x_movement) + abs(y_movement)



        if self.rect.right >= screen_width or self.rect.left <= 0:
            self.x_speed *= -1
        if  self.rect.top <= 0:
            self.y_speed *= -1


        # # 檢查子彈是否與方塊相交
        for i, squares in enumerate(all_square_list):
            for j, square in enumerate(squares):
                if self.rect.colliderect(square):
                    
                   
                  
                    #反轉子彈速度
                    if  abs(square.bottom - self.rect.top) <=10:
                        self.y_speed *=-1
                    if  abs(square.top - self.rect.bottom) <=10:
                        self.y_speed *=-1
                    if  abs(square.left - self.rect.right) <=10:
                        self.x_speed *=-1
                    if  abs(square.right - self.rect.left) <=10:
                        self.x_speed *=-1
                    

                    square_collision_counts[i][j] += 1
                    if square_collision_counts[i][j] >= (i + 1):
                        squares.remove(square)
                        del square_collision_counts[i][j]
                        score.count +=1
                        score.score_chage(current_turn)
                    break  # 避免多次碰撞检查

    def destroyed(self):
        if  self.rect.bottom >= screen_height:
            return True
        else:
            return False
   

move_counter = 0
bullet_check = False
can_fire = True

def change_turn():
    global current_turn,last_turn,move_counter,player_rect,bullet_check,score,can_fire
    
    if current_turn != last_turn:
        
        last_turn = current_turn
        move_counter = 0
    if len(bullets)<=0 and bullet_check:
        current_turn += 1
        score.count = 0
        bullet_check = False
        can_fire =True
        
        
def move_bullets():
    global move_counter
    threshold_distance = 50  # 子彈需要移動的距離，之後允許下一個子彈開始移動
    
    for i in range(len(bullets)):
        if i== 0:
            bullets[i].move()
        elif i >0 and bullets[i-1].moved_distance >=threshold_distance:
            bullets[i].move()



def draw_square():
   
    global current_turn,last_turn,all_square_list,square_collision_counts
   
    square_list_tmp = []
    square_list = []
    random_numbers = random.sample(range(2, 6), 1)
  
    square_list_tmp = random.sample(spuare_pos, random_numbers[0])

    if current_turn != last_turn:
        for pos in square_list_tmp:
            tmp = pygame.Rect(pos, -100, 100, 100)
            square_list.append(tmp)
        all_square_list.append(square_list)
        square_collision_counts.append([0] * len(square_list))
        square_move()

    # 創建字體對象
    font = pygame.font.SysFont(None, 36)
    
    try:
       
        for i in range(current_turn):
            for square in all_square_list[i]:
                pygame.draw.rect(screen,(255,0,255),square,width=6)
                
                # 繪製方塊中的數字
                text_surface = font.render(str(i+1), True, (255, 255, 255))  # 白色數字
                text_rect = text_surface.get_rect(center=square.center)  # 文字位置設為方塊中心
                screen.blit(text_surface, text_rect)
        
    except:
        pass


def square_move():
    global all_square_list, bullets, continue_game, score
    
    already_written = False  # 用於追踪是否已經寫入

    for i in range(current_turn):
        for square in all_square_list[i]:
            square.centery += 100
            if square.centery >= 600:
                continue_game = False
                if not already_written:  # 只有在尚未寫入時才寫入
                    with open('./game_data/highscore.txt', 'a') as file:
                        file.write(f"{score.score}\n")  # 新增文字到檔案末尾，前面的'\n'是換行符。
                    score.reset()
                    already_written = True


def rest():
    global player_rect,current_turn,last_turn,screen_width,bullet_rect,x_speed,y_speed,bullets,square_collision_counts,all_square_list,font_list,creat_square,move_counter,bullet_check,can_fire,score
    player_rect.centerx = screen_width // 2
    player_rect.centery = 650
    player_rect.center = (player_rect.centerx/2,player_rect.centery)

    bullet_rect.centerx = player_rect.centerx
    bullet_rect.centery = player_rect.centery
    x_speed = 8
    y_speed = 8
    bullets = [] 

    square_collision_counts = []
  
    all_square_list = []
    font_list = []
    creat_square = True

    current_turn =1
    last_turn = 0
    
    move_counter = 0
    bullet_check = False
    can_fire = True




def main():
    global current_turn,last_turn,bullets,bullet_check,score,continue_game,can_fire
    current_turn +=1
    clock = pygame.time.Clock()
    game_over = False
    black = (0, 0, 0)
    Left = False
    Right = False  
    white = (255, 255, 255)
    
    

    while not game_over:
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if can_fire:
                    for i in range(current_turn):
                        bullets.append(Bullet(bullet_image,pos_x=player_rect.centerx,pos_y=player_rect.centery,x_speed=10,y_speed=10,start=(player_rect.x,player_rect.y),pos=pygame.mouse.get_pos()))
                    bullet_check = True  
                    can_fire = False            
            # checking if keydown event happened or not
            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_a:
                    Left = True

                if event.key == pygame.K_d:
                    Right = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_a:
                    Left = False
                if event.key == pygame.K_d:
                    Right = False
            
         
            if Left:
                player_rect.centerx -=10
            if Right:
                player_rect.centerx +=10
        
        if continue_game:
            screen.fill(black)
            move_bullets()  
            try:
                for bullet in bullets:
                    bullet.draw()
                    if bullet.destroyed():
                        bullets.remove(bullet)
            except:
                pass
            pos = pygame.mouse.get_pos()
            pygame.draw.line(screen,white,(player_rect.centerx+7,player_rect.centery),pos,width=5)
            screen.blit(player_image, player_rect)
    
            draw_square()
            
            score.draw_text()
            change_turn()
        else:
            rest()

            screen.fill(black)
            font = pygame.font.SysFont(None, 72)  # 使用較大的字體大小
            game_over_surface = font.render("GAME OVER", True, (255, 255, 255))
            game_over_rect = game_over_surface.get_rect(center=(screen_width // 2, screen_height // 2))
            screen.blit(game_over_surface, game_over_rect)
            font_2 = pygame.font.SysFont(None,32)
            game_over_surface_2 = font_2.render("press R to retry or press ESC to exit",True,(255,255,255))
            game_over_rect_2 = game_over_surface_2.get_rect(center=(screen_width // 2, screen_height // 2 + 50))
            screen.blit(game_over_surface_2, game_over_rect_2)
            


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        continue_game = True
                        
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        

            
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
  
    main()
    