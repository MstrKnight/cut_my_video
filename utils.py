#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utility functions for video processing with FFmpeg
"""

import os
import subprocess
import re
import math

def get_ffmpeg_path(app_dir):
    """Get the path to the FFmpeg executable"""
    # Check if we're using bundled FFmpeg
    ffmpeg_path = os.path.join(app_dir, "assets", "ffmpeg.exe")
    if os.path.exists(ffmpeg_path):
        return ffmpeg_path
    
    # Fallback: Try to use system FFmpeg if available
    try:
        subprocess.run(["ffmpeg", "-version"], 
                       stdout=subprocess.PIPE, 
                       stderr=subprocess.PIPE,
                       check=True)
        return "ffmpeg"
    except (subprocess.SubprocessError, FileNotFoundError):
        raise FileNotFoundError("FFmpeg not found. Please ensure FFmpeg is installed or included in the assets folder.")

def get_video_duration(video_path, app_dir):
    """
    Get the duration of a video file in seconds
    
    Args:
        video_path (str): Path to the video file
        app_dir (str): Application directory
        
    Returns:
        float: Duration in seconds
    """
    ffmpeg_path = get_ffmpeg_path(app_dir)
    
    try:
        # Run FFmpeg to get video information
        result = subprocess.run(
            [ffmpeg_path, "-i", video_path], 
            capture_output=True, 
            text=True
        )
        
        # FFmpeg outputs info to stderr
        output = result.stderr
        
        # Extract duration using regex
        duration_match = re.search(r"Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})", output)
        if duration_match:
            hours = int(duration_match.group(1))
            minutes = int(duration_match.group(2))
            seconds = int(duration_match.group(3))
            centiseconds = int(duration_match.group(4))
            
            total_seconds = hours * 3600 + minutes * 60 + seconds + centiseconds / 100
            return total_seconds
        
        return 0
    except subprocess.SubprocessError as e:
        print(f"Error getting video duration: {str(e)}")
        return 0

def format_time(seconds):
    """
    Format time in seconds to HH:MM:SS.ms format
    
    Args:
        seconds (float): Time in seconds
        
    Returns:
        str: Formatted time string
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"

def cut_video_into_parts(video_path, output_dir, num_parts, duration, app_dir, status_callback=None):
    """
    Cut a video into equal parts
    
    Args:
        video_path (str): Path to the video file
        output_dir (str): Directory to save the output files
        num_parts (int): Number of parts to create
        duration (float): Duration of the video in seconds
        app_dir (str): Application directory
        status_callback (function): Callback function for status updates
        
    Returns:
        bool: Success status
    """
    ffmpeg_path = get_ffmpeg_path(app_dir)
    
    try:
        # Calculate segment duration
        segment_duration = duration / num_parts
        
        # Get file extension
        _, ext = os.path.splitext(video_path)
        if not ext:
            ext = ".mp4"  # Default extension
        
        # Create parts
        for i in range(num_parts):
            if status_callback:
                status_callback(f"Processing part {i+1} of {num_parts}...")
                
            start_time = i * segment_duration
            
            # For the last segment, use the full duration to avoid rounding issues
            if i == num_parts - 1:
                cmd = [
                    ffmpeg_path,
                    "-y",  # Overwrite output files
                    "-i", video_path,
                    "-ss", format_time(start_time),
                    "-c", "copy",  # Copy streams without re-encoding
                    os.path.join(output_dir, f"part_{i+1:03d}{ext}")
                ]
            else:
                cmd = [
                    ffmpeg_path,
                    "-y",  # Overwrite output files
                    "-i", video_path,
                    "-ss", format_time(start_time),
                    "-t", format_time(segment_duration),
                    "-c", "copy",  # Copy streams without re-encoding
                    os.path.join(output_dir, f"part_{i+1:03d}{ext}")
                ]
            
            # Run FFmpeg command
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if process.returncode != 0:
                print(f"Error cutting part {i+1}: {process.stderr}")
                if status_callback:
                    status_callback(f"Error processing part {i+1}")
                return False
        
        return True
    except Exception as e:
        print(f"Error cutting video: {str(e)}")
        return False
