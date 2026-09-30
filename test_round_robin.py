import unittest

from entrada import ler_configuracao
from processo import Processo
from simulacao import simular


class RoundRobinTests(unittest.TestCase):
    def setUp(self):
        self.processos = [
            Processo("P1", 0, 5, 2),
            Processo("P2", 0, 2, 3),
            Processo("P3", 1, 4, 1),
            Processo("P4", 3, 3, 4),
        ]

    def test_exemplo_do_enunciado_com_quantum_2(self):
        processos, linha, trocas = simular(self.processos, "round_robin", quantum=2)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P3", "P3", "P1", "P1",
                                 "P4", "P4", "P3", "P3", "P1", "P4"])
        self.assertEqual([p.termino for p in processos], [13, 4, 12, 14])
        self.assertEqual(trocas, 7)

    def test_quantum_grande_vira_fcfs(self):
        processos = [Processo("P1", 0, 3, 1), Processo("P2", 1, 2, 1)]

        _, linha, trocas = simular(processos, "round_robin", quantum=100)

        self.assertEqual(linha, ["P1"] * 3 + ["P2"] * 2)
        self.assertEqual(trocas, 1)

    def test_chegada_no_fim_do_quantum_entra_antes_do_processo_interrompido(self):
        processos = [Processo("P1", 0, 4, 1), Processo("P2", 1, 3, 1), Processo("P3", 2, 2, 1)]

        _, linha, _ = simular(processos, "round_robin", quantum=2)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P3", "P3", "P1", "P1", "P2"])

    def test_processo_sozinho_nao_tem_troca_de_contexto(self):
        _, linha, trocas = simular([Processo("P1", 0, 5, 1)], "round_robin", quantum=2)

        self.assertEqual(linha, ["P1"] * 5)
        self.assertEqual(trocas, 0)


class RoundRobinComEnvelhecimentoTests(unittest.TestCase):
    def test_exemplo_do_enunciado(self):
        processos = [
            Processo("P1", 0, 5, 2),
            Processo("P2", 0, 2, 3),
            Processo("P3", 1, 4, 1),
            Processo("P4", 3, 3, 4),
        ]

        processos, linha, trocas = simular(processos, "round_robin_prioridade_aging",
                                           quantum=2, aging=1)

        self.assertEqual(linha, ["P2", "P2", "P1", "P1", "P4", "P4", "P3",
                                 "P3", "P4", "P1", "P1", "P3", "P3", "P1"])
        self.assertEqual([p.termino for p in processos], [14, 2, 13, 9])
        self.assertEqual(trocas, 7)

    def test_processo_de_maior_prioridade_nao_repete_o_quantum_seguinte(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 1)]

        _, linha, _ = simular(processos, "round_robin_prioridade_aging", quantum=2, aging=0)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2"] * 3)

    def test_sem_envelhecimento_a_menor_prioridade_espera_os_outros_terminarem(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 3), Processo("P3", 0, 2, 1)]

        processos, _, _ = simular(processos, "round_robin_prioridade_aging", quantum=2, aging=0)

        self.assertEqual(processos[2].inicio, 12)

    def test_com_envelhecimento_a_menor_prioridade_chega_a_executar_antes(self):
        processos = [Processo("P1", 0, 6, 5), Processo("P2", 0, 6, 3), Processo("P3", 0, 2, 1)]

        processos, _, _ = simular(processos, "round_robin_prioridade_aging", quantum=2, aging=2)

        self.assertEqual(processos[2].inicio, 6)

    def test_nao_ha_preempcao_por_prioridade_no_meio_do_quantum(self):
        processos = [Processo("P1", 0, 4, 1), Processo("P2", 1, 2, 9)]

        _, linha, _ = simular(processos, "round_robin_prioridade_aging", quantum=2, aging=1)

        self.assertEqual(linha, ["P1", "P1", "P2", "P2", "P1", "P1"])

    def test_terminar_no_meio_do_quantum_nao_envelhece_ninguem(self):
        processos = [Processo("P1", 0, 1, 3), Processo("P2", 0, 5, 2), Processo("P3", 0, 5, 1)]

        _, linha, _ = simular(processos, "round_robin_prioridade_aging", quantum=2, aging=10)

        self.assertEqual(linha[1:3], ["P2", "P2"])


class ConfiguracaoTests(unittest.TestCase):
    def test_uma_chave_por_linha(self):
        self.assertEqual(ler_configuracao(["quantum:2", "aging:1"]), (2, 1))

    def test_duas_chaves_na_mesma_linha(self):
        self.assertEqual(ler_configuracao(["quantum:3 aging:0"]), (3, 0))


if __name__ == "__main__":
    unittest.main()
