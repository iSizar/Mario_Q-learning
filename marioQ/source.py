#! /usr/bin/python

import pygame
from pygame import *
import gridmario as gm
import numpy as np
WIN_WIDTH = 800
WIN_HEIGHT = 275
HALF_WIDTH = int(WIN_WIDTH / 2)
HALF_HEIGHT = int(WIN_HEIGHT / 2)

DISPLAY = (WIN_WIDTH, WIN_HEIGHT)
DEPTH = 32
FLAGS = 0
CAMERA_SLACK = 30

ACTION = "KEYUP"
new_action = False
# state
timer = 1
screen = 2
camera = 3
player = 4
platforms = 5
bg = 6
entities = 7
enemygroup = 8
GAME = 0
playerForward=0

speed=4
inplace=0

spritesheet = pygame.image.load("media/graphics/mario_bros.png")

character = Surface((13, 15), pygame.SRCALPHA)
character.blit(spritesheet, (-177, -33))
character = pygame.transform.scale(character, (32, 32))
mariostand1 = character

character = Surface((14, 15), pygame.SRCALPHA)
character.blit(spritesheet, (-80, -33))
character = pygame.transform.scale(character, (32, 32))
mariowalk1 = character

character = Surface((14, 15), pygame.SRCALPHA)
character.blit(spritesheet, (-98, -33))
character = pygame.transform.scale(character, (32, 32))
mariowalk2 = character

character = Surface((14, 15), pygame.SRCALPHA)
character.blit(spritesheet, (-113, -33))
character = pygame.transform.scale(character, (32, 32))
mariowalk3 = character

character = Surface((14, 15), pygame.SRCALPHA)
character.blit(spritesheet, (-145, -33))
character = pygame.transform.scale(character, (32, 32))
mariojump1 = character

spritesheet = pygame.image.load("media/graphics/smb_enemies_sheet.png")
character = Surface((16, 17), pygame.SRCALPHA)
character.blit(spritesheet, (0, -3))
character = pygame.transform.scale(character, (32, 32))
goombawalk1 = character

character = Surface((16, 17), pygame.SRCALPHA)
character.blit(spritesheet, (-30, -3))
character = pygame.transform.scale(character, (32, 32))
goombawalk2 = character

character = Surface((16, 17), pygame.SRCALPHA)
character.blit(spritesheet, (-60, -3))
character = pygame.transform.scale(character, (32, 32))
goombaflat1 = character

spritesheet = pygame.image.load("media/graphics/item_objects.png")
character = Surface((10, 14), pygame.SRCALPHA)
character.blit(spritesheet, (-147, -98))
character = pygame.transform.scale(character, (32, 32))
goldcoin = character

def actionListen(action):
    global ACTION, new_action
    ACTION = action
    new_action = True
    state,reward = makeTheMouve()
    return state,reward

def init_game(level):
    global cameraX, cameraY, GAME
    global timer, screen, camera, player, platforms, bg, entities, enemygroup,inplace
    pygame.init()
    inplace = 0
    GAME += 1
    screen = pygame.display.set_mode(DISPLAY, FLAGS, DEPTH)
    pygame.display.set_caption(str("Mario"))
    timer = pygame.time.Clock()

    up = down = left = right = running = False
    bg = Surface((WIN_WIDTH, WIN_HEIGHT)).convert()
    bg.convert()
    bg.fill(Color("#00455b"))
    entities = pygame.sprite.Group()
    enemygroup = pygame.sprite.Group()
    player = Player(32, 32*(gm.gridX-2))
    platforms = []

    x = y = 0
    # build the level

    for row in level:
        for col in row:
            if 31 in col:
                p = Platform(x, y)
                platforms.append(p)
                entities.add(p)
            if 51 in col:
                e = CoinBlock(x, y)
                platforms.append(e)
                entities.add(e)
            if 71 in col:
                e = PitBlock(x, y-1)
                platforms.append(e)
                entities.add(e)
            if 101 in col:
                e = EndBlock(x, y)
                platforms.append(e)
                entities.add(e)
            if 91 in col:
                enemygroup.add(Goomba(x, y))
            x += 32
        y += 32
        x = 0
    f = Floor(0,32*(gm.levelX-1))
    platforms.append(f)
    entities.add(f)
    # f = Floor(32*7, 32 * (gm.gridX-1))
    # platforms.append(f)
    # entities.add(f)
    # f = Floor(32 * 8, 32 * (gm.gridX-1))
    # platforms.append(f)
    # entities.add(f)
    total_level_width = len(level[0]) * 32
    total_level_height = len(level) * 32
    camera = Camera(complex_camera, total_level_width, total_level_height)
    entities.add(player)


def makeTheMouve():
    global timer, screen, camera, player, platforms, bg, entities, GAME
    global new_action,playerForward,inplace
    timer.tick(60)
    up = False
    down = False
    right = False
    left = False
    running = False
    reward = -4
    if ACTION == "QUIT": raise SystemExit("QUIT")
    if ACTION == "K_UP":
        up = True
    if ACTION == "K_DOWN":
        down = True
    if ACTION == "K_LEFT":
        left = True
    if ACTION == "K_RIGHT":
        right = True
    if ACTION == "K_SPACE":
        running = True
    new_action = False

    pygame.event.get()
    camera.update(player)
    intialpos=player.getCoord()
    if not up:
        for i in range(speed):
            # draw background
            screen.blit(bg, (0, 0))
        # update player, draw everything else
            posible_reward=player.update(up, down, left, right, running, platforms, enemygroup)
            if (posible_reward==-5 or posible_reward>reward) and reward!=-5:
                reward = posible_reward
            for e in entities:
                if isinstance(e, Floor):
                    screen.blit(e.image, camera.apply(e))
            for e in entities:
                if not isinstance(e, Floor):
                    screen.blit(e.image, camera.apply(e))
            for e in enemygroup:
                screen.blit(e.image, camera.apply(e))
                e.update(platforms, entities, player.getCoord())
            pygame.display.update()
    else:
        for i in range(speed):
        # draw background
            screen.blit(bg, (0, 0))
            posible_reward = player.update(up, down, left, right, running, platforms, enemygroup)
            if (posible_reward==-5 or posible_reward>reward) and reward!=-5:
                reward = posible_reward

            for e in entities:
                if isinstance(e, Floor):
                    screen.blit(e.image, camera.apply(e))
            for e in entities:
                if not isinstance(e, Floor):
                    screen.blit(e.image, camera.apply(e))
            #screen.blit(f.image, camera.apply(f))
            for e in enemygroup:
                screen.blit(e.image, camera.apply(e))
                e.update(platforms, entities, player.getCoord())
            pygame.display.update()
    x, y = player.getCoord()
    playerForward = x
    #print(x,y)
    state = np.zeros((gm.gridX, gm.gridY))
    for e in entities:
        x_e, y_e = e.getCoord()

        if 0 <= x_e - x < gm.gridY and -1 <= y_e - y < gm.gridX:

            if isinstance(e, CoinBlock):
                if not e.destroyed:
                    if state[y_e, x_e - playerForward] == 0:
                        state[y_e, x_e - playerForward] = 51
            elif isinstance(e, Platform):
                if state[y_e, x_e - playerForward] == 0:
                    state[y_e, x_e - playerForward] = 31
            elif isinstance(e, PitBlock):
                state[y_e, x_e - playerForward] = 71

    for e in enemygroup:
        if not e.destroyed:
            x_e, y_e = e.getCoord()
            if 0 <= x_e - x < gm.gridY and -1 <= y_e - y < gm.gridX:
                state[y_e, x_e - playerForward] = 91
    if(y<gm.gridX):
        state[y, 0] = 11
    # except:
    #     new_action = True
    #     makeTheMouve()

    if (x,y)==intialpos and reward != 5 and reward != -5:
        inplace+=1
        reward -= 0.6

    if inplace > 50:
        reward = -5

    #print(state, reward)
    return state, reward

class Camera(object):
    def __init__(self, camera_func, width, height):
        self.camera_func = camera_func
        self.state = Rect(0, 0, width, height)

    def apply(self, target):
        return target.rect.move(self.state.topleft)

    def update(self, target):
        self.state = self.camera_func(self.state, target.rect)
def simple_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    return Rect(-l + HALF_WIDTH, -t + HALF_HEIGHT, w, h)
def complex_camera(camera, target_rect):
    l, t, _, _ = target_rect
    _, _, w, h = camera
    l, t, _, _ = -l + HALF_WIDTH, -t + HALF_HEIGHT, w, h

    l = min(0, l)  # stop scrolling at the left edge
    l = max(-(camera.width - WIN_WIDTH), l)  # stop scrolling at the right edge
    t = max(-(camera.height - WIN_HEIGHT), t)  # stop scrolling at the bottom
    t = min(0, t)  # stop scrolling at the top
    return Rect(l, t, w, h)
class Entity(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
class Player(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.x = x
        self.y = y
        self.xvel = 0
        self.yvel = 0
        self.faceright = True
        self.onGround = False
        self.airborne = True
        self.counter = 0
        self.image = mariostand1
        self.rect = Rect(x, y, 32, 32)

    def update(self, up, down, left, right, running, platforms, enemygroup):
        reward = 0
        if up:
            # only jump if on the ground
            if self.onGround: self.yvel -= 8
            reward = 0.5
        if down:
            pass
        if running:
            self.xvel = 8
            reward = 0.5
        if left:
            self.xvel = -8
            reward = -1
            self.faceright = False
        if right:
            self.xvel = 8
            reward = +1
            self.faceright = True
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.55
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        if not (left or right):
            self.xvel = 0
        if self.yvel < 0 or self.yvel > 1.2: self.airborne = True
        # increment in x direction
        self.rect.left += self.xvel
        # do x-axis collisions

        reward = self.collide(self.xvel, 0, platforms, enemygroup, reward)
        # increment in y direction
        self.rect.top += self.yvel
        # assuming we're in the air
        self.onGround = False
        # do y-axis collisions
        if reward != -5:
            reward = self.collide(0, self.yvel, platforms, enemygroup,reward)
        self.animate()
        #print(reward)
        return reward

    def getCoord(self):
        return int(self.rect.left/32), int(self.rect.top/32)

    def collide(self, xvel, yvel, platforms, enemygroup, reward):
        i = 0

        for p in platforms:
            i += 1
            if pygame.sprite.collide_rect(self, p):
                if isinstance(p, EndBlock):
                    print("JOC TERMINAT!")
                    reward = 5
                    pygame.event.post(pygame.event.Event(QUIT))
                elif isinstance(p, CoinBlock):
                    if pygame.sprite.collide_rect(self, p) and not p.destroyed:
                        p.remove()
                        reward = 2
                    if not p.destroyed:
                        if xvel > 0:
                            self.rect.right = p.rect.left
                            #print("collide right")
                        if xvel < 0:
                            self.rect.left = p.rect.right
                            #print("collide left")
                elif isinstance(p, PitBlock) and abs(self.rect.right -p.rect.left) < 50 :
                    reward = -5
                    pygame.event.post(pygame.event.Event(QUIT))
                    pygame.event.clear()
                else:
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        #print("collide right")
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        #print("collide left")
                    if yvel > 1:
                        #print("onground")
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.airborne = False
                        self.yvel = 0
                    if yvel < 0:
                        #print("offground")
                        self.rect.top = p.rect.bottom
        for e in enemygroup:
            p.update()
            if pygame.sprite.collide_rect(self, e) and not e.destroyed:
                dif = self.rect.bottom - e.rect.top
                if dif <=8:
                    #print("Here I kill")
                    self.yvel = - 5
                    reward=2
                    e.destroyed = True
                    e.counter = 0
                    e.xvel = 0
                else:
                    #print("Here I die")
                    reward = -5
                    e.counter = 0
                    e.xvel = 0
                    self.xvel=0
                    self.yvel=0
                    pygame.event.post(pygame.event.Event(QUIT))
                    pygame.event.clear()
        return reward
    def animate(self):

        if self.xvel > 0 or self.xvel < 0:
            self.walkloop()
            if self.airborne: self.updatecharacter(mariojump1)
        else:
            self.updatecharacter(mariostand1)
            if self.airborne: self.updatecharacter(mariojump1)

    def walkloop(self):
        if self.counter == 5:
            self.updatecharacter(mariowalk3)
        elif self.counter == 10:
            self.updatecharacter(mariowalk2)
        elif self.counter == 15:
            self.updatecharacter(mariowalk1)
            self.counter = 0
        self.counter = self.counter + 1

    def updatecharacter(self, ansurf):
        if not self.faceright: ansurf = pygame.transform.flip(ansurf, True, False)
        self.image = ansurf
class Platform(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load("media/graphics/terrain.jpg").convert()
        self.image = pygame.transform.scale(self.image, (16 * 2, 16 * 2))
        self.rect = Rect(x, y, 16 * 2, 16 * 2)

    def getCoord(self):
        return int(self.rect.left / 32), int(self.rect.top / 32)

    def update(self):
        pass
class CoinBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image = goldcoin
        self.destroyed = False

    def remove(self):
        self.destroyed = True
        self.image = goombaflat1
        self.kill()
    def getCoord(self):
        return int(self.rect.left/32), int(self.rect.top/32)
class Floor(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.image = pygame.image.load("media/graphics/level_1.png").convert()
        self.image = pygame.transform.scale(self.image, (32 * gm.levelY, 16 * 2*2))
        self.rect = Rect(x, y, 32 * gm.levelY, 16 * 2*2)
    def getCoord(self):
        return int(self.rect.left / 32), int(self.rect.top / 32)


    def update(self):
        pass
class EndBlock(Platform):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(Color("#000000"))

    def getCoord(self):
        return int(self.rect.left/32), int(self.rect.top/32)
class PitBlock(Entity):
    def __init__(self, x, y):
        Platform.__init__(self, x, y)
        self.image.fill(Color("#960000"))
    def getCoord(self):
        return int(self.rect.left/32), int(self.rect.top/32)
class Goomba(Entity):
    def __init__(self, x, y):
        Entity.__init__(self)
        self.xvel = -4
        self.walking = False
        self.yvel = 0
        self.onGround = False
        self.destroyed = False
        self.counter = 0
        self.image = goombawalk1
        self.rect = Rect(x, y, 32, 32)

    def getCoord(self):
        return int(self.rect.left/32), int(self.rect.top/32)

    def update(self, platforms, entities, playerCoord):
        if not self.onGround:
            # only accelerate with gravity if in the air
            self.yvel += 0.5
            # max falling speed
            if self.yvel > 100: self.yvel = 100
        if abs(playerCoord[0] - int(self.rect.left / 32)) > 8:
            self.xvel = 0
        else:
            self.walking = True
            self.xvel = -4
            # increment in x direction
            self.rect.left += self.xvel
            # do x-axis collisions
            self.collide(self.xvel, 0, platforms, entities)

            # assuming we're in the air
            self.onGround = False;
            # do y-axis collisions
            self.collide(0, self.yvel, platforms, entities)

        self.animate()

    def collide(self, xvel, yvel, platforms, entities):
        for p in platforms:
            if pygame.sprite.collide_rect(self, p) and not self.destroyed:
                if isinstance(p, PitBlock):
                    self.destroyed = True
                    self.counter = 0
                    self.rect = p.rect
                    self.xvel = 0
                    self.yvel = 0
                    self.kill()
                elif not isinstance(p, CoinBlock):
                    if xvel > 0:
                        self.rect.right = p.rect.left
                        self.xvel = -abs(xvel)
                        # print("collide right")
                    if xvel < 0:
                        self.rect.left = p.rect.right
                        self.xvel = abs(xvel)
                        # print("collide left")
                    if yvel > 0:
                        self.rect.bottom = p.rect.top
                        self.onGround = True
                        self.yvel = 0
                    if yvel < 0:
                        self.rect.top = p.rect.bottom
        for p in entities:
            if pygame.sprite.collide_rect(self, p) and not self.destroyed:
                dif = p.rect.bottom - self.rect.top
                #print(p.getCoord(),self.getCoord(),dif,p.rect.bottom,self.rect.top)
                if dif <= 8:
                   # print("Here he die")
                    self.destroyed = True
                    self.counter = 0
                    self.xvel = 0
                else:
                    #print("quit")
                    pygame.event.post(pygame.event.Event(QUIT))
                    pygame.event.clear()

    def animate(self):
        if not self.destroyed:
            if self.walking:
                self.walkloop()
        else:
            self.destroyloop()

    def walkloop(self):
        if self.counter == 10:
            self.updatecharacter(goombawalk1)
        elif self.counter == 20:
            self.updatecharacter(goombawalk2)
            self.counter = 0
        self.counter = self.counter + 1

    def destroyloop(self):
        if self.counter == 0:
            self.updatecharacter(goombaflat1)
        elif self.counter == 10:
            self.kill()
        self.counter = self.counter + 1

    def updatecharacter(self, ansurf):
        self.image = ansurf

def init():
    global timer, screen, camera, player, platforms, bg, entities, enemygroup, GAME
    level, state = gm.initGridPlayer()
    init_game(level)
    return level, state
# reward=0
# level,state = init()
# for j in range(10):
#     while reward>-5:
#         new_state, reward = actionListen("K_RIGHT")
#         print(new_state,reward)
#     init_game(level)
#     reward=0
# new_state, reward = actionListen("K_RIGHT")
# print(new_state,reward)
# new_state, reward = actionListen("K_RIGHT")
# print(new_state,reward)
# new_state, reward = actionListen("K_RIGHT")
# print(new_state,reward)
# new_state, reward = actionListen("K_UP")
# print(new_state,reward)
# # new_state, reward = actionListen("K_UP")
# # print(new_state,reward)
# #
# # new_state, reward = actionListen("K_SPACE")
# # print(new_state,reward)
# # new_state, reward = actionListen("K_SPACE")
# # print(new_state,reward)
# new_state, reward = actionListen("K_RIGHT")
# print(new_state,reward)
# new_state, reward = actionListen("K_RIGHT")
# print(new_state,reward)
#
#
#
# for i in range(40):
#     new_state, reward = actionListen("K_SPACE")
#     new_state, reward = actionListen("K_UP")
#     print(new_state,reward)