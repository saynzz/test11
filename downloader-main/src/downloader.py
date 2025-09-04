import os
import time
import json
import requests
import yt_dlp
from urllib.parse import urlparse, parse_qs
import re
from datetime import datetime
import threading
from pathlib import Path

class VideoDownloader:
    def __init__(self):
        self.queue = []
        self.download_dir = os.getcwd()
        self.options = {}
        self.current_downloads = {}
        self.is_downloading = False
        self._stop_flag = False
        
    def set_download_dir(self, directory):
        """Устанавливает директорию для сохранения файлов"""
        self.download_dir = directory
        if not os.path.exists(directory):
            os.makedirs(directory)
        return True
    
    def set_options(self, options):
        """Устанавливает опции загрузки"""
        self.options = options
        return True
    
    def add_to_queue(self, url):
        """Добавляет URL в очередь загрузки"""
        if self._validate_url(url):
            self.queue.append(url)
            return True
        return False
    
    def _validate_url(self, url):
        """Проверяет валидность URL"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False
    
    def get_queue_length(self):
        """Возвращает длину очереди"""
        return len(self.queue)
    
    def clear_queue(self):
        """Очищает очередь загрузки"""
        self.queue = []
        return True
    
    def stop_download(self):
        """Останавливает текущую загрузку"""
        self._stop_flag = True
        return True
    
    def _get_ydl_opts(self, url, format_type):
        """Возвращает опции для yt-dlp"""
        output_template = os.path.join(
            self.options.get('output_dir', self.download_dir),
            '%(title)s.%(ext)s'
        )
        
        # Базовые опции
        ydl_opts = {
            'outtmpl': output_template,
            'quiet': True,
            'no_warnings': False,
            'progress_hooks': [self._progress_hook],
        }
        
        # Настройки формата
        if format_type == 'audio_only':
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })
        else:
            # Для видео определяем качество
            quality_map = {
                '2160p': 'bestvideo[height<=2160]+bestaudio/best[height<=2160]',
                '1440p': 'bestvideo[height<=1440]+bestaudio/best[height<=1440]',
                '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
                '240p': 'bestvideo[height<=240]+bestaudio/best[height<=240]',
                '144p': 'bestvideo[height<=144]+bestaudio/best[height<=144]',
            }
            
            quality = self.options.get('quality', '1080p')
            format_string = quality_map.get(quality, 'bestvideo+bestaudio/best')
            
            if format_type == 'video_only':
                format_string = format_string.replace('+bestaudio', '')
            
            ydl_opts['format'] = format_string
        
        # Дополнительные опции
        if self.options.get('watermark', False):
            # Попытка удалить водяные знаки (если поддерживается платформой)
            ydl_opts['postprocessors'] = ydl_opts.get('postprocessors', []) + [{
                'key': 'ExecAfterDownload',
                'exec_cmd': f'ffmpeg -i "%(filepath)q" -c copy -map 0 -y "%(filepath)q"',
            }]
        
        # Настройки VPN (если нужно)
        if self.options.get('vpn', False):
            # Здесь можно добавить прокси-настройки
            # ydl_opts['proxy'] = 'http://your-vpn-proxy:port'
            pass
        
        return ydl_opts
    
    def _progress_hook(self, d):
        """Хук для отслеживания прогресса загрузки"""
        if d['status'] == 'downloading':
            url = d.get('info_dict', {}).get('webpage_url', 'unknown')
            if url in self.current_downloads:
                self.current_downloads[url]['progress'] = d.get('_percent_str', '0%')
                self.current_downloads[url]['speed'] = d.get('_speed_str', 'N/A')
                self.current_downloads[url]['eta'] = d.get('_eta_str', 'N/A')
        
        elif d['status'] == 'finished':
            url = d.get('info_dict', {}).get('webpage_url', 'unknown')
            if url in self.current_downloads:
                self.current_downloads[url]['progress'] = '100%'
                self.current_downloads[url]['status'] = 'processing'
    
    def download(self, url, callback=None):
        """Загружает видео/аудио"""
        if self._stop_flag:
            return {'status': 'cancelled', 'message': 'Download cancelled'}
        
        try:
            format_type = self.options.get('format', 'video+audio')
            ydl_opts = self._get_ydl_opts(url, format_type)
            
            # Инициализируем информацию о загрузке
            self.current_downloads[url] = {
                'status': 'downloading',
                'progress': '0%',
                'speed': 'N/A',
                'eta': 'N/A',
                'start_time': datetime.now()
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                
                if self._stop_flag:
                    return {'status': 'cancelled', 'message': 'Download cancelled'}
                
                # Получаем путь к скачанному файлу
                downloaded_file = ydl.prepare_filename(info)
                
                # Для аудио меняем расширение
                if format_type == 'audio_only':
                    downloaded_file = os.path.splitext(downloaded_file)[0] + '.mp3'
                
                result = {
                    'status': 'success',
                    'path': os.path.abspath(downloaded_file),
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'format': format_type,
                    'message': 'Download completed successfully'
                }
                
                if callback:
                    callback(result)
                
                return result
                
        except yt_dlp.utils.DownloadError as e:
            error_msg = str(e)
            if 'Private video' in error_msg:
                error_msg = 'Video is private'
            elif ' unavailable' in error_msg:
                error_msg = 'Video is unavailable'
            elif 'Sign in' in error_msg:
                error_msg = 'Authentication required'
            
            result = {
                'status': 'error',
                'message': f'Download failed: {error_msg}'
            }
            
            if callback:
                callback(result)
            
            return result
            
        except Exception as e:
            result = {
                'status': 'error',
                'message': f'Download failed: {str(e)}'
            }
            
            if callback:
                callback(result)
            
            return result
        
        finally:
            # Удаляем из текущих загрузок
            if url in self.current_downloads:
                del self.current_downloads[url]
    
    def download_all(self, callback=None):
        """Загружает все видео в очереди"""
        self.is_downloading = True
        self._stop_flag = False
        
        results = {}
        total = len(self.queue)
        
        for i, url in enumerate(self.queue):
            if self._stop_flag:
                break
                
            if callback:
                callback('progress', i, total, url)
            
            result = self.download(url, 
                lambda res: callback('item_progress', i, total, url, res) if callback else None
            )
            
            results[url] = result
            
            if callback:
                callback('item_complete', i, total, url, result)
        
        self.is_downloading = False
        self.queue = []  # Очищаем очередь после загрузки
        
        if callback:
            callback('complete', results)
        
        return results
    
    def get_download_info(self, url):
        """Возвращает информацию о текущей загрузке"""
        return self.current_downloads.get(url, {})
    
    def get_all_downloads_info(self):
        """Возвращает информацию о всех текущих загрузках"""
        return self.current_downloads.copy()

# Система плагинов для поддержки разных платформ
class DownloaderPlugin:
    def can_handle(self, url):
        raise NotImplementedError
        
    def download(self, url, options):
        raise NotImplementedError

class YouTubePlugin(DownloaderPlugin):
    def can_handle(self, url):
        return any(domain in url for domain in ['youtube.com', 'youtu.be'])
    
    def download(self, url, options):
        # Используем базовый метод через yt-dlp
        downloader = VideoDownloader()
        downloader.set_options(options)
        return downloader.download(url)

class VKPlugin(DownloaderPlugin):
    def can_handle(self, url):
        return 'vk.com' in url
    
    def download(self, url, options):
        # Базовая реализация для VK
        # В реальном проекте нужно добавить специфичную логику для VK
        downloader = VideoDownloader()
        downloader.set_options(options)
        return downloader.download(url)

class PluginManager:
    def __init__(self):
        self.plugins = [
            YouTubePlugin(),
            VKPlugin()
        ]
    
    def get_plugin_for_url(self, url):
        for plugin in self.plugins:
            if plugin.can_handle(url):
                return plugin
        return None

# Глобальный экземпляр загрузчика
downloader = VideoDownloader()
plugin_manager = PluginManager()