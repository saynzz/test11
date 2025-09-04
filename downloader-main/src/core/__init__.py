self.current_options = {
    'quality': '720p',
    'format': 'video+audio',
    'include_audio': True,  # True — со звуком, False — только видео
    'output_dir': './downloads',
    'watermark': True
}

self.presets = {
    'default': {
        'quality': '720p',
        'format': 'video+audio',
        'include_audio': True,
        'watermark': True
    },
    'silent_video': {
        'quality': '1080p',
        'format': 'video+audio',
        'include_audio': False,
        'watermark': False
    }
}

def set_options(self, options: Dict):
    self.current_options.update(options)
    if 'preset' in options and options['preset'] in self.presets:
        self.current_options.update(self.presets[options['preset']])
