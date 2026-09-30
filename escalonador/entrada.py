from .processo import Processo


def ler_processos(linhas):
    # cada linha: chegada duração prioridade (separadas por um ou mais espaços)
    processos = []
    for i, linha in enumerate(linhas):
        partes = linha.split()
        if not partes:
            continue  # ignora linha em branco
        chegada, duracao, prioridade = map(int, partes[:3])
        # o id vem da posição na entrada: P1, P2, ...
        processos.append(Processo(f"P{i + 1}", chegada, duracao, prioridade))
    return processos


def ler_configuracao(linhas):
    # quantum:N e aging:N, na mesma linha ou em linhas separadas
    config = {}
    for linha in linhas:
        for parte in linha.split():
            chave, valor = parte.split(":")
            config[chave] = int(valor)
    return config["quantum"], config["aging"]
