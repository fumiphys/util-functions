/*
 * parse text file with Mecab
 */

#include <fstream>
#include <iostream>
#include <map>
#include <mecab.h>
#include <random>
#include <regex>
#include <string>
#include <vector>
#define __BEGIN__ "__BEGIN__"
#define __END__ "__END__"
using namespace std;


// main
int main(int argc, char const* argv[])
{
	ifstream fin("tweets.csv");
	if(fin.fail()){
			cerr << "failed to load tweet data" << endl;
			return 1;
	}
	ofstream fout("tweet_extracted.txt");
	int text_row = 5;

	// list of words in tweet
	vector<vector<string> > wordlist;
	string str;

	// MeCab
	MeCab::Tagger *tagger = MeCab::createTagger("-Owakati");

	getline(fin, str);
	while(getline(fin, str)){
			if(str[0] != '"')continue;
			if(str.find("RT") != string::npos || str.find("@") != string::npos){
					continue;
			}
			if(str.size() < 10)continue;
			regex sep (",");
			auto itr = sregex_token_iterator(str.begin(), str.end(), sep, -1);
			auto end = sregex_token_iterator();
			string thistext;
			int count = 0;
			while(itr != end){
					if(count == text_row){
							thistext = *itr;
					}
					count++;
					itr++;
			}
			thistext = thistext.substr(1, thistext.size() - 2);
			if(thistext.find("http") != string::npos)continue;
			fout << thistext << endl;
			const char *restext = tagger->parse(thistext.c_str());

			string parsed_text = string(restext);

			// vector for this line
			vector<string> thisline;
			regex sep_parsed (" ");
			auto itr_parsed = sregex_token_iterator(parsed_text.begin(), parsed_text.end(), sep_parsed, -1);
			auto end_parsed = sregex_token_iterator();
			while(itr_parsed != end_parsed){
					thisline.push_back(*itr_parsed++);
			}
			wordlist.push_back(thisline);
	}

	fout.close();

	map<pair<string, string>, vector<string> > mp;
	vector<string> initial;
	for(int i = 0; i < wordlist.size(); i++){
			if(wordlist[i].size() < 2)continue;
			mp[pair<string, string>(__BEGIN__, wordlist[i][0])].push_back(wordlist[i][1]);
			initial.push_back(wordlist[i][0]);
			for(int j = 0; j < wordlist[i].size() - 2; j++){
					mp[pair<string, string>(wordlist[i][j], wordlist[i][j+1])].push_back(wordlist[i][j+2]);
			}
			mp[pair<string, string>(wordlist[i][wordlist[i].size()-2], wordlist[i][wordlist[i].size()-1])].push_back(__END__);
	}
	
	random_device rnd;
	mt19937 mt(rnd());
	uniform_int_distribution<> rand100(0, initial.size() - 1);
	int n = 10000;
	int current = rand100(mt);
	string first = __BEGIN__;
	string second = initial[current];
	for(int i = 0; i < n; i++){
			if(second == __END__){
					cout << endl;
					first = __BEGIN__;
					second = initial[rand100(mt)];
					continue;
			}
			cout << second;
			if(mp.find(pair<string, string>(first, second)) == mp.end()){
					cout << endl;
					first = __BEGIN__;
					second = initial[rand100(mt)];
					continue;
			}
			uniform_int_distribution<> randc(0, mp[pair<string, string>(first, second)].size() - 1);
			string tmp = second;
			second = mp[pair<string, string>(first, second)][randc(mt)];
			first = tmp;
	}
	cout << endl;

	return 0;
}
