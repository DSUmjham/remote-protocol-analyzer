# Remote Protocol Analyzer
This repository contains code for a Dockerized Flask app and Saleae Logic 2 software for remote protocol analysis. This configuration allows remote leaners to remotely interact with a logic analyzer connected to a target device and perform basic control via a web platform (i.e., triggering the device to send, configuring basic input, etc.).

## Docker
Two [docker containers](https://github.com/DSUmjham/remote-protocol-analyzer/tree/main/docker) compose the application. One container serves the Flask application for the web interface and a second is used for the Saleae Logic 2 software. 

Build the images and bring up the containers by running the following command:
```console
docker compose up -d
```
Update the docker-compose.yml file to meet your system configuration (i.e., device mappings). The web interface will be on http://127.0.0.1:5000 by default and the noVNC session for Logic 2 is hosted at http://127.0.0.1:8080. 

### rpa-app
This Flask app serves multiple functions, offering remote access to the Saleae Logic 2 software through a noVNC connection. Users can interact with Logic 2 remotely, simulating a direct local connection. Additionally, the web interface includes configurable buttons for sending serial commands to the target device, along with a live stream of the target hardware, allowing users to monitor interactions in real time.
![Web GUI](https://github.com/DSUmjham/remote-protocol-analyzer/blob/main/images/interface.png?raw=true)

### logic2
Logic 2, an Electron-based application, functions best with a GUI. While it can operate in headless mode, running it this way in Docker introduces certain challenges. To address this, the Docker image emulates a virtual display, which is shared through noVNC, allowing remote access via the Flask app.

For the virtual display setup, Xtigervnc starts on display 0 and listens on port 5900. easy-novnc then bridges this VNC server (port 5900) to a web-accessible port (8080), enabling browser-based interaction. The bspwm window manager initializes next, setting the DISPLAY environment variable to route output to display 0. Finally, Logic 2 launches, utilizing display 0 for its GUI.

## Arduino
The files contained within the [Arduino](https://github.com/DSUmjham/remote-protocol-analyzer/tree/main/arduino) folder are a sample project used in the demo. The .ino file shows how a program can be written to carry out specific actions based on Serial input. 

## Resources
* [Saleae Logic 2]([https://support.saleae.com/logic-software/sw-download])