This project allows monitoring of a remote server on a web page.
Client Components collect the data and upload it to the server running the visualization.
Configuration is done in config.json on top level of the directory structure, please check the example config

To install, first make sure that you have a revent version of python installed on your remote imaging PC, I currently use Python 3.12.

Clone the project to a directory of your choice, enter a cmd shell in that directory and then type:

python -m venv venv

This will create a virtual environment for you.

Then activate the virtual environment by typing:

venv\Scripts\activate.bat

you are now ready to install dependencies:

pip3 install -r requirements-client.txt

you are now ready to use the software.

Please check the scripts telescopeStatus.bat and telescopeDataSync.bat to see how to call the scripts that you desire to use...

