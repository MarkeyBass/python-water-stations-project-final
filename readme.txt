
####################################
# The Water Stations Application ###
####################################

A brief explanation on the different parts of this project:

server.py
==========
    The main process.
    It deals with receiving and sending data from client processes via TCP protocol.
    The data is stored in sqlite database file all_stations.sqlite.
    In addition the server will make a copy of the database to a JSON file all_stations.json

    The main of the sever will start two threads one will run the server process the other will
    run the ui process. The ui was built by PyQt5Designer. THe code was generated automatically.
    Later I changed it gave it functionality and made little cosmetic changes.

    In order to make the server work you'll have to install pyqt5 on your device or comment few rows of code.
    More about that pleas read The explanation at the top of server.py code.

CLIENTS
========
    In each client folder there are two files one is the client process (client_01.py)
    the other is the status file (status_01.txt) from which the client retrieves the data that is sent to the server.
    The status file holds: fist line - client id, second line - status of alarm 1 (0/1), third line status of alarm 2 (0/1).
    The clients will send request to the server every 60 seconds in order to make this faster
    change the SLEEP_TIME global variable at the top of the code of each client.

Programmer: Mark Kirzhner