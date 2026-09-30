import unittest

from escalonador.processo import Processo
from escalonador.simulacao import simular


class FcfsTests(unittest.TestCase):
    def test_exemplo_do_enunciado(self):
        processos = [Processo("P1", 0, 5, 2), Processo("P2", 0, 2, 3),
                     Processo("P3", 1, 4, 1), Processo("P4", 3, 3, 4)]

        processos, linha, trocas = simular(processos, "fcfs")

        self.assertEqual(linha, ["P2"] * 2 + ["P1"] * 5 + ["P3"] * 4 + ["P4"] * 3)
        self.assertEqual([p.termino for p in processos], [7, 2, 11, 14])
        self.assertEqual(trocas, 3)

    def test_atende_na_ordem_de_chegada_mesmo_com_entrada_desordenada(self):
        processos = [Processo("P1", 5, 1, 1), Processo("P2", 0, 2, 1), Processo("P3", 2, 1, 1)]

        _, linha, _ = simular(processos, "fcfs")

        self.assertEqual(linha, ["P2", "P2", "P3", None, None, "P1"])

    def test_nao_interrompe_quem_esta_executando(self):
        processos = [Processo("P1", 0, 5, 1), Processo("P2", 1, 1, 9)]

        _, linha, _ = simular(processos, "fcfs")

        self.assertEqual(linha, ["P1"] * 5 + ["P2"])


if __name__ == "__main__":
    unittest.main()
