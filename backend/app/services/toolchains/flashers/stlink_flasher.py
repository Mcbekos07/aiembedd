class StlinkFlasher:
    def flash(self, image_path: str, port: str) -> str:
        return f'stlink flashing {image_path} on {port}'
