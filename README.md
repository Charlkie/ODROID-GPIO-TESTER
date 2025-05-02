# Testing GUI & Tunnel Control Panel

This repository provides tools for interfacing with the ODROID-M1S hardware and testing its functionalities through a graphical user interface.

## Table of Contents

- [Directory Structure](#directory-structure)
- [ODROID-M1S GPIO Library](#odroid-m1s-gpio-library)
- [Testing GUI](#testing-gui)
- [Tunnel Control Panel](#tunnel-control-panel)
- [Fake Control Panel](#fake-control-panel)
- [Making Changes](#making-changes)
- [VS Code on ODROID-M1S](#vscode-on-odroid-m1s)

## Directory Structure

- **odroid_gpio**  
  Contains the GPIO library for interfacing with the ODROID-M1S hardware.
- **TesterGUI**  
  Implements a graphical interface to test the methods in the `odroid_gpio` library.
- **TunnelControlPanel.py**  
  The main script managing the shock tunnel operations. It automates fill processes and ensures a safe shutdown.
- **FakeControlPanel**  
  A dummy version of the tunnel control panel. This stub allows testing the GUI on any machine without requiring actual ODROID hardware.

## Running Code

To run any of the files in this repository, use the Python interpreter. Note that if you are executing any file except for FakeControlPanel.py, you need to run it with sudo. For example:

To run the tunnel control panel:
```bash
sudo python3 TunnelControlPanel.py
```

To run the Testing GUI:
```bash
sudo python3 TesterGUI.py
```

To run the Fake Control Panel (does not require sudo):
```bash
python3 FakeControlPanel.py
```


## ODROID-M1S GPIO Library

The `odroid_gpio.py` file provides a library of methods that simplify writing to GPIO pins and reading from ADC outputs on the ODROID-M1S. These methods encapsulate hardware interactions, making it easier to develop applications for the ODROID platform.

## Testing GUI

The Testing GUI is a graphical implementation that uses the `odroid_gpio.py` methods. It provides users with a visual way to interact with GPIO pins and view ADC readouts without needing to write any additional code. A screenshot of the interface is provided below for reference.

![GUI Screenshot](TesterGUI.png)

This tool is highly useful for testing individual components quickly before deploying the full tunnel control script.

## Tunnel Control Panel

The `TunnelControlPanel.py` script is the main component for operating the prototype shock tunnel. It is designed to automatically control the filling process and manage a safe shutdown, ensuring efficient and secure tunnel operation.

## Fake Control Panel

The Fake Control Panel is a stand-in for the full tunnel control panel. The methods are not implemented, which allows developers to test and develop the GUI on any platform without requiring the ODROID hardware. This is ideal for debugging and making iterative improvements.

## Making Changes

Due to the ARM-based CPU architecture of the ODROID-M1S, there is no official VS Code binary available. To work around this limitation, you can host VS Code in a browser using [code-server](https://github.com/cdr/code-server). This approach allows you to edit and manage your code remotely on the ODROID device.

## VS Code on ODROID-M1S

To run VS Code on the ODROID-M1S:

1. Deploy code-server on the device:
   ```bash
   code-server
   ```
2. When prompted, retrieve the initial password using:
   ```bash
   grep "password" ~/.config/code-server/config.yaml
   ```
3. It is recommended to change the default password to avoid having to retrieve it every time.

This setup allows you to use a full-featured VS Code interface through your browser, making development on the ODROID-M1S much more convenient.