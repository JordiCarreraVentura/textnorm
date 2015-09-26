class Streamer:
    def __init__(self, f, n=None):
        self.source = f
        self.n = n
        self.c = 0
    
    def __iter__(self):
        with open(self.source, 'rb') as rd:
            for l in rd:
                self.c += 1
                try:
                    yield l.decode('utf-8').strip()
                except Exception:
                    yield l.strip()
                if self.c >= self.n:
                    break
                if not self.c % 100000:
                    print self.c, self.n
