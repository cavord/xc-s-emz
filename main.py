import requests, os, base64, sys
from pystyle import Colorate, Colors

def clear(): 
    os.system("cls" if os.name=="nt" else "clear")
    os.system(f'title ^| xc - s/emz ^| guns.lol/cavord ^|')

def banner():
    clear()
    width = os.get_terminal_size().columns
    for line in BANNER.split("\n"):
        line_centered = line.center(width)
        print(Colorate.Horizontal(Colors.rainbow, line_centered))
    
BANNER = r"""
██╗  ██╗ ██████╗        ███████╗    ██╗███████╗███╗   ███╗███████╗
╚██╗██╔╝██╔════╝        ██╔════╝   ██╔╝██╔════╝████╗ ████║╚══███╔╝
 ╚███╔╝ ██║      █████╗ ███████╗  ██╔╝ █████╗  ██╔████╔██║  ███╔╝ 
 ██╔██╗ ██║      ╚════╝ ╚════██║ ██╔╝  ██╔══╝  ██║╚██╔╝██║ ███╔╝  
██╔╝ ██╗╚██████╗        ███████║██╔╝   ███████╗██║ ╚═╝ ██║███████╗
╚═╝  ╚═╝ ╚═════╝        ╚══════╝╚═╝    ╚══════╝╚═╝     ╚═╝╚══════╝

guns.lol/cavord
"""

HEADERS = {"User-Agent": "Mozilla/5.0",}

def api_get(token, url):
    h = HEADERS.copy(); h["Authorization"] = token
    r = requests.get(url, headers=h)
    r.raise_for_status()
    return r.json()

def upload_emoji(token, gid, name, img, ani):
    t = "gif" if ani else "png"
    b = "data:image/{};base64,".format(t)+base64.b64encode(img).decode()
    h = HEADERS.copy(); h["Authorization"] = token; h["Content-Type"]="application/json"
    return requests.post(f"https://discord.com/api/v9/guilds/{gid}/emojis", headers=h, json={"name":name,"image":b})

def upload_sticker(token, gid, name, img_bytes, tags):
    h = HEADERS.copy(); h["Authorization"] = token
    data = {"name": name, "description": "Imported", "tags": tags or ""}
    files = {"file": (f"{name}.png", img_bytes, "image/png")}
    return requests.post(f"https://discord.com/api/v9/guilds/{gid}/stickers", headers=h, data=data, files=files)

def pick(sel, total):
    out=set()
    for p in (x.strip() for x in sel.split(",") if x.strip()):
        if "-" in p:
            try:
                a,b = map(int, p.split("-",1))
                out.update(range(a, b+1))
            except: pass
        else:
            if p.isdigit(): out.add(int(p))
    return sorted(i for i in out if 1<=i<=total)

def emoji_menu(token, src, tgt):
    clear(); banner()
    try: em = sorted(api_get(token,f"https://discord.com/api/v9/guilds/{src}/emojis"), key=lambda x:x["animated"])
    except Exception as e:
        print(Colors.orange, f" Failed to fetch emojis: ", e); input(); return
    if not em: print(" No emojis."); input(); return
    for i,e in enumerate(em,1): print(f"{i}. {e['name']} ({'Animated' if e['animated'] else 'Static'})")
    sel = pick(input("\nSelect: "), len(em))
    clear(); banner()
    if not sel: print(" No selection."); input(); return
    for i in sel:
        e = em[i-1]
        try:
            img = requests.get(f"https://cdn.discordapp.com/emojis/{e['id']}.{'gif' if e['animated'] else 'png'}", headers=HEADERS).content
            r = upload_emoji(token, tgt, e["name"], img, e["animated"])
            if r.status_code==201: print(Colors.green, f"Copied:", e["name"])
            else: print(Colors.red, f" Failed: {e['name']}")
        except Exception as ex:
            print(Colors.yellow, f" Error for", e["name"], ex)

def sticker_menu(token, src, tgt):
    clear(); banner()
    try: st = api_get(token, f"https://discord.com/api/v9/guilds/{src}/stickers")
    except Exception as e:
        print(Colors.orange, f" Failed to fetch stickers: ", e); input(); return
    if not st: print(" No stickers."); input(); return
    for i,s in enumerate(st,1):
        ftype = s.get("format_type", -1)
        tstr = "Lottie" if ftype==3 else "PNG"
        print(f"{i}. {s.get('name','<no name>')} ({tstr})")
    sel = pick(input("\nSelect: "), len(st))
    clear(); banner()
    if not sel: print(" No selection."); input(); return
    for i in sel:
        s = st[i-1]
        try:
            img = requests.get(f"https://cdn.discordapp.com/stickers/{s['id']}.png", headers=HEADERS).content
            tags = s.get("tags","")
            r = upload_sticker(token, tgt, s.get("name","sticker"), img, tags)
            if r.status_code==201: print(Colors.green ,f"Copied:", s.get("name"))
            else: print(Colors.red ,f" Failed: {s.get('name')}")
        except Exception as ex:
            print(Colors.yellow ,f" Error for", s.get("name"), ex)

def main():
    clear(); banner()
    token = input(Colors.gray + " user-t0ken: ").strip()
    src = input(Colors.gray + " src-guild-ID: ").strip()
    tgt = input(Colors.gray + " tgt-guild-ID: ").strip()
    clear(); banner()
    while True:
        c=input(Colors.gray + "emoji or sticker :~choice : ").strip()
        if c=="emoji": emoji_menu(token, src, tgt)
        elif c=="sticker": sticker_menu(token, src, tgt)
        clear(); banner()

if __name__=="__main__":
    main()
