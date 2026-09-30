# Simulador de Escalonamento de Processos

Simulador de algoritmos de escalonamento de CPU, desenvolvido para a disciplina de **Sistemas Operacionais**.

Dado um conjunto de processos, simula cada algoritmo segundo a segundo e mostra turnaround médio, espera média, resposta média, número de trocas de contexto e o diagrama de execução.

## Algoritmos implementados

- [x] FCFS — First Come, First Served
- [x] SJF — Shortest Job First
- [x] SRTF — Shortest Remaining Time First
- [x] PRIOc — prioridade cooperativa (sem preempção)
- [x] PRIOp — prioridade com preempção
- [x] RR — Round-Robin com quantum, sem prioridade
- [x] RR (aging) — Round-Robin com prioridade e envelhecimento

## Como executar

Os processos são lidos da entrada padrão (stdin):

```bash
python main.py < entrada.txt
```

No PowerShell:
```powershell
Get-Content entrada.txt | python main.py
```

Também é possível passar o arquivo como argumento:
```bash
python main.py entrada.txt
```

Interface gráfica (abre `http://127.0.0.1:8000/` no navegador; Ctrl+C no terminal encerra):
```bash
python interface.py
```

## Entrada

**Processos.** Cada linha é um processo, com três inteiros separados por um ou mais espaços: instante de criação, duração em segundos e prioridade estática (maior número = maior prioridade). A lista não precisa estar ordenada, e os processos são numerados (`P1`, `P2`, ...) pela ordem em que aparecem. Exemplo (`entrada.txt`):

```
0 5 2
0 2 3
1 4 1
3 3 4
```

**Configuração.** `quantum` e `aging` ficam no arquivo `config.txt`, ao lado do `main.py`:

```
quantum:2
aging:1
```

## Saída

Para cada algoritmo, o programa imprime:

- tabela por processo com chegada, duração, início, término, TT (turnaround: término − chegada), TW (espera: TT − duração) e TR (resposta: início − chegada);
- tempo médio de vida (turnaround), de espera e de resposta;
- número de trocas de contexto;
- diagrama de tempo na vertical, uma linha por segundo: `##` executando, `--` esperando na fila e vazio quando o processo ainda não chegou ou já terminou.

## Interface gráfica

Além do terminal, há uma interface no navegador que usa o mesmo simulador (`escalonador/simulacao.py`). Nela é possível:

- editar os processos, carregar um `.txt` no mesmo formato ou usar a entrada do enunciado;
- escolher o algoritmo e ajustar quantum e aging (valores iniciais vindos do `config.txt`);
- ver as métricas, o gráfico de execução com modo passo a passo e a comparação dos 7 algoritmos.

`interface.py` é um servidor local (só biblioteca padrão, acessível apenas da própria máquina) que entrega a página da pasta `web/` e simula quando a página pede.

## Decisões de implementação

### Estrutura do projeto

```
.
├── main.py                # Ponto de entrada (terminal)
├── interface.py           # Servidor da interface web
├── config.txt             # Quantum e aging
├── entrada.txt            # Exemplo de entrada
├── escalonador/           # Núcleo da simulação
│   ├── entrada.py         # Leitura dos processos e do config.txt
│   ├── processo.py        # Classe Processo
│   ├── escalonadores.py   # Função de escolha de cada algoritmo
│   ├── simulacao.py       # Motor da simulação
│   └── relatorio.py       # Saída no terminal (tabela + diagrama)
└── web/                   # Página da interface (index.html, style.css, app.js)
```

### Classe `Processo` (`escalonador/processo.py`)

Cada processo é um objeto `Processo` que guarda as informações de controle:

| Atributo             | Descrição                                                                 |
|----------------------|---------------------------------------------------------------------------|
| `pid`                | Identificador (`P1`, `P2`, ...)                                           |
| `status`             | `novo` (ainda não chegou), `pronto`, `executando` ou `terminado`          |
| `chegada`            | Instante de criação                                                       |
| `duracao`            | Tempo total de CPU necessário                                             |
| `prioridade`         | Prioridade estática                                                       |
| `restante`           | Tempo que ainda falta executar                                            |
| `inicio`             | Primeiro instante em que ocupou a CPU                                     |
| `termino`            | Instante em que terminou                                                  |
| `prioridade_dinamica`| Prioridade que cresce com o envelhecimento (só RR com aging)              |
| `fila`               | Posição na fila de prontos do RR: `(instante em que entrou, 0 = chegada ou 1 = perdeu a CPU)` |

As propriedades `turnaround` (término − chegada), `espera` (turnaround − duração) e `resposta` (início − chegada) são calculadas a partir desses atributos.

### Estruturas de dados

- **Lista de `Processo`**, na ordem da entrada. Cada algoritmo trabalha sobre uma cópia (`copy.deepcopy`), então todos partem dos mesmos dados.
- **`linha_do_tempo`**: lista com o `pid` que ocupou a CPU em cada segundo (`None` = CPU ociosa). O diagrama e a contagem de trocas de contexto saem dela.
- **`ALGORITMOS`**: dicionário `nome → (função de escolha, é preemptivo?)`.
- **`COM_QUANTUM`**: tupla com os algoritmos em que o quantum define a troca (RR e RR (aging)).

### Padrão de projeto

Usamos uma forma simples do padrão **Strategy**: há um único motor (`simular`) e cada algoritmo é uma função de escolha intercambiável em `escalonador/escalonadores.py`. Todas recebem os candidatos (processos prontos) e o `pid` em execução, e devolvem quem ocupa a CPU. Para criar um algoritmo novo basta escrever a função e registrá-la em `ALGORITMOS`.

### Motor da simulação (`escalonador/simulacao.py`)

A cada segundo, o motor:

1. marca como `pronto` quem já chegou e ainda não terminou;
2. escolhe quem executa, conforme o tipo do algoritmo:
   - **cooperativo** (FCFS, SJF, PRIOc): só escolhe quando a CPU fica livre;
   - **preemptivo** (SRTF, PRIOp): refaz a escolha a cada segundo;
   - **com quantum** (RR, RR (aging)): só troca quando o processo termina ou o quantum acaba com outro esperando;
3. executa o escolhido por 1 segundo (`status = executando`), registra na `linha_do_tempo` e, se acabou, marca `terminado`.

No fim, conta as trocas de contexto: uma troca é cada vez que a CPU passa a executar um processo diferente do anterior. Tempo ocioso entre dois processos não conta.

### Regra de desempate

Como no enunciado, quando há empate na escolha de quem ocupa a CPU, vale esta ordem:

1. o processo que já está com o processador (evita troca de contexto);
2. o de menor tempo restante;
3. escolha arbitrária: usamos o `pid`, para o resultado ser sempre o mesmo.

Por exemplo, no FCFS do enunciado, P1 e P2 chegam em 0; nenhum está na CPU, então vence P2, que tem menor tempo restante.

### RR e RR (aging)

**RR:** cada processo executa no máximo `quantum` segundos seguidos. Se não terminar, volta para o fim da fila. Se terminar antes do fim do quantum, o próximo assume a CPU na hora. A fila é por ordem de entrada: chegadas simultâneas entram pela ordem da entrada (como no diagrama do enunciado) e, se um processo chega no mesmo instante em que outro perde a CPU por fim de quantum, o que chegou entra na frente.

**RR (aging):** a escolha só acontece quando a CPU fica livre ou o quantum acaba, e não há preempção por prioridade. Vence a maior prioridade dinâmica entre os outros processos: quem acabou de usar o quantum não repete no quantum seguinte se houver alguém esperando. Depois da escolha, quem estava esperando ganha `+aging` e o escolhido volta à prioridade estática. O envelhecimento ocorre a cada quantum completo: se o processo anterior terminou antes do fim do quantum, ninguém envelhece. Empate de prioridade dinâmica segue a regra de desempate acima.

## Requisitos

- Python 3.8+
- Nenhuma dependência externa (apenas biblioteca padrão)

## Autores

- _[nome dos integrantes da equipe]_
