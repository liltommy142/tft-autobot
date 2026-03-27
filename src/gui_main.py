#!/usr/bin/env python
"""
gui_main.py - GUI interface for TFT assistant using PyQt5
"""
import sys
from pathlib import Path

# Add src to Python path if run from root
if str(Path(__file__).parent) != Path.cwd():
    sys.path.insert(0, str(Path(__file__).parent))

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QGroupBox, QStatusBar, QMessageBox,
    QMenuBar, QMenu, QAction
)
from PyQt5.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
# try:
#     import easyocr
#     EASYOCR_AVAILABLE = True
# except ImportError:
#     EASYOCR_AVAILABLE = False
# import pyautogui
try:
    from pynput import mouse
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False
from PyQt5.QtGui import QFont, QColor, QPainter, QPen

from core_models import GameState, UnitInstance
from core_engine import recommend_comps, econ_advice, recommend_items
from logger import read_logs
from config import TOP_N_LOGS_TO_SHOW


class OCRThread(QThread):
    result_signal = pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        # if EASYOCR_AVAILABLE:
        #     self.reader = easyocr.Reader(['en'])
        # else:
        self.reader = None
        self.running = False

    def run(self):
        self.running = True
        while self.running:
            try:
                # Capture screen
                # screenshot = pyautogui.screenshot()
                # img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
                img = None  # Placeholder

                # Define TFT UI regions (these are example coordinates, need to be calibrated)
                level_bbox = self.level_bbox
                gold_bbox = self.gold_bbox
                hp_bbox = self.hp_bbox
                round_bbox = self.round_bbox
                units_bbox = self.units_bbox

                level_text = self.ocr_region(img, level_bbox)
                gold_text = self.ocr_region(img, gold_bbox)
                hp_text = self.ocr_region(img, hp_bbox)
                round_text = self.ocr_region(img, round_bbox)
                units_text = self.ocr_region(img, units_bbox)

                # Parse
                level = self.parse_int(level_text) or 6
                gold = self.parse_int(gold_text) or 30
                hp = self.parse_int(hp_text) or 70
                round_str = round_text.strip() or "3-2"
                units = self.parse_units(units_text)

                # Create game state
                game_state = GameState(level=level, gold=gold, hp=hp, round=round_str, units=units)

                # Predict
                comps = recommend_comps(game_state)
                econ = econ_advice(game_state)
                items = recommend_items(game_state)

                result = {
                    'level': level,
                    'gold': gold,
                    'hp': hp,
                    'round': round_str,
                    'units': units,
                    'comps': comps,
                    'econ': econ,
                    'items': items
                }

                self.result_signal.emit(result)

            except Exception as e:
                print(f"OCR Error: {e}")

            self.msleep(2000)  # 2 second delay

    def ocr_region(self, img, bbox):
        if not self.reader:
            return "OCR not available"
        x1, y1, x2, y2 = bbox
        roi = img[y1:y2, x1:x2]
        results = self.reader.readtext(roi)
        text = ' '.join([res[1] for res in results])
        return text

    def parse_int(self, text):
        try:
            return int(''.join(filter(str.isdigit, text)))
        except:
            return None

    def parse_units(self, raw):
        # Simple parsing, can be improved
        if not raw.strip():
            return []
        parts = [p.strip() for p in raw.split() if p.strip()]
        units = []
        for p in parts:
            name = ''.join([c for c in p if not c.isdigit()])
            star = 1
            digits = ''.join([c for c in p if c.isdigit()])
            if digits:
                star = int(digits)
            try:
                units.append(UnitInstance(name=name, star=star))
            except ValueError:
                pass
        return units

    def stop(self):
        self.running = False

    def update_bboxes(self, bboxes):
        self.level_bbox, self.gold_bbox, self.hp_bbox, self.round_bbox, self.units_bbox = bboxes


class OverlayWindow(QWidget):
    def __init__(self, bboxes):
        super().__init__()
        self.bboxes = bboxes
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.setWindowOpacity(0.7)  # semi-transparent

        # Set size to screen size
        screen = QApplication.primaryScreen().geometry()
        self.setGeometry(screen)
        self.show()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(QPen(Qt.red, 3))
        painter.setBrush(Qt.NoBrush)
        for bbox in self.bboxes:
            x1, y1, x2, y2 = bbox
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.hide()


class TFTAssistantGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TFT AutoBot - Rank Assistant")
        self.setGeometry(100, 100, 900, 700)

        # TFT Colors
        self.primary_color = QColor(30, 144, 255)  # Blue
        self.secondary_color = QColor(255, 215, 0)  # Gold

        # OCR Bboxes
        self.level_bbox = (100, 100, 150, 120)
        self.gold_bbox = (200, 100, 250, 120)
        self.hp_bbox = (300, 100, 350, 120)
        self.round_bbox = (400, 100, 450, 120)
        self.units_bbox = (100, 200, 500, 250)

        # OCR Thread
        self.ocr_thread = OCRThread()
        self.ocr_thread.result_signal.connect(self.update_from_ocr)

        self.init_ui()

    def init_ui(self):
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # Title
        title_label = QLabel("TFT AutoBot - Rank Assistant")
        title_font = QFont("Arial", 16, QFont.Bold)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet(f"color: {self.primary_color.name()}; margin: 10px;")
        main_layout.addWidget(title_label)

        # Input section
        input_group = QGroupBox("Game State Input")
        input_layout = QGridLayout()

        # Level, Gold
        input_layout.addWidget(QLabel("Level:"), 0, 0)
        self.level_edit = QLineEdit("6")
        input_layout.addWidget(self.level_edit, 0, 1)

        input_layout.addWidget(QLabel("Gold:"), 0, 2)
        self.gold_edit = QLineEdit("30")
        input_layout.addWidget(self.gold_edit, 0, 3)

        # HP, Round
        input_layout.addWidget(QLabel("HP:"), 1, 0)
        self.hp_edit = QLineEdit("70")
        input_layout.addWidget(self.hp_edit, 1, 1)

        input_layout.addWidget(QLabel("Round:"), 1, 2)
        self.round_edit = QLineEdit("3-2")
        input_layout.addWidget(self.round_edit, 1, 3)

        # Units
        input_layout.addWidget(QLabel("Units (comma separated):"), 2, 0, 1, 1)
        self.units_edit = QTextEdit()
        self.units_edit.setMaximumHeight(60)
        input_layout.addWidget(self.units_edit, 2, 1, 1, 3)

        # Target Comp
        input_layout.addWidget(QLabel("Target Comp (optional):"), 3, 0, 1, 1)
        self.target_comp_edit = QLineEdit()
        input_layout.addWidget(self.target_comp_edit, 3, 1, 1, 3)

        input_group.setLayout(input_layout)
        main_layout.addWidget(input_group)

        # Buttons
        button_layout = QHBoxLayout()
        button_font = QFont("Arial", 10, QFont.Bold)

        self.comp_btn = QPushButton("🎯 Get Comp Suggestions")
        self.comp_btn.setFont(button_font)
        self.comp_btn.setStyleSheet(f"background-color: {self.primary_color.name()}; color: white; padding: 8px; border-radius: 4px;")
        self.comp_btn.clicked.connect(self.get_comps)
        button_layout.addWidget(self.comp_btn)

        self.econ_btn = QPushButton("💰 Get Econ Advice")
        self.econ_btn.setFont(button_font)
        self.econ_btn.setStyleSheet(f"background-color: {self.primary_color.name()}; color: white; padding: 8px; border-radius: 4px;")
        self.econ_btn.clicked.connect(self.get_econ)
        button_layout.addWidget(self.econ_btn)

        self.items_btn = QPushButton("⚔️ Get Item Suggestions")
        self.items_btn.setFont(button_font)
        self.items_btn.setStyleSheet(f"background-color: {self.primary_color.name()}; color: white; padding: 8px; border-radius: 4px;")
        self.items_btn.clicked.connect(self.get_items)
        button_layout.addWidget(self.items_btn)

        self.logs_btn = QPushButton("📊 View Recent Logs")
        self.logs_btn.setFont(button_font)
        self.logs_btn.setStyleSheet(f"background-color: {self.primary_color.name()}; color: white; padding: 8px; border-radius: 4px;")
        self.logs_btn.clicked.connect(self.view_logs)
        button_layout.addWidget(self.logs_btn)

        self.ocr_btn = QPushButton("🤖 Start Auto OCR")
        self.ocr_btn.setFont(button_font)
        self.ocr_btn.setStyleSheet(f"background-color: {self.secondary_color.name()}; color: black; padding: 8px; border-radius: 4px;")
        self.ocr_btn.clicked.connect(self.start_ocr)
        button_layout.addWidget(self.ocr_btn)

        self.debug_btn = QPushButton("🔍 Debug Overlay")
        self.debug_btn.setFont(button_font)
        self.debug_btn.setStyleSheet(f"background-color: {self.secondary_color.name()}; color: black; padding: 8px; border-radius: 4px;")
        self.debug_btn.clicked.connect(self.show_debug_overlay)
        button_layout.addWidget(self.debug_btn)

        self.calibrate_btn = QPushButton("🎯 Calibrate Regions")
        self.calibrate_btn.setFont(button_font)
        self.calibrate_btn.setStyleSheet(f"background-color: {self.secondary_color.name()}; color: black; padding: 8px; border-radius: 4px;")
        self.calibrate_btn.clicked.connect(self.calibrate_regions)
        button_layout.addWidget(self.calibrate_btn)

        main_layout.addLayout(button_layout)

        # Output section
        output_group = QGroupBox("Recommendations & Logs")
        output_layout = QVBoxLayout()

        self.output_edit = QTextEdit()
        self.output_edit.setFont(QFont("Consolas", 10))
        output_layout.addWidget(self.output_edit)

        output_group.setLayout(output_layout)
        main_layout.addWidget(output_group)

        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        # Menu bar
        self.create_menu()

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu('File')
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def start_ocr(self):
        if not self.ocr_thread.isRunning():
            self.ocr_thread.start()
            self.ocr_btn.setText("⏹️ Stop Auto OCR")
            self.status_bar.showMessage("OCR running...")
        else:
            self.ocr_thread.stop()
            self.ocr_btn.setText("🤖 Start Auto OCR")
            self.status_bar.showMessage("OCR stopped")

    def show_debug_overlay(self):
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.hide()
            self.debug_btn.setText("🔍 Debug Overlay")
        else:
            bboxes = [
                self.level_bbox,
                self.gold_bbox,
                self.hp_bbox,
                self.round_bbox,
                self.units_bbox,
            ]
            self.overlay = OverlayWindow(bboxes)
            self.debug_btn.setText("❌ Hide Overlay")

    def calibrate_regions(self):
        if not PYNPUT_AVAILABLE:
            QMessageBox.warning(self, "Error", "pynput not available. Install with: pip install pynput")
            return

        self.status_bar.showMessage("Click on Level, Gold, HP, Round, Units regions in order...")
        self.click_count = 0
        self.new_bboxes = []

        def on_click(x, y, button, pressed):
            if pressed and button == mouse.Button.left:
                # Create small rect around click point
                rect_size = 30
                bbox = (int(x - rect_size/2), int(y - rect_size/2), int(x + rect_size/2), int(y + rect_size/2))
                self.new_bboxes.append(bbox)
                self.click_count += 1
                self.status_bar.showMessage(f"Clicked {self.click_count}/5: ({x}, {y})")
                if self.click_count >= 5:
                    # Update bboxes
                    self.level_bbox, self.gold_bbox, self.hp_bbox, self.round_bbox, self.units_bbox = self.new_bboxes
                    # Update overlay if visible
                    if hasattr(self, 'overlay') and self.overlay.isVisible():
                        self.overlay.bboxes = self.new_bboxes
                        self.overlay.update()
                    # Update OCR thread bboxes
                    self.ocr_thread.update_bboxes(self.new_bboxes)
                    self.status_bar.showMessage("Calibration complete!")
                    return False  # stop listener

        try:
            with mouse.Listener(on_click=on_click) as listener:
                listener.join()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Calibration failed: {e}")

    def get_game_state(self):
        try:
            level = int(self.level_edit.text())
            gold = int(self.gold_edit.text())
            hp = int(self.hp_edit.text())
            round_str = self.round_edit.text()
            units_raw = self.units_edit.toPlainText().strip()
            units = self.parse_units(units_raw)
            return GameState(level=level, gold=gold, hp=hp, round=round_str, units=units)
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")
            return None

    def parse_units(self, raw):
        if not raw.strip():
            return []
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        units = []
        for p in parts:
            name = ""
            star = 1
            for i, ch in enumerate(p):
                if ch.isdigit():
                    name = p[:i]
                    star = int(p[i:])
                    break
            if not name:
                name = p
            try:
                units.append(UnitInstance(name=name, star=star))
            except ValueError:
                pass  # Ignore invalid
        return units

    def get_comps(self):
        self.status_bar.showMessage("Getting comp suggestions...")
        QApplication.processEvents()
        game_state = self.get_game_state()
        if not game_state:
            self.status_bar.showMessage("Ready")
            return
        target_comp = self.target_comp_edit.text().strip() or None
        try:
            comps = recommend_comps(game_state, target_comp=target_comp)
            self.output_edit.clear()
            self.output_edit.append("Recommended Compositions:\n")
            for comp in comps:
                self.output_edit.append(f"{comp}\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.status_bar.showMessage("Ready")

    def get_econ(self):
        self.status_bar.showMessage("Getting econ advice...")
        QApplication.processEvents()
        game_state = self.get_game_state()
        if not game_state:
            self.status_bar.showMessage("Ready")
            return
        try:
            advice = econ_advice(game_state)
            self.output_edit.clear()
            self.output_edit.append(f"Econ Advice: {advice}\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.status_bar.showMessage("Ready")

    def get_items(self):
        self.status_bar.showMessage("Getting item suggestions...")
        QApplication.processEvents()
        game_state = self.get_game_state()
        if not game_state:
            self.status_bar.showMessage("Ready")
            return
        try:
            items = recommend_items(game_state)
            self.output_edit.clear()
            self.output_edit.append("Recommended Items:\n")
            for item in items:
                self.output_edit.append(f"{item}\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.status_bar.showMessage("Ready")

    def view_logs(self):
        self.status_bar.showMessage("Loading recent logs...")
        QApplication.processEvents()
        try:
            logs = read_logs(limit=TOP_N_LOGS_TO_SHOW)
            self.output_edit.clear()
            self.output_edit.append("Recent Game Logs:\n")
            for log in logs:
                self.output_edit.append(f"{log}\n")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
        self.status_bar.showMessage("Ready")

    def start_ocr(self):
        if not self.ocr_thread.isRunning():
            self.ocr_thread.start()
            self.ocr_btn.setText("⏹️ Stop Auto OCR")
            self.status_bar.showMessage("OCR running...")
        else:
            self.ocr_thread.stop()
            self.ocr_btn.setText("🤖 Start Auto OCR")
            self.status_bar.showMessage("OCR stopped")

    def show_debug_overlay(self):
        if hasattr(self, 'overlay') and self.overlay.isVisible():
            self.overlay.hide()
            self.debug_btn.setText("🔍 Debug Overlay")
        else:
            bboxes = [
                (100, 100, 150, 120),  # level
                (200, 100, 250, 120),  # gold
                (300, 100, 350, 120),  # hp
                (400, 100, 450, 120),  # round
                (100, 200, 500, 250),  # units
            ]
            self.overlay = OverlayWindow(bboxes)
            self.debug_btn.setText("❌ Hide Overlay")

    def update_from_ocr(self, result):
        self.level_edit.setText(str(result['level']))
        self.gold_edit.setText(str(result['gold']))
        self.hp_edit.setText(str(result['hp']))
        self.round_edit.setText(result['round'])
        units_str = ', '.join([f"{u.name}{u.star}" for u in result['units']])
        self.units_edit.setPlainText(units_str)

        # Update output
        self.output_edit.clear()
        self.output_edit.append("Auto-detected Game State:\n")
        self.output_edit.append(f"Level: {result['level']}, Gold: {result['gold']}, HP: {result['hp']}, Round: {result['round']}\n")
        self.output_edit.append(f"Units: {units_str}\n\n")
        self.output_edit.append("Recommended Compositions:\n")
        for comp in result['comps']:
            self.output_edit.append(f"{comp}\n")
        self.output_edit.append(f"\nEcon Advice: {result['econ']}\n")
        self.output_edit.append("Recommended Items:\n")
        for item in result['items']:
            self.output_edit.append(f"{item}\n")

    def show_about(self):
        about_text = """TFT AutoBot - Rank Assistant

A tool to support decision-making for compositions, economy, and items in Teamfight Tactics.

Version: 2.0.0
Built with Python and PyQt5

Features:
- Comp Suggestions based on game state
- Econ Advice (ROLL/LEVEL/SAVE)
- Item Recommendations
- Game Logging and Analysis
- Riot API Integration
- Auto OCR Detection from screen

For more info, visit the GitHub repository."""
        QMessageBox.about(self, "About TFT AutoBot", about_text)


def main():
    app = QApplication(sys.argv)
    window = TFTAssistantGUI()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()