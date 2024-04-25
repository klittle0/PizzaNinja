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
import pygame 


# GO THROUGH AND ADD PYGAME 
# GENERATE A WINDOW

RED = (255, 0, 0)
ANIMATION_TIME = 2
WIDTH = 2000
HEIGHT = 1000

# Library Constants
BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkPoints = mp.solutions.hands.HandLandmark
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode
DrawingUtil = mp.solutions.drawing_utils

class Customer: 
    def __init__(self, difficulty):
        self.is_on_screen = False
        self.num_slices = random.randint(1, 4) * 2
        # the instant when the customer is created
        self.appear_time = time.time()
        # When the customer has been waiting a long time, set to true. 
        self.is_mad = False
        self.difficulty = difficulty
        # CHANGE THIS to be neg SO THE character spawns off screen 
        # IS THIS POSSIBLE? 
        self.x_pos = 0
        self.y_pos = 200
        self.normal_image = cv2.imread('data/character.png', -1)
        

        ## The customer needs a couple dif. potential graphics. One for normal mode, another for when they are mad 

    ## slides the customer onto screen by shifting x coordinate
    def appear(self): 
        if time.time() - self.appear_time < ANIMATION_TIME:
            self.x_pos += 12
            

    def leave(self):
        # TODO 
        disappear_start = time.time()
        if self.x_pos > -150: 
            self.x_pos += -2
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

    def draw(self, image):
        # TODO 
        if self.is_mad: 
            # draw image[1], aka the mad image
            return
        else: 
            # Remove alpha channel from normal_image if it exists 
            # I used ChatGPT to debug this if statement 
            if self.normal_image.shape[2] == 4:
            # If the normal image has an alpha channel, apply transparency
                alpha_s = self.normal_image[:, :, 3] / 255.0
                alpha_l = 1.0 - alpha_s

                for c in range(0, 3):
                    image[self.y_pos:self.y_pos + self.normal_image.shape[0], self.x_pos:self.x_pos + self.normal_image.shape[1], c] = (alpha_s * self.normal_image[:, :, c] +
                                                    alpha_l * image[self.y_pos:self.y_pos + self.normal_image.shape[0], self.x_pos:self.x_pos + self.normal_image.shape[1], c])
            else:
            # Draw the customer image onto the frame
                image[self.y_pos:self.y_pos + self.normal_image.shape[0], self.x_pos:self.x_pos + self.normal_image.shape[1]] = self.normal_image
        return image
    

class Pizza(pygame.sprite.Sprite): 
    def __init__(self): 
        # is this line necessary? 
        super().__init__()
        # Q: I HAD TO COLOR CORRECT AWAY FROM BLUE, BUT AS A RESULT, IT MAKES THE TRANSPARENT PARTS BLACK...??
        self.image = cv2.cvtColor(cv2.imread('data/pizza.png', -1), cv2.COLOR_BGR2RGB)
        self.x_pos = WIDTH / 2 - self.image.shape[1] / 2
        self.y_pos = HEIGHT / 2 + self.image.shape[0] / 2
        self.is_on_screen = False
        self.slices = 0 
        self.appear_time = time.time()

    def appear(self): 
        if time.time() - self.appear_time < ANIMATION_TIME:
            self.y_pos -= 15

    def box(self):
        # TODO 
        ## if the customer approves the pizza, put it in a box 
        ## slide it away w/ the customer 
        return

    # image no longer needs to be a parameter
    def draw(self, image, screen): 
        # This is for the pygame version of the code: 
        screen.blit(self.image, self.x_pos, self.y_pos)


        # Remove alpha channel from normal_image if it exists 
        # I used ChatGPT to debug this if statement 
        # IMAGE APPEARS BLUE!!
        if self.image.shape[2] == 4:
        # If the normal image has an alpha channel, apply transparency
            alpha_s = self.image[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                image[self.y_pos:self.y_pos + self.image.shape[0], self.x_pos:self.x_pos + self.image.shape[1], c] = (alpha_s * self.image[:, :, c] +
                                                alpha_l * image[self.y_pos:self.y_pos + self.image.shape[0], self.x_pos:self.x_pos + self.image.shape[1], c])
        else:
        # Draw the customer image onto the frame
            image[self.y_pos:self.y_pos + self.image.shape[0], self.x_pos:self.x_pos + self.image.shape[1]] = self.image
        return image

class Game: 
    def __init__(self):
        self.difficulty = 1 
        self.score = 0
        self.is_slicing = False
        # there only need to be 2 pizzas at one time. I need to treat this like a queue 
        self.pizzas = []
        self.pizzas.append(Pizza())
        self.pizzas.append(Pizza())
        self.starting_points = []

        pygame.init()

        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Pizza Ninja')

        # generate random customer, put them in the list, then as soon as they're off screen, remove them from list. 
        self.customers = []
        self.customers.append(Customer(self.difficulty))

        # Create the hand detector
        # Sourced from Ms. Namasivayam's code in the finger tracking game 
        base_options = BaseOptions(model_asset_path='data/hand_landmarker.task')
        options = HandLandmarkerOptions(base_options=base_options,
                                                num_hands=2)
        self.detector = HandLandmarker.create_from_options(options)

        # Load video
        self.video = cv2.VideoCapture(1)

    # Draw a star on the pointer finger using hand landmarks
    def draw_star(self, image, detection_result):
        # Get image details
        imageHeight, imageWidth = image.shape[:2]

        # is the -1 necessary here? what does that do??
        star = cv2.imread('data/Star.png', -1)

        # Get a list of the landmarks
        hand_landmarks_list = detection_result.hand_landmarks
        
        # Loop through the detected hands to visualize each landmark 
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # get coordinates of just the index finger
            index_finger = hand_landmarks[HandLandmarkPoints.INDEX_FINGER_TIP.value]

            # map the finger coordinates back to screen dimensions 
            pixelCoord = DrawingUtil._normalized_to_pixel_coordinates(index_finger.x, index_finger.y, imageWidth, imageHeight)

            # here, instead, just return the coordinates, and then use them later to draw the star here w/ pygame 
            if pixelCoord:
                # draw + center the star at the coordinates of the finger
                start_x = int(pixelCoord[0] - star.shape[0] / 2) 
                start_y = int(pixelCoord[1] - star.shape[1] / 2)  
                end_x = start_x + star.shape[0]
                end_y = start_y + star.shape[1]

                # debugged with ChatGPT 
                if start_x >= 0 and start_y >= 0 and end_x <= imageWidth and end_y <= imageHeight:
                    alpha_s = star[:, :, 3] / 255.0
                    alpha_l = 1.0 - alpha_s

                # Overlay the star image onto the frame
                # FOR SOME REASON, THE STAR PRINTS BLUE...
                for c in range(0, 3):
                    image[start_y:end_y, start_x:end_x, c] = (alpha_s * star[:, :, c] +
                                                            alpha_l * image[start_y:end_y, start_x:end_x, c])


    
    def draw_start_points(self):
        # change the x & y depending on size of window 
        starting_x = 600
        starting_y = 500 
        num_slices = self.customers[0].num_slices 
        slice_angle = 360 / num_slices

        pygame.draw.circle()
        # For now, I can just draw a circle on the center of the screen that acts like the final pizza position 
        # Depending on the desired # of slices, draw start/end points around the pizza for each slice 


        # OR: The starting point can be the right-most point on the pizza. it is always the same:
        #the center of the screen + the pizza's radius for the x-coordinate 

        
        for i in range(num_slices):
            # draw a point 
            # the angle at which to draw the slice = i * slice_angle 
            # store the coordinates of the point in the self.starting_points list

            return 
        return
    
    # only call this/ if is_slicing is set to true 
    def draw_line_tracker(self):
        #Draw a line between the start point and the user's current coordinates
            # just set start x & y to the start point's coordinates
            # end x & y to the finger's coordinates
        
        return 
    


    # Identifies hand motion/change in the location of the index finger 
    def check_for_slice(self):
        # tallies the slice counter of the current pizza object
    
        # if a user touches one of points
            # AKA: If the coordinates of the user's finger make contact with any of the points around the pizza (which are stored in a list)
                # then is_slicing is set to True 
                # set the point that the user has touched to the starting point 
    
        for point in self.starting_points: 
            if _____: 
                self.is_slicing = True 
                active_point = point
    
    
        #if one of these contact points 

        # basically, a slice occurs when a user goes from touching one point to the opposite point 

        # maybe the 
    
        # if the distance that the user's finger moves before touching the opposite point is greater than the diameter, 
        # then the setting of actively tracing out a pizza slice is turned off 
        return
    
    # draws a slice on the pizza
    def draw_slice(self):
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

            # I can delete this line when I switch fully to pygame 
            # cv2.rectangle(image, (0, 0), (2000, 1200), RED, -1)

            self.screen.fill(RED)

            # # draw all customers in current positions
            # for customer in self.customers:
            #     customer.appear()
            #     customer.draw(image)

            # for pizza in self.pizzas:
            #     pizza.appear()
            #     pizza.draw(image)
            # self.draw_star(image, results)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False


            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            # cv2.imshow('Hand Tracking', image)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(50) & 0xFF == ord('q'):
                print(self.score)
                break

        self.video.release()
        cv2.destroyAllWindows()
    
    
if __name__ == "__main__":        
    g = Game()
    g.run()