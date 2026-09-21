/* ==========================================================================
   面试陪练 · 前端交互脚本
   使用 api.js 提供的接口封装；URL 加 ?mock=1 时自动切换 mock 后端（mock.js）。
   ========================================================================== */

const $ = (sel, root = document) => root.querySelector(sel);
const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

/* ---------- 通用：顶栏（用户名 + 退出） ---------- */
function setupTopbar() {
  const auth = requireAuth();
  const nameEl = $('#username');
  if (nameEl) nameEl.textContent = (auth && auth.username) || '';
  const logoutEl = $('#logout');
  if (logoutEl) {
    logoutEl.addEventListener('click', (e) => {
      e.preventDefault();
      clearAuth();
      location.href = 'login.html';
    });
  }
}

/* ---------- 通用：分段均分题目数 ---------- */
function buildSegments(types, total) {
  const per = Math.floor(total / types.length);
  const remainder = total % types.length;
  return types.map((type, i) => ({ type, count: per + (i < remainder ? 1 : 0) }));
}

/* ---------- 通用：时间格式化 ---------- */
function formatDate(iso) {
  const d = new Date(iso);
  if (isNaN(d.getTime())) return iso;
  const p = (n) => String(n).padStart(2, '0');
  return `${d.getFullYear()}-${p(d.getMonth() + 1)}-${p(d.getDate())} ${p(d.getHours())}:${p(d.getMinutes())}`;
}

/* ==========================================================================
   页面：登录 / 注册
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

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    errorEl.classList.remove('visible');
    const username = $('#username').value.trim();
    const password = passwordInput.value;
    if (!username || !password) {
      errorEl.textContent = '请填写用户名和密码';
      errorEl.classList.add('visible');
      return;
    }
    try {
      const data = mode === 'login' ? await login(username, password) : await register(username, password);
      setAuth(data.token, data.user.username);
      location.href = 'index.html';
    } catch (err) {
      errorEl.textContent = err.message;
      errorEl.classList.add('visible');
    }
  });
  render();
}

/* ==========================================================================
   页面：面试配置
   ========================================================================== */
function initIndex() {
  setupTopbar();

  const list = $('#template-list');
  const errorEl = $('#error');

  function showError(msg) { errorEl.textContent = msg; errorEl.classList.add('visible'); }
  function hideError() { errorEl.classList.remove('visible'); }

  // 预设模板
  getTemplates().then((templates) => {
    list.innerHTML = '';
    templates.forEach((t) => {
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
          <a class="list-item-action" href="#">开始</a>
        </div>`;
      $('.list-item-name', li).textContent = t.name;
      $('.list-item-desc', li).textContent = `${directionLabel(t.direction)} · ${desc}`;
      $('.list-item-count', li).textContent = `${totalQuestions(t.segments)} 题`;
      $('.list-item-action', li).addEventListener('click', (e) => {
        e.preventDefault();
        startInterview({ template_id: t.id });
      });
      list.appendChild(li);
    });
  }).catch((err) => {
    list.innerHTML = `<li class="state">加载失败：${err.message}</li>`;
  });

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

  function startInterview(config) {
    hideError();
    createInterview(config).then((data) => {
      sessionStorage.setItem('pending_interview', JSON.stringify(data));
      location.href = `interview.html?session_id=${data.session_id}`;
    }).catch((err) => showError(err.message));
  }

  $('#custom-start').addEventListener('click', () => {
    hideError();
    const direction = $('.chip.selected', $('#direction-chips')).dataset.value || 'general';
    const types = $$('#type-chips .chip.selected').map((c) => c.dataset.value);
    if (!types.length) { showError('请至少选择一种题型'); return; }
    if (count < types.length) { showError(`题目数量不能少于已选题型数量（${types.length}）`); return; }
    startInterview({ direction, segments: buildSegments(types, count) });
  });
}

/* ==========================================================================
   页面：面试进行
   ========================================================================== */
function initInterview() {
  setupTopbar();

  const params = new URLSearchParams(location.search);
  const sessionId = params.get('session_id');
  let pending = {};
  try { pending = JSON.parse(sessionStorage.getItem('pending_interview') || '{}'); } catch (e) {}

  const progressEl = $('#progress');
  const bar = $('#progress-bar-fill');
  const conversation = $('#conversation');
  const currentBlock = $('#current-block');
  const currentText = $('#current-text');
  const answerEl = $('#answer');
  const hintEl = $('#hint');
  const submitBtn = $('#submit');
  const doneBlock = $('#done-block');

  let total = pending.total_questions || 0;
  let current = pending.current_question || null;
  let finished = false;

  function showHint(msg) { hintEl.textContent = msg; hintEl.classList.add('visible'); }
  function hideHint() { hintEl.classList.remove('visible'); }

  function renderProgress() {
    const idx = current ? current.round_index + 1 : 0;
    progressEl.textContent = `第 ${idx} 题 / 共 ${total} 题`;
    bar.style.width = `${total ? (idx / total) * 100 : 0}%`;
  }

  function renderCurrent() {
    currentText.textContent = current ? current.content : '';
    answerEl.value = '';
    hideHint();
    renderProgress();
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
    currentBlock.style.display = 'none';
    doneBlock.style.display = 'block';
    progressEl.textContent = `共 ${total} 题`;
    bar.style.width = '100%';
  }

  function goReport() { location.href = `report.html?session_id=${sessionId}`; }

  submitBtn.addEventListener('click', async () => {
    const answer = answerEl.value.trim();
    if (!answer) { showHint('请先输入回答'); return; }
    submitBtn.disabled = true;
    try {
      const data = await submitAnswer(sessionId, answer);
      if (data.is_finished) {
        appendTurn(current.content, answer, data.feedback);
        finished = true;
        showFinish();
      } else if (data.next_question && data.next_question.round_index === current.round_index) {
        showHint(data.feedback);
      } else {
        appendTurn(current.content, answer, data.feedback);
        current = data.next_question;
        renderCurrent();
      }
    } catch (err) {
      showHint(err.message);
    } finally {
      submitBtn.disabled = false;
    }
  });

  $('#finish').addEventListener('click', async () => {
    if (!confirm('确定提前结束面试吗？已完成题目将计入报告。')) return;
    try {
      await finishInterview(sessionId);
      goReport();
    } catch (err) { showHint(err.message); }
  });

  $('#view-report').addEventListener('click', goReport);

  if (!sessionId || !current) {
    currentBlock.style.display = 'none';
    doneBlock.style.display = 'block';
    $('#done-text').textContent = '缺少面试上下文';
    $('#view-report').textContent = '返回首页';
    $('#view-report').addEventListener('click', () => { location.href = 'index.html'; });
    return;
  }
  renderCurrent();
}

/* ==========================================================================
   页面：评估报告
   ========================================================================== */
function initReport() {
  setupTopbar();
  const sessionId = new URLSearchParams(location.search).get('session_id');
  const content = $('#content');

  function showError(msg) {
    content.innerHTML = '';
    const d = document.createElement('div');
    d.className = 'state';
    d.textContent = msg;
    content.appendChild(d);
  }

  if (!sessionId) { showError('缺少会话参数'); return; }

  getReport(sessionId).then((r) => {
    content.innerHTML = '';
    const head = document.createElement('div');
    head.className = 'report-head';
    head.innerHTML = `
      <h1 class="report-title">面试评估报告</h1>
      <div class="report-meta">
        <span class="tag seal"></span>
        <span class="tag"></span>
      </div>`;
    $('.tag.seal', head).textContent = directionLabel(r.direction);
    $('.tag:not(.seal)', head).textContent = statusLabel(r.status);
    content.appendChild(head);

    const mkCard = (title, body) => {
      const card = document.createElement('section');
      card.className = 'card';
      card.innerHTML = `<h2 class="card-title"></h2><div class="card-body"></div>`;
      $('.card-title', card).textContent = title;
      $('.card-body', card).textContent = body;
      return card;
    };
    content.appendChild(mkCard('总体评价', r.overall_evaluation));
    content.appendChild(mkCard('改进建议', r.improvement_suggestions));

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
  }).catch((err) => showError(err.message));
}

/* ==========================================================================
   页面：历史记录
   ========================================================================== */
function initHistory() {
  setupTopbar();
  const list = $('#history-list');
  const countEl = $('#count');

  listInterviews().then((sessions) => {
    list.innerHTML = '';
    countEl.textContent = sessions.length ? `共 ${sessions.length} 场` : '';
    if (!sessions.length) {
      list.innerHTML = '<li class="state">暂无面试记录，<a class="start-link" href="index.html">去开始第一场面试</a></li>';
      return;
    }
    sessions.forEach((s) => {
      const li = document.createElement('li');
      li.className = 'list-item';
      const meta = `${s.total_questions} 题 · ${formatDate(s.started_at)}`;
      if (s.status === 'completed' || s.status === 'finished') {
        li.innerHTML = `
          <a class="list-item-main" href="report.html?session_id=${s.id}" style="flex:1">
            <div class="list-item-name"></div>
            <div class="list-item-desc"></div>
          </a>
          <div class="list-item-side">
            <span class="tag ${s.status}"></span>
            <span class="arrow">›</span>
          </div>`;
        $('.list-item-name', li).textContent = directionLabel(s.direction);
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
        $('.list-item-name', li).textContent = directionLabel(s.direction);
        $('.list-item-desc', li).textContent = meta;
        $('.tag', li).textContent = statusLabel(s.status);
      }
      list.appendChild(li);
    });
  }).catch((err) => {
    list.innerHTML = `<li class="state">加载失败：${err.message}</li>`;
  });
}

/* ==========================================================================
   入口
   ========================================================================== */
document.addEventListener('DOMContentLoaded', () => {
  const page = document.body.dataset.page;
  const handlers = { login: initLogin, index: initIndex, interview: initInterview, report: initReport, history: initHistory };
  if (handlers[page]) handlers[page]();
});
