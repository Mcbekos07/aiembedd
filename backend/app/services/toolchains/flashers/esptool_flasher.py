class EsptoolFlasher:
    def flash(self, image_path: str, port: str) -> str:
        return f'esptool flashing {image_path} on {port}'
