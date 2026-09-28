"""
Desk-robot face generator v2 — now with pupils.
Cyan-on-black glow style, 320x240. Tweak PARAMS to taste.
Pupils are dark dots drawn on top of each eye, with a highlight sparkle.
Glances move the PUPIL, not the whole eye, so the gaze darts naturally.
"""
from PIL import Image, ImageDraw, ImageChops, ImageFilter

W, H = 320, 240
CYAN = (39, 233, 251)
DARK = (6, 40, 44)
PUPIL = (4, 26, 30)          # near-black teal, reads as a hole in the eye
HILITE = (200, 255, 255)     # tiny sparkle
BG = (0, 0, 0)
GLOW_RADIUS = 7
LX, RX = 100, 220            # eye centres (x)

def eye_tile(w, h, r, rot=0, shape="rrect", carve=None):
    pad = 40
    tile = Image.new("RGBA", (w + pad, h + pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    box = [pad//2, pad//2, pad//2 + w, pad//2 + h]
    if shape == "rrect":
        d.rounded_rectangle(box, radius=r, fill=CYAN + (255,))
    elif shape == "ellipse":
        d.ellipse(box, fill=CYAN + (255,))
    if carve:
        side, frac = carve
        x0, y0, x1, y1 = box
        if side == "bottom":
            d.rectangle([x0-2, y1 - int((y1-y0)*frac), x1+2, y1+2], fill=(0,0,0,0))
        elif side == "top":
            d.rectangle([x0-2, y0-2, x1+2, y0 + int((y1-y0)*frac)], fill=(0,0,0,0))
    if rot:
        tile = tile.rotate(rot, expand=True, resample=Image.BICUBIC)
    return tile

def paste_eye(ink, tile, cx, cy):
    ink.paste(tile, (cx - tile.width//2, cy - tile.height//2), tile)

def mouth(ink, style, cx=160, cy=200):
    d = ImageDraw.Draw(ink)
    if style == "none": return
    if style == "smile":  d.arc([cx-34, cy-30, cx+34, cy+18], 20, 160, fill=CYAN, width=8)
    elif style == "frown": d.arc([cx-30, cy+2, cx+30, cy+46], 200, 340, fill=CYAN, width=8)
    elif style == "flat":  d.rounded_rectangle([cx-26, cy-4, cx+26, cy+4], 4, fill=CYAN)
    elif style == "o":
        d.ellipse([cx-16, cy-16, cx+16, cy+16], fill=CYAN); d.ellipse([cx-8, cy-8, cx+8, cy+8], fill=DARK)
    elif style == "talk_open":
        d.rounded_rectangle([cx-30, cy-17, cx+30, cy+17], 16, fill=CYAN); d.rounded_rectangle([cx-21, cy-8, cx+21, cy+8], 9, fill=DARK)
    elif style == "talk_closed":
        d.rounded_rectangle([cx-26, cy-4, cx+26, cy+4], 4, fill=CYAN)

def draw_pupil(d, cx, cy, r=11, dx=0, dy=0):
    px, py = cx+dx, cy+dy
    d.ellipse([px-r, py-r, px+r, py+r], fill=PUPIL)
    hr = max(2, r//3)                                  # sparkle, upper-left
    d.ellipse([px-r//2-hr, py-r//2-hr, px-r//2+hr, py-r//2+hr], fill=HILITE)

def render(spec):
    ink = Image.new("RGB", (W, H), BG)
    ey = spec.get("ey", 95)
    lspec = dict(spec["left"]); rspec = dict(spec["right"])
    ldy = lspec.pop("dy", 0); rdy = rspec.pop("dy", 0)
    paste_eye(ink, eye_tile(**lspec), LX, ey + ldy)
    paste_eye(ink, eye_tile(**rspec), RX, ey + rdy)
    mouth(ink, spec.get("mouth", "none"))
    glow = ink.filter(ImageFilter.GaussianBlur(GLOW_RADIUS))
    out = ImageChops.lighter(ImageChops.add(ink, glow), ink)
    # pupils on top (crisp, no glow)
    p = spec.get("pupil")
    if p:
        d = ImageDraw.Draw(out)
        # eye visual centre ~ paste centre + a little down into the slab
        ecy = ey
        draw_pupil(d, LX, ecy + ldy + p.get("cy",0), p.get("r",11), p.get("dx",0), p.get("dy",0))
        draw_pupil(d, RX, ecy + rdy + p.get("cy",0), p.get("r",11), p.get("dx",0), p.get("dy",0))
    return out

EYE = dict(w=90, h=110, r=26, shape="rrect")
def eyes(**over):
    l = dict(EYE); r = dict(EYE); l.update(over.get("l", {})); r.update(over.get("r", {})); return l, r

C = lambda **k: dict(k)   # pupil shorthand
PARAMS = {}
l,r=eyes();                       PARAMS["neutral"]      = {"left":l,"right":r,"pupil":C()}
l,r=eyes(l={"h":60},r={"h":60});  PARAMS["blink_half"]   = {"left":l,"right":r,"ey":120,"pupil":C(r=8)}
l,r=eyes(l={"h":16,"r":8},r={"h":16,"r":8}); PARAMS["blink_closed"]={"left":l,"right":r,"ey":140}
l,r=eyes(l={"carve":("bottom",0.45)},r={"carve":("bottom",0.45)}); PARAMS["happy"]={"left":l,"right":r,"mouth":"smile","pupil":C(cy=-16,r=9)}
l,r=eyes(l={"rot":-12,"dy":6},r={"rot":12,"dy":6}); PARAMS["sad"]={"left":l,"right":r,"mouth":"frown","pupil":C(dy=10,dx=-4)}
l,r=eyes(l={"rot":16},r={"rot":-16}); PARAMS["angry"]={"left":l,"right":r,"mouth":"flat","pupil":C(dy=16,r=11)}
l,r=eyes(l={"carve":("top",0.55)},r={"carve":("top",0.55)}); PARAMS["sleepy"]={"left":l,"right":r,"ey":110,"pupil":C(cy=30,r=8)}
l,r=eyes(l={"w":100,"h":100,"shape":"ellipse"},r={"w":100,"h":100,"shape":"ellipse"}); PARAMS["surprised"]={"left":l,"right":r,"mouth":"o","pupil":C(r=15)}
l,r=eyes(l={"h":118},r={"h":96}); PARAMS["curious"]={"left":l,"right":r,"pupil":C(dx=8,dy=-6,r=11)}
l,r=eyes();                       PARAMS["talk_closed"]  = {"left":l,"right":r,"mouth":"talk_closed","pupil":C()}
l,r=eyes();                       PARAMS["talk_open"]    = {"left":l,"right":r,"mouth":"talk_open","pupil":C()}
l,r=eyes();                       PARAMS["look_left"]    = {"left":l,"right":r,"pupil":C(dx=-26,r=11)}
l,r=eyes();                       PARAMS["look_right"]   = {"left":l,"right":r,"pupil":C(dx=26,r=11)}

import os
os.makedirs("/mnt/user-data/outputs/faces", exist_ok=True)
names=[]
for name, spec in PARAMS.items():
    render(spec).save(f"/mnt/user-data/outputs/faces/eyes_{name}.png"); names.append(name)

cols=4; rows=(len(names)+cols-1)//cols
sheet=Image.new("RGB",(cols*160,rows*130),(20,20,20)); d=ImageDraw.Draw(sheet)
for i,name in enumerate(names):
    t=Image.open(f"/mnt/user-data/outputs/faces/eyes_{name}.png").resize((150,112))
    x=(i%cols)*160+5; y=(i//cols)*130+5; sheet.paste(t,(x,y)); d.text((x+4,y+114),name,fill=(200,200,200))
sheet.save("/mnt/user-data/outputs/faces/_contact_sheet.png")
print("regenerated", len(names), "faces with pupils")
