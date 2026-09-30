import unittest

from escalonador.processo import Processo
from escalonador.simulacao import simular


class PriocTests(unittest.TestCase):
    def setUp(self):
        self.processos = [
            Processo("P1", 0, 4, 1),
            Processo("P2", 1, 2, 3),
            Processo("P3", 1, 1, 2),
        ]

    def test_mantem_processo_ate_terminar(self):
        processos, linha, trocas = simular(self.processos, "prioc")

        self.assertEqual(linha, ["P1"] * 4 + ["P2"] * 2 + ["P3"])
        self.assertEqual([p.termino for p in processos], [4, 6, 7])
        self.assertEqual(trocas, 2)

    def test_exemplo_do_enunciado(self):
        processos = [Processo("P1", 0, 5, 2), Processo("P2", 0, 2, 3),
                     Processo("P3", 1, 4, 1), Processo("P4", 3, 3, 4)]

        processos, linha, _ = simular(processos, "prioc")

        self.assertEqual(linha, ["P2"] * 2 + ["P1"] * 5 + ["P4"] * 3 + ["P3"] * 4)
        self.assertEqual([p.termino for p in processos], [7, 2, 14, 10])


if __name__ == "__main__":
    unittest.main()
