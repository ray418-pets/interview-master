// 前端 Mock 后端：模拟后端全部 /api 接口
// 使用 localStorage 作为模拟数据库，无需真实后端即可测试各模块。
// 通过 window.__mockRequest(method, path, body) 返回 { code, message, data }，契约与真实后端一致。
(function () {
  var USERS_KEY = 'mock_users';
  var SESSIONS_KEY = 'mock_sessions';
  var REPORTS_KEY = 'mock_reports';
  var CURRENT_KEY = 'mock_current_user';
  var SEQ_KEY = 'mock_seq';

  function load(key) {
    try { return JSON.parse(localStorage.getItem(key) || '{}'); }
    catch (e) { return {}; }
  }
  function save(key, val) { localStorage.setItem(key, JSON.stringify(val)); }
  function ok(data) { return { code: 0, message: 'success', data: data }; }
  function err(code, message) { return { code: code, message: message }; }
  function genToken() { return 'mock_' + Math.random().toString(36).slice(2) + Date.now().toString(36); }
  function currentUser() { return load(CURRENT_KEY); }
  function nextId() {
    var n = parseInt(localStorage.getItem(SEQ_KEY) || '0', 10) + 1;
    localStorage.setItem(SEQ_KEY, String(n));
    return n;
  }

  var MOCK_TEMPLATES = [
    { id: 1, name: '前端开发面试', direction: 'technical_frontend', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 },
      { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 } ] },
    { id: 2, name: '后端开发面试', direction: 'technical_backend', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 },
      { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 } ] },
    { id: 3, name: '算法工程师面试', direction: 'technical_algorithm', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'technical', count: 4 },
      { type: 'behavioral', count: 2 }, { type: 'open_ended', count: 1 } ] },
    { id: 4, name: '产品经理面试', direction: 'product', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 3 },
      { type: 'project_experience', count: 2 }, { type: 'open_ended', count: 1 } ] },
    { id: 5, name: '运营面试', direction: 'operations', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 2 },
      { type: 'open_ended', count: 2 } ] },
    { id: 6, name: '通用行为面试', direction: 'general', segments: [
      { type: 'self_introduction', count: 1 }, { type: 'behavioral', count: 3 },
      { type: 'open_ended', count: 1 } ] },
  ];

  var _qid = 0;
  function genQuestions(direction, segments) {
    var qs = [];
    segments.forEach(function (seg) {
      for (var i = 0; i < seg.count; i++) {
        qs.push({
          id: ++_qid,
          direction: direction,
          question_type: seg.type,
          difficulty: 'easy',
          content: '【Mock】' + seg.type + ' 第 ' + (i + 1) + ' 题（方向：' + direction + '）',
          reference_points: ['要点一', '要点二'],
        });
      }
    });
    return qs;
  }

  function evaluate(question, answer) {
    var pts = question.reference_points || [];
    var hit = pts.filter(function (p) { return answer.indexOf(p) !== -1; });
    if (!pts.length || hit.length === pts.length) return '回答覆盖了全部参考要点，回答较完整。';
    if (hit.length) {
      var miss = pts.filter(function (p) { return hit.indexOf(p) === -1; });
      return '回答覆盖了部分要点，建议补充：' + miss.join('、') + '。';
    }
    return '回答未命中参考要点，建议围绕：' + pts.join('、') + '。';
  }

  // ---- 认证 ----
  function apiRegister(body) {
    var username = (body && body.username || '').trim();
    var password = (body && body.password) || '';
    if (username.length < 3 || username.length > 64) return err(40000, '参数校验失败');
    if (password.length < 6 || password.length > 128) return err(40000, '参数校验失败');
    var users = load(USERS_KEY);
    if (users[username]) return err(40901, '用户名已被占用');
    var id = Object.keys(users).length + 1;
    users[username] = { id: id, username: username, password: password };
    save(USERS_KEY, users);
    save(CURRENT_KEY, { id: id, username: username });
    return ok({ token: genToken(), user: { id: id, username: username } });
  }

  function apiLogin(body) {
    var username = (body && body.username) || '';
    var password = (body && body.password) || '';
    var user = load(USERS_KEY)[username];
    if (!user || user.password !== password) return err(40101, '用户名或密码错误');
    save(CURRENT_KEY, { id: user.id, username: user.username });
    return ok({ token: genToken(), user: { id: user.id, username: user.username } });
  }

  // ---- 模板 ----
  function apiTemplates() { return ok(MOCK_TEMPLATES); }

  // ---- 面试 ----
  function apiCreateInterview(body) {
    var me = currentUser();
    if (!me || !me.id) return err(40100, '缺少认证信息');
    var direction, segments;
    if (body && body.template_id != null) {
      var tpl = MOCK_TEMPLATES.filter(function (t) { return t.id === body.template_id; })[0];
      if (!tpl) return err(40402, '模板不存在');
      direction = tpl.direction; segments = tpl.segments;
    } else if (body && body.direction && body.segments && body.segments.length) {
      direction = body.direction; segments = body.segments;
    } else {
      return err(40008, '必须提供模板或自定义配置');
    }
    var total = segments.reduce(function (n, s) { return n + s.count; }, 0);
    if (total < 1 || total > 20) return err(40005, '题目总数须在 1-20 之间');
    var questions = genQuestions(direction, segments);
    var sessions = load(SESSIONS_KEY);
    var sid = nextId();
    sessions[sid] = {
      id: sid, user_id: me.id, direction: direction, segments: segments,
      status: 'in_progress', questions: questions,
      records: questions.map(function (q, i) { return { round_index: i, question: q, user_answer: null, feedback: null }; }),
      created_at: new Date().toISOString(),
    };
    save(SESSIONS_KEY, sessions);
    return ok({
      session_id: sid, direction: direction, total_questions: total, status: 'in_progress',
      current_question: { round_index: 0, content: questions[0].content },
    });
  }

  function apiAnswer(sid, body) {
    var me = currentUser();
    var sessions = load(SESSIONS_KEY);
    var session = sessions[sid];
    if (!session) return err(40401, '会话不存在');
    if (session.user_id !== me.id) return err(40301, '无权访问该会话');
    if (session.status !== 'in_progress') return err(40902, '会话已结束，无法继续作答');
    var answer = (body && body.answer || '').trim();
    var current = session.records.filter(function (r) { return r.user_answer == null; })[0];
    if (!current) return err(40902, '会话已结束，无法继续作答');
    if (answer.length < 10) {
      return ok({
        feedback: '回答过短，请至少输入 10 个字符后再提交。', is_finished: false,
        next_question: { round_index: current.round_index, content: current.question.content },
      });
    }
    current.user_answer = answer;
    current.feedback = evaluate(current.question, answer);
    var next = session.records.filter(function (r) { return r.user_answer == null; })[0];
    var isLast = !next;
    if (isLast) session.status = 'completed';
    save(SESSIONS_KEY, sessions);
    return ok({
      feedback: current.feedback, is_finished: isLast,
      next_question: isLast ? null : { round_index: next.round_index, content: next.question.content },
    });
  }

  function apiFinish(sid) {
    var me = currentUser();
    var sessions = load(SESSIONS_KEY);
    var session = sessions[sid];
    if (!session) return err(40401, '会话不存在');
    if (session.user_id !== me.id) return err(40301, '无权访问该会话');
    if (session.status !== 'in_progress') return err(40902, '会话已结束，无法操作');
    session.status = 'finished';
    save(SESSIONS_KEY, sessions);
    return ok({ session_id: session.id, status: session.status });
  }

  function apiList() {
    var me = currentUser();
    if (!me || !me.id) return err(40100, '缺少认证信息');
    var sessions = load(SESSIONS_KEY);
    var list = Object.keys(sessions).map(function (k) { return sessions[k]; })
      .filter(function (s) { return s.user_id === me.id; })
      .sort(function (a, b) { return b.created_at.localeCompare(a.created_at); })
      .map(function (s) {
        return { id: s.id, direction: s.direction, total_questions: s.questions.length, started_at: s.created_at, status: s.status };
      });
    return ok(list);
  }

  // ---- 报告 ----
  function apiReport(sid) {
    var me = currentUser();
    var sessions = load(SESSIONS_KEY);
    var session = sessions[sid];
    if (!session) return err(40401, '会话不存在');
    if (session.user_id !== me.id) return err(40301, '无权访问该会话');
    if (session.status === 'in_progress') return err(40903, '面试尚未完成，暂无报告');
    var reports = load(REPORTS_KEY);
    if (!reports[sid]) {
      var answered = session.records.filter(function (r) { return r.user_answer != null; });
      reports[sid] = {
        overall_evaluation: '（Mock）你完成了 ' + answered.length + '/' + session.records.length + ' 题。',
        improvement_suggestions: '（Mock）建议针对薄弱环节继续练习。',
      };
      save(REPORTS_KEY, reports);
    }
    var answered = session.records.filter(function (r) { return r.user_answer != null; });
    return ok({
      session_id: session.id, direction: session.direction, status: session.status,
      overall_evaluation: reports[sid].overall_evaluation,
      improvement_suggestions: reports[sid].improvement_suggestions,
      questions: answered.map(function (r) {
        return { question_content: r.question.content, user_answer: r.user_answer, feedback: r.feedback };
      }),
    });
  }

  // ---- 路由 ----
  window.__mockRequest = function (method, path, body) {
    var m;
    if (method === 'POST' && path === '/auth/register') return apiRegister(body);
    if (method === 'POST' && path === '/auth/login') return apiLogin(body);
    if (method === 'GET' && path === '/templates') return apiTemplates();
    if (method === 'POST' && path === '/interviews') return apiCreateInterview(body);
    if (method === 'GET' && path === '/interviews') return apiList();
    if (method === 'POST' && (m = path.match(/^\/interviews\/(\d+)\/answer$/))) return apiAnswer(parseInt(m[1], 10), body);
    if (method === 'POST' && (m = path.match(/^\/interviews\/(\d+)\/finish$/))) return apiFinish(parseInt(m[1], 10));
    if (method === 'GET' && (m = path.match(/^\/reports\/(\d+)$/))) return apiReport(parseInt(m[1], 10));
    return err(50000, 'mock 未实现的接口: ' + method + ' ' + path);
  };

  window.__mockReset = function () {
    localStorage.removeItem(USERS_KEY);
    localStorage.removeItem(SESSIONS_KEY);
    localStorage.removeItem(REPORTS_KEY);
    localStorage.removeItem(CURRENT_KEY);
    localStorage.removeItem(SEQ_KEY);
  };
})();
