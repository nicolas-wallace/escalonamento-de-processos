# cada função recebe os candidatos (já chegados, com tempo restante) e o pid em execução


def _com_desempate(candidatos, executando_pid, chave_primaria):
    # desempate: quem já está na CPU, menor tempo restante, pid
    def chave(p):
        ja_rodando = 0 if p.pid == executando_pid else 1
        return (chave_primaria(p), ja_rodando, p.restante, p.pid)
    return min(candidatos, key=chave)


# FCFS: menor instante de chegada
def escolher_fcfs(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.chegada)


# SJF: menor tempo restante (sem preempção: o motor só escolhe quando a CPU fica livre)
def escolher_sjf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


# SRTF: menor tempo restante, reavaliado a cada segundo (preemptivo)
def escolher_srtf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


# PRIOc e PRIOp: maior prioridade (PRIOp reavalia a cada segundo, PRIOc só ao liberar a CPU)
def escolher_prioridade(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: -p.prioridade)


# RR: fila FIFO; p.fila = (instante em que entrou na fila, 0 = chegada / 1 = perdeu a CPU)
def escolher_rr(candidatos, executando_pid, quantum_completo, aging):
    # vence quem entrou antes na fila; empate: menor tempo restante, pid
    return min(candidatos, key=lambda p: (p.fila, p.restante, p.pid))


# RR (aging): prioridade dinâmica sobe +aging por quantum de espera
def escolher_rr_aging(candidatos, executando_pid, quantum_completo, aging):
    # maior prioridade dinâmica, sem repetir quem acabou de executar;
    # empate: menor tempo restante, pid
    outros = [p for p in candidatos if p.pid != executando_pid]
    escolhido = min(outros, key=lambda p: (-p.prioridade_dinamica, p.restante, p.pid))
    # quem esperou ganha +aging, só se o quantum foi completo
    if quantum_completo:
        for p in candidatos:
            if p is not escolhido:
                p.prioridade_dinamica += aging
    # o escolhido volta à prioridade estática
    escolhido.prioridade_dinamica = escolhido.prioridade
    return escolhido


# algoritmo -> (função de escolha, é preemptivo?)
ALGORITMOS = {
    "FCFS": (escolher_fcfs, False),
    "SJF": (escolher_sjf, False),
    "SRTF": (escolher_srtf, True),
    "PRIOc": (escolher_prioridade, False),
    "PRIOp": (escolher_prioridade, True),
    "RR": (escolher_rr, True),
    "RR (aging)": (escolher_rr_aging, True),
}

# algoritmos em que o quantum define a troca de processo
COM_QUANTUM = ("RR", "RR (aging)")
