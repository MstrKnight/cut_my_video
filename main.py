#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cut It Now - Video Cutter Application
A simple GUI application to cut videos into equal parts.
"""

import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
from utils import get_video_duration, cut_video_into_parts

class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cut It Now - Video Cutter")
        self.root.geometry("500x400")
        self.root.resizable(True, True)
        
        # Variables
        self.video_path = tk.StringVar()
        self.num_parts = tk.IntVar(value=2)  # Default: 2 parts
        self.status = tk.StringVar(value="Ready")
        self.is_processing = False
        
        # Get the directory of the executable or script
        if getattr(sys, 'frozen', False):
            # If the application is frozen (compiled)
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # If running as a script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.create_widgets()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video selection
        ttk.Label(main_frame, text="Select Video:", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        self.video_entry = ttk.Entry(video_frame, textvariable=self.video_path, width=50)
        self.video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Button(video_frame, text="Browse", command=self.browse_video).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Number of parts
        parts_frame = ttk.Frame(main_frame)
        parts_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        ttk.Label(parts_frame, text="Number of parts:", font=("Arial", 12)).pack(side=tk.LEFT)
        
        parts_spinner = ttk.Spinbox(parts_frame, from_=2, to=100, width=5, textvariable=self.num_parts)
        parts_spinner.pack(side=tk.LEFT, padx=(5, 0))
        
        # Process button
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        self.process_button = ttk.Button(process_frame, text="Cut Video", command=self.start_cutting)
        self.process_button.pack(fill=tk.X)
        
        # Progress bar and status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=100, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        self.status_label = ttk.Label(progress_frame, textvariable=self.status, font=("Arial", 10))
        self.status_label.pack(fill=tk.X)
        
    def browse_video(self):
        """Open file dialog to select a video file"""
        filetypes = (
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*")
        )
        
        video_file = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=filetypes
        )
        
        if video_file:
            self.video_path.set(video_file)
            self.status.set(f"Video selected: {os.path.basename(video_file)}")
    
    def start_cutting(self):
        """Start the video cutting process"""
        video_path = self.video_path.get()
        num_parts = self.num_parts.get()
        
        if not video_path:
            messagebox.showerror("Error", "Please select a video file")
            return
        
        if num_parts < 2:
            messagebox.showerror("Error", "Number of parts must be at least 2")
            return
        
        # Disable UI while processing
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.status.set("Processing... Getting video information")
        
        # Start processing in a separate thread
        thread = threading.Thread(target=self.process_video, args=(video_path, num_parts))
        thread.daemon = True
        thread.start()
    
    def process_video(self, video_path, num_parts):
        """Process the video in a separate thread"""
        try:
            # Get video duration
            self.status.set("Processing... Analyzing video duration")
            duration = get_video_duration(video_path, self.app_dir)
            
            if duration <= 0:
                self.root.after(0, lambda: self.show_error("Could not determine video duration"))
                return
            
            # Create output directory
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_dir = os.path.join(os.path.dirname(video_path), f"{video_name}_parts")
            os.makedirs(output_dir, exist_ok=True)
            
            # Cut video
            self.status.set("Processing... Cutting video into parts")
            success = cut_video_into_parts(
                video_path, 
                output_dir, 
                num_parts, 
                duration,
                self.app_dir,
                self.update_status
            )
            
            if success:
                self.root.after(0, lambda: self.show_success(output_dir))
            else:
                self.root.after(0, lambda: self.show_error("Error occurred while cutting the video"))
                
        except Exception as e:
            self.root.after(0, lambda: self.show_error(f"Error: {str(e)}"))
        finally:
            # Re-enable UI
            self.root.after(0, self.reset_ui)
    
    def update_status(self, message):
        """Update status label from a thread"""
        self.root.after(0, lambda: self.status.set(message))
    
    def show_success(self, output_dir):
        """Show success message"""
        messagebox.showinfo("Success", f"Video successfully cut into parts!\nOutput directory: {output_dir}")
        self.status.set(f"Done. Files saved to {output_dir}")
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.status.set("Error occurred. Please try again.")
    
    def reset_ui(self):
        """Reset UI after processing"""
        self.is_processing = False
        self.process_button.config(state=tk.NORMAL)
        self.progress_bar.stop()

def main():
    root = tk.Tk()
    app = VideoCutterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
