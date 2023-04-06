from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QApplication, QVBoxLayout, \
    QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QTextEdit, QDialog, QPushButton, QGraphicsProxyWidget
from PyQt5.QtGui import QBrush, QColor, QPainter, QPixmap
from PyQt5.QtCore import Qt, QEvent, QTimer, QTime, QResource
import sys
import numpy as np
from pieces import *


class ChessScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.w_moved = False
        self.b_moved = False
        self.number = 1
        self.seconds = 120
        self.capture_row = 0
        self.setSceneRect(0, 0, 1600, 900)
        self.current_turn = "w"
        self.all_pieces = []
        self.pieces_id = []
        self.special_symbols = {'': 'no_check', '+': 'check'}
        self.figures_values = {'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight', '': 'pawn'}
        self.row_values = {'a': 0, 'b': 100, 'c': 200, 'd': 300, 'e': 400, 'f': 500, 'g': 600, 'h': 700}
        self.col_values = {'1': 0, '2': 100, '3': 200, '4': 300, '5': 400, '6': 500, '7': 600, '8': 700}
        self.start_pos = [('b_rook', (0, 0)), ('b_knight', (100, 0)), ('b_bishop', (200, 0)), ('b_queen', (300, 0)),
                          ('b_king', (400, 0)), ('b_bishop', (500, 0)), ('b_knight', (600, 0)), ('b_rook', (700, 0)),
                          ('w_rook', (0, 700)), ('w_knight', (100, 700)), ('w_bishop', (200, 700)),
                          ('w_queen', (300, 700)), ('w_king', (400, 700)), ('w_bishop', (500, 700)),
                          ('w_knight', (600, 700)), ('w_rook', (700, 700))]

        self.create_starting_board()

        # Text box
        self.textedit = QTextEdit()
        self.textedit.setGeometry(1000, 600, 350, 50)
        self.textedit.setFontPointSize(16)
        self.textedit.installEventFilter(self)
        self.addWidget(self.textedit)

        # White timer
        self.w_timer_widget = QTextEdit()
        self.w_timer_widget.setGeometry(1000, 200, 150, 50)
        self.w_timer_widget.setFontPointSize(20)
        self.w_timer_widget.setReadOnly(True)
        self.addWidget(self.w_timer_widget)
        self.w_timer = QTimer(self)
        self.w_timer.setInterval(1)
        self.w_timer.timeout.connect(self.update_timer)
        self.w_time_left = self.seconds * 1000 + 1
        self.update_timer()
        self.w_timer.start()

        # White button
        self.w_button = QPushButton("White button")
        self.w_button.setGeometry(1000, 100, 150, 50)
        self.w_button.setStyleSheet("font-size: 16px;")
        self.w_button_proxy = QGraphicsProxyWidget()
        self.w_button_proxy.setWidget(self.w_button)
        self.addItem(self.w_button_proxy)
        self.w_button.clicked.connect(self.w_button_clicked)

        # Black timer
        self.b_timer_widget = QTextEdit()
        self.b_timer_widget.setGeometry(1200, 200, 150, 50)
        self.b_timer_widget.setFontPointSize(20)
        self.b_timer_widget.setReadOnly(True)
        self.addWidget(self.b_timer_widget)
        self.b_timer = QTimer(self)
        self.b_timer.setInterval(1)
        self.b_timer.timeout.connect(self.update_timer)
        self.b_time_left = self.seconds * 1000 + 1
        self.update_timer()

        # Black button
        self.b_button = QPushButton("Black button")
        self.b_button.setGeometry(1200, 100, 150, 50)
        self.b_button.setStyleSheet("font-size: 16px;")
        self.b_button_proxy = QGraphicsProxyWidget()
        self.b_button_proxy.setWidget(self.b_button)
        self.addItem(self.b_button_proxy)
        self.b_button.clicked.connect(self.b_button_clicked)

    def open_new_window(self, color, x, y):
        self.dialog = QDialog()
        self.dialog.setModal(False)
        layout = QVBoxLayout()
        queen = QPushButton("Queen")
        queen.setObjectName("queen")
        rook = QPushButton("Rook")
        rook.setObjectName("rook")
        bishop = QPushButton("Bishop")
        bishop.setObjectName("bishop")
        knight = QPushButton("Knight")
        knight.setObjectName("knight")
        layout.addWidget(queen)
        layout.addWidget(rook)
        layout.addWidget(bishop)
        layout.addWidget(knight)

        queen.clicked.connect(lambda: self.promotion_button(color, x, y))
        rook.clicked.connect(lambda: self.promotion_button(color, x, y))
        bishop.clicked.connect(lambda: self.promotion_button(color, x, y))
        knight.clicked.connect(lambda: self.promotion_button(color, x, y))

        def closeEvent(event):
            event.ignore()

        self.dialog.closeEvent = closeEvent
        self.dialog.setLayout(layout)
        self.dialog.exec()

    def promotion_button(self, color, x, y):
        button = self.sender()
        choice = button.objectName()
        piece = ChessPiece(color, choice, x, y, self)
        index = self.all_pieces.index((color, "pawn", x, y))
        self.all_pieces[index] = (color, choice, x, y)
        self.pieces_id[index] = piece
        self.addItem(piece)
        self.dialog.accept()

    def w_button_clicked(self):
        if (self.w_moved or self.b_moved) and self.current_turn == "w":
            self.w_timer.stop()
            self.b_timer.start()
            self.current_turn = "b"
            self.w_moved = False

    def b_button_clicked(self):
        if (self.w_moved or self.b_moved) and self.current_turn == "b":
            self.b_timer.stop()
            self.w_timer.start()
            self.current_turn = "w"
            self.b_moved = False

    def update_timer(self):
        time_left = getattr(self, self.current_turn + "_time_left")
        timer = getattr(self, self.current_turn + "_timer")
        timer_widget = getattr(self, self.current_turn + "_timer_widget")
        setattr(self, self.current_turn + "_time_left", time_left - 1)
        if time_left < 0:
            timer.stop()
        else:
            minutes = time_left // 60000
            seconds = (time_left // 1000) % 60
            millisecs = time_left % 1000
            time_str = QTime(0, minutes, seconds, millisecs).toString('mm:ss.zzz')
            timer_widget.setText(time_str)

    # When enter is clicked
    def eventFilter(self, obj, event):
        if obj == self.textedit and event.type() == QEvent.KeyPress and event.key() == Qt.Key_Return:
            text = self.textedit.toPlainText().strip()
            try:
                if not self.w_moved and not self.b_moved:
                    part_one, part_two = text.split("-")[0], text.split("-")[1]
                    piece_type = self.figures_values[part_one[-3:-2]]
                    x_pos = self.row_values[part_one[-2:-1]]
                    y_pos = self.col_values[part_one[-1]]
                    stop_x = self.row_values[part_two[0]]
                    stop_y = self.col_values[part_two[1]]
                    color = self.current_turn
                    if (color, piece_type, x_pos, y_pos) in self.all_pieces:
                        index = self.all_pieces.index((color, piece_type, x_pos, y_pos))
                        piece = ChessPiece(color, piece_type, x_pos, y_pos, self)
                        piece.move_from_chat(index, stop_x, stop_y)
            except:
                pass

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
            # Create board numbers
            text = QGraphicsTextItem(str(i + 1))
            text.setPos(-35, i * 100 + 35)
            text.setScale(2)
            self.addItem(text)

            # Create board letters
            text = QGraphicsTextItem(letters[i])
            text.setPos(i * 100 + 35, -40)
            text.setScale(2)
            self.addItem(text)

            # Create black pawns
            piece = ChessPiece('b', 'pawn', i * 100, 100, self)
            self.all_pieces.append(('b', 'pawn', i * 100, 100))
            self.pieces_id.append(piece)
            self.addItem(piece)

            # Create white pawns
            piece = ChessPiece('w', 'pawn', i * 100, 600, self)
            self.all_pieces.append(('w', 'pawn', i * 100, 600))
            self.pieces_id.append(piece)
            self.addItem(piece)

        for name, pos in self.start_pos:
            piece = ChessPiece(name.split('_')[0], name.split('_')[1], pos[0], pos[1], self)
            self.all_pieces.append((name.split('_')[0], name.split('_')[1], pos[0], pos[1]))
            self.pieces_id.append(piece)
            self.addItem(piece)

    # Change skin by double clicking
    def mouseDoubleClickEvent(self, event):
        if self.number == 1:
            self.number = 2
        else:
            self.number = 1
        for i, piece in enumerate(self.all_pieces):
            self.removeItem(self.pieces_id[i])
            new_piece = ChessPiece(piece[0], piece[1], piece[2], piece[3], self)
            self.pieces_id[i] = new_piece
            self.addItem(new_piece)


class ChessPiece(QGraphicsPixmapItem):
    def __init__(self, color, piece_type, x_pos, y_pos, chess_scene, parent=None):
        super().__init__(parent)
        self.x_pos = x_pos
        self.y_pos = y_pos
        self.color = color
        self.piece_type = piece_type
        self.cs = chess_scene
        self.possible_moves = []
        self.move_rects = []
        self.first_move = True
        self.setPixmap(QPixmap(f':/Pieces{self.cs.number}/{self.color}_{self.piece_type}.png').scaled(100, 100))
        self.setFlags(QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemIsMovable)
        self.setPos(self.x_pos, self.y_pos)
        self.setZValue(1)

    def move_from_chat(self, index, x, y):
        to_remove = None
        getattr(self, f"{self.piece_type}_movement")(self.x_pos, self.y_pos)
        if (x, y) in self.possible_moves and not self.uncheck(x, y):
            # Check for capturing, it was not working so created to_remove and its somehow working
            for i, piece in enumerate(self.cs.all_pieces):
                if (piece[2], piece[3]) == (x, y):
                    self.cs.pieces_id[i].setPos(1500, self.cs.capture_row * 25)
                    self.cs.pieces_id[i].setFlags(QGraphicsItem.ItemIgnoresTransformations)
                    self.cs.capture_row += 1
                    self.cs.pieces_id[i].setZValue(self.cs.capture_row)
                    # del self.cs.pieces_id[i]
                    # del self.cs.all_pieces[i]
                    to_remove = i
                    break
            self.cs.pieces_id[index].setPos(x, y)
            self.cs.pieces_id[index].x_pos = x
            self.cs.pieces_id[index].y_pos = y
            self.cs.all_pieces[index] = (self.color, self.piece_type, x, y)
            setattr(self.cs, self.cs.current_turn + "_moved", True)

            del self.cs.pieces_id[to_remove]
            del self.cs.all_pieces[to_remove]
        else:
            raise ValueError

    # Check and highlight possible moves
    def mousePressEvent(self, event):
        if self.color == self.cs.current_turn and not self.cs.w_moved and not self.cs.b_moved:
            self.x_pos = self.pos().x()
            self.y_pos = self.pos().y()
            self.move_rects.clear()
            self.setZValue(2)
            getattr(self, f"{self.piece_type}_movement")(self.x_pos, self.y_pos)

            # Color possible moves
            for possible_move in self.possible_moves:
                if 0 <= possible_move[0] <= 700 and 0 <= possible_move[1] <= 700:
                    self.move_rects.append(QGraphicsRectItem(possible_move[0], possible_move[1], 100, 100))
                    self.move_rects[-1].setBrush(QColor(255, 255, 0))
                    self.scene().addItem(self.move_rects[-1])

        super().mousePressEvent(event)

    # Move the figure
    def mouseReleaseEvent(self, event):
        if self.color == self.cs.current_turn and not self.cs.w_moved and not self.cs.b_moved:
            self.setZValue(1)
            x = round(self.pos().x() / 100) * 100
            y = round(self.pos().y() / 100) * 100
            if 0 <= x <= 700 and 0 <= y <= 700 and (x, y) in self.possible_moves and not self.uncheck(x, y):
                # Castling
                if self.piece_type == "king" and (self.color, "rook", x, y) in self.cs.all_pieces:
                    index = self.cs.all_pieces.index((self.color, "rook", x, y))
                    self.cs.all_pieces[index] = (self.color, "rook", self.x_pos, self.y_pos)
                    self.cs.pieces_id[index].setPos(self.x_pos, self.y_pos)

                # Check for capturing
                for i, piece in enumerate(self.cs.all_pieces):
                    if (piece[2], piece[3]) == (x, y):
                        self.cs.pieces_id[i].setPos(1500, self.cs.capture_row * 25)
                        self.cs.pieces_id[i].setFlags(QGraphicsItem.ItemIgnoresTransformations)
                        self.cs.capture_row += 1
                        self.cs.pieces_id[i].setZValue(self.cs.capture_row)
                        del self.cs.pieces_id[i]
                        del self.cs.all_pieces[i]
                        break

                self.setPos(x, y)
                piece_index = self.cs.all_pieces.index((self.color, self.piece_type, self.x_pos, self.y_pos))
                self.cs.all_pieces[piece_index] = (self.color, self.piece_type, x, y)
                self.x_pos = x
                self.y_pos = y
                # Check for promotion
                if self.piece_type == "pawn" and (y == 0 or y == 700):
                    self.setPos(-1000, -1000)
                    self.cs.open_new_window(self.color, self.x_pos, self.y_pos)
                setattr(self.cs, self.cs.current_turn + "_moved", True)
            else:
                self.setPos(self.x_pos, self.y_pos)

            for move_rect in self.move_rects:
                self.scene().removeItem(move_rect)

        else:
            self.setPos(self.x_pos, self.y_pos)
        super().mouseReleaseEvent(event)

    def del_impossible_moves(self, directions):
        for piece in self.cs.all_pieces:
            if (piece[2], piece[3]) in self.possible_moves and piece[0] == self.color:
                start_index = self.possible_moves.index((piece[2], piece[3]))
                for index in range(start_index, len(self.possible_moves), directions):
                    self.possible_moves[index] = (-1, -1)
            elif (piece[2], piece[3]) in self.possible_moves and piece[0] != self.color:
                start_index = self.possible_moves.index((piece[2], piece[3])) + directions
                for index in range(start_index, len(self.possible_moves), directions):
                    self.possible_moves[index] = (-1, -1)

    def pawn_movement(self, x, y):
        direction = 1 if self.color == "b" else -1
        self.possible_moves = [(x, y + direction * 100)]
        if (y == 100 and self.color == "b") or (y == 600 and self.color == "w"):
            self.possible_moves.append((x, y + direction * 200))
        for piece in self.cs.all_pieces:
            if (piece[2], piece[3]) in self.possible_moves:
                index = self.possible_moves.index((piece[2], piece[3]))
                self.possible_moves[index] = (-1, -1)
                if (piece[2], piece[3]) == (x, y + direction * 100) and (x, y + direction * 200) in self.possible_moves:
                    index = self.possible_moves.index((x, y + direction * 200))
                    self.possible_moves[index] = (-1, -1)
            if (piece[2], piece[3]) == (x + direction * 100, y + direction * 100) and piece[0] != self.color:
                self.possible_moves.append((self.x_pos + direction * 100, self.y_pos + direction * 100))
            if (piece[2], piece[3]) == (x - direction * 100, y + direction * 100) and piece[0] != self.color:
                self.possible_moves.append((x - direction * 100, y + direction * 100))

    def rook_movement(self, x, y):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.extend([(x + 100 * i, y), (x + 100 * -i, y), (x, y + 100 * i), (x, y + 100 * -i)])

        self.del_impossible_moves(4)

    def bishop_movement(self, x, y):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.extend([(x + 100 * i, y + 100 * i), (x - 100 * i, y + 100 * i),
                                        (x + 100 * i, y - 100 * i), (x - 100 * i, y - 100 * i)])

        self.del_impossible_moves(4)

    def knight_movement(self, x, y):
        self.possible_moves = [(x + 200, y + 100), (x + 200, y - 100),
                               (x - 200, y + 100), (x - 200, y - 100),
                               (x + 100, y + 200), (x + 100, y - 200),
                               (x - 100, y + 200), (x - 100, y - 200)]

        self.del_impossible_moves(10)

    def queen_movement(self, x, y):
        self.possible_moves.clear()
        for i in range(1, 8):
            self.possible_moves.extend([(x + 100 * i, y), (x + 100 * -i, y),
                                        (x, y + 100 * i), (x, y + 100 * -i),
                                        (x + 100 * i, y + 100 * i), (x - 100 * i, y + 100 * i),
                                        (x + 100 * i, y - 100 * i), (x - 100 * i, y - 100 * i)])

        self.del_impossible_moves(8)

    def king_movement(self, x, y):
        self.possible_moves = [(x + 100, y + 100), (x - 100, y - 100),
                               (x + 100, y - 100), (x - 100, y + 100),
                               (x + 100, y), (x - 100, y),
                               (x, y + 100), (x, y - 100)]

        self.del_impossible_moves(10)

        dx, dy = 400, 700 if self.color == "w" else 100
        if (self.color, self.piece_type, dx, dy) in self.cs.all_pieces and (self.color, "rook", dx + 300, dy) in self.cs.all_pieces:
            if not any(piece[2:4] in ((500, 700), (600, 700)) for piece in self.cs.all_pieces):
                self.possible_moves.append((700, 700))

    def uncheck(self, x, y):
        index = self.cs.all_pieces.index((self.color, self.piece_type, self.x_pos, self.y_pos))
        self.cs.all_pieces[index] = (self.color, self.piece_type, x, y)
        king_pos = [pos for pos in self.cs.all_pieces if pos[1] == 'king' and pos[0] == self.cs.current_turn]
        self.color = "w" if self.cs.current_turn == "b" else "b"
        self.cs.current_turn = "w" if self.cs.current_turn == "b" else "b"
        for piece in self.cs.all_pieces:
            if piece[0] == self.cs.current_turn and (piece[2], piece[3]) != (x, y):
                getattr(self, f"{piece[1]}_movement")(piece[2], piece[3])
                if (king_pos[0][2], king_pos[0][3]) in self.possible_moves:
                    self.color = "w" if self.cs.current_turn == "b" else "b"
                    self.cs.current_turn = "w" if self.cs.current_turn == "b" else "b"
                    self.cs.all_pieces[index] = (self.color, self.piece_type, self.x_pos, self.y_pos)
                    return True

        self.color = "w" if self.cs.current_turn == "b" else "b"
        self.cs.current_turn = "w" if self.cs.current_turn == "b" else "b"
        self.cs.all_pieces[index] = (self.color, self.piece_type, self.x_pos, self.y_pos)
        return False


class ChessView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setScene(ChessScene(self))
        self.setRenderHint(QPainter.Antialiasing)
        self.setFixedSize(1920, 1080)


if __name__ == '__main__':
    QResource.registerResource('pieces.qrc')
    app = QApplication(sys.argv)
    view = ChessView()
    view.show()
    sys.exit(app.exec())
