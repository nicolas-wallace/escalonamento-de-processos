import unittest

from escalonador.processo import Processo


class ProcessoTests(unittest.TestCase):
    def test_metricas_depois_de_executar(self):
        p = Processo("P1", 2, 4, 1)
        p.inicio = 5
        p.termino = 11

        self.assertEqual(p.turnaround, 9)
        self.assertEqual(p.espera, 5)
        self.assertEqual(p.resposta, 3)

    def test_metricas_antes_de_executar(self):
        p = Processo("P1", 0, 3, 1)

        self.assertIsNone(p.turnaround)
        self.assertIsNone(p.espera)
        self.assertIsNone(p.resposta)


if __name__ == "__main__":
    unittest.main()
