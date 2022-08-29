import threading
import socket
import random
import time
import logging


users = []
sessions = []


class User:
    user_codes = []

    def __init__(self, socket_details, address, name):
        self.sock = socket_details
        self.address = address
        self.name = name
        self.code = self.user_code_generator()
        self.code_zone = "Type something"
        self.partner = 0

    def user_code_generator(self) -> str:
        random_code = random.randint(23082004, 28082004)
        if random_code in User.user_codes:
            self.user_code_generator()
        else:
            User.user_codes.append(random_code)
            return str(random_code)


def code_handler(user):
    other_user = user.partner
    while True:
        try:
            user.code_zone = user.sock.recv(4096).decode('ascii')
            other_user.sock.send(user.code_zone.encode("ascii"))
        except:
            users.remove(user)
            for i in sessions:
                if user in i:
                    sessions.remove(i)
            break
        

logging.basicConfig(level=logging.INFO, filename='log.txt',
                    format='%(asctime)s :: %(levelname)s :: %(thread)d :: %(message)s')


'''logging.info("a = {a}, b = {b}".format(**kwargs))
logging.debug("Hypotenuse of {a}, {b} is {c}".format(**kwargs))
logging.warning("a={a} and b={b} are equal".format(**kwargs))
logging.error("a={a} and b={b} cannot be negative".format(**kwargs))
logging.critical("Hypotenuse of {a}, {b} is {c}".format(**kwargs))'''


def index_of_users_from_code(input_code: str) -> int:
    global users
    for i in range(len(users)):
        if users[i].code == input_code:
            return i
    return None


def index_of_users_from_sock(input_sock) -> int:
    global users
    for i in range(len(users)):
        if users[i].sock == input_sock:
            return i
    return None


host = '127.0.0.1'
port = 23280


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
logging.info(f"server bound to (host: {host}, port: {port}")
server.listen()


def connection_getter():
    while True:
        connection, address = server.accept()
        logging.info(f"socket logged into server: {connection}")
        print(f"{address} connected to the server")
        logging.info(f"starts the handle for {address}")
        thread1 = threading.Thread(target=handle, args=(connection, address), daemon=True)
        thread1.start()


def handle(connection, address):
    while True:
        try:
            msg = connection.recv(50).decode('ascii')
            logging.info(f'{address} : msg')

            if msg[:8] == '!@#$2328':   # get the name of the user
                logging.info("user name incoming")

                users.append(user := User(connection, address, msg[8:]))
                logging.info("user info added to users list and local 'user' variable")

                user.sock.send(f'!@#$2328{user.code}'.encode('ascii'))
                logging.info("user code sent")

            elif msg[:8] == '!@#$2430':    # receive request from one and send to another
                # msg == !@#$2430{other_user.code}

                logging.info("session initialization in process, request being sent")
                other_user = users[index_of_users_from_code(msg[8:])]
                other_user.sock.send(f'!@#$2430{user.code}'.encode('ascii'))
                logging.info(f"session initialization in process, request sent to {other_user.name}")

            elif msg[:8] == '!@#$0604':    # request accepted and send each other's name
                # msg == !@#$0604{other_user.code}
                logging.info("session initialization in process, request accepted")
                other_user = users[index_of_users_from_code(msg[8:])]
                user.sock.send(f"!@#$0604{other_user.name}".encode('ascii'))
                user.partner = other_user
                other_user.partner = user
                other_user.sock.send(f"!@#$0604{user.name}".encode('ascii'))
                logging.info(f"session created : {'success' if user is not None else 'unsuccessful'}"
                             f" between {user.name} and {users[index_of_users_from_code(msg[8:])].name}")

            elif msg[:8] == '!@#$2808':    # when all over, receives this code from both and breaks handle
                thread2 = threading.Thread(target=code_handler, args=(user,))
                thread2.start()
                logging.info(f"{address} handle broke")

                break


        except:
            users.remove(user)
            for i in sessions:
                if user in i:
                    sessions.remove(i)
            break


print("server is running...")
connection_getter()
