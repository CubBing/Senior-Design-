import cv2
import mediapipe as mp
import numpy as np
import pyttsx3
import os
import platform
import tempfile
import subprocess
import time


# Initialize mediapipe pose class and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()


# Initialize text-to-speech engine
engine = pyttsx3.init()
engine.setProperty('rate', 120)  # Set the speed of the speech
engine.setProperty('voice', engine.getProperty('voices')[1].id)  # Set a different voice if available


# Function to calculate angle between three points
def calculate_angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


# Function to convert text to speech seamlessly
def text_to_speech(text):
    engine.say(text)
    engine.runAndWait()


# Function to draw text with a shadow for better visibility
def put_text_with_shadow(img, text, position, font_scale, color, shadow_color, thickness=2):
    x, y = position
    # Draw shadow
    cv2.putText(img, text, (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, shadow_color, thickness, cv2.LINE_AA)
    # Draw main text
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)


# Function to display the introduction screen 
def display_intro():
    global selected_workout
    selected_workout = None

    # Load and resize the background image
    background = cv2.imread('Fitness-Background.jpg')  
    if background is None:
        print("Error: Could not load background image.")
        return
    
    background = cv2.resize(background, (800, 600))

    # Apply a fading effect to the background image
    alpha = 0.3  # Transparency factor (0.0 to 1.0)
    faded_background = cv2.addWeighted(background, alpha, background, 1 - alpha, 0)

    # Display welcome text with shadow
    put_text_with_shadow(faded_background, 'Welcome to AI Fitness Coach', (90, 150), 1.5, (255, 255, 255), (0, 0, 0), 3)
    put_text_with_shadow(faded_background, 'Press a key to select your workout', (120, 300), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(faded_background, '1: Pushups  2: Squats  3: Bicep Curl', (100, 400), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(faded_background, '4: Lunges  5: Overhead Dumbbell Press', (100, 450), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(faded_background, '4: Lunges  5: Overhead Dumbbell Press', (100, 450), 1, (255, 255, 255), (0, 0, 0), 2)


    # Display the introduction screen
    cv2.imshow('Intro', faded_background)
    key = cv2.waitKey(0)
    if key == ord('1'):
        selected_workout = "pushups"
    elif key == ord('2'):
        selected_workout = "squats"
    elif key == ord('3'):
        selected_workout = "bicep curl"
    elif key == ord('4'):
        selected_workout = "lunges"
    elif key == ord('5'):
        selected_workout = "overhead dumbbell press"
    
    if selected_workout:
        cv2.destroyAllWindows()





def detect_squats(landmarks, frame, count, stage):
    # Get coordinates for hips, knees, and ankles
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

    # Calculate the angles at the knees
    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

    # Visualize the angles
    put_text_with_shadow(frame, str(int(left_knee_angle)), tuple(np.multiply(left_knee, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, str(int(right_knee_angle)), tuple(np.multiply(right_knee, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)

    # Check for squat stages based on knee angles
    if left_knee_angle > 130 and right_knee_angle > 130:
        stage = "up"
    if left_knee_angle < 110 and right_knee_angle < 110 and stage == "up":
        stage = "down"
        count += 1
        text_to_speech("Good squat!")

    # --- Implementing Coaching Feedback ---
    # 1. Knee Alignment: Ensure knees track over toes
    if abs(left_knee[0] - left_ankle[0]) > 0.1 or abs(right_knee[0] - right_ankle[0]) > 0.1:
        put_text_with_shadow(frame, "Align knees with toes!", (50, 200), 1, (0, 0, 255), (0, 0, 0), 2)

    # 2. Depth: Ensure proper squat depth
    if left_knee_angle > 120 or right_knee_angle > 120:
        put_text_with_shadow(frame, "Go lower for a full squat!", (50, 250), 1, (0, 0, 255), (0, 0, 0), 2)

    # 3. Back Position: Avoid leaning forward excessively
    if left_hip[1] > left_knee[1] or right_hip[1] > right_knee[1]:
        put_text_with_shadow(frame, "Keep your back straight!", (50, 300), 1, (0, 0, 255), (0, 0, 0), 2)

    # Display squat count
    put_text_with_shadow(frame, f'Squat Count: {count}', (50, 50), 1, (255, 255, 255), (0, 0, 0), 2)


    return count, stage




# Function for bicep curl detection
def detect_bicep_curls(landmarks, frame, left_count, right_count, left_stage, right_stage):
    # Get coordinates for left and right shoulders, elbows, and wrists
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    # Calculate the angles at the elbows
    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    # Visualize the angles
    put_text_with_shadow(frame, str(int(left_elbow_angle)), tuple(np.multiply(left_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, str(int(right_elbow_angle)), tuple(np.multiply(right_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)

    # --- Implementing Form Corrections ---

    # 1. Elbow Position: Ensure elbows stay close to the torso
    if landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x > landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x + 0.1 or \
       landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x > landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x + 0.1:
        put_text_with_shadow(frame, "Keep your elbows close to your body!", (50, 150), 1, (0, 0, 255), (0, 0, 0), 2)

    # 2. Back Stability: Avoid swinging the torso
    if abs(landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x - landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x) > 0.1 or \
       abs(landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x - landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x) > 0.1:
        put_text_with_shadow(frame, "Avoid swinging; keep your back straight!", (50, 200), 1, (0, 0, 255), (0, 0, 0), 2)

    # 3. Full Range of Motion: Ensure arm is fully extended at the bottom
    if left_elbow_angle > 160 and right_elbow_angle > 160:  # This assumes full extension is above 160 degrees
        put_text_with_shadow(frame, "Lower your arm fully between reps!", (50, 250), 1, (0, 0, 255), (0, 0, 0), 2)

    # 4. Shoulder Engagement: Shoulders should remain stable and not rise
    #if landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y < landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y - 0.05 or \
    #   landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y < landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y - 0.05:
    #    put_text_with_shadow(frame, "Keep your shoulders relaxed!", (50, 300), 1, (0, 0, 255), (0, 0, 0), 2)

    # 5. Wrist Position: Ensure wrists stay straight
    if abs(landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x - landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x) > 0.05 or \
       abs(landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x - landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x) > 0.05:
        put_text_with_shadow(frame, "Keep your wrists straight!", (50, 350), 1, (0, 0, 255), (0, 0, 0), 2)

    # Check for left arm curl stages
    if left_elbow_angle > 160:
        left_stage = "down"
    if left_elbow_angle < 50 and left_stage == "down":
        left_stage = "up"
        left_count += 1

    # Check for right arm curl stages
    if right_elbow_angle > 160:
        right_stage = "down"
    if right_elbow_angle < 50 and right_stage == "down":
        right_stage = "up"
        if left_stage != "up":
            right_count += 1

    # Display curl counts
    put_text_with_shadow(frame, f'Left Curl Count: {left_count}', (50, 50), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, f'Right Curl Count: {right_count}', (50, 100), 1, (255, 255, 255), (0, 0, 0), 2)

    return left_count, right_count, left_stage, right_stage





# Placeholder functions for other exercise detection



# function for pushup detection
def detect_pushups(landmarks, frame, count, stage):
    # Get coordinates for shoulders, elbows, and wrists
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    # Calculate the angles at the elbows
    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    # Visualize the angles
    put_text_with_shadow(frame, str(int(left_elbow_angle)), tuple(np.multiply(left_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, str(int(right_elbow_angle)), tuple(np.multiply(right_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)

    # Check for pushup stages
    if left_elbow_angle > 160 and right_elbow_angle > 160:
        stage = "up"
    elif left_elbow_angle < 90 and right_elbow_angle < 90 and stage == "up":
        stage = "down"
        count += 1
        put_text_with_shadow(frame, "Good pushup!", (50, 150), 1, (0, 255, 0), (0, 0, 0), 2)
    else:
        # Provide feedback on the screen if the user is not doing the push-up correctly
        if left_elbow_angle > 90 or right_elbow_angle > 90:
            put_text_with_shadow(frame, "Go lower!", (50, 150), 1, (0, 0, 255), (0, 0, 0), 2)
        if left_elbow_angle < 90 and right_elbow_angle < 90 and left_shoulder[1] > left_wrist[1] and right_shoulder[1] > right_wrist[1]:
            put_text_with_shadow(frame, "Keep your back straight!", (50, 200), 1, (0, 0, 255), (0, 0, 0), 2)
    
    # Display pushup count
    put_text_with_shadow(frame, f'Pushup Count: {count}', (50, 50), 1, (255, 255, 255), (0, 0, 0), 2)

    return count, stage




def detect_overhead_dumbbell_press(landmarks, frame, count, stage):
    # Get coordinates for shoulders, elbows, and wrists
    left_shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    left_elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    left_wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]

    right_shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
    right_elbow = [landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW.value].y]
    right_wrist = [landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_WRIST.value].y]

    # Calculate the angles at the elbows
    left_elbow_angle = calculate_angle(left_shoulder, left_elbow, left_wrist)
    right_elbow_angle = calculate_angle(right_shoulder, right_elbow, right_wrist)

    # Visualize the angles
    put_text_with_shadow(frame, str(int(left_elbow_angle)), tuple(np.multiply(left_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, str(int(right_elbow_angle)), tuple(np.multiply(right_elbow, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)

    # Check for overhead position (wrists above shoulders)
    if left_wrist[1] < left_shoulder[1] and right_wrist[1] < right_shoulder[1]:
        # Check for press stages
        if left_elbow_angle > 160 and right_elbow_angle > 160 and stage != "up":
            stage = "up"
        elif left_elbow_angle < 100 and right_elbow_angle < 100 and stage == "up":
            stage = "down"
            count += 1
            text_to_speech("Good overhead press!")
    else:
        # Reset stage if wrists are not overhead to avoid incorrect counting
        stage = None

    # --- Implementing Coaching Feedback ---
    # 1. Wrist Alignment: Wrists must be straight
    if abs(left_wrist[0] - left_elbow[0]) > 0.1 or abs(right_wrist[0] - right_elbow[0]) > 0.1:
        put_text_with_shadow(frame, "Keep your wrists straight!", (50, 150), 1, (0, 0, 255), (0, 0, 0), 2)

    # 2. Don't Drop Arms: Only if arms are below halfway
    halfway_line = (left_shoulder[1] + right_shoulder[1]) / 2
    if left_wrist[1] > halfway_line and right_wrist[1] > halfway_line:
        put_text_with_shadow(frame, "Don't drop your arms!", (50, 200), 1, (0, 0, 255), (0, 0, 0), 2)

    # 3. Fully Extend Arms: Only if arms are halfway up or above
    if left_wrist[1] <= halfway_line or right_wrist[1] <= halfway_line:
        if left_elbow_angle < 160 or right_elbow_angle < 160:
            put_text_with_shadow(frame, "Fully extend your arms!", (50, 250), 1, (0, 0, 255), (0, 0, 0), 2)

    # 4. Back Posture: Avoid leaning backward
    if abs(landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x - left_shoulder[0]) > 0.1 or \
       abs(landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x - right_shoulder[0]) > 0.1:
        put_text_with_shadow(frame, "Maintain a straight back!", (50, 300), 1, (0, 0, 255), (0, 0, 0), 2)

    # Display press count
    put_text_with_shadow(frame, f'Press Count: {count}', (50, 50), 1, (255, 255, 255), (0, 0, 0), 2)

    return count, stage









# Function for lunge detection with coaching feedback
def detect_lunges(landmarks, frame, left_count, right_count, left_stage, right_stage):
    # Get coordinates for hips, knees, and ankles for both legs
    left_hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    left_knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    left_ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]

    right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
    right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
    right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]

    # Calculate the angles at the knees
    left_knee_angle = calculate_angle(left_hip, left_knee, left_ankle)
    right_knee_angle = calculate_angle(right_hip, right_knee, right_ankle)

    # Visualize the angles
    put_text_with_shadow(frame, str(int(left_knee_angle)), tuple(np.multiply(left_knee, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, str(int(right_knee_angle)), tuple(np.multiply(right_knee, [frame.shape[1], frame.shape[0]]).astype(int)), 1, (255, 255, 255), (0, 0, 0), 2)

    # Check for lunge stages
    if left_knee_angle > 160 and right_knee_angle < 110:
        right_stage = "down"
    elif right_knee_angle > 160 and left_knee_angle < 110:
        left_stage = "down"
    elif left_knee_angle > 160 and right_knee_angle > 160:
        if right_stage == "down":
            right_count += 1
            text_to_speech("Good right lunge!")
            right_stage = None
        if left_stage == "down":
            left_count += 1
            text_to_speech("Good left lunge!")
            left_stage = None

    # Coaching feedback for lunges
    # 1. Knee Position
    if left_knee[0] > left_ankle[0] + 0.05 or right_knee[0] > right_ankle[0] + 0.05:
        put_text_with_shadow(frame, "Avoid letting your knee go past your toes!", (50, 200), 1, (0, 0, 255), (0, 0, 0), 2)

    # 3. Back Leg Form
    if left_knee_angle < 70 or right_knee_angle < 70:
        put_text_with_shadow(frame, "Lower your back knee toward the ground!", (50, 250), 1, (0, 0, 255), (0, 0, 0), 2)

    # 4. Torso Stability
    if abs(left_hip[0] - left_knee[0]) > 0.1 or abs(right_hip[0] - right_knee[0]) > 0.1:
        put_text_with_shadow(frame, "Keep your torso upright; avoid leaning forward!", (50, 300), 1, (0, 0, 255), (0, 0, 0), 2)

    # Display lunge counts
    put_text_with_shadow(frame, f'Right Lunge Count: {right_count}', (50, 50), 1, (255, 255, 255), (0, 0, 0), 2)
    put_text_with_shadow(frame, f'Left Lunge Count: {left_count}', (50, 100), 1, (255, 255, 255), (0, 0, 0), 2)
    
    return left_count, right_count, left_stage, right_stage






# Countdown function for the 5-second grace period
def countdown(frame, seconds=5):
    height, width = frame.shape[:2]  # Get the frame dimensions
    for i in range(seconds, 0, -1):
        # Clear the frame
        frame_copy = frame.copy()  # Copy the frame to clear previous text

        # Calculate text size and position for centering
        text = f'Starting in {i}'
        text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
        text_x = (width - text_size[0]) // 2
        text_y = (height + text_size[1]) // 2

        # Display the countdown text on the center of the frame
        put_text_with_shadow(frame_copy, text, (text_x, text_y), 2, (255, 255, 255), (0, 0, 0), 3)
        
        # Show the frame with the countdown number
        cv2.imshow('Fitness Coach', frame_copy)
        cv2.waitKey(1000)  # Wait for 1 second
        
        # Announce the countdown
        text_to_speech(str(i))

    # Display "Starting now!" message
    frame_copy = frame.copy()  # Clear frame again for "Starting now!" text
    text = 'Starting now!'
    text_size = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
    text_x = (width - text_size[0]) // 2
    text_y = (height + text_size[1]) // 2
    put_text_with_shadow(frame_copy, text, (text_x, text_y), 2, (0, 255, 0), (0, 0, 0), 3)
    cv2.imshow('Fitness Coach', frame_copy)
    cv2.waitKey(1000)  # Display "Starting now!" for a second
    text_to_speech("Starting now!")











# Main function to handle the exercise detection
def main():
    global selected_workout
    
    # Display intro screen
    display_intro()
    if selected_workout is None:
        print("No workout selected. Exiting...")
        return

    # Start capturing video
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    pushup_count = 0
    pushup_stage = None
    
    squat_count = 0
    squat_stage = None
    
    left_curl_count = 0
    right_curl_count = 0
    left_curl_stage = None
    right_curl_stage = None
    both_curl_count = 0
    
    left_lunge_count = 0
    right_lunge_count = 0
    left_lunge_stage = None
    right_lunge_stage = None

    # Define the current exercise
    current_exercise = selected_workout





    # Capture the initial frame for countdown
    ret, frame = cap.read()
    if ret:
        countdown(frame)  # 5-second countdown before starting the workout





    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read from camera.")
            break

               

        # Recolor the image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

       
        
        
        # Process the frame with Mediapipe Pose
        results = pose.process(rgb_frame)

        # Check if landmarks are detected
        if results.pose_landmarks:
            
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

            landmarks = results.pose_landmarks.landmark
            
            # Call the function based on the current exercise
            if current_exercise == "pushups":
                pushup_count, pushup_stage = detect_pushups(landmarks, frame, pushup_count, pushup_stage)
            elif current_exercise == "squats":
                squat_count, squat_stage = detect_squats(landmarks, frame, squat_count, squat_stage)
            elif current_exercise == "bicep curl":
                left_curl_count, right_curl_count, left_curl_stage, right_curl_stage = detect_bicep_curls(landmarks, frame, left_curl_count, right_curl_count, left_curl_stage, right_curl_stage)
            elif current_exercise == "lunges":
                left_lunge_count, right_lungeF_count, left_lunge_stage, right_lunge_stage = detect_lunges(landmarks, frame, left_lunge_count, right_lunge_count, left_lunge_stage, right_lunge_stage)
            elif current_exercise == "overhead dumbbell press":
                squat_count, squat_stage = detect_overhead_dumbbell_press(landmarks, frame, squat_count, squat_stage)
        else:
            print("No landmarks detected. Please adjust your position.")

        # Display frame
        cv2.imshow('Fitness Coach', frame)

        # Exit condition
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
	