# Smart Choice 365 — 채팅 중심 게시 작업 원칙

Owner direction (2026-11-02):

- Smart Choice 365의 YouTube Shorts, Facebook Reels, Instagram Reels, Instagram Stories 제작·게시 요청은 **현재 ChatGPT 대화에서 기존 연결 수단을 우선 활용하여 수행**한다.
- **Work 모드로 전환하라고 반복 안내하지 않는다.** 채팅에서 작업해온 기존 GitHub Actions / YouTube API / Meta API 경로를 먼저 탐색한다.
- 기존 GitHub 저장소 `Hoonygogo/smartchoice365-video`의 승인된 게시 워크플로와 비밀키를 활용하고, 사용자의 계정 권한이 없다고 근거 없이 단정하지 않는다.
- 실제 채팅 세션에서 호출 가능한 도구가 제한되어 있다면, **사용자의 계정 권한 부족**과 **해당 세션의 도구 실행 한계**를 구분해 설명한다. 실행하지 못한 업로드를 게시 완료라고 주장하지 않는다.
- 승인된 영상 원본과 원본 음성·배경음·효과음을 유지한다. RUA EP.00 10초 원본에는 이미 엔딩이 포함되어 있으므로 공식 엔딩을 중복 추가하지 않는다. 이후 새 쇼츠에는 승인된 5.5~10초 구간의 RUA 공식 엔딩을 활용한다.
- 0원 우선 운영, 소유자의 명시적 승인 없이는 유료 API 또는 구독을 시작하지 않는다.
- 실제 공개 게시 후 YouTube/Instagram/Facebook/Instagram Stories 각각 공개 링크와 게시 상태를 확인한다. 중복 게시를 방지한다.

This file is an editorial/operational preference record, not a claim that a video has been published or that all tools are available in every chat session.

## 바로 업로드 화면 링크 규칙 (2026-11-02 확정)
- 앞으로 영상 게시를 위해 GitHub 업로드가 필요하면 저장소 디렉터리 링크가 아니라 **해당 폴더의 직접 업로드 UI** `https://github.com/Hoonygogo/smartchoice365-video/upload/main/uploads` 로 안내한다.
- 업로드할 승인본을 해당 규칙에 필요한 **정확한 파일명으로 먼저 준비**하고 파일명·SHA-256·용량을 안내한다. 영상 원본의 음성과 기존 엔딩은 임의로 수정하지 않는다.
- 웹 링크만으로 사용자의 로컬 파일을 자동 선택·첨부할 수 있다고 주장하지 않는다. 필요한 경우 채팅에서 올린 파일을 GitHub 커밋으로 바로 이전할 수 있는 도구를 우선 확인한다.
- 사용자가 다른 파일명으로 올렸다면 다시 업로드를 요구하기 전에 기존 GitHub Blob SHA를 활용한 안전한 파일명 수정으로 자동 게시를 연결하고, 발행 결과를 각 플랫폼의 기록으로 확인한다.
- 2026-11-02 RUA EP00는 GitHub에서 `main(2).mp4`를 정확한 자동게시 파일명으로 수정하여 YouTube, Instagram Reel, Facebook Reel, Instagram Story 네 곳 모두 `published_verified` 게시 기록과 GitHub Actions 성공을 확인했다. Workflow run: `41396691722`.

## 최종 파일 다운로드 검증·전달 필수 규칙 (2026-11-02, 사용자 반복 실패 신고)
- 사용자가 루아 쇼츠 완성본의 채팅 다운로드 링크가 **반복적으로 열리지 않는다고 직접 보고**했다. 동일한 실패 방식(기존 임시 경로를 검증 없이 재게시)으로 다시 제공하지 않는다.
- 영상 MP4를 전달하기 전 현재 실행 환경의 **정확한 경로에 파일이 실제 존재하고 크기가 0 이상인지 확인**한다. 파일명만 보고 `sandbox:/mnt/data/...` 링크를 지어내지 않는다.
- 반드시 `ffprobe`로 정확한 재생시간, 영상 크기, 코덱, 오디오 스트림을 확인하고 `ffmpeg -v error -xerror`로 영상/음성을 **끝까지 디코딩 검사**한다. 예측/메타데이터만으로 '정상 다운로드·재생 검증 완료'라고 말하지 않는다.
- 짧은 영문 ASCII 전용 파일명으로 최종 MP4를 새로 내보내고, 모바일/웹 호환성을 위해 H.264/AAC, `-movflags +faststart`를 적용한다. 원본의 연출/음성/승인된 엔딩은 그대로 둔다.
- 같은 세션에서 파일이 실제 만들어져 확인된 경우에만 검증된 새 `sandbox:` 링크를 제공한다. **sandbox 다운로드 링크가 사용자의 실제 UI에서 동작함까지 서버 측에서 보장할 수 없으므로**, 동작 검증을 과장하지 않는다.
- 채팅 링크 **외에 별도의 영구 백업**을 반드시 마련한다. 먼저 ChatGPT Library `/SmartChoice365/FinalShorts/`에 완성본을 업로드하고 상태가 succeeded인지 확인한 후, 해당 Library 경로와 파일명을 함께 안내한다. 가능하면 GitHub 리포지토리에도 실제 MP4를 저장해 고정된 파일 다운로드 링크를 제공한다. GitHub 업로드 실패 시에도 'GitHub 저장 완료'라고 말하지 않는다.
- 파일을 다시 업로드할 필요가 있는 경우 기존 GitHub upload UI를 직접 연결하고 파일명을 명확히 제시한다. 원본에 중복 엔딩을 넣지 않으며 영상 완성본 자체의 비디오 링크와 엔딩 원본을 혼동하지 않는다.
- 첫 사례: `RUA_EP01_FINAL_14s.mp4`, 길이 14.549초, 720×1280 H.264/AAC, 3,724,808 bytes, SHA-256 `672e91ea81e47226d89a8c0cff54707ced43301448308b3ac3314e976587ab3f`. 현재 환경에서 영상과 오디오 전체 디코딩 검증. Library 백업 `/SmartChoice365/FinalShorts/RUA_EP01_FINAL_14s.mp4` 저장 성공. **사용자 UI 다운로드 성공 여부는 별도 미확인.**
