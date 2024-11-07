import tkinter as tk
from tkinter import ttk
import threading
from pystray import MenuItem as item
import pystray
from PIL import Image, ImageDraw
import sys
import os
import textwrap

class Widget(tk.Tk):

    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        self.attributes('-alpha', 0.9)
        self.geometry('400x300+100+100')  # Increased window size
        
        # Configure the main window
        self.configure(bg='#f0f0f0')
        self.frame = ttk.Frame(self, padding="10")
        self.frame.pack(fill=tk.BOTH, expand=True)
        
        # Load text from daily-text.txt
        self.text_items = self.load_text_from_file('daily-text.txt')
        self.current_index = 0
        
        # Create text display frame
        text_frame = ttk.Frame(self.frame)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Create styled label with text wrapping
        self.label = ttk.Label(
            text_frame,
            wraplength=360,  # Increased wrap length
            justify=tk.LEFT,  # Changed to left alignment
            padding=(15, 15),
            style='Custom.TLabel'
        )
        self.label.pack(fill=tk.BOTH, expand=True)
        
        # Create navigation frame
        nav_frame = ttk.Frame(self.frame)
        nav_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Add counter label
        self.counter_label = ttk.Label(
            nav_frame,
            style='Counter.TLabel',
            padding=(0, 0, 0, 5)
        )
        self.counter_label.pack(side=tk.TOP, fill=tk.X)
        
        # Create button frame
        button_frame = ttk.Frame(nav_frame)
        button_frame.pack(fill=tk.X)
        
        # Create styled buttons
        self.prev_button = ttk.Button(
            button_frame,
            text="← Previous",
            command=self.show_previous_text,
            style='Custom.TButton'
        )
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(
            button_frame,
            text="Next →",
            command=self.show_next_text,
            style='Custom.TButton'
        )
        self.next_button.pack(side=tk.RIGHT, padx=5)
        
        # Configure custom styles
        self.style = ttk.Style()
        self.style.configure(
            'Custom.TLabel',
            background='#ffffff',
            font=('Segoe UI', 11),
            wraplength=360
        )
        self.style.configure(
            'Counter.TLabel',
            font=('Segoe UI', 9),
            foreground='#666666',
            padding=(0, 5),
            anchor='center'
        )
        self.style.configure(
            'Custom.TButton',
            padding=5,
            font=('Segoe UI', 9)
        )
        
        # Show initial text
        self.update_text()

    def load_text_from_file(self, filename):
        try:
            with open(filename, 'r') as file:
                # Strip whitespace and filter out empty lines
                return [line.strip() for line in file.readlines() if line.strip()]
        except FileNotFoundError:
            return ["Text file not found!"]

    def update_text(self):
        # Wrap text and update label
        text = self.text_items[self.current_index]
        wrapped_text = textwrap.fill(text, width=60)  # Adjusted width
        self.label.config(text=wrapped_text)
        
        # Update counter label
        total = len(self.text_items)
        current = self.current_index + 1
        self.counter_label.config(text=f"{current} of {total}")
        
    def show_previous_text(self):
        self.current_index = (self.current_index - 1) % len(self.text_items)
        self.update_text()

    def show_next_text(self):
        self.current_index = (self.current_index + 1) % len(self.text_items)
        self.update_text()

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
        self.update_text()
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
            item('Restart', self.restart_app),
            item('Exit', self.exit_app)
        )
        
        # Create the icon
        self.icon = pystray.Icon("name", image, "Daily Text", menu)
        self.icon.run_detached()

    def show_window(self):
        self.deiconify()

    def hide_window(self):
        self.withdraw()

    def restart_app(self):
        """Restart the entire application"""
        # Clean up current instance
        if self.timer.is_alive():
            self.timer.cancel()
        if self.icon:
            self.icon.stop()
        self.quit()  # Properly quit Tkinter
        
        # Start new process
        os.startfile(sys.argv[0])  # Start new instance
        sys.exit()  # Exit current instance

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