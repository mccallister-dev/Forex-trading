"""Read original TradingView exports and produce reproducible analysis evidence.
Uses bundled Python/openpyxl for read-only XLSX extraction. Does not edit sources.
"""
from pathlib import Path
from collections import Counter, defaultdict
import csv, hashlib, json, math, statistics
from datetime import datetime
from zoneinfo import ZoneInfo
import openpyxl

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'Strategy Tester Results'
OUT = ROOT / 'ORB Research 2026-09-14'

def metric(rows, name, col=1):
    return next((r[col] for r in rows if r[0] == name), None)

def date_value(v):
    if isinstance(v,datetime): return v.isoformat()
    for fmt in ['%Y-%m-%d %H:%M:%S','%b %d, %Y, %H:%M','%Y-%m-%d %H:%M']:
        try: return datetime.strptime(v,fmt).isoformat()
        except ValueError: pass
    return datetime.fromisoformat(v).isoformat()

def stats(trades, key='pnl'):
    x = [t[key] for t in trades]
    wins = [v for v in x if v > 0]
    losses = [v for v in x if v < 0]
    gp, gl = sum(wins), -sum(losses)
    n = len(x)
    p = len(wins)/n if n else None
    z = 1.96
    if n:
        mid=(p+z*z/(2*n))/(1+z*z/n)
        half=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/(1+z*z/n)
    else:
        mid=half=None
    balance=peak=drawdown=0.0
    max_streak=streak=0
    for v in x:
        balance += v
        peak=max(peak,balance)
        drawdown=max(drawdown,peak-balance)
        streak=streak+1 if v<0 else 0
        max_streak=max(max_streak,streak)
    payoff=statistics.mean(wins)/abs(statistics.mean(losses)) if wins and losses else None
    return dict(n=n,wins=len(wins),losses=len(losses),even=n-len(wins)-len(losses),net=sum(x),gross_profit=gp,gross_loss=gl,pf=gp/gl if gl else None,win_pct=p*100 if p is not None else None,ci_low=(mid-half)*100 if n else None,ci_high=(mid+half)*100 if n else None,mean=statistics.mean(x) if n else None,median=statistics.median(x) if n else None,payoff=payoff,breakeven_pct=100/(1+payoff) if payoff else None,closed_drawdown=drawdown,max_loss_streak=max_streak,net_without_best=sum(x)-max(x) if x else None)

def read_book(path):
    w=openpyxl.load_workbook(path,read_only=True,data_only=True)
    sheets={s.title:list(s.values) for s in w}
    props=dict(sheets['Properties'][1:])
    rows=sheets['Trades']; headers=rows[0]
    grouped=defaultdict(list)
    for row in rows[1:]:
        rec=dict(zip(headers,row)); grouped[rec['Trade number']].append(rec)
    trades=[]; open_trades=[]; issues=[]
    equity=float(props['Initial capital']); risk_pct=float(props['Equity risk per trade (%)'])
    for num,recs in sorted(grouped.items()):
        entries=[r for r in recs if str(r['Type']).startswith('Entry')]
        exits=[r for r in recs if str(r['Type']).startswith('Exit')]
        if len(entries)!=1 or len(exits)!=1:
            issues.append(f'Trade {num}: {len(entries)} entries / {len(exits)} exits');continue
        en,ex=entries[0],exits[0]
        if ex['Date and time']=='Open' or ex['Signal']=='Open':
            open_trades.append(dict(number=num,entry=date_value(en['Date and time']),side=en['Type'].split()[-1],unrealized_pnl=ex['Net PnL ZAR']))
            continue
        pnl=ex['Net PnL ZAR']
        budget=equity*risk_pct/100
        trades.append(dict(number=num,entry=date_value(en['Date and time']),exit=date_value(ex['Date and time']),side=en['Type'].split()[-1],signal=en['Signal'],exit_reason=ex['Signal'],entry_price=next(v for k,v in en.items() if k.startswith('Price ')),exit_price=next(v for k,v in ex.items() if k.startswith('Price ')),quantity=en['Size (qty)'],pnl=pnl,commission=ex['Commission ZAR'],equity_before=equity,risk_budget=budget,budget_r=pnl/budget if budget>0 else None,mfe=ex['Favorable excursion ZAR'],mae=ex['Adverse excursion ZAR']))
        equity+=pnl
    summary=stats(trades)
    reported_net=metric(sheets['Performance'],'Net profit')
    reported_n=metric(sheets['Trades analysis'],'Total trades')
    if abs(summary['net']-reported_net)>max(.05,len(trades)*.0051): issues.append('Net profit mismatch beyond rounding')
    if summary['n']!=reported_n: issues.append(f'Count differs: {summary["n"]} / {reported_n}')
    summary.update(reported_net=reported_net,reported_n=reported_n,net_difference=summary['net']-reported_net,dd_pct=metric(sheets['Performance'],'Max drawdown (intrabar)',2),dd_zar=metric(sheets['Performance'],'Max drawdown (intrabar)'),margin_calls=metric(sheets['Risk-adjusted performance'],'Margin calls'),session_exits=sum(t['exit_reason']=='Session end' for t in trades))
    selected=props['ORB session']
    pair=path.parent.name
    if selected=='Auto':
        selected=props['Manual preferred session'] if props['Preferred session mode']=='Manual' else 'New York' if pair in ['XAUUSD','NAS100','USDZAR'] else 'London' if any(x in pair for x in ['EUR','GBP','CHF']) else 'Asian'
    norm=stats([t for t in trades if t['budget_r'] is not None], 'budget_r')
    w.close()
    return dict(file=str(path.relative_to(ROOT)),sha256=hashlib.sha256(path.read_bytes()).hexdigest(),pair=pair,session=selected,props=props,summary=summary,budget_r=norm,issues=issues,trades=trades,open_trades=open_trades)

def main():
    OUT.mkdir(exist_ok=True)
    runs=[read_book(p) for p in sorted(SOURCE.rglob('*.xlsx')) if not p.name.startswith('~$')]
    seen={}
    for r in runs:
        fingerprint=json.dumps(dict(props={k:v for k,v in r['props'].items() if k not in ['Trading range','Backtesting range']},trades=r['trades'],open_trades=r['open_trades']),sort_keys=True)
        r['duplicate_of']=seen.get(fingerprint)
        seen.setdefault(fingerprint,r['file'])
        p=r['props']; name=r['session']; spec=p[name+' session']; zone=ZoneInfo(p[name+' timezone'])
        start_hour,start_minute=map(int,spec.split(' — ')[0].split(':'))
        end_hour,end_minute=map(int,spec.split(' — ')[1].split(':'))
        for t in r['trades']:
            local=datetime.fromisoformat(t['entry']).replace(tzinfo=ZoneInfo('Africa/Johannesburg')).astimezone(zone)
            minute=local.hour*60+local.minute
            t['entry_delay_minutes']=minute-(start_hour*60+start_minute)
            t['entry_inside_session']=(start_hour*60+start_minute)<=minute<(end_hour*60+end_minute)
        r['timing_diagnostic']={
            'inside_before90':stats([t for t in r['trades'] if t['entry_inside_session'] and t['entry_delay_minutes']<90],'budget_r'),
            'inside_after90':stats([t for t in r['trades'] if t['entry_inside_session'] and t['entry_delay_minutes']>=90],'budget_r'),
            'outside_session':stats([t for t in r['trades'] if not t['entry_inside_session']],'budget_r')}
    # Compare each pair over the intersection of its available data, bounded by requested start.
    for pair in sorted({r['pair'] for r in runs}):
        group=[r for r in runs if r['pair']==pair]
        starts=[];ends=[]
        for r in group:
            p=r['props']; raw=p['Backtesting range'].split(' — ')
            starts.append(max(datetime.strptime(raw[0],'%b %d, %Y, %H:%M'),datetime.strptime(p['Start date'],'%b %d, %Y, %H:%M')))
            ends.append(datetime.strptime(raw[1],'%b %d, %Y, %H:%M'))
        start,end=max(starts),min(ends)
        cut=start+(end-start)*.7
        for r in group:
            ts=[t for t in r['trades'] if datetime.fromisoformat(t['entry'])>=start and datetime.fromisoformat(t['exit'])<=end and t['budget_r'] is not None]
            r['common_window']=dict(start=start.isoformat(),end=end.isoformat(),chronological_split=cut.isoformat(),all=stats(ts,'budget_r'),early=stats([t for t in ts if datetime.fromisoformat(t['entry'])<cut],'budget_r'),late=stats([t for t in ts if datetime.fromisoformat(t['entry'])>=cut],'budget_r'))
            r['side_stats']={s:stats([t for t in r['trades'] if t['side']==s]) for s in ['long','short']}
            r['entry_hour_stats']={str(h):stats([t for t in r['trades'] if datetime.fromisoformat(t['entry']).hour==h],'budget_r') for h in sorted({datetime.fromisoformat(t['entry']).hour for t in r['trades']})}
    paper={}
    for p in SOURCE.rglob('*.csv'):
        with p.open(newline='',encoding='utf-8-sig') as f: paper[p.name]=list(csv.DictReader(f))
    history=next(v for k,v in paper.items() if 'trade-history' in k)
    exits=sorted([dict(symbol=r['Symbol'],number=r['Trade number'],entry=None,exit=date_value(r['Date and time']),pnl=float(r['Net PnL ZAR'])) for r in history if r['Type'].startswith('Exit')],key=lambda t:t['exit'])
    balances=next(v for k,v in paper.items() if 'balance-history' in k)
    orderhist=next(v for k,v in paper.items() if 'order-history' in k)
    balance_pnl=sum(float(r['Realized PnL (value)']) for r in balances)
    paper_summary=dict(closed_trades=stats(exits),per_symbol={s:stats([t for t in exits if t['symbol']==s]) for s in sorted({t['symbol'] for t in exits})},balance_events=len(balances),balance_pnl=balance_pnl,balance_first=float(balances[-1]['Balance before']),balance_last=float(balances[0]['Balance after']),reconciliation=stats(exits)['net']-balance_pnl,order_status=dict(Counter(r['Status'] for r in orderhist)),leverage=dict(Counter(r['Leverage'] for r in orderhist)),open_positions_rows=len(next(v for k,v in paper.items() if 'positions' in k)),working_order_rows=len(next(v for k,v in paper.items() if 'orders-all' in k)),closed_trade_rows=exits)
    data=dict(as_of='2026-09-14',export_timezone='Africa/Johannesburg, confirmed by user',unique_runs=len(seen),runs=runs,paper=paper_summary)
    (OUT/'analysis_evidence.json').write_text(json.dumps(data,indent=2,allow_nan=False))
    fields=['pair','file','duplicate_of','symbol','timeframe','session','session_timezone','session_exit_enabled','direction','model','risk_pct','target_r','trades','open_trades','net_zar','pf','win_pct','dd_pct','payoff','break_even_pct','mean_budget_r','common_start','common_end','common_trades','common_pf','late_trades','late_pf','issues']
    with (OUT/'run_comparison.csv').open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader()
        for r in runs:
            p,s,c=r['props'],r['summary'],r['common_window']; row=dict(pair=r['pair'],file=r['file'],duplicate_of=r['duplicate_of'],symbol=p['Symbol'],timeframe=p['Timeframe'],session=r['session'],session_timezone=p[r['session']+' timezone'],session_exit_enabled=p['Close open trade after session'],direction=p['Trade direction'],model=p['Entry model'],risk_pct=p['Equity risk per trade (%)'],target_r=p['Profit target (R)'],trades=s['n'],open_trades=len(r['open_trades']),net_zar=s['reported_net'],pf=s['pf'],win_pct=s['win_pct'],dd_pct=s['dd_pct'],payoff=s['payoff'],break_even_pct=s['breakeven_pct'],mean_budget_r=r['budget_r']['mean'],common_start=c['start'],common_end=c['end'],common_trades=c['all']['n'],common_pf=c['all']['pf'],late_trades=c['late']['n'],late_pf=c['late']['pf'],issues='; '.join(r['issues']));writer.writerow(row)
    for r in runs:
        p,s,c=r['props'],r['summary'],r['common_window'];print(r['pair'],Path(r['file']).stem.split('2026-09-14')[-1] or '(0)',p['Timeframe'],r['session'],p['Trade direction'],p['Entry model'],'risk',p['Equity risk per trade (%)'],'RR',p['Profit target (R)'],'n',s['n'],'net',round(s['net'],2),'PF',round(s['pf'] or 0,2),'win',round(s['win_pct'] or 0,1),'DD',s['dd_pct'],'common',c['all']['n'],round(c['all']['pf'] or 0,2),'late',c['late']['n'],round(c['late']['pf'] or 0,2),'issues',r['issues'])
    print('PAPER',json.dumps(paper_summary,indent=2))

if __name__=='__main__':main()
