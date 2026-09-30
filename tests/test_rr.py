import unittest

from escalonador.processo import Processo
from escalonador.simulacao import simular


class RrTests(unittest.TestCase):
    def setUp(self):
        self.processos = [
            Processo("P1", 0, 5, 2),
            Processo("P2", 0, 2, 3),
            Processo("P3", 1, 4, 1),
            Processo("P4", 3, 3, 4),
        ]

    def test_exemplo_do_enunciado_com_quantum_2(self):
        processos, linha, trocas = simular(self.processos, "rr", quantum=2)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P3", "P3", "P1", "P1",
                                 "P4", "P4", "P3", "P3", "P1", "P4"])
        self.assertEqual([p.termino for p in processos], [13, 4, 12, 14])
        self.assertEqual(trocas, 7)

    def test_quantum_grande_vira_fcfs(self):
        processos = [Processo("P1", 0, 3, 1), Processo("P2", 1, 2, 1)]

        _, linha, trocas = simular(processos, "rr", quantum=100)

        self.assertEqual(linha, ["P1"] * 3 + ["P2"] * 2)
        self.assertEqual(trocas, 1)

    def test_chegada_no_fim_do_quantum_entra_antes_do_processo_interrompido(self):
        processos = [Processo("P1", 0, 4, 1), Processo("P2", 1, 3, 1), Processo("P3", 2, 2, 1)]

        _, linha, _ = simular(processos, "rr", quantum=2)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P3", "P3", "P1", "P1", "P2"])

    def test_processo_sozinho_nao_tem_troca_de_contexto(self):
        _, linha, trocas = simular([Processo("P1", 0, 5, 1)], "rr", quantum=2)

        self.assertEqual(linha, ["P1"] * 5)
        self.assertEqual(trocas, 0)


if __name__ == "__main__":
    unittest.main()
