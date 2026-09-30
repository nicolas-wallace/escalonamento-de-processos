def imprimir_resultado(algoritmo, processos, linha_do_tempo, trocas):
    # TT = término - chegada, TW = TT - duração, TR = início - chegada
    n = len(processos)
    tts = [p.turnaround for p in processos]
    tws = [p.espera for p in processos]
    trs = [p.resposta for p in processos]

    print(f"\n===== Algoritmo: {algoritmo} =====")
    print(f"{'Processo':10}{'Chegada':10}{'Duração':10}{'Início':10}{'Término':10}{'TT':6}{'TW':6}{'TR':6}")
    for p, tt, tw, tr in zip(processos, tts, tws, trs):
        print(f"{p.pid:10}{p.chegada:<10}{p.duracao:<10}{p.inicio:<10}{p.termino:<10}{tt:<6}{tw:<6}{tr:<6}")

    print(f"\nTempo médio de vida (turnaround):  {sum(tts) / n:.2f}")
    print(f"Tempo médio de espera (waiting):   {sum(tws) / n:.2f}")
    print(f"Tempo médio de resposta:           {sum(trs) / n:.2f}")
    print(f"Número de trocas de contexto:      {trocas}")

    imprimir_diagrama(processos, linha_do_tempo)


def imprimir_diagrama(processos, linha_do_tempo):
    # ## executando, -- esperando na fila, vazio = ainda não chegou ou já terminou
    pids = [p.pid for p in processos]
    cabecalho = f"{'tempo':8}" + "".join(f"{pid:5}" for pid in pids)
    print("\n" + cabecalho)

    for t, pid_executando in enumerate(linha_do_tempo):
        linha = f"{t:>3}-{t + 1:<4}"
        for p in processos:
            if pid_executando == p.pid:
                simbolo = "##"
            elif p.chegada <= t and (p.termino is None or t < p.termino):
                simbolo = "--"
            else:
                simbolo = ""
            linha += f"{simbolo:5}"
        print(linha)
