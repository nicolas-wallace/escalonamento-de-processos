import unittest

from escalonador.processo import Processo
from escalonador.simulacao import simular


class RrAgingTests(unittest.TestCase):
    def test_exemplo_do_enunciado(self):
        processos = [
            Processo("P1", 0, 5, 2),
            Processo("P2", 0, 2, 3),
            Processo("P3", 1, 4, 1),
            Processo("P4", 3, 3, 4),
        ]

        processos, linha, trocas = simular(processos, "rr_aging",
                                           quantum=2, aging=1)

        self.assertEqual(linha, ["P2", "P2", "P1", "P1", "P4", "P4", "P3",
                                 "P3", "P4", "P1", "P1", "P3", "P3", "P1"])
        self.assertEqual([p.termino for p in processos], [14, 2, 13, 9])
        self.assertEqual(trocas, 7)

    def test_processo_de_maior_prioridade_nao_repete_o_quantum_seguinte(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 1)]

        _, linha, _ = simular(processos, "rr_aging", quantum=2, aging=0)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2"] * 3)

    def test_sem_envelhecimento_a_menor_prioridade_espera_os_outros_terminarem(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 3), Processo("P3", 0, 2, 1)]

        processos, _, _ = simular(processos, "rr_aging", quantum=2, aging=0)

        self.assertEqual(processos[2].inicio, 12)

    def test_com_envelhecimento_a_menor_prioridade_chega_a_executar_antes(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 3), Processo("P3", 0, 2, 1)]

        processos, _, _ = simular(processos, "rr_aging", quantum=2, aging=2)

        self.assertEqual(processos[2].inicio, 6)

    def test_nao_ha_preempcao_por_prioridade_no_meio_do_quantum(self):
        processos = [Processo("P1", 0, 4, 1), Processo("P2", 1, 2, 9)]

        _, linha, _ = simular(processos, "rr_aging", quantum=2, aging=1)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P1", "P1"])

    def test_terminar_no_meio_do_quantum_nao_envelhece_ninguem(self):
        processos = [Processo("P1", 0, 1, 3), Processo("P2", 0, 5, 2), Processo("P3", 0, 5, 1)]

        _, linha, _ = simular(processos, "rr_aging", quantum=2, aging=10)

        self.assertEqual(linha[1:3], ["P2", "P2"])


if __name__ == "__main__":
    unittest.main()
