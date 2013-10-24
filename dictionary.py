
class Dictionary():
    def __init__(self, language_str, path):

        self.language        = language_str
        self.rank_hash       = {}
        self.correction_hash = {}
        self.negation_hash   = set()
        self.pos_word_hash   = set()
        self.neg_word_hash   = set()
        self.pos_emoc_hash   = set()
        self.neg_emoc_hash   = set()

        if path[-1] != '/':
            path = path + '/'

        adjlist        = path + 'score_list.txt'
        wordcorrection = path + 'word_corrections.txt'
        negation       = path + 'neg_words.txt'
        poslist        = path + 'pos_sentiwords.txt'
        neglist        = path + 'neg_sentiwords.txt'
        posemocon      = path + 'positive_emoticons.txt'
        negemocon      = path + 'negative_emoticons.txt'

        try:
            with open(adjlist) as f:
                for line in f:
                    (key, val) = line.lower().split()
                    self.rank_hash[key] = float(val)

            with open(wordcorrection) as f:
                for line in f:
                    (wrong, right) = line.lower().split(",")
                    wrong = wrong.strip()
                    right = right.strip()
                    self.correction_hash[wrong] = right

            with open(negation) as f:
                for line in f:
                    key = line.lower().strip()
                    self.negation_hash.add(key)

            with open(poslist) as f:
                for line in f:
                    key = line.lower().strip()
                    self.pos_word_hash.add(key)

            with open(neglist) as f:
                for line in f:
                    key = line.lower().strip()
                    self.neg_word_hash.add(key)

            with open(posemocon) as f:
                for line in f:
                    key = line.lower().strip()
                    self.pos_emoc_hash.add(key)

            with open(negemocon) as f:
                for line in f:
                    key = line.lower().strip()
                    self.neg_emoc_hash.add(key)

        except Exception:
            print "ERROR! Unable to load \"%s\" dictionary in %s" % (language_str, path)
