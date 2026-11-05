"""Collect public AWS observations; credentials never enter output JSON."""
import concurrent.futures
import datetime as dt
import json
import os
from pathlib import Path
import re
import time
import urllib.error
import urllib.parse
import urllib.request

KST = dt.timezone(dt.timedelta(hours=9))
TARGETS = ('의정부', '신곡')
FIELDS = ('SIGUN_NM SIGUN_CD SPOT_NO SPOT_NM LEGALDONG_NM MESURE_DE MESURE_TM WGS84_LAT WGS84_LOGT HT_INFO WD_INFO WS_INFO TP_INFO HD_INFO LOCTN_ATM_INFO WTRLVL_ATM_INFO RAINF_YN_INFO RAINF_1HR_INFO RAINF_DAY_INFO').split()


def station(row):
    return re.sub(r'\s|관측지점|관측소|지점', '', str(row.get('SPOT_NM', '')))


def observed_at(row):
    date = re.sub(r'\D', '', str(row.get('MESURE_DE', '')))[:8]
    hour = re.sub(r'\D', '', str(row.get('MESURE_TM', ''))).zfill(2).ljust(4, '0')[:4]
    try:
        return dt.datetime.strptime(date + hour, '%Y%m%d%H%M').replace(tzinfo=KST)
    except ValueError:
        return None


def query_day(key, date):
    params = dict(KEY=key, Type='json', pIndex=1, pSize=1000, SIGUN_NM='의정부시', MESURE_DE=date)
    url = 'https://openapi.gg.go.kr/AWS1hourObser?' + urllib.parse.urlencode(params)
    for attempt in range(2):
        try:
            with urllib.request.urlopen(url, timeout=20) as response:
                body = json.load(response)
            section = body.get('AWS1hourObser')
            if not section:
                code = body.get('RESULT', {}).get('CODE', 'UNKNOWN')
                if code == 'INFO-200':
                    return []
                raise ValueError('API 응답코드 ' + re.sub(r'[^A-Za-z0-9_-]', '', str(code))[:40])
            head = next((part['head'] for part in section if 'head' in part), [])
            result = next((item['RESULT'] for item in head if 'RESULT' in item), {})
            code = result.get('CODE')
            if code == 'INFO-200':
                return []
            if code and code != 'INFO-000':
                raise ValueError('API 응답코드 ' + re.sub(r'[^A-Za-z0-9_-]', '', str(code))[:40])
            total = int(next((item['list_total_count'] for item in head if 'list_total_count' in item), 0))
            if total > 1000:
                raise ValueError('일자별 응답이 1000건을 초과했습니다. 조회 조건 확인 필요')
            rows = next((part['row'] for part in section if 'row' in part), [])
            return [row for row in rows if re.sub(r'\D', '', str(row.get('MESURE_DE', '')))[:8] == date]
        except ValueError as exc:
            # Only locally authored/code-only messages; never expose a request URL or key.
            if attempt:
                raise RuntimeError(str(exc).replace(key, '[보호됨]')) from None
        except Exception:
            if attempt:
                raise RuntimeError('API 접속 실패 또는 응답 해석 실패 (인증키·네트워크 확인)') from None
        time.sleep(2)


def latest_rows(rows):
    return [max((r for r in rows if station(r) == name), key=observed_at) for name in TARGETS if any(station(r) == name for r in rows)]


def assemble(previous, results, failures, now):
    unique = {}
    for row in previous.get('rows', []) + results:
        stamp = observed_at(row)
        if station(row) not in TARGETS or stamp is None or not (now - dt.timedelta(hours=48) <= stamp <= now + dt.timedelta(minutes=5)):
            continue
        if row.get('SIGUN_NM') not in (None, '', '의정부시'):
            continue
        unique[(station(row), stamp)] = {field: row.get(field) for field in FIELDS}
    rows = sorted(unique.values(), key=lambda r: (station(r), observed_at(r)))
    received = {station(r) for r in results if station(r) in TARGETS and observed_at(r) and now - dt.timedelta(hours=48) <= observed_at(r) <= now + dt.timedelta(minutes=5)}
    current = latest_rows(rows)
    stale = [station(r) for r in current if now - observed_at(r) > dt.timedelta(hours=3)]
    missing = [name for name in TARGETS if name not in received]
    ok = not failures and not missing and not stale and len(current) == 2
    messages = list(failures)
    if missing:
        messages.append('이번 수집 미수신: ' + '·'.join(missing))
    if stale:
        messages.append('관측시각 3시간 초과: ' + '·'.join(stale))
    warnings = ' / '.join(messages)
    fresh_times = [observed_at(r) for r in results if observed_at(r) and station(r) in TARGETS]
    # Receipt time advances only when target observations are actually received.
    generated = now.isoformat() if fresh_times else previous.get('generatedAt')
    snapshot = dict(schemaVersion=1, source='경기데이터드림 AWS 시간별 관측현황', generatedAt=generated,
                    lastAttemptAt=now.isoformat(), ok=ok, error=warnings if not ok else '', rows=rows)
    status = dict(schemaVersion=1, ok=ok, lastAttemptAt=now.isoformat(), generatedAt=generated,
                  rowCount=len(rows), message=warnings,
                  stations=[dict(name=station(r), observedAt=observed_at(r).isoformat()) for r in current])
    return snapshot, status


def main():
    out = Path('data'); out.mkdir(exist_ok=True)
    try:
        previous = json.loads((out / 'observations.json').read_text(encoding='utf-8'))
    except (FileNotFoundError, ValueError):
        previous = {}
    now = dt.datetime.now(KST)
    key = os.environ.get('GG_DATA_KEY', '').strip()
    results, failures = [], []
    if not key:
        failures.append('GG_DATA_KEY Secret가 등록되지 않았습니다.')
    else:
        days = [(now - dt.timedelta(days=i)).strftime('%Y%m%d') for i in (0, 1)]
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            futures = {pool.submit(query_day, key, day): day for day in days}
            for future in concurrent.futures.as_completed(futures):
                try:
                    results.extend(future.result())
                except Exception as exc:
                    failures.append(futures[future] + ': ' + str(exc).replace(key, '[보호됨]'))
    snapshot, status = assemble(previous, results, failures, now)
    latest = latest_rows(snapshot['rows'])
    history = [r for r in snapshot['rows'] if observed_at(r) >= now - dt.timedelta(hours=24)]
    files = {'observations.json': snapshot, 'status.json': status,
             'latest.json': dict(generatedAt=snapshot['generatedAt'], rows=latest),
             'history.json': dict(generatedAt=snapshot['generatedAt'], rows=history)}
    for name, content in files.items():
        temp = out / (name + '.tmp')
        temp.write_text(json.dumps(content, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temp.replace(out / name)
    print(json.dumps(status, ensure_ascii=False, indent=2))
    summary = os.environ.get('GITHUB_STEP_SUMMARY')
    if summary:
        with open(summary, 'a', encoding='utf-8') as file:
            file.write('## 기상자료 수집 결과\n\n' + ('정상' if status['ok'] else '확인 필요') + '\n\n')
            for item in status['stations']:
                file.write('- ' + item['name'] + ': ' + item['observedAt'] + '\n')
            if status['message']:
                file.write('\n' + status['message'] + '\n')


if __name__ == '__main__':
    main()
