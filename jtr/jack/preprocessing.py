import re

__pattern = re.compile('\w+|[^\w\s]')

@staticmethod
def tokenize(text):
    return FastQAInputModule.__pattern.findall(text)

def prepare_data(self, dataset, vocab, with_answers=False,
        to_lowercase=True):

    qa_setting = None
    corpus = {"support": [], "question": []}

    for d in dataset:
        if isinstance(d, QASetting):
            qa_setting = d
        else:
            qa_setting, answer = d

        if to_lowercase:
            corpus["support"].append(" ".join(qa_setting.support).lower())
            corpus["question"].append(qa_setting.question.lower())
        else:
            corpus["support"].append(" ".join(qa_setting.support))
            corpus["question"].append(qa_setting.question)

    corpus_tokenized = deep_map(corpus, self.tokenize, ['question', 'support'])
    corpus_ids = deep_map(corpus_tokenized, vocab, ['question', 'support'])

    word_in_question = []
    question_lengths = []
    support_lengths = []
    token_offsets = []
    answer_spans = []

    for i, (q, s) in enumerate(zip(corpus_tokenized["question"], corpus_tokenized["support"])):
        support_lengths.append(len(s))
        question_lengths.append(len(q))

        # char to token offsets
        support = corpus["support"][i]
        offsets = token_to_char_offsets(support, s)
        token_offsets.append(offsets)

        # word in question feature
        wiq = []
        for token in s:
            wiq.append(float(token in q))
        word_in_question.append(wiq)

        if with_answers:
            answers = dataset[i][1]
            spans = []
            for a in answers:
                start = 0
                while start < len(offsets) and offsets[start] < a.span[0]:
                    start += 1

                if start == len(offsets):
                    continue

                end = start
                while end + 1 < len(offsets) and offsets[end + 1] < a.span[1]:
                    end += 1
                if (start, end) not in spans:
                    spans.append((start, end))
            answer_spans.append(spans)

    return corpus_tokenized["question"], corpus_ids["question"], question_lengths, \
           corpus_tokenized["support"], corpus_ids["support"], support_lengths, \
           word_in_question, token_offsets, answer_spans

