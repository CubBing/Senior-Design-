import 'package:flutter/material.dart';
import 'package:video_player/video_player.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:flutter/cupertino.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'AI Fitness',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: SplashScreen(),
    );
  }
}

class SplashScreen extends StatefulWidget {
  @override
  _SplashScreenState createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  // Check if the user has logged in previously
  Future<void> _checkLoginStatus() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();
    bool? isLoggedIn = prefs.getBool('isLoggedIn') ?? false;

    // Delay for the splash effect and then navigate
    await Future.delayed(Duration(seconds: 2)); // Optional splash delay

    if (isLoggedIn) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => HomePage()),
      );
    } else {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => LoginPage()),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey, // Set the splash screen background color
      body: Center(
        child: ClipOval(
          child: Image.asset(
            'asssets/images/splash_logo.png',
            width: 200,
            height: 200,
            fit: BoxFit.contain,
          ), // Splash screen while checking login
        )
      ),
    );
  }
}

class LoginPage extends StatefulWidget {
  @override
  _LoginPageState createState() => _LoginPageState();
}

class _LoginPageState extends State<LoginPage> {
  int _selectedWeight = 60;  // Default weight
  int _selectedHeight = 170; // Default height
  int _selectedAge = 25;     // Default age

  Future<void> _saveUserData() async {
    SharedPreferences prefs = await SharedPreferences.getInstance();

    // Save user data in SharedPreferences
    await prefs.setInt('weight', _selectedWeight);
    await prefs.setInt('height', _selectedHeight);
    await prefs.setInt('age', _selectedAge);
    await prefs.setBool('isLoggedIn', true);

    // Navigate to the Welcome Page
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => HomePage()),
    );
  }

  // Function to show the scroll wheel picker
  void _showPicker(BuildContext context, int initialValue, int min, int max, Function(int) onSelectedItemChanged) {
    showModalBottomSheet(
      context: context,
      builder: (context) {
        return Container(
          height: 300,
          child: CupertinoPicker(
            backgroundColor: Colors.white,
            itemExtent: 32.0, // Height of each item in the picker
            scrollController: FixedExtentScrollController(initialItem: initialValue - min),
            onSelectedItemChanged: onSelectedItemChanged,
            children: List<Widget>.generate(max - min + 1, (index) {
              return Center(child: Text('${min + index}'));
            }),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey,
      appBar: AppBar(title: Text("Let's learn more about you!")),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Weight Picker
            ListTile(
              title: Text(
                  "Weight: $_selectedWeight kg",
                  style: TextStyle(
                    fontSize: 18, // Increase font size
                    fontWeight: FontWeight.bold, // Make text bold
                  ),
              ),
              trailing: Icon(Icons.arrow_drop_down),
              onTap: () {
                _showPicker(context, _selectedWeight, 30, 200, (int newValue) {
                  setState(() {
                    _selectedWeight = newValue + 30;  // Adjust according to min value
                  });
                });
              },
            ),

            // Height Picker
            ListTile(
              title: Text(
                  "Height: $_selectedHeight cm",
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  )
              ),
              trailing: Icon(Icons.arrow_drop_down),
              onTap: () {
                _showPicker(context, _selectedHeight, 100, 250, (int newValue) {
                  setState(() {
                    _selectedHeight = newValue + 100;  // Adjust according to min value
                  });
                });
              },
            ),

            // Age Picker
            ListTile(
              title: Text(
                  "Age: $_selectedAge years",
                  style: TextStyle(
                    fontSize: 18, // Increase font size
                    fontWeight: FontWeight.bold, // Make text bold
                  ),
              ),
              trailing: Icon(Icons.arrow_drop_down),
              onTap: () {
                _showPicker(context, _selectedAge, 10, 100, (int newValue) {
                  setState(() {
                    _selectedAge = newValue + 10;  // Adjust according to min value
                  });
                });
              },
            ),

            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _saveUserData,
              child: Text("Submit"),
            ),
          ],
        ),
      ),
    );
  }
}

class HomePage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.blueGrey,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Red box with cut edges
            Container(
              width: 300,
              height: 150,
              decoration: BoxDecoration(
                color: Colors.blue[200],
                borderRadius: BorderRadius.only(
                  topLeft: Radius.circular(40),
                  topRight: Radius.circular(40),
                  bottomLeft: Radius.circular(40),
                  bottomRight: Radius.circular(40),
                ),
              ),
              child: Center(
                child: Text(
                  'Welcome to AI Fitness',
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontSize: 24,
                    color: Colors.white,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ),
            SizedBox(height: 30), // Spacer
            ElevatedButton(
              onPressed: () {
                // Navigate to Workout Page
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => WorkoutPage()),
                );
              },
              child: Text('Start Workout'),
            ),
            ElevatedButton(
              onPressed: () async {
                SharedPreferences prefs = await SharedPreferences.getInstance();
                prefs.setBool('isLoggedIn', false); // Clear login state

                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (context) => LoginPage()),
                );
              },
              child: Text("Logout"),
            ),
          ],
        ),
      ),
    );
  }
}

class WorkoutPage extends StatelessWidget {
  final List<Map<String, dynamic>> workouts = [
    {
      'name': 'Squat',
      'videoUrl': 'asssets/videos/squat.mp4',
      'primaryGroup': 'asssets/images/squat.png',
      'secondGroup': 'asssets/images/squat2.png',
      'steps': [
        'Stand with feet shoulder-width apart.',
        'Lower your body by bending your knees and hips.',
        'Keep your back straight and your chest up.',
        'Go down until your thighs are parallel to the floor.',
        'Push through your heels to return to the starting position.'
      ],
    },

    {
      'name': 'Push-up',
      'videoUrl': 'asssets/videos/pushup.mp4',
      'primaryGroup': 'asssets/images/pushup.png',
      'secondGroup': 'asssets/images/pushup2.png',
      'steps': [
        'Start in a plank position with your hands slightly wider than shoulder-width.',
        'Lower your body until your chest nearly touches the floor.',
        'Keep your body in a straight line from head to toe.',
        'Push yourself back to the starting position.'
      ],
    },

    {
      'name': 'Lunge',
      'videoUrl': 'asssets/videos/lunges.mp4',
      'primaryGroup': 'asssets/images/lunges.png',
      'secondGroup': 'asssets/images/lunges2.png',
      'steps': [
        'Stand tall with feet together.',
        'Step forward with one leg, lowering your hips until both knees are bent at 90 degrees.',
        'Keep your front knee over your ankle.',
        'Push through your heel to return to the starting position.'
      ],
    },

    {
      'name': 'Bicep Curls',
      'videoUrl': 'asssets/videos/bicepcurl.mp4',
      'primaryGroup': 'asssets/images/bicepcurl.png',
      'secondGroup': 'asssets/images/bicepcurl2.png',
      'steps': [
        'Stand with feet shoulder-width apart, holding a dumbbell in each hand.',
        'Keep your elbows close to your torso and curl the weights to shoulder level.',
        'Lower the weights back down in a controlled motion.',
        'Repeat the movement for the desired number of repetitions.'
      ],
    },

    {
      'name': 'Overhead Press',
      'videoUrl': 'asssets/videos/overheadpress.mp4',
      'primaryGroup': 'asssets/images/overheadpress.png',
      'secondGroup': 'asssets/images/overheadpress2.png',
      'steps': [
        'Stand with feet shoulder-width apart, holding a barbell at shoulder height.',
        'Press the barbell overhead until your arms are fully extended.',
        'Lower the barbell back to shoulder height in a controlled motion.',
        'Keep your core tight throughout the movement.'
      ],
    },

    {
      'name': 'Sit-ups',
      'videoUrl': 'asssets/videos/situps.mp4',
      'primaryGroup': 'asssets/images/situps.png',
      'secondGroup': 'asssets/images/situps2.png',
      'steps': [
        'Lie on your back with your knees bent and feet flat on the floor.',
        'Cross your arms over your chest or place them behind your head.',
        'Lift your upper body towards your knees by contracting your abs.',
        'Lower your body back down to the starting position.'
      ],
    },

  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.deepPurple[200],
      appBar: AppBar(
        title: Text('Select a Workout'),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: workouts.map((workout) {
              return Padding(
                padding: const EdgeInsets.symmetric(vertical: 8.0),
                child: SizedBox(
                  width: 250, // Set the width for all buttons
                  child: ElevatedButton(
                    style: ElevatedButton.styleFrom(
                      padding: EdgeInsets.symmetric(vertical: 16.0),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(30.0), // Rounded corners
                      ),
                      backgroundColor: Colors.deepPurple, // Background color
                      foregroundColor: Colors.white, // Text color
                    ),
                    onPressed: () {
                      // Navigate to the VideoPage
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => VideoPage(
                            workoutName: workout['name']!,
                            videoAsset: workout['videoUrl']!,
                            primaryMuscleImage: workout['primaryGroup']!,
                            secondaryMuscleImage: workout['secondGroup']!,
                            steps: workout['steps']!,
                          ),
                        ),
                      );
                    },
                    child: Text(
                      workout['name']!,
                      style: TextStyle(fontSize: 18),
                    ),
                  ),
                ),
              );
            }).toList(),
          ),
        ),
      ),
    );
  }
}

class VideoPage extends StatefulWidget {
  final String workoutName;
  final String videoAsset;
  final String primaryMuscleImage;
  final String secondaryMuscleImage;
  final List<String> steps;

  VideoPage({
    required this.workoutName,
    required this.videoAsset,
    required this.primaryMuscleImage,
    required this.secondaryMuscleImage,
    required this.steps,
  });

  @override
  _VideoPageState createState() => _VideoPageState();
}

class _VideoPageState extends State<VideoPage> {
  late VideoPlayerController _controller;
  late Future<void> _initializeVideoPlayerFuture;

  @override
  void initState() {
    super.initState();

    // Initialize the video player with the provided asset
    _controller = VideoPlayerController.asset(widget.videoAsset);

    _initializeVideoPlayerFuture = _controller.initialize().then((_) {
      setState(() {
        _controller.play();
      });
    }).catchError((error) {
      print('Error initializing video player: $error');
    });

    _controller.setLooping(true); // Optional: Loop the video
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  // Function to show the expanded image
  void _showImageDialog(String imagePath) {
    showDialog(
      context: context,
      builder: (context) => Dialog(
        child: GestureDetector(
          onTap: () {
            Navigator.of(context).pop(); // Close the dialog on tap
          },
          child: Container(
            color: Colors.black,
            child: Image.asset(
              imagePath,
              fit: BoxFit.contain,
            ),
          ),
        ),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.workoutName),
      ),
      body: SingleChildScrollView(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.center,
          children: [
            // Display the workout video at the top
            FutureBuilder(
              future: _initializeVideoPlayerFuture,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.done) {
                  return AspectRatio(
                    aspectRatio: _controller.value.aspectRatio,
                    child: VideoPlayer(_controller),
                  );
                } else if (snapshot.hasError) {
                  return Text('Error loading video');
                } else {
                  return CircularProgressIndicator();
                }
              },
            ),
            SizedBox(height: 20),

            // Text to display "Primary and Secondary Muscle Groups"
            Text(
              "Muscle Groups Activated",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),

            // Images for Primary and Secondary Muscle Groups
            Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Column(
                  children: [
                    Text("Primary", style: TextStyle(fontSize: 18)),
                    GestureDetector(
                      onTap: () => _showImageDialog(widget.primaryMuscleImage),
                      child: Image.asset(
                        widget.primaryMuscleImage,
                        width: 150,
                        height: 150,
                      )
                    )
                  ],
                ),
                SizedBox(width: 20),
                Column(
                  children: [
                    Text("Secondary", style: TextStyle(fontSize: 18)),
                    GestureDetector(
                      onTap: () => _showImageDialog(widget.secondaryMuscleImage),
                      child: Image.asset(
                        widget.secondaryMuscleImage,
                        width: 150,
                        height: 150,
                      ),
                    ),
                  ],
                ),
              ],
            ),

            SizedBox(height: 20),

            // Step-by-step instructions for the exercise
            Text(
              "Step-by-Step Instructions",
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            Padding(
              padding: const EdgeInsets.all(16.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: widget.steps.map((step) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(vertical: 4.0),
                    child: Text(
                      "- $step",
                      style: TextStyle(fontSize: 18),
                    ),
                  );
                }).toList(),
              ),
            ),

            // A button to navigate to a blank page or other feature
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => BlankPage()),
                );
              },
              child: Text("Start Workout"),
            ),
          ],
        ),
      ),
    );
  }
}


// Blank page that will be displayed when the user clicks "Start"
class BlankPage extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text("Blank Page"),
      ),
      body: Center(
        child: Text(
          "This is a blank page",
          style: TextStyle(fontSize: 24),
        ),
      ),
    );
  }
}