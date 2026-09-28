import unittest

from processo import Processo
from simulacao import simular


class EscalonamentoPorPrioridadeTests(unittest.TestCase):
    def setUp(self):
        self.processos = [
            Processo("P1", 0, 4, 1),
            Processo("P2", 1, 2, 3),
            Processo("P3", 1, 1, 2),
        ]

    def test_sem_preempcao_mantem_processo_ate_terminar(self):
        processos, linha, trocas = simular(self.processos, "prioridade_sem_preempcao")

        self.assertEqual(linha, ["P1"] * 4 + ["P2"] * 2 + ["P3"])
        self.assertEqual([p.termino for p in processos], [4, 6, 7])
        self.assertEqual(trocas, 2)

    def test_com_preempcao_interrompe_por_prioridade_maior(self):
        processos, linha, trocas = simular(self.processos, "prioridade_com_preempcao")

        self.assertEqual(linha, ["P1", "P2", "P2", "P3", "P1", "P1", "P1"])
        self.assertEqual([p.termino for p in processos], [7, 3, 4])
        self.assertEqual(trocas, 3)

    def test_prioridades_iguais_mantem_processo_em_execucao(self):
        processos = [Processo("P1", 0, 3, 3), Processo("P2", 1, 1, 3)]

        _, linha, trocas = simular(processos, "prioridade_com_preempcao")

        self.assertEqual(linha, ["P1", "P1", "P1", "P2"])
        self.assertEqual(trocas, 1)


if __name__ == "__main__":
    unittest.main()
