# imports
import re
from nltk.corpus import gutenberg
from timer import timer
from nltk.tokenize import sent_tokenize
import spacy
nlp = spacy.load('en_core_web_sm')

# dummy input text file
sp = gutenberg.raw('shakespeare-macbeth.txt')

# regex patterns
alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov|uk)"
digits = "([0-9])"
urls = "((http|https)\:\/\/)[a-zA-Z0-9\.\/\?\:@\-_=#]+\.([a-zA-Z]){2,6}([a-zA-Z0-9\.\&\/\?\:@\-_=#])*"


class TextSplitter:
    """A class to handle all text splitting functions

    Methods
    -------
    split_into_sentences(text)
       splits text into sentences using auxiliary functions

    process_substitutions(text)
        substitues regex patterns with stopwords

    process_special_cases(text)
        handles special cases

    process_special_chars(text)
        handles special characters

    replace_placeholders(text)
        replaces placeholders with punctuation

    create_sentences(text)
        creates a list of sentences
    
    split_into_sentences_with_nltk(text)
        splits text into sentences using nltk library
    
    split_into_sentences_with_spacy(text)
        splits text into sentences using spacy library

    """

    @classmethod
    @timer
    def split_into_sentences(cls, text: str) -> list[str]:
        """Creates a list of sentences after processing the text

        Parameters
        ----------
        text : str
            input text to be split into sentences

        Returns
        -------
        sentences: list[str]
            list of sentences after transformation
        """
        text = " " + text + "  "  # Do not understand the purpose of this
        text = text.replace("\n", " ")
        text = cls.process_substitutions(text)
        text = cls.process_special_chars(text)
        text = cls.replace_placeholders(text)
        sentences = cls.create_sentences(text)
        return sentences

    @classmethod
    def process_substitutions(cls, text: str) -> str:
        """Substitutes regex patterns with stopwords

        Parameters
        ----------
        text : str
           text which needs to be processed

        Returns
        -------
        text : str
            text after substitutions
        """
        text = re.sub(prefixes, "\\1<prd>", text)
        text = re.sub(websites, "<prd>\\1", text)
        text = re.sub(digits + "[.]" + digits, "\\1<prd>\\2", text)
        text = re.sub("\s" + alphabets + "[.] ", " \\1<prd> ", text)
        text = re.sub(acronyms+" "+starters, "\\1<stop> \\2", text)
        text = re.sub(alphabets + "[.]" + alphabets + "[.]" +
                      alphabets + "[.]", "\\1<prd>\\2<prd>\\3<prd>", text)
        text = re.sub(alphabets + "[.]" + alphabets +
                      "[.]", "\\1<prd>\\2<prd>", text)
        text = re.sub(" "+suffixes+"[.] "+starters, " \\1<stop> \\2", text)
        text = re.sub(" "+suffixes+"[.]", " \\1<prd>", text)
        text = re.sub(" " + alphabets + "[.]", " \\1<prd>", text)
        return text

    @classmethod
    def process_special_cases(cls, text: str) -> str:
        """Handles special case substitutions

        Parameters
        ----------
        text : str
            _description_

        Returns
        -------
        str
            text after special case substitutions

        Notes
        -----
        url and ellipses are handled using generator functions which make them more efficient
        """
        # urls
        for match in re.compile(urls).finditer(text):
            text = text.replace(match.group(
                0), match.group(0).replace('.', '<prd>'))

        # ellipses
        for match in re.compile(r"(\.)(\.+)").finditer(text):
            text = text.replace(match.group(
                0), (len(match.group(0)) * '<prd>') + '<stop>')

        if "Ph.D" in text:
            text = text.replace("Ph.D.", "Ph<prd>D<prd>")

    @classmethod
    def process_special_chars(cls, text: str) -> str:
        """Handles special character substitutions

        Parameters
        ----------
        text : str
            text that needs to be processed

        Returns
        -------
        text : str
            text after special character substitutions
        """
        if "”" in text:
            text = text.replace(".”", "”.")
        if "\"" in text:
            text = text.replace(".\"", "\".")
        if "!" in text:
            text = text.replace("!\"", "\"!")
        if "?" in text:
            text = text.replace("?\"", "\"?")
        return text

    @classmethod
    def replace_placeholders(cls, text: str) -> str:
        """Replaces placeholders with punctuation

        Parameters
        ----------
        text : str
            text that needs to be processed

        Returns
        -------
        text : str
            text after replacing placeholders with punctuation
        """
        text = text.replace(".", ".<stop>")
        text = text.replace("?", "?<stop>")
        text = text.replace("!", "!<stop>")
        text = text.replace("<prd>", ".")
        return text

    @classmethod
    def create_sentences(cls, text: str) -> list[str]:
        """Creates a list of sentences

        Parameters
        ----------
        text : str
            text that needs to be processed

        Returns
        -------
        sentence : list[str]
            list of sentences
        """
        sentences = text.split("<stop>")
        sentences = [s.strip() for s in sentences]
        sentences = [s for s in sentences if not len(s) == 0]
        return sentences
    
    @classmethod
    @timer
    def split_into_sentences_with_nltk(cls, text: str) -> list[str]:
        """Creates a list of sentences using nltk tokenizer

        Parameters
        ----------
        text : str
            text that needs to be processed
        
        Returns
        -------
        sentence : list[str]
            list of sentences
        """
        sentences = sent_tokenize(text)
        return sentences
    
    @classmethod
    @timer
    def split_into_sentences_with_spacy(cls, text: str) -> list[str]:
        """Creates a list of sentences using spacy tokenizer

        Parameters
        ----------
        text : str
            text that needs to be processed

        Returns
        -------
        sentences : list[str]
            list of sentences
        """
        doc = nlp(text)
        sentences = [sent.text for sent in doc.sents]
        return sentences


# Limitation Demonstration:
limit_test_sentence = 'I don\'t know what I could\'ve done to save  Martin Luther King Jr. \n This is a second sentence talking about mr. King. Mr. King was nice person.'

# testing regex tokenizer speed on a large sentence
print('regex long sentence:')
regex_tokens = TextSplitter.split_into_sentences(sp)
# testing regex tokenizer for limitations
print('regex limit test sentence:')
regex_limit_token = TextSplitter.split_into_sentences(limit_test_sentence)
print('regex token:\n',regex_limit_token)
print('sentence count:', len(regex_limit_token)) # fewer tokens than expected

# Simplicity option 1:  use nltk tokenizer
# testing nltk tokenizer speed on a large sentence
print('nltk long sentence:')
nltk_token = TextSplitter.split_into_sentences_with_nltk(sp)
# testing nltk tokenizer for limitations 
print('nltk limit test sentence:')
nltk_limit_token = TextSplitter.split_into_sentences_with_nltk(limit_test_sentence)
print('nltk token:\n', nltk_limit_token)
print('sentence count:', len(nltk_limit_token))

# Both have three tokens, but nltk has correct sentences tokenized.

# Simplicity option 2: use spacy tokenizer
# testing spacy tokenizer speed on a large sentence
print('spacy long sentence:')
spacy_tokens = TextSplitter.split_into_sentences_with_spacy(sp)
# testing spacy tokenizer for limitations
print('spacy limit test sentence:')
spacy_limit_token = TextSplitter.split_into_sentences_with_spacy(limit_test_sentence)
print('spacy token:\n', spacy_limit_token)
print('sentence count:', len(spacy_limit_token))
