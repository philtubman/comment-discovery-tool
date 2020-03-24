from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from csv import DictReader
from ims_lti_py.tool_provider import DjangoToolProvider
from io import TextIOWrapper
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk import ne_chunk, pos_tag, Tree
#from urllib.parse import urlparse # Python 3
from urlparse import urlparse # Python 2
import logging

import numpy

from importlib import import_module
from django.conf import settings

from .models import *

logger = logging.getLogger(__name__)

def index(request):
    return render(request, 'wordcloud/index.html')

# This function gets the text of a single comment by its FutureLearn ID
def comment(request):
    # Mandatory checks
    if not 'id' in request.GET:
        return JsonResponse({'status': 'NO DATA', 'comment' : ''})
    id = request.GET['id']
    if not id.isnumeric():
        return JsonResponse({'status': 'NO DATA', 'comment' : ''})
    # Query
    comment = ""
    print(id)
    with connection.cursor() as cursor:
        sql = """SELECT text FROM wordcloud_comment WHERE source_id = '""" + id + """'"""
        cursor.execute(sql)
        for result in cursor:
            comment = result[0]
        return JsonResponse({'comment' : comment})

# This function returns JSON data containing the count of distinct courses and courses runs with their name
def courses(request):
    results = []
    with connection.cursor() as cursor:
        sql = """SELECT DISTINCT course_name, course_run FROM wordcloud_comment ORDER BY course_name ASC, course_run ASC"""
        cursor.execute(sql)
        count = 0
        results.append({'count': count})
        for result in cursor:
            results.append({'course': result[0], 'run': str(result[1])})
            count += 1
        results[0]['count'] = count
    return JsonResponse(results, safe=False)

# This function returns the weeks available for a specific course and run in a JSON response
def weeks(request):
    results = []
    # This function needs a course and a run to be able to work
    if request.session['chosen_topic'] is None or request.session['course_run'] is None:
        return JsonResponse(results, safe=False)
    params = [request.session['chosen_topic'], request.session['course_run']]
    with connection.cursor() as cursor:
        sql = """SELECT DISTINCT week_number FROM wordcloud_comment WHERE course_name = %s AND course_run = %s ORDER BY week_number ASC"""
        cursor.execute(sql, params)
        for result in cursor:
            results.append({'week': result[0]})
    return JsonResponse(results, safe=False)

# This function returns the weeks available for a specific course and run in a python list
def getWeeks(request):
    results = []
    # This function needs a course and a run to be able to work
    if request.session['chosen_topic'] is None or request.session['course_run'] is None:
        return results
    params = [request.session['chosen_topic'], request.session['course_run']]
    with connection.cursor() as cursor:
        sql = """SELECT DISTINCT week_number FROM wordcloud_comment WHERE course_name = %s AND course_run = %s ORDER BY week_number ASC"""
        cursor.execute(sql, params)
        for result in cursor:
            results.append(result[0])
    # Checks if the week in session exists and deletes it otherwise
    if "week" in request.session:
        if not request.session["week"] in results:
            del request.session['week']
    return results

@csrf_exempt
@require_POST
def ltilaunch(request):
    consumer_key = request.POST.get('oauth_consumer_key')

    if consumer_key:
        consumer = LTIConsumer.objects.get(consumer_key=consumer_key)
    else:
        return HttpResponse('oauth_consumer_key must be supplied', status=403)

    tool_provider = DjangoToolProvider(consumer_key, consumer.secret, request.POST)

    if not tool_provider.is_launch_request():
        return HttpResponse('Not a launch request', status=403)

    lti_params = tool_provider.to_params()

    # Set the session stuff in here.
    request.session['user_id'] = lti_params['user_id']
    course_id = str(lti_params['context_id'])
    request.session['course_id'] = course_id

    request.session['course_title'] = lti_params['context_title']

    return_url = lti_params.get('launch_presentation_return_url')

    # This is FutureLearn specific
    if return_url and 'www.futurelearn.com' in return_url:
        parts = urlparse(lti_params['launch_presentation_return_url']).path.split('/')
        if len(parts) >= 4:
            chosen_topic = parts[2]
            request.session['chosen_topic'] = 'Ebola' if 'sandpit' in course_id else chosen_topic
            request.session['course_run'] = int(parts[3])
    else:
        # Test data.
        request.session['chosen_topic'] = 'dyslexia'
        request.session['course_run'] = 1

    _log_launch(lti_params['user_id'],lti_params['context_id'], lti_params.get('launch_presentation_return_url'))

    return wordcloud(request)

def wordcloud(request):
    # Resets search in session
    if 'chosen_words' in request.session:
        del request.session['chosen_words']
        request.session.modified = True

    if 'searched_comment_ids' in request.session:
        del request.session['searched_comment_ids']
        request.session.modified = True
        
    if 'week' in request.session:
        del request.session['week']
        request.session.modified = True

    params = { "chosen_topic" : request.session['chosen_topic'], "course_run" : request.session['course_run']}
    weeks = getWeeks(request)
    params["weeks"] = weeks

    return render(request, 'wordcloud/wordcloud.html', params)

@csrf_exempt
@require_POST
def results(request):
    user_id = request.session['user_id']
    course_id = request.session['course_id']
    course_title = request.session['course_title']
    chosen_topic = request.session['chosen_topic']
    course_run = request.session['course_run']
    chosen_words = request.POST.getlist('chosen_words')
    
    if "week" in request.POST:
        week = 0
        try:
            week = int(request.POST.get("week", 0))
        except:
            week = 0
        if week > 0:
            request.session["week"] = week
        else:
            if "week" in request.session:
                del request.session["week"]
            
    # Checks for repeated words and errors
    for word in chosen_words:
        if "," in word:
            chosen_words.remove(word)
    request.session['chosen_words'] = chosen_words
    
    pageData = {'chosen_words': chosen_words, 'chosen_topic': chosen_topic, 'course_run': course_run}
    weeks = getWeeks(request)
    pageData["weeks"] = weeks
    if 'week' in request.session:
        pageData["selectedWeek"] = request.session["week"]
    pageData["chosen_topic"] = request.session['chosen_topic']
    pageData["course_run"] = request.session['course_run']

    if not chosen_words:
        # No search or search has been reset, wiping searched comments
        if 'searched_comment_ids' in request.session:
            del request.session['searched_comment_ids']
        request.session.modified = True
        return render(request, 'wordcloud/wordcloud.html', pageData)

    sql = """SELECT id, source_id, author_id, text, parent_id
            FROM wordcloud_comment
            WHERE course_name = %s AND course_run = %s"""
    
    if "week" in request.session:
        sql += " AND week_number = %s"

    for word in chosen_words:
        sql += " AND LOWER(text) like LOWER(%s)" # LOWER() for case insensitive results

    sql += """ ORDER BY timestamp DESC
            fetch first 100 rows only"""
	
    comments = []
    if chosen_words:
        with connection.cursor() as cursor:
            params = [chosen_topic, course_run]
            if "week" in request.session:
                params.append(request.session["week"])
            params.extend(["% {} %".format(w) for w in chosen_words])
            cursor.execute(sql, params)
            for result in cursor:
                comment_text = result[3].replace(chosen_words[0], "<mark>{}</mark>".format(chosen_words[0]))
                for cw in chosen_words:
                    # The following lines will highlight the selected word also if the first letter is uppercase or lowercase
                    if cw[0].isupper():
                        cw = cw.lower()
                    elif cw[0].islower():
                        cw = cw.capitalize()
                    comment_text = comment_text.replace(cw, "<mark>{}</mark>".format(cw))
                    # TODO: Improve with a proper case insensitive replacement, string doesn't support it but re (re.IGNORECASE) seems to do it
                comments.append({'id': result[0], 'source_id': result[1], 'author_id': result[2], 'text': comment_text, 'parent_id' : result[4]})
        _log_search(user_id, chosen_words, chosen_topic, course_run)

    # Store the comment ids in the session for search refinement later
    request.session['searched_comment_ids'] = [c['id'] for c in comments]
    pageData["comments"] = comments
    
    return render(request, 'wordcloud/wordcloud.html', pageData)

@login_required(login_url='/admin/login/')
def uploadcomments(request):

    def is_number(s):
        try:
            float(s)
        except ValueError:
            return False
        else:
            return True

    if request.method == 'POST':
        # Load all the current terms into a dictionary for lookup
        current_terms = {}
        for ct in Term.objects.all():
            current_terms[ct.term] = ct.id

        stop = set(stopwords.words('english'))
        tokenizer = RegexpTokenizer(r'\w+')

        csvfile = request.FILES['csvfile']
        course,run = csvfile.name[0:csvfile.name.index('_')].rsplit('-', 1) # fails if the CSV isn't named as it should from FutureLearn
        wrapper = TextIOWrapper(csvfile, encoding='utf8')
        reader = DictReader(csvfile)
        for row in reader:
            comment = Comment()
            comment.source_id = row['id']
            comment.author_id = row['author_id']
            if row['parent_id'] == '':
                row['parent_id'] = None
            comment.parent_id = row['parent_id']
            comment.step = row['step']
            comment.week_number = row['week_number']
            comment.step_number = row['step_number']
            comment.text = row['text']
            comment.timestamp = row['timestamp'][:-4]
            comment.moderated = row['moderated'][:-4] if row['moderated'] else None
            comment.likes = row['likes']
            comment.course_name = course
            comment.course_run = run
            raw_tokens = tokenizer.tokenize(comment.text)
            # Added try and except here as it sometimes fails to read some unicode characters
            try:
                named_entities = [l[0][0] for l in ne_chunk(pos_tag(raw_tokens)) if type(l) == Tree]
            except:
                continue
            words = [w.lower() for w in raw_tokens if w not in named_entities]
            # Filter out numbers and stopwords.
            words = [w for w in words if not is_number(w) if w not in stop]
            # Add the named entities back in.
            words.extend(named_entities)
            comment.word_count = len(words)

            try:
                comment.save()
            except IntegrityError as ie:
                # This is okay. Updated csvs are appended, so duplicates happen.
                #print("Comment {} exists already. Skipping ...".format(comment.source_id)) # Uncommenting this line will generates lots of console outputs which slows down execution
                continue

            term_count = {}
            for word in words:
                if word in current_terms:
                    term_id = current_terms[word]
                else:
                    term = Term(term=word)
                    term.save()
                    term_id = term.id
                    current_terms[word] = term_id
                if term_id not in term_count:
                    term_count[term_id] = 1
                else:
                    term_count[term_id] = term_count[term_id] + 1

            comment_terms = []
            for term_id, count in term_count.items():
                comment_terms.append(CommentTerms(comment_id=comment.id, term_id=term_id, count=count))
            CommentTerms.objects.bulk_create(comment_terms)

        pageData = {'uploadstatus': "Comments updated."}
        return render(request, 'wordcloud/uploadcomments.html', pageData)
    else:
        return render(request, 'wordcloud/uploadcomments.html')

@login_required(login_url='/admin/login/')
def uploadbadwords(request):

    if request.method == 'POST':
        current_badwords = BadWord.objects.values_list('word')

        textfile = request.FILES['textfile']
        wrapper = TextIOWrapper(textfile)
        done = []
        for line in wrapper:
            badword = line.strip()
            if badword not in current_badwords and badword not in done:
                BadWord.objects.create(word=badword)
                done.append(badword)

        return redirect('wordcloud')
    else:
        return render(request, 'wordcloud/uploadbadwords.html')

def terms(request):
    user_id = request.session['user_id']
    course_id = request.session['course_id']
    course_title = request.session['course_title']

    # FutureLearn specific
    chosen_topic = request.session['chosen_topic']
    course_run = request.session['course_run']
    
    #print("user_id: " + user_id + " | course_id: " + course_id + " | course_title: " + course_title + " | chosen_topic: " + chosen_topic + " | course_run: " + str(course_run))

    if Comment.objects.filter(course_name=chosen_topic, course_run=course_run).count():
        # For the specified course run, select all the terms that occurred in a comment on the course, together
        # with the total occurrences of that term across all the comments in the run.
        sql = """SELECT term AS text, sum(count) AS size FROM wordcloud_comment c INNER JOIN wordcloud_commentterms ct ON c.id = ct.comment_id INNER JOIN wordcloud_term t ON t.id = ct.term_id WHERE course_name = %s AND course_run = %s AND term NOT IN (SELECT word from wordcloud_badword)"""
        
        if "week" in request.session:
            sql += " AND week_number = %s"

        commentsFound = 0
        if 'searched_comment_ids' in request.session:
            if request.session['searched_comment_ids']:
                commentsFound = len(request.session['searched_comment_ids'])
                sql += ' AND c.id IN ({})'.format(','.join(map(str, request.session['searched_comment_ids'])))

        chosenWords = 0
        if 'chosen_words' in request.session:
            chosenWords = len(request.session['chosen_words'])
            for cw in request.session['chosen_words']:
                sql += " AND LOWER(term) != LOWER(%s)" # LOWER() for case insensitive results
        
        # Check if no comments are found and return no data if it's the case
        if chosenWords > 0 and commentsFound == 0:
            return JsonResponse({'status': 'NO DATA'})
        
        sql += """ AND LENGTH(term) > 2 GROUP BY term ORDER BY size DESC fetch first 200 rows only"""
        
        print(sql);
        
        results = []
        with connection.cursor() as cursor:
            params = [chosen_topic, course_run]
            if "week" in request.session:
                params.append(request.session["week"])
            if 'chosen_words' in request.session:
                params.extend(request.session['chosen_words'])
            cursor.execute(sql, params)
            nbrResults = 0
            for result in cursor:
                nbrResults = nbrResults + 1
                # Case insensitive fix: un/capitalize and check if already in result, if yes, keeping highest size and adding size of smallest, otherwise the opposite
                wasInResult = 0
                wordCaseReverted = ""
                if result[0][0].isupper():
                    wordCaseReverted = result[0].lower()
                elif result[0][0].islower():
                    wordCaseReverted = result[0].capitalize()
                for resultSaved in results:
                    if resultSaved["text"] == wordCaseReverted: # The word is already in result with a different case
                        wasInResult = 1
                        print("found one: " + result[0] + " > " + wordCaseReverted)
                        resultSaved["size"] = int(resultSaved["size"]) + int(result[1]) # Updating the size of both words combined
                        if resultSaved["size"] < result[1]: # The new word is bigger, replacing string
                            resultSaved["text"] = result[0]
                            break
                        else:
                            break
                            # TODO: I'm not satisfied with this solution, performance wise it's not very good (lots of loops)
                
                if not wasInResult:
                    results.append({'text': result[0], 'size': str(result[1])})

        print("nbrResults: " + str(nbrResults));
        return JsonResponse(results, safe=False)
    else:
        return JsonResponse({'status': 'NO DATA'})

def log_click(request):
    user_id = request.session['user_id']
    comment_id = request.POST.get('commentId')

    if not comment_id:
        return HttpResponse('No commentId supplied', status=400)

    ClickLog.objects.create(user_id=user_id, comment_id=comment_id)
    return HttpResponse(status=204)

def _log_launch(user_id, course_id, return_url):
    user_access, created = UserAccess.objects.get_or_create(user_id=user_id)
    user_access.count += 1
    user_access.save()
    CourseLog.objects.create(user_id=user_id, return_url=return_url, course_id=course_id)

def _log_search(user_id, search, course_name, course_run):
    SearchLog.objects.create(user_id=user_id, search='+'.join(search), course_name=course_name, course_run=course_run)
