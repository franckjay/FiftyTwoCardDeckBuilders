
Method 1: Using Xcode (Recommended)
Prerequisites:

A Mac computer (required for iOS development)
Xcode installed (free from Mac App Store)
An Apple ID (free to create)

Steps:

Install Xcode

Open the Mac App Store
Search for "Xcode"
Download and install (it's large, ~10GB)


Create a New iOS Project

Open Xcode
Click "Create New Project" or File → New → Project
Choose "iOS" → "App"
Click "Next"


Configure Your Project

Product Name: StarshipSalvage
Team: Select your Apple ID (you may need to add it first)
Organization Identifier: com.yourname (replace with your name)
Interface: SwiftUI
Language: Swift
Click "Next" and save the project


Replace the Code

In the project navigator (left sidebar), find ContentView.swift
Delete all the existing code
Copy and paste the entire code I provided above
Delete the StarshipSalvageApp.swift file if it exists separately (the code above includes it)


Configure Your Device

Connect your iPhone to your Mac with a USB cable
In Xcode, at the top of the window, click the device selector (next to the play button)
Select your iPhone from the list
If prompted, trust the computer on your iPhone


Enable Developer Mode on iPhone (iOS 16+)

On your iPhone: Settings → Privacy & Security
Scroll down to "Developer Mode"
Toggle it on and restart your phone


Run the App

Click the Play button (▶️) in Xcode
First time: You'll get an "Untrusted Developer" error on your phone
On iPhone: Settings → General → VPN & Device Management
Tap your developer profile and trust it
Try running again from Xcode



Method 2: Using Swift Playgrounds (Easier, No Mac Required)
Prerequisites:

An iPad with Swift Playgrounds 4.0+ (available on App Store)
Or a Mac with Swift Playgrounds

Steps:

Install Swift Playgrounds

Download from the App Store (free)


Create New App

Open Swift Playgrounds
Tap "App" to create a new SwiftUI app
Name it "Starship Salvage"


Add the Code

Replace the default ContentView code with the code provided above
Make sure to include all the code


Run the App

Tap the "Run My Code" button
The app will run in preview mode


Export to iPhone (if using iPad)

Tap the share button
Choose "Export to Xcode Project" or use AirDrop to send to your iPhone
