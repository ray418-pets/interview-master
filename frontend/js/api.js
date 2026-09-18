const API_BASE = '/api';
const TOKEN_KEY = 'auth_token';
const USERNAME_KEY = 'auth_username';

// ---------- 展示用文案映射 ----------
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

function directionLabel(value) {
  return DIRECTION_LABELS[value] || value;
}

function typeLabel(value) {
  return TYPE_LABELS[value] || value;
}

function statusLabel(value) {
  return STATUS_LABELS[value] || value;
}

function totalQuestions(segments) {
  return (segments || []).reduce((n, s) => n + (s.count || 0), 0);
}

// ---------- 认证 ----------
function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function getAuth() {
  return {
    token: localStorage.getItem(TOKEN_KEY),
    username: localStorage.getItem(USERNAME_KEY),
  };
}

function setAuth(token, username) {
  localStorage.setItem(TOKEN_KEY, token);
  localStorage.setItem(USERNAME_KEY, username);
}

function clearAuth() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USERNAME_KEY);
}

function requireAuth() {
  const auth = getAuth();
  if (!auth.token) {
    window.location.href = 'login.html';
    return null;
  }
  return auth;
}

// ---------- 请求封装 ----------
async function request(method, path, body) {
  const headers = { 'Content-Type': 'application/json' };
  const token = getToken();
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  const resp = await fetch(API_BASE + path, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (resp.status === 401) {
    clearAuth();
    if (!location.pathname.endsWith('login.html')) {
      window.location.href = 'login.html';
    }
    throw new Error('登录已失效，请重新登录');
  }
  const data = await resp.json();
  if (data.code !== 0) {
    throw new Error(data.message || '请求失败');
  }
  return data.data;
}

// ---------- 业务 API ----------
async function register(username, password) {
  return request('POST', '/auth/register', { username, password });
}

async function login(username, password) {
  return request('POST', '/auth/login', { username, password });
}

async function getTemplates() {
  return request('GET', '/templates');
}

async function createInterview(config) {
  return request('POST', '/interviews', config);
}

async function submitAnswer(sessionId, answer) {
  return request('POST', `/interviews/${sessionId}/answer`, { answer });
}

async function finishInterview(sessionId) {
  return request('POST', `/interviews/${sessionId}/finish`);
}

async function listInterviews() {
  return request('GET', '/interviews');
}

async function getReport(sessionId) {
  return request('GET', `/reports/${sessionId}`);
}
