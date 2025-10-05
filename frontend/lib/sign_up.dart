import 'package:flutter/material.dart';
import 'package:google_sign_in/google_sign_in.dart';
import 'package:http/http.dart' as http; // for sending requests to backend
import 'dart:convert';


import 'package:hackaton_app/login.dart'; 
import 'package:hackaton_app/forgot_password.dart'; 

class SignUpPage extends StatefulWidget {
  const SignUpPage({super.key});

  @override
  State<SignUpPage> createState() => _SignUpPageState();
}

class _SignUpPageState extends State<SignUpPage> {
  // Variables to store user input
  String email = '';
  String password = '';
  String retypePassword = '';

  bool _obscurePassword = true; 
  bool _obscureRetypePassword = true; 

  final String backendUrl = "http://127.0.0.1:3000/add_user"; // put url here 
  Future<void> _signUp() async {
    if (email.isEmpty || password.isEmpty || retypePassword.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text("Fill all fields")));
      return;
    }

    if (password != retypePassword) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text("Passwords do not match")));
      return;
    }

    try {
      // Send POST request to backend to add user to db_users.json
      final response = await http.post(
        Uri.parse(backendUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'password': password.trim(),
        }),
      );

      if (response.statusCode == 200) {// if registration was success 
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text("User registered!")));
        Navigator.push(
          context,
          MaterialPageRoute(builder: (context) => const LoginPage()),
        );
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text("Error: ${response.body}")),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text("Error: $e")));
    }
  }
  


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color.fromARGB(255, 255, 255, 255), // light pink background
      body: Center(
        child: Stack(
          alignment: Alignment.center,
          children: [
            // Orange shadow box
            Transform.translate(
              offset: const Offset(10,10), //move yellow box right 10px and down 10px
              child: Container(
                height: 550, 
                width: 320,
                decoration: BoxDecoration(
                  color: const Color(0xFFFFB74D), 
                  borderRadius: BorderRadius.circular(8),
                ),
              ),
            ),
            
            //White main card 
            // White main card
            Container(
              height: 550,
              width: 320,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    offset: const Offset(2, 2),
                    blurRadius: 6,
                  ),
                ],
              ),
              child: Padding(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 20),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.start,
                  children: [
                    // Top icon
                    Image.asset(
                      'assets/graph_logo.png', // replace with your chart image asset
                      height: 60,
                    ),
                    const SizedBox(height: 10),

                    // Title
                    const Align(
                      alignment: Alignment.centerLeft,
                      child: Text(
                        'Sign Up',
                        style: TextStyle(
                          fontSize: 22,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFFFFA726),
                        ),
                      ),
                    ),
                    const SizedBox(height: 15),

                    // Email
                    TextField(
                      decoration: InputDecoration(
                        hintText: 'Email Here',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFCA28)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFA726)),
                        ),
                      ),
                      onChanged: (value) => setState(() => email = value),
                    ),
                    const SizedBox(height: 12),

                    // Password
                    TextField(
                      obscureText: true,
                      decoration: InputDecoration(
                        hintText: 'Password Here',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFCA28)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFA726)),
                        ),
                      ),
                      onChanged: (value) => setState(() => password = value),
                    ),
                    const SizedBox(height: 12),

                    // Retype Password
                    TextField(
                      obscureText: true,
                      decoration: InputDecoration(
                        hintText: 'Retype Password',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFCA28)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFA726)),
                        ),
                      ),
                      onChanged: (value) => setState(() => retypePassword = value),
                    ),
                    const SizedBox(height: 18),

                    // Sign Up button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _signUp, 
                        /*
                        onPressed: () {

                          // TODO: handle sign-up logic
                          
                          // Navigate to Login page
                          
                          print('Email: $email');
                          print('Password: $password');
                        }, */
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFFB74D),
                          shadowColor: Colors.black45,
                          elevation: 4,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        child: const Text(
                          'Sign Up',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Colors.white,
                          ),
                        ),
                      ),
                    ),

                    // Forgot Password
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(builder: (context) => ForgotPasswordPage()),
                          );
                        },
                        child: const Text(
                          'Forgot Password?',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ),
                    ),

                    // Divider with OR
                    Row(
                      children: const [
                        Expanded(child: Divider(color: Colors.grey)),
                        Padding(
                          padding: EdgeInsets.symmetric(horizontal: 8),
                          child: Text('OR'),
                        ),
                        Expanded(child: Divider(color: Colors.grey)),
                      ],
                    ),
                    const SizedBox(height: 10),

                    // Google and Apple logos
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        GestureDetector(
                          onTap: () {
                          // TODO: integrate Google Login 
                          print ("Google login pressed ");
                          }, 
                          child: Image.asset(
                            'assets/google_logo.png',
                            height: 30, 
                          ),
                        ),
                        
                        const SizedBox(width: 20),
                        GestureDetector(
                          onTap: () {
                          // TODO: integrate Apple Login 
                          print ("Apple login pressed ");
                          }, 
                          child: Image.asset(
                            'assets/apple_logo.png',
                            height: 30, 
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}