import os, shutil, zipfile
from datetime import datetime
from .utils import ensure_dir, log
class BackupManager:
    def __init__(self, src, root):
        self.src = src; self.root = ensure_dir(root)
    def _ts(self): return datetime.now().strftime("%Y%m%d-%H%M%S")
    def mirror(self):
        t = os.path.join(self.root, "mirror-"+self._ts())
        shutil.copytree(self.src, t); log("Mirror: "+t); return t
    def zip(self):
        t = os.path.join(self.root, "snapshot-"+self._ts()+".zip")
        with zipfile.ZipFile(t,"w",zipfile.ZIP_DEFLATED) as z:
            for r,_,fs in os.walk(self.src):
                for f in fs:
                    full = os.path.join(r,f)
                    z.write(full, os.path.relpath(full, self.src))
        log("ZIP: "+t); return t
    def run(self): return {"mirror": self.mirror(), "zip": self.zip()}
