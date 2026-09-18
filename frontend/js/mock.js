// 前端 Mock 数据层：模拟后端 /api/auth 认证接口
// 使用 localStorage 作为模拟数据库，无需真实后端即可测试用户模块。
// 通过 window.__mockRegister / window.__mockLogin 暴露给 api.js 使用。
(function () {
  var MOCK_USERS_KEY = 'mock_users';

  function loadUsers() {
    try {
      return JSON.parse(localStorage.getItem(MOCK_USERS_KEY) || '{}');
    } catch (e) {
      return {};
    }
  }

  function saveUsers(users) {
    localStorage.setItem(MOCK_USERS_KEY, JSON.stringify(users));
  }

  function genToken() {
    return 'mock_' + Math.random().toString(36).slice(2) + Date.now().toString(36);
  }

  // 契约与真实后端一致：成功返回 data（{token, user}），失败 throw Error(message)
  function mockRegister(username, password) {
    if (!username || username.length < 3 || username.length > 64) {
      throw new Error('参数校验失败');
    }
    if (!password || password.length < 6 || password.length > 128) {
      throw new Error('参数校验失败');
    }
    var users = loadUsers();
    if (users[username]) {
      throw new Error('用户名已被占用');
    }
    var id = Object.keys(users).length + 1;
    users[username] = { id: id, username: username, password: password };
    saveUsers(users);
    return { token: genToken(), user: { id: id, username: username } };
  }

  function mockLogin(username, password) {
    var user = loadUsers()[username];
    if (!user || user.password !== password) {
      throw new Error('用户名或密码错误');
    }
    return { token: genToken(), user: { id: user.id, username: user.username } };
  }

  function mockReset() {
    localStorage.removeItem(MOCK_USERS_KEY);
  }

  window.__mockRegister = mockRegister;
  window.__mockLogin = mockLogin;
  window.__mockReset = mockReset;
})();
