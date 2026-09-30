import unittest

from escalonador.processo import Processo
from escalonador.simulacao import simular


class SjfTests(unittest.TestCase):
    def test_exemplo_do_enunciado(self):
        processos = [Processo("P1", 0, 5, 2), Processo("P2", 0, 2, 3),
                     Processo("P3", 1, 4, 1), Processo("P4", 3, 3, 4)]

        processos, linha, trocas = simular(processos, "SJF")

        self.assertEqual(linha, ["P2"] * 2 + ["P3"] * 4 + ["P4"] * 3 + ["P1"] * 5)
        self.assertEqual([p.termino for p in processos], [14, 2, 6, 9])
        self.assertEqual(trocas, 3)

    def test_nao_interrompe_para_processo_mais_curto(self):
        processos = [Processo("P1", 0, 5, 1), Processo("P2", 1, 1, 1)]

        _, linha, _ = simular(processos, "SJF")

        self.assertEqual(linha, ["P1"] * 5 + ["P2"])

    def test_empate_de_duracao_escolhe_pelo_pid(self):
        processos = [Processo("P1", 0, 1, 1), Processo("P2", 0, 3, 1), Processo("P3", 0, 3, 1)]

        _, linha, _ = simular(processos, "SJF")

        self.assertEqual(linha, ["P1"] + ["P2"] * 3 + ["P3"] * 3)


if __name__ == "__main__":
    unittest.main()
