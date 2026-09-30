import copy

from .escalonadores import ALGORITMOS, COM_QUANTUM


def simular(processos_originais, algoritmo, quantum=2, aging=1):
    # devolve (processos, linha do tempo com um pid por segundo, trocas de contexto)
    processos = copy.deepcopy(processos_originais)
    n = len(processos)
    escolher, preemptivo = ALGORITMOS[algoritmo]

    tempo = 0
    concluidos = 0
    executando = None
    fatia = 0  # segundos seguidos do processo atual (conta o quantum)
    linha_do_tempo = []

    # trava de segurança contra laço infinito
    tempo_maximo = sum(p.duracao for p in processos) + \
        (max((p.chegada for p in processos), default=0)) + 10

    while concluidos < n and tempo < tempo_maximo:
        # a cada segundo: quem já chegou e não terminou está pronto
        for p in processos:
            if p.restante > 0:
                p.status = "pronto" if p.chegada <= tempo else "novo"
        chegaram = [p for p in processos if p.status == "pronto"]

        if not chegaram:
            # CPU ociosa até a próxima chegada
            linha_do_tempo.append(None)
            executando = None
            tempo += 1
            continue

        # escolhe quem ocupa a CPU neste segundo
        if algoritmo in COM_QUANTUM:
            # só escolhe outro se o atual terminou ou o quantum acabou com alguém esperando
            proc_atual = next((p for p in processos if p.pid == executando), None)
            terminou = proc_atual is None or proc_atual.restante <= 0
            quantum_completo = executando is not None and fatia >= quantum
            tem_outros = any(p is not proc_atual for p in chegaram)
            if terminou or (quantum_completo and tem_outros):
                if not terminou:
                    # perdeu a CPU por quantum: vai para o fim da fila
                    proc_atual.fila = (tempo, 1)
                escolhido = escolher(chegaram, executando, quantum_completo, aging)
                fatia = 0
            else:
                escolhido = proc_atual
                if quantum_completo:
                    fatia = 0
        elif preemptivo:
            # reavalia a escolha a cada segundo
            escolhido = escolher(chegaram, executando)
        else:
            # sem preempção: só escolhe quando a CPU fica livre
            proc_atual = next((p for p in processos if p.pid == executando), None)
            if proc_atual is None or proc_atual.restante <= 0:
                escolhido = escolher(chegaram, executando)
            else:
                escolhido = proc_atual

        executando = escolhido.pid
        proc = next(p for p in processos if p.pid == executando)
        proc.status = "executando"

        if proc.inicio is None:
            proc.inicio = tempo

        # executa o processo escolhido por 1 segundo
        proc.restante -= 1
        fatia += 1
        linha_do_tempo.append(proc.pid)

        if proc.restante == 0:
            proc.termino = tempo + 1
            proc.status = "terminado"
            concluidos += 1

        tempo += 1

    trocas = _contar_trocas_de_contexto(linha_do_tempo)
    return processos, linha_do_tempo, trocas


def _contar_trocas_de_contexto(linha_do_tempo):
    # mudança de um processo para outro; ociosidade no meio não conta
    trocas = 0
    anterior = None
    for pid in linha_do_tempo:
        if pid != anterior and anterior is not None and pid is not None:
            trocas += 1
        anterior = pid
    return trocas