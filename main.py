from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QApplication, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QTextEdit
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap, QFont, QKeyEvent
from PyQt5.QtCore import Qt, QEvent
import sys
import numpy as np

#First_move bugged

class ChessScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.stop_x = None
        self.stop_y = None
        self.text = None
        self.setSceneRect(0, 0, 1500, 800)
        self.all_pieces = []
        self.pieces_id = []
        self.start_pos = [('b_rook', (0, 0)), ('b_knight', (100, 0)), ('b_bishop', (200, 0)), ('b_queen', (300, 0)),
                          ('b_king', (400, 0)), ('b_bishop', (500, 0)), ('b_knight', (600, 0)), ('b_rook', (700, 0)),
                          ('w_rook', (0, 700)), ('w_knight', (100, 700)), ('w_bishop', (200, 700)),
                          ('w_queen', (300, 700)), ('w_king', (400, 700)), ('w_bishop', (500, 700)),
                          ('w_knight', (600, 700)), ('w_rook', (700, 700))]

        self.row_values = {'a': 0, 'b': 100, 'c': 200, 'd': 300, 'e': 400, 'f': 500, 'g': 600, 'h': 700}
        self.col_values = {'1': 0, '2': 100, '3': 200, '4': 300, '5': 400, '6': 500, '7': 600, '8': 700}
        self.figures_values = {'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight', '': 'pawn'}
        self.special_symbols = {'': 'no_check', '+': 'check'}

        self.create_starting_board()

        self.textedit = QTextEdit()
        self.textedit.setGeometry(1200, 800, 500, 50)
        self.textedit.setFontPointSize(16)
        self.textedit.installEventFilter(self)
        self.addWidget(self.textedit)

    def eventFilter(self, obj, event):
        if obj == self.textedit and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            self.text = self.textedit.toPlainText().strip()
            print(f"Entered text: {self.text}")
            try:
                part_one, part_two = self.text.split("-")[0], self.text.split("-")[1]
                piece_type = self.figures_values[part_one[-3:-2]]
                x_pos = self.row_values[part_one[-2:-1]]
                y_pos = self.col_values[part_one[-1]]
                self.stop_x = self.row_values[part_two[0]]
                self.stop_y = self.col_values[part_two[1]]
                color = "w"
                if (color, piece_type, x_pos, y_pos) in self.all_pieces:
                    new_piece = ChessPiece(color, piece_type, x_pos, y_pos, self)
                    for i, piece in enumerate(self.all_pieces):
                        if (piece[2], piece[3]) == (x_pos, y_pos):
                            self.removeItem(self.pieces_id[i])
                            del self.pieces_id[i]
                            del self.all_pieces[i]
                            self.addItem(new_piece)
                            self.pieces_id.append(new_piece)
                            self.all_pieces.append((color, piece_type, self.stop_x, self.stop_y))
                            break
            except:
                print("wrong")

            self.textedit.clear()
            return True
        return False

    def create_starting_board(self):
        x, y = np.meshgrid(np.arange(8), np.arange(8))
        colors = np.where((x + y) % 2 == 0, QColor(255, 255, 255), QColor(0, 0, 0))
        rects = [QGraphicsRectItem(i * 100, j * 100, 100, 100) for i, j in zip(x.flat, y.flat)]
        for rect, color in zip(rects, colors.flat):
            rect.setBrush(QBrush(color))
            self.addItem(rect)

        letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        for i in range(8):
            text = QGraphicsTextItem(str(i + 1))
            text.setPos(-35, i * 100 + 35)
            text.setScale(2)
            self.addItem(text)

            text = QGraphicsTextItem(letters[i])
            text.setPos(i * 100 + 35, -40)
            text.setScale(2)
            self.addItem(text)

            piece = ChessPiece('b', 'pawn', i * 100, 100, self)
            self.all_pieces.append(('b', 'pawn', i * 100, 100))
            self.pieces_id.append(piece)
            self.addItem(piece)
            piece = ChessPiece('w', 'pawn', i * 100, 600, self)
            self.all_pieces.append(('w', 'pawn', i * 100, 600))
            self.pieces_id.append(piece)
            self.addItem(piece)

        for name, pos in self.start_pos:
            piece = ChessPiece(name.split('_')[0], name.split('_')[1], pos[0], pos[1], self)
            self.all_pieces.append((name.split('_')[0], name.split('_')[1], pos[0], pos[1]))
            self.pieces_id.append(piece)
            self.addItem(piece)


class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, color, piece_type, x_pos, y_pos, chess_scene, parent=None):
        super().__init__(parent)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.piece_type = piece_type
        self.chess_scene = chess_scene
        self.possible_moves = []
        self.move_rects = []
        self.first_move = True
        self.setPixmap(QPixmap(f'Pieces/{self.color}_{self.piece_type}.png').scaled(100, 100))
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setPos(self.x_pos, self.y_pos)
        self.setZValue(1)
        if self.chess_scene.text is not None:
            self.move_from_chat()

    def move_from_chat(self):
        getattr(self, f"{self.piece_type}_movement")()
        if (self.chess_scene.stop_x, self.chess_scene.stop_y) in self.possible_moves:
            self.setPos(self.chess_scene.stop_x, self.chess_scene.stop_y)
        else:
            raise ValueError

    def mousePressEvent(self, event):
        self.x_pos = self.pos().x()
        self.y_pos = self.pos().y()
        self.move_rects.clear()
        getattr(self, f"{self.piece_type}_movement")()
        self.color_possible_moves()
        self.setZValue(2)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        x = round(self.pos().x() / 100) * 100
        y = round(self.pos().y() / 100) * 100
        if 0 <= x <= 700 and 0 <= y <= 700 and (x, y) in self.possible_moves:
            for i, piece in enumerate(self.chess_scene.all_pieces):
                if (piece[2], piece[3]) == (x, y):
                    self.scene().removeItem(self.chess_scene.pieces_id[i])
                    del self.chess_scene.pieces_id[i]
                    del self.chess_scene.all_pieces[i]

            self.setPos(x, y)
            self.update_pieces(x, y)
            self.first_move = False
        else:
            self.setPos(self.x_pos, self.y_pos)

        for move_rect in self.move_rects:
            self.scene().removeItem(move_rect)

        self.setZValue(1)
        super().mouseReleaseEvent(event)

    def update_pieces(self, x, y):
        piece_index = self.chess_scene.all_pieces.index((self.color, self.piece_type, self.x_pos, self.y_pos))
        self.chess_scene.all_pieces[piece_index] = (self.color, self.piece_type, x, y)

    def color_possible_moves(self):
        for possible_move in self.possible_moves:
            if 0 <= possible_move[0] <= 700 and 0 <= possible_move[1] <= 700:
                self.move_rects.append(QGraphicsRectItem(possible_move[0], possible_move[1], 100, 100))

        for move_rect in self.move_rects:
            move_rect.setBrush(QColor(255, 255, 0))
            self.scene().addItem(move_rect)

    def del_impossible_moves(self, directions):
        for piece in self.chess_scene.all_pieces:
            if (piece[2], piece[3]) in self.possible_moves:
                if piece[0] == self.color:
                    start_index = self.possible_moves.index((piece[2], piece[3]))
                    for index in range(start_index, len(self.possible_moves), directions):
                        self.possible_moves[index] = (-1, -1)
                else:
                    start_index = self.possible_moves.index((piece[2], piece[3])) + directions
                    for index in range(start_index, len(self.possible_moves), directions):
                        self.possible_moves[index] = (-1, -1)

    def pawn_movement(self):
        if self.color == "b":
            self.possible_moves = [(self.x_pos, self.y_pos + 100)]
            if self.first_move:
                self.possible_moves.append((self.x_pos, self.y_pos + 200))
            for piece in self.chess_scene.all_pieces:
                if (piece[2], piece[3]) in self.possible_moves:
                    index = self.possible_moves.index((piece[2], piece[3]))
                    self.possible_moves[index] = (-1, -1)
                    if self.first_move:
                        self.possible_moves[index + 1] = (-1, -1)
                if (piece[2], piece[3]) == (self.x_pos + 100, self.y_pos + 100) and piece[0] != self.color:
                    self.possible_moves.append((self.x_pos + 100, self.y_pos + 100))
                if (piece[2], piece[3]) == (self.x_pos - 100, self.y_pos + 100) and piece[0] != self.color:
                    self.possible_moves.append((self.x_pos - 100, self.y_pos + 100))
        elif self.color == "w":
            self.possible_moves = [(self.x_pos, self.y_pos - 100)]
            if self.first_move:
                self.possible_moves.append((self.x_pos, self.y_pos - 200))
            for piece in self.chess_scene.all_pieces:
                if (piece[2], piece[3]) in self.possible_moves:
                    index = self.possible_moves.index((piece[2], piece[3]))
                    self.possible_moves[index] = (-1, -1)
                    if self.first_move:
                        self.possible_moves[index + 1] = (-1, -1)
                if (piece[2], piece[3]) == (self.x_pos + 100, self.y_pos - 100) and piece[0] != self.color:
                    self.possible_moves.append((self.x_pos + 100, self.y_pos - 100))
                if (piece[2], piece[3]) == (self.x_pos - 100, self.y_pos - 100) and piece[0] != self.color:
                    self.possible_moves.append((self.x_pos - 100, self.y_pos - 100))

    def rook_movement(self):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos))
            self.possible_moves.append((self.x_pos + 100 * -i, self.y_pos))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * -i))

        self.del_impossible_moves(4)

    def bishop_movement(self):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos - 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos - 100 * i))

        self.del_impossible_moves(4)

    def knight_movement(self):
        self.possible_moves = [(self.x_pos + 200, self.y_pos + 100), (self.x_pos + 200, self.y_pos - 100),
                               (self.x_pos - 200, self.y_pos + 100), (self.x_pos - 200, self.y_pos - 100),
                               (self.x_pos + 100, self.y_pos + 200), (self.x_pos + 100, self.y_pos - 200),
                               (self.x_pos - 100, self.y_pos + 200), (self.x_pos - 100, self.y_pos - 200)]

        self.del_impossible_moves(10)

    def queen_movement(self):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos))
            self.possible_moves.append((self.x_pos + 100 * -i, self.y_pos))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * -i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos - 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos - 100 * i))

        self.del_impossible_moves(8)

    def king_movement(self):
        self.possible_moves = [(self.x_pos + 100, self.y_pos + 100), (self.x_pos - 100, self.y_pos - 100),
                               (self.x_pos + 100, self.y_pos - 100), (self.x_pos - 100, self.y_pos + 100),
                               (self.x_pos + 100, self.y_pos), (self.x_pos - 100, self.y_pos),
                               (self.x_pos, self.y_pos + 100), (self.x_pos, self.y_pos - 100)]

        self.del_impossible_moves(10)


class ChessView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(ChessScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(1920, 1080)

    # def process_input(self):
    #     text = self.textbox.text()
    #     row_values = {'a': 0, 'b': 100, 'c': 200, 'd': 300, 'e': 400, 'f': 500, 'g': 600, 'h': 700}
    #     col_values = {'1': 0, '2': 100, '3': 200, '4': 300, '5': 400, '6': 500, '7': 600, '8': 700}
    #     figures_values = {'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight', '': 'pawn'}
    #     special_symbols = {'': 'no_check', '+': 'check'}
    #     part_one, part_two = text.split("-")[0], text.split("-")[1]
    #     try:
    #         ChessPiece.move_with_chat(text, str(figures_values[part_one[-3:-2]]), row_values[part_one[-2:-1]],
    #                                   col_values[part_one[-1]], row_values[part_two[0]], col_values[part_two[1]])
    #     except:
    #         print("wrong")
    #     self.textbox.clear()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ChessView()
    view.show()
    sys.exit(app.exec())
