// Dashboard LTFU — Resultados do Modelo

// Estado Global
let dadosBrutos     = [];
let dadosFiltrados  = [];
let paginaAtual     = 1;
const ITENS_POR_PAGINA = 20;

// Referências de gráficos 
let graficoPizza       = null;
let graficoHistograma  = null;
let graficoAcertos     = null;
let graficoRealPrevisto = null;


// Upload e Drop
const zonaArrastoElemn = document.getElementById('zona-drop');
const entradaCsvElem   = document.getElementById('entrada-csv');

zonaArrastoElemn.addEventListener('dragover', (evento) => {
  evento.preventDefault();
  zonaArrastoElemn.classList.add('dragover');
});
zonaArrastoElemn.addEventListener('dragleave', () => {
  zonaArrastoElemn.classList.remove('dragover');
});
zonaArrastoElemn.addEventListener('drop', (evento) => {
  evento.preventDefault();
  zonaArrastoElemn.classList.remove('dragover');
  const arquivo = evento.dataTransfer.files[0];
  if (arquivo) processarCsv(arquivo);
});
entradaCsvElem.addEventListener('change', (evento) => {
  if (evento.target.files[0]) processarCsv(evento.target.files[0]);
});

function processarCsv(arquivo) {
  const leitor = new FileReader();
  leitor.onload = (evento) => {
    const linhas    = evento.target.result.trim().split('\n');
    const cabecalho = linhas[0].split(',').map(c => c.trim().replace(/"/g, ''));

    dadosBrutos = linhas.slice(1).map((linha, indice) => {
      const valores = linha.split(',').map(v => v.trim().replace(/"/g, ''));
      const registro = { _indice: indice + 1 };
      cabecalho.forEach((col, j) => registro[col] = valores[j] || '');
      return registro;
    });

    dadosBrutos.forEach(r => {
      r.id              = r.id || String(r._indice);
      r.probabilidade_ltfu = parseFloat(r.probabilidade_ltfu) || 0;
      r.nivel_risco     = (r.nivel_risco || '').toLowerCase();
      r.predicao_modelo = r.predicao_modelo || '';
      r.resultado_real  = r.resultado_real  || '';
    });

    dadosFiltrados = [...dadosBrutos];
    paginaAtual    = 1;
    renderizarDashboard();
    document.getElementById('zona-drop').classList.add('hidden');
    document.getElementById('painel-dashboard').classList.remove('hidden');
  };
  leitor.readAsText(arquivo, 'UTF-8');
}


// Renderização principal
function renderizarDashboard() {
  renderizarKpis();
  renderizarMetricasTecnicas();
  renderizarDistribuicao();
  renderizarHistograma();
  renderizarAcertosPorRisco();
  renderizarRealVsPrevisto();
  renderizarTabela();
  lucide.createIcons();
}


// KPIs
function renderizarKpis() {
  const total       = dadosBrutos.length;
  const qtdAltos    = dadosBrutos.filter(r => r.nivel_risco === 'alto').length;
  const qtdMedios   = dadosBrutos.filter(r => r.nivel_risco === 'medio').length;
  const qtdBaixos   = dadosBrutos.filter(r => r.nivel_risco === 'baixo').length;
  const probMedia   = dadosBrutos.reduce((soma, r) => soma + r.probabilidade_ltfu, 0) / total;
  const ltfuReais   = dadosBrutos.filter(r => normalizar(r.resultado_real) === 'abandona').length;
  const acertos     = dadosBrutos.filter(r => normalizar(r.predicao_modelo) === normalizar(r.resultado_real)).length;
  const acuracia    = acertos / total;

  const kpis = [
    { rotulo: 'Total',          valor: total,                         sub: 'pacientes',               classe: 'primary' },
    { rotulo: 'Risco Alto',     valor: qtdAltos,                      sub: pct(qtdAltos, total)+'%',  classe: 'alto'   },
    { rotulo: 'Risco Médio',    valor: qtdMedios,                     sub: pct(qtdMedios,total)+'%',  classe: 'medio' },
    { rotulo: 'Risco Baixo',    valor: qtdBaixos,                     sub: pct(qtdBaixos,total)+'%',  classe: 'baixo' },
    { rotulo: 'Prob. Média',    valor: (probMedia*100).toFixed(1)+'%',sub: 'abandono',                classe: 'primary'  },
    { rotulo: 'LTFU Reais',     valor: ltfuReais,                     sub: pct(ltfuReais,total)+'%',  classe: 'alto'   },
  ];

  document.getElementById('linha-kpis').innerHTML = kpis.map(k => `
    <div class="kpi-card ${k.classe}">
      <div class="kpi-label">${k.rotulo}</div>
      <div class="kpi-value">${k.valor}</div>
      <div class="kpi-sub">${k.sub}</div>
    </div>
  `).join('');
}


// Métricas Técnicas
function renderizarMetricasTecnicas() {
  const verdadeiroPositivo = dadosBrutos.filter(r =>
    normalizar(r.predicao_modelo) === 'abandona' && normalizar(r.resultado_real) === 'abandona'
  ).length;
  const falsoPositivo = dadosBrutos.filter(r =>
    normalizar(r.predicao_modelo) === 'abandona' && normalizar(r.resultado_real) === 'conclui'
  ).length;
  const falsoNegativo = dadosBrutos.filter(r =>
    normalizar(r.predicao_modelo) === 'conclui' && normalizar(r.resultado_real) === 'abandona'
  ).length;
  const verdadeiroNegativo = dadosBrutos.filter(r =>
    normalizar(r.predicao_modelo) === 'conclui' && normalizar(r.resultado_real) === 'conclui'
  ).length;

  const precisao = verdadeiroPositivo / (verdadeiroPositivo + falsoPositivo) || 0;
  const recall   = verdadeiroPositivo / (verdadeiroPositivo + falsoNegativo) || 0;
  const f1       = 2 * precisao * recall / (precisao + recall) || 0;
  const acuracia = (verdadeiroPositivo + verdadeiroNegativo) / dadosBrutos.length;

  const metricas = [
    { rotulo: 'Precisão',   valor: precisao.toFixed(3), descricao: 'dos previstos como abandono, quantos realmente abandonaram' },
    { rotulo: 'Recall',     valor: recall.toFixed(3),   descricao: 'dos que realmente abandonaram, quantos foram identificados' },
    { rotulo: 'F1-Score',   valor: f1.toFixed(3),       descricao: 'média harmônica entre precisão e recall' },
    { rotulo: 'Acurácia',   valor: (acuracia*100).toFixed(1)+'%', descricao: 'proporção de predições corretas no total' },
  ];

  document.getElementById('grade-metricas').innerHTML = metricas.map(m => `
    <div class="metric-card">
      <div class="metric-label">${m.rotulo}</div>
      <div class="metric-value">${m.valor}</div>
      <div class="metric-desc">${m.descricao}</div>
    </div>
  `).join('');

  document.getElementById('val-vp').textContent = verdadeiroPositivo;
  document.getElementById('val-fp').textContent = falsoPositivo;
  document.getElementById('val-fn').textContent = falsoNegativo;
  document.getElementById('val-vn').textContent = verdadeiroNegativo;
}


// Distribuição de Risco (Pizza + Barras)
function renderizarDistribuicao() {
  const total   = dadosBrutos.length;
  const altos   = dadosBrutos.filter(r => r.nivel_risco === 'alto').length;
  const medios  = dadosBrutos.filter(r => r.nivel_risco === 'medio').length;
  const baixos  = dadosBrutos.filter(r => r.nivel_risco === 'baixo').length;

  if (graficoPizza) graficoPizza.destroy();
  graficoPizza = new Chart(document.getElementById('grafico-pizza'), {
    type: 'doughnut',
    data: {
      labels: ['Alto', 'Médio', 'Baixo'],
      datasets: [{ data: [altos, medios, baixos],
        backgroundColor: ['#EF4444','#F59E0B','#10B981'],
        borderWidth: 2, borderColor: '#fff' }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 600 },
      plugins: { legend: { display: false } },
      cutout: '68%'
    }
  });

  document.getElementById('barras-risco').innerHTML = [
    { rotulo: 'Alto',  qtd: altos,  classe: 'rb-alto'   },
    { rotulo: 'Médio', qtd: medios, classe: 'rb-medio' },
    { rotulo: 'Baixo', qtd: baixos, classe: 'rb-baixo' },
  ].map(({ rotulo, qtd, classe }) => {
    const perc = pct(qtd, total);
    return `
      <div class="risk-bar-item ${classe}">
        <div class="risk-bar-label">
          <span>${rotulo}</span><span>${perc}% (${qtd})</span>
        </div>
        <div class="risk-bar-track">
          <div class="risk-bar-fill" style="width:${perc}%"></div>
        </div>
      </div>`;
  }).join('');
}


// Histograma de probabilidade
function renderizarHistograma() {
  const faixas = Array.from({ length: 10 }, (_, i) => ({
    rotulo: `${i*10}-${(i+1)*10}%`, contagem: 0
  }));
  dadosBrutos.forEach(r => {
    const indice = Math.min(Math.floor(r.probabilidade_ltfu * 10), 9);
    faixas[indice].contagem++;
  });
  const cores = faixas.map((_, i) => i >= 6 ? '#EF4444' : i >= 3 ? '#F59E0B' : '#10B981');

  if (graficoHistograma) graficoHistograma.destroy();
  graficoHistograma = new Chart(document.getElementById('grafico-histograma'), {
    type: 'bar',
    data: {
      labels: faixas.map(f => f.rotulo),
      datasets: [{ label: 'Pacientes', data: faixas.map(f => f.contagem),
        backgroundColor: cores, borderRadius: 4 }]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: { legend: { display: false } },
      scales: {
        y: { beginAtZero: true, grid: { color: '#F3F4F6' } },
        x: { grid: { display: false } }
      }
    }
  });
}


// Acertos por nivel de risco
function renderizarAcertosPorRisco() {
  const niveis = ['alto', 'medio', 'baixo'];
  const qtdAcertos = [], qtdErros = [];

  niveis.forEach(nivel => {
    const grupo   = dadosBrutos.filter(r => r.nivel_risco === nivel);
    const acertos = grupo.filter(r => normalizar(r.predicao_modelo) === normalizar(r.resultado_real)).length;
    qtdAcertos.push(acertos);
    qtdErros.push(grupo.length - acertos);
  });

  if (graficoAcertos) graficoAcertos.destroy();
  graficoAcertos = new Chart(document.getElementById('grafico-acertos'), {
    type: 'bar',
    data: {
      labels: ['Alto', 'Médio', 'Baixo'],
      datasets: [
        { label: 'Acertos', data: qtdAcertos, backgroundColor: '#10B981', borderRadius: 4 },
        { label: 'Erros',   data: qtdErros,   backgroundColor: '#EF4444', borderRadius: 4 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: { legend: { position: 'top' } },
      scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#F3F4F6' } } }
    }
  });
}


// Real vs Previsto
function renderizarRealVsPrevisto() {
  const abandonaReal   = dadosBrutos.filter(r => normalizar(r.resultado_real)  === 'abandona').length;
  const concluiReal    = dadosBrutos.filter(r => normalizar(r.resultado_real)  === 'conclui').length;
  const abandonaPrev   = dadosBrutos.filter(r => normalizar(r.predicao_modelo) === 'abandona').length;
  const concluiPrev    = dadosBrutos.filter(r => normalizar(r.predicao_modelo) === 'conclui').length;

  if (graficoRealPrevisto) graficoRealPrevisto.destroy();
  graficoRealPrevisto = new Chart(document.getElementById('grafico-real-previsto'), {
    type: 'bar',
    data: {
      labels: ['Abandonaram', 'Concluíram'],
      datasets: [
        { label: 'Real',    data: [abandonaReal, concluiReal], backgroundColor: '#2563EB', borderRadius: 4 },
        { label: 'Previsto',data: [abandonaPrev, concluiPrev], backgroundColor: '#93C5FD', borderRadius: 4 },
      ]
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      animation: { duration: 500 },
      plugins: { legend: { position: 'top' } },
      scales: { x: { grid: { display: false } }, y: { beginAtZero: true, grid: { color: '#F3F4F6' } } }
    }
  });
}


// Tabela com paginação
document.getElementById('busca-tabela').addEventListener('input', filtrarTabela);
document.getElementById('filtro-risco').addEventListener('change', filtrarTabela);

function filtrarTabela() {
  const termo      = document.getElementById('busca-tabela').value.toLowerCase();
  const riscoFiltro = document.getElementById('filtro-risco').value;
  dadosFiltrados = dadosBrutos.filter(r => {
    const buscaOk = !termo || String(r.id).includes(termo) || r.nivel_risco.includes(termo);
    const riscoOk = !riscoFiltro || r.nivel_risco === riscoFiltro;
    return buscaOk && riscoOk;
  });
  paginaAtual = 1;
  renderizarTabela();
}

function renderizarTabela() {
  const inicio   = (paginaAtual - 1) * ITENS_POR_PAGINA;
  const paginaDados = dadosFiltrados.slice(inicio, inicio + ITENS_POR_PAGINA);
  const corpoTabela = document.getElementById('corpo-tabela');

  corpoTabela.innerHTML = paginaDados.map(r => {
    const prob    = r.probabilidade_ltfu;
    const percVal = (prob * 100).toFixed(1);
    const classeRisco = r.nivel_risco === 'alto' ? 'alto' : r.nivel_risco === 'medio' ? 'medio' : 'baixo';
    const rotuloRisco = r.nivel_risco === 'alto' ? 'Alto' : r.nivel_risco === 'medio' ? 'Médio' : 'Baixo';
    const acerto = normalizar(r.predicao_modelo) === normalizar(r.resultado_real);
    const prevLabel = normalizar(r.predicao_modelo) === 'abandona' ? 'Abandona' : 'Conclui';
    const realLabel = normalizar(r.resultado_real)  === 'abandona' ? 'Abandona' : 'Conclui';

    return `
      <tr>
        <td>${r.id}</td>
        <td>
          <div class="prob-cell">
            <div class="prob-track">
              <div class="prob-fill ${classeRisco}" style="width:${percVal}%"></div>
            </div>
            <span class="prob-label">${percVal}%</span>
          </div>
        </td>
        <td>
          <span class="badge ${classeRisco}">${rotuloRisco}</span>
        </td>
        <td>${prevLabel}</td>
        <td>${realLabel}</td>
        <td class="${acerto ? 'acerto-sim' : 'acerto-nao'}">
          ${acerto ? '✓ Sim' : '✗ Não'}
        </td>
      </tr>`;
  }).join('');

  renderizarPaginacao();
}

function renderizarPaginacao() {
  const totalPaginas = Math.ceil(dadosFiltrados.length / ITENS_POR_PAGINA);
  const elem = document.getElementById('paginacao');
  if (totalPaginas <= 1) { elem.innerHTML = ''; return; }

  let html = `<span class="page-info">Página ${paginaAtual} de ${totalPaginas} · ${dadosFiltrados.length} registros</span>`;
  if (paginaAtual > 1)
    html += `<button onclick="irParaPagina(${paginaAtual-1})" class="page-btn">‹</button>`;

  const inicio = Math.max(1, paginaAtual - 2);
  const fim    = Math.min(totalPaginas, paginaAtual + 2);
  for (let i = inicio; i <= fim; i++) {
    html += `<button onclick="irParaPagina(${i})"
      class="page-btn ${i === paginaAtual ? 'active' : ''}">${i}</button>`;
  }
  if (paginaAtual < totalPaginas)
    html += `<button onclick="irParaPagina(${paginaAtual+1})" class="page-btn">›</button>`;

  elem.innerHTML = html;
}

function irParaPagina(numero) {
  paginaAtual = numero;
  renderizarTabela();
  document.getElementById('painel-dashboard').scrollIntoView({ behavior: 'smooth', block: 'start' });
}


function pct(valor, total) { return total ? (valor / total * 100).toFixed(1) : '0.0'; }
function normalizar(str)   { return (str || '').toLowerCase().trim().normalize("NFD").replace(/[\u0300-\u036f]/g, ""); }
lucide.createIcons();
