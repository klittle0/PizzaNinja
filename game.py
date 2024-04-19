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
        self.appear_time = time.time()
        # When the customer has been waiting a long time, set to true. 
        self.is_mad = False
        self.difficulty = difficulty

        ## The customer needs a couple dif. potential graphics. One for normal mode, another for when they are mad 

    def appear(self): 
        # TODO 
        ## add code that slides the customer into view from the edge of the screen
        return

    def leave(self):
        # TODO 
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
            #draw image[0], aka the normal image
            return



class Pizza: 
    def __init__(self): 
        self.x = 1000
        self.y = 400
        self.is_on_screen = False
        self.slices = 0 

    def appear(self): 
        # TODO
        return

    def box(self):
        # TODO 
        ## if the customer approves the pizza, put it in a box 
        ## slide it away w/ the customer 
        return

    def draw(self): 
        # TODO 
        return

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

    def draw_hand_landmarks(self, image, detection_result):
        """
        Draws all the landmarks on the hand
        Args:
            image (Image): Image to draw on
            detection_result (HandLandmarkerResult): HandLandmarker detection results
        """
        # Get a list of the landmarks
        hand_landmarks_list = detection_result.hand_landmarks
        
        # Loop through the detected hands to visualize each landmark 
        for idx in range(len(hand_landmarks_list)):
            hand_landmarks = hand_landmarks_list[idx]

            # Save the landmarks into a NormalizedLandmarkList -- normalizing the landmarks 
            hand_landmarks_proto = landmark_pb2.NormalizedLandmarkList()
            hand_landmarks_proto.landmark.extend([
            landmark_pb2.NormalizedLandmark(x=landmark.x, y=landmark.y, z=landmark.z) for landmark in hand_landmarks
            ])

            # Draw the landmarks on the hand
            DrawingUtil.draw_landmarks(image,
                                       hand_landmarks_proto,
                                       solutions.hands.HAND_CONNECTIONS,
                                       solutions.drawing_styles.get_default_hand_landmarks_style(),
                                       solutions.drawing_styles.get_default_hand_connections_style())

    
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
            frame = self.video.read()[0]

            # Convert it to an RGB image
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # the image comes mirrored - flip it 
            image = cv2.flip(image, 0)

            # Convert the image to a readable format and find the hands
            to_detect = mp.Image(image_format=mp.ImageFormat.SRGB, data=image)
            results = self.detector.detect(to_detect)

            # Draw the hand landmarks
            # Do I need this??
            self.draw_hand_landmarks(image, results)

            # Change the color of the frame back
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            cv2.imshow('Hand Tracking', image)


        self.video.release()
        cv2.destroyAllWindows()


    
    
if __name__ == "__main__":        
    g = Game()
    g.run()