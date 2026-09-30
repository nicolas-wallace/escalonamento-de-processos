"""Interface gráfica (web local): serve a página da pasta web/ e expõe uma API
que chama o simulador. Toda a lógica de escalonamento continua em simulacao.py."""

import argparse
import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from entrada import ler_configuracao
from escalonadores import ALGORITMOS
from processo import Processo
from simulacao import simular

PASTA = os.path.dirname(os.path.abspath(__file__))
PASTA_WEB = os.path.join(PASTA, "web")
ARQUIVOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}
MAX_PROCESSOS = 12
MAX_CORPO = 100_000


def configuracao_padrao():
    # lê o mesmo config.txt do main.py; se não existir, usa quantum 2 e aging 1
    try:
        with open(os.path.join(PASTA, "config.txt"), encoding="utf-8") as arquivo:
            quantum, aging = ler_configuracao(arquivo.read().splitlines())
    except (OSError, ValueError, KeyError):
        quantum, aging = 2, 1
    return {"quantum": quantum, "aging": aging}


def inteiro(valor, nome, minimo, maximo):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"{nome} deve ser um número inteiro")
    if not minimo <= valor <= maximo:
        raise ValueError(f"{nome} deve estar entre {minimo} e {maximo}")
    return valor


def montar_processos(lista):
    if not isinstance(lista, list) or not lista:
        raise ValueError("informe pelo menos um processo")
    if len(lista) > MAX_PROCESSOS:
        raise ValueError(f"no máximo {MAX_PROCESSOS} processos")
    processos = []
    for i, item in enumerate(lista):
        rotulo = f"P{i + 1}"
        chegada = inteiro(item["chegada"], f"{rotulo}: chegada", 0, 1000)
        duracao = inteiro(item["duracao"], f"{rotulo}: duração", 1, 1000)
        prioridade = inteiro(item["prioridade"], f"{rotulo}: prioridade", 0, 999)
        processos.append(Processo(rotulo, chegada, duracao, prioridade))
    return processos


def calcular(dados):
    """Roda os 7 algoritmos e devolve tudo o que a página precisa desenhar."""
    processos = montar_processos(dados.get("processos"))
    quantum = inteiro(dados.get("quantum"), "quantum", 1, 100)
    aging = inteiro(dados.get("aging"), "aging", 0, 100)

    resultados = {}
    for nome in ALGORITMOS:
        simulados, linha, trocas = simular(processos, nome, quantum, aging)
        n = len(simulados)
        resultados[nome] = {
            "linha": linha,
            "trocas": trocas,
            "tt_medio": sum(p.turnaround for p in simulados) / n,
            "tw_medio": sum(p.espera for p in simulados) / n,
            "tr_medio": sum(p.inicio - p.chegada for p in simulados) / n,
            "processos": [
                {"pid": p.pid, "chegada": p.chegada, "duracao": p.duracao,
                 "prioridade": p.prioridade, "inicio": p.inicio, "termino": p.termino,
                 "turnaround": p.turnaround, "espera": p.espera,
                 "resposta": p.inicio - p.chegada}
                for p in simulados
            ],
        }
    return {"resultados": resultados}


class Handler(BaseHTTPRequestHandler):
    def enviar(self, status, tipo, corpo):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(corpo)

    def enviar_json(self, status, dados):
        corpo = json.dumps(dados).encode("utf-8")
        self.enviar(status, "application/json; charset=utf-8", corpo)

    def do_GET(self):
        caminho = self.path.split("?")[0]
        if caminho == "/api/config":
            return self.enviar_json(200, configuracao_padrao())
        if caminho not in ARQUIVOS:
            return self.enviar_json(404, {"erro": "não encontrado"})
        nome, tipo = ARQUIVOS[caminho]
        with open(os.path.join(PASTA_WEB, nome), "rb") as arquivo:
            self.enviar(200, tipo, arquivo.read())

    def do_POST(self):
        if self.path != "/api/simular":
            return self.enviar_json(404, {"erro": "não encontrado"})
        tamanho = int(self.headers.get("Content-Length") or 0)
        if tamanho > MAX_CORPO:
            return self.enviar_json(413, {"erro": "requisição grande demais"})
        try:
            dados = json.loads(self.rfile.read(tamanho))
            self.enviar_json(200, calcular(dados))
        except (ValueError, KeyError, TypeError, AttributeError) as erro:
            self.enviar_json(400, {"erro": str(erro) or "dados inválidos"})

    def log_message(self, *args):
        pass


def criar_servidor(porta):
    # só aceita conexões da própria máquina; se a porta estiver ocupada, usa uma livre
    try:
        return ThreadingHTTPServer(("127.0.0.1", porta), Handler)
    except OSError:
        return ThreadingHTTPServer(("127.0.0.1", 0), Handler)


def main():
    parser = argparse.ArgumentParser(description="Interface web do simulador de escalonamento.")
    parser.add_argument("--porta", type=int, default=8000)
    parser.add_argument("--sem-navegador", action="store_true",
                        help="não abre o navegador automaticamente")
    args = parser.parse_args()

    servidor = criar_servidor(args.porta)
    url = f"http://127.0.0.1:{servidor.server_address[1]}/"
    print(f"Interface em {url}  (Ctrl+C para encerrar)")
    if not args.sem_navegador:
        webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")
    finally:
        servidor.server_close()


if __name__ == "__main__":
    main()
