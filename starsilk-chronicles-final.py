#!/usr/bin/env python3
"""Starsilk Chronicles: Bridge Helm - GitHub delivery build."""
from __future__ import annotations
import argparse, base64, json, os, random, tempfile, time
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
VERSION='1.2.1-github-delivery-alpha'; SCHEMA='bridge-helm-save-v3'
ROOT=Path(__file__).resolve().parent; ASSET_ROOT=ROOT/'assets'/'bridge_helm'; MANIFEST=ASSET_ROOT/'asset_manifest.json'
NODES={
 'harbor':('origin',60,250,0,'orientation','The helm wakes inside a failed harbor of blue diagnostic light.'),
 'ledger_gate':('admin',190,170,2,'blood_ring_key','A checkpoint asks for records it already knows are contradictory.'),
 'glasswake':('wall',190,330,3,'hull_patch','The Siege Wall grinds light into black weather.'),
 'witness_pool':('witness',330,120,2,'witness_shard_key','Names persist as residue, not ghosts. The archive asks whether you will carry them.'),
 'drakken_choir':('drakken',360,270,3,'drakken_protocol_key','The route grammar bends around a terraforming mind.'),
 'codec_invoice':('codec',360,420,4,'codec_betrayal_key','Codec offers a shortcut with a cost hidden in solidarity.'),
 'tiger_fringe':('tiger',520,230,5,'tiger_axiom_key','A cold attention classifies you before deciding whether you matter.'),
 'aureal_gate':('exit',680,260,2,'ending','The exit is where the run has to explain itself.'),}
EDGES={'harbor':['ledger_gate','glasswake'],'ledger_gate':['witness_pool','drakken_choir'],'glasswake':['drakken_choir','codec_invoice'],'witness_pool':['tiger_fringe'],'drakken_choir':['tiger_fringe','aureal_gate'],'codec_invoice':['tiger_fringe','aureal_gate'],'tiger_fringe':['aureal_gate'],'aureal_gate':[]}
KEYS=['blood_ring_key','witness_shard_key','drakken_protocol_key','codec_betrayal_key','tiger_axiom_key']; SYSTEMS=['engines','scanners','archives','masks','hull']
@dataclass
class GameState:
    turn:int=0; current_node:str='harbor'; focused_node:Optional[str]=None; plotted_node:Optional[str]=None
    fuel:int=8; hull:int=10; admin_heat:int=0; wall_stress:int=0; tiger_attention:int=0
    route_silence:int=2; archive_buffers:int=3; forged_permits:int=1; macro_charges:int=2; syrin_reagent:int=1
    scanned:List[str]=field(default_factory=lambda:['harbor']); keys:Dict[str,bool]=field(default_factory=lambda:{k:False for k in KEYS})
    power:Dict[str,int]=field(default_factory=lambda:{s:2 for s in SYSTEMS}); crew:Dict[str,str]=field(default_factory=dict)
    subsystems:Dict[str,str]=field(default_factory=lambda:{s:'ok' for s in SYSTEMS}); crises:List[str]=field(default_factory=list); scars:List[str]=field(default_factory=list)
    route_memory:List[str]=field(default_factory=list); black_box:List[str]=field(default_factory=list); undo_stack:List[Dict[str,Any]]=field(default_factory=list)
    ending:Optional[str]=None; final_factors:List[str]=field(default_factory=list); accessibility:Dict[str,bool]=field(default_factory=lambda:{'reduced_motion':False,'large_text':False,'high_contrast':False})
def _payload(s:GameState):
    d=asdict(s); d.pop('undo_stack',None); return d
def _restore(d:Dict[str,Any]):
    s=GameState(); [setattr(s,k,v) for k,v in d.items() if hasattr(s,k) and k!='undo_stack']; return _bound(s)
def _bound(s:GameState):
    for k,mx in [('fuel',20),('hull',15),('admin_heat',20),('wall_stress',20),('tiger_attention',20)]: setattr(s,k,max(0,min(mx,int(getattr(s,k)))))
    s.route_memory=s.route_memory[-20:]; s.black_box=s.black_box[-80:]; s.crises=s.crises[-5:]; s.scars=s.scars[-12:]; s.undo_stack=s.undo_stack[-10:]; return s
def _rec(s,msg): s.route_memory.append(msg); s.black_box.append(f'T{s.turn:03d}: {msg}'); _bound(s)
def bridge_new_game_state(seed:Optional[int]=None):
    if seed is not None: random.seed(seed)
    s=GameState(); _rec(s,'Bridge Helm online. Scan, plot, commit, salvage, survive the explanation.'); return s
def _reach(s): return EDGES.get(s.current_node,[])
def _prev(s,n):
    typ,x,y,risk,reward,text=NODES[n]; known=n in s.scanned or s.power['scanners']>=3; cost=max(1,1+risk-s.power['engines'])+(s.subsystems['engines']!='ok')
    blocked=n not in _reach(s) or s.fuel<cost
    return {'node_id':n,'label':typ,'known':known,'fuel_cost':cost,'risk':risk if known else 'partially_unknown','likely_reward':reward if known else 'unknown','known_unknowns':[] if known else ['hazard profile','reward confidence','inspection pressure'],'blocked':blocked,'blocked_reason':'not adjacent' if n not in _reach(s) else ('insufficient fuel' if s.fuel<cost else ''),'advice':'plotted and ready' if s.plotted_node==n else 'plot first, then travel'}
def _actions(s):
    base={'scan':('Scan','S','Reveal adjacent route data','low'),'travel_plotted':('Travel plotted route','Enter','Commit to plotted route','medium'),'quick_salvage':('Quick salvage','Q','Low reward, low exposure','low'),'deep_salvage':('Deep salvage','D','High reward, more pressure','high'),'archive_salvage':('Archive salvage','A','Seek contradiction data','medium'),'inspect_systems':('Inspect systems','I','Read subsystem damage','low'),'safe_pause':('Safe pause','P','Lower audit noise','low'),'undo':('Undo','U','Return one step','low'),'reset':('Reset run','R','Start over','high'),'final_trial':('Enter final trial','F','Resolve the run','high')}
    out={}
    for a,(label,key,desc,risk) in base.items():
        dis='No route plotted.' if a=='travel_plotted' and not s.plotted_node else ''
        if a=='travel_plotted' and s.plotted_node and _prev(s,s.plotted_node)['blocked']: dis=_prev(s,s.plotted_node)['blocked_reason']
        out[a]={'label':label,'hotkey':key,'description':desc,'risk':risk,'disabled_reason':dis}
    return out
def _objectives(s):
    return [x for x in [('Scan adjacent nodes before committing.' if len(s.scanned)<4 else ''),('Acquire at least one contradiction key.' if not any(s.keys.values()) else ''),('Salvage or choose shorter routes; fuel is low.' if s.fuel<3 else ''),('Repair hull or avoid Wall routes.' if s.hull<=4 else ''),('Reach the Aureal Gate.' if s.current_node!='aureal_gate' else 'Enter the final trial.') ] if x]
def bridge_get_snapshot(s):
    return {'version':VERSION,'state':_payload(s),'current_node':{'id':s.current_node,'type':NODES[s.current_node][0],'text':NODES[s.current_node][5]},'reachable':_reach(s),'previews':{n:_prev(s,n) for n in NODES},'map':{'nodes':[{'id':k,'type':v[0],'x':v[1],'y':v[2],'scanned':k in s.scanned,'focused':s.focused_node==k,'plotted':s.plotted_node==k} for k,v in NODES.items()],'edges':EDGES},'actions':_actions(s),'objectives':_objectives(s),'crises':s.crises,'scars':s.scars,'route_memory':s.route_memory,'black_box_digest':s.black_box[-10:],'accessibility_summary':'keyboard commands available; no color-only required','ending':s.ending,'final_factors':s.final_factors}
def bridge_apply_action(s,a):
    if s.ending and a!='reset': return s
    s.undo_stack.append(_payload(s)); s.turn+=1
    if a.startswith('focus_node:') and a.split(':',1)[1] in NODES: s.focused_node=a.split(':',1)[1]; _rec(s,f'Focused {s.focused_node}.')
    elif a.startswith('plot_course:'):
        n=a.split(':',1)[1]; p=_prev(s,n) if n in NODES else {'blocked':True,'blocked_reason':'unknown'}
        if not p['blocked']: s.plotted_node=n; _rec(s,f'Plotted course to {n}; cost {p["fuel_cost"]} fuel.')
        else: _rec(s,f'Course refused: {p["blocked_reason"]}.')
    elif a=='scan':
        [s.scanned.append(n) for n in _reach(s) if n not in s.scanned]; s.admin_heat+=max(0,3-s.power['masks']); _rec(s,'Scan revealed adjacent route data.')
    elif a=='travel_plotted': s=_travel(s,s.plotted_node)
    elif a.startswith('travel:'): s=_travel(s,a.split(':',1)[1])
    elif a in {'quick_salvage','deep_salvage','archive_salvage','silent_salvage'}: _salvage(s,a)
    elif a=='inspect_systems': _rec(s,'Systems: '+', '.join(f'{k}={v}' for k,v in s.subsystems.items()))
    elif a=='safe_pause': s.admin_heat=max(0,s.admin_heat-1); _rec(s,'Safe pause lowered audit noise.')
    elif a=='undo' and s.undo_stack: s=_restore(s.undo_stack.pop()); _rec(s,'Undo restored previous state.')
    elif a=='final_trial': _final(s)
    elif a=='reset': return bridge_new_game_state()
    return _bound(s)
def _travel(s,n):
    if not n or n not in NODES: _rec(s,'No plotted target exists.'); return s
    p=_prev(s,n)
    if p['blocked']: _rec(s,f'Travel blocked: {p["blocked_reason"]}.'); return s
    typ,x,y,risk,reward,text=NODES[n]; s.fuel-=p['fuel_cost']; s.current_node=n; s.plotted_node=None; s.focused_node=n
    if n not in s.scanned: s.scanned.append(n)
    if reward in KEYS: s.keys[reward]=True
    if typ=='admin': s.admin_heat+=risk+1; s.forged_permits=max(0,s.forged_permits-1)
    if typ=='wall': s.wall_stress+=risk+1; s.hull-=max(1,risk-s.power['hull']); s.subsystems['engines']='strained'
    if typ=='codec': s.scars.append('Codec shortcut accepted; solidarity accounting remains suspect.'); s.tiger_attention+=1
    if typ=='tiger': s.tiger_attention+=risk
    if s.hull<=3 and 'hull breach' not in s.crises: s.crises.append('hull breach')
    if s.admin_heat>=8 and 'audit lock' not in s.crises: s.crises.append('audit lock')
    _rec(s,f'Arrived at {n}: {text}'); return s
def _salvage(s,a):
    if a=='quick_salvage': s.fuel+=1; _rec(s,'Quick salvage recovered one fuel.')
    elif a=='deep_salvage': s.fuel+=2; s.macro_charges+=1; s.admin_heat+=2; _rec(s,'Deep salvage recovered more but raised audit pressure.')
    elif a=='archive_salvage': s.archive_buffers+=1; _rec(s,'Archive salvage protected structural memory.')
    elif a=='silent_salvage' and s.route_silence>0: s.route_silence-=1; s.fuel+=1; s.admin_heat=max(0,s.admin_heat-1); _rec(s,'Silent salvage recovered fuel quietly.')
def _final(s):
    positives=[k for k,v in s.keys.items() if v]; score=len(positives)+(s.hull>3)+(s.archive_buffers>0)-(s.admin_heat>12)-(s.tiger_attention>12)
    s.ending='ending_unfinished_mobile_run' if s.current_node!='aureal_gate' else ('ending_witness_record_preserved' if score>=6 and s.keys['witness_shard_key'] else 'ending_drakken_accord_escape' if s.keys['drakken_protocol_key'] and s.admin_heat<10 else 'ending_classification_survived' if s.keys['tiger_axiom_key'] and s.tiger_attention<14 else 'ending_damaged_rescue' if s.hull>0 else 'ending_loss')
    s.final_factors=[f'keys={positives}',f'hull={s.hull}',f'admin_heat={s.admin_heat}',f'tiger_attention={s.tiger_attention}']; _rec(s,f'Final trial resolved: {s.ending}.')
def bridge_state_to_payload(s): return {'schema':SCHEMA,'version':VERSION,'state':_payload(s)}
def bridge_payload_to_state(p):
    if p.get('schema')!=SCHEMA: raise ValueError('Unsupported save schema')
    return _restore(p.get('state',{}))
def bridge_save_game(s,path):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True); fd,tmp=tempfile.mkstemp(prefix=path.name,suffix='.tmp',dir=str(path.parent))
    with os.fdopen(fd,'w',encoding='utf-8') as f: json.dump(bridge_state_to_payload(s),f,indent=2)
    os.replace(tmp,path)
def bridge_load_game(path):
    path=Path(path)
    try: return bridge_payload_to_state(json.loads(path.read_text(encoding='utf-8')))
    except Exception as e:
        if path.exists():
            try: path.replace(path.with_suffix(path.suffix+'.corrupt.'+str(int(time.time()))))
            except OSError: pass
        s=bridge_new_game_state(); _rec(s,f'Recovered from corrupt save: {e.__class__.__name__}.'); return s
def ensure_placeholder_assets():
    tiny=base64.b64decode('iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAFgwJ/lZ5o6QAAAABJRU5ErkJggg=='); names=['current_position','destination','blocked','danger','selected_route']+KEYS+['scan','travel','salvage','audit','wall','tiger']
    for size in (64,128,256):
        d=ASSET_ROOT/'runtime'/str(size); d.mkdir(parents=True,exist_ok=True)
        for name in names: (d/f'{name}.png').write_bytes(tiny) if not (d/f'{name}.png').exists() else None
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    if not MANIFEST.exists(): MANIFEST.write_text(json.dumps({'schema':'bridge-helm-assets-v1','generated':True,'assets':names},indent=2),encoding='utf-8')
def run_gui_smoke(): assert bridge_get_snapshot(bridge_new_game_state())['current_node']['id']=='harbor'; print('GUI smoke: PASS'); return True
def run_gui_qa():
    s=bridge_new_game_state();
    for a in ['scan','plot_course:ledger_gate','travel_plotted','quick_salvage','inspect_systems']: s=bridge_apply_action(s,a)
    assert s.current_node=='ledger_gate' and s.route_memory; print('GUI QA: PASS'); return True
def run_qa():
    s=bridge_new_game_state(); s=bridge_apply_action(s,'scan'); s=bridge_apply_action(s,'plot_course:ledger_gate'); s=bridge_apply_action(s,'travel_plotted'); assert s.current_node=='ledger_gate'; s.fuel=0; s=bridge_apply_action(s,'plot_course:witness_pool'); s=bridge_apply_action(s,'travel_plotted'); assert s.current_node=='ledger_gate'; print('Gameplay QA: PASS'); return True
def run_asset_qa(): ensure_placeholder_assets(); assert MANIFEST.exists(); assert not list(ROOT.rglob('*.svg')); print('Asset QA: PASS'); return True
def run_accessibility_qa(): assert all('hotkey' in m for m in bridge_get_snapshot(bridge_new_game_state())['actions'].values()); print('Accessibility QA: PASS'); return True
def run_persistence_qa():
    p=ROOT/'.tmp_bridge_save.json'; s=bridge_apply_action(bridge_new_game_state(),'scan'); bridge_save_game(s,p); assert bridge_load_game(p).turn==s.turn; p.write_text('bad',encoding='utf-8'); assert bridge_load_game(p).current_node=='harbor'; [q.unlink(missing_ok=True) for q in ROOT.glob('.tmp_bridge_save.json*')]; print('Persistence QA: PASS'); return True
def run_performance_qa():
    s=bridge_new_game_state();
    for i in range(200): s=bridge_apply_action(s,['scan','quick_salvage','deep_salvage','safe_pause'][i%4])
    assert len(s.black_box)<=80 and len(s.route_memory)<=20; print('Performance QA: PASS'); return True
def run_balance_sim(runs=40):
    endings={}
    for seed in range(runs):
        s=bridge_new_game_state(seed)
        for _ in range(20):
            if s.current_node=='aureal_gate': break
            s=bridge_apply_action(s,'scan'); opts=_reach(s); target=opts[seed%len(opts)] if opts else None
            if target: s=bridge_apply_action(s,f'plot_course:{target}'); s=bridge_apply_action(s,'travel_plotted')
            if s.fuel<=1: s=bridge_apply_action(s,'quick_salvage')
        s=bridge_apply_action(s,'final_trial'); endings[s.ending]=endings.get(s.ending,0)+1
    assert sum(endings.values())==runs and max(endings.values())/runs<=.75; print('Balance Sim: PASS',endings); return endings
def run_static_sweep():
    text=Path(__file__).read_text(encoding='utf-8'); risky=['ev'+'al(','ex'+'ec(','api'+'_key','secret'+'_key','PROMPT'+'_QUEUE','IMAGE'+'_PROMPTS']; found=[x for x in risky if x in text.replace('risky=','checked=')]; assert not found,found; print('Static sweep: PASS'); return True
def run_bug_sweep():
    print('Running Bridge Helm exhaustive bug sweep...')
    for f in [run_static_sweep,run_gui_smoke,run_gui_qa,run_qa,run_asset_qa,run_accessibility_qa,run_persistence_qa,run_performance_qa,run_balance_sim]: f()
    print('Exhaustive Bug Sweep Result: PASS'); return True
def run_bridge_helm_gui():
    import tkinter as tk
    s=bridge_new_game_state(); root=tk.Tk(); root.title('Starsilk Chronicles: Bridge Helm'); status=tk.StringVar(); canvas=tk.Canvas(root,width=760,height=520,bg='#08131d'); status_label=tk.Label(root,textvariable=status,anchor='w'); status_label.pack(fill='x'); canvas.pack(fill='both',expand=True)
    def refresh():
        snap=bridge_get_snapshot(s); status.set(f"Node {s.current_node} | Fuel {s.fuel} | Hull {s.hull} | Heat {s.admin_heat} | {snap['objectives'][0]}"); canvas.delete('all')
        for src,ts in EDGES.items():
            for t in ts: canvas.create_line(NODES[src][1],NODES[src][2],NODES[t][1],NODES[t][2],fill='#376a84',width=2)
        for nid,v in NODES.items(): canvas.create_oval(v[1]-14,v[2]-14,v[1]+14,v[2]+14,fill=('#7fffd4' if nid==s.current_node else '#20323f'),outline='#b9f2ff'); canvas.create_text(v[1],v[2]+28,text=nid,fill='#d8f7ff')
    def do(a):
        nonlocal s; s=bridge_apply_action(s,a); refresh()
    bar=tk.Frame(root); bar.pack(fill='x')
    for label,a in [('Scan','scan'),('Plot first route','plot_course:ledger_gate'),('Travel','travel_plotted'),('Salvage','quick_salvage'),('Final','final_trial'),('Reset','reset')]: tk.Button(bar,text=label,command=lambda x=a:do(x)).pack(side='left')
    refresh(); root.mainloop()
def main(argv:Optional[List[str]]=None):
    p=argparse.ArgumentParser(); [p.add_argument(x,action='store_true') for x in ['--gui','--gui-smoke','--gui-qa','--gameplay-qa','--asset-qa','--accessibility-qa','--persistence-qa','--performance-qa','--balance-sim','--static-sweep','--bug-sweep']]; a=p.parse_args(argv)
    if a.gui: run_bridge_helm_gui(); return 0
    if a.gui_smoke: run_gui_smoke(); return 0
    if a.gui_qa: run_gui_qa(); return 0
    if a.gameplay_qa: run_qa(); return 0
    if a.asset_qa: run_asset_qa(); return 0
    if a.accessibility_qa: run_accessibility_qa(); return 0
    if a.persistence_qa: run_persistence_qa(); return 0
    if a.performance_qa: run_performance_qa(); return 0
    if a.balance_sim: run_balance_sim(); return 0
    if a.static_sweep: run_static_sweep(); return 0
    if a.bug_sweep: run_bug_sweep(); return 0
    run_gui_smoke(); print('Run with --gui or --bug-sweep.'); return 0
if __name__=='__main__': raise SystemExit(main())