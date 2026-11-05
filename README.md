# 의정부시 기상 통합 상황판 — GitHub Pages 설치 안내

이 패키지는 의정부·신곡 AWS 두 지점을 표시하는 기상 상황판입니다.
화면은 GitHub Pages가 제공하고, GitHub Actions가 기상 API를 수집하며, 결과는 JSON으로 보관합니다.
이 파일을 받은 것만으로 저장소나 웹사이트가 자동 생성되는 것은 아닙니다.

## 1. 클로드 안내와 달라지는 점

| 붙여 넣은 다른 프로젝트의 안내 | 이 기상 상황판에 적용할 내용 |
|---|---|
| ujb-youth 저장소 | 새 저장소 uijeongbu-weather-did 권장 |
| DATA_GO_KR_KEY, GG_DATA_KEY | GG_DATA_KEY 한 개만 등록 |
| 보조금24·기업마당·K-Startup 수집 | 경기데이터드림 AWS1hourObser 조회 |
| data/items.json 점검 | data/observations.json·latest.json·history.json·status.json 점검 |
| 09:00·16:00 하루 두 번 수집 | 매시간 05분·35분 수집 예약 |
| 키 입력 완료만으로 사이트 준비 완료 | collect·deploy·check 결과와 관측시각까지 확인 |

다른 사업의 저장소에 이 파일을 그대로 덮어쓰면 기존 사이트가 바뀔 수 있습니다.
별도 저장소에 올리는 것이 안전합니다. 계정명과 저장소명을 정하지 않았으므로 특정 계정의 URL을 미리 확정하지 않았습니다.

## 2. 받은 파일과 업로드할 내용

- weather-github-pages.zip: 화면·수집 스크립트·JSON 초기파일·워크플로·이 안내서 전체
- github-workflows.zip: `.github/workflows/` 폴더와 세 워크플로만 포함

처음 설치할 때는 전체 ZIP을 사용하세요. 전체 ZIP에 `.github`도 들어 있으므로, 폴더가 정상 업로드됐다면 두 번째 ZIP은 필요 없습니다.
`.github`만 누락됐을 때 두 번째 ZIP을 추가로 풀어 올리세요. **ZIP 자체를 저장소에 올리는 것이 아니라 압축을 풀어 내용물을 올립니다.**

저장소 첫 화면의 구조는 아래와 같아야 합니다.

| 경로 | 역할 |
|---|---|
| index.html | 기상 상황판 화면 |
| scripts/collect.py | API 수집 및 JSON 생성 |
| scripts/check_data.py | 자료 누락·지연 점검 |
| scripts/test_collect.py | 인증키 없이 실행하는 수집 로직 검증 |
| scripts/test_static.mjs | JSON 화면 동작 검증용, 운영 필수 아님 |
| data/observations.json | 두 지점 최근 자료 통합 |
| data/latest.json | 지점별 최신값 |
| data/history.json | 최근 24시간 관측값 |
| data/status.json | 수집 성공 여부·수신시각·관측시각 |
| .github/workflows/collect.yml | 수집 및 data 브랜치 저장 |
| .github/workflows/deploy.yml | Pages 배포 |
| .github/workflows/check.yml | 저장된 자료 점검 |
| README.md | 이 설치 안내 |

`weather-github-pages/index.html`처럼 상위 폴더가 한 겹 더 들어가면 안 됩니다. `index.html`이 저장소 첫 화면에 바로 보여야 합니다.
초기 JSON은 실제 관측값이 없는 빈 파일입니다. 예시 기상 수치를 실제 데이터처럼 표시하지 않습니다.

## 3. GitHub 저장소 만들기

1. GitHub에 로그인합니다.
2. 오른쪽 위 `+` → `New repository`를 누릅니다.
3. `Owner`에서 사용할 개인 계정 또는 기관 조직을 고릅니다.
4. `Repository name`에 `uijeongbu-weather-did`를 입력합니다. 다른 이름도 가능합니다.
5. GitHub Free로 공개 호스팅하려면 `Public`을 선택합니다.
6. `Add a README file`을 켜서 첫 브랜치를 생성합니다.
7. `Create repository`를 누릅니다.

기관 조직에서 공개 저장소·Actions·Pages를 제한한 경우 관리자 설정 확인이 먼저 필요합니다.
공개 저장소와 Pages에는 코드와 관측 JSON이 공개됩니다. 이 패키지에는 인증키가 포함되어 있지 않습니다.

## 4. 전체 파일 업로드

1. `weather-github-pages.zip`을 압축 해제합니다.
2. GitHub 저장소의 `Code` 첫 화면에서 `Add file` → `Upload files`를 누릅니다.
3. 압축을 푼 폴더 **안의** `index.html`, `scripts`, `data`, `.github`, `README.md` 등을 모두 끌어다 놓습니다.
4. `Commit changes`를 누릅니다. 확인 창이 나오면 한 번 더 확정합니다.
5. 기본 브랜치(보통 `main`)에 파일이 들어갔는지 확인합니다.

`.github`는 숨김 폴더일 수 있습니다. macOS Finder에서는 `Cmd + Shift + .`, Windows에서는 탐색기 `보기 → 표시 → 숨긴 항목`을 확인하세요.
브라우저·운영체제에 따라 숨김 폴더가 드래그 업로드에서 빠질 수 있으므로, 실제 저장소 경로를 반드시 확인하세요.

### .github가 빠졌다면

1. `github-workflows.zip`을 압축 해제합니다.
2. 안의 `.github` 폴더를 저장소의 `Upload files`에 **폴더째** 올립니다.
3. 저장소에서 `.github` → `workflows`를 눌러 `collect.yml`, `deploy.yml`, `check.yml`을 확인합니다.
4. 폴더 업로드가 안 되면 `Add file → Create new file`로 `.github/workflows/collect.yml` 경로를 입력하고 ZIP 안의 해당 내용을 복사합니다.
5. 같은 방법으로 `deploy.yml`, `check.yml`도 만듭니다. `yaml`이나 코드블록의 백틱은 붙이지 말고, 첫 줄 `name:`부터 붙여 넣습니다.

`.github.yml`처럼 이름을 바꾸거나 세 YAML 파일을 저장소 최상위에 올리면 실행되지 않습니다.
전체 파일을 올리지 않고 워크플로 ZIP만 올리면 `scripts/collect.py`가 없어 수집에 실패합니다.

## 5. 경기데이터드림 인증키 등록

1. 저장소의 `Settings`를 누릅니다.
2. 왼쪽 `Secrets and variables` → `Actions`를 누릅니다.
3. `New repository secret`을 누릅니다.
4. 다음 두 칸을 입력합니다.
   - Name: `GG_DATA_KEY`
   - Secret: 경기데이터드림에서 발급받은 실제 인증키
5. `Add secret`을 누릅니다.
6. Secrets 목록에 `GG_DATA_KEY` 이름이 보이면 등록된 것입니다. 저장 후 실제 키 값이 다시 보이지 않는 것은 정상입니다.

이 사이트에는 `DATA_GO_KR_KEY`가 필요 없습니다. 다른 프로젝트가 쓰는 키를 지울 필요는 없습니다.
API 키를 `index.html`, YAML, JSON에 직접 적거나 공개 커밋하지 마세요.
화면의 키 이름 목록을 확인할 때 실제 인증키 값을 캡처하거나 공유할 필요가 없습니다.

## 6. Pages 사용 설정

1. 저장소 `Settings` → 왼쪽 `Pages`를 누릅니다.
2. `Build and deployment`의 `Source`를 **GitHub Actions**로 선택합니다.
3. 선택이 반영됐는지 확인합니다. 보통 별도 Save 버튼 없이 적용됩니다.

`Deploy from a branch`로 두는 방식은 이 패키지의 배포 방식과 다릅니다.
기관 정책 때문에 Actions나 Pages가 비활성화돼 있으면 저장소·조직 관리자에게 허용을 요청하세요.
워크플로에는 수집용 `contents: write`, 배포용 `pages: write`, `id-token: write`가 명시되어 있습니다.
이 패키지 실행을 위해 별도 PAT(개인 토큰)를 만들 필요는 없습니다.

## 7. 첫 수집 실행

1. 위쪽 `Actions` 탭을 누릅니다.
2. 왼쪽에서 `collect`를 고릅니다.
3. 오른쪽 `Run workflow`를 누릅니다.
4. 브랜치는 기본 브랜치(보통 `main`)로 둡니다.
5. 실행 창의 `Run workflow`를 눌러 시작합니다.
6. 실행 목록에 새 항목이 나타나면 눌러 진행 상황을 확인합니다.

collect는 다음 순서로 작동합니다.

1. 이전 data 브랜치의 관측값을 복원합니다. 첫 실행에는 생략됩니다.
2. 한국시간 오늘·어제 자료를 `YYYYMMDD` 날짜 조건으로 조회합니다.
3. 의정부·신곡 자료만 남기고 중복·기간 밖 자료를 걸러 JSON을 작성합니다.
4. 두 지점의 자료와 관측시각을 점검합니다.
5. 생성된 JSON을 `data` 브랜치에 저장합니다.
6. 점검에서 문제가 발견되면 collect를 빨간색 실패로 표시합니다. 기존 수신자료와 오류 상태는 보존됩니다.

정상 수집의 기준은 단순히 파일이 존재하는 것이 아닙니다. 두 지점 자료가 모두 있어야 하고, 현재 기준 관측시각이 3시간 이내여야 합니다.
3시간은 이 패키지의 수집 점검 기준이며, 공식 기상특보 기준이 아닙니다.

## 8. 배포·점검 확인

collect가 종료되면 `deploy`와 `check`가 자동으로 실행됩니다.
이는 `workflow_run`으로 연결했으므로 data 브랜치 저장에 따른 push 이벤트에만 의존하지 않습니다.

- collect: 수집 결과 및 JSON 저장 확인
- deploy: 저장된 JSON과 화면을 GitHub Pages에 게시
- check: 저장된 두 지점 관측값·24시간 자료·관측시각 점검

정상 운영의 최초 확인은 **세 워크플로가 모두 초록색인지**와 화면의 실제 관측시각을 함께 보는 것입니다.
수집 실패 시에도 이전 자료와 오류 표시를 배포하므로, **deploy만 초록색이라고 최신 자료 수집에 성공한 것은 아닙니다.**
첫 수집 전에 deploy 또는 check만 수동 실행하면 data 브랜치가 없어 실패할 수 있습니다. collect부터 실행하세요.
수집 스크립트 자체의 실행 오류나 쓰기 권한 오류로 data 브랜치가 생성되지 않으면 배포도 실패할 수 있습니다.

## 9. 사이트 주소 확인

1. `Settings → Pages`에서 게시된 주소를 확인하거나,
2. 성공한 deploy 실행의 배포 링크를 누릅니다.

프로젝트 Pages의 기본 주소 형식은 다음과 같습니다.

`https://계정명.github.io/저장소명/`

예를 들어 계정이 `aiinnoteam01-web`, 새 저장소가 `uijeongbu-weather-did`라면 예상 주소는
`https://aiinnoteam01-web.github.io/uijeongbu-weather-did/`입니다.
이는 주소 형식의 예시이며, 해당 계정에 실제 저장소를 생성하거나 배포한 상태라는 의미는 아닙니다.
붙여 주신 `.../ujb-youth/`는 청년정책 사이트 주소이므로 새 기상 상황판의 주소와 구분하세요.

배포 대기·조직 승인·API 응답시간에 따라 개설 시간은 달라집니다. **10분 이내 개설을 보장할 수 없습니다.**

## 10. 화면 확인 및 일상 운영

- 의정부·신곡이 한 화면에 나오는지 확인합니다.
- 상단 날짜는 현재 한국시간입니다. 각 지점의 `관측시각`이 실제 기상자료 시각입니다.
- `마지막 수신`은 Actions가 자료를 받은 시각이며 관측시각과 다릅니다.
- 최근 24시간 그래프에는 어제 자료가 포함될 수 있습니다.
- 원자료가 시간 단위이므로 예약 수집 때마다 관측값이 달라지지는 않습니다.
- 화면은 열려 있는 동안 30분마다 JSON을 다시 확인합니다.
- 수집은 매시간 05분·35분에 예약되어 화면이 닫혀 있어도 실행될 수 있습니다.
- Actions 예약 실행과 Pages 배포에는 지연이 생길 수 있습니다. 정확한 분 단위 갱신을 보장하지 않습니다.
- 상단 새로고침 버튼은 **최근 배포된 JSON을 다시 읽습니다. API 즉시 수집 버튼이 아닙니다.**
- 즉시 새 수집을 원하면 `Actions → collect → Run workflow`를 실행하고, deploy 완료 후 화면을 새로고침합니다.
- 웹 화면에서 Actions를 실행하려고 GitHub 토큰을 HTML에 넣지 마세요.
- 공개 저장소의 예약 실행은 장기간 저장소 활동이 없을 때 비활성화될 수 있으므로 Actions 상태를 주기적으로 확인하세요.

## 11. 오류별 확인 위치

| 증상 | 확인 및 조치 |
|---|---|
| Actions에 세 이름이 안 보임 | 기본 브랜치의 `.github/workflows/` 경로와 YAML 확장자 확인 |
| GG_DATA_KEY 없음 | Repository Secret 이름·공백·발급기관 확인 |
| API 응답코드 오류 | collect 실행의 수집 단계에서 코드 확인. 키 유효성·서비스 이용 권한 확인 |
| API 접속 실패 | 제공기관 응답·네트워크 문제 가능. 잠시 뒤 collect 재실행 |
| 403 또는 push 권한 오류 | collect의 contents: write와 조직·브랜치 보호 정책 확인 |
| data 브랜치 없음 | collect부터 실행. 첫 수집의 JSON 저장 단계 확인 |
| Pages 배포 오류 | Source=GitHub Actions, deploy의 권한과 github-pages 환경 정책 확인 |
| 화면은 열리지만 —만 보임 | collect/check와 data 브랜치의 status.json 확인 |
| 어제 관측값만 보임 | 상태 메시지·관측시각 확인. collect 재실행 후 deploy 완료 여부 확인 |
| 새로고침해도 동일한 수치 | 동일 관측시각인지 확인. 새 JSON 배포 전에는 수치가 같을 수 있음 |
| 404 | 실제 Pages 주소와 경로 확인. index.html이 저장소 첫 화면에 있는지 확인 |

도움이 필요하면 실패한 워크플로 이름, 빨간 단계의 오류 문구, Secrets 이름 목록만 알려 주세요.
인증키 원문은 보내지 마세요. 캡처를 보낼 때도 인증키가 보이지 않게 하세요.

## 12. 검증 범위

파일 구성, YAML 문법, 날짜·중복·누락·실패 시 보존 처리, JSON 화면 재조회,
최초 data 브랜치 생성과 반복 저장 명령을 오프라인에서 점검했습니다.
기존 상황판에서 검증했던 경기데이터드림 AWS 제공 필드와 YYYYMMDD 날짜 조건을 사용합니다.
귀하의 GitHub 계정에서 실제 Actions 수집·Pages 배포는 아직 실행하지 않았습니다.
최초 실수집 성공 여부는 Secret 등록과 Run workflow 이후에 확인할 수 있습니다.

## 공식 참고 문서

- Pages 사용자 워크플로: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- 워크플로 트리거·예약 실행: https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows
- Actions Secrets: https://docs.github.com/en/actions/concepts/security/secrets
