// Run only through the connected Browser tool after inspecting the live form.
// No standalone Chrome launch, cookie export, hidden API or public-post action.
export async function fillAndSaveDraft(tab, job) {
  if (job.mode !== 'draft' || job.privacy !== 'private' || job.public_publish_enabled !== false)
    throw new Error('Only private drafts allowed');
  const p = tab.playwright;
  // Caller must first check list/receipts and select the exact hash-verified file.
  const snapshot = await p.domSnapshot();
  if (!snapshot.includes('기본 정보') || !snapshot.includes('임시저장'))
    throw new Error('Upload file and inspect the new draft form first');
  await p.getByRole('switch', {name:'전체 공개', exact:true}).uncheck();
  await p.getByRole('textbox', {name:'설명', exact:true}).fill(job.description);
  await p.getByRole('button', {name:'1차 카테고리', exact:true}).click();
  await p.getByRole('button', {name:job.category_primary, exact:true}).click();
  await p.getByRole('button', {name:'2차 카테고리', exact:true}).click();
  await p.getByRole('button', {name:job.category_secondary, exact:true}).click();
  for (const [name, enabled] of [['AI 활용 설정',job.ai_used],['광고・협찬 설정',job.advertising]]) {
    const control=p.getByRole('switch',{name,exact:true});
    if(enabled) await control.check(); else await control.uncheck();
  }
  await p.getByRole('button',{name:'블로그',exact:true}).click();
  // Stop here for fresh dialog inspection. Select the row matching BOTH the
  // requested blog title and exact URL, never blindly the first search result.
  return {status:'awaiting_verified_blog_selection', next:'Select verified matching blog row, inspect fields, then call saveDraft'};
}

export async function saveDraft(tab) {
  const p=tab.playwright;
  await p.getByRole('switch',{name:'전체 공개',exact:true}).uncheck();
  const before=await p.domSnapshot();
  if(!before.includes('이 동영상을 나만 볼 수 있어요.')) throw new Error('Privacy not established');
  await p.getByRole('button',{name:'임시저장',exact:true}).click();
  return {status:'awaiting_save_verification', next:'Require saved confirmation and persisted draft row; capture screenshot and write hash-bound receipt. Never click 등록.'};
}
