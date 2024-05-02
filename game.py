""" 
A version of fruit ninja that uses machine learning.

@author: Kate Little
@version: April 2024
"""

import mediapipe as mp
from mediapipe import solutions
from mediapipe.framework.formats import landmark_pb2
import cv2
import random
import time
import math
import pygame 


# GO THROUGH AND ADD PYGAME 
# GENERATE A WINDOW

RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
ANIMATION_TIME = 2
WIDTH = 1200
HEIGHT = 800
PIZZA_RADIUS = 225

# Library Constants
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkPoints = mp.solutions.hands.HandLandmark
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
DrawingUtil = mp.solutions.drawing_utils

class Customer(pygame.sprite.Sprite): 
    def __init__(self, difficulty, prev_customer_y):
        # is this line necessary? 
        super().__init__()
        self.is_on_screen = False
        self.num_slices = random.randint(1, 4) * 2
        # the instant when the customer is created
        self.appear_time = None
        # When the customer has been waiting a long time, set to true. 
        self.is_mad = False
        self.is_done = False
        self.difficulty = difficulty
        # CHANGE THIS to be neg SO THE character spawns off screen 
        # IS THIS POSSIBLE? 
        self.normal_image = pygame.image.load('data/character.png')
        self.bubble = pygame.image.load('data/speech_bubble.png')
        self.x = -self.normal_image.get_width()
        self.final_x = self.normal_image.get_width() - 15
        # Customer's position is dependent on their position in line 
        self.y = prev_customer_y + 120
        ## The customer needs a couple dif. potential graphics. One for normal mode, another for when they are mad 

    ## slides the customer onto screen by shifting x coordinate
    def appear(self): 
        if self.appear_time == None: 
            self.appear_time = time.time()

        if time.time() - self.appear_time < ANIMATION_TIME and self.x + 12 <= self.final_x:
            self.x += 12
        elif self.is_done == False:
            if self.x != self.final_x:
                self.x = self.final_x

    # Slides the customer off screen 
    def move_up(self):
        if self.y > -self.normal_image.get_height(): 
            self.y -= 8
    
    # Displays the customer's order on the screen
    def give_order(self, screen):
        x = self.x + self.normal_image.get_width() + 10
        y = self.y - 20
        bubble_rect = self.bubble.get_rect(topleft=(x, y))

        # Convert the integer num_slices to a string
        message = str(self.num_slices) + " slices!"

        font = pygame.font.Font(None, 24)  # Choose your font and font size
        text = font.render(message, True, BLACK)

        # Finds position to display the text in speech bubble
        text_rect = text.get_rect(center=bubble_rect.center)

        # Displays bubble + text to the screen
        screen.blit(self.bubble, (x, y))
        screen.blit(text, text_rect)


    def is_long_wait(self):
        # Depending on the game difficulty, a long wait is characterized differently 
        if self.difficulty == 1: 
            thres = 12
        elif self.difficulty == 2: 
            thres = 9
        elif self.difficulty == 3: 
            thres = 6
        elif self.difficulty == 4: 
            thres = 4
        elif self.difficulty == 5: 
            thres = 2

        if time.time() - self.appear_time > thres: 
            self.is_mad = True

    def draw(self, screen):
        if self.is_mad: 
            # adjust for mad image
            screen.blit(self.normal_image, (self.x, self.y))
        else: 
            screen.blit(self.normal_image, (self.x, self.y))
    

class Pizza(pygame.sprite.Sprite): 
    def __init__(self): 
        # is this line necessary? 
        super().__init__()
        self.pizza_image = pygame.image.load('data/pizza.png')
        self.box_image = pygame.image.load('data/pizza_box.png')
        self.x = WIDTH / 2 - self.pizza_image.get_width() / 2
        self.y = 800
        self.final_y = HEIGHT / 2 - self.pizza_image.get_height() / 2
        self.is_on_screen = False
        self.slices_complete = 0 
        self.appear_time = None
        self.is_done = False

    def appear(self): 
        if self.appear_time == None: 
            self.appear_time = time.time()

        if time.time() - self.appear_time < ANIMATION_TIME and self.y -40 >= self.final_y:
            self.y -= 40
        elif self.is_done == False: 
            if self.y != self.final_y:
                self.y = self.final_y
            self.is_on_screen = True

    # Checks to see if pizza has been cut into right # of slices
    def check_is_done(self, customer):
        if self.slices_complete == customer.num_slices: 
            self.is_done = True
        return self.is_done

    def disappear(self):
        if self.y + 40 >= -820: 
            self.y -= 40

    def draw(self, screen): 
        if not self.is_done:
            screen.blit(self.pizza_image, (self.x, self.y))
        # Draws the pizza in a box if it has been completed
        else:
            screen.blit(self.box_image, (self.x, self.y))




class Game: 
    def __init__(self):
        self.difficulty = 1 
        self.score = 0
        self.is_slicing = False
        self.is_moving = False
        self.pizzas = []
        self.starting_points = []
        self.cutter_coor = (0, 0)
        self.complete_slices = []
        self.current_point = None
        self.background = pygame.image.load('data/background.jpg')
        self.chef = pygame.image.load('data/chef.png')

        pygame.init()

        # Game starts with 2 pizzas 
        self.pizzas.append(Pizza())
        self.pizzas.append(Pizza())
        self.current_pizza = self.pizzas[0]

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pizza Ninja')

        # Add 1 random customer to the list 
        self.customers = []
        self.customers.append(Customer(self.difficulty, -60))
        self.current_customer = self.customers[0]
        self.finished_customers = []

        # Create the hand detector
        # Sourced from Ms. Namasivayam's code in the finger tracking game 
        base_options = BaseOptions(model_asset_path='data/hand_landmarker.task')
        options = HandLandmarkerOptions(base_options=base_options,
                                                num_hands=2)
        self.detector = HandLandmarker.create_from_options(options)

        # Load video
        self.video = cv2.VideoCapture(1)

    # Draw a pizza cutter on the pointer finger using hand landmarks
    def draw_cutter(self, screen, detection_result):
        cutter = pygame.image.load('data/cutter.png')

        # Get a list of the landmarks
        hand_landmarks_list = detection_result.hand_landmarks
        
        # Loop through the detected hands to visualize each landmark 
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # get coordinates of just the index finger
            index_finger = hand_landmarks[HandLandmarkPoints.INDEX_FINGER_TIP.value]

            # map the finger coordinates back to screen dimensions 
            pixelCoord = DrawingUtil._normalized_to_pixel_coordinates(index_finger.x, index_finger.y, WIDTH, HEIGHT)

            if pixelCoord:
                # draw + center the pizza cutter at the coordinates of the finger
                start_x = int(pixelCoord[0] - cutter.get_width() / 2) 
                start_y = int(pixelCoord[1] - cutter.get_height() / 2)  
                screen.blit(cutter, (start_x, start_y))
                self.cutter_coor = (start_x + cutter.get_width() / 2, start_y + cutter.get_height() / 2)


    def find_start_points(self, customer):
        num_slices = customer.num_slices 
        slice_angle = math.radians(360 / num_slices)
        if len(self.starting_points) < 2: 
            for i in range(num_slices):
                # the angle at which to draw the slice around the pizza
                angle = i * slice_angle
                # represent the coordinates of the new point
                # https://stackoverflow.com/questions/34372480/rotate-point-about-another-point-in-degrees-python
                # Debugged with ChatGPT
                new_x = int(math.cos(angle) * PIZZA_RADIUS + WIDTH/2)
                new_y = int(math.sin(angle) * PIZZA_RADIUS + HEIGHT/2)
                # store the coordinates of the point for future use
                self.starting_points.append((new_x, new_y))
            
    def draw_start_points(self):
        for point in self.starting_points:
            pygame.draw.circle(self.screen, BLACK, (point[0], point[1]), 10)

    def draw_line_tracker(self):
        #Draw a line between the start point and the user's current coordinates
        pygame.draw.line(self.screen, BLACK, (self.current_point[0], self.current_point[1]), (self.cutter_coor[0], self.cutter_coor[1]), 5)
    
    # Identifies hand motion/change in the location of the index finger 
    def check_is_slicing(self):
        # if a user touches one of points
            # AKA: If the coordinates of the user's finger make contact with any of the points around the pizza (which are stored in a list)
                # then is_slicing is set to True 
                # set the point that the user has touched to the starting point 
        if self.current_point == None and self.is_slicing == False:
            for point in self.starting_points: 
                # because a user can't make the same slice twice
                if self.is_valid_point(point): 
                    x_check = point[0] - 20 <= self.cutter_coor[0] and point[0] + 20 >= self.cutter_coor[0]
                    y_check = point[1] - 20 <= self.cutter_coor[1] and point[1] + 20 >= self.cutter_coor[1]
                    if (x_check and y_check): 
                        self.is_slicing = True 
                        self.current_point = point

    # checks to ensure that the point that the user is touching is not already part of a completed slice
    def is_valid_point(self, point):
        for pair in self.complete_slices: 
            if point in pair:
                return False
        return True
    
    def check_slice_completed(self):
    # A slice is completed when the user touches the opposite starting point
       # Finds the point opposite the current one
        current_index = self.starting_points.index(self.current_point)
        num_slices = len(self.starting_points)
        opp_index = int(current_index + num_slices / 2)
        if opp_index >= num_slices:
            opp_index -= num_slices
        opp_point = self.starting_points[opp_index]

        # checks intersection b/w index finger and the opposite point
        x_check = opp_point[0] - 20 <= self.cutter_coor[0] and opp_point[0] + 20 >= self.cutter_coor[0]
        y_check = opp_point[1] - 20 <= self.cutter_coor[1] and opp_point[1] + 20 >= self.cutter_coor[1]
        # if the user has completed the slice
        if (x_check and y_check):
            # increments slice counter & draw slice
            self.current_pizza.slices_complete += 2
            self.complete_slices.append((self.current_point, opp_point))
            # reset variables
            self.is_slicing = False
            self.current_point = None

    # draws all completed slices on the pizza 
    def draw_slices(self):
        for pair in self.complete_slices: 
            # draw a line between points
            point1 = pair[0]
            point2 = pair[1]
            pygame.draw.line(self.screen, BLACK, (point1[0], point1[1]), (point2[0], point2[1]), 5)
        return
    
    def change_difficulty(self):
        if self.score > 20:
            self.difficulty = 5
        elif self.score > 15:
            self.difficulty = 4
        elif self.score > 10:
            self.difficulty = 3
        elif self.score > 5:
            self.difficulty = 2

    def update_positions(self):
        # Moves all existing customers forward in line
            if self.customers[0].y > 68: 
                for customer in self.customers:
                    customer.move_up()
            if self.customers[0].y <= 68:
                self.is_moving = False

            # Moves customers w/ completed orders off screen
            for customer in self.finished_customers:
                customer.move_up()
                customer.give_order(self.screen)
                customer.draw(self.screen)

    def print_score(self):
        width = 150 
        height = 76
        message = "Score: " + str(self.score)
        pygame.draw.rect(self.screen, WHITE, pygame.Rect(WIDTH - width, 0, width, height))

        # Print score text
        font = pygame.font.Font(None, 24)  # Choose your font and font size
        text = font.render(message, True, BLACK)

        # Finds position to display the text in speech bubble

        ## Change this to go in the right position. reference how I printed the orders.
        text_rect = text.get_rect((1000, 500))

        # Displays bubble + text to the screen
        self.screen.blit(self.bubble, (x, y))
        self.screen.blit(text, text_rect)



    # Main game loop 
    def run(self): 
        """
        Main game loop. Runs until the 
        user presses "q".
        """  
        running = True  
        # Use this to generate customers
        start_time = time.time()
            
        while self.video.isOpened() and running:
            # Get the current frame
            frame = self.video.read()[1]

            # Convert it to an RGB image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # the image comes mirrored - flip it 
            image = cv2.flip(image, 1)

            # Convert the image to a readable format and find the hands
            to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            results = self.detector.detect(to_detect)

            self.screen.blit(self.background, (0, 0))
            self.screen.blit(self.chef, (WIDTH / 2 + 200, 30))
            self.print_score()
             
            # Finds the starting points on pizza depending on the current customer
            self.find_start_points(self.current_customer)

            # Draws all waiting customers on screen
            for customer in self.customers:
                customer.appear()
                customer.draw(self.screen)
                customer.give_order(self.screen)
            customer_timer = time.time() - start_time

            # Adds new customers to the screen 
            # The rate depends on the difficulty of the game 
            # High difficuly = high rate 
            if customer_timer > (12 - self.difficulty * 2):
                # Creates a customer based on the previous customer's y position 
                if len(self.customers) >= 1: 
                    self.customers.append(Customer(self.difficulty, self.customers[-1].y + 70))
                else: 
                    self.customers.append(Customer(self.difficulty, -60))
                # Reset customer timer variables 
                start_time = time.time()

            # Draw the first pizza in the list 
            self.current_pizza.appear()
            self.current_pizza.draw(self.screen)

            if self.current_pizza.is_on_screen and not self.current_pizza.is_done:
                self.draw_start_points()

            self.draw_cutter(self.screen, results)

            # Draw pizza slices as they're being made 
            if not self.current_pizza.is_done and self.current_pizza.is_on_screen:
                self.check_is_slicing()
                if self.is_slicing:
                    self.draw_line_tracker()
                    self.check_slice_completed()
                self.draw_slices()

            # Check if pizza is complete
            if self.current_pizza.check_is_done(self.current_customer):
                self.score += 1
                # This line should be displayed on the screen somewhere!
                print("score: ", self.score)

                # Makes current pizza disappear
                self.current_pizza.disappear()

                # Removes old customer and adds new one 
                # This is not allowing the customer to disappear from screen! They are removed from this list, so they pop off immediately!!
                # I need to only remove the current customer if it is OFF the screen
                self.finished_customers.append(self.current_customer)
                self.customers.remove(self.current_customer)
                self.current_customer.is_done = True 

                if len(self.customers) <= 1: 
                    # Creates a customer based on the previous customer's y position 
                    if len(self.customers) == 1: 
                        self.customers.append(Customer(self.difficulty, self.customers[-1].y + 70))
                    else: 
                        self.customers.append(Customer(self.difficulty, -60))
                     # Reset customer timer variables 
                    start_time = time.time()
                self.current_customer = self.customers[0]

                # Removes old pizza and adds new one
                self.pizzas.remove(self.current_pizza)
                self.pizzas.append(Pizza())
                self.current_pizza = self.pizzas[0]

                # Resets pizza slices 
                self.complete_slices = []
                self.starting_points = []

                self.is_moving = True

            # Move customers forward (either up in line or off screen)
            self.update_positions()



            self.change_difficulty()

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(50) & 0xFF == ord('q'):
                break

        self.video.release()
        cv2.destroyAllWindows()
    
    
if __name__ == "__main__":        
    g = Game()
    g.run()