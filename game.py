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

RED = (255, 0, 0)
ANIMATION_TIME = 2

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
        self.slices_wanted = random.randint(1, 4) * 2
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
    

class Pizza: 
    def __init__(self): 
        self.x_pos = 400
        self.y_pos = 700
        self.is_on_screen = False
        self.slices = 0 
        self.appear_time = time.time()
        # Q: I HAD TO COLOR CORRECT AWAY FROM BLUE, BUT AS A RESULT, IT MAKES THE TRANSPARENT PARTS BLACK...??
        self.image = self.normal_image = cv2.cvtColor(cv2.imread('data/pizza.png', -1), cv2.COLOR_BGR2RGB)

    def appear(self): 
        if time.time() - self.appear_time < ANIMATION_TIME:
            self.y_pos -= 15

    def box(self):
        # TODO 
        ## if the customer approves the pizza, put it in a box 
        ## slide it away w/ the customer 
        return

    def draw(self, image): 
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
        # there only need to be 2 pizzas at one time. I need to treat this like a queue 
        self.pizzas = []
        self.pizzas.append(Pizza())
        self.pizzas.append(Pizza())

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
        self.video = cv2.VideoCapture(0)

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
        # Depending on the desired # of slices, draw start/end points around the pizza for each slice 
        return 

    # Identifies hand motion/change in the location of the index finger 
    def check_for_slice(self):
        return
        # tallies the slice counter of the current pizza object
    
    # draws a slice on the pizza
    def draw_slice(self):
        return
    
    # Main game loop 
    def run(self): 
        """
        Main game loop. Runs until the 
        user presses "q".
        """  
        # How to do this without actually opening the video? 
        while self.video.isOpened():
            # Get the current frame
            frame = self.video.read()[1]

            # Convert it to an RGB image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # the image comes mirrored - flip it 
            image = cv2.flip(image, 1)

            # Convert the image to a readable format and find the hands
            to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            results = self.detector.detect(to_detect)

            cv2.rectangle(image, (0, 0), (2000, 1200), RED, -1)

            # draw all customers in current positions
            for customer in self.customers:
                customer.appear()
                customer.draw(image)

            for pizza in self.pizzas:
                pizza.appear()
                pizza.draw(image)
            self.draw_star(image, results)


            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imshow('Hand Tracking', image)

            # Break the loop if the user presses 'q'
            if cv2.waitKey(50) & 0xFF == ord('q'):
                print(self.score)
                break

        self.video.release()
        cv2.destroyAllWindows()
    
    
if __name__ == "__main__":        
    g = Game()
    g.run()