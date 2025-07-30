#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Cut It Now - Video Cutter Application
A simple GUI application to cut videos into equal parts.
"""

import os
import sys
import time
import threading
import subprocess
from datetime import timedelta
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

from utils import get_video_duration, cut_video_into_parts, get_video_size, cut_video_by_size, cut_video_by_duration

class VideoCutterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Cut It Now - Video Cutter")
        self.root.geometry("600x500")
        self.root.resizable(True, True)
        
        # Variables
        self.video_path = tk.StringVar()
        self.num_parts = tk.IntVar(value=2)  # Default: 2 parts
        self.status = tk.StringVar(value="Ready")
        self.is_processing = False
        self.elapsed_time = tk.StringVar(value="00:00:00")
        self.split_mode = tk.StringVar(value="parts")  # Default: split by parts
        self.target_size = tk.DoubleVar(value=100)  # Default: 100 MB
        self.target_duration = tk.DoubleVar(value=10)  # Default: 10 minutes
        self.timer_running = False
        self.start_time = 0
        self.timer_id = None
        
        # Get the directory of the executable or script
        if getattr(sys, 'frozen', False):
            # If the application is frozen (compiled)
            self.app_dir = os.path.dirname(sys.executable)
        else:
            # If running as a script
            self.app_dir = os.path.dirname(os.path.abspath(__file__))
        
        self.create_widgets()
        self.setup_drag_drop()
        
    def create_widgets(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Video selection
        ttk.Label(main_frame, text="Select Video (or drag and drop):", font=("Arial", 12)).grid(row=0, column=0, sticky=tk.W, pady=(0, 10))
        
        video_frame = ttk.Frame(main_frame)
        video_frame.grid(row=1, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        # Create the entry field with normal layout
        self.video_entry = ttk.Entry(video_frame, textvariable=self.video_path, width=40)
        self.video_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(video_frame, text="Browse", command=self.browse_video).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Split mode selection
        split_mode_frame = ttk.Frame(main_frame)
        split_mode_frame.grid(row=2, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        ttk.Label(split_mode_frame, text="Split mode:", font=("Arial", 12)).pack(side=tk.LEFT)
        
        ttk.Radiobutton(split_mode_frame, text="Equal parts", variable=self.split_mode, value="parts").pack(side=tk.LEFT, padx=(10, 5))
        ttk.Radiobutton(split_mode_frame, text="By size", variable=self.split_mode, value="size").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(split_mode_frame, text="By duration", variable=self.split_mode, value="duration").pack(side=tk.LEFT, padx=5)
        
        # Parameters frame (changes based on split mode)
        self.params_frame = ttk.LabelFrame(main_frame, text="Split Parameters")
        self.params_frame.grid(row=3, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        # Initial parameters (parts mode)
        self.show_parts_params()
        
        # Bind the change of split mode
        self.split_mode.trace("w", lambda *args: self.update_params_frame())
        
        # Process button
        process_frame = ttk.Frame(main_frame)
        process_frame.grid(row=4, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(0, 15))
        
        self.process_button = ttk.Button(process_frame, text="Cut Video", command=self.start_cutting)
        self.process_button.pack(fill=tk.X)
        
        # Progress bar, timer and status
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=2, sticky=tk.W+tk.E)
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=100, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(0, 5))
        
        timer_frame = ttk.Frame(progress_frame)
        timer_frame.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(timer_frame, text="Elapsed time:", font=("Arial", 10)).pack(side=tk.LEFT)
        ttk.Label(timer_frame, textvariable=self.elapsed_time, font=("Arial", 10)).pack(side=tk.LEFT, padx=(5, 0))
        
        # Status label
        self.status_label = ttk.Label(progress_frame, textvariable=self.status, font=("Arial", 10))
        self.status_label.pack(fill=tk.X)
    
    def update_params_frame(self):
        """Update the parameters frame based on selected split mode"""
        # Clear existing widgets
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        # Show relevant parameters based on selected mode
        mode = self.split_mode.get()
        if mode == "parts":
            self.show_parts_params()
        elif mode == "size":
            self.show_size_params()
        elif mode == "duration":
            self.show_duration_params()
    
    def show_parts_params(self):
        """Show parameters for splitting into equal parts"""
        parts_frame = ttk.Frame(self.params_frame)
        parts_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(parts_frame, text="Number of parts:").pack(side=tk.LEFT)
        parts_spinner = ttk.Spinbox(parts_frame, from_=2, to=100, width=5, textvariable=self.num_parts)
        parts_spinner.pack(side=tk.LEFT, padx=(5, 0))
    
    def show_size_params(self):
        """Show parameters for splitting by size"""
        size_frame = ttk.Frame(self.params_frame)
        size_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(size_frame, text="Target size per part (MB):").pack(side=tk.LEFT)
        size_spinner = ttk.Spinbox(size_frame, from_=1, to=9999, width=7, textvariable=self.target_size)
        size_spinner.pack(side=tk.LEFT, padx=(5, 0))
    
    def show_duration_params(self):
        """Show parameters for splitting by duration"""
        duration_frame = ttk.Frame(self.params_frame)
        duration_frame.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(duration_frame, text="Target duration per part (minutes):").pack(side=tk.LEFT)
        duration_spinner = ttk.Spinbox(duration_frame, from_=0.1, to=999.9, increment=0.1, width=7, textvariable=self.target_duration)
        duration_spinner.pack(side=tk.LEFT, padx=(5, 0))
        
    def setup_drag_drop(self):
        """Configure drag and drop functionality for video files"""
        # Make root accept file drops
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # Also make the entry widget and main window accept drops
        self.video_entry.drop_target_register(DND_FILES)
        self.video_entry.dnd_bind('<<Drop>>', self.on_drop)
        
    def truncate_path(self, path, max_length=40):
        """Truncate a long path for display"""
        if len(path) <= max_length:
            return path
        
        # Get filename and keep it intact
        filename = os.path.basename(path)
        # Get directory part
        directory = os.path.dirname(path)
        
        if len(filename) >= max_length - 5:  # If filename alone is too long
            # Truncate filename but keep extension
            name, ext = os.path.splitext(filename)
            avail_chars = max_length - 5 - len(ext)  # Account for "..." and extension
            return name[:avail_chars] + "..." + ext
        else:
            # Truncate directory part
            avail_chars = max_length - len(filename) - 5  # Account for "..." and filename
            return directory[:avail_chars] + "..." + os.sep + filename
    
    def on_drop(self, event):
        """Handle file drop event"""
        file_path = event.data
        
        # Clean the path (remove {} and quotation marks if present)
        if file_path.startswith('{') and file_path.endswith('}'): 
            file_path = file_path[1:-1]
        file_path = file_path.strip('"')
        
        # Check if it's a video file
        valid_extensions = (".mp4", ".avi", ".mov", ".mkv", ".wmv")
        if file_path.lower().endswith(valid_extensions):
            # Store the full path but display truncated version
            self.full_video_path = file_path
            self.video_path.set(self.truncate_path(file_path))
            
            # Copy full path to clipboard for convenience
            self.root.clipboard_clear()
            self.root.clipboard_append(file_path)
            
            # Show just the filename (truncated if needed) in the status bar
            filename = os.path.basename(file_path)
            # Truncate filename if it's too long (max 30 chars)
            if len(filename) > 30:
                name, ext = os.path.splitext(filename)
                filename = name[:26] + "..." + ext
            self.status.set(f"Video dropped: {filename}")
        else:
            messagebox.showerror("Error", "The dropped file is not a supported video format.")
    
    def browse_video(self):
        """Open file dialog to select video"""
        filetypes = [
            ("Video files", "*.mp4 *.avi *.mov *.mkv *.wmv"),
            ("All files", "*.*")
        ]
        file_path = filedialog.askopenfilename(
            title="Select a video file",
            filetypes=filetypes
        )
        if file_path:
            # Store the full path but display truncated version
            self.full_video_path = file_path
            self.video_path.set(self.truncate_path(file_path))
            
            # Copy full path to clipboard for convenience if it was truncated
            if len(file_path) > 40:
                self.root.clipboard_clear()
                self.root.clipboard_append(file_path)
            
            # Show the filename (truncated if needed) in status
            filename = os.path.basename(file_path)
            # Truncate filename if it's too long (max 30 chars)
            if len(filename) > 30:
                name, ext = os.path.splitext(filename)
                filename = name[:26] + "..." + ext
            self.status.set(f"Video selected: {filename}")
    
    def start_timer(self):
        """Start the elapsed time timer"""
        self.start_time = time.time()
        self.timer_running = True
        self.update_timer()
    
    def update_timer(self):
        """Update the elapsed time display"""
        if not self.timer_running:
            return
            
        elapsed = time.time() - self.start_time
        formatted_time = str(timedelta(seconds=int(elapsed)))
        self.elapsed_time.set(formatted_time)
        
        # Schedule next update
        self.timer_id = self.root.after(1000, self.update_timer)
    
    def stop_timer(self):
        """Stop the elapsed time timer"""
        if self.timer_id:
            self.root.after_cancel(self.timer_id)
        self.timer_running = False
    
    def start_cutting(self):
        """Start the video cutting process"""
        # Use the full path stored during selection/drop instead of potentially truncated path
        video_path = getattr(self, 'full_video_path', self.video_path.get())
        mode = self.split_mode.get()
        
        if not video_path:
            messagebox.showerror("Error", "Please select a video file")
            return
        
        if mode == "parts":
            num_parts = self.num_parts.get()
            if num_parts < 2:
                messagebox.showerror("Error", "Number of parts must be at least 2")
                return
        elif mode == "size":
            target_size = self.target_size.get()
            if target_size <= 0:
                messagebox.showerror("Error", "Target size must be greater than 0 MB")
                return
        elif mode == "duration":
            target_duration = self.target_duration.get()
            if target_duration <= 0:
                messagebox.showerror("Error", "Target duration must be greater than 0 minutes")
                return
        
        # Disable UI while processing
        self.is_processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        self.elapsed_time.set("00:00:00")
        self.start_timer()
        self.status.set("Processing... Getting video information")
        
        # Start processing in a separate thread
        mode = self.split_mode.get()
        if mode == "parts":
            thread = threading.Thread(target=self.process_video_parts, args=(video_path, self.num_parts.get()))
        elif mode == "size":
            thread = threading.Thread(target=self.process_video_size, args=(video_path, self.target_size.get()))
        elif mode == "duration":
            thread = threading.Thread(target=self.process_video_duration, args=(video_path, self.target_duration.get()))
            
        thread.daemon = True
        thread.start()
    
    def process_video_parts(self, video_path, num_parts):
        """Process the video by splitting into equal parts"""
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
            self.status.set("Processing... Cutting video into equal parts")
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
    
    def process_video_size(self, video_path, target_size_mb):
        """Process the video by splitting into parts of specified size"""
        try:
            # Get video size and duration
            self.status.set("Processing... Analyzing video properties")
            duration = get_video_duration(video_path, self.app_dir)
            total_size = get_video_size(video_path)
            
            if duration <= 0:
                self.root.after(0, lambda: self.show_error("Could not determine video duration"))
                return
            
            if total_size <= 0:
                self.root.after(0, lambda: self.show_error("Could not determine video size"))
                return
            
            # Create output directory
            video_name = os.path.splitext(os.path.basename(video_path))[0]
            output_dir = os.path.join(os.path.dirname(video_path), f"{video_name}_parts")
            os.makedirs(output_dir, exist_ok=True)
            
            # Cut video by size
            self.status.set(f"Processing... Cutting video into {target_size_mb}MB parts")
            success = cut_video_by_size(
                video_path, 
                output_dir, 
                target_size_mb, 
                duration,
                total_size,
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
    
    def process_video_duration(self, video_path, target_duration_min):
        """Process the video by splitting into parts of specified duration"""
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
            
            # Cut video by duration
            target_duration_sec = target_duration_min * 60  # Convert minutes to seconds
            self.status.set(f"Processing... Cutting video into {target_duration_min}min parts")
            success = cut_video_by_duration(
                video_path, 
                output_dir, 
                target_duration_sec, 
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
        # Show full path in the dialog box
        messagebox.showinfo("Success", f"Video successfully cut into parts!\nOutput directory: {output_dir}")
        
        # Truncate path for status bar
        if len(output_dir) > 40:
            # Try to keep the folder name visible
            folder_name = os.path.basename(output_dir)
            parent_dir = os.path.dirname(output_dir)
            
            if len(folder_name) > 20:  # If folder name itself is too long
                truncated_path = folder_name[:17] + "..."
            else:
                # Show drive letter + ... + folder name
                drive = os.path.splitdrive(output_dir)[0] + os.sep
                truncated_path = drive + "..." + os.sep + folder_name
        else:
            truncated_path = output_dir
            
        self.status.set(f"Done. Files saved to {truncated_path}")
    
    def show_error(self, message):
        """Show error message"""
        messagebox.showerror("Error", message)
        self.status.set("Error occurred. Please try again.")
    
    def reset_ui(self):
        """Reset UI after processing"""
        self.is_processing = False
        self.process_button.config(state=tk.NORMAL)
        self.progress_bar.stop()
        self.stop_timer()

def main():
    # Use TkinterDnD.Tk instead of tk.Tk for drag-and-drop support
    root = TkinterDnD.Tk()
    root.title("Cut It Now - Video Cutter")
    app = VideoCutterApp(root)
    
    # Update idletasks to calculate widget sizes
    root.update_idletasks()
    
    # Get window size based on content
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    
    # Add some padding
    width = min(width + 20, 500)  # Max width of 500 pixels
    height = min(height + 20, 400)  # Max height of 400 pixels
    
    # Center the window on screen
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    
    # Set window size and position
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Disable resizing if window is already optimal size
    root.resizable(True, True)
    
    root.mainloop()

if __name__ == "__main__":
    main()
