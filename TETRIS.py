from mcpi.minecraft import Minecraft
from mcpi import block
import time
import collections
import random

# Исправление для Python 3.10+
collections.Iterable = collections.abc.Iterable

# Windows-клавиши
from ctypes import windll

ESCAPE = 27
LEFT = 37
UP = 38
RIGHT = 39
DOWN = 40

def isPressedNow(key):
    return bool(0x8000 & windll.user32.GetAsyncKeyState(int(key)))

mc = Minecraft.create()

# размеры поля
WIDTH = 10
HEIGHT = 20

# позиция в мире
base_x, base_y, base_z = mc.player.getTilePos()
base_x += 2
base_y += 10

# игровое поле
field = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT)]

# фигуры
shapes = [
    [[1,1,1,1]], [[1,1],[1,1]], [[0,1,0],[1,1,1]],
    [[1,0,0],[1,1,1]], [[0,0,1],[1,1,1]], [[0,1,1],[1,1,0]], [[1,1,0],[0,1,1]]
]

# цвета блоков
colors = [
    block.STONE.id, block.GOLD_BLOCK.id, block.IRON_BLOCK.id,
    block.EMERALD_ORE.id, block.DIAMOND_BLOCK.id, block.GLOWSTONE_BLOCK.id, block.WOOL.id
]

# Рисуем поле
def draw():
    for y in range(HEIGHT):
        for x in range(WIDTH):
            if field[y][x]:
                mc.setBlock(base_x + x, base_y - y, base_z, field[y][x])
            else:
                mc.setBlock(base_x + x, base_y - y, base_z, block.AIR.id)

def can_place(shape, px, py):
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                fx = px + x
                fy = py + y
                if fx < 0 or fx >= WIDTH or fy >= HEIGHT:
                    return False
                if fy >= 0 and field[fy][fx]:
                    return False
    return True

def place(shape, px, py, color):
    for y in range(len(shape)):
        for x in range(len(shape[y])):
            if shape[y][x]:
                field[py + y][px + x] = color

def clear_lines():
    global field
    new_field = []
    lines_cleared = 0

    # Проверка и очистка полных строк
    for row in field:
        if all(row):  # Если строка полная
            lines_cleared += 1  # Увеличиваем счетчик очищенных линий
        else:
            new_field.append(row)  # Сохраняем неполные строки

    # Добавляем пустые строки сверху
    for _ in range(lines_cleared):
        new_field.insert(0, [0] * WIDTH)

    # Обновляем поле
    field = new_field

    # Проверка и очистка полных столбцов
    for x in range(WIDTH):
        if all(field[y][x] for y in range(HEIGHT)):  # Если столбец полный
            lines_cleared += 1  # Увеличиваем счетчик очищенных линий
            for y in range(HEIGHT):
                field[y][x] = 0  # Очищаем столбец

    # Добавляем пустые столбцы слева
    for _ in range(lines_cleared):
        for y in range(HEIGHT):
            field[y].insert(0, 0)  # Добавляем пустой столбец слева
            field[y].pop()  # Удаляем последний элемент, чтобы сохранить ширину

def rotate(shape):
    return [list(row) for row in zip(*shape[::-1])]

def build_frame():
    for y in range(HEIGHT):
        for x in range(-1, WIDTH + 1):
            mc.setBlock(base_x + x, base_y - y, base_z - 1, block.OBSIDIAN.id)
        mc.setBlock(base_x - 1, base_y - y, base_z, block.OBSIDIAN.id)
        mc.setBlock(base_x + WIDTH, base_y - y, base_z, block.OBSIDIAN.id)

build_frame()

# Главный цикл
while True:
    index = random.randint(0, len(shapes) - 1)
    shape = shapes[index]
    color = colors[index]

    x = WIDTH // 2
    y = 0
    speed = 0.2  # скорость падения

    while True:
        if isPressedNow(ESCAPE):
            mc.postToChat("Игра остановлена.")
            exit()

        # управление стрелками
        if isPressedNow(LEFT) and can_place(shape, x - 1, y):
            x -= 1
        if isPressedNow(RIGHT) and can_place(shape, x + 1, y):
            x += 1
        if isPressedNow(DOWN) and can_place(shape, x, y + 1):
            y += 1
        if isPressedNow(UP):
            rotated = rotate(shape)
            if can_place(rotated, x, y):
                shape = rotated

        # падение фигуры
        if can_place(shape, x, y + 1):
            y += 1
        else:
            place(shape, x, y, color)
            clear_lines()  # Удаляем полные линии
            break

        draw()
        for dy in range(len(shape)):
            for dx in range(len(shape[dy])):
                if shape[dy][dx]:
                    mc.setBlock(base_x + x + dx, base_y - (y + dy), base_z, color)

        time.sleep(speed)