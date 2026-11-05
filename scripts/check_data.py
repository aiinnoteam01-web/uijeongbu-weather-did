"""Fail visibly on missing, invalid, or stale observations, not just file presence."""
import argparse
import datetime as dt
import json
from pathlib import Path
import sys
from collect import station


def check(path, now=None):
    errors = []
    now = now or dt.datetime.now(dt.timezone.utc)
    try:
        status = json.loads((path / 'status.json').read_text(encoding='utf-8'))
        snapshot = json.loads((path / 'observations.json').read_text(encoding='utf-8'))
        latest = json.loads((path / 'latest.json').read_text(encoding='utf-8'))
        history = json.loads((path / 'history.json').read_text(encoding='utf-8'))
        if not status.get('ok'):
            errors.append('수집 상태: ' + status.get('message', '미수집'))
        if not snapshot.get('rows') or not history.get('rows'):
            errors.append('관측자료 또는 최근 24시간 자료가 비어 있습니다')
        found = {station(row) for row in latest.get('rows', [])}
        if found != {'의정부', '신곡'}:
            errors.append('의정부·신곡 두 지점 최신자료가 모두 필요합니다')
        for item in status.get('stations', []):
            stamp = dt.datetime.fromisoformat(item['observedAt'])
            if stamp.tzinfo is None or not -dt.timedelta(minutes=5) <= now - stamp <= dt.timedelta(hours=3):
                errors.append(item['name'] + ': 관측시각이 현재 기준 3시간을 초과했거나 잘못되었습니다')
        if not status.get('generatedAt'):
            errors.append('실제 수신시각이 없습니다')
    except Exception:
        errors.append('JSON 파일 누락 또는 형식 오류')
    for error in errors:
        print('::error::' + error)
    if not errors:
        print('정상: 의정부·신곡 관측자료 및 최근 24시간 JSON 확인 완료')
    return not errors


if __name__ == '__main__':
    parser = argparse.ArgumentParser(); parser.add_argument('--data-dir', default='data')
    args = parser.parse_args()
    sys.exit(0 if check(Path(args.data_dir)) else 1)
