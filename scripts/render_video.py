#!/usr/bin/env python3
"""Illustrated 2D story-cartoon renderer: layered sets, expressive characters and directed shots."""
from __future__ import annotations
import argparse, json, math, subprocess, sys, wave, random, shutil
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from textwrap import wrap

W, H, FPS = 1920, 1080, 30
SW, SH = 960, 540
MAX_SECONDS = 90
PALETTES = {
 "historical": ((207,205,190),(238,224,194),(80,73,64),(48,47,46)),
 "classroom": ((206,204,184),(235,222,190),(111,89,67),(44,43,39)),
 "home": ((88,83,76),(151,120,89),(111,84,61),(40,35,31)),
 "village": ((177,199,202),(229,211,177),(183,163,125),(58,52,43)),
 "crime": ((34,39,48),(62,66,73),(178,164,139),(24,25,29)),
 "investigation": ((49,57,66),(83,89,91),(206,190,155),(25,29,32)),
 "prison": ((82,88,82),(117,117,103),(194,181,150),(32,36,34)),
 "desert": ((222,185,126),(244,218,166),(112,84,55),(54,54,44)),
 "shipwreck": ((56,91,112),(103,143,153),(211,192,154),(31,48,57)),
 "wilderness": ((91,119,91),(154,158,112),(83,70,53),(35,49,39)),
 "war": ((111,105,91),(165,151,125),(78,73,62),(37,39,38)),
 "disaster": ((103,91,83),(155,130,109),(75,65,58),(35,34,33)),
 "survival": ((104,119,105),(163,157,123),(81,73,58),(37,43,37)),
 "night": ((28,36,52),(59,68,86),(173,157,129),(18,21,30)),
 "clock": ((47,52,61),(89,91,91),(195,177,139),(26,28,33)),
 "conversation": ((213,212,194),(240,227,199),(100,82,64),(48,45,40)),
 "journey": ((173,190,171),(224,216,183),(102,83,62),(47,49,42)),
 "science": ((35,49,68),(67,84,105),(203,188,154),(23,29,39)),
 "room": ((207,207,193),(239,229,205),(111,92,71),(49,45,40))
}
def font(size, bold=False):
    path="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    try: return ImageFont.truetype(path,size)
    except OSError: return ImageFont.load_default()
def load_scenes(text):
    code="import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan("+json.dumps(text)+")));"
    return json.loads(subprocess.run(["node","--input-type=module","-e",code],check=True,capture_output=True,text=True).stdout)
def inkline(d, pts, color, width=3):
    d.line(pts,fill=color,width=width,joint="curve")
def ellipse(d, box, fill, outline, width=2):
    d.ellipse(box,fill=fill,outline=outline,width=width)
def rounded(d, box, radius, fill, outline, width=2):
    d.rounded_rectangle(box,radius=radius,fill=fill,outline=outline,width=width)
def draw_cloud(d,x,y,s,color):
    for dx,dy,r in [(-25,5,20),(0,-7,27),(27,3,19),(48,9,14)]:
        ellipse(d,(x+(dx-r)*s,y+(dy-r)*s,x+(dx+r)*s,y+(dy+r)*s),color,color,1)
    d.rectangle((x-25*s,y+2*s,x+48*s,y+17*s),fill=color)
def draw_building(d,x,ground,w,h,wall,roof,ink,windows=True):
    d.rectangle((x,ground-h,x+w,ground),fill=wall,outline=ink,width=2)
    d.polygon([(x-7,ground-h),(x+w*.5,ground-h-24),(x+w+8,ground-h)],fill=roof,outline=ink)
    d.line((x,ground-h+3,x+w,ground-h+3),fill=ink,width=2)
    if windows:
        cols=max(1,int(w//34))
        for row in range(2):
            for c in range(cols):
                wx=x+8+c*(w-22)/max(1,cols-1); wy=ground-h+18+row*42
                if wx+15<x+w-3:
                    d.rectangle((wx,wy,wx+15,wy+25),fill=(111,137,143),outline=ink,width=2)
                    d.line((wx+7,wy,wx+7,wy+25),fill=ink,width=1)
    d.rectangle((x+w*.42,ground-48,x+w*.62,ground),fill=(105,75,55),outline=ink,width=2)
def draw_tree(d,x,y,scale,ink,leaf):
    d.rectangle((x-4*scale,y-55*scale,x+5*scale,y),fill=(92,69,49),outline=ink,width=1)
    for ox,oy,r in [(-15,-52,19),(5,-68,22),(20,-47,17)]:
        ellipse(d,(x+(ox-r)*scale,y+(oy-r)*scale,x+(ox+r)*scale,y+(oy+r)*scale),leaf,ink,1)
def draw_background(d,visual,t):
    sky,mid,ground,ink=PALETTES.get(visual,PALETTES["room"])
    d.rectangle((0,0,SW,SH),fill=sky)
    # Atmospheric sky and distant landscape
    if visual not in ("crime","investigation","prison","night","science","clock"):
        draw_cloud(d,140+int(math.sin(t*.08)*8),80,.8,(225,222,207))
        draw_cloud(d,690,62,.55,(231,226,208))
    if visual in ("historical","war","disaster","journey","conversation","village"):
        d.rectangle((0,0,SW,SH),fill=sky)
        # street perspective and varied facades
        draw_building(d,-15,355,190,245,(204,190,163),(107,79,62),ink)
        draw_building(d,160,355,150,195,(218,205,178),(132,91,66),ink)
        draw_building(d,720,355,160,220,(206,194,169),(113,84,66),ink)
        draw_building(d,855,355,145,270,(220,207,179),(121,83,65),ink)
        d.polygon([(0,355),(SW,355),(SW,SH),(0,SH)],fill=ground)
        d.polygon([(350,355),(610,355),(850,SH),(110,SH)],fill=(188,176,151))
        for k in range(8):
            yy=385+k*22
            d.line((390-k*28,yy,570+k*30,yy),fill=(151,139,119),width=1)
        # paving seams and curb
        for x in range(-50,1050,90): d.line((x,355,x+(x-480)*.35,SH),fill=(143,132,114),width=1)
        if visual=="war":
            d.rectangle((0,300,SW,SH),fill=(115,108,91))
            for x in (80,250,730,870):
                d.polygon([(x,340),(x+28,270),(x+60,340)],fill=(87,86,75))
            for x in (110,480,810):
                d.ellipse((x,320,x+34,334),fill=(57,56,49))
    elif visual in ("room","conversation","investigation","prison","crime","science","clock","classroom","home"):
        # interior walls with wood wainscot, windows, framed art and floorboards
        d.rectangle((0,0,SW,SH),fill=mid)
        d.rectangle((0,350,SW,SH),fill=(128,105,82))
        d.line((0,350,SW,350),fill=ink,width=4)
        d.rectangle((34,62,245,292),fill=(94,111,112),outline=ink,width=5)
        d.line((140,62,140,292),fill=(220,211,187),width=5)
        d.line((34,175,245,175),fill=(220,211,187),width=5)
        d.rectangle((305,72,440,205),fill=(112,86,65),outline=ink,width=5)
        d.rectangle((316,83,429,194),fill=(207,191,157),outline=ink,width=2)
        d.line((0,420,SW,420),fill=(82,68,55),width=2)
        for y in range(445,SH,35): d.line((0,y,SW,y),fill=(95,76,60),width=1)
        if visual in ("investigation","crime"):
            rounded(d,(565,65,900,325),8,(42,49,54),(24,27,29),5)
            for i in range(5):
                d.rectangle((590+i*57,100,630+i*57,160+(i%2)*50),fill=(168,145,108),outline=(220,204,168),width=2)
                d.line((585+i*57,180,630+i*57,180),fill=(209,197,164),width=2)
            d.line((585,270,865,270),fill=(190,174,139),width=3)
        elif visual=="science":
            rounded(d,(550,55,920,300),5,(42,68,77),(26,35,43),5)
            d.line((580,235,860,235),fill=(205,211,194),width=2)
            for i,h in enumerate((60,105,145,190)):
                d.rectangle((600+i*58,235-h,630+i*58,235),fill=(107,153,166),outline=(221,220,194),width=2)
        elif visual=="classroom":
            rounded(d,(560,70,900,265),4,(43,82,66),(28,39,34),5)
            d.line((590,110,850,110),fill=(222,219,190),width=2)
            d.line((590,150,790,150),fill=(222,219,190),width=2)
            d.line((590,190,825,190),fill=(222,219,190),width=2)
            for x in (115,300,470):
                rounded(d,(x,335,x+95,360),4,(132,91,58),ink,2)
                d.line((x+10,360,x+5,410),fill=ink,width=3)
                d.line((x+85,360,x+90,410),fill=ink,width=3)
        elif visual=="home":
            # upright piano, warm lamp and curtains
            d.rectangle((565,245,835,340),fill=(92,59,42),outline=ink,width=4)
            d.rectangle((580,260,820,286),fill=(45,39,35),outline=ink,width=2)
            for k in range(14):
                x=585+k*16
                d.rectangle((x,286,x+12,309),fill=(237,228,205),outline=ink,width=1)
            d.line((590,340,590,420),fill=ink,width=5); d.line((810,340,810,420),fill=ink,width=5)
            d.line((30,45,30,300),fill=(103,68,58),width=5)
            d.line((250,45,250,300),fill=(103,68,58),width=5)
        elif visual=="prison":
            for x in (520,600,680,760,840):
                d.line((x,0,x,SH),fill=(43,47,46),width=8)
            d.line((500,130,880,130),fill=(43,47,46),width=8)
    elif visual in ("desert","survival","wilderness"):
        d.rectangle((0,0,SW,SH),fill=sky)
        d.polygon([(0,300),(150,210),(310,300),(500,195),(710,290),(860,220),(SW,300),(SW,SH),(0,SH)],fill=mid)
        d.polygon([(0,370),(220,285),(430,380),(690,275),(SW,370),(SW,SH),(0,SH)],fill=ground)
        for x in (95,840): draw_tree(d,x,370,.8,ink,(79,103,66)) if visual=="wilderness" else None
        if visual=="desert":
            d.ellipse((740,65,830,155),fill=(238,196,119),outline=(238,196,119))
            for x in range(0,SW,70): d.line((x,455,x+45,452),fill=(188,145,91),width=2)
    elif visual=="shipwreck":
        d.rectangle((0,0,SW,SH),fill=sky)
        for y in (300,350,405,460):
            d.arc((-60,y-35,SW+80,y+65),0,180,fill=(160,194,196),width=5)
        d.polygon([(250,300),(730,300),(665,380),(325,380)],fill=(93,68,50),outline=ink)
        d.line((470,90,470,300),fill=ink,width=7)
        d.polygon([(478,110),(620,265),(478,265)],fill=(222,216,192),outline=ink)
    # atmospheric foreground grain / vignette
    d.rectangle((0,SH-9,SW,SH),fill=ink)
def draw_character(d,cx,base,scale,t,action,mood,variant=0,close=False):
    # Individualized wardrobe and silhouettes; coordinates are local scene pixels.
    ink=(31,30,29); skin=(249,246,235)
    coats=[(47,61,76),(91,73,57),(72,84,68),(83,81,78),(116,82,52),(53,62,67)]
    coat=coats[variant%len(coats)]
    bob=math.sin(t*3+variant)*2.2
    headw=48 if not close else 120; headh=58 if not close else 145
    bodyh=180 if not close else 330
    def P(x,y): return (cx+x*scale,base+y*scale)
    # legs behind coat
    stride=math.sin(t*5+variant)*13 if action in ("running","walking or travelling","fighting") else math.sin(t*2+variant)*2
    inkline(d,[P(-9, -bodyh*.22),P(-15+stride,-2)],ink,max(2,int(5*scale)))
    inkline(d,[P(9,-bodyh*.22),P(17-stride,-2)],ink,max(2,int(5*scale)))
    # shoes
    ellipse(d,(cx+(-25+stride)*scale,base-8*scale,cx+(-7+stride)*scale,base+1*scale),ink,ink,1)
    ellipse(d,(cx+(8-stride)*scale,base-8*scale,cx+(27-stride)*scale,base+1*scale),ink,ink,1)
    # jacket torso
    rounded(d,(cx-23*scale,base-bodyh*.75*scale,cx+23*scale,base-bodyh*.18*scale),7*scale,coat,ink,max(2,int(4*scale)))
    # shirt and tie
    d.polygon([P(-8,-bodyh*.74),P(8,-bodyh*.74),P(4,-bodyh*.28),P(0,-bodyh*.22),P(-4,-bodyh*.28)],fill=(242,237,219),outline=ink)
    d.polygon([P(-2,-bodyh*.68),P(3,-bodyh*.68),P(5,-bodyh*.35),P(0,-bodyh*.29),P(-4,-bodyh*.35)],fill=(76,45,42),outline=ink)
    # arms with animated gestures
    shoulder=P(-19,-bodyh*.68); shoulder2=P(19,-bodyh*.68)
    gesture=math.sin(t*4.2+variant*.7)
    if action in ("speaking or arguing","discovering or revealing"):
        left=P(-42,-bodyh*.48+gesture*5); left2=P(-52-gesture*7,-bodyh*.58+math.cos(t*4.2+variant)*10)
        right=P(42,-bodyh*.50-gesture*4); right2=P(56+gesture*9,-bodyh*.65+math.sin(t*4)*13)
    elif action in ("running","walking or travelling","fighting"):
        left=P(-42,-bodyh*.75+stride*.35); left2=P(-50,-bodyh*.94+stride*.65)
        right=P(42,-bodyh*.45-stride*.35); right2=P(52,-bodyh*.32-stride*.65)
    elif action in ("opening or unlocking","picking up or collecting","reaching or handing over"):
        left=P(-39,-bodyh*.45); left2=P(-47,-bodyh*.36)
        right=P(48,-bodyh*.58); right2=P(65,-bodyh*.50)
    else:
        sway=math.sin(t*2.3+variant)*4
        left=P(-37,-bodyh*.42+sway); left2=P(-38,-bodyh*.25+sway*1.4)
        right=P(37,-bodyh*.42-sway); right2=P(39,-bodyh*.25-sway*1.4)
    for a,b in ((shoulder,left),(left,left2),(shoulder2,right),(right,right2)):
        inkline(d,[a,b],coat,max(5,int(12*scale)))
        inkline(d,[a,b],ink,max(2,int(3*scale)))
    for hand in (left2,right2):
        ellipse(d,(hand[0]-5*scale,hand[1]-5*scale,hand[0]+5*scale,hand[1]+5*scale),skin,ink,max(1,int(2*scale)))
    # head and hair
    hy=base-bodyh*.80*scale+bob*scale
    ellipse(d,(cx-headw*scale/2,hy-headh*scale/2,cx+headw*scale/2,hy+headh*scale/2),skin,ink,max(2,int(3*scale)))
    hair=["short","side","bald","hat","cap","long"][variant%6]
    if hair=="short":
        d.pieslice((cx-headw*.52*scale,hy-headh*.58*scale,cx+headw*.52*scale,hy+headh*.22*scale),180,360,fill=(47,39,34),outline=ink,width=max(1,int(2*scale)))
    elif hair=="side":
        d.pieslice((cx-headw*.55*scale,hy-headh*.62*scale,cx+headw*.55*scale,hy+headh*.25*scale),180,355,fill=(67,49,38),outline=ink,width=max(1,int(2*scale)))
        d.polygon([(cx-2*scale,hy-headh*.52*scale),(cx+headw*.48*scale,hy-headh*.25*scale),(cx+headw*.18*scale,hy-headh*.35*scale)],fill=(67,49,38))
    elif hair=="bald":
        d.arc((cx-headw*.45*scale,hy-headh*.5*scale,cx+headw*.45*scale,hy+headh*.15*scale),190,350,fill=(120,105,90),width=max(1,int(2*scale)))
    elif hair in ("hat","cap"):
        d.rectangle((cx-headw*.52*scale,hy-headh*.42*scale,cx+headw*.52*scale,hy-headh*.26*scale),fill=(43,39,35),outline=ink,width=max(1,int(2*scale)))
        d.pieslice((cx-headw*.48*scale,hy-headh*.92*scale,cx+headw*.48*scale,hy-headh*.1*scale),180,360,fill=(40,38,36),outline=ink,width=max(1,int(2*scale)))
        d.rectangle((cx-headw*.5*scale,hy-headh*.5*scale,cx+headw*.5*scale,hy-headh*.36*scale),fill=(40,38,36))
    else:
        d.pieslice((cx-headw*.6*scale,hy-headh*.6*scale,cx+headw*.6*scale,hy+headh*.6*scale),180,360,fill=(49,38,34),outline=ink,width=max(1,int(2*scale)))
    # brows, eyes, nose and expressive mouth
    eye_y=hy+2*scale; eye_dx=10*scale
    if mood=="worried":
        inkline(d,[(cx-eye_dx-4*scale,eye_y-9*scale),(cx-eye_dx+4*scale,eye_y-5*scale)],ink,max(1,int(2*scale)))
        inkline(d,[(cx+eye_dx-4*scale,eye_y-5*scale),(cx+eye_dx+4*scale,eye_y-9*scale)],ink,max(1,int(2*scale)))
    elif mood=="active":
        inkline(d,[(cx-eye_dx-4*scale,eye_y-7*scale),(cx-eye_dx+4*scale,eye_y-9*scale)],ink,max(1,int(2*scale)))
        inkline(d,[(cx+eye_dx-4*scale,eye_y-9*scale),(cx+eye_dx+4*scale,eye_y-7*scale)],ink,max(1,int(2*scale)))
    else:
        inkline(d,[(cx-eye_dx-4*scale,eye_y-7*scale),(cx-eye_dx+4*scale,eye_y-7*scale)],ink,max(1,int(2*scale)))
        inkline(d,[(cx+eye_dx-4*scale,eye_y-7*scale),(cx+eye_dx+4*scale,eye_y-7*scale)],ink,max(1,int(2*scale)))
    blink=(math.sin(t*1.7+variant*2.1)>0.985)
    if blink:
        inkline(d,[(cx-eye_dx-4*scale,eye_y+2*scale),(cx-eye_dx+4*scale,eye_y+2*scale)],ink,max(1,int(2*scale)))
        inkline(d,[(cx+eye_dx-4*scale,eye_y+2*scale),(cx+eye_dx+4*scale,eye_y+2*scale)],ink,max(1,int(2*scale)))
    else:
        ellipse(d,(cx-eye_dx-3*scale,eye_y-2*scale,cx-eye_dx+3*scale,eye_y+5*scale),ink,ink,1)
        ellipse(d,(cx+eye_dx-3*scale,eye_y-2*scale,cx+eye_dx+3*scale,eye_y+5*scale),ink,ink,1)
    inkline(d,[(cx,eye_y+4*scale),(cx-2*scale,eye_y+11*scale),(cx+2*scale,eye_y+12*scale)],(139,111,91),max(1,int(1.5*scale)))
    if mood=="worried":
        d.arc((cx-8*scale,hy+15*scale,cx+8*scale,hy+30*scale),190,345,fill=ink,width=max(1,int(2*scale)))
    elif mood=="happy":
        d.arc((cx-11*scale,hy+9*scale,cx+11*scale,hy+29*scale),0,180,fill=ink,width=max(1,int(3*scale)))
    elif action=="speaking or arguing":
        mouth_open=5+abs(math.sin(t*8+variant))*8
        ellipse(d,(cx-5*scale,hy+14*scale,cx+5*scale,hy+(14+mouth_open)*scale),(91,43,42),ink,max(1,int(1*scale)))
    else:
        inkline(d,[(cx-7*scale,hy+20*scale),(cx+7*scale,hy+20*scale)],ink,max(1,int(2*scale)))
    # lapel and buttons
    inkline(d,[P(-9,-bodyh*.72),P(0,-bodyh*.58),P(9,-bodyh*.72)],(220,211,190),max(1,int(2*scale)))
    for by in (.48,.58,.67):
        ellipse(d,(cx-2*scale,base-bodyh*by*scale-2*scale,cx+2*scale,base-bodyh*by*scale+2*scale),ink,ink,1)
def draw_prop(d,name,x,y,ink):
    n=name.lower()
    if any(k in n for k in ("map","document","letter","evidence","photograph","note","book")):
        d.polygon([(x-27,y-20),(x+24,y-23),(x+28,y+22),(x-27,y+25)],fill=(231,216,178),outline=ink)
        for yy in (y-10,y,y+10): d.line((x-17,yy,x+15,yy),fill=(115,102,83),width=1)
    elif "clock" in n:
        ellipse(d,(x-21,y-21,x+21,y+21),(235,229,207),ink,3)
        d.line((x,y,x,y-13),fill=ink,width=2); d.line((x,y,x+12,y+6),fill=ink,width=2)
    elif any(k in n for k in ("boat","raft","vessel")):
        d.polygon([(x-38,y),(x+38,y),(x+25,y+14),(x-25,y+14)],fill=(122,81,53),outline=ink)
        d.line((x,y-40,x,y),fill=ink,width=3)
        d.polygon([(x+2,y-37),(x+29,y-9),(x+2,y-9)],fill=(231,222,198),outline=ink)
    elif any(k in n for k in ("weapon","rifle","gun")):
        d.rectangle((x-27,y-4,x+27,y+3),fill=(76,73,65),outline=ink,width=2)
        d.rectangle((x-8,y+2,x-1,y+13),fill=(92,65,45),outline=ink)
    elif "fire" in n:
        d.polygon([(x,y-28),(x-17,y+14),(x,y+7),(x+14,y+17)],fill=(219,112,49),outline=ink)
        d.polygon([(x,y-10),(x-6,y+13),(x+7,y+14)],fill=(246,196,91))
    else:
        rounded(d,(x-13,y-21,x+13,y+22),5,(179,183,166),ink,2)
def draw_scene(scene,index,t,duration,caption):
    visual=scene.get("visual","room"); mood=scene.get("mood","explaining"); action=scene.get("action","observing or explaining")
    sky,mid,ground,ink=PALETTES.get(visual,PALETTES["room"])
    im=Image.new("RGB",(SW,SH),sky); d=ImageDraw.Draw(im)
    draw_background(d,visual,t)
    shot=index%4
    if mood=="worried" and shot==0: shot=1
    if shot==0: # establishing: people small, place dominates
        scale=.86; cx=SW*.50; base=450
    elif shot==1: # medium two-shot / character and prop
        scale=1.18; cx=SW*.43; base=455
    elif shot==3: # controlled emotional close-up with full facial features in frame
        scale=1.45; cx=SW*.50; base=640
    else: # off-centre cinematic composition
        scale=1.28; cx=SW*.34; base=460
    # subtle distant crowd in historical/war/city scenes
    if visual in ("historical","war","conversation","disaster","village") and shot in (0,1):
        for j in range(9):
            px=70+j*100
            draw_character(d,px,382,.36,t*.5,"observing or explaining","explaining",j+2)
    # Supporting cast turns a single-person pose into a staged story beat.
    if shot==1 and (visual in ("conversation","investigation","crime","historical","war") or action in ("speaking or arguing","helping or rescuing","reaching or handing over")):
        partner_x=min(850,cx+245)
        draw_character(d,partner_x,base,scale*.78,t+1.1,"observing or explaining","worried" if mood=="worried" else "thinking",3)
    # main character
    draw_character(d,cx,base,scale,t,action,mood,0,close=(shot==3))
    props=scene.get("props",[])
    if props and shot!=3:
        px=min(850,cx+105*scale); py=base-150*scale
        draw_prop(d,props[0],px,py,ink)
    # scene-specific furniture / table foreground
    if visual in ("investigation","crime") and shot!=3:
        rounded(d,(cx-125,base-105,cx+165,base-72),5,(104,76,55),ink,2)
        for j in range(3): draw_prop(d,"document",cx-75+j*75,base-119,ink)
    elif visual=="room" and shot!=3:
        d.rectangle((cx+90,base-145,cx+240,base-90),fill=(120,82,52),outline=ink,width=3)
        d.line((cx+100,base-90,cx+100,base-10),fill=ink,width=4)
        d.line((cx+230,base-90,cx+230,base-10),fill=ink,width=4)
    # hand-drawn texture marks and subtle atmospheric overlay
    if visual in ("war","disaster","shipwreck"):
        for k in range(7):
            x=(k*137+int(t*8))%SW
            d.line((x,120+k*13,x+38,113+k*13),fill=(205,195,171),width=1)
    # top-left chapter marker is deliberately small, not a giant title card
    if shot==0:
        d.text((28,20),f"SCENE {index+1:02d}",font=font(13,True),fill=(242,235,218))
    # camera drift/zoom, then upscale to delivery resolution
    zoom=1.025+0.018*math.sin(t*.55)
    if shot==3: zoom=1.035+0.012*math.sin(t*.7)
    nw,nh=int(SW*zoom),int(SH*zoom)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    ox=max(0,(nw-SW)//2+int(math.sin(t*.24)*5)); oy=max(0,(nh-SH)//2+int(math.cos(t*.21)*3))
    im=im.crop((ox,oy,ox+SW,oy+SH))
    # cinematic soft vignette
    shade=Image.new("L",(SW,SH),0); sd=ImageDraw.Draw(shade)
    sd.ellipse((-SW*.12,-SH*.18,SW*1.12,SH*1.18),fill=255)
    shade=shade.filter(ImageFilter.GaussianBlur(45))
    dark=Image.new("RGB",(SW,SH),(12,14,17))
    im=Image.composite(im,dark,shade)
    d=ImageDraw.Draw(im)
    # subtitle panel with readable two-line safe margins
    if caption:
        lines=wrap(caption,width=78)[:2]
        y=SH-48
        rounded(d,(55,y-8,905,SH-12),8,(15,17,19),(15,17,19),1)
        for j,txt in enumerate(lines):
            d.text((SW//2,y+j*23),txt,font=font(17,True),fill=(250,248,239),anchor="ma")
    return im

def draw_scene_image(plate, scene, index, t, caption):
    # The generated illustration is the scene itself; animate it with a restrained Ken Burns move.
    im=ImageOps.fit(plate,(SW,SH),method=Image.Resampling.LANCZOS)
    zoom=1.025+0.022*math.sin(t*.42)
    if scene.get("mood")=="worried": zoom=1.045+0.025*math.sin(t*.55)
    nw,nh=int(SW*zoom),int(SH*zoom)
    im=im.resize((nw,nh),Image.Resampling.LANCZOS)
    ox=max(0,(nw-SW)//2+int(math.sin(t*.19+index)*8))
    oy=max(0,(nh-SH)//2+int(math.cos(t*.17+index)*5))
    im=im.crop((ox,oy,ox+SW,oy+SH))
    d=ImageDraw.Draw(im)
    visual=scene.get("visual","")
    action=scene.get("action","observing or explaining")
    mood=scene.get("mood","explaining")
    # Composite reusable animated character rigs over the AI-generated environment.
    # Background plates contain no people, so the same character design remains consistent
    # while limbs, expressions and mouth shapes animate independently on every frame.
    shot=index%3
    if mood=="worried" and shot==0:
        shot=1
    if shot==0:
        cx,base,scale=SW*.51,470,.82
    elif shot==1:
        cx,base,scale=SW*.39,478,1.02
    else:
        cx,base,scale=SW*.50,625,1.38
    interactive=(visual in ("conversation","investigation","crime","historical","war","classroom","home")
                 or action in ("speaking or arguing","helping or rescuing","reaching or handing over"))
    if shot==1 and interactive:
        draw_character(d,min(850,cx+260),base,scale*.76,t+1.1,"observing or explaining",
                       "worried" if mood=="worried" else "thinking",3)
    draw_character(d,cx,base,scale,t,action,mood,0,close=(shot==2))
    props=scene.get("props",[])
    if props and shot!=2:
        draw_prop(d,props[0],min(875,cx+115*scale),base-145*scale,(31,30,29))
    if visual in ("war","disaster","shipwreck","wilderness","desert"):
        for k in range(5):
            x=(k*181+int(t*12))%SW
            y=65+k*67
            if visual in ("war","disaster"):
                d.line((x,y,x+22,y-5),fill=(225,215,193),width=1)
            else:
                d.ellipse((x,y,x+2,y+2),fill=(224,216,197))
    if caption:
        lines=wrap(caption,width=78)[:2]
        y=SH-48
        rounded(d,(55,y-8,905,SH-12),8,(15,17,19),(15,17,19),1)
        for j,txt in enumerate(lines):
            d.text((SW//2,y+j*23),txt,font=font(17,True),fill=(250,248,239),anchor="ma")
    return im

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--narration",required=True,type=Path); ap.add_argument("--voice",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    ap.add_argument("--music",type=Path,default=Path("output/music.wav")); ap.add_argument("--sfx",type=Path,default=Path("output/sfx.wav"))
    args=ap.parse_args(); text=args.narration.read_text(encoding="utf-8").strip()
    if not text or len(text)>1800: raise SystemExit("Pilot narration must contain 1–1,800 characters.")
    scenes=load_scenes(text)
    with wave.open(str(args.voice),"rb") as wav:
        if wav.getnchannels()!=1 or wav.getsampwidth()!=2: raise SystemExit("Voice WAV must be mono 16-bit PCM.")
        audio_duration=wav.getnframes()/wav.getframerate()
    if audio_duration>MAX_SECONDS: raise SystemExit(f"Pilot audio is {audio_duration:.1f}s; maximum is {MAX_SECONDS}s.")
    total_frames=max(1,round(audio_duration*FPS)); weights=[max(1,len(s["narration"].split())) for s in scenes]
    total_words=sum(weights); durations=[audio_duration*w/total_words for w in weights]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    lead_visual=scenes[0].get("visual","historical") if scenes else "historical"
    subprocess.run([sys.executable,"scripts/generate_music.py","--seconds",str(audio_duration),"--visual",lead_visual,"--output",str(args.music)],check=True)
    subprocess.run([sys.executable,"scripts/generate_sfx.py","--narration",str(args.narration),"--seconds",str(audio_duration),"--output",str(args.sfx)],check=True)
    def stamp(v):
        ms=round(v*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); sec,ms=divmod(ms,1000)
        return f"{h:02}:{m:02}:{sec:02},{ms:03}"
    srt=[]; cursor=0.0
    for i,(scene,dur) in enumerate(zip(scenes,durations),1):
        start=cursor; cursor+=dur; srt.append(f"{i}\n{stamp(start)} --> {stamp(cursor)}\n{scene['narration']}\n")
    args.output.with_suffix(".srt").write_text("\n".join(srt),encoding="utf-8")
    scene_dir=args.output.parent/"scenes"
    ai_scene_count=sum(1 for i in range(len(scenes)) if (scene_dir/f"scene_{i+1:04d}.png").exists())
    meta={"renderer":"AI-illustrated scene plates with 2D camera animation + Pillow/FFmpeg" if ai_scene_count else "layered procedural illustrated 2D cartoon + Pillow/FFmpeg","resolution":"1920x1080","fps":FPS,"audio_seconds":round(audio_duration,3),"scene_count":len(scenes),"voice":"mono narration WAV supplied","captions":"burned in; scene-weighted timing","music":"procedural cinematic underscore ducked under narration","sound_effects":"procedural event cues","ai_generated_scene_count":ai_scene_count,"visual_features":(["AI-generated bespoke scene plates","Ken Burns camera movement and scene dissolves"] if ai_scene_count else ["procedural period/location-specific illustrated environments","individualized clothed characters with facial expressions","crowd layers","wide/medium/close shot variation","subtle camera drift and zoom"]),"limitations":(["AI scene plates are still illustrations animated with camera motion and dissolves, not frame-by-frame character animation","scene timing is estimated by narration word count"] if ai_scene_count else ["characters and sets are procedural vector-style illustrations, not hand-animated frame-by-frame","scene timing is estimated by narration word count"])}
    args.output.with_suffix(".json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    ffmpeg_bin=shutil.which("ffmpeg")
    if not ffmpeg_bin:
        try:
            import imageio_ffmpeg
            ffmpeg_bin=imageio_ffmpeg.get_ffmpeg_exe()
        except ImportError as exc:
            raise RuntimeError("FFmpeg is missing. Install imageio-ffmpeg or provide ffmpeg on PATH.") from exc
    cmd=[ffmpeg_bin,"-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{SW}x{SH}","-r",str(FPS),"-i","-","-i",str(args.voice),"-i",str(args.music),"-i",str(args.sfx),"-filter_complex","[2:a]volume=0.24[bed];[bed][1:a]sidechaincompress=threshold=0.025:ratio=8:attack=20:release=550[ducked];[3:a]volume=0.55[sfx];[1:a][ducked][sfx]amix=inputs=3:duration=first:dropout_transition=2:normalize=0,alimiter=limit=0.95[aout]","-map","0:v:0","-s:v",f"{W}x{H}","-map","[aout]","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(args.output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE); scene_index=0; boundaries=[]; c=0
    for dur in durations: c+=dur; boundaries.append(c)
    current_plate=None; current_plate_index=-1; previous_frame=None; transition_from=None
    try:
        for frame in range(total_frames):
            while scene_index<len(durations)-1 and frame/FPS>=boundaries[scene_index]: scene_index+=1
            if scene_index!=current_plate_index:
                if previous_frame is not None: transition_from=previous_frame.copy()
                current_plate_index=scene_index
                plate_path=scene_dir/f"scene_{scene_index+1:04d}.png"
                current_plate=Image.open(plate_path).convert("RGB") if plate_path.exists() else None
            local_t=max(0,frame/FPS-(boundaries[scene_index-1] if scene_index else 0))
            scene=scenes[scene_index]
            if current_plate is not None:
                frame_image=draw_scene_image(current_plate,scene,scene_index,local_t,scene["narration"])
            else:
                frame_image=draw_scene(scene,scene_index,local_t,durations[scene_index],scene["narration"])
            if transition_from is not None:
                if local_t<0.35:
                    frame_image=Image.blend(transition_from,frame_image,min(1.0,local_t/0.35))
                else:
                    transition_from=None
            proc.stdin.write(frame_image.tobytes())
            previous_frame=frame_image
            if frame%150==0: print(f"Rendered {frame}/{total_frames} frames",flush=True)
        proc.stdin.close(); code=proc.wait()
        if code: raise RuntimeError(f"FFmpeg exited with code {code}")
    except Exception:
        if proc.poll() is None: proc.kill()
        raise
    if not args.output.exists() or args.output.stat().st_size<100000: raise RuntimeError("MP4 output missing or unexpectedly small.")
    print(json.dumps(meta))
if __name__=="__main__":
    try: main()
    except Exception as exc: print(f"Render failed: {exc}",file=sys.stderr); raise
