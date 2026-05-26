// Interface Médica LTFU — Avaliação de Risco de Abandono
// Estado Global
let listaPacientes   = JSON.parse(localStorage.getItem('ltfu_pacientes') || '[]');
let resultadoAtual   = null;
let graficoGauge     = null;


// Painel Histórico
function alternarHistorico() {
  const painelHistorico     = document.getElementById('painel-historico');
  const sobreposicaoHistorico = document.getElementById('sobreposicao-historico');
  const estaAberto          = painelHistorico.classList.contains('open');

  painelHistorico.classList.toggle('open', !estaAberto);
  sobreposicaoHistorico.classList.toggle('hidden', estaAberto);

  if (!estaAberto) renderizarListaPacientes();
}

function renderizarListaPacientes() {
  const containerLista = document.getElementById('lista-pacientes');
  if (!listaPacientes.length) {
    containerLista.innerHTML = `
      <div class="empty-msg">
        <i data-lucide="inbox" style="width: 32px; height: 32px; margin-bottom: 8px; color: var(--text-light);"></i>
        <p>Nenhum paciente avaliado ainda.</p>
      </div>`;
    lucide.createIcons();
    return;
  }

  containerLista.innerHTML = [...listaPacientes].reverse().map((paciente, indiceInvertido) => {
    const indiceReal = listaPacientes.length - 1 - indiceInvertido;
    const classeRisco = paciente.nivel_risco === 'alto' ? 'alto' : paciente.nivel_risco === 'medio' ? 'medio' : 'baixo';
    const rotuloRisco = paciente.nivel_risco === 'alto' ? 'Alto' : paciente.nivel_risco === 'medio' ? 'Médio' : 'Baixo';
    const dataFormatada = paciente.data && !isNaN(new Date(paciente.data).getTime())
      ? new Date(paciente.data).toLocaleDateString('pt-BR')
      : 'Sem data';

    return `
      <div onclick="abrirPacienteSalvo(${indiceReal})" class="pac-card">
        <button onclick="confirmarRemocao(event, ${indiceReal})" class="btn-remover-card" title="Remover paciente">
          <i data-lucide="trash-2" style="width: 14px; height: 14px;"></i>
        </button>
        <div class="pac-card-name" style="padding-right: 28px;">${paciente.nome}</div>
        <div class="pac-card-info">${paciente.idade} anos · ${dataFormatada}</div>
        <div class="pac-card-risk" style="display: flex; justify-content: space-between; align-items: center; margin-top: 8px;">
          <span class="pac-badge ${classeRisco}">${rotuloRisco}</span>
          <span style="font-size: 0.88rem; font-weight: 700;">${paciente.probabilidade_pct}%</span>
        </div>
      </div>`;
  }).join('');
  lucide.createIcons();
}

function abrirPacienteSalvo(indice) {
  const paciente = listaPacientes[indice];
  preencherFormulario(paciente);
  abrirResultado(paciente);
  alternarHistorico();
}

function preencherFormulario(paciente) {
  if (!paciente) return;
  
  document.getElementById('campo-nome').value = paciente.nome || '';
  document.getElementById('campo-idade').value = paciente.idade || '';
  
  const f = paciente.dados_formulario;
  if (!f) return;
  
  document.getElementById('campo-sexo').value = f.CS_SEXO || '';
  document.getElementById('campo-raca').value = f.CS_RACA || '';
  document.getElementById('campo-escolaridade').value = f.CS_ESCOL_N || '';
  document.getElementById('campo-contatos').value = f.NU_CONTATO !== undefined && f.NU_CONTATO !== null ? f.NU_CONTATO : '';
  document.getElementById('campo-tratamento').value = f.TRATAMENTO || '';
  document.getElementById('campo-hiv').value = f.HIV || '';
  document.getElementById('campo-baciloscopia').value = f.BACILOSC_E || '';
  document.getElementById('campo-raiox').value = f.RAIOX_TORA || '';
  document.getElementById('campo-uf').value = f.SG_UF_NOT || '';
  document.getElementById('campo-aids').value = f.AGRAVAIDS !== undefined ? f.AGRAVAIDS : '9';
  document.getElementById('campo-alcool').value = f.AGRAVALCOO !== undefined ? f.AGRAVALCOO : '9';
  document.getElementById('campo-diabetes').value = f.AGRAVDIABE !== undefined ? f.AGRAVDIABE : '9';
  document.getElementById('campo-doenca-mental').value = f.AGRAVDOENC !== undefined ? f.AGRAVDOENC : '9';
  document.getElementById('campo-drogas').value = f.AGRAVDROGA !== undefined ? f.AGRAVDROGA : '9';
  document.getElementById('campo-tabagismo').value = f.AGRAVTABAC !== undefined ? f.AGRAVTABAC : '9';
  document.getElementById('campo-privado-liberdade').value = f.POP_LIBER !== undefined ? f.POP_LIBER : '2';
  document.getElementById('campo-situacao-rua').value = f.POP_RUA !== undefined ? f.POP_RUA : '2';
  document.getElementById('campo-trat-supervisionado').value = f.TRAT_SUPER !== undefined ? f.TRAT_SUPER : '9';
  document.getElementById('campo-institucionalizado').value = f.INSTITUCIO !== undefined ? f.INSTITUCIO : '0';
  document.getElementById('campo-beneficio').value = f.BENEF_GOV !== undefined ? f.BENEF_GOV : '9';
}

function atualizarContadorPacientes() {
  const contador  = document.getElementById('contador-pacientes');
  const numero    = document.getElementById('numero-pacientes');
  numero.textContent = listaPacientes.length;
  contador.classList.toggle('hidden', listaPacientes.length === 0);
}


// Painel de resultado
function abrirResultado(resultado) {
  resultadoAtual = resultado;

  document.getElementById('resultado-nome').textContent = resultado.nome;
  document.getElementById('resultado-idade').textContent = `${resultado.idade} anos`;
  document.getElementById('gauge-percentual').textContent = `${resultado.probabilidade_pct}%`;

  const badgeRisco = document.getElementById('badge-risco');
  const descricoes = {
    alto:  'Paciente com alto risco de abandono. Recomenda-se acompanhamento intensivo, contato frequente e envolvimento da família e equipe de saúde.',
    medio: 'Paciente com risco moderado. Monitore de perto, avalie barreiras ao tratamento e reforce a adesão nas consultas.',
    baixo: 'Paciente com baixo risco de abandono. Continue o acompanhamento padrão e reforce a educação em saúde.',
  };
  const configBadge = {
    alto:  { classe: 'alto',  texto: 'Risco Alto'  },
    medio: { classe: 'medio', texto: 'Risco Médio' },
    baixo: { classe: 'baixo', texto: 'Risco Baixo' },
  };
  const cfg = configBadge[resultado.nivel_risco] || configBadge.baixo;
  badgeRisco.className = `risk-badge ${cfg.classe}`;
  badgeRisco.textContent = cfg.texto;
  document.getElementById('descricao-resultado').textContent = descricoes[resultado.nivel_risco] || '';

  // Gauge (doughnut chart)
  const prob    = resultado.probabilidade_pct / 100;
  const coresGauge = { alto: '#EF4444', medio: '#F59E0B', baixo: '#10B981' };
  const corGauge   = coresGauge[resultado.nivel_risco] || '#3B82F6';

  if (graficoGauge) graficoGauge.destroy();
  graficoGauge = new Chart(document.getElementById('grafico-gauge'), {
    type: 'doughnut',
    data: {
      datasets: [{
        data: [prob, 1 - prob],
        backgroundColor: [corGauge, '#F3F4F6'],
        borderWidth: 0,
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '74%',
      plugins: { legend: { display: false }, tooltip: { enabled: false } },
      animation: { animateRotate: true, duration: 700 },
    }
  });

  // Resetar botão salvar
  const botaoSalvar = document.getElementById('botao-salvar');
  botaoSalvar.innerHTML = '<i data-lucide="save" style="width: 16px; height: 16px;"></i> Salvar no histórico';
  botaoSalvar.disabled = false;
  botaoSalvar.className = 'btn-save';
  botaoSalvar.style.background = '';
  botaoSalvar.style.cursor = '';
  lucide.createIcons();

  // Renderizar o resumo clínico
  renderizarResumoClinico();

  document.getElementById('painel-resultado').classList.add('open');
  document.getElementById('sobreposicao-resultado').classList.remove('hidden');
}

function fecharResultado() {
  document.getElementById('painel-resultado').classList.remove('open');
  document.getElementById('sobreposicao-resultado').classList.add('hidden');
  document.getElementById('resumo-clinico').classList.add('hidden');
}

// Formulário — Calcular Risco
async function calcularRisco(evento) {
  evento.preventDefault();
  definirCarregando(true);

  const dadosPaciente = coletarDados();

  try {
    const resposta = await fetch('http://localhost:8000/predict', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(dadosPaciente),
    });
    if (!resposta.ok) throw new Error(`Erro ${resposta.status}`);

    const resultado = await resposta.json();
    resultado.nome  = document.getElementById('campo-nome').value.trim();
    resultado.idade = parseInt(document.getElementById('campo-idade').value);
    resultado.data  = new Date().toISOString();
    resultado.dados_formulario = dadosPaciente;

    definirCarregando(false);
    abrirResultado(resultado);
  } catch (erro) {
    definirCarregando(false);
    mostrarErroServidor();
  }
}

function coletarDados() {
  return {
    idade_anos:  parseInt(document.getElementById('campo-idade').value) || null,
    CS_SEXO:     document.getElementById('campo-sexo').value || null,
    CS_RACA:     document.getElementById('campo-raca').value || null,
    CS_ESCOL_N:  document.getElementById('campo-escolaridade').value || null,
    NU_CONTATO:  parseInt(document.getElementById('campo-contatos').value) || 0,
    TRATAMENTO:  document.getElementById('campo-tratamento').value || null,
    HIV:         document.getElementById('campo-hiv').value || null,
    BACILOSC_E:  document.getElementById('campo-baciloscopia').value || null,
    RAIOX_TORA:  document.getElementById('campo-raiox').value || null,
    SG_UF_NOT:   document.getElementById('campo-uf').value || null,
    AGRAVAIDS:   document.getElementById('campo-aids').value,
    AGRAVALCOO:  document.getElementById('campo-alcool').value,
    AGRAVDIABE:  document.getElementById('campo-diabetes').value,
    AGRAVDOENC:  document.getElementById('campo-doenca-mental').value,
    AGRAVDROGA:  document.getElementById('campo-drogas').value,
    AGRAVTABAC:  document.getElementById('campo-tabagismo').value,
    POP_LIBER:   document.getElementById('campo-privado-liberdade').value,
    POP_RUA:     document.getElementById('campo-situacao-rua').value,
    TRAT_SUPER:  document.getElementById('campo-trat-supervisionado').value,
    INSTITUCIO:  document.getElementById('campo-institucionalizado').value,
    BENEF_GOV:   document.getElementById('campo-beneficio').value,
  };
}


// Salvar Paciente
function salvarPaciente() {
  if (!resultadoAtual) return;
  const jaSalvo = listaPacientes.some(
    p => p.nome === resultadoAtual.nome && p.data === resultadoAtual.data
  );
  if (jaSalvo) return;

  listaPacientes.push(resultadoAtual);
  localStorage.setItem('ltfu_pacientes', JSON.stringify(listaPacientes));
  atualizarContadorPacientes();

  const botaoSalvar = document.getElementById('botao-salvar');
  botaoSalvar.innerHTML = '<i data-lucide="check" style="width: 16px; height: 16px;"></i> Salvo com sucesso!';
  botaoSalvar.disabled = true;
  botaoSalvar.className = 'btn-save';
  botaoSalvar.style.background = 'var(--baixo)';
  botaoSalvar.style.cursor = 'not-allowed';
  lucide.createIcons();
}


// Toast — Erro de Servidor
function mostrarErroServidor() {
  const anterior = document.getElementById('toast-erro-servidor');
  if (anterior) anterior.remove();

  const toast = document.createElement('div');
  toast.id = 'toast-erro-servidor';
  toast.className = 'toast-erro';
  toast.innerHTML = `
    <span class="toast-icon">⚠️</span>
    <div class="toast-body">
      <strong>Servidor offline</strong>
      <span>Não foi possível conectar ao backend. Inicie com:</span>
      <code>uvicorn app.backend.main:app --reload --port 8000</code>
    </div>
    <button onclick="this.parentElement.remove()" class="toast-close">✕</button>
  `;
  document.body.appendChild(toast);
  setTimeout(() => { if (toast.parentElement) toast.remove(); }, 9000);
}


// Utilitários
function definirCarregando(carregando) {
  document.getElementById('texto-botao').classList.toggle('hidden', carregando);
  document.getElementById('icone-botao').classList.toggle('hidden', carregando);
  document.getElementById('spinner-botao').classList.toggle('hidden', !carregando);
  document.getElementById('botao-calcular').disabled = carregando;
}

let indiceParaRemover = null;

function confirmarRemocao(evento, indice) {
  evento.stopPropagation();
  indiceParaRemover = indice;
  
  const paciente = listaPacientes[indice];
  document.getElementById('modal-paciente-nome').textContent = paciente.nome;
  
  document.getElementById('modal-confirmar').classList.remove('hidden');
}

function fecharModalConfirmar() {
  document.getElementById('modal-confirmar').classList.add('hidden');
  indiceParaRemover = null;
}

// Configurar o clique do botão de remoção no modal
document.getElementById('btn-modal-confirmar-remover').onclick = function() {
  if (indiceParaRemover !== null) {
    const pacRemovido = listaPacientes[indiceParaRemover];
    if (resultadoAtual && resultadoAtual.nome === pacRemovido.nome && resultadoAtual.data === pacRemovido.data) {
      fecharResultado();
    }
    
    listaPacientes.splice(indiceParaRemover, 1);
    localStorage.setItem('ltfu_pacientes', JSON.stringify(listaPacientes));
    atualizarContadorPacientes();
    renderizarListaPacientes();
    fecharModalConfirmar();
  }
};

function renderizarResumoClinico() {
  const container = document.getElementById('resumo-clinico');
  const grid = document.getElementById('resumo-itens');
  if (!container || !grid) return;

  const tratamento = obterTextoSelect('campo-tratamento');
  const hiv = obterTextoSelect('campo-hiv');
  const baciloscopia = obterTextoSelect('campo-baciloscopia');
  const raiox = obterTextoSelect('campo-raiox');
  const uf = obterTextoSelect('campo-uf');
  const dot = obterTextoSelect('campo-trat-supervisionado');
  const benef = obterTextoSelect('campo-beneficio');
  
  // Coletar agravidades ativas (Sim)
  const agravidades = [];
  if (document.getElementById('campo-aids').value === '1') agravidades.push('AIDS');
  if (document.getElementById('campo-alcool').value === '1') agravidades.push('Álcool');
  if (document.getElementById('campo-diabetes').value === '1') agravidades.push('Diabetes');
  if (document.getElementById('campo-doenca-mental').value === '1') agravidades.push('Doença Mental');
  if (document.getElementById('campo-drogas').value === '1') agravidades.push('Drogas');
  if (document.getElementById('campo-tabagismo').value === '1') agravidades.push('Tabagismo');
  if (document.getElementById('campo-privado-liberdade').value === '1') agravidades.push('Priv. Liberdade');
  if (document.getElementById('campo-situacao-rua').value === '1') agravidades.push('Sit. Rua');
  if (document.getElementById('campo-institucionalizado').value === '1') agravidades.push('Institucionalizado');

  const listaAgravidades = agravidades.length > 0 ? agravidades.join(', ') : 'Nenhuma';

  const itens = [];
  if (tratamento && tratamento !== 'Selecione') itens.push({ label: 'Tratamento', valor: tratamento });
  if (uf && uf !== 'Selecione') itens.push({ label: 'UF de Notificação', valor: uf });
  if (hiv && hiv !== 'Selecione') itens.push({ label: 'Sorologia HIV', valor: hiv });
  if (baciloscopia && baciloscopia !== 'Selecione') itens.push({ label: 'Baciloscopia', valor: baciloscopia });
  if (raiox && raiox !== 'Selecione') itens.push({ label: 'Raio-X Tórax', valor: raiox });
  if (dot && dot !== 'Selecione') itens.push({ label: 'Trat. Supervisionado (DOT)', valor: dot });
  if (benef && benef !== 'Selecione') itens.push({ label: 'Benefício Gov.', valor: benef });
  itens.push({ label: 'Vulnerabilidades', valor: listaAgravidades });

  grid.innerHTML = itens.map(item => `
    <div class="resumo-item">
      <span class="resumo-label">${item.label}</span>
      <span class="resumo-valor">${item.valor}</span>
    </div>
  `).join('');

  container.classList.remove('hidden');
}

function obterTextoSelect(idSelect) {
  const el = document.getElementById(idSelect);
  if (!el) return '';
  if (el.tagName === 'SELECT') {
    return el.options[el.selectedIndex]?.text || '';
  }
  return el.value || '';
}

atualizarContadorPacientes();
lucide.createIcons();
