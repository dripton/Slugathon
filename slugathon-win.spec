# -*- mode: python -*-
a = Analysis([os.path.join(HOMEPATH,'support/_mountzlib.py'), os.path.join(HOMEPATH,'support/useUnicode.py'), 'bin/slugathon'],
             pathex=['bin'])
pyz = PYZ(a.pure)
images = Tree("slugathon/images", prefix="images")
docs = Tree("slugathon/docs", prefix="docs")
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
