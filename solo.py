import pygame
from infra import KeyBoard, Grid, Button, colorDict, choose_word

word = choose_word()
word = "cacao"
grid = Grid(word)
keyboard = KeyBoard()
randWord = Button("hehe", (100, 540), (60, 40), colorDict["red"], 15)

def main():
    run = True
    clock = pygame.time.Clock()
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                key = pygame.key.name(event.key)
                grid.update(key, keyboard.usedLetters)

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                # game = n.send(f"clickLetter{pos}")

                if randWord.click(pos):
                    word = choose_word()
                    for letter in word:
                        grid.update(letter, keyboard.usedLetters)
        keyboard.draw(hide = False)
        grid.draw(hide = False)
        randWord.draw()
main()