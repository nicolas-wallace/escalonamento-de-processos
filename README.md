# Simulador de Escalonamento de Processos

Simulador de algoritmos de escalonamento de CPU, desenvolvido para a disciplina de **Sistemas Operacionais** — Departamento de Computação, UFC.

## Objetivo

Simular o escalonamento de um conjunto de processos usando os algoritmos clássicos de escalonamento de processador, exibindo métricas de desempenho (tempo médio de vida, tempo médio de espera, número de trocas de contexto) e o diagrama de execução ao longo do tempo.

## Algoritmos implementados

- [x] FCFS (First Come, First Served)
- [x] SJF (Shortest Job First)
- [x] SRTF (Shortest Remaining Time First)
- [x] Escalonamento por prioridade, sem preempção
- [x] Escalonamento por prioridade, com preempção
- [x] Round-Robin com quantum, sem prioridade
- [x] Round-Robin com prioridade e envelhecimento

## Estrutura do projeto

```
.
├── main.py            # Ponto de entrada do programa
├── entrada.py          # Leitura e parsing da entrada (arquivo ou stdin)
├── config.txt          # Valores de quantum e aging
├── processo.py         # Classe Processo (estrutura de controle)
├── escalonadores.py     # Funções de escolha de processo para cada algoritmo
├── simulacao.py         # Motor da simulação (loop principal de execução)
└── relatorio.py         # Formatação da saída (tabela de métricas + diagrama)
```

### `processo.py`
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

Também expõe as propriedades `turnaround` (tempo de vida) e `espera` (tempo de espera), calculadas a partir de `termino`, `chegada` e `duracao`.

### `escalonadores.py`
Contém uma função de escolha para cada algoritmo, todas seguindo a mesma assinatura: recebem a lista de processos já chegados (candidatos) e o pid do processo em execução, e devolvem o processo escolhido para ocupar a CPU.

O dicionário `ALGORITMOS` mapeia o nome do algoritmo para `(função_de_escolha, é_preemptivo)`, o que permite adicionar novos algoritmos sem alterar o motor de simulação.

### `simulacao.py`
Executa a simulação segundo a segundo: a cada instante, identifica os processos já chegados e com tempo restante, aplica a função de escolha do algoritmo, executa o processo escolhido por 1 segundo e atualiza seu estado. Ao final, conta o número de trocas de contexto.

### `relatorio.py`
Imprime a tabela de métricas por processo (chegada, duração, início, término, TT, TW), as médias de turnaround e espera, o número de trocas de contexto e o diagrama de tempo vertical.

## Regra de desempate

Em caso de empate na escolha do processo a ocupar a CPU, é aplicada a seguinte ordem de critérios (conforme especificado no enunciado):

1. Processo que já está com o processador (evita troca de contexto desnecessária);
2. Processo com menor tempo restante de execução;
3. Escolha determinística pelo `pid` (usado como substituto de uma escolha aleatória, garantindo reprodutibilidade dos testes).

## Round-Robin

O `quantum` e a taxa de envelhecimento (`aging`) são lidos do arquivo `config.txt`, que fica ao lado do `main.py`:

```
quantum:2
aging:1
```

**Sem prioridade:** cada processo executa no máximo `quantum` segundos seguidos. Se não terminar, volta para o fim da fila. Se terminar antes do fim do quantum, o próximo assume a CPU na hora.

**Com prioridade e envelhecimento:** a escolha só acontece quando a CPU fica livre ou o quantum acaba (não há preempção por prioridade). Vence a maior prioridade dinâmica (maior número = maior prioridade) entre os outros processos: quem acabou de usar o quantum não repete o quantum seguinte se houver alguém esperando. Depois da escolha, quem estava esperando ganha `+aging` e o escolhido volta à prioridade estática. O envelhecimento só ocorre quando o processo anterior usou o quantum inteiro: se ele terminou antes, ninguém envelhece.

Convenções adotadas (o enunciado não define):
- Se um processo chega no mesmo instante em que outro perde a CPU por fim de quantum, o que chegou entra na fila antes.
- Chegadas simultâneas entram na fila pela ordem da entrada.
- Empate de prioridade dinâmica: vence quem está há mais tempo na fila.

## Trocas de contexto

Uma troca de contexto é contabilizada sempre que a CPU passa a executar um processo diferente do anterior. Transições envolvendo tempo ocioso (CPU livre) não são contadas, pois não há contexto de outro processo a ser salvo/restaurado.

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

Nos algoritmos por prioridade, valores maiores indicam prioridade maior. Sem preempção, o processo escolhido executa até terminar; com preempção, a escolha é refeita a cada segundo e uma prioridade maior pode interrompê-lo. Empates seguem a regra de desempate descrita acima.

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

## Testes

```bash
python -m unittest
```

## Saída

Para cada algoritmo, o programa imprime:

- Tabela com chegada, duração, início, término, turnaround (TT) e tempo de espera (TW) de cada processo;
- Tempo médio de vida (turnaround médio);
- Tempo médio de espera;
- Número de trocas de contexto;
- Diagrama de tempo de execução, na vertical (uma linha por segundo).

No diagrama:
- `##` — processo em execução naquele segundo;
- `--` — processo já chegou e aguarda na fila;
- *(célula em branco)* — processo ainda não chegou ou já terminou.

## Requisitos

- Python 3.8+
- Nenhuma dependência externa (apenas biblioteca padrão)

## Autores

- _[nome dos integrantes da equipe]_
