import pygame
#import random
from infra import Grid, KeyBoard, Button, play_game, Notification, \
    colorDict, choose_word
from network import Network

def main():
    run = True
    clock = pygame.time.Clock()
    n = Network()
    player = int(n.getP())
    print("You are player", player)
    # btns = [Button("Rock", (50, 500), (50, 20), (0, 0, 0)), Button("Scissors", (250, 500),(50, 20), (255, 0, 0)),
    #         Button("Paper", (450, 500), (50, 20), (0, 255, 0))]
    # text, (pos), (size), color, fontSize
    switchBoard = Button("Your Board", (250, 540), (100, 40), (152, 226, 247), 15)
    lockInfo = Button("Send", (350, 540), (60, 40), colorDict["grey"], 15)
    randWord = Button("hehe", (100,540), (60, 40), colorDict["red"], 15)

    btns = [switchBoard, lockInfo, randWord]
    #btns = [Button("Your opponent's word is: ")]

    while run:

        clock.tick(60)
        try:
            game = n.send("get")
            #print(game.__dict__)
        except:
            run = False
            print("Couldn't get game")
            break
        # if game.bothWent():
        #     play_game(game, player, btns)
        #     pygame.time.delay(500)
        #     try:
        #         game = n.send("reset")
        #     except:
        #         run = False
        #         print("Couldn't get game")
        #         break

            # font = pygame.font.SysFont("comicsans", 30)
            # if (game.winner() == 1 and player == 1) or (game.winner() == 0 and player == 0):
            #     text = font.render("You Won!", 1, (255,0,0))
            # elif game.winner() == -1:
            #     text = font.render("Tie Game!", 1, (255,0,0))
            # else:
            #     text = font.render("You Lost...", 1, (255, 0, 0))
            #
            # win.blit(text, (width/2 - text.get_width()/2, height/2 - text.get_height()/2))
            # pygame.display.update()
            # pygame.time.delay(2000)

        state = game.determine_state()
        game = n.send(f"changeState{state}")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                game = n.send(f"update{key}")

            if event.type == pygame.MOUSEBUTTONDOWN:
                #print(game.mode)
                pos = pygame.mouse.get_pos()
                game = n.send(f"clickLetter{pos}")

                if switchBoard.click(pos):
                    game = n.send(f"changeView")
                    if switchBoard.text == "Opponents Board":
                        switchBoard.text = "Your Board"
                        switchBoard.color = (152, 226, 247)
                    else:
                        switchBoard.text = "Opponents Board"
                        switchBoard.color = (247, 197, 221)

                if game.playerViews[player] == 1:
                    game = n.send(f"highlight{pos}")

                if lockInfo.click(pos):
                    game = n.send("lockinfo")

                if randWord.click(pos):
                    word = choose_word()
                    game = n.send(f"pickRandom{word}")




                # for btn in btns:
                #     if btn.click(pos):
                #         game = n.send(f"changeView{btn.text}")
                        #game.switch_board(btn, player)
                #print(game.player)
                #pos = pygame.mouse.get_pos()
                # for btn in btns:
                #     if btn.click(pos) and game.connected():
                #         if player == 0:
                #             if not game.p1Went:
                #                 n.send(btn.text)
                #         else:
                #             if not game.p2Went:
                #                 n.send(btn.text)

        play_game(game, player, btns)
main()