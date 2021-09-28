import socket
import json
import time


ADDRESS = ("127.0.0.1", 54321)
BUFF_MAX = 1024
FILE_NAME = "status_02.txt"
# sleep time for sending request to server
SLEEP_TIME = 60
# sleep time for reconnecting if connection was broken
SLEEP_TIME_RECONNECTING = 5


def reconnecting_to_server(client_socket, err):
    print('An existing connection was forcibly closed by the remote host')
    print("Trying to reconnect...")
    print(err)
    client_socket.close()
    client_socket = socket.socket()
    not_connected = True
    while not_connected:
        try:
            client_socket.connect(ADDRESS)
            not_connected = False
            print("client has reconnected successfully...")
            return client_socket
        except OSError as err:
            print(err)
            time.sleep(SLEEP_TIME_RECONNECTING)


def read_data_file(file_name):

    with open(file_name, "r") as f:

        my_dictionary = {
            "station_id": int(f.readline()),
            "alarm_1": int(f.readline()),
            "alarm_2": int(f.readline())
        }

        if (my_dictionary["station_id"] < 0
                or my_dictionary["alarm_1"] not in (0, 1)
                or my_dictionary["alarm_2"] not in (0, 1)):
            raise ValueError

        return my_dictionary


def main_flow():
    try:
        s = socket.socket()
        s.connect(ADDRESS)
        print("client connected to {} successfully...".format(ADDRESS))

        while True:
            data = {}
            try:
                data = read_data_file(FILE_NAME)

            except ValueError:

                print("You have entered wrong values to the file. Pleas Fix")

                # sending server - wrong data type message
                data = {"msg": "client dealing with ValueError"}

                # handling file system exceptions
            except FileNotFoundError:
                data = {"msg": "client dealing with FileNotFoundError"}
                print("file {} does not exist. pleas create it properly. Restart the process if needed.".format(FILE_NAME))

            try:
                # sending the data to the server in json format encoded
                s.send(json.dumps(data).encode())
                response_text = s.recv(BUFF_MAX).decode()
                print(response_text)
                time.sleep(SLEEP_TIME)

            # Reconnecting Automatically to Server in case of broken communication (Works only after successful initial communication)
            except (ConnectionResetError, OSError) as err:
                s = reconnecting_to_server(s, err)
                time.sleep(SLEEP_TIME_RECONNECTING)

    # If initially connection was not established the client will not try to reconnect and process will exit.
    except ConnectionRefusedError:
        print("The server is not connected/working.")
        print("connection closed.")
        exit()


if __name__ == "__main__":
    main_flow()
