"""Leitura e parsing da entrada padrão (stdin)."""

from processo import Processo


def ler_processos(linhas):
    processos = []
    for i, linha in enumerate(linhas):
        partes = linha.split()
        if not partes:
            continue
        chegada, duracao, prioridade = map(int, partes[:3])
        processos.append(Processo(f"P{i + 1}", chegada, duracao, prioridade))
    return processos