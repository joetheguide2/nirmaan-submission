from collections import defaultdict
from sentence_transformers import SentenceTransformer, util
import language_tool_python
from lexicalrichness import LexicalRichness
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
import json
import sys


def check_flow_order(text, model=None):
    """
    Checks if the text follows the correct flow order:
    Salutation -> Name -> Mandatory -> Optional (if present) -> Closing
    
    Returns:
        bool: True if flow is correct, False otherwise
    """
    if model is None:
        flow_model = SentenceTransformer('all-MiniLM-L6-v2')
    else:
        flow_model = model
    
    # Define comprehensive patterns for each section
    patterns = {
        'salutation': [
            # Basic
            r'\b(hi|hello|hey|greetings)\b',
            r'\bhey there\b',
            r'\bhi there\b',
            r'\bhello there\b',
            r'\bhi all\b',
            r'\bhey all\b',
            r'\bhi team\b',
            r'\bhello team\b',
            r'\bhey team\b',
            r'\bhi everyone\b',
            r'\bhello everyone\b',
            r'\bhey everyone\b',
            # Mid-level
            r'\bgood morning\b',
            r'\bgood afternoon\b',
            r'\bgood evening\b',
            r'\bgood day\b',
            r'\bgood morning everyone\b',
            r'\bgood afternoon everyone\b',
            r'\bgood evening everyone\b',
            r'\ba very good day to you all\b',
            r'\bladies and gentlemen\b',
            r'\bdear team\b',
            r'\bdear all\b',
            r'\bwarm greetings\b',
            # Strong
            r'\bthrilled to\b',
            r'\bpleased to\b',
            r'\bexcited to\b',
            r'\bexcited to introduce myself\b',
            r'\bfeeling great to be here\b',
            r'\bso excited to be here\b',
            r'\bthrilled to introduce myself\b',
            r'\babsolutely delighted to share\b',
            r'\bpleasure to finally introduce myself\b',
            r'\bincredibly excited to present myself\b',
            r'\bfeeling wonderful and excited\b',
            r'\bpleased to share my introduction\b',
            r'\bpleased to introduce myself\b',
            r'\bhonored to share\b',
            r'\bhonored to introduce myself\b',
            r'\bdelighted to share my story\b',
            r'\bdelighted to introduce myself\b',
            r'\bthrilled to share who i am\b',
            r'\bcan\'t wait to tell you\b',
            r'\bbursting with excitement\b',
            r'\bfantastic day to share\b',
            r'\blooking forward to sharing my story\b',
        ],
        'name': [
            r'\bmy name is\b',
            r'\bmyself\b',
            r'\bi am\b',
            r'\bi\'m\b',
            r'\bcalled\b',
            r'\bi go by\b',
            r'\bpeople call me\b',
            r'\byou can call me\b',
            r'\bthey call me\b',
            r'\bmy name\'s\b',
            r'\bi am known as\b',
            r'\bi\'m known as\b',
            r'\bthis is\b',
        ],
        'mandatory': [
            # Age
            r'\byears old\b',
            r'\bage\b',
            r'\bold\b',
            r'\bi am \d+\b',
            r'\bi\'m \d+\b',
            r'\bmy age is\b',
            r'\bi\'m aged\b',
            # School/Class
            r'\bschool\b',
            r'\bof class\b',
            r'\bin grade\b',
            r'\bstudent of\b',
            r'\bstudying in\b',
            r'\bsection\b',
            r'\bfrom school\b',
            r'\bi study in\b',
            r'\bi\'m a student\b',
            r'\bi attend\b',
            r'\bi go to school\b',
            r'\benrolled in\b',
            r'\bclass \d+\b',
            r'\bgrade \d+\b',
            # Family
            r'\bfamily\b',
            r'\bparents\b',
            r'\bmother\b',
            r'\bfather\b',
            r'\bsiblings\b',
            r'\blive with\b',
            r'\bmembers\b',
            r'\bfamily members\b',
            r'\bpeople in my family\b',
            r'\bmy family has\b',
            r'\bthere are \d+ people\b',
            r'\bi live with my family\b',
            r'\bfamily consists of\b',
            r'\bmy mom\b',
            r'\bmy dad\b',
            r'\bmy brother\b',
            r'\bmy sister\b',
            r'\bme, my\b',
        ],
        'optional': [
            # Hobbies/Interests
            r'\bhobbies\b',
            r'\binterests\b',
            r'\blike to\b',
            r'\bfree time\b',
            r'\benjoy\b',
            r'\bplay\b',
            r'\bplaying\b',
            r'\bdoing\b',
            r'\bi love\b',
            r'\bi like\b',
            r'\bi enjoy\b',
            r'\bfavorite activity\b',
            r'\bpassion\b',
            r'\bone thing i enjoy\b',
            r'\bone thing i really enjoy\b',
            # Goals/Dreams
            r'\bgoal\b',
            r'\bdream\b',
            r'\bambition\b',
            r'\bwant to be\b',
            r'\baspire\b',
            r'\bfavorite subject\b',
            r'\bwant\b',
            r'\btry\b',
            r'\bwill\b',
            r'\bhope to\b',
            r'\bi wish\b',
            r'\bmy aim\b',
            r'\bi plan to\b',
            r'\blooking forward to\b',
            r'\bin the future\b',
            r'\bsomeday i will\b',
            r'\bi would like to\b',
            r'\bthrough .* i can\b',
            r'\bexplore\b',
            r'\bmake discoveries\b',
            r'\bimprove the lives\b',
            # Unique facts
            r'\bunique\b',
            r'\bfun fact\b',
            r'\binteresting\b',
            r'\bspecial\b',
            r'\bpeople don\'t know\b',
            r'\bone thing about me\b',
            r'\bspecial thing\b',
            r'\bone thing i\b',
            r'\bsomething interesting\b',
            r'\ba fun fact\b',
            r'\bpeople might not know\b',
            r'\bnot many know\b',
            r'\bsecret\b',
            r'\bone special thing\b',
            # Strengths/Achievements
            r'\bstrength\b',
            r'\bachievement\b',
            r'\bgood at\b',
            r'\bskill\b',
            r'\bimprove\b',
            r'\bi excel at\b',
            r'\bi\'m talented\b',
            r'\bi can\b',
            r'\bi\'m able to\b',
            r'\bmy strength is\b',
            r'\bproud of\b',
            r'\baccomplished\b',
            # Origin
            r'\bfrom\b',
            r'\bborn in\b',
            r'\borigin\b',
            r'\bhometown\b',
            r'\bare from\b',
        ],
        'closing': [
            r'\bthank you\b',
            r'\bthanks\b',
            r'\bthank you for listening\b',
            r'\bthanks for your time\b',
            r'\bappreciate\b',
            r'\bgrateful\b',
            r'\bthat\'s all\b',
            r'\bthat\'s it\b',
            r'\bthat\'s me\b',
            r'\bthat\'s all about me\b',
            r'\bthank you for your attention\b',
            r'\bthanks for hearing me out\b',
            r'\bi appreciate your time\b',
            r'\blooking forward\b',
            r'\bnice meeting you\b',
            r'\bpleasure to share\b',
            r'\bglad to share\b',
            r'\bhappy to share\b',
        ]
    }
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    if len(sentences) < 3:
        return False
    
    # Match sentences to sections using keyword patterns
    sentence_sections = []
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        matched_section = None
        
        # Try to match with patterns
        for section, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, sentence_lower):
                    matched_section = section
                    break
            if matched_section:
                break
        
        if matched_section:
            sentence_sections.append({
                'index': i,
                'section': matched_section,
                'sentence': sentence
            })
    
    if not sentence_sections:
        return False
    
    # Get first occurrence of each section
    found_sections = {}
    for item in sentence_sections:
        section = item['section']
        if section not in found_sections:
            found_sections[section] = item['index']
    
    # Must have all required sections
    required = ['salutation', 'name', 'mandatory', 'closing']
    if not all(s in found_sections for s in required):
        return False
    
    # Check order: salutation < name < mandatory < closing
    if found_sections['salutation'] >= found_sections['name']:
        return False
    
    if found_sections['name'] >= found_sections['mandatory']:
        return False
    
    # Handle optional section if present
    if 'optional' in found_sections:
        # Optional should be after mandatory and before closing
        if found_sections['mandatory'] >= found_sections['optional']:
            return False
        if found_sections['optional'] >= found_sections['closing']:
            return False
    else:
        # No optional, so mandatory must come before closing
        if found_sections['mandatory'] >= found_sections['closing']:
            return False
    
    return True


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

    tool = language_tool_python.LanguageToolPublicAPI('en-US')
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
                "Greetings", "Hi everyone",
            ]

            mid = [
                "Good Morning", "Good Afternoon", "Good Evening", "Good Day",
                "Good morning everyone", "Good afternoon everyone", "Good evening everyone",
                "A very good day to you all", "Ladies and gentlemen, hello",
                "Dear team, hello", "Dear all, hello", "Warm greetings everyone", "Hello everyone", "hi everyone", "hey everyone"
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

        if criteria == 'SpeechRate':
            words = text.split()
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
            elif(0.7 <= err <= 0.899999999999):
                score = 8
            elif(0.5 <= err <= 0.699999999):
                score = 6
            elif (0.3 <= err <= 0.4999999):
                score = 4
            else:
                score = 2

            scores[criteria] = score

        if criteria == "Richness":
            lex = LexicalRichness(text)
            words = text.lower().split()
            mtld_score = lex.mtld()/100
            score = 0
            if(0.9 <= mtld_score <= 1.0):
                score = 10
            elif(0.7 <= mtld_score <= 0.89999999999):
                score = 8
            elif(0.5 <= mtld_score <= 0.6999999999999999):
                score = 6
            elif(0.3 <= mtld_score <= 0.4999999999999999):
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

            if(prob >= 0.999999999999):
                score = 15
            elif(0.7 <= prob <= 0.8999999999999):
                score = 12
            elif(0.5 <= prob <= 0.6999999999999):
                score = 9
            elif(0.3 <= prob <= 0.4999999999999):
                score = 6
            else:
                score = 3

            scores[criteria] = score

        if criteria == 'Flow':
            if(check_flow_order(text)):
                scores[criteria] = 5
            else:
                scores[criteria] = 0
    return scores


def analyze_introduction(text, duration):
    """
    Main function to analyze introduction and return structured results
    """
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

    # Calculate scores using your existing grade function
    scores = grade(text, gradingCriterion, subCriterion, weights)
    
    # Calculate overall score
    overall_score = sum(scores.values())
    
    # Calculate speech rate for additional info
    word_count = len(text.split())
    speech_rate = word_count / (duration / 60) if duration > 0 else 0
    
    # Structure the response for UI
    result = {
        "overallScore": overall_score,
        "totalDuration": duration,
        "wordCount": word_count,
        "speechRate": round(speech_rate, 2),
        "criteriaScores": [
            {
                "category": "Content & Structure",
                "metrics": [
                    {
                        "name": "Salutation Level",
                        "score": scores.get('Salutation', 0),
                        "maxScore": weights['Salutation'],
                        "feedback": f"Salutation effectiveness: {scores.get('Salutation', 0)}/{weights['Salutation']}"
                    },
                    {
                        "name": "Keyword Presence", 
                        "score": scores.get('KeyWord', 0),
                        "maxScore": weights['KeyWord'],
                        "feedback": f"Key information coverage: {scores.get('KeyWord', 0)}/{weights['KeyWord']}"
                    },
                    {
                        "name": "Flow & Structure",
                        "score": scores.get('Flow', 0),
                        "maxScore": weights['Flow'],
                        "feedback": f"Introduction flow: {scores.get('Flow', 0)}/{weights['Flow']}"
                    }
                ]
            },
            {
                "category": "Speech Rate", 
                "metrics": [
                    {
                        "name": "Speech Rate (words/min)",
                        "score": scores.get('SpeechRate', 0),
                        "maxScore": weights['SpeechRate'],
                        "feedback": f"Speech pace: {round(speech_rate, 2)} words/minute"
                    }
                ]
            },
            {
                "category": "Language & Grammar",
                "metrics": [
                    {
                        "name": "Grammar Accuracy",
                        "score": scores.get('Error', 0),
                        "maxScore": weights['Error'],
                        "feedback": f"Grammar and language accuracy"
                    },
                    {
                        "name": "Vocabulary Richness",
                        "score": scores.get('Richness', 0),
                        "maxScore": weights['Richness'],
                        "feedback": f"Vocabulary diversity and richness"
                    }
                ]
            },
            {
                "category": "Clarity",
                "metrics": [
                    {
                        "name": "Filler Word Rate", 
                        "score": scores.get('FillerWordRate', 0),
                        "maxScore": weights['FillerWordRate'],
                        "feedback": f"Clarity and filler word usage"
                    }
                ]
            },
            {
                "category": "Engagement",
                "metrics": [
                    {
                        "name": "Sentiment & Positivity",
                        "score": scores.get('Sentiment', 0),
                        "maxScore": weights['Sentiment'],
                        "feedback": f"Positive tone and engagement"
                    }
                ]
            }
        ]
    }
    
    return result

if __name__ == "__main__":
    # Read input from command line
    try:
        input_data = json.loads(sys.argv[1])
        text = input_data['introduction']
        duration = input_data['duration']
        
        result = analyze_introduction(text, duration)
        print(json.dumps(result))
        
    except Exception as e:
        error_result = {
            "error": str(e),
            "overallScore": 0,
            "criteriaScores": []
        }
        print(json.dumps(error_result))