#!/usr/bin/env python3
"""Generate an original, royalty-free procedural cinematic underscore (no samples)."""
import argparse, math, random, wave
from pathlib import Path
from array import array

RATE=24000
SCALE={
 "minor":[0,3,7,10], "major":[0,4,7,11], "suspense":[0,1,7,10],
 "hope":[0,4,7,9], "epic":[0,5,7,10]
}
ROOTS={"historical":110.0,"crime":82.41,"investigation":98.0,"prison":92.5,
 "desert":123.47,"shipwreck":82.41,"wilderness":110.0,"war":73.42,
 "disaster":82.41,"survival":98.0,"night":73.42,"clock":82.41,
 "conversation":130.81,"journey":110.0,"science":65.41,"room":110.0}
def generate(path, seconds, visual):
    seconds=max(.1,float(seconds)); count=round(seconds*RATE)
    root=ROOTS.get(visual,110.0)
    mode="suspense" if visual in ("crime","investigation","prison","night","clock","shipwreck") else ("epic" if visual in ("war","disaster") else "minor")
    intervals=SCALE[mode]
    rng=random.Random(37)
    phases=[rng.random()*math.tau for _ in range(9)]
    progressions={
        "minor":[0,5,3,7],
        "suspense":[0,-1,3,7],
        "epic":[0,5,7,3],
        "major":[0,5,3,4],
        "hope":[0,5,3,7]
    }
    progression=progressions.get(mode,[0,5,3,7])
    samples=array("h")
    chord_seconds=8.0
    for i in range(count):
        t=i/RATE
        chord=int(t/chord_seconds)%4
        transpose=progression[chord]
        chord_root=root*(2**(transpose/12))
        semis=(0, intervals[1], intervals[2], intervals[3])
        # Layered string-like pad, low cinematic drone, and a restrained repeating ostinato.
        value=0.0
        for j,step in enumerate(semis):
            freq=chord_root*(2**(step/12))
            lfo=0.88+0.12*math.sin(math.tau*(0.035+j*0.009)*t+phases[j])
            voice=math.sin(math.tau*freq*t+phases[j]+0.10*math.sin(t*.17))
            detuned=math.sin(math.tau*(freq*1.003)*t+phases[j+4])
            value += (0.075/(1+j*.25))*lfo*(0.72*voice+0.28*detuned)
        value += .045*math.sin(math.tau*(chord_root/2)*t+phases[8])
        # Soft repeating arpeggio gives the bed a pulse without competing with speech.
        beat=t%1.5
        arp_step=(0,2,1,3)[int((t%3.0)/.75)]
        arp_freq=chord_root*(2**(semis[arp_step]/12))*2
        arp_env=math.exp(-beat*3.8)
        value += .026*arp_env*math.sin(math.tau*arp_freq*t)
        pulse=(.5+.5*math.sin(math.tau*.25*t))**5
        value += .022*pulse*math.sin(math.tau*chord_root*t)
        # gentle fade at both ends; no abrupt clicks
        fade=min(1.0,t/2.5,(seconds-t)/3.0)
        value*=max(0.0,fade)
        value=max(-.8,min(.8,value))
        sample=int(value*32767)
        samples.append(sample); samples.append(sample)
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with wave.open(str(path),"wb") as out:
        out.setnchannels(2); out.setsampwidth(2); out.setframerate(RATE)
        out.writeframes(samples.tobytes())
    return {"duration":round(seconds,3),"sample_rate":RATE,"channels":2,"style":mode,"source":"original procedural synthesis"}
def main():
    p=argparse.ArgumentParser()
    p.add_argument("--seconds",type=float,required=True); p.add_argument("--visual",default="historical")
    p.add_argument("--output",type=Path,required=True); a=p.parse_args()
    print(generate(a.output,a.seconds,a.visual))
if __name__=="__main__": main()
