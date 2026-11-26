import re,json,collections
L=open('RPG/DictDatas.txt',encoding='utf-8',errors='replace').read().split('\n')
L=[l.rstrip('\r') for l in L]
# top-level table boundaries
tops=[(i,l.strip().split()[1]) for i,l in enumerate(L) if re.match(r'^\t[A-Za-z]+ [a-zA-Z]+\s*$',l)]
rng={}
for k,(i,n) in enumerate(tops):
    rng[n]=(i,tops[k+1][0] if k+1<len(tops) else len(L))
def records(name):
    a,b=rng[name]
    recs=[];cur=None
    # records start at depth 3 tabs "Dict... data"
    for l in L[a:b]:
        if re.match(r'^\t\t\t[A-Za-z0-9]+ data\s*$',l):
            cur={};recs.append(cur);continue
        m=re.match(r'^\t\t\t\t([A-Za-z0-9]+) (\w+) = (.*)$',l)
        if m and cur is not None:
            t,k,v=m.groups()
            if v.startswith('"'): v=v[1:-1]
            elif t in('float',): v=float(v)
            else:
                try:v=int(v)
                except:pass
            cur[k]=v
        # nested vector of dialogIds
        m2=re.match(r'^\t\t\t\t\t\t\t\[?\d*\]?\s*$',l)
        m3=re.match(r'^\t\t\t\t\t\t\tSInt16 data = (\-?\d+)',l)
        if m3 and cur is not None and name=='chapters': cur.setdefault('dialogIdsList',[]).append(int(m3.group(1)))
    return recs
out={}
for n in ['chapters','mainStorySets','subStorys','subStoryReads','friendshipStorys','portraits','heroes','mobs','writers','dialogs','talks','birthdays']:
    out[n]=records(n); print(n,len(out[n]), out[n][0] if out[n] else None)
json.dump(out,open('tables.json','w'),ensure_ascii=False)
