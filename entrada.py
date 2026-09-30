"""Leitura dos processos e da configuração (quantum e aging)."""

from processo import Processo


def ler_processos(linhas):
    """Cada linha: chegada duração prioridade. Linhas em branco são ignoradas."""
    processos = []
    for i, linha in enumerate(linhas):
        partes = linha.split()
        if not partes:
            continue
        chegada, duracao, prioridade = map(int, partes[:3])
        processos.append(Processo(f"P{i + 1}", chegada, duracao, prioridade))
    return processos


def ler_configuracao(linhas):
    """Lê quantum:N e aging:N, na mesma linha ou em linhas separadas."""
    config = {}
    for linha in linhas:
        for parte in linha.split():
            chave, valor = parte.split(":")
            config[chave] = int(valor)
    return config["quantum"], config["aging"]