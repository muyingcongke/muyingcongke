import pygame as pg
import os
import sys 
import time
from api import *


# 初始化 Pygame
pg.init()

font_path = os.path.join("fonts", "msyh.ttc")  # 替换为您的字体文件
font = pg.font.Font(font_path, 36)
countdown_font = pg.font.Font(font_path, 24)  # 倒计时字体大小

def draw_game_over_screen(screen, is_win=False):
    overlay = pg.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pg.SRCALPHA)
    overlay.fill((255, 255, 255, 128))
    screen.blit(overlay, (0, 0))
    
    if is_win:
        image = win_image
        text = "恭喜你赢了！按空格键重新开始"
        text_color = (0, 255, 0)  # 绿色
    else:
        image = fail_image
        text = "游戏失败！按空格键重新开始"
        text_color = (255, 0, 0)  # 红色
    
    # 计算图片位置（居中）
    image_rect = image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
    screen.blit(image, image_rect)
    
    # 渲染文本
    text_surface = font.render(text, True, text_color)
    text_rect = text_surface.get_rect(center=(SCREEN_WIDTH // 2, image_rect.bottom + 30))
    screen.blit(text_surface, text_rect)

def draw_countdown(screen, remaining_time):
    minutes = int(remaining_time / 60)
    seconds = int(remaining_time % 60)
    time_text = countdown_font.render(f"时间: {minutes:02d}:{seconds:02d}", True, WHITE)
    screen.blit(time_text, (10, 10))  # 在屏幕左上角显示时间

def main():
    global game_state
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption("动了个物")
    clock = pg.time.Clock()

    # 创建难度选择按钮和退出按钮
    button_width, button_height = 200, 50
    button_spacing = 20
    total_height = 4 * button_height + 3 * button_spacing
    start_y = (SCREEN_HEIGHT - total_height) // 2

    easy_button = Button(SCREEN_WIDTH // 2 - button_width // 2, start_y, button_width, button_height, "简单", GRAY)
    normal_button = Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + button_height + button_spacing, button_width, button_height, "普通", GRAY)
    hard_button = Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + 2 * (button_height + button_spacing), button_width, button_height, "困难", GRAY)
    quit_button = Button(SCREEN_WIDTH // 2 - button_width // 2, start_y + 3 * (button_height + button_spacing), button_width, button_height, "退出游戏", GRAY)

    game_over_screen = None

    game_state = MENU
    game_images = [] #存放所有生成的图片
    bottom_images = [None] * BOTTOM_GRID_COLS
    start_time = 0
    remaining_time = COUNTDOWN_TIME
    waiting_for_match = False

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.MOUSEBUTTONDOWN and game_state == MENU:
                pos = event.pos
                if easy_button.is_clicked(pos):
                    game_state = EASY
                elif normal_button.is_clicked(pos):
                    game_state = MEDIUM
                elif hard_button.is_clicked(pos):
                    game_state = HARD
                elif quit_button.is_clicked(pos):
                    pg.quit()
                    sys.exit()
                if game_state in [EASY, MEDIUM, HARD]:
                    game_images = create_game_images(images, game_state)
                    start_time = time.time()  # 记录游戏开始时间
                    remaining_time = COUNTDOWN_TIME
                    game_over_screen = None  # 确保清除游戏结束画面
            elif event.type == pg.MOUSEBUTTONDOWN and game_state in [EASY, MEDIUM, HARD]:
                if not waiting_for_match:
                    if handle_click(event.pos, game_images, bottom_images):
                        # 检查是否达到7张图片
                        if sum(1 for img in bottom_images if img is not None) >= 7:
                            waiting_for_match = True
            elif game_state in [WIN, FAIL]:
                if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                    # 重置游戏
                    game_state = MENU
                    game_over_screen = None
                    game_images = []
                    bottom_images = [None] * BOTTOM_GRID_COLS
                    start_time = 0
                    remaining_time = COUNTDOWN_TIME
                    waiting_for_match = False

        if game_state == MENU:
            screen.blit(menu_image, (0, 0))
            easy_button.draw(screen,font)
            normal_button.draw(screen,font)
            hard_button.draw(screen,font)
            quit_button.draw(screen,font)
        elif game_state in [EASY, MEDIUM, HARD]:
            screen.blit(background, (0, 0))
            draw_grid(screen)

            # 更新移动中的图片
            moving_images = [img for img in bottom_images if img and img.is_moving]
            for img in moving_images:
                img.update()
                if not img.is_moving:  # 图片刚刚停止移动
                    waiting_for_match = True
            
            # 检查和移除匹配
            if waiting_for_match and not any(img.is_moving for img in bottom_images if img):
                if check_and_remove_matches(bottom_images):
                    bottom_images = rearrange_bottom_images(bottom_images)
                waiting_for_match = False

            draw_layered_images(screen, game_images)
            draw_bottom_images(screen, bottom_images)
            
            # 更新并显示倒计时
            elapsed_time = time.time() - start_time
            remaining_time = max(0, COUNTDOWN_TIME - elapsed_time)
            draw_countdown(screen, remaining_time)
            
            if check_fail_condition(game_images, bottom_images, remaining_time):
                game_state = FAIL
                game_over_screen = None
            elif check_win_condition(game_images, bottom_images, remaining_time):
                game_state = WIN
                game_over_screen = None
        elif game_state in [WIN, FAIL]:
            if game_over_screen is None:
                game_over_screen = screen.copy()
                draw_game_over_screen(game_over_screen, game_state == WIN)
            screen.blit(game_over_screen, (0, 0))

        pg.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
    pg.quit()