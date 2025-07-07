import pyxel
import math
import random
from cell import Cell


class Grid:
    def __init__(self, width, height, hex_size, mine_count):
        self.width = width  # Number of columns in offset coordinates
        self.height = height  # Number of rows in offset coordinates
        self.hex_size = hex_size
        self.mine_count = mine_count
        self.flag_count = 0
        self.game_over = False
        self.game_won = False
        self.first_click = True
        self.start_time = None
        self.end_time = None
        self.cells = {}
        self._populate_cells()

        # Calculate offsets for centering the grid (flat-top hexes)
        # Width of a hex: 2 * hex_size
        # Height of a hex: sqrt(3) * hex_size
        # Horizontal spacing between hex centers: 1.5 * hex_size
        # Vertical spacing between hex centers: sqrt(3) * hex_size
        grid_pixel_width = (self.width * 1.5 + 0.5) * self.hex_size
        grid_pixel_height = (
            self.height * math.sqrt(3) + 0.5 * math.sqrt(3)
        ) * self.hex_size
        self.offset_x = (pyxel.width - grid_pixel_width) / 2 + 10
        self.offset_y = (pyxel.height - grid_pixel_height) / 2 + 30

    def _populate_cells(self):
        for col in range(self.width):
            for row in range(self.height):
                q, r = self._offset_to_axial(col, row)
                self.cells[(q, r)] = Cell(q, r)

    def restart(self):
        self.game_over = False
        self.game_won = False
        self.flag_count = 0
        self.first_click = True
        self.start_time = None
        self.end_time = None
        self.cells = {}
        self._populate_cells()

    def _offset_to_axial(self, col, row):
        q = col
        r = row - (col + (col & 1)) // 2
        return q, r

    def _axial_to_offset(self, q, r):
        col = q
        row = r + (q + (q & 1)) // 2
        return col, row

    def _hex_to_pixel(self, q, r):
        x = self.hex_size * (3 / 2 * q)
        y = self.hex_size * (math.sqrt(3) * r + math.sqrt(3) / 2 * q)
        return x, y

    def _initialize_mines(self, initial_q, initial_r):
        forbidden_cells = set()
        forbidden_cells.add((initial_q, initial_r))
        for dq, dr in [
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1),
        ]:  # Flat-top neighbors
            nq, nr = initial_q + dq, initial_r + dr
            if (nq, nr) in self.cells:
                forbidden_cells.add((nq, nr))

        mines_placed = 0
        available_cells = list(self.cells.keys())
        while mines_placed < self.mine_count and available_cells:
            q, r = random.choice(available_cells)
            if (q, r) not in forbidden_cells and not self.cells[(q, r)].has_mine:
                self.cells[(q, r)].has_mine = True
                mines_placed += 1
            available_cells.remove((q, r))
        self._calculate_neighbor_mine_counts()
        self.start_time = pyxel.frame_count

    def _place_mines(self):
        # This method is no longer called directly from __init__ or restart
        pass

    def _calculate_neighbor_mine_counts(self):
        for cell_coords in self.cells:
            q, r = cell_coords
            if not self.cells[(q, r)].has_mine:
                self.cells[(q, r)].neighbor_mine_count = self._count_neighbor_mines(
                    q, r
                )

    def _count_neighbor_mines(self, q, r):
        count = 0
        for dq, dr in [
            (1, 0),
            (0, 1),
            (-1, 1),
            (-1, 0),
            (0, -1),
            (1, -1),
        ]:  # Flat-top neighbors
            nq, nr = q + dq, r + dr
            if (nq, nr) in self.cells and self.cells[(nq, nr)].has_mine:
                count += 1
        return count

    def draw(self):
        for cell_coords in self.cells:
            q, r = cell_coords
            x, y = self._hex_to_pixel(q, r)
            self.draw_hexagon(
                x + self.offset_x,
                y + self.offset_y,
                self.hex_size,
                self.cells[cell_coords],
            )

        if self.game_over:
            pyxel.text(110, 5, "GAME OVER", 8)
            for cell_coords in self.cells:
                q, r = cell_coords
                cell = self.cells[cell_coords]
                if cell.has_mine:
                    x, y = self._hex_to_pixel(q, r)
                    pyxel.circ(
                        x + self.offset_x, y + self.offset_y, self.hex_size / 4, 8
                    )  # Draw a red circle for mine
            pyxel.text(90, 15, "Press R to restart", 7)
        elif self.game_won:
            pyxel.text(110, 5, "YOU WIN!", 7)
            pyxel.text(90, 15, "Press R to restart", 7)

        pyxel.text(5, 5, f"MINES: {self.mine_count}", 7)
        pyxel.text(5, 15, f"FLAGS: {self.flag_count}", 7)

        if self.start_time is None:
            pyxel.text(5, 25, "TIME: 0s", 7)
        if self.start_time is not None and self.end_time is None:
            elapsed_time = (
                pyxel.frame_count - self.start_time
            ) // 30  # Convert frames to seconds (assuming 30 FPS)
            pyxel.text(5, 25, f"TIME: {elapsed_time}s", 7)
        elif self.end_time is not None:
            clear_time = (self.end_time - self.start_time) // 30
            pyxel.text(5, 25, f"TIME: {clear_time}s", 7)

    def draw_hexagon(self, x, y, size, cell):
        color = 7  # Default color (white)
        if cell.is_revealed:
            if cell.has_mine:
                color = 8  # Red for mine
            else:
                color = 5  # Green for revealed
        elif cell.is_flagged:
            color = 10  # Yellow for flagged
        else:
            color = 1  # Dark blue for unrevealed

        for i in range(6):
            angle1 = math.pi / 3 * i
            angle2 = math.pi / 3 * (i + 1)
            x1 = x + size * math.cos(angle1)
            y1 = y + size * math.sin(angle1)
            x2 = x + size * math.cos(angle2)
            y2 = y + size * math.sin(angle2)
            pyxel.tri(x, y, x1, y1, x2, y2, color)
            pyxel.line(x1, y1, x2, y2, 0)  # Draw border in black

        if cell.is_revealed and not cell.has_mine and cell.neighbor_mine_count > 0:
            pyxel.text(x - size / 4, y - size / 4, str(cell.neighbor_mine_count), 7)

    def handle_input(self):
        if self.game_over or self.game_won:
            return

        if pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT):
            q, r = self._pixel_to_hex(pyxel.mouse_x, pyxel.mouse_y)
            if (q, r) in self.cells:
                if self.first_click:
                    self._initialize_mines(q, r)
                    self.first_click = False
                self.reveal_cell(q, r)
                self.check_win_condition()

        if pyxel.btnp(pyxel.MOUSE_BUTTON_RIGHT):
            q, r = self._pixel_to_hex(pyxel.mouse_x, pyxel.mouse_y)
            if (q, r) in self.cells:
                cell = self.cells[(q, r)]
                if not cell.is_revealed:
                    if cell.is_flagged:
                        cell.is_flagged = False
                        self.flag_count -= 1
                    else:
                        cell.is_flagged = True
                        self.flag_count += 1

    def reveal_cell(self, q, r):
        cell = self.cells.get((q, r))
        if cell is None or cell.is_revealed or cell.is_flagged:
            return

        cell.is_revealed = True
        if cell.has_mine:
            self.game_over = True
            self.end_time = pyxel.frame_count
        elif cell.neighbor_mine_count == 0:
            for dq, dr in [
                (1, 0),
                (0, 1),
                (-1, 1),
                (-1, 0),
                (0, -1),
                (1, -1),
            ]:  # Flat-top neighbors
                nq, nr = q + dq, r + dr
                self.reveal_cell(nq, nr)

    def check_win_condition(self):
        for cell in self.cells.values():
            if not cell.has_mine and not cell.is_revealed:
                return
        self.game_won = True
        self.end_time = pyxel.frame_count

    def _pixel_to_hex(self, x, y):
        # Adjust for offset
        x -= self.offset_x
        y -= self.offset_y

        # Flat-top pixel to axial hex conversion
        q = (x * 2 / 3) / self.hex_size
        r = (-x / 3 + y * math.sqrt(3) / 3) / self.hex_size

        return self._hex_round(q, r)

    def _hex_round(self, q, r):
        s = -q - r
        rq = round(q)
        rr = round(r)
        rs = round(s)
        q_diff = abs(rq - q)
        r_diff = abs(rr - r)
        s_diff = abs(rs - s)
        if q_diff > r_diff and q_diff > s_diff:
            rq = -rr - rs
        elif r_diff > s_diff:
            rr = -rq - rs
        return int(rq), int(rr)
