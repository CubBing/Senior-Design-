import cv2
import mediapipe as mp
import numpy as np
import speech_recognition as sr
from gtts import gTTS
import os

# Initialize mediapipe pose class and drawing utilities
mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
pose = mp_pose.Pose()

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

# Function to convert text to speech
def text_to_speech(text):
    language = 'en'
    output = gTTS(text=text, lang=language, slow=False)
    output_file = "output.mp3"
    output.save(output_file)
    os.system(f"start {output_file}")  # On Windows, this will play the audio.
    os.remove(output_file)

# Function to draw text with a shadow for better visibility
def put_text_with_shadow(img, text, position, font_scale, color, shadow_color, thickness=2):
    x, y = position
    # Draw shadow
    cv2.putText(img, text, (x + 2, y + 2), cv2.FONT_HERSHEY_SIMPLEX, font_scale, shadow_color, thickness, cv2.LINE_AA)
    # Draw main text
    cv2.putText(img, text, position, cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness, cv2.LINE_AA)

# Function to display the introduction screen without border or oval
def display_intro():
    global selected_workout
    selected_workout = None

    # Load and resize the background image
    background = cv2.imread('Fitness-Background.jpg')  
    background = cv2.resize(background, (800, 600))

    # Apply a fading effect to the background image
    alpha = 0.3  # Transparency factor (0.0 to 1.0)
    faded_background = cv2.addWeighted(background, alpha, background, 1 - alpha, 0)

    # Display welcome text with shadow
    put_text_with_shadow(faded_background, 'Welcome to AI Fitness Coach', (90, 150), 1.5, (255, 255, 255), (0, 0, 0), 3)

    # Display instruction text
    put_text_with_shadow(faded_background, 'Please select the workout you wish to do:', (50, 250), 1, (255, 255, 255), (0, 0, 0), 2)

    # Draw buttons with different colors and rounded corners
    button_color_curl = (144, 238, 144)  # Light green
    button_color_squat = (135, 206, 250)  # Light blue
    button_color_lunge = (250, 206, 135)  # Light orange
    button_color_pushup = (238, 144, 144)  # Light red
    
    # Create buttons for different workouts
    cv2.rectangle(faded_background, (100, 400), (300, 450), button_color_curl, -1, cv2.LINE_AA)  # Bicep Curl
    cv2.rectangle(faded_background, (100, 500), (300, 550), button_color_squat, -1, cv2.LINE_AA)  # Squat
    cv2.rectangle(faded_background, (400, 400), (600, 450), button_color_pushup, -1, cv2.LINE_AA)  # Pushup
    cv2.rectangle(faded_background, (400, 500), (600, 550), button_color_lunge, -1, cv2.LINE_AA)  # Lunge

    # Display button text
    put_text_with_shadow(faded_background, 'Bicep Curl', (130, 430), 0.8, (0, 0, 0), (255, 255, 255), 2)
    put_text_with_shadow(faded_background, 'Squat', (180, 530), 0.8, (0, 0, 0), (255, 255, 255), 2)
    put_text_with_shadow(faded_background, 'Pushup', (430, 430), 0.8, (0, 0, 0), (255, 255, 255), 2)
    put_text_with_shadow(faded_background, 'Lunge', (450, 530), 0.8, (0, 0, 0), (255, 255, 255), 2)


    # Set up the OpenCV window
    cv2.namedWindow('Introduction')
    cv2.setMouseCallback('Introduction', select_workout)

    while selected_workout is None:
        cv2.imshow('Introduction', faded_background)
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break

    cv2.destroyWindow('Introduction')

# Function to handle mouse clicks for selecting workouts
def select_workout(event, x, y, flags, param):
    global selected_workout
    if event == cv2.EVENT_LBUTTONDOWN:
        if 100 < x < 300 and 400 < y < 450:
            selected_workout = 'bicep curl'
        elif 100 < x < 300 and 500 < y < 550:
            selected_workout = 'squat'
        elif 400 < x < 600 and 400 < y < 450:
            selected_workout = 'pushups'
        elif 400 < x < 600 and 500 < y < 550:
            selected_workout = 'lunges'

# Function to detect push-ups
def detect_pushups(landmarks, frame, pushup_count, stage):
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    
    # Calculate elbow angle
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    
    # Check hip position (for form correction)
    form_correct = True
    if hip[1] < shoulder[1] - 0.05:
        form_correct = False
        text_to_speech(f"Lower your hips")
    if hip[1] > shoulder[1] + 0.05:
        form_correct = False
        text_to_speech(f"Raise your hips")
    
    # Push-up logic
    if elbow_angle > 160 and form_correct:
        stage = "up"
    if elbow_angle < 90 and stage == "up" and form_correct:
        stage = "down"
        pushup_count += 1

    # Display push-up count
    cv2.putText(frame, f'Push-ups: {pushup_count}', (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    text_to_speech({pushup_count})
    
    return pushup_count, stage

# Function to detect squats
def detect_squats(landmarks, frame, squat_count, stage):
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, 
           landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, 
            landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, 
             landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    ear = [landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].x, 
           landmarks[mp_pose.PoseLandmark.LEFT_EAR.value].y]

    # Calculate angles
    knee_angle = calculate_angle(hip, knee, ankle)  # Knee angle for squat depth
    torso_angle = calculate_angle(hip, shoulder, ear)  # Torso angle to check forward lean

    # Form correction flags
    form_correct = True

    # Check for not going low enough (knee angle > 90)
    if knee_angle > 90:
        form_correct = False
        text_to_speech(f"Go lower")

    # Check for leaning forward too much (torso angle < 75)
    if torso_angle < 75:
        form_correct = False
        text_to_speech(f"Keep your torso upright")

    # Squat logic: count rep when knee angle goes below 90 and form is correct
    if knee_angle > 160:
        stage = "up"
    if knee_angle < 90 and stage == "up" and form_correct:
        stage = "down"
        squat_count += 1

    # Display squat count
    cv2.putText(frame, f'Squats: {squat_count}', (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    text_to_speech({squat_count})
    
    return squat_count, stage

def detect_bicep_curls(landmarks, frame, curl_count, stage):
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, 
                landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]
    elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x, 
             landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
    wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x, 
             landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
    
    # Calculate elbow angle (bicep curl)
    elbow_angle = calculate_angle(shoulder, elbow, wrist)
    
    # Form correction flags
    form_correct = True

    # Full range of motion (extension and flexion)
    if elbow_angle > 160:  # Elbow extended
        stage = "down"
    if elbow_angle < 50 and stage == "down":  # Elbow fully flexed
        stage = "up"
        curl_count += 1
    
    # Check if elbow moves too much vertically (stability)
    if abs(shoulder[1] - elbow[1]) > 0.05:  # Example threshold for stability
        form_correct = False
        text_to_speech(f"Keep elbows stable")
    
    # Display bicep curl count
    cv2.putText(frame, f'Bicep Curls: {curl_count}', (50, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)
    text_to_speech({curl_count})

    return curl_count, stage

# Function to detect lunges
def detect_lunges(landmarks, frame, lunge_count, stage):
    hip = [landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].x, landmarks[mp_pose.PoseLandmark.LEFT_HIP.value].y]
    knee = [landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_KNEE.value].y]
    ankle = [landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.LEFT_ANKLE.value].y]
    shoulder = [landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x, landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y]

    # Calculate angles
    knee_angle = calculate_angle(hip, knee, ankle)  # Knee angle for lunge depth
    hip_angle = calculate_angle(shoulder, hip, knee)  # Hip angle to ensure posture

    # Form correction flags
    form_correct = True

    # Check for not going low enough (knee angle > 90)
    if knee_angle > 90:
        form_correct = False
        cv2.putText(frame, "Go lower", (50, 100), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Check for hip position (hip should not bend too far forward)
    if hip_angle < 160:
        form_correct = False
        cv2.putText(frame, "Keep your hips straight", (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)

    # Lunge logic: count when knee angle goes below 90 and form is correct
    if knee_angle > 160:
        stage = "up"
    if knee_angle < 90 and stage == "up" and form_correct:
        stage = "down"
        lunge_count += 1

    # Display lunge count
    cv2.putText(frame, f'Lunges: {lunge_count}', (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    return lunge_count, stage

def main():
   
    display_intro()  # Show introduction screen
    if selected_workout is None:
        print("No valid workout selected. Exiting.")
        return
    cap = cv2.VideoCapture(0)

    # Variables for push-ups and squats
    pushup_count = 0
    pushup_stage = None

    squat_count = 0
    squat_stage = None
    
    curl_count = 0
    curl_stage = None
    
    lunge_count = 0
    lunge_stage = None

    # Define the current exercise (pushups by default)
    current_exercise = selected_workout  # You can change this dynamically

    while cap.isOpened():
        ret, frame = cap.read()
        
        # Recolor the image to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = pose.process(rgb_frame)

        # Draw pose landmarks
        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            
            landmarks = results.pose_landmarks.landmark
            
            # Call the function based on the current exercise
            if current_exercise == "pushups":
                pushup_count, pushup_stage = detect_pushups(landmarks, frame, pushup_count, pushup_stage)
            elif current_exercise == "squats":
                squat_count, squat_stage = detect_squats(landmarks, frame, squat_count, squat_stage)
            elif current_exercise =="bicep curl":
                curl_count, curl_stage = detect_bicep_curls(landmarks, frame, curl_count, curl_stage)
            elif current_exercise == "lunges":
                lunge_count, lunge_stage = detect_lunges(landmarks, frame, lunge_count, lunge_stage)

        cv2.imshow('Fitness Coach', frame)

        # Switch between exercises using keys
        key = cv2.waitKey(10) & 0xFF
        if key == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
    