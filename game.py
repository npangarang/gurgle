import random
from infra import Grid, KeyBoard, colorDict, choose_word

class Game:
    def __init__(self, id):
        self.p1Went = False
        self.p2Went = False
        self.ready = False
        self.id = id
        self.wins = [0,0]
        self.ties = 0
        self.moves = [None, None]

        self.mode = "guess" #"validate"
        self.readyToSend = [False, False]
        self.bothSentInfo = [False, False]

        self.turn = 0
        p1Word, p2Word = choose_word(), choose_word()
        #p1Word = "trims" #panty
        #p2Word = "slick" #fudge
        #self.words = [p1Word, p2Word]
        self.words = [p1Word, p2Word]
        self.playerGrids = [Grid(p1Word), Grid(p2Word)]
        self.playerKeyboards = [KeyBoard(), KeyBoard()]
        self.playerViews = [0,0]

    # def scroll(self, p, direction):
    #     grid = game.playerGrids[p]
    #     if direction == "down" and grid.firstRow == 0:



    def exchange_info(self, p):
        grid = self.playerGrids[1 - p]
        keyboard = self.playerKeyboards[1-p]
        level = self.playerGrids[1 - p].level - 1
        found = 0
        # reveal the appropriate tiles

        revealedLetters = []
        for tile in grid.rows[level].tiles:
            if tile.color == colorDict["green"] or tile.selected:
                tile.revealed = True
                revealedLetters.append(tile.letter)
            if tile.color == colorDict["yellow"]:
                found += 1
        print(found)

        # account for no letters found (more keyboard info)
        if found == 0:
            for tile in grid.rows[level].tiles:
                if tile.color != colorDict["green"]:
                    tile.revealed = True
                    tile.color = colorDict["red"]
                    revealedLetters.append(tile.letter)

        # update keyboard
        print(revealedLetters)
        for letter, key in keyboard.keys.items():
            if letter in revealedLetters:
                #print(f"player {p} revealed {letter}")
                key.revealed = True
        #print(revealedLetters)


        self.bothSentInfo[p] = False


    def lock_in_info(self, p):
        if self.mode == "validate":
            self.bothSentInfo[p] = True
            self.readyToSend[p] = False

    def highlight_letter(self, p, pos):
        if self.mode == "validate":
            if type(pos) is str:
                x, y = pos[1:-1].split(', ')
                pos = (int(x), int(y))
            grid = self.playerGrids[1-p]
            level = self.playerGrids[1-p].level - 1

            # account for no yellow tiles
            numYellow = 0
            for tile in grid.rows[level].tiles:
                if tile.color == colorDict["yellow"]:
                    numYellow += 1
            if numYellow == 0:
                self.readyToSend[p] = True
                return

            # highlighting
            for tile in grid.rows[level].tiles:
                if tile.click(pos) and tile.color == colorDict["yellow"]:
                    for tile2 in grid.rows[level].tiles:
                        if tile2.selected:
                            tile2.selected = False
                    tile.selected = not tile.selected
                    self.readyToSend[p] = True

    def switch_board(self, p):
        if self.playerViews[p] == 0:
            self.playerViews[p] = 1
        else:
            self.playerViews[p] = 0
        #print(f"player {p} changed views!")

    def determine_state(self):
        if self.turn == self.playerGrids[0].level - 1 == self.playerGrids[1].level - 1:
            return "validate"
        else:
            return "guess"

    def change_state(self, state):
        self.mode = state

    def type_letter(self, p, key):
        if self.mode == "guess" and self.playerGrids[p].level <= self.playerGrids[1-p].level:
            self.playerGrids[p].update(key, self.playerKeyboards[p].usedLetters)

    def click_letter(self, p, pos):
        if self.mode == "guess" and self.playerGrids[p].level <= self.playerGrids[1 - p].level:
            if type(pos) is str:
                x, y = pos[1:-1].split(', ')
                pos = (int(x), int(y))
            for letter, tile in self.playerKeyboards[p].keys.items():
                if tile.click(pos):
                    self.playerGrids[p].update(letter, self.playerKeyboards[p].usedLetters)
        
    def get_player_word(self, p):
        return self.words[p]

    def get_player_move(self, p):
        """
        :param p: [0,1]
        :return: Move
        """
        return self.moves[p]

    def play(self, player, move):
        self.moves[player] = move
        if player == 0:
            self.p1Went = True
        else:
            self.p2Went = True

    def connected(self):
        return self.ready

    def bothWent(self):
        return self.p1Went and self.p2Went

    def winner(self):

        p1 = self.moves[0].upper()[0]
        p2 = self.moves[1].upper()[0]

        winner = -1
        if p1 == "R" and p2 == "S":
            winner = 0
        elif p1 == "S" and p2 == "R":
            winner = 1
        elif p1 == "P" and p2 == "R":
            winner = 0
        elif p1 == "R" and p2 == "P":
            winner = 1
        elif p1 == "S" and p2 == "P":
            winner = 0
        elif p1 == "P" and p2 == "S":
            winner = 1

        return winner

    def resetWent(self):
        self.p1Went = False
        self.p2Went = False