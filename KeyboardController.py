from pynput.keyboard import Controller, KeyCode

# https://learn.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

class KeyboardController():
    def __init__(self):
        self.keyboard = Controller()
    
    def pause(self):
        self.keyboard.press(KeyCode.from_vk(0xB3))
    
    def next_song(self):
        self.keyboard.press(KeyCode.from_vk(0xB0))
    
    def prev_song(self):
        self.keyboard.press(KeyCode.from_vk(0xB1))