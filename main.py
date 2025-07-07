import pyxel
from grid import Grid


class Game:
    def __init__(self):
        pyxel.init(256, 224, title="Hex Minesweeper", display_scale=2)
        self.grid = Grid(width=16, height=10, hex_size=10, mine_count=30)
        pyxel.run(self.update, self.draw)

    def update(self):
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        if pyxel.btnp(pyxel.KEY_R):
            self.grid.restart()
        self.grid.handle_input()

    def draw(self):
        pyxel.cls(0)
        self.grid.draw()
        # Draw cursor
        pyxel.line(
            pyxel.mouse_x - 3, pyxel.mouse_y, pyxel.mouse_x + 3, pyxel.mouse_y, 3
        )  # Horizontal line
        pyxel.line(
            pyxel.mouse_x, pyxel.mouse_y - 3, pyxel.mouse_x, pyxel.mouse_y + 3, 3
        )  # Vertical line


Game()
