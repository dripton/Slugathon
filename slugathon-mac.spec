# -*- mode: python -*-
a = Analysis(['bin/slugathon'],
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
          name=os.path.join('dist', 'slugathon.mac'),
          debug=False,
          strip=False,
          upx=False,
          console=True )
app = BUNDLE(exe,
          name=os.path.join('dist', 'slugathon.app'),
          version='0.1')
