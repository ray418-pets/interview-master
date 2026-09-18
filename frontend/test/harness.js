// 测试辅助函数（全局），供各模块 mock 测试页复用
var __results = [];

function assert(cond, msg) {
  if (!cond) throw new Error(msg || '断言失败');
}

function assertRejects(fn, expectedMsg) {
  return Promise.resolve()
    .then(fn)
    .then(
      function () { throw new Error('期望抛出异常，但未抛出'); },
      function (err) {
        if (expectedMsg && err.message.indexOf(expectedMsg) === -1) {
          throw new Error('期望错误包含「' + expectedMsg + '」，实际「' + err.message + '」');
        }
      }
    );
}

function test(name, fn) {
  return Promise.resolve()
    .then(fn)
    .then(function () { __results.push({ name: name, pass: true, detail: '' }); })
    .catch(function (e) { __results.push({ name: name, pass: false, detail: e.message }); });
}

function renderResults() {
  var summaryEl = document.getElementById('summary');
  var resultsEl = document.getElementById('results');
  var passed = __results.filter(function (r) { return r.pass; }).length;
  var failed = __results.length - passed;

  summaryEl.innerHTML = '';
  summaryEl.appendChild(pill('共 ' + __results.length + ' 例'));
  summaryEl.appendChild(pill('通过 ' + passed + ' 例', 'pass'));
  if (failed) summaryEl.appendChild(pill('失败 ' + failed + ' 例', 'fail'));

  resultsEl.innerHTML = '';
  __results.forEach(function (r) {
    var row = document.createElement('div');
    row.className = 'row';
    var status = document.createElement('div');
    status.className = 'status ' + (r.pass ? 'pass' : 'fail');
    status.textContent = r.pass ? 'PASS' : 'FAIL';
    var body = document.createElement('div');
    body.className = 'body';
    var name = document.createElement('div');
    name.className = 'name';
    name.textContent = r.name;
    body.appendChild(name);
    if (r.detail) {
      var detail = document.createElement('div');
      detail.className = 'detail';
      detail.textContent = r.detail;
      body.appendChild(detail);
    }
    row.appendChild(status);
    row.appendChild(body);
    resultsEl.appendChild(row);
  });
}

function pill(text, cls) {
  var s = document.createElement('span');
  s.className = 'pill' + (cls ? ' ' + cls : '');
  s.textContent = text;
  return s;
}
