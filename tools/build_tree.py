import json,glob,re,collections
T=json.load(open('tables.json'))
tx={}  # only for existence + outline
for f in glob.glob('RPG/Text_*_loc_kor.txt'):
    for l in open(f,encoding='utf-8-sig').read().split('\n'):
        l=l.rstrip('\r')
        if '\t' in l:
            k,v=l.split('\t',1); tx[k]=v
hero={h['id']:h['name'] for h in T['heroes']}
mob={m['id']:m['name'] for m in T['mobs']}
por={p['id']:p['name'] for p in T['portraits']}
def spk(pid):
    if pid<0: return None
    return por.get(pid) or hero.get(pid) or mob.get(pid)
by=collections.defaultdict(list)
for d in T['dialogs']: by[d['id']].append(d)
for k in by: by[k].sort(key=lambda d:d['order'])
P={}
def pos(t2,t3):
    if t2==11: return 'L'
    if t2==12: return 'R'
    return {3:'L',4:'R',5:'C'}.get(t3,'C')
def reg(pid):
    s=spk(pid)
    if s: P[str(pid)]=s
def parse(rows,i,stop):
    out=[]
    while i<len(rows):
        d=rows[i];t1,t2,t3=d['type1'],d['type2'],d['type3'];pid=d['portraitId'];key=d['text']
        if t1==5 and t2==51:
            if stop: return out,i
            i+=1;continue
        if t1==5 and t2==50:
            opts=[]
            while i<len(rows) and rows[i]['type1']==5 and rows[i]['type2']==50:
                opts.append(rows[i]['text']); i+=1
            brs=[[] for _ in opts]
            while i<len(rows) and rows[i]['type1']==5 and rows[i]['type2']==51:
                b=rows[i]['type3']
                if b==60: i+=1;break
                body,i=parse(rows,i+1,True)
                if 0<=b-55<len(brs): brs[b-55]=body
            out.append(['Q',opts,brs]);continue
        i+=1
        if t1==0: continue
        if t1==1:
            if t2 not in(0,1,-1) or key not in tx or not tx[key]: continue
            g=t3 if (t2==0 and t3 in(1,2)) else 0
            reg(pid); out.append(['T',pid,key,g])
        elif t1==2 and t2==1: out.append(['H',key])
        elif t1==3 and t2==1: out.append(['L',key])
        elif t1 in(4,23):
            if t2==1: out.append(['F',1,key,t3])
            elif t2==2: out.append(['F',0])
        elif t1==7:
            if t2==1 and d['strValue']: out.append(['B',d['strValue'],d['delay']])
        elif t1==6:
            if t2 in(1,11,12,13,14): out.append(['C',pid,pos(t2,t3)]); reg(pid)
            elif t2==2: out.append(['X',pid])
            elif t2==15: out.append(['XA'])
            elif t2==62: out.append(['E',pid,t3])
            elif t2==61: out.append(['M',pid,pos(0,t3)])
        elif t1==22 and t2==62: out.append(['E',pid,t3])
        elif t1==19 and t2==1 and t3>=100: out.append(['I',pid,t3])
        elif t1==13: out.append(['K',1 if t2==1 else 0])
        elif t1==9:
            sv=d['strValue']
            if t2==1 and sv: out.append(['G',sv,d['delay']])
            elif t2==69 and sv: out.append(['G',sv,d['delay'],1])
            elif t2==10:
                try: out.append(['GS',float(sv or 0)])
                except ValueError: out.append(['GS',0])
            elif t2==2: out.append(['GS',0])
            elif t2==9: out.append(['GA'])
        elif t1==14:
            sv=d['strValue']
            if t2==1 and sv: out.append(['S',sv,d['delay']])
            elif t2==2: out.append(['SX'])
        elif t1==10 and d['strValue']: out.append(['V',d['strValue']])
        elif t1==15 and t2 in(1,65): out.append(['Z',d['strValue']])
    return out,i
S={}
def story(did):
    rows=by.get(did)
    if not rows: return False
    if did in S: return True
    sm=''
    for d in rows:
        if d['type1']==0 and d['order']==0:
            t=tx.get(d['text'],'')
            if t and '추후 스토리' not in t: sm=d['text']
            break
    S[str(did)]={'sm':sm,'st':parse(rows,0,False)[0]}
    return True
def node(title,did,**kw): return dict({'title':title,'dialogId':did},**kw)
ch={c['id']:c['name'] for c in T['chapters']}
tree=[]
g=collections.defaultdict(list)
for s in sorted(T['mainStorySets'],key=lambda s:(s['chapterId'],s['order'])):
    if story(s['dialogId']): g[s['chapterId']].append(node(['@'+s['storyName']],s['dialogId'],order=s['order'],storyId=s['id']))
tree.append({'id':'main','label':'메인 스토리','children':[{'id':'chapter%d'%c,'title':['%d. '%c,'@'+ch[c]],'children':g[c]} for c in sorted(g)]})
reads=collections.defaultdict(list)
for r in T['subStoryReads']: reads[r['groupId']].append(r)
sg=[]
for ss in T['subStorys']:
    ch_=[node(['@'+r['storyName']],r['dialogId'],order=r['order']) for r in sorted(reads[ss['subStoryReadGroupId']],key=lambda r:r['order']) if story(r['dialogId'])]
    sg.append({'id':'sub%d'%ss['id'],'title':['@'+ss['name']],'children':ch_})
tree.append({'id':'sub','label':'서브 스토리','children':sg})
fg=collections.defaultdict(list)
for f in T['friendshipStorys']:
    if story(f['dialogId']): fg[f['id']//1000].append(node(['@'+f['storyName']],f['dialogId'],storyId=f['id']))
# FriendshipStory ids (id//1000) are NOT hero ids: heroes without friendship stories are skipped
# and later groups are shifted. Resolve the real hero per group from the SpeakText speakers.
def group_hero(g):
    c=collections.Counter()
    for n in fg[g]:
        for d in by[n['dialogId']]:
            if d['type1']==1 and 0<=d['portraitId']<1000 and d['portraitId'] in hero: c[d['portraitId']]+=1
    return g if c[g]>0 else c.most_common(1)[0][0]  # identity when the hero speaks in the group (covers alt-forms like 32), else main speaker
gmap={g:group_hero(g) for g in fg}
assert len(set(gmap.values()))==len(gmap),'duplicate hero among friendship groups'
fgh={}
for g,h in gmap.items(): fgh[h]=(g,fg[g])
print('friendship groups remapped (group->hero):',{g:(h,tx.get(hero[h])) for g,h in gmap.items() if g!=h})
print('heroes without friendship stories:',[(h,tx.get(hero[h])) for h in sorted(hero) if h not in fgh])
tree.append({'id':'fr','label':'호감도 스토리','children':[{'id':'hero%d'%h,'heroId':h,'friendshipGroup':fgh[h][0],'title':['@'+hero[h]],'children':fgh[h][1]} for h in sorted(fgh)]})
bl=[node(['@'+hero[b['id']],' 생일 (%d/%d)'%(b['month'],b['day'])] if b['id'] in hero else ['#%d'%b['id']],b['birthDayDialogId'],heroId=b['id']) for b in T['birthdays'] if story(b['birthDayDialogId'])]
# Birthday stories carry no Bg/BGM/Sound/Character-placement rows. Fixed resources (user-verified in game):
# Bg=BirthdayRoom, BGM=BirthDay, image BirthdayCake (horizontally centred, bottom-aligned), no Sound/Voice.
# BirthdayCharacterImage rows use portraitId -1 = the birthday hero (birthdays.id).
def _bd(st,h):
    return [['E',h,x[2]] if x[0]=='E' and x[1]==-1 else x for x in st]
for b in T['birthdays']:
    k=str(b['birthDayDialogId'])
    if k in S:
        reg(b['id'])
        S[k]['st']=[['B','BirthdayRoom',0],['G','BirthDay',0],['IM','BirthdayCake','C','B'],['C',b['id'],'C']]+_bd(S[k]['st'],b['id'])

tree.append({'id':'bd','label':'생일 스토리','children':[{'id':'birthday','title':['캐릭터 생일'],'children':bl}]})
used=set()
def walk(n):
    for c in n.get('children',[]):
        if 'dialogId' in c: used.add(c['dialogId'])
        else: walk(c)
for c in tree: walk(c)
stg=[];tut=[]
for did in sorted(by):
    if did in used: continue
    if story(did): (tut if did>=30000 else stg).append(node(['#%d'%did],did))
tree.append({'id':'etc','label':'기타','children':[x for x in [{'id':'stage','title':['스테이지·이벤트 대사'],'children':stg},{'id':'tutorial','title':['튜토리얼 등'],'children':tut}] if x['children']]})
tk=collections.defaultdict(list)
for t in T['talks']: tk[str(t['heroId'])].append([t['behaviour'],t['expressionID'],t['text']])
textfiles=['Text_Chapter','Text_MainStorySet','Text_SubStory','Text_SubStoryRead','Text_FriendshipStory','Text_Hero','Text_Mob','Text_Portrait','Text_Writer','Text_Dialog','Text_Talk']
tree_doc={'version':1,'textDir':'TextAsset/','lang':'kor','textFiles':[t+'_loc_{lang}.txt' for t in textfiles],
 'speakers':P,'heroes':{str(k):v for k,v in hero.items()},'tree':tree}
json.dump(tree_doc,open('story_tree.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
json.dump({'S':S,'talk':tk},open('story_scripts.json','w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
aud=collections.defaultdict(collections.Counter)
def aw(st,sid):
    for x in st:
        if x[0] in('G','S','V'): aud[{'G':'bgm','S':'sfx','V':'voice'}[x[0]]][x[1]]+=1
        elif x[0]=='Q':
            for b in x[2]: aw(b,sid)
for k,v in S.items(): aw(v['st'],k)
json.dump({'_note':'Names as written in dialog data (case differs in places, e.g. SFX_Ding / SFX_ding). Match audio files case-insensitively. bgm entries with dots (TalesRunner.*) come from PlayOneTime rows.',
 **{k:[{'name':n,'count':c,'key':n.lower()} for n,c in sorted(v.items(),key=lambda x:-x[1])] for k,v in aud.items()}},open('audio_names.json','w',encoding='utf-8'),ensure_ascii=False,indent=1)
# outline text
def rs(parts):
    return ''.join(tx.get(p[1:],p[1:]) if p.startswith('@') else p for p in parts)
o=[]
def ow(n,d):
    for c in n.get('children',[]):
        o.append('  '*d+(c['label'] if 'label' in c else rs(c['title']))+(' [dialogId=%d]'%c['dialogId'] if 'dialogId' in c else ''))
        ow(c,d+1)
for c in tree: o.append(c['label']); ow(c,1)
open('story_tree_outline.txt','w',encoding='utf-8').write('\n'.join(o))
import os
print({f:os.path.getsize(f) for f in ['story_tree.json','story_scripts.json','story_tree_outline.txt']},len(S))
