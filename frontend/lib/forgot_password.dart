import 'package:flutter/material.dart';
import 'package:hackaton_app/sign_up.dart'; 
import 'package:hackaton_app/login.dart'; 
import 'package:http/http.dart' as http; // for sending requests to backend
import 'dart:convert';

class ForgotPasswordPage extends StatefulWidget {
  const ForgotPasswordPage({super.key});

  @override
  State<ForgotPasswordPage> createState() => _ForgotPasswordState();
}

class _ForgotPasswordState extends State<ForgotPasswordPage> {
  // Variables to store user input
  String email = '';
  String newPassword = '';
  String retypePassword = '';

  bool _obscurePassword = true; 
  bool _obscureRetypePassword = true; 

  final String backendUrl = "http://127.0.0.1:3000/forgot_password";

  Future<void> _resetPassword() async {
    if (email.isEmpty || newPassword.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text("Fill all fields")));
      return;
    }


    try {
      final response = await http.post(
        Uri.parse(backendUrl),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email.trim(),
          'new_password': newPassword.trim(),
        }),
      );

      if (response.statusCode == 200) {
        ScaffoldMessenger.of(context)
            .showSnackBar(const SnackBar(content: Text("Password updated!")));
        Navigator.pop(context); // Go back to login page
      } else {
        final resp = jsonDecode(response.body);
        ScaffoldMessenger.of(context)
            .showSnackBar(SnackBar(content: Text("Error: ${resp['error']}")));
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
                        'Set New Password',
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
                        hintText: 'Retype New Password',
                        contentPadding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
                        enabledBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFCA28)),
                        ),
                        focusedBorder: OutlineInputBorder(
                          borderSide: const BorderSide(color: Color(0xFFFFA726)),
                        ),
                      ),
                      onChanged: (value) => setState(() => newPassword = value),
                    ),
                    const SizedBox(height: 12),

                   

                    // New Password button
                    SizedBox(
                      width: double.infinity,
                      child: ElevatedButton(
                        onPressed: _resetPassword, 
                        style: ElevatedButton.styleFrom(
                          backgroundColor: const Color(0xFFFFB74D),
                          shadowColor: Colors.black45,
                          elevation: 4,
                          padding: const EdgeInsets.symmetric(vertical: 12),
                        ),
                        child: const Text(
                          'Set Password',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            fontSize: 16,
                            color: Colors.white,
                          ),
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
                    const SizedBox(height: 20), 
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center, 
                      children: [
                        const Text(
                          "Don't have an account? ", 
                          style: TextStyle(color: Colors.grey), 
                        ), 
                        GestureDetector(
                          onTap: () {
                            Navigator.push(
                              context, 
                              MaterialPageRoute(builder: (context) => SignUpPage()),
                            );
                          }, 
                          child: const Text(
                            "Sign Up", 
                            style: TextStyle(
                              color: Color(0xFFFFB74D),
                              fontWeight: FontWeight.bold, 
                            ),
                          ),
                        ),
                      ]
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