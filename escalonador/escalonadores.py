# cada função recebe os candidatos (já chegados, com tempo restante) e o pid em execução


def _com_desempate(candidatos, executando_pid, chave_primaria):
    # desempate: quem já está na CPU, menor tempo restante, pid
    def chave(p):
        ja_rodando = 0 if p.pid == executando_pid else 1
        return (chave_primaria(p), ja_rodando, p.restante, p.pid)
    return min(candidatos, key=chave)


def escolher_fcfs(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.chegada)


def escolher_sjf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


def escolher_srtf(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: p.restante)


def escolher_prioridade(candidatos, executando_pid):
    return _com_desempate(candidatos, executando_pid, lambda p: -p.prioridade)


def escolher_rr(candidatos, executando_pid, quantum_completo, aging):
    # vence quem está há mais tempo na fila
    return min(candidatos, key=lambda p: p.fila)


def escolher_rr_aging(candidatos, executando_pid, quantum_completo, aging):
    # maior prioridade dinâmica, sem repetir quem acabou de executar
    outros = [p for p in candidatos if p.pid != executando_pid]
    escolhido = min(outros, key=lambda p: (-p.prioridade_dinamica, p.fila))
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
    "fcfs": (escolher_fcfs, False),
    "sjf": (escolher_sjf, False),
    "srtf": (escolher_srtf, True),
    "prioridade_sem_preempcao": (escolher_prioridade, False),
    "prioridade_com_preempcao": (escolher_prioridade, True),
    "round_robin": (escolher_rr, True),
    "round_robin_prioridade_aging": (escolher_rr_aging, True),
}

# algoritmos em que o quantum define a troca de processo
COM_QUANTUM = ("round_robin", "round_robin_prioridade_aging")
