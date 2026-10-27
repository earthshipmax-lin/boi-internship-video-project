from pathlib import Path
from urllib.request import urlretrieve
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor
root=Path(__file__).resolve().parents[1]/'public/fonts'
fonts=[('notoseriftc','NotoSerifTC[wght].ttf','NotoSerifTC.ttf'),('notosanstc','NotoSansTC[wght].ttf','NotoSansTC.ttf'),('sourceserif4','SourceSerif4[opsz,wght].ttf','SourceSerif4.ttf'),('geist','Geist[wght].ttf','Geist.ttf')]
def download(item):
 folder,name,out=item
 for remote,local in [(name,out),('OFL.txt',folder+'-OFL.txt')]:
  url='https://raw.githubusercontent.com/google/fonts/main/ofl/'+folder+'/'+quote(remote)
  urlretrieve(url,root/local)
 print(out,(root/out).stat().st_size,flush=True)
with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(download,fonts))
