async function postJSON(url, payload){
  const res = await fetch(url, {
    method: 'POST',
    headers: {'Content-Type':'application/json'},
    body: JSON.stringify(payload)
  });
  return res.json();
}
async function getJSON(url){
  const res = await fetch(url);
  return res.json();
}
function val(id){ return parseFloat(document.getElementById(id).value || 0) }

document.getElementById('btnScore').onclick = async () => {
  const features = {
    foot_traffic: val('foot_traffic'),
    competitors_500m: val('competitors_500m'),
    avg_income: val('avg_income'),
    rent_cost: val('rent_cost'),
    age_20s_ratio: val('age_20s_ratio')
  };
  const data = await postJSON('/api/recs/score', {features});
  const out = document.getElementById('out');
  out.textContent = JSON.stringify(data, null, 2);

  // KPI 박스
  const kpi = document.getElementById('kpi');
  kpi.innerHTML = '';
  const scoreBox = document.createElement('div');
  scoreBox.className = 'box';
  scoreBox.innerHTML = '<div>총점</div><div style="font-size:22px;font-weight:800;">' + data.score + '</div>';
  kpi.appendChild(scoreBox);
  Object.entries(data.breakdown).forEach(([k, v]) => {
    const d = document.createElement('div');
    d.className = 'box';
    d.innerHTML = `<div>${k}</div><div class="small">value: ${v.value} · weight: ${v.weight} · contrib: ${v.contrib.toFixed(3)}</div>`;
    kpi.appendChild(d);
  });
};

document.getElementById('btnSample').onclick = async () => {
  const data = await getJSON('/api/recs/sample');
  const tbody = document.querySelector('#tbl tbody');
  tbody.innerHTML = '';
  data.items.forEach(item => {
    const tr = document.createElement('tr');
    const f = item.features;
    tr.innerHTML = `<td>${item.area_name}</td>
      <td><b>${item.score}</b></td>
      <td class="small">${f.foot_traffic}</td>
      <td class="small">${f.competitors_500m}</td>
      <td class="small">${f.avg_income}</td>
      <td class="small">${f.rent_cost}</td>
      <td class="small">${f.age_20s_ratio}</td>`;
    tbody.appendChild(tr);
  });
};

/* -------------------- [React/SwiftUI SPA 자리] --------------------
   추후 이 파일(app.js) 하단에 React 앱 마운트/SwiftUI WebView 브릿지 추가 예정.
   실제 SPA 도입 시 위 데모 함수는 제거/대체됩니다.
------------------------------------------------------------------- */
