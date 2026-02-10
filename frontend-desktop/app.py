
import sys
import requests
import json
import base64
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QTableWidget,
    QTableWidgetItem, QTabWidget, QMessageBox, QHeaderView
)
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

API_URL = "http://localhost:8000/api"

class ChartWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots(1, 2, figsize=(10, 4))
        self.canvas = FigureCanvas(self.figure)
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_charts(self, summary):
        self.ax[0].clear()
        self.ax[1].clear()

        # Type distribution (Pie)
        dist = summary.get('type_distribution', {})
        if dist:
            self.ax[0].pie(dist.values(), labels=dist.keys(), autopct='%1.1f%%', colors=plt.cm.Paired.colors)
            self.ax[0].set_title("Type Distribution")

        # Averages (Bar)
        labels = ['Flow', 'Press', 'Temp']
        vals = [summary['avg_flowrate'], summary['avg_pressure'], summary['avg_temperature']]
        self.ax[1].bar(labels, vals, color=['blue', 'green', 'red'])
        self.ax[1].set_title("Averages benchmark")

        self.figure.tight_layout()
        self.canvas.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.resize(1000, 700)
        
        self.username = ""
        self.password = ""
        self.current_summary = None

        self.init_ui()

    def init_ui(self):
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Tab 1: Login & Upload
        self.login_tab = QWidget()
        self.init_login_tab()
        self.tabs.addTab(self.login_tab, "Auth & Upload")

        # Tab 2: Summary & Charts
        self.summary_tab = QWidget()
        self.init_summary_tab()
        self.tabs.addTab(self.summary_tab, "Dashboard")

        # Tab 3: History
        self.history_tab = QWidget()
        self.init_history_tab()
        self.tabs.addTab(self.history_tab, "History")

    def init_login_tab(self):
        layout = QVBoxLayout()
        
        title = QLabel("System Access")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4f46e5; margin-bottom: 20px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        form_layout = QVBoxLayout()
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Username")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Password")
        self.pass_input.setEchoMode(QLineEdit.Password)
        
        form_layout.addWidget(QLabel("Credentials"))
        form_layout.addWidget(self.user_input)
        form_layout.addWidget(self.pass_input)
        
        self.login_btn = QPushButton("Connect to Server")
        self.login_btn.clicked.connect(self.handle_login)
        form_layout.addWidget(self.login_btn)
        
        layout.addLayout(form_layout)
        layout.addSpacing(40)
        
        self.upload_btn = QPushButton("Upload CSV Data")
        self.upload_btn.setEnabled(False)
        self.upload_btn.setFixedSize(200, 50)
        self.upload_btn.clicked.connect(self.handle_upload)
        layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        
        layout.addStretch()
        self.login_tab.setLayout(layout)

    def init_summary_tab(self):
        layout = QVBoxLayout()
        
        self.summary_lbl = QLabel("No data loaded. Please upload a CSV first.")
        self.summary_lbl.setWordWrap(True)
        self.summary_lbl.setStyleSheet("font-size: 14px; padding: 10px; background-color: #f3f4f6; border-radius: 5px;")
        layout.addWidget(self.summary_lbl)
        
        self.chart_widget = ChartWidget()
        layout.addWidget(self.chart_widget)
        
        self.summary_tab.setLayout(layout)

    def init_history_tab(self):
        layout = QVBoxLayout()
        
        self.history_table = QTableWidget(0, 5)
        self.history_table.setHorizontalHeaderLabels(["ID", "Filename", "Count", "Avg Flow", "Action"])
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.history_table)
        
        self.refresh_btn = QPushButton("Refresh History")
        self.refresh_btn.clicked.connect(self.fetch_history)
        layout.addWidget(self.refresh_btn)
        
        self.history_tab.setLayout(layout)

    def get_auth_headers(self):
        auth_str = f"{self.username}:{self.password}"
        b64_auth = base64.b64encode(auth_str.encode()).decode()
        return {"Authorization": f"Basic {b64_auth}"}

    def handle_login(self):
        self.username = self.user_input.text()
        self.password = self.pass_input.text()
        
        # Test connection
        try:
            resp = requests.get(f"{API_URL}/history/", headers=self.get_auth_headers())
            if resp.status_code == 200:
                QMessageBox.information(self, "Success", "Authenticated successfully!")
                self.upload_btn.setEnabled(True)
                self.fetch_history()
            else:
                QMessageBox.warning(self, "Error", "Invalid credentials or server error.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Could not connect: {str(e)}")

    def handle_upload(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open file', '', "CSV files (*.csv)")
        if not fname:
            return
            
        try:
            with open(fname, 'rb') as f:
                files = {'file': f}
                resp = requests.post(f"{API_URL}/upload/", files=files, headers=self.get_auth_headers())
                
                if resp.status_code == 201:
                    data = resp.json()
                    self.current_summary = data
                    self.update_dashboard(data)
                    self.tabs.setCurrentIndex(1)
                    self.fetch_history()
                else:
                    QMessageBox.warning(self, "Upload Failed", resp.json().get('error', 'Unknown error'))
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Upload failed: {str(e)}")

    def update_dashboard(self, data):
        summary_text = (
            f"<b>File:</b> {data['filename']}<br>"
            f"<b>Count:</b> {data['total_count']} units<br>"
            f"<b>Flowrate:</b> {data['avg_flowrate']:.2f} m³/h<br>"
            f"<b>Pressure:</b> {data['avg_pressure']:.2f} bar<br>"
            f"<b>Temperature:</b> {data['avg_temperature']:.2f} °C"
        )
        self.summary_lbl.setText(summary_text)
        self.chart_widget.update_charts(data)

    def fetch_history(self):
        if not self.username: return
        try:
            resp = requests.get(f"{API_URL}/history/", headers=self.get_auth_headers())
            if resp.status_code == 200:
                data = resp.json()
                self.history_table.setRowCount(0)
                for row_idx, item in enumerate(data):
                    self.history_table.insertRow(row_idx)
                    self.history_table.setItem(row_idx, 0, QTableWidgetItem(str(item['id'])))
                    self.history_table.setItem(row_idx, 1, QTableWidgetItem(item['filename']))
                    self.history_table.setItem(row_idx, 2, QTableWidgetItem(str(item['total_count'])))
                    self.history_table.setItem(row_idx, 3, QTableWidgetItem(f"{item['avg_flowrate']:.2f}"))
                    
                    btn = QPushButton("PDF")
                    btn.clicked.connect(lambda ch, pid=item['id']: self.download_pdf(pid))
                    self.history_table.setCellWidget(row_idx, 4, btn)
        except:
            pass

    def download_pdf(self, pid):
        try:
            params = {"username": self.username, "password": self.password}
            resp = requests.get(f"{API_URL}/report/{pid}/", params=params, stream=True)
            if resp.status_code == 200:
                path, _ = QFileDialog.getSaveFileName(self, "Save Report", f"report_{pid}.pdf", "PDF Files (*.pdf)")
                if path:
                    with open(path, 'wb') as f:
                        for chunk in resp.iter_content(chunk_size=8192):
                            f.write(chunk)
                    QMessageBox.information(self, "Success", "PDF saved!")
            else:
                QMessageBox.warning(self, "Error", "Could not download PDF.")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
