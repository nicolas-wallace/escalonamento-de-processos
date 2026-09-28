"""Ponto de entrada do simulador."""

import sys

from entrada import ler_processos
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


def main():
    linhas = obter_linhas()
    processos = ler_processos(linhas)

    if not processos:
        print("Nenhum processo informado na entrada.")
        return

    for algoritmo in (
        "fcfs", "sjf", "srtf",
        "prioridade_sem_preempcao", "prioridade_com_preempcao",
    ):
        resultado_processos, linha_do_tempo, trocas = simular(processos, algoritmo)
        imprimir_resultado(algoritmo, resultado_processos, linha_do_tempo, trocas)


if __name__ == "__main__":
    main()
