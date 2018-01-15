import gridmario as gm
import source as s
from keras.models import Sequential
from keras.layers.core import Dense, Dropout, Activation
from keras.optimizers import RMSprop
from keras.models import load_model
from collections import deque
from IPython.display import clear_output
import random
import numpy as np
import tensorflow as tf

config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
from keras import backend as K

K.set_session(sess)

inputGrid = gm.gridX * gm.gridY
inputN = 256
hiddenN = 150
outputN = 3
nr_states = 4
input_states = []

model = Sequential()
model.add(Dense(inputN, kernel_initializer='lecun_uniform', input_shape=(nr_states * inputGrid,)))
model.add(Activation('relu'))
#model.add(Dropout(0.2))  # I'm not using dropout, but maybe you wanna give it a try?

model.add(Dense(hiddenN, kernel_initializer='lecun_uniform'))
model.add(Activation('relu'))
#model.add(Dropout(0.2))

model.add(Dense(outputN, kernel_initializer='lecun_uniform'))
model.add(Activation('linear'))  # linear output so we can have range of real-valued outputs

rms = RMSprop()
model.compile(loss='mse', optimizer=rms)

f = open("log.txt", 'w')

def train2():
    model.compile(loss='mse', optimizer=rms)  # reset weights of neural network
    epochs = 100000
    observetime = 1000
    gamma = 0.9
    epsilon =  0.2
    epsilon_final = 0.0001
    epsilon_initial = 1
    explore = 10000
    batchSize = 64
    buffer = 100000
    replay = deque()
    # stores tuples of (S, A, R, S')
    h = 0
    good = 0
    bad = 0
    passed = 0
    progress = 0
    level, initialState = s.init()

    # input_states=np.zeros((nr_states,gm.gridX,gm.gridY))
    # input_states[0]=initialState
    input_states = np.stack((initialState, initialState, initialState, initialState), axis=0)
    i = -1
    jump = 0
    stay = 0
    forward = 0
    while i < epochs:
        i += 1
        printed = False

        # if i%100==0:
        # state = gm.initGridRand()  # using the harder state initialization function
        # else:

        if i % 200 == 0:
            level, initialState = s.init()
            input_states = np.stack((initialState, initialState, initialState, initialState), axis=0)
        state, reward = s.actionListen("K_SPACE")
        status = 1
        # while game still in progress
        steps = 0
        lossmean = 0
        dead = 0
        lastReward = deque()

        while (status == 1):
            # We are in state S
            # Let's run our Q function on S to get Q values for all possible actions

            steps += 1
            randnr=random.random()
            if (randnr < epsilon):  # choose random action
                action = np.random.randint(0, outputN)

            else:  # choose best action from Q(s,a) values
                qval = model.predict(input_states.reshape(1, inputGrid * nr_states), batch_size=1)
                action = (np.argmax(qval))
                if action == 2:
                    jump += 1
                elif action == 1:
                    forward += 1
                else:
                    stay += 1
            # Take action, observe new state S'

            if action == 2:
                action1 = "K_UP"
            elif action == 1:
                action1 = "K_RIGHT"
            else:
                action1 = "K_SPACE"
            new_state, reward = s.actionListen(action1)
            new_input_states = np.stack((new_state, input_states[1], input_states[2], input_states[3]), axis=0)

            # Observe reward
            # reward = gm.getReward(new_state,state)

            if i % 1000 == 0 and len(replay) >= observetime:
               # print(gm.dispGrid(state))
                #print(action)
                model.save("model.h5")
                model.save_weights('my_model_weights.h5')
                model_json = model.to_json()
                with open("model.json", "w") as json_file:
                    json_file.write(model_json)

                # f.write(gm.dispGrid(state)+"\n")
                # f.write(action+"\n")

            # Experience replay storage
            if len(replay) < observetime:  # if buffer not filled, add to it
                replay.append((input_states, action, reward, new_input_states))
                i = 0
            else:  # if buffer full, overwrite old values
                if len(replay) > buffer:
                    replay.popleft()
                replay.append((input_states, action, reward, new_input_states))
                # randomly sample our experience replay memory
                minibatch = random.sample(replay, batchSize)
                X_train = []
                y_train = []

                for memory in minibatch:
                    # Get max_Q(S',a)
                    old_state, action_m, reward_m, new_state_m = memory
                    old_qval = model.predict(old_state.reshape(1, inputGrid * nr_states), batch_size = 1)
                    newQ = model.predict(new_state_m.reshape(1, inputGrid * nr_states), batch_size = 1)
                    maxQ = np.max(newQ)

                    y = np.zeros((1, outputN))
                    y[:] = old_qval[:]
                    if abs(reward_m) <= 5:  # non-terminal state
                        update = (reward_m + (gamma * maxQ))
                    else:  # terminal state
                        update = reward_m
                    y[0][action_m] = update
                    X_train.append(old_state.reshape(nr_states * inputGrid, ))
                    y_train.append(y.reshape(outputN, ))

                X_train = np.array(X_train)
                y_train = np.array(y_train)

                # loss=model.train_on_batch(X_train,y_train)
                model.fit(X_train, y_train, batch_size=batchSize, epochs=1, verbose=0)
                # lossmean+=loss
                if i % 10 == 0 and not printed and len(replay) >= observetime:
                    print("Game #: %s %s/%s/%s with %s at %s %s actions: %s %s %s " % (
                    i, good, bad, passed/10, progress / 10, epsilon,randnr, stay, forward, jump))
                    f.write("Game #: %s %s/%s/%s with %s at %s actions %s %s %s \n" % (
                    i, good, bad, passed/10, progress / 10, epsilon, stay, forward, jump))
                    f.flush()
                    good = 0
                    bad = 0
                    passed = 0
                    progress = 0
                    stay, forward, jump = 0, 0, 0
                    printed = True
                state = new_state
                input_states = new_input_states
                if (len(lastReward) > 15):
                    lastReward.popleft()
                lastReward.append(reward)
            if abs(reward) >= 5:  # if reached terminal state, update game status
                status = 0
                if not dead:
                    progress += s.playerForward
                #print(lastReward)
                if reward >= 5:
                    if not dead:
                        good += 1
                        s.init_game(level)
                else:
                    s.init_game(level)
                    dead = 1
                    bad += 1
                # status = 0
            if reward > 1:
                passed += 1

            # clear_output(wait=True)
        if epsilon > epsilon_final and i > 1:  # decrement epsilon over time
            epsilon -= (epsilon_initial - epsilon_final) / explore

    # serialize weights to HDF5

    f.close()


def testAlgo(init=0):
    i = 0
    level,state=gm.initGridPlayer()

    print("Initial State:")
    print(gm.dispGrid(state))
    status = 1
    input_states = np.stack((state, state, state, state), axis=0)
    # while game still in progress
    while (status == 1):
        qval = model.predict(input_states.reshape(1, inputGrid * nr_states), batch_size=1)
        action = (np.argmax(qval))  # take action with highest Q-value
        newstate, reward = gm.makeMove(state, action)
        print('Move #: %s; Taking action: %s with reward %s' % (i, action,reward))
        input_states = np.stack((newstate, input_states[1], input_states[2], input_states[3]), axis=0)
        state=newstate
        print(gm.dispGrid(newstate))
        # reward = gm.getReward(newstate,state)
        if abs(reward) >= 5:
            status = 0
            print("Reward: %s" % (reward,))
        i += 1  # If we're taking more than 10 actions, just stop, we probably can't win this game
        if (i > 50):
            print("Game lost; too many moves.")
            break


del model
model = load_model("model.h5")
train2()

testAlgo(1)
testAlgo(1)
