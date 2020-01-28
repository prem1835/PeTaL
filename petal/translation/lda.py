# Adapted from https://rstudio-pubs-static.s3.amazonaws.com/79360_850b2a69980c4488b1db95987a24867a.html
# Editor: Lucas Saldyt
# The following documentation is also exceptionally helpful: https://radimrehurek.com/gensim/models/ldamodel.html
# I also recommend reading the relevant documentation for nltk functions (tokenizing, stemming, and filtering stop words)

from nltk.tokenize import word_tokenize
from nltk.corpus   import stopwords
from nltk.stem     import PorterStemmer

from gensim import corpora, models

from string import punctuation
from contractions import fix_word as expand_contractions

from pprint import pprint

class TopicModeller:
    def __init__(self, **kwargs):
        '''
        kwargs::

        class gensim.models.ldamodel.LdaModel(corpus=None, num_topics=100, id2word=None, distributed=False, chunksize=2000, passes=1, update_every=1, alpha='symmetric', eta=None, decay=0.5, offset=1.0, eval_every=10, iterations=50, gamma_threshold=0.001, minimum_probability=0.01, random_state=None, ns_conf=None, minimum_phi_value=0.01, per_word_topics=False, callbacks=None, dtype=<class 'numpy.float32'>)¶
        '''
        self.stop_words = set(stopwords.words('english'))
        self.stemmer    = PorterStemmer()
        self.lda_model  = None
        self.lda_kwargs = kwargs
        self.dictionary = None

    def clean(self, doc):
        for word in word_tokenize(doc):
            words = expand_contractions(word)
            for word in words:
                if word not in self.stop_words and word not in punctuation:
                    yield self.stemmer.stem(word)

    def update(self, docs):
        cleaned    = [list(self.clean(doc)) for doc in docs]
        self.dictionary = corpora.Dictionary(cleaned)
        corpus     = [self.dictionary.doc2bow(text) for text in cleaned]

        if self.lda_model is None:
            self.lda_model = models.ldamodel.LdaModel(corpus, id2word=self.dictionary, **self.lda_kwargs)
        else:
            self.lda_model.update(corpus, id2word=self.dictionary)
        # print(self.lda_model.print_topics(num_topics=3, num_words=3))

    def classify(self, doc):
        bow = self.dictionary.doc2bow(list(self.clean(doc)))
        topic = max(self.lda_model.get_document_topics(bow), key=lambda x : x[1])[0]
        return self.lda_model.show_topic(topic)

def main():
    doc_a = "Brocolli is good to eat. My brother likes to eat good brocolli, but not my mother."
    doc_b = "My mother spends a lot of time driving my brother around to baseball practice."
    doc_c = "Some health experts suggest that driving may cause increased tension and blood pressure."
    doc_d = "I often feel pressure to perform well at school, but my mother never seems to drive my brother to do better."
    doc_e = "Health professionals say that brocolli is good for your health."
    docs = [doc_a, doc_b, doc_c, doc_d]
    modeller = TopicModeller(num_topics=3, passes=20, alpha='auto', minimum_probability=0.01, decay=0.5)
    modeller.update(docs)
    print(modeller.classify(doc_e))

if __name__ == '__main__':
    main()

