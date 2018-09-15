# Crazy Game - User's Guide

## Introduction  
This project was made as a part of the [Motion Planning for Robots](http://acg.cs.tau.ac.il/projects) workshop at Tel-Aviv University, the department of CS, 2018, under the guidance of [Prof. Dan Halperin
](http://acg.cs.tau.ac.il/danhalperin/homepage).


In this project, we created a framework for developing games of controlling real world robots on a competition between human and computer players. We also developed two games using this framework, that can be played once the system is up. The system was developed with special emphasis on motion planning algorithms.

 We used the **Crazyflie drones**, **Optitrack** motion tracking system and various software (further details later in this document). 


This guide provides the links and instructions for the steps needed in order to set up this project and play the games. The proceeding [Developers Guide](https://github.com/yuvalailer/CrazyFlie/blob/master/README.md) gives a deeper look into the software we wrote and can be useful for creating your own games and frameworks.

## Watch it in action:
[![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/Video_image_new.jpg)](https://youtu.be/r_WV8khKviY)

## Table of Content
#### 1. Installation and Prerequisites 
     1.1. Hardware - OptiTrack, VM, Windows, Peripherals (Joystick, LED)
     
     1.2. Software - Git
#### 2. Crazy Game
     2.1. Capture the Flag  - 2 players (human or machine), fly 2-4 drones in a competition to capture the rival’s flags.
 
     2.2 SandBox - Freeform game to experiment with the drones
 
     2.3. Catch’em all - 2 players (human or machine), taking turns flying one drone on a mission to capture all the targets in the shortest time.
     
     2.4. How to run the game

#### 3. Thanks and Disclaimer


# 1. Installation and Prerequisites 
## 1.1 Hardware
### Optitrack
- [Flex 3 capture cameras](http://optitrack.com/products/flex-3/) .
There is no standard number of needed cameras for this project to work. The amount depend on the size of the “playing field”. A good “rule of thumb” at least 3 cameras have to be able to see all infrared markers related to a “rigid object” at any given moment.
We had 6 cameras covering an area of about 1.5X1.5 meters, and up to 0.5 meter in the Z (upward) axis.
- [Infrared markers](http://optitrack.com/products/motion-capture-markers/) - 
Optitrack Cameras are able to identify objects by the reflection from the IR markers connected to the quadcopter.
For example, 4 markers used for each Crazyflie 2.0 drone, each drone is consider as 1 “rigid object”.
- [Calibration tools](http://optitrack.com/products/tools/) - We used CW-500 Calibration Wand Kit for calibrating the cameras and CS-200 Calibration Square to set (X, Y, Z) coordinates directions. Calibration process will be further detailed later in this document.
- [Hardware key](http://optitrack.com/products/keys/) - A hardware key dongle is required for using the Motive software.
- [OptiHub 2.0](http://optitrack.com/products/optihub/) - All cameras connect to OptiHub device that connects them to the PC.
All the hardware and software mentioned here can be bought together in the following [link](http://optitrack.com/cart/?shopurl=http://optitrack.com/systems/).

 

Other required hardware.
- [2/4 Crazyflie 2.0 drones](https://www.bitcraze.io/crazyflie-2/) - The set of drones we used in this project. 
- [Arduino Joystick.](https://store.arduino.cc/grove-thumb-joystick)
- WS2811 Controlled Leds.
- USB - RF antenna for communicating with the Crazyflie drones.


### The VM:
- Bitcraze virtual machine image, a xubuntu-14.04.4 linux VM already containing Ros code and launch files necessary for the system to work. adopted from another project, this Image is unique and has to be download from [here](https://drive.google.com/file/d/1OSWwj7HVpXB0UVi14W5PEDzpQ00gjmQb/view).


As mentioned before, the VM acts as a server. The main game (on Windows) communicate with the VM over TCP connection and other code parts in the VM handle the communication with the drones.

### Windows:
The second software environment is Windows 10, which need to contain the Motive software and other files related to the game. These files can be found in [CrazyGame for Windows PC]{https://github.com/xqgex/CrazyFlie} - The GUI repository (without the motive software).


# 1.2 Software
## Motive
Motive is the software used for controlling and processing the information received from the Optitrack cameras set. It is proprietary and requires a license. In Motive, collections of markers, identified by the cameras, are grouped together into trackable ‘rigid bodies’, that represent the location of objects in the real world. In our project, such objects are the Crazyflie Drones and the LEDs. it is very important to follow the next **naming convention** in order to use our system “as is” without changes.
#### For Drones:
- Drone number X will be called **crazyflieX** in Motive (as a ‘rigid body’).
- Its designated MAC address will be **E7E7E7E70X**.

For example: 

drone 3 will be called **crazyflie3** and have the address **E7E7E7E703**. 

drone 15 will be called **crazyflie15** and have the address **E7E7E7E715**.

#### For LEDs:
- LED number X will be called **ledX** in Motive (as a ‘rigid body’).

For example: 

LED 3 will be called **led3**.  
LED 15 will be called **led15**.

 ## Git
Our project is divided into five different Git repositories. Each one can be used by its own, but of course the parts were built to fit together, and therefore some adjustments will be necessary. In order to install the full framework, follow the steps provided in the installation guide.

### Repositories:
- [CrazyGame Website](https://tau-crazygame.github.io/)
- [CrazyGame for Windows PC - The GUI](https://github.com/xqgex/CrazyFlie)
- [CrazyGame VM code - Communication with the drones](https://github.com/xqgex/CrazyFlie_ros) 
- [CrazyGame Arduino code - For joystick and led strips](https://github.com/xqgex/CrazyFlie_Arduino)
- [CrazyGame Automatic player](https://github.com/xqgex/CrazyFlie_Autoplayer)

## Dependencies:
Different parts of the project are made using different inviruments and software dependencies. Best practise of using this project is following the installation guide, on a **Windows** computer strong enough to carry the simultaneous load of the VM and the hoat softwarea, Which means **minimum 8 GB of RAM and virtualization capabilities**.
Alternatively it is possible to use it in other configurations but we don’t offer additional support for it.

## Installation Guide:
Assuming:
- You are using a Windows computer that meets the demands in the dependencies section.

- That the Optitrack + motive system is installed and ready to go.

- That the Crazyflie antenna dongle is connected.

1. Download and install [Oracle VirtualBox](https://www.virtualbox.org/) or alternative VM host software of your choice.
2. Download the [Linux Xubuntu VM](https://drive.google.com/file/d/1OSWwj7HVpXB0UVi14W5PEDzpQ00gjmQb/view) we supply in our git repository. It is based on the [original Crazyflie project VM](https://wiki.bitcraze.io/projects:virtualmachine:index). You can move to the next steps while it is downloading. 
3. Install [python 3.6](https://www.python.org/downloads/release/python-366/) on the windows PC.
4. Install the needed Python dependencies by opening Windows CMD and typing: 
```
pip install shapely pyserial munch
```
5. Download and Install [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git) on the Windows PC. 
6. Clone the Windows-side repository by opening the now installed **Git bash** program, and typing in the command:
```
git clone https://github.com/xqgex/CrazyFlie
```
It is very important to add the main crazyFlie directory to python path.
7. Import the downloaded VM from step 2, in the VM host software from step 1. You can use [this guide](https://docs.oracle.com/cd/E26217_01/E26796/html/qs-import-vm.html).
8. Set the following configuration ([“How To” guide](https://www.virtualbox.org/manual/ch03.html)) for the VM:
- At least 4 GB of RAM
- static IP - 172.16.1.2
- Network adapter attached to - “Host-Only adapter” (in the Virtualbox VM settings)
 
9. Start the VM (root password is “crazyflie”).
10. **optional:** if you wish to control the drone using an Arduino Joystick + LED targets, install the [Arduino IDE](https://www.arduino.cc/en/Main/Software), and clone/use the code from the - [CrazyGame Arduino code - For joystick and led strips](https://github.com/xqgex/CrazyFlie_Arduino) repository.

### You now have all you need to start the game. Move to the “How to run the game” part to start playing! 

  


# 2. Crazy Game
After choosing the controller you wish to work wish, you will get to the **choose your game** window:

![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/choose_game.JPG)

From this screen you can choose the mode you wish to play.

## 2.1 Capture the Flag
### Getting Started
By pressing the `Capture the Flag` button you will be transferred to the Capture the Flag game mode selection screen:

![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/capture_menu.JPG)

Here you can choose the way you wish to play the game:
- Computer Vs. Computer
- Player Vs. Computer
- Player Vs. Player

Regardless of  which mode you chose, you will be passed to the main game window.
At first the drones will take their starting positions.
Then, in turns each player will have 4 seconds to make his move towards the goal.
### Goal
The first player to reach his respective colored LED is the winner.

### Features
- At the top left corner of the screen you have battery indications for all drones in the field.
- The drones have a safety zone that will not allow to get close to each to other more than a certain radius, both in the game and in the field.
### Controls
The player controls his drones with the arrow keys on the keyboard.

---
## 2.2 Sand Box
### Getting Started
By pressing the `Sand Box` Button you will be transferred to the Sand Box:

![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/sandbox_window.JPG)

### Goal
Here you are free to play around with the drones with no special restrictions or goal.
### Controls
| Key | Function |
|:-----:|:------------:|
| Up arrow  | Move drone "north"|
| Down arrow | Move drone "south" |
| Left arrow |  Move drone "west" |
| Right arrow | Move drone "east" |
| U | Take off selected drone |
| L | Land selected drone |
| S | stop the selected drone |
| Space | Change selected drone |
| R | Change LED to red |
| G | Change LED to green |
| B | Change LED to blue |

- By clicking with the mouse on a drone you can change the selected drone
- Same hold for LEDs


- The selected drone will be marked green while the other drones are black.

### Features
At the top left corner of the screen we have a few ways to control the motion of the drones:
- The two top buttons: `Velocity` and `Step Size` are Radio Buttons. Meaning, only one can be pressed down at any given moment.
- While one of them is pressed, you can change the value associated with it with the `+` and `-` buttons.
- After the desired value is selected, you can press the `update` button to update the values.
- A message will appear at the bottom of the screen confirming the new values.
---


## 2.3 Catch’em all 
### Watch this game in action:
[![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/Video_image_new.jpg)](https://youtu.be/awm4osTDK7g)
### Getting Started
By pressing the `Catch’em all` button you will be transferred to the Catch’em All game screen:

![](https://github.com/yuvalailer/CrazyFlie/blob/master/images/catch_screen.JPG)

### Goal
The goal in this mode is to pass through all given targets at the minimal time possible to beat the computer’s time.
### The Flow
1. First of all the system will try to connect to the computer’s side algorithm. If none is present, the system will use a simplified static algorithm for the computer’s turn.
2. Then, the first turn will be of the player. You will have a countdown to the start of your turn and then you will have to pass through all the targets in a path that seems shortest to you.
3. After you have passed through all the targets, the drone will return to the starting position to prepare for the computer’s turn.
4. The computer will execute its path, and in the end the winner with the shortest time will be announced.
### LEDs
- The LEDs will be used as the targets to pass through. They are all red at the start of the game and once a target is reached it will turn green.
- If no physical LEDs are detected by the system, 4 simulative LEDs will be randomly placed on the game board.


---

## 2.4. How to run the game 
After downloads all files related to the game both VM and Windows sides and after setting the drones and leds (optional) in Motive software follow those instructions to run the game.
### VM side:
In CrazyFlie_ros/crazyflie_demo/scripts/ folder, enter: 


```
python main.py crazyflie2 crazyflie3 led1 led2
```

Replace “crazyflie2 crazyflie3 led1 led2” with your drones and leds setup in Motive

Then at the same folder, run:

```
python crazyGameVM.py
```

### Windows side:
In /CrazyFlie

```
python crazyGame.py
``` 
Enjoy the game. 











## 3. Thanks and Disclaimer 
We would like to thank Prof. Dan Halperin and the staff of the course for their guidance, Yoni Mendel and the Advanced Control Systems Lab in TAU for hosting and supporting this project. Special Thanks to Yotam Gani and Orel Ben-Yeshai for their support and assistance. 

#### We don't own any IP rights for 3rd party components, such as software, hardware, internet articles, manuals, images (found on google image search) or any other 3rd party component of this project, which may be subjected to any kind of copyrights. All activities in this project were made for educational purposes only.






