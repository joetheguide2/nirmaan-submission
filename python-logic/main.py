from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
import torch
import language_tool_python
from mtld import mtld 
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re

def calculate_positive_word_probability(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_scores = analyzer.polarity_scores(text)
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words) if words else 1  
    
    positive_words = []
    for word in words:
        word_score = analyzer.lexicon.get(word, 0)
        if word_score > 0:
            positive_words.append(word)
    
    # Calculate probability
    positive_word_count = len(positive_words)
    positive_word_probability = positive_word_count / total_words
    
    return round(positive_word_probability, 4)

def get_grammar_error_count(text):

    tool = language_tool_python.LanguageTool('en-US')
    matches = tool.check(text)
    error_count = len(matches)
    tool.close()
    return error_count


class KeywordGrader:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Define keyword categories with their weights
        self.keyword_categories = {
            # Must Have (4 points each)
            "name": {"weight": 4, "keywords": ["name", "called", "myself", "I am"]},
            "age": {"weight": 4, "keywords": ["age", "years old", "I am", "old"]},
            "school_class": {"weight": 4, "keywords": ["school", "of class", "in grade", "student of", "studying in", "section"]},
            "family": {"weight": 4, "keywords": ["family", "parents", "mother", "father", "siblings", "live with", "members", "family members"]},
            "hobbies": {"weight": 4, "keywords": ["hobbies", "interests", "like to", "free time", "enjoy", "play", "playing", "doing"]},
            
            # Good to Have (2 points each)
            "goals": {"weight": 2, "keywords": ["goal", "dream", "ambition", "want to be", "aspire", "favorite subject", "want", "try", "will"]},
            "origin": {"weight": 2, "keywords": ["from", "born in", "origin", "hometown", "are from"]},
            "unique_fact": {"weight": 2, "keywords": ["unique", "fun fact", "interesting", "special", "people don't know"]},
            "strengths": {"weight": 2, "keywords": ["strength", "achievement", "good at", "skill", "improve"]}
        }
    
    def semantic_similarity(self, text, keywords, threshold=0.2):
        """Calculate semantic similarity between text and keywords"""
        text_embedding = self.model.encode(text.lower(), convert_to_tensor=True)
        
        max_similarity = 0
        
        for keyword in keywords:
            keyword_embedding = self.model.encode(keyword.lower(), convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(text_embedding, keyword_embedding).item()
            
            if similarity > max_similarity:
                max_similarity = similarity
        
        return max_similarity >= threshold, max_similarity
    
    def calculate_keyword_score(self, text):
        """Calculate total keyword score based on semantic matching"""
        total_score = 0
        matches_found = []
        
        for category, details in self.keyword_categories.items():
            is_match, similarity_score = self.semantic_similarity(
                text, details["keywords"]
            )
            
            if is_match:
                total_score += details["weight"]
                matches_found.append({
                    "category": category,
                    "similarity": round(similarity_score, 3),
                    "points": details["weight"]
                })
        
        return total_score, matches_found

# Initialize the keyword grader
keyword_grader = KeywordGrader()



def grade(text, gradingCriterion, subCriterion, weights):
    scores = defaultdict(int)

    for criteria in weights.keys():
        max_score = weights[criteria]
        score = 0

        if criteria == 'Salutation':
            basic = [
                "Hi", "Hello", "Hey", "Hey there", "Hi there", "Hello there", 
                "Hi all", "Hey all", "Hi team", "Hello team", "Hey team", 
                "Greetings", "Hi everyone", "Hey everyone", "Hello everyone",
            ]

            mid = [
                "Good Morning", "Good Afternoon", "Good Evening", "Good Day",
                "Good morning everyone", "Good afternoon everyone", "Good evening everyone",
                "A very good day to you all", "Ladies and gentlemen, hello",
                "Dear team, hello", "Dear all, hello", "Warm greetings everyone"
            ]
            
            strong = [
                "thrilled to", 'Pleased to', "Excited to", "I am excited to introduce myself",
                "Feeling great to be here", "I'm so excited to be here today", "I'm thrilled to introduce myself",
                "I'm absolutely delighted to share", "It's a pleasure to finally introduce myself",
                "I'm incredibly excited to present myself", "Feeling wonderful and excited to introduce myself",
                "Pleased to share my introduction", "Pleased to introduce myself", "Honored to share a bit about myself",
                "Honored to introduce myself", "Delighted to share my story", "Delighted to introduce myself",
                "Thrilled to share who I am", "Thrilled to introduce myself", "Good morning! I'm thrilled to introduce myself...",
                "Hello everyone! I'm so excited to share my background...", "Hi team! Pleased to finally introduce myself...",
                "Hey there! Feeling great and ready to tell you about myself...", "Greetings! I am absolutely delighted to present myself...",
                "Good afternoon! I'm incredibly honored to introduce myself...", "Hello! I can't wait to tell you about myself...",
                "Hi all! I'm bursting with excitement to introduce myself...", "Hey everyone! What a fantastic day to share my introduction...",
                "I'm so excited to finally introduce myself to all of you", "It's an absolute pleasure to have this chance to introduce myself",
                "I'm really looking forward to sharing my story with you all"
            ]
            
            for txt in basic:
                if txt.lower() in text.lower():
                    score = 2
                    break

            for txt in mid:
                if txt.lower() in text.lower():
                    score = 4
                    break
                    
            for txt in strong:
                if txt.lower() in text.lower():
                    score = 5
                    break

            scores[criteria] = score
        
        if criteria == 'KeyWord':
            # Use semantic checker for keyword matching
            keyword_score, matches = keyword_grader.calculate_keyword_score(text)
            scores[criteria] = min(keyword_score, weights[criteria])  # Cap at max weight
            print(f"Keyword Matches Found: {matches}")

        if criteria == 'SpeechRate':
            words = text.split()
            print(words)
            rate = len(words)/(duration/60)
            score = 0
            if(111 <= rate <= 140):
                score = 10
            elif(141 <= rate <= 160):
                score = 6
            elif(81 <= rate <= 110):
                score = 6
            else:
                score = 2

            scores[criteria] = score

        if criteria == 'Error':
            count = get_grammar_error_count(text)
            words = len(text.split())
            err = 1 - min((count/words)*10, 1)
            score = 0
            if(err >= 0.9):
                score = 10
            elif(0.7 <= err <= 0.89):
                score = 8
            elif(0.5 <= err <= 0.69):
                score = 6
            elif (0.3 <= err <= 0.49):
                score = 4
            else:
                score = 2

            scores[criteria] = score

        if criteria == "Richness":

            words = text.lower().split()
            mtld_score = mtld(words)/100
            score = 0
            if(0.9 <= mtld_score <= 1.0):
                score = 10
            elif(0.7 <= mtld_score <= 0.89):
                score = 8
            elif(0.5 <= mtld_score <= 0.69):
                score = 6
            elif(0.3 <= mtld_score <= 0.49):
                score = 4
            else:
                score = 2

            scores[criteria] = score

        if criteria == 'FillerWordRate':
            s = ["um", "uh", "like", "you know", "so", "actually", "basically", "right", "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah"]
            filler_count = 0
            for word in s:
                if word.lower() in text.lower():
                    filler_count += 1

            fwr = filler_count/len(text.split())*100
            score = 0
            if(0 <= fwr <= 3):
                score = 15
            elif(4 <= fwr <= 6):
                score = 12
            elif(7 <= fwr <= 9):
                score = 9
            elif(10 <= fwr <= 12):
                score = 6
            else:
                score = 3

            scores[criteria] = score

        if criteria == 'Sentiment':
            prob = calculate_positive_word_probability(text)

            if(prob >= 0.9):
                score = 15
            elif(0.7 <= prob <= 0.89):
                score = 12
            elif(0.5 <= prob <= 0.69):
                score = 9
            elif(0.3 <= prob <= 0.49):
                score = 6
            else:
                score = 3
    return scores

# Test the code
intro_text = """Hello everyone, myself Muskan, studying in class 8th B section from Christ Public School. 
I am 13 years old. I live with my family. There are 3 people in my family, me, my mother and my father.
One special thing about my family is that they are very kind hearted to everyone and soft spoken. One thing I really enjoy is play, playing cricket and taking wickets.
A fun fact about me is that I see in mirror and talk by myself. One thing people don't know about me is that I once stole a toy from one of my cousin.
 My favorite subject is science because it is very interesting. Through science I can explore the whole world and make the discoveries and improve the lives of others. 
Thank you for listening."""

duration = 52.0

gradingCriterion = [
    "ContentAndStucture",
    "SpeechRate",
    "LanguageAndGrammar",
    "Clarity",
    "Engagement"
]

subCriterion = {
    "ContentAndStucture": ['Salutation', 'KeyWord', 'Flow'],
    "SpeechRate": ['SpeechRate'],
    "LanguageAndGrammar": ['Error', 'Richness'],
    "Clarity": ['FillerWordRate'],
    "Engagement": ['Sentiment']
}

weights = {
    'Salutation': 5, 
    'KeyWord': 30, 
    'Flow': 5,
    'SpeechRate': 10,
    'Error': 10,
    'Richness': 10,
    'FillerWordRate': 15,
    'Sentiment': 15
}

scores = grade(intro_text, gradingCriterion=gradingCriterion, subCriterion=subCriterion, weights=weights)
print("\nFinal Scores:", dict(scores))