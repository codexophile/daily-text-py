import tkinter as tk
import time
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw

class Widget(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-alpha', 0.8)
        self.geometry('200x150+100+100')
        
        # Load text from daily-text.txt
        self.text_items = self.load_text_from_file('daily-text.txt')
        self.current_index = 0
        
        # Create label to display text
        self.label = tk.Label(self, text=self.text_items[self.current_index])
        self.label.pack(pady=10)
        
        # Create buttons to flip through text items
        self.prev_button = tk.Button(self, text="Previous", command=self.show_previous_text)
        self.prev_button.pack(side=tk.LEFT, padx=10)
        
        self.next_button = tk.Button(self, text="Next", command=self.show_next_text)
        self.next_button.pack(side=tk.RIGHT, padx=10)
        
        # Bind mouse events for dragging
        self.bind('<ButtonPress-1>', self.start_move)
        self.bind('<ButtonRelease-1>', self.stop_move)
        self.bind('<B1-Motion>', self.do_move)
        
        # Start the timer to change text daily
        self.interval = 24 * 60 * 60  # Default interval is 24 hours (in seconds)
        self.start_timer()

        # Create system tray icon
        self.create_system_tray_icon()

    def load_text_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                return file.readlines()
        except FileNotFoundError:
            return ["Text file not found!"]

    def show_previous_text(self):
        self.current_index = (self.current_index - 1) % len(self.text_items)
        self.label.config(text=self.text_items[self.current_index])

    def show_next_text(self):
        self.current_index = (self.current_index + 1) % len(self.text_items)
        self.label.config(text=self.text_items[self.current_index])

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def stop_move(self, event):
        self.x = None
        self.y = None

    def do_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.winfo_x() + deltax
        y = self.winfo_y() + deltay
        self.geometry(f"+{x}+{y}")

    def start_timer(self):
        self.timer = threading.Timer(self.interval, self.change_text)
        self.timer.start()

    def change_text(self):
        self.current_index = (self.current_index + 1) % len(self.text_items)
        self.label.config(text=self.text_items[self.current_index])
        self.start_timer()

    def create_system_tray_icon(self):
        # Create a simple image for the icon
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        dc.rectangle((28, 20, 36, 40), fill='black')
        dc.rectangle((20, 28, 44, 36), fill='black')
        
        # Define menu items
        menu = (
            item('Show', self.show_window),
            item('Hide', self.hide_window),
            item('Exit', self.exit_app)
        )
        
        # Create the icon
        self.icon = pystray.Icon("name", image, "Daily Text", menu)
        self.icon.run_detached()

    def show_window(self):
        self.deiconify()

    def hide_window(self):
        self.withdraw()

    def exit_app(self):
        # Stop the timer if running
        if self.timer.is_alive():
            self.timer.cancel()
        
        # Stop the tray icon
        if self.icon:
            self.icon.stop()
        
        # Destroy the Tkinter window
        self.after(0, self.destroy)


if __name__ == "__main__":
    widget = Widget()
    widget.mainloop()