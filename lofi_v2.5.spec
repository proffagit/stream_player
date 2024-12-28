# -*- mode: python ; coding: utf-8 -*-

import os
vlc_path = r"C:\Program Files\VideoLAN\VLC"

a = Analysis(
    ['lofi_v2.5.py'],
    pathex=[],
    binaries=[
        # Include VLC plugins and DLLs
        (os.path.join(vlc_path, '*.dll'), '.'),
        (os.path.join(vlc_path, 'plugins'), 'plugins'),
    ],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=None)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='lofi_v2.5',
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
)
