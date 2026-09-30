import unittest

from escalonador.entrada import ler_configuracao, ler_processos


class ConfiguracaoTests(unittest.TestCase):
    def test_uma_chave_por_linha(self):
        self.assertEqual(ler_configuracao(["quantum:2", "aging:1"]), (2, 1))

    def test_duas_chaves_na_mesma_linha(self):
        self.assertEqual(ler_configuracao(["quantum:3 aging:0"]), (3, 0))


class ProcessosTests(unittest.TestCase):
    def test_ignora_linhas_em_branco_e_numera_pela_posicao(self):
        processos = ler_processos(["0 5 2", "", "1 4 1"])

        self.assertEqual([p.pid for p in processos], ["P1", "P3"])
        self.assertEqual([(p.chegada, p.duracao, p.prioridade) for p in processos],
                         [(0, 5, 2), (1, 4, 1)])


if __name__ == "__main__":
    unittest.main()
