#!/usr/bin/env python3
"""Render a bounded narration-driven stick-figure MP4 with voice and burned captions."""
from __future__ import annotations
import argparse, json, math, subprocess, sys, wave
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from textwrap import wrap

W, H, FPS = 1920, 1080, 30
MAX_SECONDS = 90
BG = {
 "historical": (225, 216, 194), "crime": (34, 39, 48),
 "investigation": (38, 48, 59), "prison": (76, 80, 79),
 "desert": (220, 183, 125), "shipwreck": (42, 83, 105),
 "wilderness": (83, 111, 87), "war": (111, 99, 82),
 "disaster": (105, 88, 79), "survival": (103, 118, 108),
 "night": (24, 31, 49), "clock": (43, 49, 58),
 "conversation": (222, 224, 219), "journey": (174, 191, 177),
 "science": (31, 43, 61), "room": (224, 226, 222)
}
DARK = {"crime","investigation","shipwreck","night","clock","science"}
def font(size, bold=False):
    paths = ["/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]
    for p in paths:
        try: return ImageFont.truetype(p, size)
        except OSError: pass
    return ImageFont.load_default()
def load_scenes(text):
    code = "import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan("+json.dumps(text)+")));"
    out = subprocess.run(["node","--input-type=module","-e",code],check=True,capture_output=True,text=True)
    return json.loads(out.stdout)
def line(draw, pts, fill, width=14):
    draw.line(pts, fill=fill, width=width, joint="curve")
def draw_person(draw, x, floor, t, action, mood, color):
    bob = math.sin(t*3)*7
    head_y = floor-340+bob
    draw.ellipse((x-76,head_y-76,x+76,head_y+76),fill=(250,249,243),outline=color,width=15)
    # expressive face
    draw.ellipse((x-27,head_y-12,x-12,head_y+3),fill=color)
    draw.ellipse((x+12,head_y-12,x+27,head_y+3),fill=color)
    if mood == "worried":
        draw.arc((x-30,head_y+15,x+30,head_y+66),180,350,fill=color,width=8)
    else:
        draw.arc((x-33,head_y+4,x+33,head_y+56),10,170,fill=color,width=8)
    shoulder=(x, floor-245+bob); hip=(x,floor-100+bob)
    line(draw,[shoulder,hip],color,18)
    stride=math.sin(t*5)*50 if action in ("running","walking or travelling") else math.sin(t*2)*9
    line(draw,[hip,(x-75+stride,floor-8)],color,17)
    line(draw,[hip,(x+75-stride,floor-8)],color,17)
    if action in ("fighting","running"):
        line(draw,[shoulder,(x-115,floor-190+bob),(x-165,floor-245+bob)],color,17)
        line(draw,[shoulder,(x+115,floor-190+bob),(x+165,floor-245+bob)],color,17)
    elif action in ("opening or unlocking","picking up or collecting","searching for clues"):
        line(draw,[shoulder,(x-105,floor-165+bob),(x-165,floor-205+bob)],color,17)
        line(draw,[shoulder,(x+105,floor-165+bob),(x+155,floor-95+bob)],color,17)
    else:
        line(draw,[shoulder,(x-105,floor-170+bob),(x-145,floor-115+bob)],color,17)
        line(draw,[shoulder,(x+105,floor-170+bob),(x+145,floor-115+bob)],color,17)
def draw_prop(draw, name, x, y, ink):
    if "map" in name or "document" in name or "letter" in name or "evidence" in name:
        draw.rectangle((x-65,y-45,x+65,y+45),fill=(239,224,180),outline=ink,width=8)
        draw.line((x-42,y-15,x+40,y-15),fill=ink,width=5); draw.line((x-42,y+5,x+25,y+5),fill=ink,width=5)
    elif "clock" in name:
        draw.ellipse((x-48,y-48,x+48,y+48),fill=(245,245,235),outline=ink,width=8)
        draw.line((x,y,x,y-28),fill=ink,width=7); draw.line((x,y,x+25,y+12),fill=ink,width=7)
    elif "boat" in name:
        draw.polygon([(x-90,y),(x+90,y),(x+55,y+35),(x-55,y+35)],fill=(129,87,54),outline=ink)
        draw.line((x,y-90,x,y),fill=ink,width=8); draw.polygon([(x+5,y-85),(x+65,y-20),(x+5,y-20)],fill=(235,230,210))
    else:
        draw.rounded_rectangle((x-38,y-60,x+38,y+60),radius=15,fill=(190,195,183),outline=ink,width=8)
def draw_scene(scene, index, t, duration, caption):
    visual=scene.get("visual","room"); bg=BG.get(visual,BG["room"]); ink=(245,245,238) if visual in DARK else (28,31,29)
    im=Image.new("RGB",(W,H),bg); d=ImageDraw.Draw(im)
    # graphic environment, horizon and atmospheric shapes
    d.rectangle((0,760,W,H),fill=tuple(max(0,min(255,int(c*.78))) for c in bg))
    d.ellipse((W-500,100,W-220,380),fill=(226,190,116) if visual not in DARK else (94,116,150))
    # setting-specific silhouettes
    if visual in ("historical","war","prison"):
        for bx in (120,1550):
            d.rectangle((bx,430,bx+240,760),outline=ink,width=13)
            for wx in range(bx+35,bx+220,75): d.rectangle((wx,490,wx+38,590),outline=ink,width=8)
    elif visual in ("desert","survival"):
        d.arc((80,520,900,1040),180,350,fill=ink,width=10); d.arc((900,500,1800,1020),190,350,fill=ink,width=10)
    elif visual in ("shipwreck","disaster"):
        for yy in (820,875,930):
            d.arc((0,yy-50,W,yy+90),0,180,fill=(170,205,213),width=10)
    elif visual in ("crime","investigation"):
        d.rectangle((1320,420,1710,760),outline=ink,width=12)
        d.line((1360,500,1660,500),fill=ink,width=8)
    elif visual=="wilderness":
        for tx in (150,1660):
            d.rectangle((tx-12,420,tx+12,790),fill=ink)
            d.ellipse((tx-120,300,tx+120,580),fill=(57,91,65))
    # scene label and camera motion
    title=scene.get("title",""); d.text((100,90),f"CHAPTER  {index+1:02d}",font=font(30,True),fill=ink)
    d.text((100,145),title[:62],font=font(42,True),fill=ink)
    progress=t/max(duration,.01); x=int(620+math.sin(t*1.1)*75)
    floor=785
    action=scene.get("action","observing or explaining")
    draw_person(d,x,floor,t,action,scene.get("mood","explaining"),ink)
    props=scene.get("props",[])
    if props: draw_prop(d,props[0],x+245,650,ink)
    if scene.get("visual") in ("conversation","investigation") or "talk" in scene.get("narration","").lower():
        draw_person(d,1320,floor,t+1.2,"observing or explaining","thinking",ink)
    # animated motion accents
    if action in ("running","fighting","falling or collapsing"):
        for k in range(3):
            sx=x-230-k*38
            d.line((sx,520+k*35,sx-45,520+k*35),fill=ink,width=7)
    # burned-in narration caption
    if caption:
        lines=wrap(caption, width=66)[:2]
        y=900
        box=(150,y-22,1770,y+len(lines)*54+25)
        d.rounded_rectangle(box,radius=22,fill=(9,12,16))
        for j,txt in enumerate(lines):
            d.text((W//2,y+j*54),txt,font=font(34,True),fill=(255,255,255),anchor="ma")
    return im
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--narration",required=True,type=Path); ap.add_argument("--voice",required=True,type=Path)
    ap.add_argument("--output",required=True,type=Path)
    args=ap.parse_args()
    text=args.narration.read_text(encoding="utf-8").strip()
    if not text or len(text)>1800: raise SystemExit("Pilot narration must contain 1–1,800 characters.")
    scenes=load_scenes(text)
    with wave.open(str(args.voice),"rb") as wav:
        if wav.getnchannels()!=1 or wav.getsampwidth()!=2: raise SystemExit("Voice WAV must be mono 16-bit PCM.")
        audio_duration=wav.getnframes()/wav.getframerate()
    if audio_duration>MAX_SECONDS: raise SystemExit(f"Pilot audio is {audio_duration:.1f}s; maximum is {MAX_SECONDS}s.")
    total_frames=max(1,round(audio_duration*FPS))
    weights=[max(1,len(s["narration"].split())) for s in scenes]; total_words=sum(weights)
    durations=[audio_duration*w/total_words for w in weights]
    args.output.parent.mkdir(parents=True,exist_ok=True)
    srt=[]; cursor=0.0
    for i,(scene,dur) in enumerate(zip(scenes,durations),1):
        start=cursor; cursor+=dur
        def stamp(v):
            ms=round(v*1000); h,ms=divmod(ms,3600000); m,ms=divmod(ms,60000); sec,ms=divmod(ms,1000)
            return f"{h:02}:{m:02}:{sec:02},{ms:03}"
        srt.append(f"{i}\n{stamp(start)} --> {stamp(cursor)}\n{scene['narration']}\n")
    srt_path=args.output.with_suffix(".srt"); srt_path.write_text("\n".join(srt),encoding="utf-8")
    meta={"renderer":"Pillow vector animation + FFmpeg","resolution":"1920x1080","fps":FPS,"audio_seconds":round(audio_duration,3),"scene_count":len(scenes),"voice":"Gemini WAV supplied","captions":"burned in; scene-weighted timing","limitations":["procedural stick-figure animation, not generative character animation","no music or sound effects in this pilot","scene timing is estimated by narration word count"]}
    args.output.with_suffix(".json").write_text(json.dumps(meta,indent=2),encoding="utf-8")
    cmd=["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(args.voice),"-map","0:v:0","-map","1:a:0","-c:v","libx264","-preset","ultrafast","-crf","22","-pix_fmt","yuv420p","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(args.output)]
    proc=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    frame_index=0; scene_index=0; scene_start=0
    try:
        for frame_index in range(total_frames):
            while scene_index<len(durations)-1 and frame_index>=round(sum(durations[:scene_index+1])*FPS):
                scene_index+=1
            local_t=max(0,frame_index/FPS-sum(durations[:scene_index]))
            scene= scenes[scene_index]
            im=draw_scene(scene,scene_index,local_t,durations[scene_index],scene["narration"])
            proc.stdin.write(im.tobytes())
            if frame_index%150==0: print(f"Rendered {frame_index}/{total_frames} frames",flush=True)
        proc.stdin.close()
        code=proc.wait()
        if code: raise RuntimeError(f"FFmpeg exited with code {code}")
    except Exception:
        if proc.poll() is None: proc.kill()
        raise
    if not args.output.exists() or args.output.stat().st_size<100000: raise RuntimeError("MP4 output missing or unexpectedly small.")
    print(json.dumps(meta))
if __name__=="__main__":
    try: main()
    except Exception as exc: print(f"Render failed: {exc}",file=sys.stderr); raise
