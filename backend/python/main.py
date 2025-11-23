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
        dict: Contains flow status and detailed information
    """
    if model is None:
        flow_model = SentenceTransformer('all-MiniLM-L6-v2')
    else:
        flow_model = model
    
    # Define comprehensive patterns for each section
    patterns = {
        'salutation': [
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
            r'\bgood morning\b',
            r'\bgood afternoon\b',
            r'\bgood evening\b',
            r'\bgood day\b',
            r'\bthrilled to\b',
            r'\bpleased to\b',
            r'\bexcited to\b',
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
        ],
        'mandatory': [
            r'\byears old\b',
            r'\bage\b',
            r'\bold\b',
            r'\bschool\b',
            r'\bof class\b',
            r'\bin grade\b',
            r'\bfamily\b',
            r'\bparents\b',
            r'\bmother\b',
            r'\bfather\b',
            r'\bsiblings\b',
        ],
        'optional': [
            r'\bhobbies\b',
            r'\binterests\b',
            r'\blike to\b',
            r'\benjoy\b',
            r'\bgoal\b',
            r'\bdream\b',
            r'\bambition\b',
        ],
        'closing': [
            r'\bthank you\b',
            r'\bthanks\b',
            r'\bthat\'s all\b',
            r'\bthat\'s it\b',
            r'\bthat\'s me\b',
        ]
    }
    
    # Split into sentences
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 5]
    
    if len(sentences) < 3:
        return {
            'is_correct': False,
            'found_sections': [],
            'missing_sections': ['salutation', 'name', 'mandatory', 'closing'],
            'issue': 'Introduction too short (less than 3 sentences)'
        }
    
    # Match sentences to sections
    sentence_sections = []
    
    for i, sentence in enumerate(sentences):
        sentence_lower = sentence.lower()
        matched_section = None
        
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
        return {
            'is_correct': False,
            'found_sections': [],
            'missing_sections': ['salutation', 'name', 'mandatory', 'closing'],
            'issue': 'No recognizable sections found'
        }
    
    # Get first occurrence of each section
    found_sections = {}
    for item in sentence_sections:
        section = item['section']
        if section not in found_sections:
            found_sections[section] = item['index']
    
    # Check for required sections
    required = ['salutation', 'name', 'mandatory', 'closing']
    missing = [s for s in required if s not in found_sections]
    
    if missing:
        return {
            'is_correct': False,
            'found_sections': list(found_sections.keys()),
            'missing_sections': missing,
            'issue': f'Missing required sections: {", ".join(missing)}'
        }
    
    # Check order
    order_issues = []
    if found_sections['salutation'] >= found_sections['name']:
        order_issues.append('Salutation should come before name')
    
    if found_sections['name'] >= found_sections['mandatory']:
        order_issues.append('Name should come before mandatory information')
    
    if 'optional' in found_sections:
        if found_sections['mandatory'] >= found_sections['optional']:
            order_issues.append('Mandatory info should come before optional details')
        if found_sections['optional'] >= found_sections['closing']:
            order_issues.append('Optional details should come before closing')
    else:
        if found_sections['mandatory'] >= found_sections['closing']:
            order_issues.append('Mandatory info should come before closing')
    
    if order_issues:
        return {
            'is_correct': False,
            'found_sections': list(found_sections.keys()),
            'missing_sections': [],
            'issue': '; '.join(order_issues)
        }
    
    return {
        'is_correct': True,
        'found_sections': list(found_sections.keys()),
        'missing_sections': [],
        'issue': None
    }


def calculate_positive_word_probability(text):
    analyzer = SentimentIntensityAnalyzer()
    words = re.findall(r'\b\w+\b', text.lower())
    total_words = len(words) if words else 1  
    
    positive_words = []
    for word in words:
        word_score = analyzer.lexicon.get(word, 0)
        if word_score > 0:
            positive_words.append(word)
    
    positive_word_count = len(positive_words)
    positive_word_probability = positive_word_count / total_words
    
    return round(positive_word_probability, 4), positive_words


def get_grammar_error_count(text):
    try:
        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(text)
        error_details = []
        
        for match in matches[:5]:  # Limit to first 5 errors for brevity
            error_details.append({
                'message': match.message,
                'context': match.context,
                'suggestions': match.replacements[:3] if match.replacements else []
            })
        
        error_count = len(matches)
        tool.close()
        return error_count, error_details
    except Exception as e:
        print(f"Grammar check error: {e}", file=sys.stderr)
        return 0, []


class KeywordGrader:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        self.keyword_categories = {
            "name": {"weight": 4, "keywords": ["name", "called", "myself", "I am"]},
            "age": {"weight": 4, "keywords": ["age", "years old", "I am", "old"]},
            "school_class": {"weight": 4, "keywords": ["school", "of class", "in grade", "student of", "studying in", "section"]},
            "family": {"weight": 4, "keywords": ["family", "parents", "mother", "father", "siblings", "live with", "members", "family members"]},
            "hobbies": {"weight": 4, "keywords": ["hobbies", "interests", "like to", "free time", "enjoy", "play", "playing", "doing"]},
            "goals": {"weight": 2, "keywords": ["goal", "dream", "ambition", "want to be", "aspire", "favorite subject", "want", "try", "will"]},
            "origin": {"weight": 2, "keywords": ["from", "born in", "origin", "hometown", "are from"]},
            "unique_fact": {"weight": 2, "keywords": ["unique", "fun fact", "interesting", "special", "people don't know"]},
            "strengths": {"weight": 2, "keywords": ["strength", "achievement", "good at", "skill", "improve"]}
        }
    
    def semantic_similarity(self, text, keywords, threshold=0.2):
        text_embedding = self.model.encode(text.lower(), convert_to_tensor=True)
        
        max_similarity = 0
        best_keyword = None
        
        for keyword in keywords:
            keyword_embedding = self.model.encode(keyword.lower(), convert_to_tensor=True)
            similarity = util.pytorch_cos_sim(text_embedding, keyword_embedding).item()
            
            if similarity > max_similarity:
                max_similarity = similarity
                best_keyword = keyword
        
        return max_similarity >= threshold, max_similarity, best_keyword
    
    def calculate_keyword_score(self, text):
        total_score = 0
        matches_found = []
        missing_categories = []
        
        for category, details in self.keyword_categories.items():
            is_match, similarity_score, best_keyword = self.semantic_similarity(
                text, details["keywords"]
            )
            
            if is_match:
                total_score += details["weight"]
                matches_found.append({
                    "category": category,
                    "similarity": round(similarity_score, 3),
                    "points": details["weight"],
                    "matched_keyword": best_keyword
                })
            else:
                missing_categories.append({
                    "category": category,
                    "points": details["weight"],
                    "suggestion": f"Consider adding information about {category.replace('_', ' ')}"
                })
        
        return total_score, matches_found, missing_categories


keyword_grader = KeywordGrader()

def grade(text, gradingCriterion, subCriterion, weights, duration):
    scores = defaultdict(int)
    detailed_feedback = {}

    for criteria in weights.keys():
        max_score = weights[criteria]
        score = 0
        feedback = {}

        if criteria == 'Salutation':
            basic = ["Hi", "Hello", "Hey", "Hey there", "Hi there", "Hello there", 
                    "Hi all", "Hey all", "Hi team", "Hello team", "Hey team", 
                    "Greetings", "Hi everyone"]
            mid = ["Good Morning", "Good Afternoon", "Good Evening", "Good Day",
                  "Good morning everyone", "Good afternoon everyone", "Good evening everyone",
                  "A very good day to you all", "Ladies and gentlemen, hello",
                  "Dear team, hello", "Dear all, hello", "Warm greetings everyone", 
                  "Hello everyone", "hi everyone", "hey everyone"]
            strong = ["thrilled to", 'Pleased to', "Excited to", "I am excited to introduce myself",
                     "Feeling great to be here", "I'm so excited to be here today"]
            
            found_salutation = None
            salutation_level = "None"
            
            for txt in basic:
                if txt.lower() in text.lower():
                    score = 2
                    found_salutation = txt
                    salutation_level = "Basic"
                    break

            for txt in mid:
                if txt.lower() in text.lower():
                    score = 4
                    found_salutation = txt
                    salutation_level = "Mid-level"
                    break
                    
            for txt in strong:
                if txt.lower() in text.lower():
                    score = 5
                    found_salutation = txt
                    salutation_level = "Strong"
                    break

            scores[criteria] = score
            feedback = {
                'found': found_salutation,
                'level': salutation_level,
                'suggestion': 'Try using more enthusiastic greetings like "I\'m thrilled to introduce myself"' if score < 4 else 'Excellent greeting!'
            }
        
        elif criteria == 'KeyWord':
            keyword_score, matches, missing = keyword_grader.calculate_keyword_score(text)
            scores[criteria] = min(keyword_score, weights[criteria])
            feedback = {
                'matched_categories': matches,
                'missing_categories': missing,
                'coverage': f"{len(matches)}/{len(keyword_grader.keyword_categories)} categories covered"
            }

        elif criteria == 'SpeechRate':
            words = text.split()
            rate = len(words)/(duration/60)
            
            if 111 <= rate <= 140:
                score = 10
                rating = "Optimal"
                suggestion = "Perfect speech rate!"
            elif 141 <= rate <= 160:
                score = 6
                rating = "Slightly fast"
                suggestion = "Consider slowing down slightly for better clarity"
            elif 81 <= rate <= 110:
                score = 6
                rating = "Slightly slow"
                suggestion = "Try speaking a bit faster to maintain engagement"
            else:
                score = 2
                rating = "Too fast" if rate > 160 else "Too slow"
                suggestion = "Adjust your speech pace significantly (aim for 110-140 wpm)"

            scores[criteria] = score
            feedback = {
                'rate': round(rate, 2),
                'rating': rating,
                'optimal_range': '111-140 wpm',
                'suggestion': suggestion
            }

        elif criteria == 'Error':
            count, error_details = get_grammar_error_count(text)
            words = len(text.split())
            err = 1 - min((count/words)*10, 1)
            
            if err >= 0.9:
                score = 10
                rating = "Excellent"
            elif 0.7 <= err <= 0.899999999999:
                score = 8
                rating = "Very Good"
            elif 0.5 <= err <= 0.699999999:
                score = 6
                rating = "Good"
            elif 0.3 <= err <= 0.4999999:
                score = 4
                rating = "Fair"
            else:
                score = 2
                rating = "Needs Improvement"

            scores[criteria] = score
            feedback = {
                'error_count': count,
                'error_rate': round((count/words)*100, 2),
                'rating': rating,
                'sample_errors': error_details,
                'suggestion': f'Found {count} grammatical issues' if count > 0 else 'No grammatical errors detected!'
            }

        elif criteria == "Richness":
            lex = LexicalRichness(text)
            mtld_score = lex.mtld()/100
            
            if 0.9 <= mtld_score <= 1.0:
                score = 10
                rating = "Excellent"
            elif 0.7 <= mtld_score <= 0.89999999999:
                score = 8
                rating = "Very Good"
            elif 0.5 <= mtld_score <= 0.6999999999999999:
                score = 6
                rating = "Good"
            elif 0.3 <= mtld_score <= 0.4999999999999999:
                score = 4
                rating = "Fair"
            else:
                score = 2
                rating = "Needs Improvement"

            scores[criteria] = score
            feedback = {
                'mtld_score': round(mtld_score, 3),
                'rating': rating,
                'suggestion': 'Try using more varied vocabulary' if score < 8 else 'Excellent vocabulary diversity!'
            }

        elif criteria == 'FillerWordRate':
            filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically", 
                          "right", "i mean", "well", "kinda", "sort of", "okay", "hmm", "ah"]
            found_fillers = []
            
            for word in filler_words:
                if word.lower() in text.lower():
                    found_fillers.append(word)

            filler_count = len(found_fillers)
            fwr = filler_count/len(text.split())*100
            
            if 0 <= fwr <= 3:
                score = 15
                rating = "Excellent"
            elif 4 <= fwr <= 6:
                score = 12
                rating = "Very Good"
            elif 7 <= fwr <= 9:
                score = 9
                rating = "Good"
            elif 10 <= fwr <= 12:
                score = 6
                rating = "Fair"
            else:
                score = 3
                rating = "Needs Improvement"

            scores[criteria] = score
            feedback = {
                'filler_count': filler_count,
                'filler_rate': round(fwr, 2),
                'found_fillers': found_fillers,
                'rating': rating,
                'suggestion': f'Reduce filler words: {", ".join(found_fillers[:3])}' if found_fillers else 'Great clarity!'
            }

        elif criteria == 'Sentiment':
            prob, positive_words = calculate_positive_word_probability(text)

            if prob >= 0.999999999999:
                score = 15
                rating = "Excellent"
            elif 0.7 <= prob <= 0.8999999999999:
                score = 12
                rating = "Very Good"
            elif 0.5 <= prob <= 0.6999999999999:
                score = 9
                rating = "Good"
            elif 0.3 <= prob <= 0.4999999999999:
                score = 6
                rating = "Fair"
            else:
                score = 3
                rating = "Needs Improvement"

            scores[criteria] = score
            feedback = {
                'positivity_score': prob,
                'positive_words': positive_words[:10],  # Show first 10
                'rating': rating,
                'suggestion': 'Add more positive and engaging words' if score < 12 else 'Great positive tone!'
            }

        elif criteria == 'Flow':
            flow_result = check_flow_order(text)
            if flow_result['is_correct']:
                scores[criteria] = 5
            else:
                scores[criteria] = 0
            
            feedback = {
                'is_correct': flow_result['is_correct'],
                'found_sections': flow_result['found_sections'],
                'missing_sections': flow_result['missing_sections'],
                'issue': flow_result['issue'],
                'suggestion': flow_result['issue'] if not flow_result['is_correct'] else 'Perfect flow structure!'
            }
        
        detailed_feedback[criteria] = feedback
    
    return scores, detailed_feedback


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

    # Calculate scores with detailed feedback
    scores, detailed_feedback = grade(text, gradingCriterion, subCriterion, weights, duration)
    
    # Calculate overall score
    overall_score = sum(scores.values())
    
    # Calculate speech rate
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
                        "feedback": f"Salutation effectiveness: {scores.get('Salutation', 0)}/{weights['Salutation']}",
                        "details": detailed_feedback.get('Salutation', {})
                    },
                    {
                        "name": "Keyword Presence", 
                        "score": scores.get('KeyWord', 0),
                        "maxScore": weights['KeyWord'],
                        "feedback": f"Key information coverage: {scores.get('KeyWord', 0)}/{weights['KeyWord']}",
                        "details": detailed_feedback.get('KeyWord', {})
                    },
                    {
                        "name": "Flow & Structure",
                        "score": scores.get('Flow', 0),
                        "maxScore": weights['Flow'],
                        "feedback": f"Introduction flow: {scores.get('Flow', 0)}/{weights['Flow']}",
                        "details": detailed_feedback.get('Flow', {})
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
                        "feedback": f"Speech pace: {round(speech_rate, 2)} words/minute",
                        "details": detailed_feedback.get('SpeechRate', {})
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
                        "feedback": f"Grammar and language accuracy",
                        "details": detailed_feedback.get('Error', {})
                    },
                    {
                        "name": "Vocabulary Richness",
                        "score": scores.get('Richness', 0),
                        "maxScore": weights['Richness'],
                        "feedback": f"Vocabulary diversity and richness",
                        "details": detailed_feedback.get('Richness', {})
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
                        "feedback": f"Clarity and filler word usage",
                        "details": detailed_feedback.get('FillerWordRate', {})
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
                        "feedback": f"Positive tone and engagement",
                        "details": detailed_feedback.get('Sentiment', {})
                    }
                ]
            }
        ]
    }
    
    return result

if __name__ == "__main__":
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