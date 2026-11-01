# Smart Choice 365 Shorts → full video linking policy

### Ninja Air Fryer (approved 2026-11-01)

- Short video file (must exactly match SHA-256): `uploads/SmartChoice365_Ninja_Shorts_RelatedVideo_CTA.mp4`
- SHA-256: `57a0721fc4381bb5f60071fa9c3a529d963d08ff9d3c7629e3e679001ee1c0ce`
- Full video: https://www.youtube.com/watch?v=2R5Nyt42hRs
- Detail buying guide: https://smartchoice365-web.pages.dev/guides/2026-ninja-af141-vs-af400-australia-single-dual-basket.html
- Auto upload workflow: `.github/workflows/ninja-airfryer-short-publish.yml`
- Upload receipt path: `publications/receipts/ninja-airfryer-tiny-basket-short-cta-20261101-youtube.json`

**Important:** Uploading video metadata and putting a YouTube URL in the Short description will NOT display YouTube's clickable Shorts "Related video" link. The official YouTube Data API does not expose this field. Upload receipt must state that the actual related-video binding remains pending until set in YouTube Studio by a user with the channel's advanced feature access.

### Final one-time Studio action

1. Open https://studio.youtube.com/
2. Content → Shorts → the newly uploaded 'Air Fryer Too Small? 4 People, 1 Tiny Basket' Short.
3. Find **Related video** and choose the already-published `2R5Nyt42hRs` (Ninja AF141 vs AF400).
4. Save.
5. Confirm a clickable video link appears below the channel handle in the Shorts player.

Never represent the Related video as attached unless its Studio state is independently verified.

### Reusable strategy for future Shorts

- Match the Shorts topic with its own related long-form video when available.
- Show clear end-screen wording like "Tap related video below".
- Ensure the long-form video description provides the specific corresponding Smart Choice 365 guide URL.
- For Shorts without a matching full-length video, promote the Smart Choice 365 channel or website according to editorial policy, but do not imply plain Shorts description links are clickable.
