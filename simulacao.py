"""Motor de simulação: executa um algoritmo sobre uma lista de processos
e devolve o estado final dos processos, a linha do tempo e o número de
trocas de contexto."""

import copy

from escalonadores import ALGORITMOS


def simular(processos_originais, algoritmo):
    processos = copy.deepcopy(processos_originais)
    n = len(processos)
    escolher, preemptivo = ALGORITMOS[algoritmo]

    tempo = 0
    concluidos = 0
    executando = None
    linha_do_tempo = []

    tempo_maximo = sum(p.duracao for p in processos) + \
        (max((p.chegada for p in processos), default=0)) + 10

    while concluidos < n and tempo < tempo_maximo:
        chegaram = [p for p in processos if p.chegada <= tempo and p.restante > 0]

        if not chegaram:
            linha_do_tempo.append(None)
            executando = None
            tempo += 1
            continue

        if preemptivo:
            escolhido = escolher(chegaram, executando)
        else:
            proc_atual = next((p for p in processos if p.pid == executando), None)
            if proc_atual is None or proc_atual.restante <= 0:
                escolhido = escolher(chegaram, executando)
            else:
                escolhido = proc_atual

        executando = escolhido.pid
        proc = next(p for p in processos if p.pid == executando)

        if proc.inicio is None:
            proc.inicio = tempo

        proc.restante -= 1
        linha_do_tempo.append(proc.pid)

        if proc.restante == 0:
            proc.termino = tempo + 1
            concluidos += 1

        tempo += 1

    trocas = _contar_trocas_de_contexto(linha_do_tempo)
    return processos, linha_do_tempo, trocas


def _contar_trocas_de_contexto(linha_do_tempo):
    trocas = 0
    anterior = None
    for pid in linha_do_tempo:
        if pid != anterior and anterior is not None and pid is not None:
            trocas += 1
        anterior = pid
    return trocas