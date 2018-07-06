# -*- coding: utf-8 -*-
'''
Create simplest search engine!
'''

import argparse
import codecs
import datetime
import glob
import MeCab
import pymongo
import re


class MeCabSearch():
    '''
    class for search engine
    variables are almost all instance variable
    '''
    def __init__(self, path_list, ext_list):
        '''
        constructor
        arguments:
            path_list: list of search path
            ext_list: list of filetype
        '''
        self.path_list = []
        for filepath in path_list:
            if not filepath[-1] == '/':
                filepath += "/"
            self.path_list.append(filepath)
        self.ext_list = ext_list
        self.data_dict = {}  # {filename: [[word, position]]}
        self.score_list = {}
        client = pymongo.MongoClient("localhost", 27017)
        self.db = client.mecab_search

    def find_all_file(self):
        '''
        find all files from `path_list` whose extensions are in ext_list
        '''
        self.all_file = []
        for filepath in self.path_list:
            thisfilelist = glob.glob(filepath + "*")
            self.all_file.extend(
                [filename for filename in thisfilelist
                 if filename.split(".")[-1] in self.ext_list])

    def create_data_for_file(self, filename):
        '''
        insert data to mongo and return dict
        arguments
            filename: file name
        '''
        file_dict = {}
        not_alphaornum = re.compile(r"[^a-zA-Z0-9]")
        mecabtagger = MeCab.Tagger()
        collection = self.db["data_list"]
        if collection.find_one({"filename": filename}) is not None:
            collection.remove({"filename": filename})
        # file is assumed to have encoding utf-8
        count = 0  # line count
        with codecs.open(filename, "r", "utf-8") as reader:
            for line in reader:
                blocks = line.strip().split(" ")
                for block in blocks:
                    if len(re.findall(not_alphaornum, block)) == 0:
                        if block not in file_dict.keys():
                            file_dict[block] = []
                        file_dict[block].append(count)
                        count = count + 1
                    else:
                        # only noun
                        word_list = mecabtagger.parse(block).split("\n")
                        for wordline in word_list:
                            word = wordline.split("\t")
                            if len(word) < 2:
                                continue
                            wordinfo = \
                                word[1].split(",")[0]
                            if wordinfo == "名詞":
                                if word[0] not in \
                                        file_dict.keys():
                                    file_dict[word[0]] = []
                                file_dict[word[0]]\
                                    .append(count)
                            count = count + 1
        for w, plist in file_dict.items():
            collection.save({"filename": filename,
                             "word": w,
                             "wordcount": plist,
                             "updatedtime": "{0:%Y/%m/%d}"
                             .format(datetime.datetime.now())})

    def create_data_by_mecab(self):
        '''
        create data for ranking by mecab
        '''
        for filename in self.all_file:
            self.create_data_for_file(filename)

    def get_filelist_from_words(self, words):
        '''
        get list of files including word in words
        arguments
            words: list of words
        '''
        self.current_list = []
        for word in words:
            for filename in self.all_file:
                if word in self.data_dict[filename].keys():
                    if filename not in self.current_list:
                        self.current_list.append(filename)

    def count_score(self, words, filename):
        '''
        calcurate score by count of word appearing in file
        arguments
            words: list of words
            filename: filename
        '''
        return sum([len(self.data_dict[filename][word]) for word in words
                    if word in self.data_dict[filename].keys()]) / \
            sum([len(w) for w in self.data_dict[filename].values()])

    def near_score(self, words, filename, default_value=0):
        '''
        calcurate score by the distance of search words
        arguments
            words: list of words
            filename: filename
            default_value: score when word is not included in text
        '''
        score = 0
        for i in range(len(words)):
            if words[i] not in self.data_dict[filename].keys():
                score += default_value * (len(words) - i)
                continue
            for j in range(i+1, len(words)):
                if words[j] not in self.data_dict[filename].keys():
                    score += default_value
                else:
                    for wi in self.data_dict[filename][words[i]]:
                        for wj in self.data_dict[filename][words[j]]:
                            score += 1.0 / ((wi - wj) * (wi - wj) + 1)
        return score

    def score_func(self, words, filename):
        '''
        control score
        '''
        # return self.count_score(words, filename)
        # return self.near_score(words, filename)
        return self.count_score(words, filename) + \
            0.02 * self.near_score(words, filename)

    def add_rank_to_filelist(self, filelist, words):
        '''
        add score to filelist matching search word
        arguments
            filelist: list of files
            words: list of words
        score_func:
            function for scoring, arguments should be (words, filename)
        '''
        self.score_list = {}
        for filename in filelist:
            self.score_list[filename] = self.score_func(words, filename)
        self.score_list = sorted(self.score_list.items(),
                                 key=lambda x: x[1],
                                 reverse=True)
        return self.score_list

    def get_data_list_from_mongo(self):
        '''
        get data of current_list from mongo db
        '''
        self.data_dict = {}  # {filename: {word, [position]}}
        for filename in self.all_file:
            self.data_dict[filename] = self.get_data_from_mongo(filename)

    def get_data_from_mongo(self, filename):
        '''
        get data for file
        arguments
            filename: file name
        '''
        data_dict = {}
        collection = self.db["data_list"]
        if collection.find_one({"filename": filename}) is None:
            self.create_data_for_file(filename)
        for data in collection.find({"filename": filename}):
            data_dict[data["word"]] = data["wordcount"]
        return data_dict

    def search_by_words(self, words):
        '''
        search file and score them
        arguments
            words: list of words
        '''
        self.find_all_file()
        # self.create_data_by_mecab()
        self.get_data_list_from_mongo()
        self.get_filelist_from_words(words)
        ranked = self.add_rank_to_filelist(self.current_list, words)
        return ranked


if __name__ == '__main__':
    '''
    arguments:
        --dirpath: paths of directory
        --words  : search words
        --exts   : extensions
    all arguments are represented by str, separated by ","
    like "a,b,c"
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument("--dirpath", help="path of directory")
    parser.add_argument("--words", help="search words")
    parser.add_argument("--exts", help="extensions")
    args = parser.parse_args()

    path_list = re.sub(" ", "", args.dirpath).strip().split(",")
    words_list = re.sub(" ", "", args.words).strip().split(",")
    ext_list = re.sub(" ", "", args.exts).strip().split(",")

    mecabsearch = MeCabSearch(path_list, ext_list)
    search_results = mecabsearch.search_by_words(words_list)
    if search_results and len(search_results) > 0:
        for filelist in search_results:
            print(filelist[0] + " " + str(filelist[1]))
