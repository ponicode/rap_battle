import random
import markovify #uses markov models to generate new sentences
import ast  
from rhyme import rhyme_finder #uses cmudict to find rhyming words based on phonetics
import tqdm
import os
from nltk.tokenize import word_tokenize
import pickle


class Rapper:
    """Ponicode Rapper generates lyrics by training on rap songs"""

    def __init__(self):
        self.data_dir = 'data'
        
    def remove_punctuation(self, word):
        for punctuation in ['"','?','!', ',','.']:
            word = word.replace(punctuation, '')
        return word
        
    def load_data(self, data_dir=None):
        """
            Input: String data dir
            Output: String with all lyrics
        """
        lyrics_data = ''
        if not data_dir:
            data_dir = self.data_dir
        lyrics_files_paths = [f'{data_dir}/{file_path}' for file_path in os.listdir(data_dir) if '.txt' in file_path]
        for file_path in lyrics_files_paths:
            with open(file_path, 'r') as f:
                lyrics_data += f.read() + '\n'
        self.tokenized_text = word_tokenize(lyrics_data)
        return lyrics_data
        
    def build_space(self, lyrics_data, sentences_number=5000, state_size=2):
        """ 
            Input: String of lyrics with all data
            Output: List of generated sentences of size sentences_number
        """
        self.markov_model = markovify.NewlineText(lyrics_data, state_size)
        sentences = []
        while len(sentences) < sentences_number:
            line = self.markov_model.make_sentence()
            if line:
                sentences.append(line)
        return sentences
    
    def build_rhyme_list(self, sentences, show_errors=False):
        """
            - Input: Generated sentences by markov model
            - Output: List of dict with rhyme and lyrics data
                    [{'line': 'All the pain I thought we could be',
                     'last_word': 'be',
                     'rhymes': ['be',
                      'me',
                      'somebody',
                      'only',
                    },
                    ..]
        """
        rhymes_list = []
        for line in tqdm.tqdm(sentences):
            try:
                rhymes_dict = {}
                last_word = line.rsplit()[-1]
                last_word = self.remove_punctuation(last_word)
                rhymes_dict = {'line': line,
                                    'last_word' : last_word,
                                    'rhymes': [last_word] + rhyme_finder(last_word, self.tokenized_text)
                                   }
                rhymes_list.append(rhymes_dict)
            except Exception as e:
                if show_errors:
                    print(e)
        return rhymes_list
    
    def build_equivalence_classes(self, rhymes_list):
        """
            - Input: List of dict with rhyme and lyrics data
                    [{'line': 'All the pain I thought we could be',
                     'last_word': 'be',
                     'rhymes': ['be',
                      'me',
                      'somebody',
                      'only',
                    },
                    ..]
            - Output: List of dict of equivalent classes grouped by rhymes
                    [
                        {
                            'be': [{'line': 'All the pain I thought we could be',
                                   'last_word': 'be',
                                   'rhymes': ['be',
                                    'me',
                                    'somebody',}
                                    ....
                                    ],
                             'me': [{'line': 'Do you feel me?',
                                      'last_word': 'me',
                                      'rhymes': ['me',
                                       'baby',
                                       'somebody',
                                       'only',
                                       ...
                                       ]
                        },
                        ...

                    ..]
        """
        equivalence_list = []
        k = 0
        while len(rhymes_list) > 0:
            # Initialize first representor
            representor = rhymes_list[0]
            # Create last word first key
            last_word_representor = representor['last_word']
            equivalence_list.append({last_word_representor: [representor]})
            rhymes_list = rhymes_list[1:]
            # Loops over all sentences to group by rhymes and last word
            for i, rhyme_dict in enumerate(rhymes_list):
                rhymes = rhyme_dict['rhymes']
                if list(set(rhymes).intersection(representor['rhymes'])) != []:
                    last_word = rhyme_dict['last_word']
                    # For never seen last word
                    if last_word not in equivalence_list[k].keys():
                        equivalence_list[k][last_word] = [rhyme_dict]
                    # For already seen last word
                    else:
                        equivalence_list[k][last_word].append(rhyme_dict)
                        rhymes_list.remove(rhyme_dict)
            k += 1
        return equivalence_list
    
    
    def train(self, lyrics_data, sentences_number=5000, state_size=2, mod='artistic'):
        """Trains model of equivalence classes from lyrics"""
        print(f'Generating a space of {sentences_number} sentences')
        sentences = self.build_space(lyrics_data, sentences_number, state_size)
        self.free_style_sentences = sentences
        print(f'Grouping the sentences by rhymes')
        if mod == 'artistic':
            rhymes_list = self.build_rhyme_list(sentences)
            print(f'Creating the equivalence classes')
            equivalence_list = self.build_equivalence_classes(rhymes_list)
            print('Training Done')
            self.equivalence_list = equivalence_list
    
    
    def save_model(self, file_path):
        with open(file_path, 'wb') as file:
            pickle.dump(self, file, pickle.HIGHEST_PROTOCOL)
            
    def load_model(self, file_path):
        with open(file_path, 'rb') as file:
            self.__dict__.update(pickle.load(file).__dict__)
        
    def generate_random_pair(self, cluster):
        values_cluster = list(cluster.values())
        random.shuffle(values_cluster)
        rhyme1_cluster, rhyme2_cluster = random.choice(values_cluster[0]), random.choice(values_cluster[1])
        return rhyme1_cluster['line'], rhyme2_cluster['line']
    
    def generate_artistic_verses(self, N_VERSES=8):
        patterns = ['abab', 'aabb', 'abba']
        generated_lyrics = ''
        equivalence_clusters = [cluster for cluster in self.equivalence_list if len(cluster.keys()) > 1]
        for _ in range(N_VERSES):
            pattern = random.choice(patterns)
            random.shuffle(equivalence_clusters)
            cluster1, cluster2 = equivalence_clusters[0], equivalence_clusters[1]
            a1, a2 = self.generate_random_pair(cluster1)
            b1, b2 = self.generate_random_pair(cluster2)
            if pattern == 'abab':
                generated_lyrics += '\n'.join([a1, b1, a2, b2])
            elif pattern == 'aabb':
                generated_lyrics += '\n'.join([a1, a2, b1, b2])
            elif pattern == 'abba':
                generated_lyrics += '\n'.join([a1, b1, b2, a2])
            generated_lyrics += '\n'
            generated_lyrics += '\n'
        generated_lyrics = self.replace_forbidden_words(generated_lyrics)
        return generated_lyrics
    
    def generate_freestyle_verses(self, N_VERSES=8):
        verse_length = 4
        index = random.choice(range(len(self.free_style_sentences)-N_VERSES*verse_length-1))
        verses = self.free_style_sentences[index : index+N_VERSES*verse_length]
        verses = [verses[i : i+verse_length] for i in range(0, len(verses), verse_length)]
        generated_lyrics = ''
        for verse_set in verses:
            generated_lyrics += '\n'.join(verse_set)
            generated_lyrics += '\n'
            generated_lyrics += '\n'
        generated_lyrics = self.replace_forbidden_words(generated_lyrics)
        return generated_lyrics
    
    def replace_forbidden_words(self, generated_text):
        BAD_WORDS = [

            ['hitler','sniffler'],
            ['white', 'knight'],
            ['fuck', 'duck'],
            ['did her', 'bid her'],
            ['bitch', 'quiche'],
            ['nigg', 'pig'],
            [' ho ', 'toe '],
            [' hore ', ' chore '],
            ['ass', 'bass']
        ]
        for bad_word in BAD_WORDS:
            forbidden_word = bad_word[0]
            generated_text = generated_text.replace(forbidden_word.capitalize(), '')
            generated_text = generated_text.replace(forbidden_word, '')
            generated_text = generated_text.replace(forbidden_word.upper(), '')
        return generated_text
