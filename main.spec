# -*- mode: python ; coding: utf-8 -*-
import os.path

block_cipher = None

a = Analysis(
    ['src\\main.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Exclude Binaries
binaries = []
binaries_exclude = {
    'opengl32sw.dll',
    'Qt6OpenGL.dll',
    'Qt6Qml.dll',
    'Qt6QmlModels.dll',
    'Qt6Quick.dll',
    'Qt6Svg.dll',
    'Qt6VirtualKeyboard.dll',
    'MSVCP140.dll',
    'MSVCP140_1.dll',
    'MSVCP140_2.dll',
    'libcrypto-1_1.dll',
    'VCRUNTIME140.dll',
    'VCRUNTIME140_1.dll',
    'qsvgicon.dll',
    'qgif.dll',
    'qicns.dll',
    'qjpeg.dll',
    'qsvg.dll',
    'qtga.dll',
    'qtvirtualkeyboardplugin.dll',
    'qdirect2d.dll',
    'qoffscreen.dll',
    'qminimal.dll',
    'qwebp.dll',
    'qtiff.dll',
    'qwbmp.dll',
    'qnetworklistmanager.dll',
    'qcertonlybackend.dll',
    'qopensslbackend.dll',
    'qschannelbackend.dll',
    'QtNetwork.pyd',
    '_webp.cp310-win_amd64.pyd',
    '_bz2.pyd',
    '_decimal.pyd',
    '_hashlib.pyd',
    '_lzma.pyd',
    'unicodedata.pyd',
}

for (dest, source, kind) in a.binaries:
    if os.path.split(source)[1] in binaries_exclude:
        continue
    binaries.append((dest, source, kind))

a.binaries = binaries

# Exclude Datas
datas = []

for (dest, source, kind) in a.datas:
    if os.path.split(source)[1].startswith('qtbase_'):
        continue
    if os.path.splitext(source)[1] == '.qm':
        continue
    datas.append((dest, source, kind))

a.datas = datas
print(a.datas)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TagPDF',
    icon='res/icon.ico',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    version='version.txt',
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TagPDF',
)
