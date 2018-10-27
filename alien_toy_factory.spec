# -*- mode: python -*-

block_cipher = None


a = Analysis(['alien_toy_factory.spec'],
             pathex=['C:\\Users\\Anthony\\mu_code'],
             binaries=[],
             datas=[
                ('data', 'data'),
                ('images', 'images'),
                ('pgzero', 'pgzero'),
                ('fonts', 'fonts'),
                ('sounds', 'sounds'),
                ('conveyors.py', '.'),
                ('data.py', '.'),
                ('items.py', '.'),
                ('machines.py', '.'),
                ('player.py', '.'),
                ('training.py', '.'),
                ('pyweek.py', '.'),
             ],
             hiddenimports=['pygame', 'asyncio', 'pygame.locals', 'timeit'],
             hookspath=[],
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
          name='alien_toy_factory',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          runtime_tmpdir=None,
          console=True )
