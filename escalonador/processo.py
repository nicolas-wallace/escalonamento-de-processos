class Processo:
    def __init__(self, pid, chegada, duracao, prioridade):
        self.pid = pid
        self.chegada = chegada
        self.duracao = duracao
        self.prioridade = prioridade
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
