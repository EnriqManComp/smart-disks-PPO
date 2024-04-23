"""
Author: Enrique Manuel Companioni Valle
Date: 25/04/2021
Description: This script is the main file to run the Deep Reinforcement Learning algorithm to solve the evasor-pursuiter problem.
The algorithm is based on the Deep Q-Learning algorithm. The environment is designed using the Pygame library.
The algorithm is implemented using the TensorFlow library.
The algorithm is trained using the Random Sample Experience Replay method.

The code defines the `Environment` class, which represents the game environment for the Deep Reinforcement Learning algorithm.
It contains methods to initialize the environment, run the game algorithm, and handle the game logic.
The environment consists of a Pygame window, obstacles, players (pursuiter and evasor), and a sensor.
The algorithm uses the Deep Q-Learning algorithm to train the pursuiter to catch the evasor while avoiding obstacles.
The algorithm is trained using the Random Sample Experience Replay method, which stores and replays past experiences to improve learning.
"""
#################################### 
##         Import Libraries       ##
####################################

import pygame
import sys
import numpy as np
from PIL import Image
import gc
import time

from pursuiter import Pursuiter
from evasor import Evasor
from utils import Utils
from obstacles import Obstacles
from memory import Memory
from DRL_algorithm import DRL_algorithm
from sensors import Sensor

#################################### 
##       Environment Design       ##
####################################

class Environment:
    """
        This class define the pygame functionality to implement the Deep Reinforcement Learning method.
    """
    def __init__(self):        
        ##### PYGAME
        # Initialise pygame
        pygame.init()
        # Set window
        self.screen = pygame.display.set_mode((200, 200))
        # FPS controler
        self.clock = pygame.time.Clock() 

        ##### OBSTACLES
        self.sensor = Sensor()
        self.obstacles = Obstacles(self.screen)

        ##### UTILS
        self.utils = Utils(self.obstacles, self.sensor)

        ##### CONSTANT PARAMETERS
        # Episodes
        self.EPISODES = 20_000
        # Possible Actions
        self.ACTIONS = {
            0: "NO ACTION",            
            1: "UP",
            2: "DOWN",
            3: "LEFT",
            4: "RIGHT",
            5: "DOUBLE-UP",
            6: "DOUBLE-DOWN",
            7: "DOUBLE-LEFT",
            8: "DOUBLE-RIGHT"
                        
        }             

        ###### MEMORY
        # Initial number of experience in storage to start the training
        
        self.memory = Memory(batch_size=32)

        ###### Deep Reinforcement Learning algorithm
        self.drl_algorithm = DRL_algorithm(self.memory)

        # Run parameters
        self.current_state = np.empty((200,200,3))
        self.next_state = np.empty((200,200,3))        
        self.done = False

        # Metric parameters        
        self.record_scores = []        

        #### Players
        self.pursuiter = Pursuiter()
        self.evasor = Evasor()

        ## triggers
        self.restart_params_trigger = False
        self.start_new_cycle_trigger = True
        self.save_exp_trigger = False
        self.training_trigger = False

        self.run_time = 1

    def run(self):              
        """
            This method run the game algorithm
        """

        ######## TRIGGERS
        save_net_indicator = 1        
        
        load = True
        if load:
            self.drl_algorithm.load_models(1)    

        n_steps = 0
        avg_score = 0
        best_scores = 84403.71148195057
        learn_iters = 0
        N = 64    
            
        for epis in range(1701, self.EPISODES+1):
            ##### Restart the initial parameters in each episode
            self.done = False           
            
            reward = 0
            
            scores = 0.0
            self.run_time = 1           

            ##### TRIGGERS
            # 1st step
            self.restart_params_trigger = False
            # 2nd step
            self.start_new_cycle_trigger = True
            # 3rd step
            self.save_exp_trigger = False
            # 4th step
            self.training_trigger = False

            # Spawn the agents and draw the environment
            self.screen.fill((138,138,138))
            self.obstacles.render_walls()

            print("STARTING RESPAWN")

            self.evasor.position = []
            self.pursuiter.position = []
            self.sensor.position = []
            x, y = self.utils.random_spawn(evasor_spawn=True)
            self.evasor.position.append(x)            
            self.evasor.position.append(y)
            self.evasor.spawn(self.screen)

            x, y = self.utils.random_spawn(self.evasor.position, self.screen, self.evasor, evasor_spawn=False)
            self.pursuiter.position.append(x)            
            self.pursuiter.position.append(y)
            self.pursuiter.spawn(self.screen)

            self.sensor.position.append(self.pursuiter.position[0])
            self.sensor.position.append(self.pursuiter.position[1])
            
            self.sensor.lidar(self.screen)
            self.screen.fill((138,138,138))
            self.obstacles.render_walls()
            self.evasor.spawn(self.screen)
            self.pursuiter.spawn(self.screen)         
            # Update the screen
            pygame.display.update()             
            
            
                           
            print("######################################################EPISODE: ", epis)
            while (self.run_time <= 452) and (not self.done):
                # Run the game algorithm
                
                for event in pygame.event.get():
                    # Exit event
                    if event.type == pygame.QUIT:
                        sys.exit()
                    
                ########### Restart parameters
                        
                if self.restart_params_trigger:                    
                    ### Save metrics
                    # Save score
                    scores += reward
                                                               
                    # Check end episode condition
                    if (self.done):
                        break
                    # Increase run time 
                    
                    # Set the dimensions of the states          
                    self.current_state = np.empty((200,200,3))
                    self.next_state = np.empty((200,200,3))        
                     
                    gc.collect()
                    time.sleep(0.05)                  
                    # Restart the trigger cycle
                    self.drl_algorithm.training_finished = False
                    self.restart_params_trigger = False                
                    self.start_new_cycle_trigger = True
                
                ########### CAPTURE CURRENT STATE
                    
                if self.start_new_cycle_trigger:
                                    
                    # Get current state
                            
                    print("Run time: ", self.run_time)
                    self.current_state = self.get_capture()                    

                    ###### EXECUTE THE ACTION 
                    # Get lidar observation
                    lidar_current_state = self.utils.lidar_observations(self.pursuiter.position[0], self.pursuiter.position[1], self.evasor)
                    # Select an action
                    
                    action, prob, val = self.drl_algorithm.policy(lidar_current_state)
                    print(action)  
                    action_string = self.ACTIONS[action]                
                    print(action)               
                    # Execute the action selected
                    self.pursuiter.controls(action= action_string)                               
                    # Update the position of the lidar rectangles
                    self.sensor.update_position(self.pursuiter.position)

                    ######## DRAW ZONE
                    # Draw the window with the updates
                    # Draw lidar
                    self.sensor.lidar(self.screen)
                    # Draw background
                    self.screen.fill((138,138,138))
                    # Draw obstacles                    
                    self.obstacles.render_walls()
                    # Draw pursuiter
                    self.pursuiter.spawn(self.screen)                         
                    # Draw evasor
                    self.evasor.spawn(self.screen)                                                           
                    
                    ####### END DRAW ZONE

                    ###########  CAPTURE NEXT STATE 
                                                    
                    
                    ######### GET REWARD
                                        
                    reward, self.done = self.utils.get_reward(self.pursuiter.robot, self.evasor.robot, self.pursuiter.position, self.evasor.position)                        

                    #print(reward)
                    
                    # Activate and deactivate step triggers
                    self.save_exp_trigger = True                   

                ########## SAVE EXPERIENCE 
                
                    if self.save_exp_trigger:      
                        # Add experience in memory                                                                          
                        self.memory.store_memory(self.current_state.copy(), lidar_current_state, action, prob, val, reward, self.done)        
                        n_steps += 1
                        # Next step (TRAINING NETWORK)                                               
                        self.save_exp_trigger = False                         
                        self.run_time += 1                            
                        pygame.display.update()
                        if self.done:
                            break


                    print("Training step")
                    self.start_new_cycle_trigger = False
                    self.training_trigger = True                                                

                if self.training_trigger:                
                    # Train the model
                    if n_steps % N == 0:
                        self.drl_algorithm.train()           
                    # Wait until the training has been completed.
                        while not self.drl_algorithm.training_finished:
                            continue
                        learn_iters += 1
                    
                    self.restart_params_trigger = True
           
                # Update the display
                pygame.display.update()                
            
            print("END RUN TIME")
            # Save scores of the episode
            self.record_scores.append(scores)            
            avg_score = np.mean(self.record_scores[-50:])
            
            # Check if the algorithm is still in the non-training phase.
            
                # Save the model if the score of the episode is grater than 2500
            if (avg_score > best_scores):
                # Save the weights
                best_scores = avg_score
                self.drl_algorithm.save_model(save_net_indicator)
                # Save network records
                with open("../records/save_network.txt", 'a') as file:
                    file.write("Save: {0}, Episode: {1}/{2}, Best Score: {3}, Play_time: {4}, Spawn distance: {5}\n".format(save_net_indicator, epis, self.EPISODES, best_scores, self.run_time, self.utils.spawn_eucl_dist))
                save_net_indicator += 1
            # Save records and model each 100 episodes.
            if epis % 100 == 0:        
                # Save scores and losses
                with open("../records/save_records.txt", 'a') as file:
                    file.write("Scores: {0}\n".format(self.record_scores))
                
                

                
                # Restart the record scores and losses
                self.record_scores = []               
            

            gc.collect()
            time.sleep(1)
            print("END EPISODE")

        pygame.quit()

    def get_capture(self):
        """
            Capture the current state image.
            Return:
                captured (NumPy array): Return a NumPy array image with dimensions (405, 410, 3).

        """
        # Create the Surface        
        capture = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        # Blit the screen on the Surface
        capture.blit(self.screen, (0, 0))
        # Convert from Surface to Array
               
        # Return the capture
        return pygame.surfarray.array3d(capture)   

    def test(self):
        # Loading the model
        self.drl_algorithm.load_models(1)                    
        scores = 0.0
        record_scores = []
        images = []
        for epis in range(100):
            print("Scores: ", scores)            
            self.done = False

            reward = 0.0

            scores = 0.0
            self.run_time = 1

            ##### TRIGGERS
            # 1st step
            self.restart_params_trigger = False
            # 2nd step
            self.start_new_cycle_trigger = True
            
            # 3rd step            

            # Spawn the agents and draw the environment
            self.screen.fill((138,138,138))
            self.obstacles.render_walls()

            print("STARTING RESPAWN")

            self.evasor.position = []
            self.pursuiter.position = []
            self.sensor.position = []
            x, y = self.utils.random_spawn(evasor_spawn=True)
            self.evasor.position.append(x)            
            self.evasor.position.append(y)
            self.evasor.spawn(self.screen)

            x, y = self.utils.random_spawn(self.evasor.position, self.screen, self.evasor, evasor_spawn=False)
            self.pursuiter.position.append(x)            
            self.pursuiter.position.append(y)
            self.pursuiter.spawn(self.screen)

            self.sensor.position.append(self.pursuiter.position[0])
            self.sensor.position.append(self.pursuiter.position[1])
            
            self.sensor.lidar(self.screen)
            self.screen.fill((138,138,138))
            self.obstacles.render_walls()
            self.evasor.spawn(self.screen)
            self.pursuiter.spawn(self.screen)         
            # Update the screen
            pygame.display.update() 

            print("######################################################EPISODE: ", epis)

            while (not self.done) and (self.run_time <= 452):
                for event in pygame.event.get():
                    # Exit event
                    if event.type == pygame.QUIT:
                        sys.exit()

                
                ### Save metrics
                # Save score
                
                                                     
                # Check end episode condition
                if (self.done):
                    break
                # Increase run time 
                    
                # Set the dimensions of the states          
                self.current_state = np.empty((200,200,3))
                self.current_state = self.get_capture()
                #images.append(Image.fromarray(self.current_state, 'RGB'))                
                     
                                          

                
                print("Run time: ", self.run_time)
                                   

                    ###### EXECUTE THE ACTION 
                    # Get lidar observation
                lidar_current_state = self.utils.lidar_observations(self.pursuiter.position[0], self.pursuiter.position[1], self.evasor)
                    # Select an action
                action, _, _ = self.drl_algorithm.policy(lidar_current_state)  
                action_string = self.ACTIONS[action]                
                print(action_string)               
                    # Execute the action selected
                self.pursuiter.controls(action= action_string)                               
                    # Update the position of the lidar rectangles
                self.sensor.update_position(self.pursuiter.position)

                    ######## DRAW ZONE
                    # Draw the window with the updates
                    # Draw lidar
                self.sensor.lidar(self.screen)
                    # Draw background
                self.screen.fill((138,138,138))
                    # Draw obstacles                    
                self.obstacles.render_walls()
                    # Draw pursuiter
                self.pursuiter.spawn(self.screen)                         
                    # Draw evasor
                self.evasor.spawn(self.screen)                                                           
                        
                    ####### END DRAW ZONE

                    ###########  CAPTURE NEXT STATE 
                
                    # Get lidar next state observations
                
                        
                    ######### GET REWARD
                                            
                reward, self.done = self.utils.get_reward(self.pursuiter.robot, self.evasor.robot, self.pursuiter.position, self.evasor.position)                        
                self.run_time += 1
                scores += reward
                
                pygame.display.update()
            
            record_scores.append(scores)
        
        #images[0].save('show_landing.gif',save_all=True,append_images=images[1:],duration=self.run_time,loop=0) # saving images to a gif
        
        with open("../records/save_record_test.txt", 'a') as file:
            file.write("Scores: {0}\n".format(record_scores))
                
        
        

# Run the algorithm
train = False
gc.enable()
gc.collect()
if train:
    Environment().run()
else:
    Environment().test()

