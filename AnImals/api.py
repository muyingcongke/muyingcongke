import random
import pygame as pg
import os


# 游戏常量
SCREEN_WIDTH = 1120
SCREEN_HEIGHT = 800

GRID_SIZE = 80
GRID_COLS = 10
GRID_ROWS = 7
GRID_START_X = 80
GRID_START_Y = 80

# 图片种类数
SORTS = 7


STACK_X = 880
STACK_Y = 80

# 新增底部区域常量
BOTTOM_GRID_START_X = GRID_START_X + 2*GRID_SIZE
BOTTOM_GRID_START_Y = 680
BOTTOM_GRID_COLS = 7
BOTTOM_GRID_ROWS = 1
RIGHT_X = 0
RIGHT_Y = 0

# 颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

MAX_LAYER = 5

# 游戏状态
MENU = 0
WIN = 1
FAIL = 2
EASY = 3
MEDIUM = 4
HARD = 5

# 修改常量
BOTTOM_LEFT_X = BOTTOM_GRID_START_X
BOTTOM_LEFT_Y = BOTTOM_GRID_START_Y

# 添加子网格的常量
SUB_GRID_SIZE = GRID_SIZE // 2

# 在全局常量中添加
COUNTDOWN_TIME = 180  # 3分钟倒计时

# 设置颜色
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

def aspect_ratio_scale(image, target_width):
    """保持纵横比缩放图片"""
    width, height = image.get_size()
    aspect_ratio = height / width
    new_height = int(target_width * aspect_ratio)
    return pg.transform.scale(image, (target_width, new_height))


def load_images():
    images = []
    for i in range(1, SORTS + 1):
        img = pg.image.load(f"./pictures/{i}.png")
        img = pg.transform.scale(img, (GRID_SIZE, GRID_SIZE))
        images.append((img, i))
    return images


# 加载背景图片
menu_image = pg.image.load(os.path.join("pictures", "menu.png"))
menu_image = pg.transform.scale(menu_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
background = pg.image.load(os.path.join("pictures", "backround.png"))
background = pg.transform.scale(background, (SCREEN_WIDTH, SCREEN_HEIGHT))

# 加载胜利和失败图片
win_image = pg.image.load(os.path.join("pictures", "win.png"))
fail_image = pg.image.load(os.path.join("pictures", "fail.png"))

images = load_images()

target_width = SCREEN_WIDTH // 2
win_image = aspect_ratio_scale(win_image, target_width)
fail_image = aspect_ratio_scale(fail_image, target_width)


class Image:
    def __init__(self, x, y, image, image_id, layer):
        self.image = image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.image_id = image_id
        self.layer = layer
        self.is_covered = False
        self.shadow = pg.Surface(self.rect.size, pg.SRCALPHA)
        self.shadow.fill((0, 0, 0, 128))  # 半透明的黑色阴影

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        if self.is_covered:
            screen.blit(self.shadow, self.rect)

    def update(self):
        if self.is_moving:
            dx = (self.target_x - self.rect.x) / 5
            dy = (self.target_y - self.rect.y) / 5
            self.rect.x += dx
            self.rect.y += dy
            if abs(self.rect.x - self.target_x) < 3 and abs(self.rect.y - self.target_y) < 3:
                self.rect.x = self.target_x
                self.rect.y = self.target_y
                self.is_moving = False
                self.in_bottom_row = True
                return True
        return False

# 创建按钮类
class Button:
    def __init__(self, x, y, width, height, text, color):
        self.rect = pg.Rect(x, y, width, height)
        self.text = text
        self.color = color

    def draw(self, screen,font):
        pg.draw.rect(screen, self.color, self.rect)
        text_surface = font.render(self.text, True, BLACK)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

def check_win_condition(game_images, bottom_images, remaining_time):
    # 检查是否所有图片都被消除
    all_images_cleared = len(game_images) == 0 and all(img is None for img in bottom_images)
    
    # 确保还有剩余时间
    time_remaining = remaining_time > 0
    
    return all_images_cleared and time_remaining

def check_fail_condition(game_images, bottom_images, remaining_time):
    # 检查时间是否用完
    if remaining_time <= 0:
        # 检查是否还有未消除的图片
        return len(game_images) > 0 or any(img is not None for img in bottom_images)
    
    # 检查是否有7张图片且都已到达底部
    if sum(1 for img in bottom_images if img is not None and not img.is_moving) == 7:
        # 检查是否有可以消除的匹配
        return not check(bottom_images)
    
    return False



def draw_layered_images(screen, game_images):
    # 按层次排序图片
    sorted_images = sorted(game_images, key=lambda img: img.layer)
    
    # 重置所有图片的遮挡状态
    for img in sorted_images:
        img.is_covered = False
    
    # 按层次绘制图片并检查遮挡
    for i, img in enumerate(sorted_images):
        if img.layer == 0:
            continue  # 跳过第0层的图片
        
        # 检查是否有比当前图片高一层的图片遮住它
        for other_img in sorted_images[i+1:]:
            if other_img.layer == img.layer + 1 and img.rect.colliderect(other_img.rect):
                img.is_covered = True
                break  # 找到一个遮挡就足够了，不需要继续检查
        
        # 绘制当前图片
        draw_3d_image(screen,img)

def draw_3d_image(screen, img):
    # 创建一个比原图稍大的表面来容纳立体效果
    surface = pg.Surface((img.rect.width + 6, img.rect.height + 6), pg.SRCALPHA)
    
    # 绘制底部和右侧的深色边框（模拟阴影）
    pg.draw.rect(surface, (100, 100, 100), (3, 3, img.rect.width + 3, img.rect.height + 3))
    
    # 绘制顶部和左侧的亮色边框（模拟高光）
    pg.draw.rect(surface, (200, 200, 200), (0, 0, img.rect.width + 3, img.rect.height + 3))
    
    # 绘制原始图像
    surface.blit(img.image, (3, 3))
    
    # 如果图片被遮挡，添加阴影效果
    if img.is_covered:
        shadow = pg.Surface((img.rect.width + 6, img.rect.height + 6), pg.SRCALPHA)
        shadow.fill((0, 0, 0, 128))  # 半透明的黑色阴影
        surface.blit(shadow, (0, 0))
    
    # 将带有立体效果的表面绘制到屏幕上
    screen.blit(surface, (img.rect.x - 3, img.rect.y - 3))

def draw_grid(screen):
    # 绘制底部网格
    for i in range(BOTTOM_GRID_ROWS + 1):
        pg.draw.line(screen, (200, 200, 200), 
                     (BOTTOM_GRID_START_X, BOTTOM_GRID_START_Y + i * GRID_SIZE),
                     (BOTTOM_GRID_START_X + BOTTOM_GRID_COLS * GRID_SIZE, BOTTOM_GRID_START_Y + i * GRID_SIZE))
    for j in range(BOTTOM_GRID_COLS + 1):
        pg.draw.line(screen, (200, 200, 200), 
                     (BOTTOM_GRID_START_X + j * GRID_SIZE, BOTTOM_GRID_START_Y),
                     (BOTTOM_GRID_START_X + j * GRID_SIZE, BOTTOM_GRID_START_Y + BOTTOM_GRID_ROWS * GRID_SIZE))

def draw_bottom_images(screen, bottom_images):
    for img in bottom_images:
        if img:
            draw_3d_image(screen, img)

def check_and_remove_matches(bottom_images):
    image_counts = {}
    for img in bottom_images:
        if img and not img.is_moving:
            if img.image_id in image_counts:
                image_counts[img.image_id].append(img)
            else:
                image_counts[img.image_id] = [img]
    
    removed = False
    for image_id, images in image_counts.items():
        if len(images) >= 3:
            for img in images[:3]:  # 只移除前三个匹配的图片
                bottom_images[bottom_images.index(img)] = None
            removed = True
    
    return removed

def check(bottom_images):
    image_counts = {}
    for img in bottom_images:
        if img:
            if img.image_id in image_counts:
                image_counts[img.image_id].append(img)
            else:
                image_counts[img.image_id] = [img]
    
    removed = False
    for image_id, images in image_counts.items():
        if len(images) >= 3:
            removed = True 
    return removed

def rearrange_bottom_images(bottom_images):
    new_bottom_images = [img for img in bottom_images if img is not None]
    new_bottom_images.extend([None] * (len(bottom_images) - len(new_bottom_images)))
    
    for i, img in enumerate(new_bottom_images):
        if img:
            img.target_x = BOTTOM_GRID_START_X + i * GRID_SIZE
            img.target_y = BOTTOM_GRID_START_Y
            img.is_moving = True
    
    return new_bottom_images

def is_overlapped(img1, img2):
    return img1.rect.colliderect(img2.rect) and img2.layer > img1.layer

def parse_coordinate(char):
    if char.isdigit():
        return int(char)
    elif char.isalpha():
        return ord(char) - ord('A') + 10
    else:
        raise ValueError(f"Invalid character: {char}")

def read_and_parse_coordinates(file_path):
    with open(file_path, 'r') as file:
        content = file.read().strip()
    
    # 移除所有的逗号（包括中文和英文逗号）
    content = content.replace(',', '').replace('，', '')
    
    layers = content.split('\n')
    parsed_layers = []

    for layer in layers:
        coordinates = []
        for i in range(0, len(layer), 2):
            if i + 1 < len(layer):
                x = parse_coordinate(layer[i])
                y = parse_coordinate(layer[i+1])
                coordinates.append((x, y))
        if coordinates:  # 只添加非空的层
            parsed_layers.append(coordinates)
    
    return parsed_layers

def create_game_images(images, game_state):
    # 地图
    full_map = read_and_parse_coordinates('map.txt')

    total_layers = 0
    image_sorts = 0
    if game_state == EASY:
        total_layers = 3
        image_sorts = 4
    elif game_state == MEDIUM:
        total_layers = 4
        image_sorts = 5
    elif game_state == HARD:
        total_layers = 5
        image_sorts = 7
    
    current_map = full_map[MAX_LAYER - total_layers:]
    
    # 创建图片列表，确保每种图片的数量是3的倍数
    game_images = []
    image_counts = {i: 0 for i in range(1, image_sorts + 1)}
    
    # 为每个坐标创建Image对象
    for layer_index, layer in enumerate(current_map):
        for x, y in layer:
            image, image_id = random.choice(images[:image_sorts])
            new_img = Image(GRID_START_X + x * SUB_GRID_SIZE, 
                            GRID_START_Y + y * SUB_GRID_SIZE, 
                            image, image_id, layer_index + 1)
            game_images.append(new_img)
            image_counts[image_id] += 1
    
    # 确保每种图片的数量是3的倍数，并直接处理0层图片
    zero_layer_begin = len(game_images)
    zero_layer_count = 0
    for image_id in image_counts:
        while image_counts[image_id] % 3 != 0:
            image, _ = next((img for img in images if img[1] == image_id))
            new_img = Image(0, 0, image, image_id, 0)
            game_images.append(new_img)
            image_counts[image_id] += 1
            zero_layer_count += 1
            if image_counts[image_id] % 3 == 0:
                for _ in range(3):
                    new_img = Image(0, 0, image, image_id, 0)
                    game_images.append(new_img)
                    image_counts[image_id] += 1
                    zero_layer_count += 1
    zero_layer = game_images[zero_layer_begin:]
    random.shuffle(zero_layer)
    game_images[zero_layer_begin:] = zero_layer
    for i, img in enumerate(zero_layer):
        if i == 0:
            img.rect.x = RIGHT_X
            img.rect.y = RIGHT_Y
            img.layer = 1
        else:
            img.rect.x = RIGHT_X
            img.rect.y = RIGHT_Y + i * SUB_GRID_SIZE // 2
            img.layer = i + 1
    # game_images = sorted(game_images, key=lambda img: img.layer, reverse=True)
    return game_images

def handle_click(pos, game_images, bottom_images):
    # 计算底部非空图片的数量
    bottom_count = sum(1 for img in bottom_images if img is not None)
    
    # 如果底部已经有7张图片，不允许继续点击
    if bottom_count >= 7:
        return False

    for img in reversed(game_images):  # 从上层到下层检查
        if img.rect.collidepoint(pos) and not img.is_covered:
            # 找到第一个空位
            empty_slot = next((i for i, b_img in enumerate(bottom_images) if b_img is None), -1)
            
            # 移动图片到底部
            img.target_x = BOTTOM_LEFT_X + empty_slot * GRID_SIZE
            img.target_y = BOTTOM_LEFT_Y
            img.is_moving = True
            game_images.remove(img)
            bottom_images[empty_slot] = img
            return True
    return False

# 在 load_images 函数后添加
def load_game_over_image():

    game_over_path = os.path.join("pictures", "game_over.jpg")
    game_over_image = pg.image.load(game_over_path).convert_alpha()
    game_over_image = pg.transform.scale(game_over_image, (400, 200))  # 调整大小为适当的尺寸
    game_over_rect = game_over_image.get_rect()
    game_over_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    return game_over_image, game_over_rect


