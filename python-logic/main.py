from collections import defaultdict


intro_text = """Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. 
I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father.
One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets.
A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin.
 My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. 
Thank you for listening."""

gradingCriterion = [
    "ContentAndStucture",
    "SpeechRate",
    "LanguageAndGrammar",
    "Clarity",
    "Engagement"
]

subCriterion = {

    "ContentAndStucture" : ['Salutation', 'KeyWord', 'Flow'],
    "SpeechRate" : ['SpeechRate'],
    "LanguageAndGrammar" : ['Error', 'Richness'],
    "Clarity" : ['FillerWordRate'],
    "Engagement" : ['Sentiment']

}

weights = {
    'Salutation' : 5, 
    'KeyWord' : 30, 
    'Flow' : 5,
    'SpeechRate' : 10,
    'Error' : 10,
    'Richness' : 10,
    'FillerWordRate' : 15,
    'Sentiment' : 15

}

scores = defaultdict(int)

def grade(text, gradingCriterion, subCriterion, weights):
    scores = defaultdict(int)

    for criteria in weights.keys():

        max_score = weights[criteria]
        score = 0

        if(criteria == 'Salutation'):
            basic = [
                "Hi",
                "Hello",
                "Hey",
                "Hey there",
                "Hi there",
                "Hello there",
                "Hi all",
                "Hey all",
                "Hi team",
                "Hello team",
                "Hey team",
                "Greetings",
                "Hi everyone",
                "Hey everyone"
            ]

            mid = [
                "Good Morning",
                "Good Afternoon", 
                "Good Evening",
                "Good Day",
                "Hello everyone",
                "Good morning everyone",
                "Good afternoon everyone",
                "Good evening everyone",
                "A very good day to you all",
                "Ladies and gentlemen, hello",
                "Dear team, hello",
                "Dear all, hello",
                "To all attendees, hello",
                "Salutations everyone",
                "Warm greetings everyone"
            ]
            strong = [
                "thrilled to",
                'Pleased to',
                "Excited to"
                "I am excited to introduce myself",
                "Feeling great to be here",
                "I'm so excited to be here today",
                "I'm thrilled to introduce myself",
                "I'm absolutely delighted to share",
                "It's a pleasure to finally introduce myself",
                "I'm incredibly excited to present myself",
                "Feeling wonderful and excited to introduce myself",
                "Pleased to share my introduction",
                "Pleased to introduce myself",
                "Honored to share a bit about myself",
                "Honored to introduce myself",
                "Delighted to share my story",
                "Delighted to introduce myself",
                "Thrilled to share who I am",
                "Thrilled to introduce myself",
                "Good morning! I'm thrilled to introduce myself...",
                "Hello everyone! I'm so excited to share my background...",
                "Hi team! Pleased to finally introduce myself...",
                "Hey there! Feeling great and ready to tell you about myself...",
                "Greetings! I am absolutely delighted to present myself...",
                "Good afternoon! I'm incredibly honored to introduce myself...",
                "Hello! I can't wait to tell you about myself...",
                "Hi all! I'm bursting with excitement to introduce myself...",
                "Hey everyone! What a fantastic day to share my introduction...",
                "I'm so excited to finally introduce myself to all of you",
                "It's an absolute pleasure to have this chance to introduce myself",
                "I'm really looking forward to sharing my story with you all"
            ]
            for txt in basic:
                if(txt.lower in text.lower):
                    score = 2
                    break

            for txt in mid:
                if(txt.lower in text.lower):
                    score = 4
                    break
            for txt in strong:
                if(txt.lower in text.lower):
                    score = 5
                    break

            scores[criteria] = score
        
        if(criteria == ''):
            pass
            
