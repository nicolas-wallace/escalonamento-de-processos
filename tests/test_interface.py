import json
import threading
import unittest
import urllib.error
import urllib.request
from http.server import HTTPServer

from interface import Handler, calcular

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
        self.assertEqual(len(calcular(dados())["resultados"]), 7)

    def test_rr_do_enunciado(self):
        rr = calcular(dados())["resultados"]["RR"]
        self.assertEqual(rr["tt_medio"], 9.75)
        self.assertEqual(rr["tw_medio"], 6.25)
        self.assertEqual(rr["tr_medio"], 2.5)
        self.assertEqual(rr["trocas"], 7)

    def test_entradas_invalidas(self):
        invalidas = [
            dados(processos=[]),
            dados(processos=[{"chegada": 0, "duracao": 0, "prioridade": 1}]),
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
        cls.servidor = HTTPServer(("127.0.0.1", 0), Handler)
        cls.base = f"http://127.0.0.1:{cls.servidor.server_address[1]}"
        threading.Thread(target=cls.servidor.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.servidor.shutdown()
        cls.servidor.server_close()

    def test_pagina(self):
        with urllib.request.urlopen(self.base + "/") as resp:
            self.assertEqual(resp.status, 200)

    def test_simular(self):
        req = urllib.request.Request(self.base + "/api/simular", data=json.dumps(dados()).encode())
        with urllib.request.urlopen(req) as resp:
            self.assertIn("RR", json.load(resp)["resultados"])

    def test_simular_invalido_devolve_400(self):
        req = urllib.request.Request(self.base + "/api/simular", data=json.dumps(dados(quantum=0)).encode())
        with self.assertRaises(urllib.error.HTTPError) as erro:
            urllib.request.urlopen(req)
        self.assertEqual(erro.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
