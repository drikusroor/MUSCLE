from django.core.validators import FileExtensionValidator

valid_extensions = ['wav', 'mp3', 'aiff', 'flac', 'ogg']

def audio_file_validator():
    return FileExtensionValidator(allowed_extensions=valid_extensions)