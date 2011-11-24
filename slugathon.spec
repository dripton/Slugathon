# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support\\_mountzlib.py'), os.path.join(HOMEPATH,'support\\useUnicode.py'), 'bin\\slugathon'],
             pathex=['C:\\src\\Slugathon\\bin'])
pyz = PYZ(a.pure)
images = Tree("/src/Slugathon/slugathon/images", prefix="images")
docs = Tree("/src/Slugathon/slugathon/docs", prefix="docs")
exe = EXE( pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,
          images,
          docs,
          name=os.path.join('dist', 'slugathon.exe'),
          debug=False,
          strip=False,
          upx=True,
          console=True )
