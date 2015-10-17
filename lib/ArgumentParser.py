
BASE_CONFIG = {
    'corpus': '',
    'out': '',
    'tmp': '',
    'minf': 5,
    'flush': (1, 200000),
    'ngrams': 5,
    'ndocs': None,
    'silent': False,
    'smooth': None
}

HELP = 'No help available yet.'


class ArgumentParser:

    def __init__(self, args):
        self.args = args
        self.names = {
            '-i': 'corpus',
            '-o': 'out',
            '-t': 'tmp',
            '--flush': 'flush',
            '--silent': 'silent',
            '-n': 'ngrams',
            '--ndocs': 'ndocs',
            '--minf': 'minf',
            '--smooth': 'smooth'
        }
        self.parsers = {
            '-i': None,
            '-o': None,
            '-t': None,
            '--flush': self.flush,
            '-n': self.integer,
            '--ndocs': self.integer,
            '--minf': self.integer,
            '--smooth': self.autofloat
        }
        return
    
    def is_flag(self, flag):
        if flag in self.names.keys():
            return True
        else:
            return False

    def integer(self, arg):
        return int(arg)

    def floatint(self, arg):
        if len(arg.split('.')) > 1:
            return float(arg)
        else:
            return int(arg)

    def autofloat(self, arg):
        if arg == 'auto':
            return None
        else:
            return float(arg)

    def flush(self, arg):
        x, over = arg.split(':')
        return (int(x), int(over))
    
    def make_paths(self, args):
        corpus = args['corpus']
        if not args['out']:
            args['out'] = '%s.textnorm.out.txt' % corpus
        if not args['tmp']:
            args['tmp'] = '/tmp/textnorm.main.temp'

    def parseargs(self):
        # -i            corpus
        # -o            out, default out wrt corpus
        # -t            tmp, default tmp wrt corpus
        # --maxk        (max_k, max_f, min_f) or 'auto'
        # --flush       flushing ratio, default (1, 200000)
        # --silent      silent, default verbose
        # -n            ngrams, default 10
        # --ndocs       ndocs, default None
        args = BASE_CONFIG
        for i, flag in enumerate(self.args):
            if self.is_flag(flag):
                argname = self.names[flag]
                if argname == 'silent':
                    args[argname] = True
                    continue
                parser = self.parsers[flag]
                if not parser:
                    args[argname] = self.args[i + 1]
                else:
                    args[argname] = parser(self.args[i + 1])
        if not args['corpus']:
            exit(HELP)
        self.make_paths(args)
        return args
