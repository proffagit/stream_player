import os
import sys

def get_application_path():
    """Get the path to the application directory"""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))

# Update VLC path handling
if os.name == "nt":
    app_path = get_application_path()
    if getattr(sys, 'frozen', False):
        os.environ['PATH'] = app_path + ';' + os.environ['PATH']
        os.add_dll_directory(app_path)
    else:
        vlc_path = r"C:\Program Files\VideoLAN\VLC"
        if os.path.exists(vlc_path):
            os.environ['PATH'] = vlc_path + ';' + os.environ['PATH']
            os.add_dll_directory(vlc_path)

import vlc
import yt_dlp
import tkinter as tk
from tkinter import ttk
import json

class AudioPlayerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Stream Player")
        
        # Prevent window resizing
        self.root.resizable(False, False)
        
        # Try to set window icon if available
        try:
            icon_path = "player_icon.ico"  # Optional icon file
            if os.path.exists(icon_path):
                self.root.iconbitmap(icon_path)
        except:
            pass  # Silently fail if icon isn't available
        
        # Apply dark theme with better contrast
        self.style = ttk.Style()
        self.style.configure(".",
            background="#1e1e1e",
            foreground="#d4d4d4",         # Light gray text
            fieldbackground="#2d2d2d",    # Darker field background
            troughcolor="#2d2d2d"
        )
        
        # Custom styles with improved visibility
        self.style.configure("TFrame", background="#1e1e1e")
        self.style.configure("TLabel", background="#1e1e1e", foreground="#ffffff")
        
        # Distinct button style with better contrast
        self.style.configure("TButton",
            background="#2d2d2d",         # Darker background
            foreground="#d4d4d4",         # Light gray text
            padding=10,
            width=15
        )
        
        # Improved button hover and pressed states
        self.style.map("TButton",
            background=[
                ("active", "#3d3d3d"),    # Slightly lighter on hover
                ("pressed", "#252525")     # Slightly darker when pressed
            ],
            foreground=[
                ("active", "#d4d4d4"),     # Keep light gray text
                ("pressed", "#d4d4d4")     # Keep light gray text
            ]
        )
        
        # Entry style with softer colors
        self.style.configure("TEntry",
            fieldbackground="#2d2d2d",    # Darker background
            foreground="#d4d4d4",         # Light gray text
            padding=5
        )
        
        self.style.configure("Horizontal.TScale",
            background="#1e1e1e",
            troughcolor="#2d2d2d"
        )
        
        # Set window background
        self.root.configure(bg="#1e1e1e")
        
        # Config file path
        self.config_file = "lofi_config.json"
        
        # Default values
        self.default_url = "https://www.youtube.com/watch?v=jfKfPfyJRdk"
        self.default_volume = 50
        
        # Load saved config
        config = self.load_config()
        self.url = config['url']
        self.volume = config['volume']
        
        # Initialize player
        self.instance = vlc.Instance()
        if self.instance is None:
            print("Error: VLC instance could not be created.")
        self.player = self.instance.media_player_new()
        self.is_playing = False
        self.is_stopped = True
        
        # Create GUI elements
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame with reduced padding
        control_frame = ttk.Frame(self.root, padding="5")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(0, weight=1)
        control_frame.grid_columnconfigure(0, weight=1)
        
        # Style configuration for thinner slider
        self.style = ttk.Style()
        self.style.configure("Slim.Horizontal.TScale",
            sliderwidth=10,      # Thinner slider
            sliderlength=15,     # Shorter slider
            troughwidth=3,       # Thinner trough
            background="#1e1e1e"
        )
        
        # URL entry with no label
        self.url_entry = tk.Entry(control_frame, 
            bg="#2d2d2d",
            fg="#d4d4d4",
            insertbackground="#d4d4d4",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#1e1e1e",
            highlightcolor="#3d3d3d"
        )
        self.url_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 4))
        self.url_entry.insert(0, self.url)
        
        # Button frame with reduced bottom padding
        button_frame = ttk.Frame(control_frame)
        button_frame.grid(row=1, column=0, pady=(0, 4), sticky=(tk.W, tk.E))
        button_frame.grid_columnconfigure(1, weight=1)  # Center space takes extra space
        
        # Left side frame for play button and status
        left_frame = ttk.Frame(button_frame)
        left_frame.grid(row=0, column=0, sticky='w')
        
        # Play/Stop button
        self.toggle_button = tk.Button(left_frame, 
            text="▶",
            command=self.toggle_playback,
            bg="#2d2d2d",
            fg="#d4d4d4",
            activebackground="#252525",
            activeforeground="#d4d4d4",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#1e1e1e",
            highlightcolor="#3d3d3d",
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            font=('TkDefaultFont', 14)
        )
        self.toggle_button.grid(row=0, column=0, padx=(0, 5))
        
        # Status label next to play button
        self.play_status = ttk.Label(left_frame, text="Stopped")
        self.play_status.grid(row=0, column=1, padx=(5, 0))
        
        # Volume controls on the right
        volume_frame = ttk.Frame(button_frame)
        volume_frame.grid(row=0, column=2, sticky='e')
        
        # Volume controls
        self.volume_down = tk.Button(volume_frame,
            text="−",
            command=lambda: self.adjust_volume(-5),
            bg="#2d2d2d",
            fg="#d4d4d4",
            activebackground="#252525",
            activeforeground="#d4d4d4",
            relief="flat",
            highlightthickness=0,
            bd=0,
            padx=5,
            pady=0,
            cursor="hand2",
            font=('TkDefaultFont', 10)
        )
        self.volume_down.grid(row=0, column=0)
        
        self.volume_label = ttk.Label(volume_frame, text=f"{self.volume}%", width=4)
        self.volume_label.grid(row=0, column=1)
        
        self.volume_up = tk.Button(volume_frame,
            text="+",
            command=lambda: self.adjust_volume(5),
            bg="#2d2d2d",
            fg="#d4d4d4",
            activebackground="#252525",
            activeforeground="#d4d4d4",
            relief="flat",
            highlightthickness=0,
            bd=0,
            padx=5,
            pady=0,
            cursor="hand2",
            font=('TkDefaultFont', 10)
        )
        self.volume_up.grid(row=0, column=2)
        
        # Set fixed window size with reduced height
        self.root.geometry("350x86")
    
    def load_config(self):
        """Loads the last used URL and volume from config file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    return {
                        'url': config.get('last_url', self.default_url),
                        'volume': config.get('volume', self.default_volume)
                    }
        except Exception:
            pass
        return {'url': self.default_url, 'volume': self.default_volume}
    
    def save_config(self):
        """Saves the current URL and volume to config file"""
        try:
            config = {
                'last_url': self.url,
                'volume': self.volume
            }
            with open(self.config_file, 'w') as f:
                json.dump(config, f)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def start_stream(self):
        try:
            # Get URL from entry field
            self.url = self.url_entry.get()
            self.save_config()  # Save URL when starting stream
            
            ydl_opts = {
                'format': 'bestaudio',
                'quiet': True,
                'no_warnings': True,
                'extract_flat': True,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                audio_url = info['url']
                
                media = self.instance.media_new(audio_url)
                self.player.set_media(media)
                self.player.play()
                self.is_playing = True
                self.toggle_button.config(text="■")    # Alternative stop symbol: ■
                self.play_status.config(text="Playing")
                
        except Exception as e:
            self.play_status.config(text=f"Error: {str(e)}")
    
    def toggle_playback(self):
        if self.is_stopped:
            self.start_stream()
            self.is_stopped = False
            self.toggle_button.config(text="■")
            self.play_status.config(text="Playing")  # Update status text
        else:
            self.player.stop()
            self.is_stopped = True
            self.toggle_button.config(text="▶")
            self.play_status.config(text="Stopped")  # Update status text
            self.is_playing = False
    
    def set_volume(self, value):
        volume = int(float(value))
        self.volume = volume  # Store current volume
        self.player.audio_set_volume(volume)
        self.save_config()  # Save when volume changes
    
    def adjust_volume(self, delta):
        """Adjusts volume by the given delta and updates display"""
        new_volume = max(0, min(100, self.volume + delta))
        self.volume = new_volume
        self.player.audio_set_volume(new_volume)
        self.volume_label.config(text=f"{new_volume}%")
        self.save_config()

def main():
    root = tk.Tk()
    app = AudioPlayerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()