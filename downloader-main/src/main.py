import sys
from PyQt5.QtWidgets import QApplication
from main_window import MainWindow  # Импортируем класс, а не модуль

def main():
    app = QApplication(sys.argv)
    
    app.setStyle('Fusion')
    
    window = MainWindow()  # Создаем экземпляр класса MainWindow
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()