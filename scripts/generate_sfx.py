#!/usr/bin/env python3
"""Create lightweight, original synthetic scene SFX cues from narration; no sampled audio."""
import argparse, json, math, random, re, wave
from array import array
from pathlib import Path

RATE=24000
def tone(freq, t, decay, phase=0):
    return math.sin(2*math.pi*freq*t+phase)*math.exp(-t/decay)
def cue(kind, seconds=1.0, seed=1):
    rng=random.Random(seed); n=max(1,round(seconds*RATE)); out=array("h")
    for i in range(n):
        t=i/RATE; v=0.0
        if kind=="steps":
            phase=(t%0.42); env=math.exp(-phase*15) if phase<.12 else 0
            v=.36*env*(tone(72-20*phase,phase,.08)+.4*rng.uniform(-1,1))
        elif kind=="door":
            v=.5*tone(95,t,.09)+.25*tone(240,t,.05)+.15*rng.uniform(-1,1)*math.exp(-t*18)
        elif kind=="keys":
            env=math.exp(-t*5); v=env*(.22*tone(1700,t,.12)+.15*tone(2350,t,.09)+.15*rng.uniform(-1,1))
        elif kind=="water":
            env=min(1,t*4)*math.exp(-t*1.3); v=.32*rng.uniform(-1,1)*env+.08*tone(110,t,.5)*env
        elif kind=="wind":
            v=.19*rng.uniform(-1,1)*(0.5+0.5*math.sin(t*2.1))*min(1,t*2)
        elif kind=="impact":
            env=math.exp(-t*8); v=.65*env*(tone(58+20*math.exp(-t*20),t,.12)+.25*rng.uniform(-1,1))
        elif kind=="fire":
            v=.18*rng.uniform(-1,1)*(.3+.7*abs(math.sin(t*9)))*math.exp(-t*.18)
        elif kind=="alarm":
            v=.25*math.sin(2*math.pi*(650+180*math.sin(t*5))*t)*math.exp(-t*.2)
        elif kind=="reveal":
            env=min(1,t*2)*math.exp(-t*.6); v=.25*env*(tone(220,t,1)+tone(330,t,1)+tone(440,t,1))
        elif kind=="train":
            # Distant steam locomotive: low rolling rhythm, metal wheel clacks and a breath of steam.
            wheel=(.5+.5*math.sin(2*math.pi*3.2*t))**7
            v=.22*wheel*tone(68,t,.45)+.13*wheel*tone(142,t,.32)+.12*rng.uniform(-1,1)*math.exp(-t*.42)
            v+=.08*tone(410+35*math.sin(t*2),t,1.1)
        elif kind=="paper":
            # Close paper handling: short dry rustles and two light folds.
            pulse=max(0,math.sin(2*math.pi*2.1*t))**10
            v=.19*rng.uniform(-1,1)*(pulse+.12)*math.exp(-t*.35)
            v+=.035*tone(1250+250*math.sin(t*13),t,.18)
        elif kind=="crowd":
            # Soft distant station murmur, deliberately kept behind narration.
            v=.07*(tone(118,t,1.7)+tone(173,t,1.3)+tone(226,t,1.1))
            v+=.045*rng.uniform(-1,1)*(0.5+0.5*math.sin(t*1.7))
        elif kind=="artillery":
            env=math.exp(-t*2.2)
            v=.55*env*(tone(46,t,.5)+.35*tone(91,t,.3))
            v+=.16*rng.uniform(-1,1)*math.exp(-t*5)
        elif kind=="whistle":
            env=min(1,t*5)*math.exp(-t*.35)
            freq=520+110*math.sin(t*1.4)
            v=.20*env*math.sin(2*math.pi*freq*t)+.08*env*math.sin(2*math.pi*(freq*1.5)*t)
        fade=min(1,t/.025,(seconds-t)/.06); v=max(-.85,min(.85,v*max(0,fade)))
        sample=int(v*32767); out.append(sample); out.append(sample)
    return out
def choose(narration, visual, action):
    text=narration.lower()
    if re.search(r'\b(explosion|explode|bomb|crash|impact|collapse|fell|fall|struck)\b',text): return "impact"
    if re.search(r'\b(opened|unlock|door|gate|key|locked)\b',text): return "door" if "door" in text or "gate" in text else "keys"
    if re.search(r'\b(waves|ocean|sea|water|ship|raft|drown|sinking)\b',text) or visual=="shipwreck": return "water"
    if re.search(r'\b(wind|storm|desert|blizzard|cold|night|darkness)\b',text) or visual in ("desert","wilderness","night"): return "wind"
    if re.search(r'\b(walk|walking|run|ran|running|flee|fled|chase|march|steps|footsteps)\b',text): return "steps"
    if re.search(r'\b(fire|flame|burn|campfire)\b',text): return "fire"
    if re.search(r'\b(discover|found|revealed|realized|uncovered)\b',text): return "reveal"
    if visual in ("war","disaster"): return "impact"
    if visual in ("crime","investigation","prison"): return "wind"
    return None
def main():
    p=argparse.ArgumentParser(); p.add_argument("--narration",type=Path,required=True); p.add_argument("--output",type=Path,required=True); p.add_argument("--seconds",type=float,required=True); a=p.parse_args()
    text=a.narration.read_text(encoding="utf-8")
    code="import {buildScenePlan} from './src/scene-planner.js'; console.log(JSON.stringify(buildScenePlan("+json.dumps(text)+")));"
    import subprocess
    scenes=json.loads(subprocess.run(["node","--input-type=module","-e",code],check=True,capture_output=True,text=True).stdout)
    total=round(a.seconds*RATE); mix=array("h",[0])*(total*2); cues=[]; cursor=0
    weights=[max(1,len(s["narration"].split())) for s in scenes]; words=sum(weights)
    for i,(scene,w) in enumerate(zip(scenes,weights)):
        duration=a.seconds*w/words; kind=choose(scene["narration"],scene["visual"],scene["action"])
        if kind:
            start=cursor+duration*.28
            clip=cue(kind,min(2.3,max(.45,duration*.62)),i+23)
            offset=round(start*RATE)*2
            for j,val in enumerate(clip):
                pos=offset+j
                if pos<len(mix): mix[pos]=max(-32768,min(32767,mix[pos]+int(val*.42)))
            cues.append({"scene":i+1,"kind":kind,"start":round(start,3),"duration":round(len(clip)/2/RATE,3)})
        cursor+=duration
    a.output.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(a.output),"wb") as f: f.setnchannels(2); f.setsampwidth(2); f.setframerate(RATE); f.writeframes(mix.tobytes())
    print(json.dumps({"cue_count":len(cues),"cues":cues,"source":"procedurally synthesized"}))
if __name__=="__main__": main()
