# Smart Choice 365 Video

한국어 Sarah 음성으로 모바일 MP4 초안을 만드는 공개 제작 저장소입니다.

## 현재 구현 범위
- Supertonic 3 Sarah (`F1`), 한국어 `ko`, 8 steps, speed 1.0.
- 음성 길이에 맞춘 화면·한글 자막, H.264 Baseline + AAC MP4, faststart.
- 음성과 영상이 들어간 휴대폰 미리보기, 다운로드, 버전 해시.
- 모든 결과는 `awaiting_approval`; SNS 게시 코드는 아직 없습니다.
- 첫 샘플은 음성/재생 확인용 브랜드 안내이며 실제 제품 비교 완성본이 아닙니다.

## 처음 한 번 할 설정
1. GitHub 저장소 **Settings → Pages → Build and deployment → Source: GitHub Actions** 선택.
2. **Actions → Build Sarah Korean Draft → Run workflow** 실행.
3. 완료 후 https://hoonygogo.github.io/smartchoice365-video/ 에서 휴대폰으로 확인.
4. 대화에서 초안 버전과 함께 수정 또는 발행 의사를 전달.

워크플로는 main의 제작 코드·요청 파일 변경 시에도 초안을 만듭니다. 첫 실행 시 Pages 설정이 없으면 `preview` 배포만 실패할 수 있습니다. `render`가 성공했다면 Actions 실행 화면에서 `sarah-korean-draft-*` ZIP을 내려받을 수 있습니다. Pages 설정 후 실패한 배포를 재실행하세요.

## 승인 및 보관 규칙
초안 → 휴대폰 미리보기 → 해당 버전 사용자 승인 → SNS 게시 → 모든 플랫폼 성공 확인 → 임시 MP4 삭제 순서입니다. 승인 전 공개 SNS 발행은 금지합니다. 미리보기 사이트와 이 저장소는 공개 접근이 가능합니다.

현재 SNS 계정 연결·자동 게시·게시 후 자동 삭제는 미구현입니다. 이 저장소 생성이 해당 기능의 완성을 뜻하지 않습니다. Actions 다운로드 파일은 3일 후 만료되며, Pages의 최신 초안은 교체/삭제 전까지 남습니다. 보관 만료와 게시 후 삭제는 별개의 기능입니다. 미리보기가 만료되면 새 버전을 확인한 후 승인해야 합니다.

## 무료 운영
표준 공개 GitHub-hosted Linux 실행만 사용합니다. 유료 API, 카드, Azure, 유료 GPU가 필요하지 않습니다. 모델은 실행할 때 다운로드하고 캐시를 쌓지 않습니다. 결과 파일은 짧게 보관합니다. Actions/Pages의 서비스 제한과 계정 저장 한도는 적용되므로 무제한 저장을 약속하지 않습니다.

## 로컬 실행
Python 3.12, ffmpeg, 한국어 Noto CJK 글꼴이 필요합니다.
```sh
python -m pip install -r requirements.txt
python scripts/download_model.py
python scripts/render.py
```
`SC365_FONT`에 한국어 글꼴 경로를 지정할 수 있습니다. `--smoke-test`는 무음 렌더러 검증용이며 실제 제작 워크플로에서는 사용하지 않습니다.

## 모델과 사용권
- 모델: https://huggingface.co/Supertone/supertonic-3
- 고정 revision: `3cadd1ee6394adea1bd021217a0e650ede09a323`
- 모델 사용권: OpenRAIL-M, 다운로드한 `LICENSE`와 사용 제한 준수.
- SDK: Supertonic 1.2.2 (MIT). 원 프로젝트는 보관 상태이므로 버전 변경은 검증 후 적용.
- Sarah = F1 근거: https://huggingface.co/spaces/Supertone/supertonic-3/blob/main/script.js 의 `VOICE_DESCRIPTIONS`.
- 제작 시점의 사실·가격·소재 사용권 및 제휴 고지를 확인하며 직접 사용하지 않은 제품에 대한 체험을 꾸미지 않습니다.

로그·공개 파일에 계정 키를 넣지 않습니다. 향후 SNS 자격 증명은 GitHub Secrets에만 저장합니다.

## Current English production path — 2026-11-01
New English general videos MUST use `english-guide/render_english_guide.py` and `english-guide/guide_video_layout.py`. The Ninja and Breville ordinary preview entry points/workflows now delegate to this common pipeline. Historical one-off owner-approved publishing implementations remain historical; do not use their permissive or old-layout settings for a new video.

- Same approved Korean Heattech/Padding visual standard: 1920×1080, 24fps, H.264/AAC, faststart, navy/cream/gold, exact original logo, illustrated quality guide, short greeting and subscribe invitation.
- Twelve distinct scenes, at least eight independently generated photograph-style scenes, entire-source contain placement, disclosure outside images, no contact-sheet crops.
- English voice remains Kokoro `af_heart`, `lang_code=a`, speed `0.96`, 24000Hz; Australian wording does not imply an Australian synthesised accent.
- All cue layouts checked before speech, real non-silent narration checked before assembly, clause-audio timings determine captions and explicit focus targets. Code blocks missing/invalid images, wrong source hashes, overflow, unknown targets and inaudible voice.
- Free local/CPU production; no paid API, animation service or replacement system voice.
- Local example: `python english-guide/render_english_guide.py --request aircon-english/request.json --storyboard-only`, then visually inspect all sources/compositions and retain truthful review metadata; run without `--storyboard-only` to build the MP4.
- Install `english-guide/requirements.txt` plus ffmpeg/DejaVu fonts. The dependency set was locally exercised with Kokoro speech and the air-conditioning preview.
- Image generation is performed in ChatGPT. Source-image bytes are NOT committed to Git history. Supply the reviewed scene assets and matching `visual_manifest.json` locally or through a trusted Actions artifact. The common manual review workflow requires that artifact's exact run/name; it does not magically generate/transfer images.
- Output includes MP4, captions, voice WAV/receipts, cue timings, scene/frame evidence, manifest and a mobile-friendly HTML player. Inspect actual encoded opening, mid-video chart and final frames before presenting completion.
- All new results remain awaiting user approval and are not automatically posted to YouTube. Upload only the exact approved hash, then verify processing/public status and guide-first description. Never claim a comment is pinned solely because the API created it.
