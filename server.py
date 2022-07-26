import socket
from _thread import *
import pickle
from game import Game

#server = "66.112.240.12"
server = "10.160.129.216"
#server = "10.160.131.80"
#server = "192.168.1.105"
#server = "192.168.1.100"
port = 5555

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try:
    s.bind((server, port))
except socket.error as e:
    print("hi")
    str(e)

s.listen()
print(f"Waiting for a connection, Server Started with local ip: {server}")

connected = set()
games = {}
idCount = 0


def threaded_client(conn, p, gameId):
    global idCount
    conn.send(str.encode(str(p)))

    reply = ""
    while True:
        try:
            data = conn.recv(2048*4).decode()

            if gameId in games:
                game = games[gameId]

                if not data:
                    break
                else:
                    if data == "reset":
                        game.resetWent()

                    elif data[:6] == "update":
                        key = data[6:]
                        game.type_letter(p, key)

                    elif data[:11] == "clickLetter":
                        pos = data[11:]
                        game.click_letter(p, pos)

                    elif data[:10] == "pickRandom":
                        for letter in data[10:]:
                            game.type_letter(p, letter)

                    elif data == "changeView":
                        game.switch_board(p)

                    elif data[:11] == "changeState":
                        game.change_state(data[11:])

                    elif data[:9] == "highlight":
                        pos = data[9:]
                        game.highlight_letter(p, pos)

                    elif data[:8] == "lockinfo":
                        game.lock_in_info(p)
                        if game.bothSentInfo == [True, True]:
                            game.exchange_info(p)
                            game.exchange_info(1-p)
                            game.turn += 1

                    elif data != "get":
                        game.play(p, data)
                    conn.sendall(pickle.dumps(game))
            else:
                break
        except:
            break

    print("Lost connection")
    try:
        del games[gameId]
        print("Closing Game", gameId)
    except:
        pass
    idCount -= 1
    conn.close()



while True:
    conn, addr = s.accept()
    print("Connected to:", addr)

    idCount += 1
    p = 0
    gameId = (idCount - 1)//2
    if idCount % 2 == 1:
        games[gameId] = Game(gameId)
        print("Creating a new game...")
    else:
        games[gameId].ready = True
        p = 1
    start_new_thread(threaded_client, (conn, p, gameId))