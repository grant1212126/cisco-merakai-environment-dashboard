# CS04 - Team Project

Building an automation dashboard based on Django using Cisco's Meraki API.

## Key Features

* Quick and easy integration with Cisco Meraki API, allowing you to easily add your Cisco Meraki devices.

* Prediction algorithm giving you the ability to make informed decisions about adjusting temperature and humidity.

* Flexible and secure django based authentication.

* Weather integration to view your sensor data in the context of your cities current weather. 

## Installation

### Installation Notes/ Requirements

* Install atleast Python version 3.9.

* Install using git. 

### Installation Instructions

1. Make a clone of the repository using git.

2. Using Pip, install all dependencies using the requirements.txt file provided

## Usage

### Usage notes 

* How to define an environment variable:

https://docs.oracle.com/en/database/oracle/machine-learning/oml4r/1.5.1/oread/creating-and-modifying-environment-variables-on-windows.html#GUID-DD6F9982-60D5-48F6-8270-A27EC53807D0

* Guide to open weather map:

https://openweathermap.org/guide

* Django overview

https://www.djangoproject.com/start/overview/

## Usage instructions

1. Define your Cisco Meraki API key in an environment variable called: MERAKI_DASHBOARD_API_KEY

2. Define your Open Weather Map API key in an environment variable called: OPENWEATHERMAP_API_KEY

4. This application uses djangos authentication system to restrict access to authenticated users, to create an initial admin user, navigate to the main directory of your local version and use "python manage.py createsuperuser". Follow the instructions to create an admin user.

3. In the command line, use "python manage.py" to configure and manage the application, to start the application use "runserver" which will start a version of the server on your local machine.

4. Once you procede to the application, you will be promoted to login, use the admin profile you just created to access the application (note you can create more non-admin users using the django admin interface, you can access this by appending /admin to the application url)

5. Procede to the settings page of the application to define your weather settings, define your locations to group and store your sensors, and add your available Cisco Meraki sensors connected to your Cisco Meraki API key.

6. Run the gather.py script to collect data from your Cisco Meraki devices, which will then be shown on your Dashboard.

## Technologies

This project uses the following core technologies:

* Django version 3.2.9: https://www.djangoproject.com/

* Cisco Meraki API version 1.12.0: https://developer.cisco.com/meraki/api-v1/

The project also uses a variety of smaller dependencies, please see requirements.txt for full list.

## Licences

This application is licenced under the GNU GPL v3 licence, see copying.txt for full licence.

The Open Weather Map is licenced under the Creative Commons Attribution-ShareAlike 4.0 International licence (CC BY-SA 4.0).

https://openweathermap.org/
