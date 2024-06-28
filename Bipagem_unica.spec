# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['C:\\Users\\dudur\\Documents\\LC-transporte\\Bipagem_unica.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\dudur\\Documents\\LC-transporte\\service-account-credentials.json', '.')],
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
    name='Bipagem_unica',
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
    icon=['C:\\Users\\dudur\\Documents\\LC-transporte\\Pacotes.ico'],
    onefile=True
)
