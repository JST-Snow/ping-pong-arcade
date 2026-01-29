import pygame
import sys
import os

# Инициализация
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Ping-Pong Arcade: World Championship')
clock = pygame.time.Clock()

# Шрифты и цвета
font_main = pygame.font.SysFont("Arial", 50)
font_small = pygame.font.SysFont("Arial", 25)
WHITE, BLACK, GOLD, RED, GREEN = (255, 255, 255), (0, 0, 0), (255, 215, 0), (255, 50, 50), (50, 255, 50)

# Файл рекордов
HS_FILE = "highscores.txt"

def load_highscores():
    if not os.path.exists(HS_FILE): return []
    with open(HS_FILE, "r") as f:
        return sorted([int(s) for s in f.readlines() if s.strip().isdigit()], reverse=True)[:5]

def save_highscore(new_score):
    scores = load_highscores()
    scores.append(new_score)
    scores = sorted(scores, reverse=True)[:5]
    with open(HS_FILE, "w") as f:
        for s in scores: f.write(f"{s}\n")

# Состояния: MENU, DIFFICULTY, PLAYING, VICTORY, GAMEOVER
game_state = 'MENU'
level = 1
player_score, opponent_score = 0, 0
ball_speed_x, ball_speed_y = 6, 6
opponent_speed = 5

# Настройки сложности
difficulties = {
    '1': {'name': 'ЛЕГКО', 'speed': 4, 'ball': 5, 'color': GREEN},
    '2': {'name': 'НОРМАЛЬНО', 'speed': 7, 'ball': 7, 'color': WHITE},
    '3': {'name': 'ХАРДКОР', 'speed': 10, 'ball': 10, 'color': RED}
}

ball = pygame.Rect(WIDTH//2 - 15, HEIGHT//2 - 15, 20, 20)
player = pygame.Rect(WIDTH - 20, HEIGHT//2 - 70, 10, 120)
opponent = pygame.Rect(10, HEIGHT//2 - 70, 10, 120)
player_movement = 0

def draw_text(text, font, color, x, y):
    img = font.render(text, True, color)
    screen.blit(img, (x - img.get_width()//2, y))

# --- Главный цикл ---
while True:
    screen.fill(BLACK)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        if event.type == pygame.KEYDOWN:
            if game_state == 'MENU' and event.key == pygame.K_SPACE:
                game_state = 'DIFFICULTY'
            
            elif game_state == 'DIFFICULTY':
                if event.key in [pygame.K_1, pygame.K_2, pygame.K_3]:
                    diff = difficulties[chr(event.key)]
                    opponent_speed = diff['speed']
                    ball_speed_x = diff['ball']
                    ball_speed_y = diff['ball']
                    player_score, level = 0, 1
                    game_state = 'PLAYING'
            
            elif game_state in ['VICTORY', 'GAMEOVER'] and event.key == pygame.K_r:
                game_state = 'MENU'
            
            if game_state == 'PLAYING':
                if event.key == pygame.K_UP: player_movement -= 8
                if event.key == pygame.K_DOWN: player_movement += 8
        
        if event.type == pygame.KEYUP and game_state == 'PLAYING':
            if event.key == pygame.K_UP: player_movement += 8
            if event.key == pygame.K_DOWN: player_movement -= 8

    # --- Экраны ---
    if game_state == 'MENU':
        draw_text("PING-PONG CHAMPION", font_main, GOLD, WIDTH//2, 100)
        draw_text("Нажми SPACE, чтобы выбрать сложность", font_small, WHITE, WIDTH//2, 220)
        draw_text("РЕКОРДЫ:", font_small, GOLD, WIDTH//2, 350)
        for i, s in enumerate(load_highscores()):
            draw_text(f"{i+1}. {s} PTS", font_small, WHITE, WIDTH//2, 390 + (i * 30))

    elif game_state == 'DIFFICULTY':
        draw_text("ВЫБЕРИ СЛОЖНОСТЬ", font_main, WHITE, WIDTH//2, 150)
        draw_text("1 - ЛЕГКО (Для новичков)", font_small, GREEN, WIDTH//2, 280)
        draw_text("2 - НОРМАЛЬНО (Классика)", font_small, WHITE, WIDTH//2, 330)
        draw_text("3 - ХАРДКОР (Только для профи)", font_small, RED, WIDTH//2, 380)

    elif game_state == 'PLAYING':
        # Логика движения мяча
        ball.x += ball_speed_x
        ball.y += ball_speed_y
        
        if ball.top <= 0 or ball.bottom >= HEIGHT: ball_speed_y *= -1
        if ball.colliderect(player) or ball.colliderect(opponent):
            ball_speed_x *= -1.05 # Постепенное ускорение
            
        # Логика ИИ и Игрока
        if opponent.centery < ball.y: opponent.y += opponent_speed
        if opponent.centery > ball.y: opponent.y -= opponent_speed
        player.y += player_movement
        player.clamp_ip(screen.get_rect())
        opponent.clamp_ip(screen.get_rect())

        # Счет и уровни
        if ball.left <= 0:
            player_score += 10
            ball.center = (WIDTH//2, HEIGHT//2)
            ball_speed_x = abs(ball_speed_x) # Направление к игроку
        if ball.right >= WIDTH:
            save_highscore(player_score)
            game_state = 'GAMEOVER'

        if player_score >= (level * 50):
            level += 1
            opponent_speed += 1
            if level > 5:
                save_highscore(player_score)
                game_state = 'VICTORY'

        # Отрисовка игры
        pygame.draw.rect(screen, WHITE, player)
        pygame.draw.rect(screen, WHITE, opponent)
        pygame.draw.ellipse(screen, GOLD, ball)
        draw_text(f"УРОВЕНЬ: {level}   ОЧКИ: {player_score}", font_small, WHITE, WIDTH//2, 30)

    elif game_state == 'VICTORY':
        draw_text("ТЫ — ЛЕГЕНДА!", font_main, GOLD, WIDTH//2, 200)
        draw_text(f"1 МЕСТО С РЕЗУЛЬТАТОМ {player_score}", font_small, WHITE, WIDTH//2, 300)
        draw_text("Нажми R для меню", font_small, WHITE, WIDTH//2, 450)

    elif game_state == 'GAMEOVER':
        draw_text("ИГРА ОКОНЧЕНА", font_main, RED, WIDTH//2, 200)
        draw_text(f"Твой финальный счет: {player_score}", font_small, WHITE, WIDTH//2, 300)
        draw_text("Нажми R, чтобы попробовать снова", font_small, WHITE, WIDTH//2, 450)

    pygame.display.flip()
    clock.tick(60)