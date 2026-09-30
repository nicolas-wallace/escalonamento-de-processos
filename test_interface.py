import json
import threading
import unittest
import urllib.error
import urllib.request

from interface import Handler, calcular
from http.server import ThreadingHTTPServer

EXEMPLO = [
    {"chegada": 0, "duracao": 5, "prioridade": 2},
    {"chegada": 0, "duracao": 2, "prioridade": 3},
    {"chegada": 1, "duracao": 4, "prioridade": 1},
    {"chegada": 3, "duracao": 3, "prioridade": 4},
]


def dados(processos=EXEMPLO, quantum=2, aging=1):
    return {"processos": processos, "quantum": quantum, "aging": aging}


class CalcularTests(unittest.TestCase):
    def test_roda_os_sete_algoritmos(self):
        resultados = calcular(dados())["resultados"]
        self.assertEqual(len(resultados), 7)

    def test_round_robin_do_enunciado(self):
        rr = calcular(dados())["resultados"]["round_robin"]
        self.assertEqual(rr["tt_medio"], 9.75)
        self.assertEqual(rr["tw_medio"], 6.25)
        self.assertEqual(rr["trocas"], 7)

    def test_entradas_invalidas(self):
        invalidas = [
            dados(processos=[]),
            dados(processos=[{"chegada": 0, "duracao": 0, "prioridade": 1}]),
            dados(processos=[{"chegada": 0, "duracao": True, "prioridade": 1}]),
            dados(processos=[EXEMPLO[0]] * 13),
            dados(quantum=0),
            dados(aging=-1),
        ]
        for entrada in invalidas:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValueError):
                    calcular(entrada)


class ServidorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.servidor = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def pedir(self, caminho, corpo=None):
        req = urllib.request.Request(self.base + caminho)
        if corpo is not None:
            req.data = json.dumps(corpo).encode("utf-8")
        try:
            with urllib.request.urlopen(req) as resp:
                return resp.status, resp.read()
        except urllib.error.HTTPError as erro:
            return erro.code, erro.read()

    def test_pagina_e_arquivos(self):
        for caminho in ("/", "/style.css", "/app.js"):
            self.assertEqual(self.pedir(caminho)[0], 200)

    def test_config(self):
        status, corpo = self.pedir("/api/config")
        self.assertEqual(status, 200)
        self.assertEqual(set(json.loads(corpo)), {"quantum", "aging"})

    def test_simular(self):
        status, corpo = self.pedir("/api/simular", dados())
        self.assertEqual(status, 200)
        self.assertIn("round_robin", json.loads(corpo)["resultados"])

    def test_simular_invalido(self):
        status, corpo = self.pedir("/api/simular", dados(quantum=0))
        self.assertEqual(status, 400)
        self.assertIn("erro", json.loads(corpo))

    def test_caminhos_desconhecidos(self):
        for caminho in ("/nada", "/../interface.py", "/web/app.js"):
            self.assertEqual(self.pedir(caminho)[0], 404)


if __name__ == "__main__":
    unittest.main()
