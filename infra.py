import pygame
import random
from collections import Counter

width = 500
height = 700
background = pygame.display.set_mode((width, height))
pygame.display.set_caption("Client")
numLetters = 5
rowLimit = 6
allWords = set()

pygame.font.init()

colorDict = {"green": (0, 209, 0),
             "yellow": (202, 209, 0),
             "grey": (105,105,105),
             "lightgrey": (211,211,211),
             "black": (0,0,0),
             "white":(255,255,255),
             "red": (255, 0, 0),
             "lightblue": (196, 222, 242)}
background.fill(colorDict["white"])

allWords = []
with open('Data/5letter.txt', 'r') as file:
    for line in file:
        for word in line.split():
            allWords.append(word)


def choose_word():
    allWords = []
    with open('Data/5letter.txt', 'r') as file:
        for line in file:
            for word in line.split():
                allWords.append(word)
    return random.choice(allWords)

class Button:
    def __init__(self, text, pos, size, color, fontSize = 20):
        self.text = text
        self.x = pos[0]
        self.y = pos[1]
        self.color = color
        self.width = size[0]
        self.height = size[1]
        self.fontSize = fontSize

    def draw(self):
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        rect.center = (self.x, self.y)
        pygame.draw.rect(background, self.color, rect)

        font = pygame.font.SysFont("Arial", self.fontSize)
        text = font.render(self.text, 1, colorDict["black"])
        text_rect = text.get_rect(center=(self.x, self.y))
        background.blit(text, text_rect)
        #(self.x + round(self.width/2) - round(text.get_width()/2), self.y + round(self.height/2) - round(text.get_height()/2))

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        if self.x - self.width/2 <= x1 <= self.x + self.width/2 and self.y - self.width/2 <= y1 <= self.y + self.width/2:
            return True
        else:
            return False

        # if self.x - self.width <= x1 <= self.x + self.width and self.y <= y1 <= self.y + self.height:
        #     return True
        # else:
        #     return False
class Tile():
    def __init__(self, letter, pos, size = 75, color = colorDict["grey"]):
        self.letter = letter
        self.pos = pos
        self.size = size
        self.color = color
        self.hide = False
        self.selected = False
        self.revealed = False

    def show_rect(self):
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size)
        rect.center = (self.pos[0], self.pos[1])
        if self.hide and not self.revealed:
            pygame.draw.rect(background, colorDict["lightgrey"], rect)
        elif self.selected and not self.revealed:
            pygame.draw.rect(background, colorDict["lightblue"], rect)
            #print(tile.letter)
        elif not self.hide and self.selected:
            pygame.draw.rect(background, colorDict["lightblue"], rect)
        else:
            pygame.draw.rect(background, self.color, rect)

    def show_text(self):
        font = pygame.font.SysFont("Arial", self.size, bold=True)
        text = font.render(self.letter, True, colorDict["white"])
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1]))
        background.blit(text, text_rect)

    def change_letter(self, event):
        key = pygame.key.name(event.key)
        if key.isalpha() and len(key) <= 1:
            self.letter = key.upper()

    def draw(self):
        self.show_rect()
        self.show_text()
        pygame.display.update()

    def click(self, pos):
        x1 = pos[0]
        y1 = pos[1]
        x, y = self.pos
        if x - self.size/2 <= x1 <= x + self.size/2 and y - self.size/2 <= y1 <= y + self.size/2:
            return True
        else:
            return False

    def highlight_tile(self, pos):
        if self.click(pos):
            self.selected = True

            #self.color = colorDict["lightblue"]
class Row():
    def __init__(self, level):
        self.level = level
        tiles = []
        tileSize = width // (numLetters + 2)
        self.xPointer = width // (numLetters)
        self.yPointer = tileSize + 2

        x = self.xPointer

        for l in range(numLetters):
            tile = Tile(letter = "", pos = (x, (self.level) * self.yPointer), size = tileSize)
            tiles.append(tile)
            x += tile.size + 2

        # for l in range(numLetters):
        #     tile = Tile(letter = "", pos = (xPointer, (yPos) * yPointer), size = tileSize)
        #     tiles.append(tile)
        #     xPointer += tile.size + 2

        self.tiles = tiles
        self.currentTile = 0

    def scroll(self, direction):
        x = self.xPointer
        for tile in self.tiles:
            if direction == "up":
                tile.pos = (x, (self.level - 1) * self.yPointer)
            elif direction == "down":
                tile.pos = (x, (self.level + 1) * self.yPointer)


    def draw(self, hide):
        for tile in self.tiles:
            if hide:
                tile.hide = True
            tile.draw()

    def check_typed(self):
        word = ""
        for tile in self.tiles:
            if tile.letter:
                word += tile.letter
        return word

    def change_letter(self, key):
        if key.isalpha() and len(key) == 1 and self.currentTile < numLetters:
            self.tiles[self.currentTile].letter = key.upper()
            if self.currentTile == numLetters:
                self.currentTile -= 1
            self.currentTile += 1
        elif key == "backspace" and self.currentTile > 0:
            self.currentTile -= 1
            self.tiles[self.currentTile].letter = ""
            if self.currentTile < 0:
                self.currentTile = 0

    def validate_word(self, usedLetters, correctWord):
        guess = ""
        for idx in range(numLetters):
            guess += self.tiles[idx].letter
        guess = guess.lower()

        if guess not in allWords:
            return ("invalid", usedLetters, guess)

        wrong = False

        correctFreq = Counter(correctWord)

        # account for greens
        for idx in range(numLetters):
            # letter match
            letter = self.tiles[idx].letter.lower()
            tile = self.tiles[idx]
            if letter == correctWord[idx]:
                tile.color = colorDict["green"]
                usedLetters[letter] = "green"
                correctFreq[letter] -= 1
                if correctFreq[letter] == 0:
                    del correctFreq[letter]
            else:
                wrong = True

        # account for yellows
        for idx in range(numLetters):
            letter = self.tiles[idx].letter.lower()
            tile = self.tiles[idx]
            #print(letter)
            if letter in correctFreq and tile.color != colorDict["green"]:
                tile.color = colorDict["yellow"]
                #print("yellow!")
                if letter not in usedLetters or usedLetters[letter] != "green":
                    usedLetters[letter] = "yellow"
                correctFreq[letter] -= 1
                if correctFreq[letter] == 0:
                    del correctFreq[letter]
            elif letter not in correctWord:
                usedLetters[letter] = "red"
            #print()
        if wrong:
            return ("wrong", usedLetters, guess)
        return ("correct", usedLetters, guess)

class Grid():
    def __init__(self, correctWord):
        rows = []
        level = 1
        for l in range(rowLimit):
            rows.append(Row(level))
            level += 1
        self.firstRow = 0 #index
        self.lastRow = rowLimit
        self.rows = rows
        self.level = 0
        self.correctWord = correctWord

    def draw(self, hide):
        for idx in range(self.firstRow, self.lastRow):
            self.rows[idx].draw(hide)
        # for row in self.rows:
        #     row.draw(hide)

    def update(self, key, usedLetters):
        # if self.level >= rowLimit:
        #     print(self.level)
        #     self.rows.append(Row(self.level))
        #     self.level += 1

        if key == "return" and self.rows[self.level].currentTile == numLetters:
            print(self.firstRow, self.lastRow, self.level)
            if self.level >= rowLimit - 1:
                self.level += 1
                self.rows.append(Row(self.level + 1))
                self.firstRow += 1
                self.lastRow += 1

            #print(self.level, self.firstRow, self.lastRow)
            result, updatedLetters, guess = self.rows[self.level].validate_word(usedLetters, self.correctWord)
            if result == "invalid":
                n = Notification(f"{guess} is not a valid word!", "alert")
                n.draw()
                #print(f"You silly billy, {guess} is not a valid word!")
            elif result == "wrong":
                self.level += 1
            else: # correct
                pass
        else:
            self.rows[self.level].change_letter(key)
        #return notification
class Key():
    def __init__(self, letter, pos, size, color = colorDict["lightgrey"]):
        self.letter = letter
        self.pos = pos
        self.size = size
        self.color = color
        self.hide = False
        self.revealed = False

    def show_rect(self):
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size, self.size + 5)
        rect.center = (self.pos[0], self.pos[1])
        if self.hide and not self.revealed:
            pygame.draw.rect(background, colorDict["lightgrey"], rect)
        else:
            pygame.draw.rect(background, self.color, rect)


    def show_text(self):
        font = pygame.font.SysFont("Arial", self.size, bold=True)
        text = font.render(self.letter, True, colorDict["black"])
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1]))
        background.blit(text, text_rect)

    def show_special(self):
        rect = pygame.Rect(self.pos[0], self.pos[1], self.size + 5, self.size + 5)
        rect.center = (self.pos[0], self.pos[1])
        pygame.draw.rect(background, self.color, rect)

        font = pygame.font.SysFont("Arial", self.size, bold=True)
        text = font.render(self.letter, True, colorDict["black"])
        text_rect = text.get_rect(center=(self.pos[0], self.pos[1]))
        background.blit(text, text_rect)

    def draw(self):
        if len(self.letter) > 1:
            self.show_special()
        else:
            self.show_rect()
            self.show_text()
        pygame.display.update()

    def click(self, pos):
        x, y = self.pos[0], self.pos[1]
        x1, y1 = pos[0], pos[1]
        # if x <= x1 <= x + self.size and y <= y1 <= y + self.size:
        #     return True
        if x - self.size/2 <= x1 <= x + self.size/2 and y - self.size/2 <= y1 <= y + self.size/2:
            return True
        else:
            return False
class KeyBoard():
    def __init__(self):
        self.keys = dict()
        keySize = 30
        yOffset = 5
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]

        r1, r2, r3 = rows

        xOffset = 50
        yOffset = keySize + 10
        for char in r1:
            letter = Key(letter=char, pos=(xOffset + keySize, yOffset + 550), size=keySize)
            xOffset += keySize + 5
            self.keys[char] = letter

        xOffset = 60
        yOffset += 40
        for char in r2:
            letter = Key(letter=char, pos=(xOffset + keySize, yOffset + 550), size=keySize)
            xOffset += keySize + 5
            self.keys[char] = letter

        xOffset = 90
        yOffset += 40
        # check = ✅
        enter = Key(letter= "ENT", pos=(xOffset - 5, yOffset + 550), size=20, color = (colorDict["green"]))
        self.keys["return"] = enter

        for char in r3:
            letter = Key(letter=char, pos=(xOffset + keySize, yOffset + 550), size=keySize)
            xOffset += keySize + 5
            self.keys[char] = letter
        # del = ⌫
        delete = Key(letter= "DEL", pos = (xOffset + keySize, yOffset + 550), size = 20, color = colorDict["red"])
        self.keys["backspace"] = delete

        self.usedLetters = dict()

    def update_letters(self, updatedLetters):
        self.usedLetters = updatedLetters

    def draw(self, hide):
        for letter, key in self.keys.items():
            letter = letter.lower()
            if letter in self.usedLetters:
                key.color = self.usedLetters[letter]
            if hide:
                key.hide = True
            key.draw()
class Notification():
    def __init__(self, text, kind = "neutral", fontSize = 15):
        self.x = width/2
        self.y = 5
        self.width = width - .25*width
        self.height = 30
        self.fontSize = fontSize
        self.text = text

        if kind == "warning":
            color = (253, 177, 150) # Maccaroni n cheese
        elif kind == "alert":
            color = (250, 210, 167) # Deep champagne
        elif kind == "neutral":
            color = (177, 217, 205)
        self.color = color

    # def update_color(self, kind):
    #     # notif color
    #     if kind == "warning":
    #         color = (253, 177, 150) # Maccaroni n cheese
    #     elif kind == "alert":
    #         color = (250, 210, 167) # Deep champagne
    #     elif kind == "neutral":
    #         color = (177, 217, 205) # Jet stream
    #     self.color = color

    def draw(self):
        #self.update_color(kind)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        rect.center = (self.x, self.y)
        pygame.draw.rect(background, self.color, rect)

        font = pygame.font.SysFont("Arial", self.fontSize)
        text = font.render(self.text, 1, colorDict["black"])
        text_rect = text.get_rect(center=(self.x, self.y + 5))
        background.blit(text, text_rect)

def play_game(game, p, btns):
    win = background
    font = pygame.font.SysFont("comicsans", 20)
    word1, word2 = game.words[0], game.words[1]

    if not (game.connected()):
        notif = Notification("Waiting for other player to join...")
        notif.draw()
    else:
        switchBoard, lockInfo, randWord, up, down = btns
        if game.readyToSend[p]:
            lockInfo.color = colorDict["green"]
        randWord.draw()
        switchBoard.draw()
        lockInfo.draw()
        up.draw()
        down.draw()

        # Turn taking
        oppWord = Notification(f"Opponents word: {game.words[1-p]}  Mode: {game.mode}", fontSize = 9)
        oppWord.y = 30
        oppWord.draw()

        if game.mode == "guess":
            if game.playerGrids[p].level == 1 + game.playerGrids[1-p].level:
                notif = Notification("Your move has been locked in. Waiting for the other player.")
            elif game.playerGrids[p].level == game.playerGrids[1-p].level:
                notif = Notification("Guess the word!")
            elif game.playerGrids[p].level == game.playerGrids[1-p].level - 1:
                notif = Notification("Your opponent has locked in their move. Waiting on you!", "alert")
            notif.draw()

        elif game.mode == "validate":
            if game.bothSentInfo[p] and not game.bothSentInfo[1-p]:
                notif = Notification("Your move has been locked in. Waiting for the other player")
            elif not game.bothSentInfo[p] and game.bothSentInfo[1-p]:
                notif = Notification("Your opponent has locked in their move. Waiting on you!", "alert")
            elif game.bothSentInfo == [False, False]:
                notif = Notification("Validate your opponents word! Click Opponents Board.")
            else:
                notif = Notification("")
            notif.draw()

        if game.playerViews[p] == 0:
            game.playerKeyboards[p].draw(hide=True)
            game.playerGrids[p].draw(hide=True)
        else:
            game.playerKeyboards[1 - p].draw(hide=False)
            game.playerGrids[1 - p].draw(hide=False)

    pygame.display.update()
