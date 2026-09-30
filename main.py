import os
import sys

from escalonador.entrada import ler_configuracao, ler_processos
from escalonador.escalonadores import ALGORITMOS
from escalonador.relatorio import imprimir_resultado
from escalonador.simulacao import simular


def obter_linhas():
    # entrada padrão (stdin), como pede o enunciado; também aceita um arquivo como argumento
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
    # lê a entrada, roda os 7 algoritmos e imprime o resultado de cada um
    linhas = obter_linhas()
    processos = ler_processos(linhas)
    quantum, aging = obter_configuracao()

    if not processos:
        print("Nenhum processo informado na entrada.")
        return

    for algoritmo in ALGORITMOS:
        # cada algoritmo parte dos mesmos processos originais
        resultado_processos, linha_do_tempo, trocas = simular(
            processos, algoritmo, quantum, aging)
        imprimir_resultado(algoritmo, resultado_processos, linha_do_tempo, trocas)


if __name__ == "__main__":
    main()
