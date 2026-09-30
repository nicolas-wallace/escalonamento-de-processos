(() => {
  "use strict";

  const ALGORITMOS = [
    { id: "fcfs", nome: "FCFS", tipo: "cooperativo" },
    { id: "sjf", nome: "SJF", tipo: "cooperativo" },
    { id: "srtf", nome: "SRTF", tipo: "preemptivo" },
    { id: "prioridade_sem_preempcao", nome: "PRIOc", tipo: "cooperativo" },
    { id: "prioridade_com_preempcao", nome: "PRIOp", tipo: "preemptivo" },
    { id: "round_robin", nome: "RR", tipo: "preemptivo", params: ["quantum"] },
    { id: "round_robin_prioridade_aging", nome: "RR (aging)", tipo: "preemptivo", params: ["quantum", "aging"] },
  ];

  const CORES = ["#4F7CE8", "#E8A33D", "#8E6BD9", "#3FB68B", "#E0607E", "#3AA7C9",
                 "#D9793A", "#7C8A99", "#C45FB0", "#8FA63E", "#5B7FA6", "#A0785A"];
  const EXEMPLO = [[0, 5, 2], [0, 2, 3], [1, 4, 1], [3, 3, 4]];
  const LIMITE = 12;
  const NS = "http://www.w3.org/2000/svg";

  const S = {
    processos: [],
    quantum: "2",
    aging: "1",
    algoritmo: "round_robin",
    resultados: null,
    t: 0,
    tocando: false,
    timer: null,
    velocidade: 1,
    aba: "gantt",
    sequencia: 0,
    espera: null,
  };

  const $ = (sel) => document.querySelector(sel);

  function el(tag, props = {}, ...filhos) {
    const e = document.createElement(tag);
    for (const [k, v] of Object.entries(props)) {
      if (k === "class") e.className = v;
      else if (k === "text") e.textContent = v;
      else if (k.startsWith("on")) e.addEventListener(k.slice(2), v);
      else e.setAttribute(k, v);
    }
    e.append(...filhos);
    return e;
  }

  function sv(tag, props = {}, ...filhos) {
    const e = document.createElementNS(NS, tag);
    for (const [k, v] of Object.entries(props)) e.setAttribute(k, v);
    e.append(...filhos);
    return e;
  }

  const fmt = (v) => v.toLocaleString("pt-BR", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  const cor = (i) => CORES[i % CORES.length];

  function luminancia(hex) {
    const n = parseInt(hex.slice(1), 16);
    const [r, g, b] = [16, 8, 0].map((s) => {
      const c = ((n >> s) & 255) / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * r + 0.7152 * g + 0.0722 * b;
  }

  function corTexto(hex) {
    const L = luminancia(hex);
    return 1.05 / (L + 0.05) > (L + 0.05) / 0.067 ? "#FFFFFF" : "#1B2233";
  }

  const atual = () => S.resultados[S.algoritmo];
  const total = () => atual().linha.length;
  const indiceDe = (pid) => parseInt(pid.slice(1), 10) - 1;

  // ---------- entrada ----------

  function inteiro(txt) {
    const s = String(txt).trim();
    return /^-?\d+$/.test(s) ? parseInt(s, 10) : null;
  }

  function marcar(seletor, ruim) {
    const campo = document.querySelector(seletor);
    if (campo) campo.classList.toggle("invalido", ruim);
  }

  function validar() {
    if (!S.processos.length) return { erro: "Adicione pelo menos um processo." };
    const dados = { processos: [] };
    let erro = "";
    S.processos.forEach((p, i) => {
      const c = inteiro(p.chegada), d = inteiro(p.duracao), pr = inteiro(p.prioridade);
      const vazio = (campo) => String(p[campo]).trim() === "";
      const ruim = {
        chegada: !vazio("chegada") && (c === null || c < 0),
        duracao: !vazio("duracao") && (d === null || d < 1),
        prioridade: !vazio("prioridade") && (pr === null || pr < 0),
      };
      for (const campo of Object.keys(ruim)) marcar(`#tabela-processos input[data-i="${i}"][data-campo="${campo}"]`, ruim[campo]);
      if (!erro && ruim.chegada) erro = `P${i + 1}: a chegada deve ser um inteiro maior ou igual a 0.`;
      if (!erro && ruim.duracao) erro = `P${i + 1}: a duração deve ser um inteiro maior ou igual a 1.`;
      if (!erro && ruim.prioridade) erro = `P${i + 1}: a prioridade deve ser um inteiro maior ou igual a 0.`;
      if (!erro && (vazio("chegada") || vazio("duracao") || vazio("prioridade"))) erro = `Preencha chegada, duração e prioridade de P${i + 1}.`;
      dados.processos.push({ chegada: c, duracao: d, prioridade: pr });
    });
    const q = inteiro(S.quantum), a = inteiro(S.aging);
    marcar("#quantum", q === null || q < 1 || q > 100);
    marcar("#aging", a === null || a < 0 || a > 100);
    if (!erro && (q === null || q < 1 || q > 100)) erro = "O quantum deve ser um inteiro entre 1 e 100.";
    if (!erro && (a === null || a < 0 || a > 100)) erro = "O aging deve ser um inteiro entre 0 e 100.";
    dados.quantum = q;
    dados.aging = a;
    return { erro, dados };
  }

  function mostrarAviso(texto) { $("#aviso").textContent = texto; }

  function renderTabela() {
    const corpo = $("#tabela-processos");
    corpo.replaceChildren(...S.processos.map((p, i) => {
      const campo = (nome) => el("input", {
        type: "number", inputmode: "numeric", step: "1", min: "0",
        value: p[nome], "data-i": String(i), "data-campo": nome,
        "aria-label": `${nome} de P${i + 1}`,
        oninput: (ev) => { S.processos[i][nome] = ev.target.value; agendar(); },
      });
      return el("tr", {},
        el("td", {}, el("span", { class: "amostra", style: `background:${cor(i)}` }), `P${i + 1}`),
        el("td", {}, campo("chegada")),
        el("td", {}, campo("duracao")),
        el("td", {}, campo("prioridade")),
        el("td", {}, el("button", {
          class: "remover", type: "button", title: `Remover P${i + 1}`, "aria-label": `Remover P${i + 1}`,
          onclick: () => { S.processos.splice(i, 1); renderTabela(); atualizar(); },
        }, "×")));
    }));
    $("#btn-add").disabled = S.processos.length >= LIMITE;
  }

  function carregar(lista) {
    S.processos = lista.map(([c, d, p]) => ({ chegada: String(c), duracao: String(d), prioridade: String(p) }));
    renderTabela();
    atualizar();
  }

  async function lerArquivo(arquivo) {
    const linhas = (await arquivo.text()).split(/\r?\n/).filter((l) => l.trim());
    const novos = [];
    for (const [i, linha] of linhas.entries()) {
      const p = linha.trim().split(/\s+/);
      if (p.length < 3 || !p.slice(0, 3).every((x) => /^-?\d+$/.test(x))) {
        mostrarAviso(`Linha ${i + 1} do arquivo inválida: esperados 3 inteiros (chegada duração prioridade).`);
        return;
      }
      novos.push([p[0], p[1], p[2]]);
    }
    if (!novos.length) { mostrarAviso("O arquivo não tem processos."); return; }
    if (novos.length > LIMITE) { mostrarAviso(`O arquivo tem mais de ${LIMITE} processos.`); return; }
    carregar(novos);
  }

  // ---------- comunicação com o simulador ----------

  function agendar() {
    clearTimeout(S.espera);
    S.espera = setTimeout(atualizar, 140);
  }

  async function atualizar() {
    const v = validar();
    mostrarAviso(v.erro);
    $(".coluna-dir").classList.toggle("desatualizado", Boolean(v.erro));
    if (v.erro) return;
    const minha = ++S.sequencia;
    try {
      const resp = await fetch("/api/simular", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(v.dados),
      });
      const json = await resp.json();
      if (!resp.ok) throw new Error(json.erro || "erro desconhecido");
      if (minha !== S.sequencia) return;
      S.resultados = json.resultados;
      parar();
      S.t = total();
      renderTudo();
    } catch (erro) {
      mostrarAviso(`Não foi possível simular: ${erro.message}`);
    }
  }

  // ---------- desenho ----------

  function renderAlgoritmos() {
    $("#algoritmos").replaceChildren(...ALGORITMOS.map((a) => el("button", {
      class: "chip", type: "button", "aria-pressed": String(a.id === S.algoritmo),
      onclick: () => selecionar(a.id),
    }, a.nome)));
    const a = ALGORITMOS.find((x) => x.id === S.algoritmo);
    const usa = a.params || [];
    $("#campo-quantum").classList.toggle("inativo", !usa.includes("quantum"));
    $("#campo-aging").classList.toggle("inativo", !usa.includes("aging"));
  }

  function selecionar(id) {
    S.algoritmo = id;
    parar();
    if (S.resultados) { S.t = total(); renderTudo(); } else renderAlgoritmos();
  }

  function renderMetricas() {
    const r = atual();
    $("#m-tt").textContent = fmt(r.tt_medio);
    $("#m-tw").textContent = fmt(r.tw_medio);
    $("#m-tr").textContent = fmt(r.tr_medio);
    $("#m-trocas").textContent = String(r.trocas);
    $("#m-total").textContent = `${total()} s`;
  }

  function trechos(linha, valor) {
    const lista = [];
    linha.forEach((x, i) => {
      const ultimo = lista[lista.length - 1];
      if (x === valor && ultimo && ultimo.fim === i) ultimo.fim = i + 1;
      else if (x === valor) lista.push({ ini: i, fim: i + 1 });
    });
    return lista;
  }

  function renderGantt() {
    const r = atual(), T = total(), t = S.t, n = r.processos.length;
    const unit = Math.max(24, Math.min(54, Math.floor(700 / T)));
    const L = 48, topo = 12, h = 34, barra = 22;
    const yCpu = topo + n * h + 10, yEixo = yCpu + 38, alt = yEixo + 30;
    const larg = L + T * unit + 16;
    const x = (s) => L + s * unit;

    const resumo = r.processos.map((p) => `${p.pid}: ${trechos(r.linha, p.pid).map((c) => `${c.ini} a ${c.fim}`).join(", ")}`).join("; ");
    const g = sv("svg", { viewBox: `0 0 ${larg} ${alt}`, width: "100%", role: "img", "aria-label": `Gráfico. ${resumo}` });
    g.style.minWidth = `${Math.min(larg, T * 24 + L + 16)}px`;

    for (let s = 0; s <= T; s++) g.append(sv("line", { class: "g-grade", x1: x(s), y1: topo - 4, x2: x(s), y2: yEixo }));

    r.processos.forEach((p, i) => {
      const y = topo + i * h + (h - barra) / 2;
      const fim = Math.min(p.termino, t);
      g.append(sv("text", { class: "g-rotulo", x: 4, y: y + barra / 2, "dominant-baseline": "central" }, document.createTextNode(p.pid)));
      if (p.chegada < fim) {
        g.append(sv("rect", { class: "g-espera", x: x(p.chegada), y, width: x(fim) - x(p.chegada), height: barra, rx: 4 }));
      }
      for (const c of trechos(r.linha, p.pid)) {
        if (c.ini >= t) continue;
        const f = Math.min(c.fim, t);
        const titulo = sv("title", {}, document.createTextNode(`${p.pid} executa de ${c.ini} a ${c.fim}`));
        g.append(sv("rect", { x: x(c.ini), y, width: x(f) - x(c.ini), height: barra, rx: 4, style: `fill:${cor(i)}` }, titulo));
      }
    });

    g.append(sv("text", { class: "g-rotulo-cpu", x: 4, y: yCpu + 14, "dominant-baseline": "central" }, document.createTextNode("CPU")));
    const faixas = [];
    r.linha.forEach((pid, s) => {
      if (s >= t) return;
      const ultima = faixas[faixas.length - 1];
      if (ultima && ultima.pid === pid && ultima.fim === s) ultima.fim = s + 1;
      else faixas.push({ pid, ini: s, fim: s + 1 });
    });
    for (const f of faixas) {
      const w = x(f.fim) - x(f.ini);
      if (f.pid === null) {
        g.append(sv("rect", { class: "g-ocioso", x: x(f.ini), y: yCpu, width: w, height: 28, rx: 4 },
          sv("title", {}, document.createTextNode(`CPU ociosa de ${f.ini} a ${f.fim}`))));
        if (w >= 52) g.append(sv("text", { class: "g-ocioso-txt", x: x(f.ini) + w / 2, y: yCpu + 14, "text-anchor": "middle", "dominant-baseline": "central" }, document.createTextNode("ociosa")));
        continue;
      }
      const i = indiceDe(f.pid), c = cor(i);
      g.append(sv("rect", { x: x(f.ini), y: yCpu, width: w, height: 28, rx: 4, style: `fill:${c}` },
        sv("title", {}, document.createTextNode(`${f.pid} na CPU de ${f.ini} a ${f.fim}`))));
      if (w >= 26) g.append(sv("text", { class: "g-barra-txt", x: x(f.ini) + w / 2, y: yCpu + 14, "text-anchor": "middle", "dominant-baseline": "central", style: `fill:${corTexto(c)}` }, document.createTextNode(f.pid)));
    }

    g.append(sv("line", { class: "g-eixo", x1: x(0), y1: yEixo, x2: x(T), y2: yEixo }));
    const cada = Math.ceil(30 / unit);
    for (let s = 0; s <= T; s++) {
      if (s % cada !== 0 && s !== T) continue;
      g.append(sv("text", { class: "g-tick", x: x(s), y: yEixo + 18, "text-anchor": "middle" }, document.createTextNode(String(s))));
    }

    if (t < T) {
      g.append(sv("line", { class: "g-cursor", x1: x(t), y1: topo - 6, x2: x(t), y2: yEixo }));
      g.append(sv("polygon", { class: "g-cursor-ponta", points: `${x(t) - 5},${topo - 10} ${x(t) + 5},${topo - 10} ${x(t)},${topo - 3}` }));
    }
    $("#gantt").replaceChildren(g);
  }

  function pilula(pid, detalhe) {
    const i = indiceDe(pid), c = cor(i);
    const p = el("span", { class: "pilula", style: `background:${c};color:${corTexto(c)}` }, pid);
    if (detalhe) p.append(el("small", { text: detalhe }));
    return p;
  }

  function linhaEstado(titulo, itens) {
    return el("div", { class: "linha" }, el("span", { class: "titulo", text: titulo }),
      ...(itens.length ? itens : [el("span", { class: "vazio", text: "ninguém" })]));
  }

  function renderEstado() {
    const r = atual(), T = total(), t = S.t, caixa = $("#estado");
    if (t >= T) {
      caixa.replaceChildren(el("div", { class: "linha" },
        el("span", { text: `Simulação completa: todos os processos terminaram em ${T} s.` })));
      return;
    }
    const naCpu = r.linha[t];
    const feito = (pid) => r.linha.slice(0, t).filter((x) => x === pid).length;
    const restam = (p) => `restam ${p.duracao - feito(p.pid)}`;
    const prontos = r.processos.filter((p) => p.chegada <= t && feito(p.pid) < p.duracao && p.pid !== naCpu);
    const futuros = r.processos.filter((p) => p.chegada > t);
    const prontoCpu = r.processos.find((p) => p.pid === naCpu);
    caixa.replaceChildren(
      el("div", { class: "linha" }, el("span", { class: "titulo", text: `Instante ${t} s` })),
      el("div", { class: "linha" },
        el("span", { text: naCpu ? "a CPU vai executar:" : "a CPU fica ociosa neste segundo" }),
        ...(naCpu ? [pilula(naCpu, restam(prontoCpu))] : [])),
      linhaEstado("Esperando na fila", prontos.map((p) => pilula(p.pid, restam(p)))),
      linhaEstado("Ainda não chegaram", futuros.map((p) => pilula(p.pid, `chega em ${p.chegada}`))));
  }

  function renderControles() {
    const T = total();
    $("#slider").max = String(T);
    $("#slider").value = String(S.t);
    $("#btn-play").textContent = S.tocando ? "Pausar" : "Executar passo a passo";
    $("#btn-voltar").disabled = S.t <= 0;
    $("#btn-reiniciar").disabled = S.t <= 0;
    $("#btn-avancar").disabled = S.t >= T;
  }

  function renderComparacao() {
    const linhas = ALGORITMOS.map((a) => ({ a, r: S.resultados[a.id] }));
    const maxTT = Math.max(...linhas.map((l) => l.r.tt_medio));
    const maxTW = Math.max(...linhas.map((l) => l.r.tw_medio), 1e-9);
    const maxTR = Math.max(...linhas.map((l) => l.r.tr_medio), 1e-9);
    const celula = (valor, max) => el("td", {}, el("div", { class: "celula-barra" },
      el("div", { class: "barra", style: `width:${Math.max(2, (valor / max) * 36)}px` }),
      el("span", { class: "num", text: fmt(valor) })));
    const corpo = linhas.map(({ a, r }) => {
      const sub = a.params ? a.params.map((k) => `${k} ${S[k]}`).join(" · ") : a.tipo;
      const tr = el("tr", { class: a.id === S.algoritmo ? "atual" : "", tabindex: "0",
        onclick: () => selecionar(a.id),
        onkeydown: (ev) => { if (ev.key === "Enter" || ev.key === " ") { ev.preventDefault(); selecionar(a.id); } } },
        el("td", {}, el("span", { class: "nome", text: a.nome }), el("span", { class: "sub", text: sub })),
        celula(r.tt_medio, maxTT),
        celula(r.tw_medio, maxTW),
        celula(r.tr_medio, maxTR),
        el("td", {}, el("span", { class: "num", text: String(r.trocas) })));
      return tr;
    });
    $("#comparacao").replaceChildren(
      el("thead", {}, el("tr", {}, el("th", { text: "Algoritmo" }), el("th", { text: "Turnaround médio" }),
        el("th", { text: "Espera média" }), el("th", { text: "Resposta média" }), el("th", { text: "Trocas" }))),
      el("tbody", {}, ...corpo));
  }

  function renderResultados() {
    $("#resultados").replaceChildren(...atual().processos.map((p, i) => el("tr", {},
      el("td", {}, el("span", { class: "amostra", style: `background:${cor(i)}` }), p.pid),
      ...[p.chegada, p.duracao, p.prioridade, p.inicio, p.termino, p.turnaround, p.espera, p.resposta].map((v) => el("td", { text: String(v) })))));
  }

  function renderAbas() {
    document.querySelectorAll(".aba").forEach((b) => b.setAttribute("aria-selected", String(b.dataset.aba === S.aba)));
    for (const nome of ["gantt", "comparacao"]) $(`#aba-${nome}`).hidden = nome !== S.aba;
    $("#cartao-resultados").hidden = S.aba !== "gantt";
  }

  function renderTudo() {
    renderAlgoritmos();
    renderMetricas();
    renderGantt();
    renderEstado();
    renderControles();
    renderComparacao();
    renderResultados();
    renderAbas();
  }

  function renderAnimacao() {
    renderGantt();
    renderEstado();
    renderControles();
  }

  // ---------- animação ----------

  function parar() {
    clearInterval(S.timer);
    S.timer = null;
    S.tocando = false;
  }

  function passo(delta) {
    S.t = Math.max(0, Math.min(total(), S.t + delta));
    renderAnimacao();
  }

  function alternarPlay() {
    if (S.tocando) { parar(); renderControles(); return; }
    if (S.t >= total()) S.t = 0;
    S.tocando = true;
    S.timer = setInterval(() => {
      if (S.t >= total()) { parar(); renderAnimacao(); return; }
      S.t += 1;
      if (S.t >= total()) parar();
      renderAnimacao();
    }, 750 / S.velocidade);
    renderAnimacao();
  }

  // ---------- eventos ----------

  $("#btn-add").addEventListener("click", () => {
    if (S.processos.length >= LIMITE) return;
    S.processos.push({ chegada: "", duracao: "", prioridade: "" });
    renderTabela();
    atualizar();
    const novo = document.querySelector(`#tabela-processos input[data-i="${S.processos.length - 1}"]`);
    if (novo) novo.focus();
  });
  $("#btn-exemplo").addEventListener("click", () => carregar(EXEMPLO));
  $("#btn-limpar").addEventListener("click", () => { S.processos = []; renderTabela(); atualizar(); });
  $("#btn-arquivo").addEventListener("click", () => $("#arquivo").click());
  $("#arquivo").addEventListener("change", (ev) => {
    const arquivo = ev.target.files[0];
    ev.target.value = "";
    if (arquivo) lerArquivo(arquivo);
  });
  $("#quantum").addEventListener("input", (ev) => { S.quantum = ev.target.value; agendar(); });
  $("#aging").addEventListener("input", (ev) => { S.aging = ev.target.value; agendar(); });

  $("#btn-play").addEventListener("click", () => { if (S.resultados) alternarPlay(); });
  $("#btn-voltar").addEventListener("click", () => { parar(); passo(-1); });
  $("#btn-avancar").addEventListener("click", () => { parar(); passo(1); });
  $("#btn-reiniciar").addEventListener("click", () => { parar(); S.t = 0; renderAnimacao(); });
  $("#slider").addEventListener("input", (ev) => { parar(); S.t = parseInt(ev.target.value, 10); renderAnimacao(); });
  $("#velocidade").addEventListener("change", (ev) => {
    S.velocidade = parseFloat(ev.target.value);
    if (S.tocando) { parar(); alternarPlay(); }
  });

  document.querySelectorAll(".aba").forEach((b) => b.addEventListener("click", () => { S.aba = b.dataset.aba; renderAbas(); }));

  // ---------- início ----------

  async function iniciar() {
    try {
      const config = await (await fetch("/api/config")).json();
      S.quantum = String(config.quantum);
      S.aging = String(config.aging);
    } catch { /* usa os valores padrão */ }
    $("#quantum").value = S.quantum;
    $("#aging").value = S.aging;
    renderAlgoritmos();
    carregar(EXEMPLO);
  }

  iniciar();
})();
