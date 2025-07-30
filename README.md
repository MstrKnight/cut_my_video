# Cut It Now - Video Cutter

A simple Python application that lets you cut videos into equal parts with ease.

## Features

- **Simple Interface**: Select a video file and choose how many parts to split it into
- **Fast Processing**: Uses FFmpeg for efficient video cutting without re-encoding
- **Standalone Application**: Can be compiled to a standalone .exe with FFmpeg included

## Requirements

- Python 3.10 or higher
- Tkinter (included with most Python installations)
- FFmpeg (bundled with the application)

## Installation

### Running from source

1. Clone this repository:
   ```
   git clone https://github.com/your-username/cut_my_video.git
   cd cut_my_video
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Download FFmpeg and place the `ffmpeg.exe` in the `assets/` folder

4. Run the application:
   ```
   python main.py
   ```

### Using compiled executable

1. Download the latest release from the Releases page
2. Extract the ZIP file
3. Run `cut_it_now.exe`

## Usage

1. Click "Browse" to select a video file
2. Enter the number of equal parts you want to split the video into
3. Click "Cut Video"
4. Wait for the process to complete
5. Find the output files in a folder next to your original video

## Compilation to .exe

You can create a standalone executable using PyInstaller:

```
pyinstaller --onefile --add-binary "assets/ffmpeg.exe;assets" --name "cut_it_now" main.py
```

## License

This project is open source and available under the MIT License.

## Credits

This application uses FFmpeg (https://ffmpeg.org/) for video processing.
