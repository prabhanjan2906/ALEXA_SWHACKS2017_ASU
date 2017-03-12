import logging
import numpy as np

from random import randint

from flask import Flask, render_template

from flask_ask import Ask, statement, question, session

app = Flask(__name__)

ask = Ask(app, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

@ask.launch

def new_game():
    welcome_msg = render_template('welcome')
    return question(welcome_msg)


@ask.intent("IntroIntent" , mapping={'name': 'Name'})

def next_round(name):
	session.attributes['namep'] = name
	session.attributes['callFirst']=0
	session.attributes['wordP']=''
	session.attributes['type']='simple'
	session.attributes['difficult word']=[]
	session.attributes['attempt']=1
	session.attributes['slp']=1
	session.attributes['mlp']=1
	session.attributes['clp']=1
	session.attributes['rlp']=1
	session.attributes['dlp']=1
	return question('How many words do you want him or her to learn today ?')
	
@ask.intent("NumberOfWordIntent" , mapping={'noofwords': 'NoofWords'})

def number_word(noofwords):
	session.attributes['wordsnumber'] = noofwords
	return question('Hi '+ session.attributes['namep']+' , how are you ' )

@ask.intent("SpeechLearnIntent" , mapping={'word': 'Word'})

def speech_round(word):
	if word == 'cancel':
		return statement('Hey,nice talking to you'+session.attributes['namep']+', will talk again soon')
	simple_words =['cat','mat','bat','rat','pat','sky','ant','eat','dad','dry','try','my','spy','cry','dog','boy','girl']
	medium_words =['madam','daddy','mummy','shop','drop','crop','laugh','hello','smile','help','famous','slow','fast','health','happy','smile']
	complex_words =['forest','ocean','earth','moon','hundred','thousand','million','molten','fairy','mother','father','tortoise','rabbits','Lion','Elephant','bird']
	
	from urllib.request import Request, urlopen, URLError
	request = Request('http://randomword.setgetgo.com/get.php')
	response = urlopen(request)
	random_word = response.read().decode('UTF-8');
	
	if int(session.attributes['callFirst']) < int(session.attributes['wordsnumber']):
		if session.attributes['callFirst'] == 0:
			session.attributes['callFirst']= session.attributes['callFirst']+1
			session.attributes['type'] = 'simple'
			session.attributes['wordP'] = simple_words[np.random.randint(len(simple_words), size=1)[0]]
			return question("Hey " + session.attributes['namep'] + " say "+ session.attributes['wordP'])
			
		if word == session.attributes['wordP']:
			session.attributes['callFirst']= session.attributes['callFirst']+1
			if session.attributes['callFirst']==1:
				session.attributes['type'] = 'medium'
				session.attributes['wordP'] = medium_words[np.random.randint(len(medium_words), size=1)[0]]
				return question("Hey 1" + session.attributes['namep'] + " say "+ session.attributes['wordP'])			

			if session.attributes['type'] == 'simple':
				session.attributes['slp'] =((1/session.attributes['attempt'])+ session.attributes['slp'])/2						
			if session.attributes['type'] == 'medium':
				session.attributes['mlp'] =((1/session.attributes['attempt'])+ session.attributes['mlp'])/2						
			if session.attributes['type'] == 'complex':
				session.attributes['clp'] =((1/session.attributes['attempt'])+ session.attributes['clp'])/2						
			if session.attributes['type'] == 'random':
				session.attributes['rlp'] =((1/session.attributes['attempt'])+ session.attributes['rlp'])/2						
			if session.attributes['type'] == 'diffcult':
				session.attributes['dlp'] =((1/session.attributes['attempt'])+ session.attributes['dlp'])/2						
			if session.attributes['attempt'] > 4:
				session.attributes['difficult word'].append(session.attributes['wordP'])								
			session.attributes['attempt'] = 1
				
			if(session.attributes['slp'] < 0.75 or session.attributes['callFirst'] % 5 ==1):
				session.attributes['type'] = 'simple'
				session.attributes['wordP'] = simple_words[np.random.randint(len(simple_words), size=1)[0]]
				return question("Hey " + session.attributes['namep'] + " say "+ session.attributes['wordP'])
				
			if(session.attributes['mlp'] < 0.5 or session.attributes['callFirst'] % 5 ==2):
				session.attributes['type'] = 'medium'
				session.attributes['wordP'] = medium_words[np.random.randint(len(medium_words), size=1)[0]]
				return question("Hey " + session.attributes['namep'] + " say "+ session.attributes['wordP'])
					
			if(session.attributes['clp'] < 0.25 or session.attributes['callFirst'] % 5 ==3):
				session.attributes['type'] = 'complex'
				session.attributes['wordP'] = complex_words[np.random.randint(len(complex_words), size=1)[0]]
				return question("Hey " + session.attributes['namep'] + " say "+ session.attributes['wordP'])
					
			if (len(session.attributes['difficult word']) != 0):
				if (session.attributes['dlp'] < 0.5 or session.attributes['callFirst'] % 5 ==5):
					session.attributes['type'] = 'diffcult'
					session.attributes['wordP'] = session.attributes['difficult word'][np.random.randint(len(session.attributes['difficult word']), size=1)[0]]
					return question("Hey " + session.attributes['namep'] + " say "+ session.attributes['wordP'])
					
			session.attributes['type'] = 'random'
			return question(session.attributes['namep'] + " say "+ random_word)													
		else:
			session.attributes['attempt'] = session.attributes['attempt'] +1;
			return question(session.attributes['namep'] + " repeat " +session.attributes['wordP'])					
		session.attributes['callFirst'] = session.attributes['callFirst']+1;
	return statement('Hey,nice talking to you'+session.attributes['namep']+', will talk again soon')

if __name__ == '__main__':

    app.run(debug=True)