import json
import os
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer

from escalonador.entrada import ler_configuracao
from escalonador.escalonadores import ALGORITMOS
from escalonador.processo import Processo
from escalonador.simulacao import simular

PASTA = os.path.dirname(os.path.abspath(__file__))
PORTA = 8000
# arquivos da pasta web/ que o servidor entrega ao navegador
ARQUIVOS = {
    "/": ("index.html", "text/html; charset=utf-8"),
    "/style.css": ("style.css", "text/css; charset=utf-8"),
    "/app.js": ("app.js", "text/javascript; charset=utf-8"),
}


# valida os números vindos da página
def inteiro(valor, nome, minimo):
    if not isinstance(valor, int) or valor < minimo:
        raise ValueError(f"{nome} deve ser um inteiro maior ou igual a {minimo}")
    return valor


def calcular(dados):
    # roda os 7 algoritmos com os dados da página
    quantum = inteiro(dados["quantum"], "quantum", 1)
    aging = inteiro(dados["aging"], "aging", 0)
    processos = []
    for i, item in enumerate(dados["processos"], start=1):
        processos.append(Processo(f"P{i}",
                                  inteiro(item["chegada"], f"P{i}: chegada", 0),
                                  inteiro(item["duracao"], f"P{i}: duração", 1),
                                  inteiro(item["prioridade"], f"P{i}: prioridade", 0)))
    if not processos:
        raise ValueError("informe pelo menos um processo")

    resultados = {}
    for nome in ALGORITMOS:
        simulados, linha, trocas = simular(processos, nome, quantum, aging)
        n = len(simulados)
        resultados[nome] = {
            "linha": linha,
            "trocas": trocas,
            "tt_medio": sum(p.turnaround for p in simulados) / n,
            "tw_medio": sum(p.espera for p in simulados) / n,
            "tr_medio": sum(p.resposta for p in simulados) / n,
            "processos": [
                {"pid": p.pid, "chegada": p.chegada, "duracao": p.duracao,
                 "prioridade": p.prioridade, "inicio": p.inicio, "termino": p.termino,
                 "turnaround": p.turnaround, "espera": p.espera, "resposta": p.resposta}
                for p in simulados
            ],
        }
    return {"resultados": resultados}


# GET entrega a página e o config.txt; POST /api/simular roda os algoritmos
class Handler(BaseHTTPRequestHandler):
    # resposta HTTP com o conteúdo já pronto
    def enviar(self, status, tipo, corpo):
        self.send_response(status)
        self.send_header("Content-Type", tipo)
        self.send_header("Content-Length", str(len(corpo)))
        self.end_headers()
        self.wfile.write(corpo)

    def enviar_json(self, status, dados):
        self.enviar(status, "application/json; charset=utf-8", json.dumps(dados).encode("utf-8"))

    # páginas e quantum/aging iniciais
    def do_GET(self):
        if self.path == "/api/config":
            with open(os.path.join(PASTA, "config.txt"), encoding="utf-8") as arquivo:
                quantum, aging = ler_configuracao(arquivo.read().splitlines())
            return self.enviar_json(200, {"quantum": quantum, "aging": aging})
        if self.path not in ARQUIVOS:
            return self.enviar_json(404, {"erro": "não encontrado"})
        nome, tipo = ARQUIVOS[self.path]
        with open(os.path.join(PASTA, "web", nome), "rb") as arquivo:
            self.enviar(200, tipo, arquivo.read())

    # recebe os processos da página, simula e devolve os resultados (erro 400 se inválidos)
    def do_POST(self):
        if self.path != "/api/simular":
            return self.enviar_json(404, {"erro": "não encontrado"})
        corpo = self.rfile.read(int(self.headers["Content-Length"]))
        try:
            self.enviar_json(200, calcular(json.loads(corpo)))
        except (ValueError, KeyError, TypeError) as erro:
            self.enviar_json(400, {"erro": str(erro)})


def main():
    # servidor só acessível da própria máquina; abre a página no navegador
    servidor = HTTPServer(("127.0.0.1", PORTA), Handler)
    url = f"http://127.0.0.1:{PORTA}/"
    print(f"Interface em {url}  (Ctrl+C para encerrar)")
    webbrowser.open(url)
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    main()
