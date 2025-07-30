# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

import os
import sys
import site
import tkinterdnd2

# Find TkinterDnD2 directory
tkinterdnd2_path = os.path.dirname(tkinterdnd2.__file__)
tkdnd_path = os.path.join(tkinterdnd2_path, 'tkdnd')

# Get all necessary TkinterDnD2 files
tkdnd_files = []

# Add platform-specific DLL and TCL files
for platform_dir in ['win-x64', 'win-x86', 'win-arm64']:  # Include all Windows platforms
    platform_path = os.path.join(tkdnd_path, platform_dir)
    if os.path.exists(platform_path):
        for file in os.listdir(platform_path):
            src = os.path.join(platform_path, file)
            if os.path.isfile(src):
                # Keep the original directory structure
                dst = os.path.join('tkinterdnd2', 'tkdnd', platform_dir)
                tkdnd_files.append((src, dst))

# Add tkdnd Python files
tkdnd_files.append((os.path.join(tkinterdnd2_path, 'TkinterDnD.py'),
                  os.path.join('tkinterdnd2')))
tkdnd_files.append((os.path.join(tkinterdnd2_path, '__init__.py'),
                  os.path.join('tkinterdnd2')))

a = Analysis(['main.py'],
             pathex=[],
             binaries=[],
             datas=[('assets/ffmpeg.exe', 'assets')] + tkdnd_files,  # Include FFmpeg and TkinterDnD2 files
             hiddenimports=['tkinterdnd2'],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          [],
          name='cut_it_now',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None,
          icon=None)  # You can add an icon file here if you have one
