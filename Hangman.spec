# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['Hangman.py'],
    pathex=[],
    binaries=[],
    datas=[('hangman0.png', '.'), ('hangman1.png', '.'), ('hangman2.png', '.'), ('hangman3.png', '.'), ('hangman4.png', '.'), ('hangman5.png', '.'), ('hangman6.png', '.')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='Hangman',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
