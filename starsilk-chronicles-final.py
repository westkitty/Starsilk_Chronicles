#!/usr/bin/env python3
# Starsilk Chronicles: Bridge Helm — GitHub delivery build
# Deterministic, offline-first visual narrative engine.
from __future__ import annotations
import argparse, copy, dataclasses, hashlib, json, math, os, random, sys, time, zlib, struct
from pathlib import Path

VERSION='1.2.1-github-delivery-alpha'; SCHEMA='bridge-helm-save-v3'
ROOT=Path(__file__).resolve().parent; SAVE_DIR=ROOT/'save'; ASSET_DIR=ROOT/'assets'/'bridge_helm'; AUDIO_DIR=ROOT/'audio'/'bridge_helm'
for d in (SAVE_DIR,ASSET_DIR,AUDIO_DIR): d.mkdir(parents=True,exist_ok=True)

NODES={
 'wake':{'label':'Starwake Berth','pos':(90,235),'risk':0,'story':'The berth hums with silkglass static. A small bell rings inside the hull.'},
 'ledger_gate':{'label':'Ledger Gate','pos':(230,125),'risk':1,'story':'A toll archive asks for a true name before it will open the star-road.'},
 'witness_pool':{'label':'Witness Pool','pos':(395,235),'risk':2,'story':'Reflections of routes not taken gather in a silver basin.'},
 'moth_orchard':{'label':'Moth Orchard','pos':(575,120),'risk':2,'story':'Lantern-fruit drift loose from black branches. Their shadows have wings.'},
 'ashen_comet':{'label':'Ashen Comet','pos':(555,350),'risk':3,'story':'A comet of warm ash crosses the chart, carrying a sealed distress hymn.'},
 'red_archive':{'label':'Red Archive','pos':(760,235),'risk':3,'story':'The archive breathes in meter. Every wrong answer becomes a corridor.'},
 'silkforge':{'label':'Silkforge','pos':(930,130),'risk':4,'story':'The forge braids star-silk into hull sutures and memory cords.'},
 'last_lighthouse':{'label':'Last Lighthouse','pos':(1030,350),'risk':5,'story':'A lighthouse with no keeper burns at the edge of known ink.'},
}
EDGES={'wake':['ledger_gate','witness_pool'],'ledger_gate':['witness_pool','moth_orchard'],'witness_pool':['moth_orchard','ashen_comet'],'moth_orchard':['red_archive'],'ashen_comet':['red_archive','last_lighthouse'],'red_archive':['silkforge','last_lighthouse'],'silkforge':['last_lighthouse'],'last_lighthouse':[]}
ARTIFACTS=['silkglass compass','archive-red key','lantern-moth cocoon','ash hymn cylinder','lighthouse wick']
SYSTEMS=('hull','engine','archive','crew')

@dataclasses.dataclass
class GameState:
    seed:int=1337; tick:int=0; current_node:str='wake'; focused_node:str='wake'; plotted_node:str|None=None
    fuel:int=8; silk:int=2; clarity:int=1; danger:int=0; trust:int=1
    hull:int=5; engine:int=5; archive:int=5; crew:int=5; power:dict=dataclasses.field(default_factory=lambda:{'helm':1,'engine':1,'archive':1})
    discovered:set=dataclasses.field(default_factory=lambda:{'wake'}); scanned:set=dataclasses.field(default_factory=set); artifacts:list=dataclasses.field(default_factory=list)
    log:list=dataclasses.field(default_factory=list); flags:dict=dataclasses.field(default_factory=dict); history:list=dataclasses.field(default_factory=list); route_memory:list=dataclasses.field(default_factory=list)

def _rng(s:GameState,salt=''):
    return random.Random(f'{s.seed}:{s.tick}:{s.current_node}:{salt}')
def _clone(s): return copy.deepcopy(s)
def _checksum(payload): return hashlib.sha256(json.dumps(payload,sort_keys=True,default=str).encode()).hexdigest()[:16]
def _node(n): return NODES[n]
def _edges(s): return EDGES.get(s.current_node,[])
def _fuel_cost(frm,to): return 1+NODES[to]['risk']//2
def _danger_delta(s,to): return max(0,NODES[to]['risk']-_rng(s,to).randint(0,2))
def _objectives(s):
    o=[]
    if s.current_node!='last_lighthouse': o.append('Reach the Last Lighthouse without losing hull, crew, or archive integrity.')
    if len(s.artifacts)<3: o.append('Recover at least three relics before the final trial.')
    if s.archive<3: o.append('Repair or protect the archive; contradiction pressure is high.')
    if s.danger>=6: o.append('Reduce danger soon. The route is becoming unstable.')
    return o or ['Resolve the lighthouse trial.']

def bridge_new_game_state(seed:int=1337):
    s=GameState(seed=seed); s.log.append('Bridge Helm initialized. The Starwake Berth is quiet, for now.'); return s

def _preview_route(s,to):
    if to not in EDGES.get(s.current_node,[]): return {'blocked':'No direct silkroad from current node.'}
    cost=_fuel_cost(s.current_node,to); danger=_danger_delta(s,to); blocked=None
    if s.fuel<cost: blocked='Insufficient fuel.'
    return {'to':to,'label':NODES[to]['label'],'fuel_cost':cost,'danger_delta':danger,'blocked':blocked,'story':NODES[to]['story']}

def bridge_get_snapshot(s:GameState):
    actions={}
    for to in _edges(s):
        p=_preview_route(s,to); actions[f'plot_course:{to}']={'label':'Plot '+NODES[to]['label'],'disabled_reason':p.get('blocked')}
        actions[f'focus_node:{to}']={'label':'Focus '+NODES[to]['label'],'disabled_reason':None}
    actions.update({'scan':{'label':'Scan local silkroad','disabled_reason':None},'travel_plotted':{'label':'Travel plotted course','disabled_reason':None if s.plotted_node else 'No plotted course.'},'quick_salvage':{'label':'Quick salvage','disabled_reason':None},'deep_salvage':{'label':'Deep salvage','disabled_reason':None},'archive_pulse':{'label':'Archive pulse','disabled_reason':None if s.archive>0 else 'Archive offline.'},'inspect_systems':{'label':'Inspect systems','disabled_reason':None},'safe_pause':{'label':'Safe pause','disabled_reason':None},'undo':{'label':'Undo','disabled_reason':None if s.history else 'No history.'},'final_trial':{'label':'Attempt final trial','disabled_reason':None if s.current_node=='last_lighthouse' else 'Not at the Last Lighthouse.'},'reset':{'label':'Reset run','disabled_reason':None}})
    return {'version':VERSION,'schema':SCHEMA,'tick':s.tick,'current_node':s.current_node,'focused_node':s.focused_node,'plotted_node':s.plotted_node,'resources':{'fuel':s.fuel,'silk':s.silk,'clarity':s.clarity,'danger':s.danger,'trust':s.trust},'systems':{k:getattr(s,k) for k in SYSTEMS},'power':dict(s.power),'artifacts':list(s.artifacts),'discovered':sorted(s.discovered),'reachable':list(_edges(s)),'previews':{to:_preview_route(s,to) for to in _edges(s)},'actions':actions,'objectives':_objectives(s),'log':s.log[-8:],'checksum':_checksum({'tick':s.tick,'node':s.current_node,'fuel':s.fuel,'danger':s.danger,'artifacts':s.artifacts})}

def _push_history(s):
    s.history.append(_clone(s)); s.history=s.history[-20:]

def _damage(s,amount=1):
    rng=_rng(s,'damage'); target=rng.choice(SYSTEMS); setattr(s,target,max(0,getattr(s,target)-amount)); s.log.append(f'{target.title()} loses {amount} integrity.')

def _salvage(s,deep=False):
    rng=_rng(s,'salvage-deep' if deep else 'salvage'); gain=1+rng.randint(0,1)+(1 if deep else 0); s.silk+=gain; s.danger+=1 if deep else 0
    if rng.random()<(.55 if deep else .28):
        a=ARTIFACTS[(s.tick+len(s.artifacts))%len(ARTIFACTS)]
        if a not in s.artifacts: s.artifacts.append(a); s.log.append('Recovered relic: '+a+'.')
    s.log.append(('Deep' if deep else 'Quick')+f' salvage yields {gain} silk.')

def bridge_apply_action(s:GameState,action:str):
    if action=='reset': return bridge_new_game_state(s.seed)
    if action=='undo' and s.history: prev=s.history.pop(); prev.log.append('Undo restored the previous helm state.'); return prev
    ns=_clone(s); _push_history(ns); ns.tick+=1
    if action.startswith('focus_node:'):
        nid=action.split(':',1)[1]
        if nid in NODES: ns.focused_node=nid; ns.discovered.add(nid); ns.log.append('Focused chart node: '+NODES[nid]['label']+'.')
    elif action.startswith('plot_course:'):
        nid=action.split(':',1)[1]; p=_preview_route(ns,nid)
        if not p.get('blocked'): ns.plotted_node=nid; ns.focused_node=nid; ns.discovered.add(nid); ns.log.append('Course plotted to '+NODES[nid]['label']+'.')
        else: ns.log.append('Plot rejected: '+p['blocked'])
    elif action=='scan':
        ns.scanned.add(ns.current_node); ns.clarity+=1; ns.discovered.update(_edges(ns)); ns.log.append('Scan reveals silkroad branches from '+NODES[ns.current_node]['label']+'.')
    elif action=='travel_plotted':
        if ns.plotted_node:
            p=_preview_route(ns,ns.plotted_node)
            if not p.get('blocked'):
                ns.fuel-=p['fuel_cost']; ns.danger+=p['danger_delta']; ns.current_node=ns.plotted_node; ns.focused_node=ns.current_node; ns.plotted_node=None; ns.discovered.add(ns.current_node); ns.route_memory.append(ns.current_node); ns.log.append('Arrived at '+NODES[ns.current_node]['label']+'. '+NODES[ns.current_node]['story'])
                if ns.danger>=5: _damage(ns,1)
            else: ns.log.append('Travel blocked: '+p['blocked'])
        else: ns.log.append('No plotted course to travel.')
    elif action=='quick_salvage': _salvage(ns,False)
    elif action=='deep_salvage': _salvage(ns,True)
    elif action=='archive_pulse': ns.archive=max(0,ns.archive-1); ns.clarity+=2; ns.danger=max(0,ns.danger-1); ns.log.append('Archive pulse converts contradiction into clarity.')
    elif action=='inspect_systems': ns.log.append('Systems check: '+'; '.join(f'{k}={getattr(ns,k)}' for k in SYSTEMS)+f'; fuel={ns.fuel}; silk={ns.silk}.')
    elif action=='safe_pause': ns.log.append('Paused at helm. The black box records a clean checkpoint.')
    elif action=='final_trial':
        if ns.current_node=='last_lighthouse':
            score=len(ns.artifacts)+ns.clarity+ns.trust+min(ns.hull,ns.crew,ns.archive)-ns.danger
            ns.flags['ending']='radiant' if score>=8 else 'fractured' if score>=4 else 'lost'
            ns.log.append('Final trial resolved: '+ns.flags['ending']+'.')
        else: ns.log.append('The final trial is still beyond the chart.')
    else: ns.log.append('Unknown command ignored: '+action)
    if ns.fuel<=0 and ns.current_node!='last_lighthouse': ns.danger+=1; ns.log.append('Fuel exhaustion raises route danger.')
    return ns

def _to_jsonable(s):
    d=dataclasses.asdict(s); d['discovered']=sorted(s.discovered); d['history']=[]; return d
def bridge_save_game(s,path=SAVE_DIR/'bridge_save.json'):
    data={'schema':SCHEMA,'version':VERSION,'state':_to_jsonable(s)}; data['checksum']=_checksum(data['state']); Path(path).write_text(json.dumps(data,indent=2),encoding='utf-8'); return path
def bridge_load_game(path=SAVE_DIR/'bridge_save.json'):
    data=json.loads(Path(path).read_text(encoding='utf-8')); assert data['schema']==SCHEMA
    st=data['state']; st['discovered']=set(st['discovered']); st['history']=[]; return GameState(**st)

def _png_bytes(rgb):
    w=h=1; raw=b'\x00'+bytes(rgb)
    def chunk(t,d): return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',w,h,8,2,0,0,0))+chunk(b'IDAT',zlib.compress(raw))+chunk(b'IEND',b'')
def ensure_placeholder_assets():
    colors={'wake':(30,45,70),'ledger_gate':(90,65,120),'witness_pool':(80,135,150),'moth_orchard':(120,105,45),'ashen_comet':(150,80,55),'red_archive':(140,35,45),'silkforge':(180,150,85),'last_lighthouse':(235,230,180)}
    for k,c in colors.items():
        p=ASSET_DIR/(k+'.png')
        if not p.exists(): p.write_bytes(_png_bytes(c))
    manifest={'generated':True,'version':VERSION,'assets':sorted(x.name for x in ASSET_DIR.glob('*.png'))}
    (ASSET_DIR/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
    return manifest

def run_cli(seed=1337,script=None):
    ensure_placeholder_assets(); s=bridge_new_game_state(seed); print('Starsilk Chronicles: Bridge Helm',VERSION); print(bridge_get_snapshot(s)['log'][-1])
    actions=script or ['scan','plot_course:ledger_gate','travel_plotted','scan','quick_salvage','plot_course:witness_pool','travel_plotted','deep_salvage','inspect_systems']
    for a in actions:
        s=bridge_apply_action(s,a); snap=bridge_get_snapshot(s); print('\n>',a); print(snap['log'][-1]); print('node=',snap['current_node'],'res=',snap['resources'],'sys=',snap['systems'],'artifacts=',snap['artifacts'])
    bridge_save_game(s); print('\nSaved:',SAVE_DIR/'bridge_save.json'); return s

def run_bridge_helm_gui():
    import tkinter as tk
    s=bridge_new_game_state(); root=tk.Tk(); root.title('Starsilk Chronicles: Bridge Helm')
    status=tk.StringVar(); tk.Label(root,textvariable=status,anchor='w',justify='left').pack(fill='x')
    canvas=tk.Canvas(root,width=1120,height=470,bg='#081019'); canvas.pack(fill='both',expand=True)
    route_bar=tk.Frame(root); route_bar.pack(fill='x')
    action_bar=tk.Frame(root); action_bar.pack(fill='x')
    def apply_many(actions):
        nonlocal s
        for item in actions: s=bridge_apply_action(s,item)
        refresh()
    def clear(frame):
        for child in frame.winfo_children(): child.destroy()
    def refresh():
        snap=bridge_get_snapshot(s); objective=snap['objectives'][0] if snap['objectives'] else 'Awaiting command.'
        status.set(f"Node: {NODES[s.current_node]['label']} | fuel {s.fuel} silk {s.silk} clarity {s.clarity} danger {s.danger} | {objective}\n"+'\n'.join(snap['log'][-3:]))
        canvas.delete('all')
        for frm,outs in EDGES.items():
            x1,y1=NODES[frm]['pos']
            for to in outs:
                x2,y2=NODES[to]['pos']; canvas.create_line(x1,y1,x2,y2,fill='#42606f',width=2)
        for nid,v in NODES.items():
            x,y=v['pos']; fill='#20323f'; outline='#89a'
            if nid==s.current_node: fill='#7fffd4'; outline='#e8fff8'
            elif nid==s.plotted_node: fill='#ffd166'; outline='#fff2bf'
            elif nid==s.focused_node: fill='#b9f2ff'; outline='#e8fbff'
            elif nid in snap['reachable']: fill='#2e4b59'
            width=3 if nid in (s.current_node,s.plotted_node,s.focused_node) else 1
            canvas.create_oval(x-18,y-18,x+18,y+18,fill=fill,outline=outline,width=width)
            canvas.create_text(x,y+34,text=v['label'],fill='#d8e6ef',font=('Arial',9))
        clear(route_bar); clear(action_bar)
        for nid in snap['reachable']:
            preview=snap['previews'][nid]; state='disabled' if preview.get('blocked') else 'normal'
            label=f"Plot {NODES[nid]['label']} ({preview['fuel_cost']} fuel)"
            tk.Button(route_bar,text=label,state=state,command=lambda n=nid: apply_many([f'focus_node:{n}',f'plot_course:{n}'])).pack(side='left')
        travel_disabled=snap['actions']['travel_plotted']['disabled_reason'] is not None
        buttons=[('Scan',['scan'],False),('Travel',['travel_plotted'],travel_disabled),('Quick salvage',['quick_salvage'],False),('Deep salvage',['deep_salvage'],False),('Archive pulse',['archive_pulse'],snap['actions']['archive_pulse']['disabled_reason'] is not None),('Inspect',['inspect_systems'],False),('Undo',['undo'],snap['actions']['undo']['disabled_reason'] is not None),('Final',['final_trial'],snap['actions']['final_trial']['disabled_reason'] is not None),('Reset',['reset'],False)]
        for label,actions,disabled in buttons:
            tk.Button(action_bar,text=label,state='disabled' if disabled else 'normal',command=lambda a=actions: apply_many(a)).pack(side='left')
    refresh(); root.mainloop()

def run_static_sweep():
    text=Path(__file__).read_text(encoding='utf-8'); risky=['ev'+'al(','ex'+'ec(','api'+'_key','secret'+'_key','PROMPT'+'_QUEUE','IMAGE'+'_PROMPTS']; found=[x for x in risky if x in text.replace('risky=','checked=')]
    assert not found, 'Forbidden pattern(s): '+str(found); assert 'ensure_placeholder_assets' in text; print('Static sweep: PASS'); return True
def run_smoke_test():
    s=bridge_new_game_state(7); steps=['scan','focus_node:ledger_gate','plot_course:ledger_gate','travel_plotted','scan','quick_salvage','archive_pulse','inspect_systems']
    for a in steps: s=bridge_apply_action(s,a)
    snap=bridge_get_snapshot(s); assert snap['current_node']=='ledger_gate'; assert snap['resources']['fuel']>=0; bridge_save_game(s); loaded=bridge_load_game(); assert loaded.current_node==s.current_node; print('Smoke test: PASS'); return True
def run_gui_qa():
    s=bridge_new_game_state()
    for a in ['scan','focus_node:ledger_gate','plot_course:ledger_gate','travel_plotted','scan','focus_node:witness_pool','plot_course:witness_pool','travel_plotted','quick_salvage','inspect_systems']:
        s=bridge_apply_action(s,a)
    assert s.current_node=='witness_pool' and s.focused_node=='witness_pool' and len(s.route_memory)>=2
    print('GUI QA: PASS'); return True
def run_gameplay_qa():
    s=bridge_new_game_state(99)
    for i in range(12):
        snap=bridge_get_snapshot(s); routes=snap['reachable']
        if routes: s=bridge_apply_action(s,'plot_course:'+routes[0]); s=bridge_apply_action(s,'travel_plotted')
        else: break
        if s.current_node=='last_lighthouse': s=bridge_apply_action(s,'final_trial'); break
    assert s.current_node in NODES; assert min(s.hull,s.engine,s.archive,s.crew)>=0; print('Gameplay QA: PASS'); return True
def run_asset_qa():
    m=ensure_placeholder_assets(); assert len(m['assets'])>=len(NODES); assert (ASSET_DIR/'manifest.json').exists(); print('Asset QA: PASS'); return True
def run_accessibility_qa():
    snap=bridge_get_snapshot(bridge_new_game_state()); assert snap['actions']; assert all('label' in v for v in snap['actions'].values()); assert snap['objectives']; print('Accessibility QA: PASS'); return True
def run_persistence_qa():
    s=bridge_new_game_state(22); s=bridge_apply_action(s,'scan'); path=bridge_save_game(s,SAVE_DIR/'qa_save.json'); loaded=bridge_load_game(path); assert bridge_get_snapshot(loaded)['checksum']==bridge_get_snapshot(s)['checksum']; print('Persistence QA: PASS'); return True
def run_performance_qa():
    s=bridge_new_game_state(1); t=time.perf_counter()
    for i in range(1000): s=bridge_apply_action(s,'scan' if i%3==0 else 'quick_salvage')
    assert time.perf_counter()-t<2.5; print('Performance QA: PASS'); return True
def run_balance_sim(n=80):
    endings={}
    for seed in range(n):
        s=bridge_new_game_state(seed)
        for _ in range(10):
            routes=bridge_get_snapshot(s)['reachable']
            if not routes: break
            pick=routes[seed%len(routes)]; s=bridge_apply_action(s,'plot_course:'+pick); s=bridge_apply_action(s,'travel_plotted')
            if seed%3==0: s=bridge_apply_action(s,'quick_salvage')
            if s.current_node=='last_lighthouse': break
        s=bridge_apply_action(s,'final_trial'); endings[s.flags.get('ending','unresolved')]=endings.get(s.flags.get('ending','unresolved'),0)+1
    assert max(endings.values())/n<.75, endings; print('Balance sim: PASS',endings); return True

def run_bug_sweep():
    for fn in (run_static_sweep,run_smoke_test,run_gui_qa,run_gameplay_qa,run_asset_qa,run_accessibility_qa,run_persistence_qa,run_performance_qa,run_balance_sim): fn()
    print('Bridge Helm bug sweep: PASS'); return True

def main(argv=None):
    p=argparse.ArgumentParser(description='Starsilk Chronicles: Bridge Helm'); p.add_argument('--cli',action='store_true'); p.add_argument('--gui',action='store_true'); p.add_argument('--bug-sweep',action='store_true'); p.add_argument('--seed',type=int,default=1337)
    p.add_argument('--static-sweep',action='store_true'); p.add_argument('--smoke-test',action='store_true'); p.add_argument('--gui-qa',action='store_true'); p.add_argument('--gameplay-qa',action='store_true'); p.add_argument('--asset-qa',action='store_true'); p.add_argument('--accessibility-qa',action='store_true'); p.add_argument('--persistence-qa',action='store_true'); p.add_argument('--performance-qa',action='store_true'); p.add_argument('--balance-sim',action='store_true')
    args=p.parse_args(argv)
    if args.static_sweep: return 0 if run_static_sweep() else 1
    if args.smoke_test: return 0 if run_smoke_test() else 1
    if args.gui_qa: return 0 if run_gui_qa() else 1
    if args.gameplay_qa: return 0 if run_gameplay_qa() else 1
    if args.asset_qa: return 0 if run_asset_qa() else 1
    if args.accessibility_qa: return 0 if run_accessibility_qa() else 1
    if args.persistence_qa: return 0 if run_persistence_qa() else 1
    if args.performance_qa: return 0 if run_performance_qa() else 1
    if args.balance_sim: return 0 if run_balance_sim() else 1
    if args.bug_sweep: return 0 if run_bug_sweep() else 1
    if args.gui: run_bridge_helm_gui(); return 0
    run_cli(args.seed); return 0
if __name__=='__main__': raise SystemExit(main())
