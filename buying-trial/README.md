# 구매재판 EP.01 — 에어프라이어 두 서랍
한국어 파일럿. 완료한 실제 MP4를 휴대폰에서 재생한 뒤 채팅으로 명시적 승인을 받아야 합니다. 유튜브 업로드는 승인 전 금지합니다. 이후 모든 한국어/영어 영상에도 같은 확인 방식을 적용합니다.

## 재현
Python 의존성은 기존 한국어 제작 환경과 같습니다. 저장소 루트에서 `python scripts/download_model.py` 실행 후, 이 폴더에 NotoSansCJK-Regular.ttc(공식 notofonts/noto-cjk Sans/OTC)를 준비합니다. 각 독립 연출 이미지는 아래 원본 순서대로 assets/1.png~8.png에 놓고 `python buying-trial/build_trial.py`를 실행합니다. 생성 이미지 원본은 ChatGPT의 해당 생성 기록에 보존됩니다. 이미지나 영상 바이너리를 Git에 커밋하지 않습니다.

- 음성: Supertonic 3, Sarah F1, ko, speed 1.1, steps 8. 무료 로컬 생성.
- 화면: 12개 1920×1080 장면. 독립 생성 원본 8개를 잘라 붙이지 않고 contain으로 배치.
- 자막/강조: 실제 문장별 합성 음성 길이에 맞춤.
- 출력: H.264/AAC, yuv420p, 24fps, faststart MP4.
- 인물/제품은 가상의 연출 이미지이며 실물 시험·공식 제품 사진이 아님.
- 최근 다섯 끼 질문은 편집용 자가 점검이며 과학적 점수나 절약 보장이 아님.
- 공식 기능 참고: https://sharkninja.com.au/products/ninja-foodi-max-xxxl-dual-zone-air-fryer-af400
- 원본 로고: assets/smartchoice365-brand-logo-v1.png.

## 독립 이미지 원본
1. exec-1f37fb67-8ae2-477c-abcf-699f733ff646.png
2. exec-3d36f037-2bdf-463c-91d9-1b9908070e34.png
3. exec-39eb6905-0b14-4ddf-be4b-0530b480ed83.png
4. exec-d331a378-ad15-48c1-b793-7f9f33086bd6.png
5. exec-72ada9bd-dda5-4910-9382-c701563a6ce4.png
6. exec-d90eece2-6b79-43cd-a9c5-2c6e598ea925.png
7. exec-6a825472-f75a-4a8e-84ad-38fca2b5274c.png
8. exec-c01dc85d-3579-4352-b40d-e9f3aa1c5e7a.png

## 공개 설명/댓글 초안
👉 구매 결정에 더 많은 도움이 필요하신가요? 스마트초이스365 구매 가이드 둘러보기: https://smartchoice365-web.pages.dev/?utm_source=youtube&utm_medium=video&utm_campaign=buying_trial_airfryer_ko_v1

서랍이 두 개면 정말 더 편할까요? 동시에 굽는 메뉴, 바구니 크기, 세척과 주방 공간으로 구매재판을 열었습니다. 여러분은 최근 다섯 번의 저녁 중 두 칸이 몇 번 필요했나요?

영상은 가상의 생활 사례와 연출 이미지로 구성했습니다. 모델별 기능과 설치·세척 안내는 제조사 설명을 확인하세요.

설명란과 댓글에 홈페이지 주소를 넣는 기존 규칙을 유지합니다. 댓글 고정은 지원 여부를 확인하고 실제 수행한 경우에만 고정했다고 보고합니다.
