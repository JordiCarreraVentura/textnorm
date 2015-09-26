import re

class Preprocessor:
    def __init__(self, using=[
        'lowercasing',
        'punctuation',
        'numerical_normalization',
        'non_alphabetical',
        'blanks'
    ]):
        self._2do = using
        self.implemented = {
            'lowercasing': self.lowercase,
            'numerical_normalization': self.num_norm,
            'punctuation': self.punct,
            'non_alphabetical': self.clean,
            'blanks': self.blanks
        }
        self.punct = re.compile('[\.,;:!\?\-\(\)]')
        self.num = re.compile('([0-9]+(.){,3})?[0-9]+')
        self.spaces = re.compile(' {2,}')
        self.junk = re.compile('[^a-z ]', re.IGNORECASE)
        self.stop = re.compile('STOP')
        self.z = re.compile('Z')
    
    def __call__(self, line):
        line = self.stop.sub('.', line)
        line = self.z.sub('1', line)
        for method in self._2do:
            funct = self.implemented[method]
            line = funct(line)
        return line
    
    def lowercase(self, line):
        return line.lower()
    
    def num_norm(self, line):
        return self.num.sub('Z', line)
    
    def punct(self, line):
        return self.punct.sub(' STOP ', line)
    
    def blanks(self, line):
        return self.spaces.sub(' ', line)
    
    def clean(self, line):
        return self.junk.sub(' ', line)
