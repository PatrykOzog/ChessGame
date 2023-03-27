from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QApplication, QGraphicsEllipseItem, \
    QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPixmap
from PyQt5.QtCore import Qt
import sys
import numpy as np


class ChessScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSceneRect(0, 0, 1500, 800)
        all_pieces = []

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
            all_pieces.append(('w', 'pawn', i * 100, 100))
            w_pawn = ChessPiece('w', 'pawn', i * 100, 100, all_pieces)
            self.addItem(w_pawn)

        white_start_pos = [('w_rook', (0, 0)), ('w_knight', (100, 0)), ('w_bishop', (200, 0)), ('w_queen', (300, 0)),
                           ('w_king', (400, 0)), ('w_bishop', (500, 0)), ('w_knight', (600, 0)), ('w_rook', (700, 0))]

        for name, pos in white_start_pos:
            all_pieces.append(('w', name.split('_')[1], pos[0], pos[1]))
            piece = ChessPiece('w', name.split('_')[1], pos[0], pos[1], all_pieces)
            self.addItem(piece)


class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, color, piece_type, x_pos, y_pos, all_pieces, parent=None):
        super().__init__(parent)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.piece_type = piece_type
        self.possible_moves = []
        self.move_rects = []
        self.all_pieces = all_pieces
        self.setPixmap(QPixmap(f'Pieces/{self.color}_{self.piece_type}.png').scaled(100, 100))
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setPos(self.x_pos, self.y_pos)
        self.setZValue(1)

    def mousePressEvent(self, event):
        self.x_pos = self.pos().x()
        self.y_pos = self.pos().y()
        getattr(self, f"{self.piece_type}_movement")()
        self.color_possible_moves()
        print(self.all_pieces)
        super().mousePressEvent(event)

    def mouseReleaseEvent(self, event):
        x = round(self.pos().x() / 100) * 100
        y = round(self.pos().y() / 100) * 100
        if 0 <= x <= 700 and 0 <= y <= 700 and (x, y) in self.possible_moves:
            self.setPos(x, y)
        else:
            self.setPos(self.x_pos, self.y_pos)

        for move_rect in self.move_rects:
            self.scene().removeItem(move_rect)

        super().mouseReleaseEvent(event)

    def color_possible_moves(self):
        for possible_move in self.possible_moves:
            if 0 <= possible_move[0] <= 700 and 0 <= possible_move[1] <= 700:
                self.move_rects.append(QGraphicsRectItem(possible_move[0], possible_move[1], 100, 100))

        for move_rect in self.move_rects:
            move_rect.setBrush(QColor(255, 255, 0))
            self.scene().addItem(move_rect)

    def pawn_movement(self):
        self.move_rects.clear()
        self.possible_moves = [(self.x_pos, self.y_pos+100)]

    def rook_movement(self):
        self.move_rects.clear()
        self.possible_moves.clear()
        for i in range(8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos))
            self.possible_moves.append((self.x_pos + 100 * -i, self.y_pos))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * -i))

        for piece in self.all_pieces:
            if (piece[2], piece[3]) in self.possible_moves:
                print("he")

    def bishop_movement(self):
        self.move_rects.clear()
        self.possible_moves.clear()
        for i in range(8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos - 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos - 100 * i))

    def knight_movement(self):
        self.move_rects.clear()
        self.possible_moves = [(self.x_pos + 200, self.y_pos + 100), (self.x_pos + 200, self.y_pos - 100),
                               (self.x_pos - 200, self.y_pos + 100), (self.x_pos - 200, self.y_pos - 100),
                               (self.x_pos + 100, self.y_pos + 200), (self.x_pos + 100, self.y_pos - 200),
                               (self.x_pos - 100, self.y_pos + 200), (self.x_pos - 100, self.y_pos - 200)]

    def queen_movement(self):
        self.move_rects.clear()
        self.possible_moves.clear()
        for i in range(8):
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos))
            self.possible_moves.append((self.x_pos + 100 * -i, self.y_pos))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos, self.y_pos + 100 * -i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos + 100 * i))
            self.possible_moves.append((self.x_pos + 100 * i, self.y_pos - 100 * i))
            self.possible_moves.append((self.x_pos - 100 * i, self.y_pos - 100 * i))

    def king_movement(self):
        self.move_rects.clear()
        self.possible_moves = [(self.x_pos + 100, self.y_pos + 100), (self.x_pos - 100, self.y_pos - 100),
                               (self.x_pos + 100, self.y_pos - 100), (self.x_pos - 100, self.y_pos + 100),
                               (self.x_pos + 100, self.y_pos), (self.x_pos - 100, self.y_pos),
                               (self.x_pos, self.y_pos + 100), (self.x_pos, self.y_pos - 100)]


class ChessView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(ChessScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(1920, 1080)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = ChessView()
    view.show()
    sys.exit(app.exec())
