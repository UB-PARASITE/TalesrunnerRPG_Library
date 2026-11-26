# 동화나라 스토리 플레이어

구조(`story_tree.json`, `story_scripts.json`)와 텍스트(`TextAsset/Text_*_loc_kor.txt`)를 분리한 스토리 플레이어.

```
index.html              플레이어 (실행 시 아래 파일들을 fetch로 읽음)
story_tree.json         스토리 트리: 카테고리 > 그룹(챕터/이벤트/캐릭터) > 화(dialogId), 제목·화자는 텍스트 key
story_scripts.json      dialogId별 연출 스크립트(배경/캐릭터/선택지 분기 등), 대사는 텍스트 key
story_tree_outline.txt  트리를 사람이 읽기 쉬운 들여쓰기 목록으로 만든 참고용 파일
TextAsset/              Text_*_loc_kor.txt (Chapter, MainStorySet, SubStory, SubStoryRead,
                        FriendshipStory, Hero, Mob, Portrait, Writer, Dialog, Talk)
tools/                  parse.py → build_tree.py 로 JSON 재생성
```

## 실행
- GitHub Pages 또는 `python3 -m http.server` 후 `http://localhost:8000/`
- 서버 없이 `index.html`을 직접 열면 fetch가 막히므로, 상단 **📁 폴더 선택**으로 이 폴더 전체를 선택하세요.

## 텍스트 교체
`TextAsset/`의 txt만 바꾸면 화면 텍스트가 바뀝니다 (key는 `키<TAB>내용` 형식).
다른 언어는 `story_tree.json`의 `"lang"` 값(`kor` → `eng` 등)과 파일명을 맞추세요.

## 트리 JSON 형식
- `tree[]` 노드: `{id,label|title,children[]}`, 말단: `{title,dialogId}`
- `title`은 배열이며 `@`로 시작하는 항목은 텍스트 key, 나머지는 그대로 출력 (예: `["@Hero_Name_0003"," 생일 (5/2)"]`)
- 배열 순서 = 재생·표시 순서
- 스크립트 스텝: `T`(대사: pid,key,성별) `H`제목 `L`장소 `F`화면글 `B`배경 `C/X/XA/E/M`캐릭터 `I`이모티콘 `K`암전 `G`BGM `Z`장면전환 `Q`(선택지: 옵션 key[], 분기 스텝[][])
