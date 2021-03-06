import config
import matplotlib.pyplot as plt
import gamemanager as gm
from snake import Snake
from cube import Cube
from time import sleep
from neuralnetwork import NeuralNet
from keras.utils import to_categorical
import seaborn as sns
import pandas as pd
import numpy as np
import pygame
import random
import sys
import os

    
def drawGrid(surface):
    width = gm.window_width
    size_btwn = width // gm.rows
    x, y = 0, 0
    for _ in range(gm.rows):
        x += size_btwn
        y += size_btwn
        pygame.draw.line(surface, (255, 255, 255), (x, 0), (x, width))
        pygame.draw.line(surface, (255, 255, 255), (0, y), (width, y))

def redraw_window(surface):
    global snake, food
    surface.fill((150, 150, 150))
    snake.draw(surface)
    food.draw(surface)
    # drawGrid(surface)
    pygame.display.update()

def generate_food(restricted_positions):
    while True:
        x = random.randrange(gm.rows)
        y = random.randrange(gm.rows)
        if len(list(filter(lambda z: z.pos == (x, y), restricted_positions))) > 0:
            continue
        elif x == gm.rows // 2 and y == gm.rows // 2:
            continue
        else:
            break
    return (x, y)

def manhatten_dist(food, snake):
    return abs(food.pos_x - snake.pos_x) + abs(food.pos_y - snake.pos_y)

def plot_seaborn(array_counter, array_score, description):
    sns.set(color_codes=True)
    ax = sns.regplot(np.array([array_counter])[0], np.array([array_score])[0], color="b", x_jitter=.1, line_kws={'color':'green'})
    ax.set(xlabel='games', ylabel='score')
    ax.set_title(description)
    # plt.show()
    plt.savefig(f"{config.FLD}\\{description}\\performance.png")
    
def init_game(player, food, network):
    state_init1 = network.get_state(player, food)
    action = [0, 1, 0] # go straight
    player.move(action)
    state_init2 = network.get_state(player, food)
    network.update_reward(False, player.is_dead)
    network.remember(state_init1, action, state_init2, False)
    network.replay_new()

def save_data(network, games_played, scores, description):
    network.model.save_weights(config.get_full_path("weights.hdf5"))
    config.save_pickle(games_played, "games_played")
    config.save_pickle(scores, "scores")
    config.save_pickle(network.memory_states, "memory_states")
    config.save_pickle(network.outcomes, "outcomes")
    plot_seaborn(range(1, games_played), scores, description)

def load_data(description, network):
    games_played = config.load_pickle("games_played")
    scores = config.load_pickle("scores")

    if games_played is None or scores is None:
        print("Starting from scratch")
        games_played = 1
        scores = []
        return games_played, scores, network

    weights_file = config.get_full_path("weights.hdf5")
    if config.exists(weights_file):
        network.model.load_weights(weights_file)    
        print("Weights loaded")
    memory_file = config.get_full_path("memory_states")
    if config.exists(memory_file):
        network.memory = config.load_pickle("memory_states")
        print("Memory loaded")
    memory_file = config.get_full_path("outcomes")
    if config.exists(memory_file):
        network.memory = config.load_pickle("outcomes")
        print("Outcomes loaded")

    return games_played, scores, network

def main(description):
    global snake, food

    death_states = []

    if gm.auto_movement is False:
        gm.display = True

    if gm.display:
        window = pygame.display.set_mode((gm.window_width, gm.window_width))

    snake = Snake((192, 0, 0), (gm.rows // 2, gm.rows // 2))
    food = Cube(generate_food(snake.body), color=(0, 220, 0))

    if gm.display:
        clock = pygame.time.Clock()

    network = NeuralNet(gm.rows)

    games_played, scores, network = load_data(description, network)

    # epsilon = 10 - games_played
    # init_game(snake, food, network)
    game_over = False

    while True:

        if game_over:
            snake.reset(((gm.rows // 2, gm.rows // 2)))
            game_over = False
        score = 0

        if gm.auto_movement:
            # Network is playing
            while not game_over:
                
                if gm.display:
                    pygame.event.get()
                # pygame.time.delay(0)
                if gm.display:
                    clock.tick(gm.speed)

                food_reached = False

                state_old = network.get_state(snake, food)
                
                #perform random actions based on network.epsilon, or choose the action
                # if random.randint(0, 200) < epsilon:
                #     move_vector = to_categorical(random.randint(0, 2), num_classes=3)
                #     # move_vector = np.array([0.0, 1.0, 0.0])
                # else:
                #     # predict action based on the old state
                prediction = network.model.predict(state_old.reshape((1, network.n_states)))[0]
                move_vector = to_categorical(np.argmax(prediction), num_classes=3)

                food_dist_pre_move = manhatten_dist(food, snake)
                snake.move(move_vector)
                food_dist_post_move = manhatten_dist(food, snake)
                food_dist_chng = food_dist_post_move - food_dist_pre_move        

                if snake.has_eaten(food.pos):
                    food_reached = True
                    snake.grow()
                    food = Cube(generate_food(snake.body), color=(0, 220, 0))

                if snake.is_dead:
                    game_over = True
                    score = snake.body_length

                state_new = network.get_state(snake, food)

                if snake.is_dead:
                    death_states.append(list(np.concatenate([state_old, move_vector, state_new])))

                network.update_reward(food_reached, food_dist_chng, game_over)
                network.train_short_memory(state_old, move_vector, state_new, game_over)
                network.remember(state_old, move_vector, state_new, game_over)
                if gm.display:
                    redraw_window(window)
            
            if games_played % 100 == 0:
                network.replay_new()
            games_played += 1
            print(f"game {games_played}, score {score}")
            scores.append(score)

            if games_played % 50 == 0:
                save_data(network, games_played, scores, description)
            if games_played % 50 == 0:
                pd.DataFrame.from_records(death_states).to_csv(config.get_full_path("death_states.txt"), mode="a")
                death_states = []

        else:
            # Manual Play
            while not game_over:
                clock.tick(gm.speed)
                food_reached = False
                snake.move()
                if snake.has_eaten(food.pos):
                    food_reached = True
                    snake.grow()
                    food = Cube(generate_food(snake.body), color=(0, 220, 0))
                if snake.is_dead:
                    game_over = True
                    score = snake.body_length
                    # snake.reset((10, 10))
                redraw_window(window)
                # print(f"x:{snake.pos_x}, y:{snake.pos_y}")

    save_data(network, games_played, scores, description)


if __name__ == "__main__":        

    for arg in sys.argv:
        if arg.lower() == "show":
            gm.display = True
        elif arg.lower() == "reset":
            config.reset_folder()

    # try:
    #     display = sys.argv[1]
    #     if display.lower() == "show":
    #         gm.display = True
    # except IndexError:
    #     pass
    print("WARNING: Memory is not loaded when resuming the game.")
    config.create_folder(config.DESCRIPTION)
    main(config.DESCRIPTION)

# Improvements
# Need to dump memory to avoid big RAM allocation
# Dump results every couple of iterations
