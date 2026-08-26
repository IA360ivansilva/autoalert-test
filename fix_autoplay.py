#!/usr/bin/env python3
"""Fix autoplay: try on load, and ALWAYS play on first user tap/click anywhere (mobile-safe)."""
SCRIPT = """<script>
(function(){
  var a=document.getElementById('au');
  if(!a) return;
  function tryPlay(){ var p=a.play(); if(p&&p.catch){ p.catch(function(){}); } }
  window.addEventListener('load', tryPlay);
  // mobile fallback: first tap anywhere starts the message
  function onFirst(){ tryPlay(); document.removeEventListener('touchstart',onFirst); document.removeEventListener('click',onFirst); }
  document.addEventListener('touchstart', onFirst, {once:true, passive:true});
  document.addEventListener('click', onFirst, {once:true});
})();
</script>"""

import glob
files = glob.glob("top50/*.html") + glob.glob("top200/*.html")
n=0
for f in files:
    h=open(f,encoding="utf-8").read()
    # replace existing trailing script before </body>
    if "<script>window.addEventListener(\"load\"" in h:
        import re
        h=re.sub(r"<script>window\.addEventListener\(\"load\",function\(\)\{[^<]*</script>", SCRIPT, h)
    elif SCRIPT not in h:
        h=h.replace("</body>", SCRIPT+"\n</body>")
    open(f,"w",encoding="utf-8").write(h)
    n+=1
print(f"patched autoplay in {n} files")
