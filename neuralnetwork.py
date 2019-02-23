from keras import optimizers
from keras import models
from keras.models import Sequential
from keras.layers.core import Dense, Dropout
from keras.layers import Input
import numpy as np
import random
import pickle
import os


class NeuralNet:

    def __init__(self):
        self.loss = "mse"
        self.reward = 0
        self.learning_rate = .0005
        self.gamma = .9
        self.n_states = 11
        self.model = self._setup()
        self.memory = []
        self.memory_states = []
        self.outcomes = []
        

    def get_state(self, player, food):
        state = []
        state.append(player.obstacle_ahead)
        state.extend(player.obstacle_left_right)
        state.extend([player.going_up,
                      player.going_down,
                      player.going_left,
                      player.going_right
        ])
        state.extend([food.pos_x < player.pos_x,
                      food.pos_x > player.pos_x,
                      food.pos_y < player.pos_y,
                      food.pos_y > player.pos_y
        ])
        
        state = np.asarray([int(s) for s in state])
        return state
    
    def update_reward(self, food_reached=None, game_over=None):
        if game_over:
            reward = -10
        elif food_reached:
            reward = 10
        else:
            reward = 0
        self.reward = reward

    def _setup(self, weights=None):
        model = Sequential()
        model.add(Dense(50, activation="relu", input_shape=(self.n_states, )))
        model.add(Dropout(0.1))
        # model.add(Dense(250, activation='relu'))
        # model.add(Dropout(0.1))
        # model.add(Dense(250, activation='relu'))
        # model.add(Dropout(0.1))
        model.add(Dense(3, activation='softmax'))
        optimizer = optimizers.Adam(self.learning_rate)
        model.compile(loss=self.loss, optimizer=optimizer)
        if weights:
            model.load_weights(weights)
        return model

    def remember(self, state, action, next_state, game_over):
        # self.memory.append((state, action, self.reward, next_state, game_over))
        target = self.reward
        if not game_over:
            target = self.reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
        target_f = self.model.predict(np.array([state]))
        target_f[0][np.argmax(action)] = target
        self.memory_states.append(np.array(state))
        self.outcomes.append(target_f.flatten())
    
    def replay_new(self):
        # if len(self.memory) > 50000:
        #     print("Reducing memory")
        #     self.memory = self.memory[-50000:]
        if len(self.outcomes) > 50000:
            self.outcomes = self.outcomes[-50000:]
            self.memory_states = self.memory_states[-50000:]
            print("Reducing memory")
        
        print("Memory length: " + str(len(self.memory)))
        # print("Preparing data for training...")

        # minibatch = self.memory
        # states, outcomes = [], []
        # for state, action, reward, next_state, game_over in minibatch:
        #     target = reward
        #     if not game_over:
        #         target = reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0])
        #     target_f = self.model.predict(np.array([state]))

        #     target_f[0][np.argmax(action)] = target  # What is this for?
        #     states.append(np.array(state))
        #     outcomes.append(target_f.flatten())
        self.model.fit(np.array(self.memory_states), np.array(self.outcomes), epochs=10, verbose=2)

    def train_short_memory(self, state, action, next_state, game_over):
        target = self.reward
        if not game_over:
            target = self.reward + self.gamma * np.amax(self.model.predict(next_state.reshape((1, self.n_states)))[0])
        target_f = self.model.predict(state.reshape((1, self.n_states)))
        target_f[0][np.argmax(action)] = target
        self.model.fit(state.reshape((1, self.n_states)), target_f, epochs=1, verbose=0)
