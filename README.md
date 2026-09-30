# Simulador de Escalonamento de Processos

Simulador de algoritmos de escalonamento de CPU, desenvolvido para a disciplina de **Sistemas Operacionais** — Departamento de Computação, UFC.

## Objetivo

Simular o escalonamento de um conjunto de processos usando os algoritmos clássicos de escalonamento de processador, exibindo métricas de desempenho (tempo médio de vida, de espera e de resposta, número de trocas de contexto) e o diagrama de execução ao longo do tempo.

## Algoritmos implementados

- [x] FCFS — First Come, First Served
- [x] SJF — Shortest Job First
- [x] SRTF — Shortest Remaining Time First
- [x] PRIOc — prioridade cooperativa (sem preempção)
- [x] PRIOp — prioridade com preempção
- [x] RR — Round-Robin com quantum, sem prioridade
- [x] RR (aging) — Round-Robin com prioridade e envelhecimento

## Como executar

**Passando o arquivo como argumento (recomendado, funciona em qualquer terminal):**
```bash
python main.py entrada.txt
```

**Via redirecionamento (Linux/macOS ou `cmd.exe` no Windows):**
```bash
python main.py < entrada.txt
```

**Via redirecionamento no PowerShell:**
```powershell
Get-Content entrada.txt | python main.py
```

**Digitando a entrada manualmente:**
```bash
python main.py
```
Digite as linhas dos processos e finalize com `Ctrl+D` (Linux/macOS) ou `Ctrl+Z` + Enter (Windows).

## Formato de entrada

Cada linha representa um processo, com três inteiros separados por espaço:

```
<instante_de_criação> <duração> <prioridade>
```

Exemplo (`entrada.txt`):
```
0 5 2
0 2 3
1 4 1
3 3 4
```

A entrada não precisa estar ordenada por instante de criação — os processos são numerados (`P1`, `P2`, ...) na ordem em que aparecem no arquivo.

Em PRIOc, PRIOp e RR (aging), valores maiores indicam prioridade maior. Em PRIOc o processo escolhido executa até terminar; em PRIOp, a escolha é refeita a cada segundo e uma prioridade maior pode interrompê-lo. Empates seguem a regra de desempate descrita acima.

## Saída

Para cada algoritmo, o programa imprime:

- Tabela com chegada, duração, início, término, turnaround (TT), tempo de espera (TW) e tempo de resposta (TR) de cada processo;
- Tempo médio de vida (turnaround médio);
- Tempo médio de espera;
- Tempo médio de resposta (primeira execução − chegada);
- Número de trocas de contexto;
- Diagrama de tempo de execução, na vertical (uma linha por segundo).

No diagrama:
- `##` — processo em execução naquele segundo;
- `--` — processo já chegou e aguarda na fila;
- *(célula em branco)* — processo ainda não chegou ou já terminou.

## Interface gráfica (web)

Além da saída no terminal, há uma interface no navegador. Ela usa o mesmo simulador (`escalonador/simulacao.py`); só a apresentação é nova.

```bash
python interface.py
```

Abre `http://127.0.0.1:8000/` no navegador (Ctrl+C no terminal encerra).

Na página é possível:
- editar os processos (chegada, duração, prioridade) ou carregar um `.txt` no mesmo formato do `entrada.txt`;
- escolher o algoritmo e ajustar quantum e aging (valores iniciais vêm do `config.txt`);
- ver turnaround médio, espera média, resposta média, trocas de contexto e tempo total;
- ver o gráfico de execução (com modo passo a passo) e a comparação dos 7 algoritmos.

## Regra de desempate

Em caso de empate na escolha do processo a ocupar a CPU, é aplicada a seguinte ordem de critérios (conforme especificado no enunciado):

1. Processo que já está com o processador (evita troca de contexto desnecessária);
2. Processo com menor tempo restante de execução;
3. Escolha determinística pelo `pid` (usado como substituto de uma escolha aleatória, garantindo resultados reproduzíveis).

## RR e RR (aging)

O `quantum` e a taxa de envelhecimento (`aging`) são lidos do arquivo `config.txt`, que fica ao lado do `main.py`:

```
quantum:2
aging:1
```

**RR:** cada processo executa no máximo `quantum` segundos seguidos. Se não terminar, volta para o fim da fila. Se terminar antes do fim do quantum, o próximo assume a CPU na hora.

**RR (aging):** a escolha só acontece quando a CPU fica livre ou o quantum acaba (não há preempção por prioridade). Vence a maior prioridade dinâmica (maior número = maior prioridade) entre os outros processos: quem acabou de usar o quantum não repete o quantum seguinte se houver alguém esperando. Depois da escolha, quem estava esperando ganha `+aging` e o escolhido volta à prioridade estática. O envelhecimento só ocorre quando o processo anterior usou o quantum inteiro: se ele terminou antes, ninguém envelhece.

Convenções adotadas (o enunciado não define):
- Se um processo chega no mesmo instante em que outro perde a CPU por fim de quantum, o que chegou entra na fila antes.
- Chegadas simultâneas entram na fila pela ordem da entrada.
- Empate de prioridade dinâmica: vence quem está há mais tempo na fila.

## Trocas de contexto

Uma troca de contexto é contabilizada sempre que a CPU passa a executar um processo diferente do anterior. Transições envolvendo tempo ocioso (CPU livre) não são contadas, pois não há contexto de outro processo a ser salvo/restaurado.

## Estrutura do projeto

```
.
├── main.py                # Ponto de entrada (terminal)
├── interface.py           # Servidor da interface web (opcional)
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

### `escalonador/processo.py`
Define a classe `Processo`, com os atributos de controle de cada processo:

| Atributo     | Descrição                                              |
|--------------|---------------------------------------------------------|
| `pid`        | Identificador do processo (`P1`, `P2`, ...)              |
| `chegada`    | Instante de criação                                      |
| `duracao`    | Duração total de execução (em segundos)                  |
| `prioridade` | Prioridade estática do processo                          |
| `restante`   | Tempo restante de execução (usado durante a simulação)   |
| `inicio`     | Instante em que o processo ocupou a CPU pela primeira vez|
| `termino`    | Instante em que o processo terminou                       |

Também expõe as propriedades `turnaround` (término − chegada), `espera` (turnaround − duração) e `resposta` (início − chegada).

### `escalonador/escalonadores.py`
Contém uma função de escolha para cada algoritmo, todas seguindo a mesma assinatura: recebem a lista de processos já chegados (candidatos) e o pid do processo em execução, e devolvem o processo escolhido para ocupar a CPU.

O dicionário `ALGORITMOS` mapeia o nome do algoritmo para `(função_de_escolha, é_preemptivo)`, o que permite adicionar novos algoritmos sem alterar o motor de simulação.

### `escalonador/simulacao.py`
Executa a simulação segundo a segundo: a cada instante, identifica os processos já chegados e com tempo restante, aplica a função de escolha do algoritmo, executa o processo escolhido por 1 segundo e atualiza seu estado. Ao final, conta o número de trocas de contexto.

### `escalonador/relatorio.py`
Imprime a tabela de métricas por processo (chegada, duração, início, término, TT, TW, TR), as médias de turnaround, espera e resposta, o número de trocas de contexto e o diagrama de tempo vertical.

## Requisitos

- Python 3.8+
- Nenhuma dependência externa (apenas biblioteca padrão)

## Autores

- _[nome dos integrantes da equipe]_
