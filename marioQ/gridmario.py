import numpy as np
import pandas as pd

desired_width = 200
pd.set_option('display.width', desired_width)
np.set_printoptions(linewidth=desired_width)


def randPair(s, e):
    return np.random.randint(s, e), np.random.randint(s, e)


gridX = 8
gridY = 10
gridZ = 4

totalprize = 20
totalpunish = 5
totalwalls = 30
totalmonsters = 8
monsters = 0
prizes = 0
punish = 0
goalReward = 0

levelX = 8
levelY = 260
playerForward = 0
level = np.zeros((levelX, levelY, 2))
touched = 0


def extraxtState(level):
    state = np.zeros((gridX, gridY))
    for i in range(levelX - gridX, levelX):
        for j in range(playerForward, min(playerForward + gridY, levelY)):
            state[i - (levelX - gridX), j - playerForward] = level[i, j, 0]

    for i in range(levelX - gridX, levelX):
        for j in range(playerForward, min(playerForward + gridY, levelY)):
            if level[i, j, 1] != 0:
                state[i - (levelX - gridX), j - playerForward] = level[i, j, 1]
    return state


# finds an array in the "depth" dimension of the grid
def findonLevel(level, obj, type=0):
    locations = []
    for i in range(0, levelX):
        for j in range(0, levelY):
            if level[i, j][type] == obj:
                locations.append((i, j))
    return locations


def findonState(state, obj):
    locations = []
    for i in range(0, gridX):
        for j in range(0, gridY):
            if state[i, j] == obj:
                locations.append((i, j))
    return locations


def initState(level):
    global prizes, punish, playerForward
    global goalReward
    goalReward = 0
    playerForward = 0
    prizes = len(findonLevel(level, 51))
    punish = len(findonLevel(level, 71)) + len(findonLevel(level, 91))
    state = extraxtState(level)
    state[gridX - 1, 0] = 11
    return state


# Initialize player in random location, but keep wall, goal and pit stationary
def initGridPlayer():
    global prizes
    global punish
    global totalprize, totalpunish, totalwalls, playerForward, goalReward
    global level
    prizes = totalprize
    punish = totalpunish
    playerForward = 0
    goalReward = 0
    level = np.zeros((levelX, levelY, 2))

    # place wall

    # for i in range(levelY):
    #     #level[0, i, 0] = 31
    #     level[levelX - 1, i, 0] = 31

    for i in range(levelX):
        # level[i, 0, 0] = 31
        level[i, levelY - 1, 0] = 101
    lastwidth = 7
    for i in range(0, totalwalls):
        height = np.random.randint(levelX - 6, levelX - 1)
        number = np.random.randint(1, 7)
        width = np.random.randint(lastwidth, lastwidth + number)
        if width + number > levelY:
            break
        if height == levelX - 2:
            for w in range(int(number / 2)):
                level[height, width + w, 0] = 31
                if number <= 3:
                    level[height - 1, width + w, 0] = 31
        else:
            for w in range(number):
                if np.random.randint(1, 5) != 1:
                    level[height, width + w,0] = 31
        lastwidth = width + number + np.random.randint(7, 30)
    # place goal
    for i in range(0, totalprize):
        level[np.random.randint(levelX - 3, levelX - 1), np.random.randint(1, levelY - 4), 0] = 51
    # place pit
    coordY = 5
    for i in range(0, totalpunish):
        if coordY > levelY - 31:
            break
        coordY = np.random.randint(coordY, coordY + 10)
        level[levelX - 1, coordY, 0] = 71
        level[levelX - 1, coordY + 1, 0] = 71
        if level[levelX - 4, coordY,0] == 31 or level[levelX - 4, coordY + 1,0] == 31 or level[levelX - 3, coordY,0] == 31 or \
                level[levelX - 3, coordY + 1,0] == 31:
            level[levelX - 2, coordY - 1,0] = 31
            level[levelX - 3, coordY - 1,0] = 31
            if np.random.randint(0,4)==1:
                level[levelX - 2, coordY - 2,0] = 31
        if level[levelX - 4,coordY+1,0]==31:
            level[levelX - 4, coordY + 1, 0] = 0
        coordY += np.random.randint(15, 30)


    coordY = 5
    for i in range(0, totalmonsters):
        if coordY > levelY - 31:
            break
        coordY = np.random.randint(coordY, coordY + 10)
        level[levelX - 2, coordY, 1] = 91
        level[levelX - 2, np.random.randint(coordY, coordY + 2), 1] = 91
        coordY += np.random.randint(3, 7)

    # state[3, 5] = np.array([0, 1, 0, 0])

    prizes = len(findonLevel(level, 51))
    punish = len(findonLevel(level, 71)) + len(findonLevel(level, 91, 1))
    totalprize = prizes
    totalpunish = punish
    # level[levelX-1,10]=71
    # level[levelX - 2, 15] = 91

    state = extraxtState(level)
    # place player
    state[gridX - 1, 0] = 11

    return level, state


isjumping = 0
jumpforce = 0
gravity = 1
inplace = 1
money = []


def makeMove(state, action):
    # need to locate player in grid
    # need to determine what object (if any) is in the new grid spot the player is moving to
    try:
        player_loc = getLoc(state, 11)[0]
    except Exception as e:
        print(dispGrid(state))
        raise e
    walls = getLoc(state, 31)

    player_loc_initial = player_loc

    actions = [[0, 0], [0, 1], [-1, 0], [1, 0]]
    global isjumping
    global jumpforce
    global punish
    global prizes
    global goalReward
    global playerForward
    global level
    global inplace
    global money

    if isjumping:
        isjumping -= gravity
        if not isjumping:
            jumpforce = 0
        if isjumping == gravity:
            jumpforce = 1
    onwall = 0
    if player_loc[0] < gridX - 1:
        if state[player_loc[0] + 1, player_loc[1]] != 31 and action == 2:
            onwall = 0
            action = 0
        else:
            onwall = 1

    if action == 2 and (player_loc[0] == gridX - 1 or onwall):
        action = 0
        isjumping = 3 * gravity
        jumpforce = 2

    if (player_loc[0] == gridX - 1 or state[player_loc[0] + 1, player_loc[1]] == 31) and jumpforce == 0:
        # e.g. up => (player row - 1, player column + 0)
        new_loc = (player_loc[0] + actions[action][0], player_loc[1] + actions[action][1])
    else:
        new_loc = (player_loc[0] + actions[action][0] + gravity - jumpforce, player_loc[1] + actions[action][1])

    new_player_loc = player_loc_initial
    if new_loc[0] < gridX and new_loc[0] >= 0:
        new_player_loc = (new_loc[0], new_player_loc[1])
    if new_loc[1] < gridY and new_loc[1] >= 0:
        new_player_loc = (new_player_loc[0], new_loc[1])

    for wall in walls:
        if new_player_loc == wall:
            if state[player_loc_initial[0], new_player_loc[1]] != 31:
                new_player_loc = player_loc_initial[0], new_player_loc[1]
            elif state[new_player_loc[0], player_loc_initial[1]] != 31:
                new_player_loc = new_player_loc[0], player_loc_initial[1]
            else:
                new_player_loc = player_loc_initial

    difference = new_player_loc[1] - player_loc_initial[1]
    playerForward += difference

    goals = getLoc(state, 51)
    pits = getLoc(state, 71) + getLoc(state, 91)

    # re-place pit
    for pit in pits:
        if pit[1] - difference < 0:
            punish -= 1

    # re-place goal
    for goal in goals:
        if goal[1] - difference < 0:
            prizes -= 1
            goalReward += 1

    if new_player_loc == player_loc_initial:
        inplace += 1
    else:
        inplace = 1

    state = extraxtState(level)
    touched = state[(new_player_loc[0], player_loc_initial[1])]
    monsters = getLoc(state, 91)

    for monster in monsters:
        monsterStep = 1
        level[monster[0] + levelX - gridX, monster[1] + playerForward, 1] = 0
        if monster[1] - 1 < 0:
            punish -= 1
        else:
            if level[monster[0] + levelX - gridX, monster[1] + playerForward - 1, 0] == 71:
                touched = 41
                continue
            elif level[monster[0] + levelX - gridX, monster[1] + playerForward - 1, 0] == 31:
                monsterStep = 0
            level[monster[0] + levelX - gridX, (monster[1] - monsterStep + playerForward), 1] = 91
    state = extraxtState(level)
    touched = max(touched, state[(new_player_loc[0], player_loc_initial[1])])
    level[new_player_loc[0], min(player_loc_initial[1] + playerForward, levelY - 1), 0] = 0
    state[(new_player_loc[0], player_loc_initial[1])] = 11
    if new_player_loc[0] > player_loc_initial[0] and touched == 91:
        touched = 41

    reward = max(-60 * (inplace / 2), -450)
    if touched == 71 or touched == 91 or inplace > 100:
        # print("Lose",playerForward)
        punish -= 1
        reward = -500
    elif playerForward == levelY - gridY - 1:
        # print("Win",playerForward)
        reward = 500
    elif touched == 31 or touched == 41:
        if touched == 31:
            prizes -= 1
        reward = 150
    elif totalpunish > punish:
        # print(totalprize,goalReward,-1 * totalprize + goalReward)
        reward = max((-1 * totalprize + goalReward) * (inplace / 2), reward + 10)

    return state, reward


def getLoc(state, level):
    locations = []
    for i in range(0, gridX):
        for j in range(0, gridY):
            if state[i, j] == level:
                locations.append((i, j))
    return locations


def getReward(state, lastState):
    player_loc = findonState(state, 11)[0]
    player_last = findonState(lastState, 11)[0]
    pits = findonState(state, 71)
    pits_last = findonState(lastState, 71)
    goals = findonState(state, 31)
    goals_last = findonState(state, 31)
    global prizes
    global punish

    # print(totalpunish, punish,len(pits))


def dispGrid(state):
    grid = np.zeros((gridX, gridY), dtype='<U2')
    players = findonState(state, 11)
    walls = findonState(state, 31)
    goals = findonState(state, 51)
    pits = findonState(state, 71)
    monsters = findonState(state, 91)
    for i in range(0, gridX):
        for j in range(0, gridY):
            grid[i, j] = ' '

    for player_loc in players:
        grid[player_loc] = 'P'  # player
    for wall in walls:
        grid[wall] = 'W'  # wall
    for goal in goals:
        grid[goal] = '+'  # goal
    for pit in pits:
        grid[pit] = '-'  # pit
    for monster in monsters:
        grid[monster] = '*'  # monster

    return grid

# level,state=initGridPlayer()
# print("initial",dispGrid(state))
# print(" ")
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 2)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(" ")
# print(reward)
# state,reward = makeMove(state, 1)
# print(dispGrid(state))
# print(reward)
