"""Funções de escolha de processo para cada algoritmo de escalonamento.

Cada função recebe a lista de candidatos (processos já chegados e com
tempo restante > 0) e o pid do processo atualmente em execução, e
devolve o processo escolhido para ocupar a CPU.

Critério de desempate comum aos algoritmos, conforme o enunciado:
  (i)   processo que já está com o processador (evita troca de contexto)
  (ii)  menor tempo restante de processamento
  (iii) escolha arbitrária (usamos o pid, por reprodutibilidade)
"""


def _com_desempate(candidatos, executando_pid, chave_primaria):
    def chave(p):
        ja_rodando = 0 if p.pid == executando_pid else 1
        return (chave_primaria(p), ja_rodando, p.restante, p.pid)
    return sorted(candidatos, key=chave)[0]


def escolher_fcfs(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.chegada)


def escolher_sjf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


def escolher_srtf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


def escolher_prioridade(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: -p.prioridade)


# algoritmo -> (função de escolha, é_preemptivo?)
ALGORITMOS = {
    "fcfs": (escolher_fcfs, False),
    "sjf": (escolher_sjf, False),
    "srtf": (escolher_srtf, True),
    "prioridade_sem_preempcao": (escolher_prioridade, False),
    "prioridade_com_preempcao": (escolher_prioridade, True),
}
