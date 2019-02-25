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

    def __init__(self, game_width):
        self.loss = "mse"
        self.reward = 0
        self.learning_rate = .01
        self.gamma = .9
        self.n_states = 8
        self.model = self._setup()
        self.memory_states = []
        self.outcomes = []
        
    def get_state(self, player, food):
        left, right = player.obstacle_left_right
        obstacles = np.array([int(player.obstacle_ahead), int(left), int(right)]).flatten()
        directions = np.array([int(player.going_up), int(player.going_down), int(player.going_left), int(player.going_right)])
        angle = np.array([food.get_angle_to_point(player.pos_x, player.pos_y, norm=True)])
        return np.concatenate((obstacles, directions, angle))

    # def get_state(self, player, food, rows):
    #     left, right = player.obstacle_left_right
    #     obstacles = np.array([int(player.obstacle_ahead), int(left), int(right)]).flatten()
    #     directions = np.array([int(player.going_up), int(player.going_down), int(player.going_left), int(player.going_right)])
    #     angle = np.array([food.get_angle_to_point(player.pos_x, player.pos_y, norm=True)])

    #     grid = np.zeros((rows + 2, rows + 2))
    #     for cube in player.body:
    #         x, y = cube.pos
    #     return np.concatenate((obstacles, directions, angle))
        
    def update_reward(self, food_reached, food_dist_chng, game_over):
        if game_over is True:
            reward = -10
        elif food_reached is True:
            reward = 10
        else:
            reward = 0
        if food_dist_chng < 0:
            reward += 1
        elif food_dist_chng > 0:
            reward -= 1
        self.reward = reward

    def _setup(self, weights=None):
        model = Sequential()
        model.add(Dense(50, activation="relu", input_shape=(self.n_states, )))
        model.add(Dropout(0.1))
        # model.add(Dense(500, activation='relu'))
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
            target = max(self.reward + self.gamma * np.amax(self.model.predict(np.array([next_state]))[0]), 0)
        target_f = self.model.predict(np.array([state]))
        target_f[0][np.argmax(action)] = target
        self.memory_states.append(np.array(state))
        self.outcomes.append(target_f.flatten())
    
    def replay_new(self):
        # if len(self.memory_states) > 50000:
        #     print("Reducing memory")
        #     self.memory_states = self.memory_states[-50000:]
        #     self.outcomes = self.outcomes[-50000:]
        print(f"Memory length: {len(self.outcomes)}")
        # if len(self.outcomes) > 50000:
        #     self.outcomes = self.outcomes[-50000:]
        #     self.memory_states = self.memory_states[-50000:]
        #     print("Reducing memory")
        
        # print("Memory length: " + str(len(self.memory)))
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
