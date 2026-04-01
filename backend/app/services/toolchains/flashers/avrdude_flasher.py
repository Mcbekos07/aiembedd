class AvrdudeFlasher:
    def flash(self, image_path: str, port: str) -> str:
        return f'avrdude flashing {image_path} on {port}'
