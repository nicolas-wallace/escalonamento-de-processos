class Processo:
    def __init__(self, pid, chegada, duracao, prioridade):
        self.pid = pid                # identificador (P1, P2, ...)
        self.chegada = chegada        # instante de criação
        self.duracao = duracao        # tempo total de CPU necessário
        self.prioridade = prioridade  # prioridade estática (maior número = maior prioridade)
        self.status = "novo"         # novo, pronto, executando ou terminado
        self.restante = duracao      # tempo restante de execução
        self.inicio = None           # primeira vez que ocupou a CPU
        self.termino = None          # instante em que terminou
        self.prioridade_dinamica = prioridade   # muda com o envelhecimento
        self.fila = (chegada, 0)                # posição na fila de prontos (round robin)

    @property
    def turnaround(self):
        return None if self.termino is None else self.termino - self.chegada

    @property
    def espera(self):
        tt = self.turnaround
        return None if tt is None else tt - self.duracao

    @property
    def resposta(self):
        return None if self.inicio is None else self.inicio - self.chegada
