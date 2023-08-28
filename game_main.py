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
bullet_image = load_scaled_image("./img/bullet_1.png", 0.06)

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

spuare_pos = [0, 100, 200, 300, 400, 500, 600]
all_square_list = []

# 遊戲狀態和分數的初始化
current_turn = 0
last_turn = 0
continue_game = True

square_index = 0

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

def read_best_score():
    global score
    
    f = open('./game_data/highscore.txt', 'r')
    best_score = list(f.read())
    f.close()
    if len(best_score)<=0:
        best_score =  0
        if score.score > best_score:
            best_score = score.score
    else:
        
        tmp  = max([int(i) for i in best_score if i != '\n'])
        if tmp >= score.score:
            best_score = tmp
        else:
            best_score = score.score



    best_score_font = pygame.font.SysFont(None, 36)
    best_score_text_surface = best_score_font.render(f"best score: {best_score}", True, (255, 255, 255))
    best_score_text_rect = best_score_text_surface.get_rect()
    best_score_text_rect.centerx =100
    best_score_text_rect.centery=700
    screen.blit(best_score_text_surface, best_score_text_rect)



class Square:
    def __init__(self,count,pos,current_turn,index) -> None:
        self.font_count = int(count)
        self.rect = pygame.Rect(pos, -100, 80, 80)
        self.turn = current_turn
        self.pos = [self.rect.x,self.rect.y]
        self.index = index
        

     

    def draw(self):
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(str(self.font_count), True, (255, 255, 255))  # 白色數字
        text_rect = text_surface.get_rect(center=self.rect.center)  # 文字位置設為方塊中心
        screen.blit(text_surface, text_rect)
        pygame.draw.rect(screen,(255,0,255),self.rect,width=6)  
    def move(self):
        self.rect.centery += 100   
    def isCollisoin(self,check):
        if check:
            
            self.font_count -=1
    def wirte_destroied(self,turn):
        
        with open('./game_data/sqare_data_destroied.txt', 'a') as file:
              file.write(f"index:{self.index},creat_turn:{self.turn},destory_turn:{turn},x_pos:{self.rect.x},y_pos:{self.rect.y}\n") 
            
    
       
        







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
        global all_square_list,score,current_turn
        
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



        coollider_distance = 10
        # # 檢查子彈是否與方塊相交
        for square in all_square_list:
            check = True
            if self.rect.colliderect(square) and check:
            #反轉子彈速度
            
                if  abs(square.rect.bottom - self.rect.top) <=coollider_distance:
                    self.y_speed *=-1
                if  abs(square.rect.top - self.rect.bottom) <=coollider_distance:
                    self.y_speed *=-1
                if  abs(square.rect.left - self.rect.right) <=coollider_distance:
                    self.x_speed *=-1
                if  abs(square.rect.right - self.rect.left) <=coollider_distance:
                    self.x_speed *=-1 

                square.isCollisoin(check) # 避免多次碰撞检查
                check = False 
                    

                
                if square.font_count <=0:
                    square.wirte_destroied(current_turn)
                    all_square_list.remove(square)
                    score.score +=1*current_turn
                
    def destroyed(self):
        if  self.rect.bottom >= screen_height:
            return True
        else:
            return False
   

move_counter = 0
bullet_check = False
can_fire = True
fire_pos = []
def wirte_player_data(turn,pos):
    global player_rect
    if pos != []:
        with open('./game_data/player_data.txt', 'a') as file:
            file.write(f"turn:{turn},x_pos:{player_rect.x},fire_pos:{pos}\n") 

def change_turn():
    global current_turn,last_turn,move_counter,player_rect,bullet_check,score,can_fire,fire_pos
    
    if current_turn != last_turn:
        last_turn = current_turn
        move_counter = 0
        for square in all_square_list:
            square.move()
        wirte_player_data(current_turn,fire_pos)




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
    global current_turn,last_turn,all_square_list,square_index
    random_numbers = random.sample(range(2, 6), 1)
  
    square_list_tmp = random.sample(spuare_pos, random_numbers[0])
    if current_turn != last_turn:
        
        for pos in square_list_tmp:
            
            all_square_list.append(Square(count=current_turn,pos=pos,current_turn=current_turn,index=square_index))
            
            square_index +=1
    for square in all_square_list:
        square.draw()
            




def is_game_over(game_sence):
    global all_square_list, bullets, continue_game, score
    if game_sence:
        already_written = False  # 用於追踪是否已經寫入
        for square in all_square_list:

            if square.rect.centery >= 600:
                
                
                continue_game = False
                if not already_written:  # 只有在尚未寫入時才寫入
                    with open('./game_data/highscore.txt', 'a') as file:
                        file.write(f"{score.score}\n")  # 新增文字到檔案末尾，前面的'\n'是換行符。   
                    already_written = True
                    with open('./game_data/player_data.txt', 'a') as file:
                        file.write(f"end\n") 
                    with open('./game_data/sqare_data_destroied.txt', 'a') as file:
                        file.write(f"end\n")
                break
             
    
    
                
                
   
    
        


def reset():
    global square_index,player_rect,current_turn,last_turn,screen_width,bullet_rect,x_speed,y_speed,bullets,all_square_list,font_list,creat_square,move_counter,bullet_check,can_fire,score
    player_rect.centerx = screen_width // 2
    player_rect.centery = 650
    player_rect.center = (player_rect.centerx/2,player_rect.centery)
    
    bullet_rect.centerx = player_rect.centerx
    bullet_rect.centery = player_rect.centery
    x_speed = 8
    y_speed = 8
    bullets = [] 

    square_index = 0
    
  
    all_square_list = []
    font_list = []
    creat_square = True

    current_turn =1
    last_turn = 0
    
    move_counter = 0
    bullet_check = False
    can_fire = True




def main():
    global current_turn,last_turn,bullets,bullet_check,score,continue_game,can_fire,fire_pos
    current_turn +=1
    clock = pygame.time.Clock()
    game_over = False
    black = (0, 0, 0)
    Left = False
    Right = False  
    white = (255, 255, 255)
    
    

    while not game_over:
        is_game_over(continue_game)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if can_fire:
                    fire_pos = list(pygame.mouse.get_pos())
                    if fire_pos[1]>630:
                        fire_pos[1] = 630
                    for i in range(current_turn):
                        bullets.append(Bullet(bullet_image,pos_x=player_rect.centerx,pos_y=player_rect.centery,x_speed=10,y_speed=10,start=(player_rect.x,player_rect.y),pos=fire_pos))
                    bullet_check = True  
                    can_fire = False            
            # checking if keydown event happened or not
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    continue_game = False
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
            pos = list(pygame.mouse.get_pos())
            if pos[1]>630:
                pos[1] = 630

            pygame.draw.line(screen,white,(player_rect.centerx+7,player_rect.centery),pos,width=5)
            screen.blit(player_image, player_rect)
            draw_square()
            score.draw_text()
            read_best_score()
            change_turn()
        else:
            
            point = score.score
            

            screen.fill(black)
            font = pygame.font.SysFont(None, 72)  # 使用較大的字體大小
            game_over_surface = font.render(f"GAME OVER", True, (255, 255, 255))
            game_over_rect = game_over_surface.get_rect(center=(screen_width // 2, screen_height // 2-20))
            screen.blit(game_over_surface, game_over_rect)

            font_3 = pygame.font.SysFont(None, 72)
            game_over_surface_3 = font.render(f"SCORE:{point} ", True, (255, 255, 255))
            game_over_rect_3 = game_over_surface_3.get_rect(center=(screen_width // 2, screen_height // 2 +50))
            screen.blit(game_over_surface_3, game_over_rect_3)



            font_2 = pygame.font.SysFont(None,32)
            game_over_surface_2 = font_2.render("press R to retry or press ESC to exit",True,(255,255,255))
            game_over_rect_2 = game_over_surface_2.get_rect(center=(screen_width // 2, screen_height // 2 + 110))
            screen.blit(game_over_surface_2, game_over_rect_2)
            
           
            
            


            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        score.reset()
                        reset()
                        continue_game = True
                        
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        

            
        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == "__main__":
  
    main()
    