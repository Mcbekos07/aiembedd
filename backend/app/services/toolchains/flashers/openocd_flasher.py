class OpenocdFlasher:
    def flash(self, image_path: str, port: str) -> str:
        return f'openocd flashing {image_path} on {port}'
