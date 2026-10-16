#!/usr/bin/env python3
"""Generate a GitHub profile dashboard from GitHub APIs. No third-party packages."""
import os, json, html, datetime as dt, urllib.request, urllib.parse
from pathlib import Path
USER='Hosnaa-gh'
TOKEN=os.environ.get('GH_TOKEN','')
HEAD={'Accept':'application/vnd.github+json','User-Agent':'profile-dashboard','X-GitHub-Api-Version':'2022-11-28'}
if TOKEN: HEAD['Authorization']='Bearer '+TOKEN

def api(url,body=None):
    req=urllib.request.Request(url,headers=HEAD,data=json.dumps(body).encode() if body else None)
    if body:req.add_header('Content-Type','application/json')
    with urllib.request.urlopen(req,timeout=30) as res:return json.load(res)

def esc(s):return html.escape(str(s),quote=True)

def text(x,y,s,size=16,color='#d8e8e5',weight='normal',anchor=None):
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="{size}" font-weight="{weight}"'+(f' text-anchor="{anchor}"' if anchor else '')+f'>{esc(s)}</text>'

user=api(f'https://api.github.com/users/{USER}')
repos=[]; page=1
while True:
    batch=api(f'https://api.github.com/users/{USER}/repos?type=owner&per_page=100&page={page}')
    repos+=batch
    if len(batch)<100:break
    page+=1
    if page>30:raise RuntimeError('Too many pages')
public_repos=user['public_repos']; followers=user['followers']; following=user['following']
stars=sum(r.get('stargazers_count',0) for r in repos if not r.get('fork'))
forks=sum(r.get('forks_count',0) for r in repos if not r.get('fork'))
lang_counts={}
for r in repos:
    if r.get('fork'):continue
    try:
        for k,v in api(r['languages_url']).items():lang_counts[k]=lang_counts.get(k,0)+v
    except Exception as e:print('Language API warning:',e)
langs=sorted(lang_counts.items(),key=lambda v:-v[1])[:7]

def search_count(q):
    try:return api('https://api.github.com/search/issues?q='+urllib.parse.quote(q))['total_count']
    except Exception as e:print('Search warning:',e);return None
prs=search_count('author:'+USER+' type:pr'); issues=search_count('author:'+USER+' type:issue')
# Contribution calendar and annual commit contributions are fetched via official GraphQL API.
calendar=None; commits=None; total=None
if TOKEN:
    query="query($login:String!){user(login:$login){contributionsCollection{totalCommitContributions contributionCalendar{totalContributions weeks{contributionDays{date contributionCount color}}}}}}"
    try:
        response=api('https://api.github.com/graphql',{'query':query,'variables':{'login':USER}})
        collection=response['data']['user']['contributionsCollection'];commits=collection['totalCommitContributions']
        calendar=collection['contributionCalendar']['weeks'];total=collection['contributionCalendar']['totalContributions']
    except Exception as e:print('Calendar warning:',e)

W=1000; H=760
out=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
'<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#101b22"/><stop offset="1" stop-color="#0a151b"/></linearGradient></defs>',
'<rect width="1000" height="760" rx="22" fill="url(#bg)"/>','<rect x="1" y="1" width="998" height="758" rx="21" fill="none" stroke="#314f50"/>',
text(32,48,'DEVELOPER ACTIVITY',25,'#b8f1d7','bold'),text(968,47,'@'+USER,16,'#88a8a5',anchor='end'),
'<path d="M32 66H968" stroke="#2c4548"/>',text(32,100,'PROFILE SNAPSHOT',13,'#86a8a7','bold')]
metrics=[('Repositories',public_repos),('Stars received',stars),('Followers',followers),('Following',following),('Forks received',forks)]
for i,(name,val) in enumerate(metrics):
    x=32+i*191
    out += [f'<rect x="{x}" y="116" width="178" height="107" rx="11" fill="#14262c" stroke="#29444a"/>',text(x+14,159,val,33,'#a4edca','bold'),text(x+14,193,name,14,'#b9cece')]
out += [text(32,265,'CONTRIBUTIONS · LAST 12 MONTHS',18,'#e2f3ed','bold')]
if calendar:
    weeks=calendar[-53:]; day_w=12; day_gap=4
    for wi,week in enumerate(weeks):
        for di,day in enumerate(week['contributionDays']):
            c=day['contributionCount']; color='#23343a' if c==0 else ('#376f60' if c<3 else '#4ba98a' if c<7 else '#8ce2ae')
            out.append(f'<rect x="{32+wi*(day_w+day_gap)}" y="{292+di*17}" width="12" height="12" rx="2" fill="{color}"><title>{esc(day["date"])}: {c} contributions</title></rect>')
    out.append(text(968,268,f'{total} contributions in the last year',13,'#a4edca',anchor='end'))
else:
    out.append(text(34,325,'Calendar unavailable — check Actions permissions / API access',17,'#f1c7a6'))
out += ['<path d="M32 438H968" stroke="#2c4548"/>',text(32,473,'LANGUAGES · PUBLIC REPOSITORIES',18,'#e2f3ed','bold')]
colors=['#a4edca','#65a5df','#df8fb7','#f1bf73','#9e93ee','#7ac2c6','#d2d9e2']
if langs:
    total_bytes=sum(n for _,n in langs)
    start=32
    for i,(_,num) in enumerate(langs):
        width=936*num/total_bytes
        out.append(f'<rect x="{start:.2f}" y="495" width="{width:.2f}" height="18" fill="{colors[i]}"/>');start+=width
    for i,(name,n) in enumerate(langs):
        x=32+(i%4)*239;y=551+(i//4)*36
        out += [f'<circle cx="{x+6}" cy="{y-5}" r="6" fill="{colors[i]}"/>',text(x+20,y,f'{name}  {n/total_bytes:.0%}',15,'#c9dddc')]
else:out.append(text(32,520,'No language data returned',16))
out += ['<path d="M32 632H968" stroke="#2c4548"/>',text(32,665,'PUBLIC ACTIVITY',18,'#e2f3ed','bold')]
items=[('Pull requests opened',prs),('Issues opened',issues),('Commits in past year',commits)]
for i,(label,val) in enumerate(items):
    x=32+i*320
    out += [text(x,704,'—' if val is None else val,27,'#a4edca','bold'),text(x+48,704,label,14,'#c9dddc')]
updated=dt.datetime.now(dt.timezone.utc).strftime('%d %b %Y · %H:%M UTC')
out += [text(968,743,'Updated '+updated,12,'#729392',anchor='end'),'</svg>']
Path('assets').mkdir(exist_ok=True)
Path('assets/developer-dashboard.svg').write_text('\n'.join(out),encoding='utf-8')
print('Dashboard updated:',public_repos,stars,followers,'calendar available:',bool(calendar))
