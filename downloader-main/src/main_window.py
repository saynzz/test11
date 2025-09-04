from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import sys
import os
import json
import time
import random
from downloader import VideoDownloader

# Базовый класс VideoDownloader (оставьте как есть)
class VideoDownloader:
    def __init__(self):
        self.queue = []
        self.download_dir = os.getcwd()
        self.options = {}
        
    def set_download_dir(self, directory):
        """Устанавливает директорию для сохранения файлов"""
        self.download_dir = directory
        if not os.path.exists(directory):
            os.makedirs(directory)
    
    def set_options(self, options):
        """Устанавливает опции загрузки"""
        self.options = options
    
    def add_to_queue(self, url):
        """Добавляет URL в очередь загрузки"""
        self.queue.append(url)
    
    def download(self, url):
        """Имитация загрузки видео"""
        try:
            # Имитация процесса загрузки
            time.sleep(1)
            
            # Определяем расширение файла
            format_ext = {
                "video+audio": "mp4",
                "video_only": "mp4",
                "audio_only": "mp3"
            }
            ext = format_ext.get(self.options.get('format', 'video+audio'), 'mp4')
            
            # Генерация имени файла
            filename = f"video_{hash(url) % 10000}.{ext}"
            filepath = os.path.join(self.download_dir, filename)
            
            return {
                'status': 'success',
                'path': filepath,
                'message': 'Download completed successfully'
            }
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Download failed: {str(e)}'
            }

# Базовый класс Reporter (оставьте как есть)
class Reporter:
    def save_report(self, results):
        """Сохраняет отчет о загрузках"""
        try:
            report_dir = os.path.join(os.getcwd(), "reports")
            if not os.path.exists(report_dir):
                os.makedirs(report_dir)
            
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            report_file = os.path.join(report_dir, f"report_{timestamp}.txt")
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write("=== VIDEO DOWNLOAD REPORT ===\n")
                f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("=" * 30 + "\n\n")
                
                success_count = sum(1 for r in results.values() if '✅' in r)
                total_count = len(results)
                
                f.write(f"Total: {total_count}\n")
                f.write(f"Successful: {success_count}\n")
                f.write(f"Failed: {total_count - success_count}\n\n")
                
                f.write("DETAILS:\n")
                f.write("-" * 20 + "\n")
                
                for url, result in results.items():
                    f.write(f"URL: {url}\n")
                    f.write(f"Result: {result}\n")
                    f.write("-" * 20 + "\n")
            
            return True
        except Exception as e:
            print(f"Error saving report: {e}")
            return False


# Класс DownloadThread должен быть определен ДО MainWindow
class DownloadThread(QThread):
    progress_signal = pyqtSignal(int, int, str, dict)
    result_signal = pyqtSignal(dict)
    
    def __init__(self, downloader):
        super().__init__()
        self.downloader = downloader
    
    def run(self):
        results = {}
        for i, url in enumerate(self.downloader.queue):
            if hasattr(self.downloader, '_stop_flag') and self.downloader._stop_flag:
                break
                
            result = self.downloader.download(url)
            results[url] = result
            self.progress_signal.emit(i, len(self.downloader.queue), url, {})
        
        self.result_signal.emit(results)

# Основной класс MainWindow
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.downloader = VideoDownloader()
        self.reporter = Reporter()
        self.current_language = "ru"
        self.dark_theme = True
        self.setup_ui()
        self.setup_translations()
        self.setup_styles()
        self.load_presets()
    
    def setup_ui(self):
        self.setWindowTitle("🔥 Ultra Video Downloader PRO")
        self.setGeometry(100, 100, 900, 750)
        
        # Главный виджет
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        
        # Основной layout
        layout = QVBoxLayout()
        main_widget.setLayout(layout)
        
        # Верхняя панель с настройками
        top_layout = QHBoxLayout()
        
        # Выбор языка
        self.language_combo = QComboBox()
        self.language_combo.addItems(["🇷🇺 Русский", "🇺🇸 English"])
        self.language_combo.currentIndexChanged.connect(self.change_language)
        
        # Переключение темы
        self.theme_btn = QPushButton("🌙 Темная тема")
        self.theme_btn.clicked.connect(self.toggle_theme)
        
        top_layout.addWidget(QLabel("Язык:"))
        top_layout.addWidget(self.language_combo)
        top_layout.addStretch()
        top_layout.addWidget(self.theme_btn)
        
        layout.addLayout(top_layout)
        
        # Шапка
        self.header = QLabel("ULTRA VIDEO DOWNLOADER")
        self.header.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.header)
        
        # Блок настроек
        self.settings_group = QGroupBox("⚙️ Настройки загрузки")
        settings_layout = QGridLayout()
        
        # Выбор папки
        self.folder_input = QLineEdit(os.getcwd())
        self.browse_btn = QPushButton("Обзор...")
        self.browse_btn.clicked.connect(self.select_folder)
        
        # Пресеты качества (добавлен 2160p)
        self.quality_combo = QComboBox()
        self.quality_combo.addItems(["2160p (макс)", "1440p", "1080p", "720p", "480p", "360p", "240p", "144p"])
        
        # Форматы (убрана опция "Только звук")
        self.format_combo = QComboBox()
        self.format_combo.addItems(["Видео+Звук", "Только видео"])
        
        # Водяные знаки и VPN
        self.watermark_check = QCheckBox("Удалять водяные знаки")
        self.vpn_check = QCheckBox("Использовать VPN")
        
        # Пресеты
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("По умолчанию")
        self.preset_combo.currentTextChanged.connect(self.load_selected_preset)
        self.save_preset_btn = QPushButton("💾 Сохранить пресет")
        self.save_preset_btn.clicked.connect(self.save_preset)
        self.save_watermark_btn = QPushButton("💧 Сохранить с водяным знаком")
        self.save_watermark_btn.clicked.connect(self.save_with_watermark)
        
        # Добавляем элементы
        settings_layout.addWidget(QLabel("Папка сохранения:"), 0, 0)
        settings_layout.addWidget(self.folder_input, 0, 1)
        settings_layout.addWidget(self.browse_btn, 0, 2)
        settings_layout.addWidget(QLabel("Качество:"), 1, 0)
        settings_layout.addWidget(self.quality_combo, 1, 1)
        settings_layout.addWidget(QLabel("Формат:"), 2, 0)
        settings_layout.addWidget(self.format_combo, 2, 1)
        settings_layout.addWidget(self.watermark_check, 3, 0, 1, 2)
        settings_layout.addWidget(self.vpn_check, 4, 0, 1, 2)
        settings_layout.addWidget(QLabel("Пресеты:"), 5, 0)
        settings_layout.addWidget(self.preset_combo, 5, 1)
        settings_layout.addWidget(self.save_preset_btn, 5, 2)
        settings_layout.addWidget(self.save_watermark_btn, 6, 0, 1, 3)
        
        self.settings_group.setLayout(settings_layout)
        layout.addWidget(self.settings_group)
        
        # Блок загрузки
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("✏️ Вставьте ссылку на видео...")
        
        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("➕ Добавить в очередь")
        self.add_btn.clicked.connect(self.add_url)
        self.download_btn = QPushButton("⏬ Начать загрузку")
        self.download_btn.clicked.connect(self.start_download)
        self.extract_audio_btn = QPushButton("🎵 Извлечь звук")
        self.extract_audio_btn.clicked.connect(self.extract_audio)
        
        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.download_btn)
        btn_layout.addWidget(self.extract_audio_btn)
        
        # Прогресс бар
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        
        # Лог действий
        self.log_area = QTextEdit()
        self.log_area.setReadOnly(True)
        
        # Добавляем элементы
        layout.addWidget(self.url_input)
        layout.addLayout(btn_layout)
        layout.addWidget(self.progress)
        layout.addWidget(self.log_area)
        
        # Статус бар
        self.status_bar = self.statusBar()
        self.update_status("🟢 Готов к работе")
    
    def setup_translations(self):
        self.translations = {
            "ru": {
                "header": "ULTRA VIDEO DOWNLOADER",
                "settings": "⚙️ Настройки загрузки",
                "folder": "Папка сохранения:",
                "browse": "Обзор...",
                "quality": "Качество:",
                "format": "Формат:",
                "watermark": "Удалять водяные знаки",
                "vpn": "Использовать VPN",
                "presets": "Пресеты:",
                "save_preset": "💾 Сохранить пресет",
                "save_watermark": "💧 Сохранить с водяным знаком",
                "placeholder": "✏️ Вставьте ссылку на видео...",
                "add": "➕ Добавить в очередь",
                "download": "⏬ Начать загрузку",
                "extract_audio": "🎵 Извлечь звук",
                "ready": "🟢 Готов к работе",
                "theme_btn": "🌙 Темная тема",
                "language": "Язык:"
            },
            "en": {
                "header": "ULTRA VIDEO DOWNLOADER",
                "settings": "⚙️ Download Settings",
                "folder": "Save folder:",
                "browse": "Browse...",
                "quality": "Quality:",
                "format": "Format:",
                "watermark": "Remove watermarks",
                "vpn": "Use VPN",
                "presets": "Presets:",
                "save_preset": "💾 Save preset",
                "save_watermark": "💧 Save with watermark",
                "placeholder": "✏️ Paste video link...",
                "add": "➕ Add to queue",
                "download": "⏬ Start download",
                "extract_audio": "🎵 Extract audio",
                "ready": "🟢 Ready to work",
                "theme_btn": "🌙 Dark theme",
                "language": "Language:"
            }
        }
    
    def change_language(self):
        if self.language_combo.currentText() == "🇺🇸 English":
            self.current_language = "en"
        else:
            self.current_language = "ru"
        
        self.translate_ui()
    
    def translate_ui(self):
        trans = self.translations[self.current_language]
        
        self.header.setText(trans["header"])
        self.settings_group.setTitle(trans["settings"])
        self.settings_group.layout().itemAtPosition(0, 0).widget().setText(trans["folder"])
        self.browse_btn.setText(trans["browse"])
        self.settings_group.layout().itemAtPosition(1, 0).widget().setText(trans["quality"])
        self.settings_group.layout().itemAtPosition(2, 0).widget().setText(trans["format"])
        self.watermark_check.setText(trans["watermark"])
        self.vpn_check.setText(trans["vpn"])
        self.settings_group.layout().itemAtPosition(5, 0).widget().setText(trans["presets"])
        self.save_preset_btn.setText(trans["save_preset"])
        self.save_watermark_btn.setText(trans["save_watermark"])
        self.url_input.setPlaceholderText(trans["placeholder"])
        self.add_btn.setText(trans["add"])
        self.download_btn.setText(trans["download"])
        self.extract_audio_btn.setText(trans["extract_audio"])
        self.theme_btn.setText("🌙 Темная тема" if self.current_language == "ru" else "🌙 Dark theme")
        self.update_status(trans["ready"])
        
        # Обновляем заголовки в layout
        top_layout = self.centralWidget().layout().itemAt(0).layout()
        top_layout.itemAt(0).widget().setText(trans["language"])
        
        # Обновляем стиль заголовка при смене языка
        self.update_header_style()
    
    def toggle_theme(self):
        self.dark_theme = not self.dark_theme
        self.setup_styles()
        
        if self.dark_theme:
            self.theme_btn.setText("🌙 Темная тема" if self.current_language == "ru" else "🌙 Dark theme")
        else:
            self.theme_btn.setText("☀️ Светлая тема" if self.current_language == "ru" else "☀️ Light theme")
    
    def update_header_style(self):
        """Обновляет стиль заголовка в зависимости от темы"""
        if self.dark_theme:
            self.header.setStyleSheet("font-size: 20px; font-weight: bold; color: #ffffff;")
        else:
            self.header.setStyleSheet("font-size: 20px; font-weight: bold; color: #000000;")
    
    def setup_styles(self):
        if self.dark_theme:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #1e1e2e;
                }
                QLabel, QGroupBox {
                    color: #ffffff;
                    font-size: 14px;
                }
                QGroupBox {
                    border: 2px solid #4cc9f0;
                    border-radius: 5px;
                    margin-top: 10px;
                    background-color: #252526;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #4cc9f0;
                }
                QPushButton {
                    background-color: #4361ee;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #4895ef;
                }
                QPushButton:pressed {
                    background-color: #3a0ca3;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #252526;
                    color: white;
                    border: 1px solid #4cc9f0;
                    border-radius: 3px;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #252526;
                    color: white;
                    selection-background-color: #4361ee;
                    selection-color: white;
                }
                QProgressBar {
                    border: 1px solid #4cc9f0;
                    border-radius: 3px;
                    text-align: center;
                    color: white;
                    background-color: #252526;
                }
                QProgressBar::chunk {
                    background-color: #f72585;
                }
                QCheckBox {
                    color: #ffffff;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:checked {
                    background-color: #4361ee;
                    border: 1px solid #4cc9f0;
                }
                QTextEdit {
                    background-color: #1a1a2e;
                    color: #00ff88;
                    font-family: 'Courier New';
                    font-size: 12px;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #f5f5f5;
                }
                QLabel, QGroupBox {
                    color: #333333;
                    font-size: 14px;
                }
                QGroupBox {
                    border: 2px solid #007acc;
                    border-radius: 5px;
                    margin-top: 10px;
                    background-color: #ffffff;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    left: 10px;
                    padding: 0 5px 0 5px;
                    color: #007acc;
                }
                QPushButton {
                    background-color: #007acc;
                    color: white;
                    border: none;
                    padding: 8px;
                    border-radius: 5px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1e90ff;
                }
                QPushButton:pressed {
                    background-color: #005a9e;
                }
                QLineEdit, QTextEdit, QComboBox {
                    background-color: #ffffff;
                    color: #333333;
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    padding: 5px;
                }
                QComboBox QAbstractItemView {
                    background-color: #ffffff;
                    color: #333333;
                    selection-background-color: #007acc;
                    selection-color: white;
                }
                QProgressBar {
                    border: 1px solid #cccccc;
                    border-radius: 3px;
                    text-align: center;
                    color: #333333;
                    background-color: #ffffff;
                }
                QProgressBar::chunk {
                    background-color: #007acc;
                }
                QCheckBox {
                    color: #333333;
                    spacing: 5px;
                }
                QCheckBox::indicator {
                    width: 16px;
                    height: 16px;
                }
                QCheckBox::indicator:checked {
                    background-color: #007acc;
                    border: 1px solid #005a9e;
                }
                QTextEdit {
                    background-color: #ffffff;
                    color: #008000;
                    font-family: 'Courier New';
                    font-size: 12px;
                    border: 1px solid #cccccc;
                }
            """)
        
        # Обновляем стиль заголовка
        self.update_header_style()
    
    def load_presets(self):
        try:
            presets_file = os.path.join(os.path.dirname(__file__), 'presets.json')
            if os.path.exists(presets_file):
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
                    self.preset_combo.addItems(presets.keys())
        except Exception as e:
            self.log_area.append(f"❌ Ошибка загрузки пресетов: {str(e)}")
    
    def save_preset(self):
        name, ok = QInputDialog.getText(self, 
            'Сохранение пресета' if self.current_language == 'ru' else 'Save preset',
            'Введите название пресета:' if self.current_language == 'ru' else 'Enter preset name:')
        
        if ok and name:
            preset = {
                'quality': self.quality_combo.currentText(),
                'format': self.format_combo.currentText(),
                'watermark': self.watermark_check.isChecked(),
                'vpn': self.vpn_check.isChecked()
            }
            
            try:
                presets_file = os.path.join(os.path.dirname(__file__), 'presets.json')
                if os.path.exists(presets_file):
                    with open(presets_file, 'r', encoding='utf-8') as f:
                        presets = json.load(f)
                else:
                    presets = {}
                    
                presets[name] = preset
                
                with open(presets_file, 'w', encoding='utf-8') as f:
                    json.dump(presets, f, ensure_ascii=False, indent=2)
                
                self.preset_combo.clear()
                self.preset_combo.addItems(["По умолчанию"] + list(presets.keys()))
                self.log_area.append(f"💾 Пресет '{name}' сохранен")
                
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось сохранить пресет: {str(e)}")

    def load_selected_preset(self, preset_name):
        if preset_name == "По умолчанию":
            return
            
        try:
            presets_file = os.path.join(os.path.dirname(__file__), 'presets.json')
            if os.path.exists(presets_file):
                with open(presets_file, 'r', encoding='utf-8') as f:
                    presets = json.load(f)
                    
                if preset_name in presets:
                    preset = presets[preset_name]
                    self.quality_combo.setCurrentText(preset['quality'])
                    self.format_combo.setCurrentText(preset['format'])
                    self.watermark_check.setChecked(preset['watermark'])
                    self.vpn_check.setChecked(preset['vpn'])
                    
                    self.log_area.append(f"📂 Загружен пресет: {preset_name}")
        except Exception as e:
            self.log_area.append(f"❌ Ошибка загрузки пресета: {str(e)}")
    
    def save_with_watermark(self):
        """Сохраняет видео с водяным знаком"""
        self.watermark_check.setChecked(False)
        self.log_area.append("💧 Режим: сохранение с водяным знаком")
    
    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 
            "Выберите папку для сохранения" if self.current_language == 'ru' else "Select save folder")
        if folder:
            self.folder_input.setText(folder)
            self.downloader.set_download_dir(folder)
    
    def add_url(self):
        url = self.url_input.text().strip()
        if url:
            self.downloader.add_to_queue(url)
            self.log_area.append(f"✅ Добавлено в очередь: {url}")
            self.url_input.clear()
            self.update_status(f"📥 В очереди: {len(self.downloader.queue)} видео")
        else:
            QMessageBox.warning(self, "Ошибка", 
                "Пожалуйста, введите URL видео" if self.current_language == 'ru' else "Please enter video URL")
    
    def extract_audio(self):
        url = self.url_input.text().strip()
        if url:
            # Устанавливаем формат "audio_only" для извлечения звука
            options = {
                'quality': self.quality_combo.currentText().split(' ')[0],
                'format': 'audio_only',
                'watermark': self.watermark_check.isChecked(),
                'vpn': self.vpn_check.isChecked(),
                'output_dir': self.folder_input.text()
            }
            self.downloader.set_options(options)
            
            self.downloader.add_to_queue(url)
            self.log_area.append(f"🎵 Добавлено в очередь для извлечения звука: {url}")
            self.url_input.clear()
            self.update_status(f"📥 В очереди: {len(self.downloader.queue)} аудио")
            
            # Автоматически начинаем загрузку для извлечения звука
            self.start_download()
        else:
            QMessageBox.warning(self, "Ошибка", 
                "Пожалуйста, введите URL видео" if self.current_language == 'ru' else "Please enter video URL")
    
    def start_download(self):
        if not self.downloader.queue:
            QMessageBox.warning(self, "Ошибка", 
                "Очередь загрузки пуста" if self.current_language == 'ru' else "Download queue is empty")
            return
            
        # Настраиваем параметры загрузки
        options = {
            'quality': self.quality_combo.currentText().split(' ')[0],
            'format': self._get_format_key(),
            'watermark': self.watermark_check.isChecked(),
            'vpn': self.vpn_check.isChecked(),
            'output_dir': self.folder_input.text()
        }
        
        self.downloader.set_options(options)
        self.downloader.set_download_dir(self.folder_input.text())
        
        self.progress.setMaximum(len(self.downloader.queue))
        self.progress.setValue(0)
        self.progress.setVisible(True)
        
        self.log_area.append("\n🚀 Начинаю загрузку..." if self.current_language == 'ru' else "\n🚀 Starting download...")
        QApplication.processEvents()
        
        # Запускаем загрузку в отдельном потоке
        self.download_thread = DownloadThread(self.downloader)
        self.download_thread.progress_signal.connect(self.update_progress)
        self.download_thread.result_signal.connect(self.handle_download_result)
        self.download_thread.start()
    
    def update_progress(self, index, total, url, progress_data):
        """Обновляет прогресс загрузки"""
        self.progress.setValue(index + 1)
        self.log_area.append(f"{index+1}/{total}. Загрузка: {url}")
    
    def handle_download_result(self, results):
        """Обрабатывает результаты загрузки"""
        self.progress.setVisible(False)
        
        success_count = sum(1 for r in results.values() if r.get('status') == 'success')
        total_count = len(results)
        
        for url, result in results.items():
            if result.get('status') == 'success':
                self.log_area.append(f"✅ {url} - Успешно: {result.get('path', '')}")
            else:
                self.log_area.append(f"❌ {url} - Ошибка: {result.get('message', '')}")
        
        # Сохраняем отчет
        try:
            self.reporter.save_report(results)
            self.log_area.append("📊 Отчет сохранен" if self.current_language == 'ru' else "📊 Report saved")
        except Exception as e:
            self.log_area.append(f"❌ Ошибка сохранения отчета: {str(e)}")
        
        self.downloader.queue.clear()
        
        msg = QMessageBox()
        msg.setWindowTitle("🎉 Завершено!" if self.current_language == 'ru' else "🎉 Completed!")
        msg.setText(f"Загрузка завершена!\nУспешно: {success_count}/{total_count}" if self.current_language == 'ru' else f"Download completed!\nSuccessful: {success_count}/{total_count}")
        msg.exec_()
        
        self.update_status("🟢 Готов к работе" if self.current_language == 'ru' else "🟢 Ready to work")
    
    def _get_format_key(self):
        """Преобразует русские названия форматов в ключи"""
        format_map = {
            "Видео+Звук": "video+audio",
            "Только видео": "video_only"
        }
        return format_map.get(self.format_combo.currentText(), "video+audio")
    
    def update_status(self, message):
        self.status_bar.showMessage(message)

def run_gui():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    run_gui()