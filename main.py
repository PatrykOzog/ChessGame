from PyQt5.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsRectItem, QApplication, QVBoxLayout, QWidget, \
    QGraphicsItem, QGraphicsTextItem, QGraphicsPixmapItem, QTextEdit, QDialog, QPushButton, QGraphicsProxyWidget, \
    QMessageBox, QRadioButton, QLineEdit, QLabel, QButtonGroup
from PyQt5.QtGui import QBrush, QColor, QPainter, QPixmap, QPolygon
from PyQt5.QtCore import Qt, QEvent, QTimer, QResource, QPoint, QEventLoop
import sys
import numpy as np
import socket
import threading
import sqlite3
import xml.etree.ElementTree as ET
import xml.dom.minidom
from datetime import datetime
import json
from pieces import *


class ServerConnect:
    def __init__(self, chess_scene, ip_address, port):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((ip_address, port))
        self.receive_thread = threading.Thread(target=self.receive)
        self.receive_thread.start()
        self.send_thread = None
        self.cs = chess_scene

    def send(self):
        msg = self.cs.all_pieces
        json_str = json.dumps(msg)
        self.client_socket.send(json_str.encode())

    def receive(self):
        while True:
            received_msg = self.client_socket.recv(1024).decode()
            received_msg = json.loads(received_msg)
            print(received_msg)

    def handle_msg(self):
        if not self.send_thread or not self.send_thread.is_alive():
            self.send_thread = threading.Thread(target=self.send)
            self.send_thread.start()


class AnalogClock(QWidget):
    millisecHand = QPolygon([
        QPoint(7, 8),
        QPoint(-7, 8),
        QPoint(0, -95)
    ])
    minuteHand = QPolygon([
        QPoint(7, 8),
        QPoint(-7, 8),
        QPoint(0, -50)
    ])
    secondHand = QPolygon([
        QPoint(7, 8),
        QPoint(-7, 8),
        QPoint(0, -70)
    ])
    millisecColor = QColor(195, 0, 0, 150)
    secondColor = QColor(0, 100, 250, 200)
    minuteColor = QColor(127, 0, 127)

    def __init__(self, color, parent=None):
        super(AnalogClock, self).__init__(parent)
        self.color = color
        self.timer = QTimer(self)
        self.msgBox = QMessageBox()
        self.timer.setInterval(1)
        self.timer.timeout.connect(self.update)
        self.time_left = 300 * 1000

    def paintEvent(self, event):
        side = min(self.width(), self.height())
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(side / 200, side / 200)
        for i in range(60):
            if (i % 5) == 0:
                painter.drawLine(88, 0, 96, 0)
            else:
                painter.drawLine(92, 0, 96, 0)
            painter.rotate(6.0)

        if self.time_left <= 0:
            self.timer.stop()
            text = "Black won!" if self.color == "w" else "White won!"
            self.msgBox.setText(text)
            self.msgBox.setWindowTitle("Time's up!")
            self.msgBox.exec()
            sys.exit()
        else:
            self.time_left -= 1

        minutes = self.time_left / 60000
        seconds = self.time_left / 1000 % 60
        milliseconds = self.time_left % 1000

        # Milliseconds
        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.millisecColor)
        painter.save()
        painter.rotate(360 / 1000 * (1000 - milliseconds))
        painter.drawConvexPolygon(AnalogClock.millisecHand)
        painter.restore()

        # Seconds
        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.secondColor)
        painter.save()
        painter.rotate(6 * (60 - seconds))
        painter.drawConvexPolygon(AnalogClock.secondHand)
        painter.restore()

        # Minutes
        painter.setPen(Qt.NoPen)
        painter.setBrush(AnalogClock.minuteColor)
        painter.save()
        painter.rotate(6 * (60 - minutes))
        painter.drawConvexPolygon(AnalogClock.minuteHand)
        painter.restore()


class ChessScene(QGraphicsScene):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.server_connection = None
        self.game_mode = None
        self.ip_address = None
        self.port = None
        self.w_moved = False
        self.b_moved = False
        self.number = None
        self.capture_row = 0
        self.setSceneRect(0, 0, 1600, 900)
        self.current_turn = "w"
        self.all_pieces = []
        self.pieces_id = []
        self.game_history = []
        self.conn = sqlite3.connect('chess.db')
        self.cursor = self.conn.cursor()
        # self.cursor.execute("DROP TABLE moves")
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS moves
                            (id INTEGER PRIMARY KEY, player TEXT, figure TEXT, from_square TEXT, to_square TEXT, timestamp TEXT)''')
        self.figures_values = {'K': 'king', 'Q': 'queen', 'R': 'rook', 'B': 'bishop', 'N': 'knight', '': 'pawn'}
        self.row_values = {'a': 0, 'b': 100, 'c': 200, 'd': 300, 'e': 400, 'f': 500, 'g': 600, 'h': 700,
                           0: 'a', 100: 'b', 200: 'c', 300: 'd', 400: 'e', 500: 'f', 600: 'g', 700: 'h'}
        self.col_values = {'1': 0, '2': 100, '3': 200, '4': 300, '5': 400, '6': 500, '7': 600, '8': 700,
                           0: '1', 100: '2', 200: '3', 300: '4', 400: '5', 500: '6', 600: '7', 700: '8'}
        self.start_pos = [('b_rook', (0, 0)), ('b_knight', (100, 0)), ('b_bishop', (200, 0)), ('b_queen', (300, 0)),
                          ('b_king', (400, 0)), ('b_bishop', (500, 0)), ('b_knight', (600, 0)), ('b_rook', (700, 0)),
                          ('w_rook', (0, 700)), ('w_knight', (100, 700)), ('w_bishop', (200, 700)),
                          ('w_queen', (300, 700)), ('w_king', (400, 700)), ('w_bishop', (500, 700)),
                          ('w_knight', (600, 700)), ('w_rook', (700, 700))]

        self.open_starting_window()

        self.create_starting_board()

        # Playback
        self.playback_button = QPushButton("Playback")
        self.playback_button.setGeometry(1000, 750, 350, 50)
        self.playback_button.setStyleSheet("font-size: 16px;")
        self.playback_button_proxy = QGraphicsProxyWidget()
        self.playback_button_proxy.setWidget(self.playback_button)
        self.addItem(self.playback_button_proxy)
        self.playback_button.clicked.connect(self.playback)

        # Save to xml
        self.xml_button = QPushButton("Save history to xml")
        self.xml_button.setGeometry(1000, 800, 350, 50)
        self.xml_button.setStyleSheet("font-size: 16px;")
        self.xml_button_proxy = QGraphicsProxyWidget()
        self.xml_button_proxy.setWidget(self.xml_button)
        self.addItem(self.xml_button_proxy)
        self.xml_button.clicked.connect(self.save_to_xml)

        # Save to json
        self.json_button = QPushButton("Save settings to json")
        self.json_button.setGeometry(1000, 850, 350, 50)
        self.json_button.setStyleSheet("font-size: 16px;")
        self.json_button_proxy = QGraphicsProxyWidget()
        self.json_button_proxy.setWidget(self.json_button)
        self.addItem(self.json_button_proxy)
        self.json_button.clicked.connect(self.save_to_json)

        # Text box
        self.textedit = QTextEdit()
        self.textedit.setGeometry(1000, 600, 350, 50)
        self.textedit.setFontPointSize(16)
        self.textedit.installEventFilter(self)
        self.addWidget(self.textedit)

        # White clock
        self.w_clock = AnalogClock("w")
        self.w_clock.setGeometry(850, 100, 300, 300)
        self.addWidget(self.w_clock)

        # Black clock
        self.b_clock = AnalogClock("b")
        self.b_clock.setGeometry(1200, 100, 300, 300)
        self.addWidget(self.b_clock)

        # White button
        self.w_button = QPushButton("White button")
        self.w_button.setGeometry(850, 50, 300, 50)
        self.w_button.setStyleSheet("font-size: 16px;")
        self.w_button_proxy = QGraphicsProxyWidget()
        self.w_button_proxy.setWidget(self.w_button)
        self.addItem(self.w_button_proxy)
        self.w_button.clicked.connect(self.w_button_clicked)

        # Black button
        self.b_button = QPushButton("Black button")
        self.b_button.setGeometry(1200, 50, 300, 50)
        self.b_button.setStyleSheet("font-size: 16px;")
        self.b_button_proxy = QGraphicsProxyWidget()
        self.b_button_proxy.setWidget(self.b_button)
        self.addItem(self.b_button_proxy)
        self.b_button.clicked.connect(self.b_button_clicked)

        self.w_clock.timer.start()

    def open_starting_window(self):
        self.dialog = QDialog()
        self.dialog.setModal(False)
        self.dialog.setGeometry(500, 500, 500, 300)
        layout = QVBoxLayout()

        group1 = QButtonGroup()
        group2 = QButtonGroup()

        # Radio buttons
        radio_button1 = QRadioButton("1 gracz")
        radio_button2 = QRadioButton("2 graczy")
        radio_button3 = QRadioButton("AI")
        radio_button1.clicked.connect(lambda: self.radio_button_clicked("1_player"))
        radio_button2.clicked.connect(lambda: self.radio_button_clicked("2_players"))
        radio_button3.clicked.connect(lambda: self.radio_button_clicked("AI"))
        group1.addButton(radio_button1)
        group1.addButton(radio_button2)
        group1.addButton(radio_button3)
        layout.addWidget(radio_button1)
        layout.addWidget(radio_button2)
        layout.addWidget(radio_button3)

        # Add image
        pixmap = QPixmap('Choice.png')
        label = QLabel()
        label.setPixmap(pixmap)
        layout.addWidget(label)

        radio_button4 = QRadioButton("Number 1")
        radio_button5 = QRadioButton("Number 2")
        radio_button4.clicked.connect(lambda: self.radio_button_clicked(1))
        radio_button5.clicked.connect(lambda: self.radio_button_clicked(2))
        group2.addButton(radio_button4)
        group2.addButton(radio_button5)
        layout.addWidget(radio_button4)
        layout.addWidget(radio_button5)

        # Create the line edit
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("Adres IP:Port")
        layout.addWidget(self.line_edit)

        connect_button = QPushButton("Connect")
        connect_button.clicked.connect(self.connect_button_clicked)
        layout.addWidget(connect_button)

        load_button = QPushButton("Load from Json")
        load_button.clicked.connect(self.load_from_json)
        layout.addWidget(load_button)

        accept_button = QPushButton("Accept")
        accept_button.clicked.connect(self.accept_button_clicked)
        layout.addWidget(accept_button)

        def closeEvent(event):
            event.ignore()

        self.dialog.closeEvent = closeEvent
        self.dialog.setLayout(layout)
        self.dialog.exec()

    def connect_button_clicked(self):
        if self.server_connection is not None:
            self.server_connection.client_socket.close()
        try:
            self.ip_address, self.port = self.line_edit.text().split(':')
            self.server_connection = ServerConnect(self, self.ip_address, int(self.port))
        except Exception as e:
            print(e)

    def accept_button_clicked(self):
        if self.game_mode is not None and self.number is not None:
            print(self.game_mode)
            self.dialog.accept()

    def radio_button_clicked(self, choice):
        if choice == "1_player" or choice == "AI" or (choice == "2_players" and self.server_connection is not None):
            self.game_mode = choice
        if choice == 1 or choice == 2:
            self.number = choice

    def save_to_json(self):
        options = {
            "Game mode": self.game_mode,
            "Skin number": self.number,
            "IP": self.ip_address,
            "Port": self.port
        }

        with open("options.json", "w") as f:
            json.dump(options, f, indent=4)

    def load_from_json(self):
        with open('options.json') as f:
            data = json.load(f)

        self.game_mode = data['Game mode']
        self.number = data['Skin number']
        self.line_edit.setText(f"{data['IP']}:{data['Port']}")

    def save_to_xml(self):
        root = ET.Element("game")
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        for all_pieces in self.game_history:
            move_section = ET.SubElement(root, "move_section")
            for piece in all_pieces:
                square = ''.join([self.row_values[piece[2]], self.col_values[piece[3]]])
                move_elem = ET.SubElement(move_section, "move")
                move_elem.set("player", piece[0])
                move_elem.set("square", square)
                move_elem.set("type", piece[1])
                move_elem.set("timestamp", timestamp)

        xml_str = ET.tostring(root, encoding="utf-8")
        xml_dom = xml.dom.minidom.parseString(xml_str)
        pretty_xml_str = xml_dom.toprettyxml()

        with open("game_history.xml", "w") as f:
            f.write(pretty_xml_str)

    def playback(self):
        self.w_clock.timer.stop() if self.current_turn == "w" else self.b_clock.timer.stop()
        for piece in self.pieces_id:
            self.removeItem(piece)

        temp_all_pieces = self.all_pieces
        self.pieces_id = []
        self.all_pieces = []

        for i in range(8):
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

        self.cursor.execute("SELECT * FROM moves")
        result = self.cursor.fetchall()
        for row in result:
            x_pos = self.row_values[row[3][-2:-1]]
            y_pos = self.col_values[row[3][-1]]
            stop_x = self.row_values[row[4][0]]
            stop_y = self.col_values[row[4][1]]
            index = self.all_pieces.index((row[1], row[2], x_pos, y_pos))

            timer = QTimer(self)
            event_loop = QEventLoop()
            timer.timeout.connect(lambda: event_loop.exit())
            timer.setSingleShot(True)
            timer.start(1000)
            event_loop.exec()

            self.pieces_id[index].x_pos = stop_x
            self.pieces_id[index].y_pos = stop_y
            self.pieces_id[index].setPos(stop_x, stop_y)
            self.all_pieces[index] = (row[1], row[2], stop_x, stop_y)

            for i, piece in enumerate(self.all_pieces):
                if (piece[2], piece[3]) == (stop_x, stop_y) and i != index:
                    self.pieces_id[i].setPos(-1000, -1000)
                    del self.pieces_id[i]
                    del self.all_pieces[i]
                    break

        self.w_clock.timer.start() if self.current_turn == "w" else self.b_clock.timer.start()

    # Promotion choice
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

    # Turn changing buttons
    def w_button_clicked(self):
        if (self.w_moved or self.b_moved) and self.current_turn == "w":
            self.w_clock.timer.stop()
            self.b_clock.timer.start()
            self.current_turn = "b"
            self.w_moved = False

    def b_button_clicked(self):
        if (self.w_moved or self.b_moved) and self.current_turn == "b":
            self.b_clock.timer.stop()
            self.w_clock.timer.start()
            self.current_turn = "w"
            self.b_moved = False

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
                        piece.move_from_chat(index, stop_x, stop_y, part_one, part_two)
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

        self.game_history.append(self.all_pieces)

    # # Change skin by double clicking
    # def mouseDoubleClickEvent(self, event):
    #     self.number = 2 if self.number == 1 else 1
    #     for i, piece in enumerate(self.all_pieces):
    #         self.removeItem(self.pieces_id[i])
    #         new_piece = ChessPiece(piece[0], piece[1], piece[2], piece[3], self)
    #         self.pieces_id[i] = new_piece
    #         self.addItem(new_piece)


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

    def move_from_chat(self, index, x, y, part_one, part_two):
        to_remove = None
        getattr(self, f"{self.piece_type}_movement")(self.x_pos, self.y_pos)
        if (x, y) in self.possible_moves and not self.uncheck(x, y):
            self.save_to_sql(part_one[-2:], part_two[-2:])
            self.cs.pieces_id[index].setPos(x, y)
            self.cs.pieces_id[index].x_pos = x
            self.cs.pieces_id[index].y_pos = y
            self.cs.all_pieces[index] = (self.color, self.piece_type, x, y)
            # Check for capturing
            for i, piece in enumerate(self.cs.all_pieces):
                if (piece[2], piece[3]) == (x, y) and i != index:
                    self.cs.pieces_id[i].setPos(1600, self.cs.capture_row * 25)
                    self.cs.pieces_id[i].setFlags(QGraphicsItem.ItemIgnoresTransformations)
                    self.cs.capture_row += 1
                    self.cs.pieces_id[i].setZValue(self.cs.capture_row)
                    del self.cs.pieces_id[i]
                    del self.cs.all_pieces[i]
                    break

            setattr(self.cs, self.cs.current_turn + "_moved", True)
            self.cs.game_history.append(self.cs.all_pieces)
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
                dx = 100 if x - self.x_pos > 0 else -100
                castling_moves = [(self.color, "rook", x + 100, y), (self.color, "rook", x - 200, y)]
                for move in castling_moves:
                    if self.piece_type == "king" and move in self.cs.all_pieces:
                        index = self.cs.all_pieces.index(move)
                        rook = self.cs.pieces_id[index]
                        if self.first_move and rook.first_move:
                            rook.setPos(self.x_pos + dx, self.y_pos)
                            rook.x_pos = self.x_pos + dx
                            rook.y_pos = self.y_pos
                            self.cs.all_pieces[index] = (self.color, "rook", self.x_pos + dx, self.y_pos)

                # Check for capturing
                for i, piece in enumerate(self.cs.all_pieces):
                    if (piece[2], piece[3]) == (x, y) and piece[0] != self.color:
                        self.cs.pieces_id[i].setPos(1600, self.cs.capture_row * 25)
                        self.cs.pieces_id[i].setFlags(QGraphicsItem.ItemIgnoresTransformations)
                        self.cs.capture_row += 1
                        self.cs.pieces_id[i].setZValue(self.cs.capture_row)
                        del self.cs.pieces_id[i]
                        del self.cs.all_pieces[i]
                        break

                self.setPos(x, y)
                self.first_move = False
                piece_index = self.cs.all_pieces.index((self.color, self.piece_type, self.x_pos, self.y_pos))
                self.cs.all_pieces[piece_index] = (self.color, self.piece_type, x, y)
                from_square = ''.join([self.cs.row_values[self.x_pos], self.cs.col_values[self.y_pos]])
                to_square = ''.join([self.cs.row_values[x], self.cs.col_values[y]])
                self.save_to_sql(from_square, to_square)
                self.x_pos = x
                self.y_pos = y
                # Check for promotion
                if self.piece_type == "pawn" and (y == 0 or y == 700):
                    self.setPos(-1000, -1000)
                    self.cs.open_new_window(self.color, self.x_pos, self.y_pos)
                setattr(self.cs, self.cs.current_turn + "_moved", True)
                self.cs.game_history.append(self.cs.all_pieces)
            else:
                self.setPos(self.x_pos, self.y_pos)

            for move_rect in self.move_rects:
                self.scene().removeItem(move_rect)

        else:
            self.setPos(self.x_pos, self.y_pos)
        super().mouseReleaseEvent(event)

    def save_to_sql(self, from_square, to_square):
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.cs.cursor.execute(
            "INSERT INTO moves (player, figure, from_square, to_square, timestamp) VALUES (?, ?, ?, ?, ?)",
            (self.color, self.piece_type, from_square, to_square, timestamp))
        self.cs.cursor.execute("SELECT * FROM moves")
        result = self.cs.cursor.fetchall()
        print(result[-1])

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

        dx, dy = 400, 700 if self.color == "w" else 0
        if (self.color, self.piece_type, dx, dy) in self.cs.all_pieces and (
        self.color, "rook", dx + 300, dy) in self.cs.all_pieces and self.first_move:
            if not any(piece[2:4] in ((500, dy), (600, dy)) for piece in self.cs.all_pieces):
                self.possible_moves.append((dx + 200, dy))
        if (self.color, self.piece_type, dx, dy) in self.cs.all_pieces and (
        self.color, "rook", dx - 400, dy) in self.cs.all_pieces and self.first_move:
            if not any(piece[2:4] in ((300, dy), (200, dy), (100, dy)) for piece in self.cs.all_pieces):
                self.possible_moves.append((dx - 200, dy))

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
