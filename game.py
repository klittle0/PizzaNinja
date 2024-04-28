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
    def __init__(self, difficulty):
        # is this line necessary? 
        super().__init__()
        self.is_on_screen = False
        self.num_slices = random.randint(1, 4) * 2
        # the instant when the customer is created
        self.appear_time = None
        # When the customer has been waiting a long time, set to true. 
        self.is_mad = False
        self.difficulty = difficulty
        # CHANGE THIS to be neg SO THE character spawns off screen 
        # IS THIS POSSIBLE? 
        self.normal_image = pygame.image.load('data/character.png')
        self.x = -self.normal_image.get_width()
        # the self.y should change depending on the customer's position in line. OR: an integer should be passed into their draw method and they 
        # are drawn at integer * self.y  
        self.y = 120
        ## The customer needs a couple dif. potential graphics. One for normal mode, another for when they are mad 

    ## slides the customer onto screen by shifting x coordinate
    def appear(self): 
        if self.appear_time == None: 
            self.appear_time = time.time()

        if time.time() - self.appear_time < ANIMATION_TIME:
            self.x += 8
            
    def leave(self):
        # TODO 
        disappear_start = time.time()
        if self.x > -150: 
            self.x += -2
        ## add code that removes the player from the screen
        return

    def approve_order(self):
        # TODO 
        # checks the # of slices made in the pizza to confirm 
        return

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
        else: 
            if self.y != self.final_y:
                self.y = self.final_y
            self.is_on_screen = True

    # Checks to see if pizza has been cut into right # of slices
    def check_is_done(self, customer):
        if self.slices_complete == customer.num_slices: 
            self.is_done = True
        return self.is_done

    # THIS DOESN'T WORK. THE METHOD IS REACHED, BUT SELF.Y DOESN'T CHANGE!!
    def disappear(self):
        print("Disappearing")
        print(self.y)
        # is this a magic number? do I need to replace? 
        self.y = 800

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
        # there only needs to be one pizza. As soon as the customer approves the order, the pizza is "boxed", aka it disappears
        #and the box slides away at the same time as the pizza returns 
        self.pizza = Pizza()
        self.starting_points = []
        self.star_coor = (0, 0)
        self.complete_slices = []
        self.current_point = None

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pizza Ninja')

        # generate random customer, put them in the list, then as soon as they're off screen, remove them from list. 
        self.customers = []
        self.customers.append(Customer(self.difficulty))

        #finds the starting points on pizza depending on the current customer
        self.find_start_points(self.customers[0])

        # Create the hand detector
        # Sourced from Ms. Namasivayam's code in the finger tracking game 
        base_options = BaseOptions(model_asset_path='data/hand_landmarker.task')
        options = HandLandmarkerOptions(base_options=base_options,
                                                num_hands=2)
        self.detector = HandLandmarker.create_from_options(options)

        # Load video
        self.video = cv2.VideoCapture(1)

    # Draw a star on the pointer finger using hand landmarks
    def draw_star(self, screen, detection_result):
        star = pygame.image.load('data/Star.png')

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
                # draw + center the star at the coordinates of the finger
                start_x = int(pixelCoord[0] - star.get_width() / 2) 
                start_y = int(pixelCoord[1] - star.get_height() / 2)  
                screen.blit(star, (start_x, start_y))
                self.star_coor = (start_x + star.get_width() / 2, start_y + star.get_height() / 2)


    def find_start_points(self, customer):
        num_slices = customer.num_slices 
        slice_angle = math.radians(360 / num_slices)
        if len(self.starting_points) < 2: 
            for i in range(num_slices):
                # the angle at which to draw the slice around the pizza
                angle = i * slice_angle
                # represent the coordinates of the new point
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
        pygame.draw.line(self.screen, BLACK, (self.current_point[0], self.current_point[1]), (self.star_coor[0], self.star_coor[1]), 5)
    
    # Identifies hand motion/change in the location of the index finger 
    def check_is_slicing(self):
        # tallies the slice counter of the current pizza object
    
        # if a user touches one of points
            # AKA: If the coordinates of the user's finger make contact with any of the points around the pizza (which are stored in a list)
                # then is_slicing is set to True 
                # set the point that the user has touched to the starting point 
        if self.current_point == None and self.is_slicing == False:
            for point in self.starting_points: 
                # because a user can't make the same slice twice
                if self.is_valid_point(point): 
                    x_check = point[0] - 20 <= self.star_coor[0] and point[0] + 20 >= self.star_coor[0]
                    y_check = point[1] - 20 <= self.star_coor[1] and point[1] + 20 >= self.star_coor[1]
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
        x_check = opp_point[0] - 20 <= self.star_coor[0] and opp_point[0] + 20 >= self.star_coor[0]
        y_check = opp_point[1] - 20 <= self.star_coor[1] and opp_point[1] + 20 >= self.star_coor[1]
        # if the user has completed the slice
        if (x_check and y_check):
            # increments slice counter & draw slice
            self.pizza.slices_complete += 2
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

    # Main game loop 
    def run(self): 
        """
        Main game loop. Runs until the 
        user presses "q".
        """  
        running = True  
    
        # How to do this without actually opening the video? 
        # I need to add something else here... there should be an "and" statement
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

            self.screen.fill(RED)

            #draw all customers in current positions
            # actually, shouldn't I just draw the first customer? Then, every 5 seconds, a new one should appear
            # the time depends on the game difficulty 
            for customer in self.customers:
                customer.appear()
                customer.draw(self.screen)

            # Draw the pizza
            self.pizza.appear()
            self.pizza.draw(self.screen)

            if self.pizza.is_on_screen and not self.pizza.is_done:
                self.draw_start_points()

            self.draw_star(self.screen, results)

            # draw pizza slices
            if not self.pizza.is_done:
                self.check_is_slicing()
                if self.is_slicing:
                    self.draw_line_tracker()
                    self.check_slice_completed()
                self.draw_slices()

            #check if pizza is complete
            if self.pizza.check_is_done(self.customers[0]):
                self.pizza.disappear()


            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(50) & 0xFF == ord('q'):
                print(self.score)
                break

        self.video.release()
        cv2.destroyAllWindows()
    
    
if __name__ == "__main__":        
    g = Game()
    g.run()