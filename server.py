"""
IMPORTANT NOTES
SERVER -
 This is the main process of the program other processes will not work properly if the server.py wasn't initially started.
 If the server already started and clients connected to it and the server crashes
 the connected clients will try to reconnect automatically.
 New clients that can't connect to server that does not work will not try to reconnect automatically and will quit their process.

 In order to make the server.py work you have to make sure that you have python 3, pip and pyqt5 installed on your device.
 To install pyqt5 on windows execute this command in the commandline: pip install pyqt5
 If you don't want to install pyqt5 you should comment the first line of code: "import ui_server",
 and the two last lines of code: "thread_2 = threading.Thread(target=ui_server.main_flow)"
                                "thread_2.start()"
 This way the UI wont run at all.

 If you install pyqt5 a window will pop along with the server terminal. There is a single button
 At the bottom. Pleas click it to refresh the data on the UI.
"""

import ui_server
import socket
import json
import datetime
import select
import sqlite3 as sql
import threading


class InvalidDataError(Exception):
    def __init__(self, msg_to_client, msg_err):
        self.msg_to_client = msg_to_client
        self.msg_err = msg_err


DB_FILE = "all_stations.sqlite"
JSON_FILE = "all_stations.json"
ADDRESS = ("127.0.0.1", 54321)
BUFF_MAX = 1024
client_diction = {}  # {client : address}


def validate_client_data(data):

    try:

        data_dic = json.loads(data.decode())

        if data_dic == {"msg": "client dealing with ValueError"}:
            msg_err = "sent wrong data!"
            msg_to_client = "SERVER MSG: you attempted to send wrong data"
            raise InvalidDataError(msg_to_client, msg_err)

        elif data_dic == {"msg": "client dealing with FileNotFoundError"}:
            msg_err = "dealing with FileNotFoundError"
            msg_to_client = "SERVER MSG: got that you are dealing with FileNotFoundError"
            raise InvalidDataError(msg_to_client, msg_err)

        return data_dic
    # This exception will be raised if data was sent in a wrong format
    except json.decoder.JSONDecodeError as err:
        msg_err = f"sent wrong data format! {err}"
        msg_to_client = "SERVER MSG: you attempted to send data in wrong format. json is expected"
        raise InvalidDataError(msg_to_client, msg_err)


def get_client_data(client):
    try:
        # RECEIVING DATA FROM CLIENT
        data = client.recv(BUFF_MAX)
        if len(data) == 0:
            print("client {}:{} disconnected".format(*client_diction[client]))
            del client_diction[client]
        else:
            data_dic = validate_client_data(data)
            return data_dic

    except ConnectionResetError:
        print("ConnectionResetError: client {}:{} unexpectedly disconnected".format(*client_diction[client]))
        del client_diction[client]
    except InvalidDataError as err:
        print(f"client {client_diction[client]}: {err.msg_err}")
        client.send(err.msg_to_client.encode())


def send_ack_to_client(time_stamp, client):
    client.send(f"Server received data at {time_stamp}".encode())


def store_to_db(data_dic, last_update):
    with sql.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS station_status(
                    station_id STRING PRIMARY KEY,
                    alarm_1 INT NOT NULL,
                    alarm_2 INT NOT NULL,
                    update_time TEXT
                ) 
            """
        )
        conn.commit()

        cur.execute(
            """INSERT OR REPLACE INTO station_status VALUES (?,?,?,?)""",
            (data_dic["station_id"], data_dic["alarm_1"], data_dic["alarm_2"], str(last_update))
        )
        conn.commit()


def get_from_db():
    with sql.connect(DB_FILE) as conn:
        cur = conn.cursor()
        cur.execute("SELECT * FROM station_status")
        all_stations_dic = {}
        for line in cur:
            # print(list(line))
            all_stations_dic[line[0]] = {
                "alarm_1": line[1],
                "alarm_2": line[2],
                "update_time": line[3]
            }

        return all_stations_dic


# This function creates a json file which is a picture of the database
# Initially created before there was GUI to present easily the DB content in a human readable file.
def dump_json(dic, path):
    with open(path, "w+") as f:
        json.dump(dic, f)
        f.flush()


def handle_client_socket(client):

    data_dic = get_client_data(client)
    if data_dic:

        # setting date time string
        last_update = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"{last_update} client {client_diction[client]} sent {data_dic}")

        # response to client
        send_ack_to_client(last_update, client)

        # Database implementation
        store_to_db(data_dic, last_update)

        # creating json file with data from the database
        all_stations_dic = get_from_db()
        dump_json(all_stations_dic, JSON_FILE)


def handle_server_socket(server_socket):
    new_client, address = server_socket.accept()
    client_diction[new_client] = address
    print("client connected {}:{}".format(*address))


def main_flow():
    with socket.socket() as server_socket:
        server_socket.bind(ADDRESS)
        server_socket.listen(16)
        print("Server listening on port {}...".format(ADDRESS[1]))

        while True:
            client_list = list(client_diction)
            # working with select API to allow multiple clients to work simultaneously with server:
            r_list, _, x_list = select.select(
                [server_socket] + client_list,
                [],
                client_list
            )

            for client in x_list:
                print("client {}:{} crashed".format(*client_diction[client]))
                del client_diction[client]

            for sock in r_list:

                # Handling actions for server in r_list
                if sock is server_socket:
                    handle_server_socket(sock)
                # Handling actions for clients in r_list
                else:
                    handle_client_socket(sock)


if __name__ == "__main__":
    # I Used threading in order to run the server program and its UI simultaneously
    # # Running server
    thread_1 = threading.Thread(target=main_flow)
    thread_1.start()

    # # Running ui_server application
    thread_2 = threading.Thread(target=ui_server.main_flow)
    thread_2.start()




