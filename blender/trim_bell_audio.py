"""Keep actual single/double strikes from the supplied recording, including decay."""
from pathlib import Path
import numpy as np
import wave,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
samples=np.load(ROOT/'build/bell-audio/samples.npy');rate=44100
out=ROOT/'site/assets/audio';out.mkdir(exist_ok=True)
report={'source':'飞书20261026-104601.qt','rate':rate,'channels':1,'processing':'Mono mix, DC removal, common gain 1.2, 5 ms fade-in and 80 ms fade-out. No synthesized or repeated strikes.','clips':{}}
for name,start,end in [('single',.925,2.10),('double',2.19,4.30)]:
    data=samples[round(start*rate):round(end*rate)].copy()
    data-=data.mean();data*=1.2
    fade_in=round(rate*.005);fade_out=round(rate*.08)
    data[:fade_in]*=np.linspace(0,1,fade_in)
    data[-fade_out:]*=np.linspace(1,0,fade_out)
    step=round(rate*.01)
    envelope=np.array([np.sqrt(np.mean(data[i:i+step]**2)) for i in range(0,len(data),step)])
    strikes=[]
    for i in np.argsort(envelope)[::-1]:
        if envelope[i]<.075:break
        if all(abs(int(i)-j)>20 for j in strikes):strikes.append(int(i))
    assert len(strikes)==(1 if name=='single' else 2),(name,strikes)
    assert np.abs(data).max()<.99,'Audio clipping'
    pcm=(np.clip(data,-1,1)*32767).astype('<i2').tobytes()
    path=out/f'bell-{name}.wav'
    with wave.open(str(path),'wb') as f:
        f.setnchannels(1);f.setsampwidth(2);f.setframerate(rate);f.writeframes(pcm)
    report['clips'][name]={'source_start':start,'source_end':end,'duration':len(data)/rate,'peak':float(np.abs(data).max()),'strikes_seconds':sorted(round(i*.01,2) for i in strikes),'sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
(ROOT/'build/bell-audio/extraction.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(report,ensure_ascii=False,indent=2))
