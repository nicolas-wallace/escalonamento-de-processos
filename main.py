"""Ponto de entrada do simulador."""

import os
import sys

from entrada import ler_configuracao, ler_processos
from simulacao import simular
from relatorio import imprimir_resultado


def obter_linhas():
    """Se um caminho de arquivo for passado como argumento, lê dele.
    Caso contrário, lê da entrada padrão (stdin)."""
    if len(sys.argv) > 1:
        caminho = sys.argv[1]
        with open(caminho, encoding="utf-8") as arquivo:
            return arquivo.read().splitlines()
    return sys.stdin.read().splitlines()


def obter_configuracao():
    # quantum e aging vêm do config.txt, que fica ao lado do main.py
    pasta = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(pasta, "config.txt"), encoding="utf-8") as arquivo:
        return ler_configuracao(arquivo.read().splitlines())


def main():
    linhas = obter_linhas()
    processos = ler_processos(linhas)
    quantum, aging = obter_configuracao()

    if not processos:
        print("Nenhum processo informado na entrada.")
        return

    for algoritmo in (
        "fcfs", "sjf", "srtf",
        "prioridade_sem_preempcao", "prioridade_com_preempcao",
        "round_robin", "round_robin_prioridade_aging",
    ):
        resultado_processos, linha_do_tempo, trocas = simular(
            processos, algoritmo, quantum, aging)
        imprimir_resultado(algoritmo, resultado_processos, linha_do_tempo, trocas)


if __name__ == "__main__":
    main()
