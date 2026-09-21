/* ==========================================================================
   面试陪练 · UI 原型交互脚本
   纯前端 mock 数据驱动，用于展示各页面交互，不接后端。
   ========================================================================== */

/* ---------- 展示文案映射 ---------- */
const DIRECTION_LABELS = {
  technical_frontend: '技术-前端',
  technical_backend: '技术-后端',
  technical_algorithm: '技术-算法',
  product: '产品',
  operations: '运营',
  general: '通用',
};
const TYPE_LABELS = {
  self_introduction: '自我介绍',
  technical: '技术题',
  behavioral: '行为题',
  project_experience: '项目经验题',
  open_ended: '开放题',
};
const STATUS_LABELS = {
  in_progress: '进行中',
  completed: '已完成',
  finished: '已结束',
};
const dirLabel = (v) => DIRECTION_LABELS[v] || v;
const typeLabel = (v) => TYPE_LABELS[v] || v;
const statusLabel = (v) => STATUS_LABELS[v] || v;
const totalCount = (segments) => (segments || []).reduce((n, s) => n + s.count, 0);

/* ---------- 工具 ---------- */
const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/* ---------- mock 数据 ---------- */
const MOCK_TEMPLATES = [
  { id: 1, name: '前端开发面试', direction: 'technical_frontend',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 }, { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 }] },
  { id: 2, name: '后端开发面试', direction: 'technical_backend',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 }, { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 }] },
  { id: 3, name: '算法工程师面试', direction: 'technical_algorithm',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 }, { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 }] },
  { id: 4, name: '产品经理面试', direction: 'product',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 3 }, { type: 'project_experience', count: 2 }, { type: 'open_ended', count: 1 }] },
  { id: 5, name: '运营面试', direction: 'operations',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 2 }] },
  { id: 6, name: '通用行为面试', direction: 'general',
    segments: [{ type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 3 }, { type: 'open_ended', count: 1 }] },
];

const MOCK_HISTORY = [
  { id: 1042, direction: 'general', total_questions: 3, started_at: '2026-09-21 10:24', status: 'finished' },
  { id: 1038, direction: 'technical_backend', total_questions: 8, started_at: '2026-09-20 19:05', status: 'completed' },
  { id: 1027, direction: 'product', total_questions: 7, started_at: '2026-09-19 15:41', status: 'completed' },
  { id: 1011, direction: 'technical_frontend', total_questions: 8, started_at: '2026-09-17 09:12', status: 'finished' },
];

const MOCK_REPORT = {
  session_id: 1042, direction: 'general', status: 'finished',
  overall_evaluation: '你已完整完成本次面试（3/3 题），整体表现良好，回答结构清晰，能够结合自身经历展开。',
  improvement_suggestions: '建议在行为题中更多地使用 STAR 法则组织回答，并补充可量化的结果数据。',
  questions: [
    { question_content: '请做一个简短的自我介绍，谈谈你的教育背景和最近的一段项目经历。', user_answer: '我是一名前端工程师，有三年经验……', feedback: '回答覆盖了全部参考要点，回答较完整。' },
    { question_content: '请描述一次你与团队协作解决冲突的经历。', user_answer: '在上一家公司，我们……', feedback: '回答覆盖了部分要点（团队协作），建议补充：解决问题。' },
    { question_content: '谈谈你未来三年的职业规划。', user_answer: '我希望在技术深度上……', feedback: '回答覆盖了部分要点（职业规划），建议补充：学习能力。' },
  ],
};

/* ==========================================================================
   页面：登录
   ========================================================================== */
function initLogin() {
  let mode = 'login';
  const title = $('#title');
  const subtitle = $('#subtitle');
  const submitBtn = $('#submit');
  const switchLink = $('#switch-link');
  const passwordInput = $('#password');
  const form = $('#form');
  const errorEl = $('#error');

  function render() {
    const isLogin = mode === 'login';
    title.textContent = isLogin ? '登录' : '创建账号';
    subtitle.textContent = isLogin ? '用一个账号，保存你的每次练习记录' : '注册后开始你的模拟面试';
    submitBtn.textContent = isLogin ? '登录' : '注册';
    switchLink.textContent = isLogin ? '注册' : '登录';
    passwordInput.setAttribute('autocomplete', isLogin ? 'current-password' : 'new-password');
    errorEl.classList.remove('visible');
  }
  switchLink.addEventListener('click', () => { mode = mode === 'login' ? 'register' : 'login'; render(); });

  form.addEventListener('submit', (e) => {
    e.preventDefault();
    const username = $('#username').value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
      errorEl.textContent = '请填写用户名和密码';
      errorEl.classList.add('visible');
      return;
    }
    // 原型：登录/注册成功后跳转到配置页
    location.href = 'config.html';
  });
  render();
}

/* ==========================================================================
   页面：配置
   ========================================================================== */
function initConfig() {
  const list = $('#template-list');
  const templateList = $$('#template-list .list-item');

  // 渲染 mock 模板
  MOCK_TEMPLATES.forEach((t) => {
    const li = document.createElement('li');
    li.className = 'list-item';
    const desc = t.segments.map((s) => `${typeLabel(s.type)} ${s.count} 题`).join('、');
    li.innerHTML = `
      <div class="list-item-main">
        <div class="list-item-name"></div>
        <div class="list-item-desc"></div>
      </div>
      <div class="list-item-side">
        <span class="list-item-count"></span>
        <a class="list-item-action" href="interview.html">开始</a>
      </div>`;
    $('.list-item-name', li).textContent = t.name;
    $('.list-item-desc', li).textContent = `${dirLabel(t.direction)} · ${desc}`;
    $('.list-item-count', li).textContent = `${totalCount(t.segments)} 题`;
    list.appendChild(li);
  });
  if (templateList.length) templateList.forEach((n) => n.remove());

  // 岗位方向单选
  const dirChips = $$('#direction-chips .chip');
  dirChips.forEach((chip) => chip.addEventListener('click', () => {
    dirChips.forEach((c) => c.classList.remove('selected'));
    chip.classList.add('selected');
  }));

  // 题型多选
  $$('#type-chips .chip').forEach((chip) => chip.addEventListener('click', () => {
    chip.classList.toggle('selected');
  }));

  // 题目数量
  let count = 8;
  const countValue = $('#count-value');
  const countTotal = $('#count-total');
  function renderCount() {
    countValue.textContent = count;
    countTotal.textContent = `共 ${count} 题（1–20）`;
  }
  $('#count-minus').addEventListener('click', () => { if (count > 1) { count--; renderCount(); } });
  $('#count-plus').addEventListener('click', () => { if (count < 20) { count++; renderCount(); } });

  // 开始面试
  $('#custom-start').addEventListener('click', () => {
    const types = $$('#type-chips .chip.selected');
    if (!types.length) {
      alert('请至少选择一种题型');
      return;
    }
    location.href = 'interview.html';
  });
}

/* ==========================================================================
   页面：面试
   ========================================================================== */
function initInterview() {
  let round = 1;
  const total = 3;
  const bar = $('#progress-bar-fill');
  const progress = $('#progress');
  const conversation = $('#conversation');
  const currentText = $('#current-text');
  const answerEl = $('#answer');
  const hintEl = $('#hint');
  const submitBtn = $('#submit');

  const QUESTIONS = [
    '请做一个简短的自我介绍，谈谈你的教育背景和最近的一段项目经历。',
    '请描述一次你与团队协作解决冲突的经历。',
    '谈谈你未来三年的职业规划。',
  ];

  function renderProgress() {
    progress.textContent = `第 ${round} 题 / 共 ${total} 题`;
    bar.style.width = `${(round / total) * 100}%`;
  }

  function appendTurn(question, answer, feedback) {
    const div = document.createElement('div');
    div.className = 'turn';
    div.innerHTML = `
      <div class="turn-q"><span class="turn-speaker">面试官</span><div class="turn-text"></div></div>
      <div class="turn-a"><span class="turn-speaker">我的回答</span><div class="turn-text"></div></div>
      <div class="turn-f"><span class="turn-speaker">点评</span><div class="turn-text"></div></div>`;
    $$('.turn-q .turn-text', div)[0].textContent = question;
    $$('.turn-a .turn-text', div)[0].textContent = answer;
    $$('.turn-f .turn-text', div)[0].textContent = feedback;
    conversation.appendChild(div);
  }

  function showFinish() {
    $('#current-block').style.display = 'none';
    $('#done-block').style.display = 'block';
    progress.textContent = `共 ${total} 题`;
    bar.style.width = '100%';
  }

  submitBtn.addEventListener('click', () => {
    const answer = answerEl.value.trim();
    if (!answer) {
      hintEl.textContent = '请先输入回答';
      hintEl.classList.add('visible');
      return;
    }
    if (answer.length < 10) {
      hintEl.textContent = '回答过短，请至少输入 10 个字符后再提交。';
      hintEl.classList.add('visible');
      return;
    }
    hintEl.classList.remove('visible');
    appendTurn(QUESTIONS[round - 1], answer, '回答覆盖了部分要点，建议补充：关键词。');
    answerEl.value = '';
    round++;
    if (round > total) {
      showFinish();
    } else {
      currentText.textContent = QUESTIONS[round - 1];
      renderProgress();
    }
  });

  $('#finish').addEventListener('click', () => {
    if (confirm('确定提前结束面试吗？已完成题目将计入报告。')) {
      location.href = 'report.html';
    }
  });

  $('#view-report').addEventListener('click', () => { location.href = 'report.html'; });

  currentText.textContent = QUESTIONS[0];
  renderProgress();
}

/* ==========================================================================
   页面：报告
   ========================================================================== */
function initReport() {
  const r = MOCK_REPORT;
  const content = $('#content');
  content.innerHTML = '';

  const head = document.createElement('div');
  head.className = 'report-head';
  head.innerHTML = `
    <h1 class="report-title">面试评估报告</h1>
    <div class="report-meta">
      <span class="tag seal"></span>
      <span class="tag"></span>
    </div>`;
  $('.tag.seal', head).textContent = dirLabel(r.direction);
  $('.tag:not(.seal)', head).textContent = statusLabel(r.status);
  content.appendChild(head);

  const overall = document.createElement('section');
  overall.className = 'card';
  overall.innerHTML = '<h2 class="card-title">总体评价</h2><div class="card-body"></div>';
  $('.card-body', overall).textContent = r.overall_evaluation;
  content.appendChild(overall);

  const suggest = document.createElement('section');
  suggest.className = 'card';
  suggest.innerHTML = '<h2 class="card-title">改进建议</h2><div class="card-body"></div>';
  $('.card-body', suggest).textContent = r.improvement_suggestions;
  content.appendChild(suggest);

  const reviews = document.createElement('section');
  reviews.className = 'card';
  reviews.innerHTML = '<h2 class="card-title">逐题点评</h2>';
  r.questions.forEach((q) => {
    const item = document.createElement('div');
    item.className = 'review';
    item.innerHTML = `
      <div class="review-q"></div>
      <div class="review-a"><span class="review-label">我的回答</span><div class="review-body"></div></div>
      <div class="review-f"><span class="review-label">点评</span><div class="review-body"></div></div>`;
    $('.review-q', item).textContent = q.question_content;
    $$('.review-a .review-body', item)[0].textContent = q.user_answer;
    $$('.review-f .review-body', item)[0].textContent = q.feedback;
    reviews.appendChild(item);
  });
  content.appendChild(reviews);
}

/* ==========================================================================
   页面：历史
   ========================================================================== */
function initHistory() {
  const list = $('#history-list');
  const countEl = $('#count');
  list.innerHTML = '';
  countEl.textContent = MOCK_HISTORY.length ? `共 ${MOCK_HISTORY.length} 场` : '';

  MOCK_HISTORY.forEach((s) => {
    const li = document.createElement('li');
    li.className = 'list-item';
    const meta = `${s.total_questions} 题 · ${s.started_at}`;
    if (s.status === 'completed' || s.status === 'finished') {
      li.innerHTML = `
        <a class="list-item-main" href="report.html" style="flex:1">
          <div class="list-item-name"></div>
          <div class="list-item-desc"></div>
        </a>
        <div class="list-item-side">
          <span class="tag ${s.status}"></span>
          <span class="arrow">›</span>
        </div>`;
      $('.list-item-name', li).textContent = dirLabel(s.direction);
      $('.list-item-desc', li).textContent = meta;
      $('.tag', li).textContent = statusLabel(s.status);
    } else {
      li.classList.add('muted');
      li.innerHTML = `
        <div class="list-item-main">
          <div class="list-item-name"></div>
          <div class="list-item-desc"></div>
        </div>
        <div class="list-item-side"><span class="tag in_progress"></span></div>`;
      $('.list-item-name', li).textContent = dirLabel(s.direction);
      $('.list-item-desc', li).textContent = meta;
      $('.tag', li).textContent = statusLabel(s.status);
    }
    list.appendChild(li);
  });
}

/* ==========================================================================
   入口：按 body[data-page] 分发
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  const handlers = { login: initLogin, config: initConfig, interview: initInterview, report: initReport, history: initHistory };
  if (handlers[page]) handlers[page]();
});
