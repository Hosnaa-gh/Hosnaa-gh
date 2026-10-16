#!/usr/bin/env python3
"""Build a GitHub-safe, self-contained SVG using public GitHub data.
No third-party Python packages. GraphQL calendar uses GITHUB_TOKEN if available.
"""
import os, json, urllib.request, urllib.error, datetime, calendar, html, math
from collections import Counter, defaultdict
from pathlib import Path

USER = os.getenv('GITHUB_PROFILE_USER', 'Hosnaa-gh')
TOKEN = os.getenv('GITHUB_TOKEN', '')
OUT = Path(__file__).resolve().parents[1] / 'assets' / 'command-center.svg'
TODAY = datetime.datetime.now(datetime.timezone.utc).date()

def api(url, payload=None):
    headers={'Accept':'application/vnd.github+json','User-Agent':'hosnaa-profile-dashboard','X-GitHub-Api-Version':'2022-11-28'}
    if TOKEN: headers['Authorization']='Bearer '+TOKEN
    data=json.dumps(payload).encode() if payload else None
    if data: headers['Content-Type']='application/json'
    req=urllib.request.Request(url,data=data,headers=headers)
    try:
        with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
    except (urllib.error.URLError, ValueError, TimeoutError) as e:
        print('Data request unavailable:',str(e)[:140]);return None

def esc(x):return html.escape(str(x),quote=True)
def txt(x,y,s,size=15,color='#cbd5e1',weight=400,mono=True,anchor=None):
    attrs=f' x="{x}" y="{y}" font-size="{size}" fill="{color}" font-weight="{weight}"'
    if anchor:attrs+=f' text-anchor="{anchor}"'
    return f'<text{attrs} font-family="{("JetBrains Mono, Consolas, monospace" if mono else "Inter, Segoe UI, sans-serif")}">{esc(s)}</text>'
def rect(x,y,w,h,fill='#08121c',stroke='#23384a',r=12):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}" stroke="{stroke}"/>'
def line(x1,y1,x2,y2,c='#263748',w=1):return f'<path d="M{x1} {y1} L{x2} {y2}" stroke="{c}" stroke-width="{w}"/>'
def panel(x,y,w,h,title):return rect(x,y,w,h)+txt(x+20,y+33,title,17,'#f1f5f9',650)
def clamp(n,a,b):return max(a,min(b,n))

profile=api(f'https://api.github.com/users/{USER}') or {}
repos=[]
for page in range(1,5):
    data=api(f'https://api.github.com/users/{USER}/repos?per_page=100&page={page}&type=owner&sort=updated')
    if not isinstance(data,list):break
    repos.extend([r for r in data if not r.get('fork') and not r.get('private')])
    if len(data)<100:break
langs=Counter()
for r in repos:
    language_data=api(r.get('languages_url','')) if r.get('languages_url') else None
    if isinstance(language_data,dict):langs.update({k:int(v) for k,v in language_data.items()})
    elif r.get('language'):langs[r['language']]+=1

# Public contribution calendar from GitHub GraphQL. If unavailable, never invent cells.
query='query($login:String!){user(login:$login){contributionsCollection{contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}'
graph=api('https://api.github.com/graphql',{'query':query,'variables':{'login':USER}}) if TOKEN else None
calendar_data=((((graph or {}).get('data') or {}).get('user') or {}).get('contributionsCollection') or {}).get('contributionCalendar') or {}
counts={d['date']:d['contributionCount'] for w in calendar_data.get('weeks',[]) for d in w.get('contributionDays',[])}
total=calendar_data.get('totalContributions')

# No made-up commits, followers, or contributions.
repo_count=profile.get('public_repos', 'N/A')
stars=sum(int(r.get('stargazers_count',0)) for r in repos) if repos else 'N/A'
followers=profile.get('followers')
updated=TODAY.strftime('%d %b %Y')
S=[]
S.append('''<svg xmlns="http://www.w3.org/2000/svg" width="1500" height="970" viewBox="0 0 1500 970" role="img" aria-label="Hosna developer command center with live GitHub data"><defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#050c14"/><stop offset="1" stop-color="#07141b"/></linearGradient><linearGradient id="a" x2="1" y2="0"><stop stop-color="#00e9a6"/><stop offset="1" stop-color="#468bff"/></linearGradient><linearGradient id="bar" x2="1" y2="0"><stop stop-color="#00cc93"/><stop offset="1" stop-color="#426bff"/></linearGradient></defs><rect width="1500" height="970" fill="url(#bg)"/>''')
# sidebar
S.append(rect(22,22,260,926,'#07111a','#254056',16))
S.append(rect(42,42,220,160,'#081b22','#164b45',14))
# stylized abstract orbital avatar, not a photo
for rad in (55,39,24):S.append(f'<circle cx="152" cy="120" r="{rad}" fill="none" stroke="#00dca2" stroke-opacity="{0.22 if rad!=39 else 0.7}" stroke-width="1.5" stroke-dasharray="5 7"/>')
S.append('<path d="M122 144 Q130 116 151 111 Q171 116 183 144 M137 108 Q137 80 154 80 Q172 80 172 108" stroke="#71f5c9" fill="none" stroke-width="3" stroke-linecap="round"/>')
S.extend([txt(42,241,'HOSNA',29,'#f7fbff',750,False),txt(42,272,'GHOREISHIAMREI',18,'#c2d4e6',650),txt(42,303,'@'+USER,16,'#00e3aa'),line(42,325,260,325),txt(42,355,'01  /  IDENTITY',12,'#5e91b1',650),txt(42,390,'Computer Science',15),txt(42,413,'Brunel University London',14),txt(42,449,'London, United Kingdom',13,'#8ca5b9'),txt(42,478,'BSc · 2025–2028',13,'#8ca5b9'),line(42,504,260,504),txt(42,535,'02  /  STATUS',12,'#5e91b1',650),txt(42,569,'●  Building & learning',14,'#31e6ae'),txt(42,604,'Software Engineering',13),txt(42,628,'Artificial Intelligence',13),txt(42,652,'Full-stack Development',13),line(42,686,260,686),txt(42,721,'03  /  LINKS',12,'#5e91b1',650),txt(42,759,'github.com/'+USER,13,'#b8d2ff'),txt(42,798,'Open to opportunities',13,'#33e4ab'),txt(42,890,'BUILD • LEARN • CREATE',12,'#62acac',600)])
# top terminal
S.append(panel(300,22,960,124,'$ whoami'))
S.append(txt(321,83,'Computer Science undergraduate exploring software engineering and AI.',16,'#dce9f6'))
S.append(txt(321,112,'I build, experiment, solve problems, and keep learning. ▌',15,'#a6bacc'))
S.append(rect(1275,22,203,124,'#07111a','#254056'))
S.append(txt(1295,54,'●  ●  ●',15,'#00e6a8'))
S.append(txt(1295,89,'CODE / CREATE',15,'#f1f5f9',650))
S.append(txt(1295,115,'REPEAT  ↗',14,'#83a8c2'))
# metrics
metrics=[('PUBLIC REPOS',str(repo_count),'#00e7a5'),('REPO STARS',str(stars),'#518cff'),('FOLLOWERS',str(followers) if followers is not None else '—','#ac73ff'),('CONTRIBUTIONS',str(total) if total is not None else 'N/A','#00e7a5')]
for i,(label,value,col) in enumerate(metrics):
    x=300+i*298
    S.append(rect(x,161,285,104))
    S.append(txt(x+18,198,value,30,col,700))
    S.append(txt(x+18,238,label,13,'#a7bbce',650))
# calendar
S.append(panel(300,281,832,286,'CONTRIBUTION GRID  /  LAST 12 MONTHS'))
S.append(txt(1112,314,('LIVE' if counts else 'UNAVAILABLE'),12,('#00e7a5' if counts else '#f4b966'),650,anchor='end'))
# 52/53 weeks x 7 cells, fixed 12 px pitch
end=TODAY
start=end-datetime.timedelta(days=364)
start-=datetime.timedelta(days=(start.weekday()+1)%7) # Sunday start
weeks=math.ceil(((end-start).days+1)/7)
ox,oy,step=340,366,13.5
for i in range(weeks):
    for j in range(7):
        d=start+datetime.timedelta(days=i*7+j)
        if d>end:continue
        n=counts.get(d.isoformat(),0)
        if not counts: color='#172b36'
        elif n==0:color='#142a32'
        elif n==1:color='#145a4b'
        elif n<=3:color='#158666'
        elif n<=7:color='#21b884'
        else:color='#42f0b0'
        S.append(f'<rect x="{ox+i*step:.1f}" y="{oy+j*step:.1f}" width="10.5" height="10.5" rx="2" fill="{color}"/>')
for j,day in [(1,'MON'),(3,'WED'),(5,'FRI')]:S.append(txt(307,oy+j*step+9,day,10,'#718da4'))
if counts:
    for i in range(weeks):
        d=start+datetime.timedelta(days=i*7)
        if d.day<=7:S.append(txt(ox+i*step,348,d.strftime('%b').upper(),10,'#93abc1'))
    S.append(txt(341,527,f'{total:,} contributions over the past year',13,'#8faac0'))
else:
    S.append(txt(340,527,'Contribution calendar needs a working GitHub Actions token.',13,'#f0b96c'))
# focus
S.append(panel(1148,281,330,286,'CURRENT FOCUS'))
for i,s in enumerate(['Python & AI/ML','Full-stack web apps','Generative AI & LLMs','Software architecture','2027 placement prep']):
    y=367+i*38
    S.append(txt(1169,y,'›',21,'#00e7a5',700))
    S.append(txt(1190,y,s,14,'#d1e1ee'))
# language panel
S.append(panel(300,584,590,223,'LANGUAGE DISTRIBUTION'))
colors=['#4788ff','#9d65ec','#1ec28c','#f4d14f','#fa8d45','#ef5967','#6cd1ff']
top=langs.most_common(6)
if top:
    denom=sum(langs.values()) or 1
    for i,(name,val) in enumerate(top):
        y=632+i*26
        share=val/denom
        S.append(txt(321,y+4,name[:17],13,'#c9d8e6'))
        S.append(rect(472,y-9,287,10,'#132531','#132531',5))
        S.append(f'<rect x="472" y="{y-9}" width="{max(3,287*share):.1f}" height="10" rx="5" fill="{colors[i]}"/>')
        S.append(txt(866,y+4,f'{share*100:.1f}%',12,'#a8bed2',anchor='end'))
else:S.append(txt(322,660,'No public repository language data yet.',14))
S.append(txt(322,791,'Based on public repository code bytes · not proficiency',11,'#718da4'))
# account stats
S.append(panel(906,584,572,223,'ACCOUNT SNAPSHOT'))
for i,(label,value) in enumerate([('PUBLIC REPOSITORIES',str(repo_count)),('TOTAL PUBLIC STARS',str(stars)),('FOLLOWERS',str(followers) if followers is not None else '—'),('CONTRIBUTIONS / YEAR',str(total) if total is not None else 'N/A')]):
    x=926+(i%2)*269;y=634+(i//2)*80
    S.append(rect(x,y,250,68,'#0a1b27','#223b4c',9))
    S.append(txt(x+13,y+27,value,22,'#e7f4ff',700))
    S.append(txt(x+13,y+49,label,10,'#83a4bc',600))
# bottom
S.append(panel(300,824,1178,124,'TECH STACK  /  CURRENT TOOLBOX'))
for i,tool in enumerate(['Python','C++','Java','C#','JavaScript','HTML / CSS','SQL','Git','GitHub','VS Code']):
    x=321+i*114
    S.append(rect(x,868,104,49,'#0a1c28','#25465a',8))
    S.append(txt(x+52,898,tool,12,'#c9e5f4',600,anchor='middle'))
S.append(txt(1476,962,f'Updated {updated} UTC  •  GitHub public API',11,'#5e7e93',anchor='end'))
S.append('</svg>')
OUT.parent.mkdir(parents=True,exist_ok=True)
OUT.write_text(''.join(S),encoding='utf-8')
print(f'Wrote {OUT} ({OUT.stat().st_size:,} bytes)')
