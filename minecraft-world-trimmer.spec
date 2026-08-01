# -*- mode: python ; coding: utf-8 -*-
#type:ignore

import os
import shutil
import anvil

shutil.rmtree("dist")

anvil_path = os.path.dirname(anvil.__file__)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[(anvil_path,"anvil")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

b = Analysis(
    ['ui.py'],
    pathex=[],
    binaries=[],
    datas=[(anvil_path,"anvil")],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

MERGE((a,"main","minecraft-world-trimmer"),(b,"ui","minecraft-world-trimmer-ui"))

pyz_a = PYZ(a.pure)
pyz_b = PYZ(b.pure)

exe_a = EXE(
    pyz_a,
    a.scripts,
    [],
    exclude_binaries=True,
    name='minecraft-world-trimmer',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icon.ico'],
    version="vf.txt"
)

exe_b = EXE(
    pyz_b,
    b.scripts,
    [],
    exclude_binaries=True,
    name='minecraft-world-trimmer-ui',
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
    icon=['icon.ico'],
    version="vf.txt"
)

coll = COLLECT(
    exe_a,
    a.binaries,
    a.datas,
    exe_b,
    b.binaries,
    b.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='minecraft-world-trimmer',
)
