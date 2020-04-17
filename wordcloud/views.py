from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.utils import IntegrityError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie

from csv import DictReader
from ims_lti_py.tool_provider import DjangoToolProvider
from io import TextIOWrapper
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from nltk import ne_chunk, pos_tag, Tree
from urllib.parse import urlparse # Python 3
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
    wordcloud_id = 0
    other_comments_nbr = 0
    with connection.cursor() as cursor:
        sql = "SELECT text,id FROM wordcloud_comment WHERE source_id = '" + id + "'"
        cursor.execute(sql)
        for result in cursor:
            comment = result[0]
            wordcloud_id = result[1]
        
        if wordcloud_id:
            sql = "SELECT COUNT(id) FROM wordcloud_comment WHERE parent_id = " + str(id)
            cursor.execute(sql)
            for result in cursor:
                other_comments_nbr = result[0]
            if other_comments_nbr > 0:
                other_comments_nbr -= 1
    return JsonResponse({'comment' : comment, 'wordcloud_id' : wordcloud_id, 'other_comments_nbr' : other_comments_nbr})

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

    return results(request)

@require_POST
def results(request):
    user_id = request.session['user_id']
    course_id = request.session['course_id']
    course_title = request.session['course_title']
    chosen_topic = request.session['chosen_topic']
    course_run = request.session['course_run']
    chosen_words = request.POST.getlist('chosen_words')
    
    pageData = {}
    pageData["chosen_topic"] = request.session['chosen_topic']
    pageData["course_run"] = request.session['course_run']
    
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
    
    weeks = getWeeks(request)
    pageData["weeks"] = weeks
    
    # Hashtag tab (special behaviour: ignores chosen words, weeks, etc... and returns special wordcloud directly)
    if "gethashtags" in request.POST:
        if 'chosen_words' in request.session:
            del request.session['chosen_words']
        if 'searched_comment_ids' in request.session:
            del request.session['searched_comment_ids']
        request.session['gethashtags'] = True
        request.session.modified = True
        pageData['hashtags'] = True
        pageData['hashtags_selected'] = True
        return render(request, 'wordcloud/wordcloud.html', pageData)
    else:
        if "gethashtags" in request.session:
            del request.session['gethashtags']
            request.session.modified = True
    
    if 'week' in request.session:
        pageData["selectedWeek"] = request.session["week"]
    
    # Checks for repeated words and errors
    for word in chosen_words:
        if "," in word:
            chosen_words.remove(word)
    request.session['chosen_words'] = chosen_words
    pageData["chosen_words"] = chosen_words
    
    # Check if there are hashtags to display the tab if there are
    hashtags = False
    with connection.cursor() as cursor:
        sql = "SELECT COUNT(*) AS bHashtags FROM wordcloud_comment c INNER JOIN wordcloud_commentterms ct ON c.id = ct.comment_id INNER JOIN wordcloud_term t ON t.id = ct.term_id WHERE course_name = '" + chosen_topic +"' AND course_run = " + str(course_run) + " AND term NOT IN (SELECT word from wordcloud_badword) AND t.term LIKE '#%' LIMIT 1"
        cursor.execute(sql)
        for result in cursor:
            if result[0] > 0:
                hashtags = True
    pageData["hashtags"] = hashtags

    if not chosen_words:
        # No search or search has been reset, wiping searched comments
        if 'searched_comment_ids' in request.session:
            del request.session['searched_comment_ids']
        request.session.modified = True
        return render(request, 'wordcloud/wordcloud.html', pageData)

    sql = "SELECT id, source_id, author_id, text, parent_id, week_number, step_number, wt.tutor_id FROM wordcloud_comment wc LEFT JOIN wordcloud_tutors wt ON (wc.author_id = wt.tutor_source_id AND wc.course_name = wt.tutor_course AND wc.course_run = wt.tutor_course_run) WHERE course_name = %s AND course_run = %s"
    
    if "week" in request.session:
        sql += " AND week_number = %s"

    for word in chosen_words:
        sql += " AND LOWER(text) SIMILAR TO LOWER(%s)" # LOWER() for case insensitive results

    sql += " ORDER BY timestamp DESC fetch first 100 rows only"
	
    comments = []
    if chosen_words:
        with connection.cursor() as cursor:
            params = [chosen_topic, course_run]
            if "week" in request.session:
                params.append(request.session["week"])
            # TODO: The following line could use a better regex, ideally we want the chosen word with a character that is not alphanumeric before and after it.
            params.extend(["%( |.|,|;|:|!|\?|\(|\)|-|<|>|/){}( |.|,|;|:|!|\?|\(|\)|-|<|>|/)%".format(w) for w in chosen_words])
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
                comments.append({'id': result[0], 'source_id': result[1], 'author_id': result[2], 'text': comment_text, 'parent_id' : result[4], 'week_number' : result[5], 'step_number' : result[6], 'tutor_id' : result[7]})
        _log_search(user_id, chosen_words, chosen_topic, course_run)

    # Store the comment ids in the session for search refinement later
    request.session['searched_comment_ids'] = [c['id'] for c in comments]
    pageData["comments"] = comments
    #pageData["sql"] = sql.replace("%s", "{}").format(*params)
    
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
        reader = DictReader(wrapper)
        source_id = [] # To remove comments that have been removed from FL
        
        for row in reader:
            comment = Comment()
            comment.source_id = row['id']
            source_id.append(row['id'])
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
                pass
            words = [w.lower() for w in raw_tokens if w not in named_entities]
            # Filter out numbers and stopwords.
            words = [w for w in words if not is_number(w) if w not in stop]
            # Add the named entities back in.
            words.extend(named_entities)
            # Hashtag detection
            if " #" in comment.text:
                hashtag = ""
                hashtag_began = False
                space_before = False
                for character in comment.text:
                    if character == ' ':
                        space_before = True
                        continue
                    if hashtag_began and not character.isalnum():
                        words.append(hashtag)
                        hashtag = ""
                        hashtag_began = False
                    if character == '#' and space_before:
                        hashtag_began = True
                    if hashtag_began:
                        hashtag += character
                    space_before = False
                if hashtag_began:
                    words.append(hashtag)
                    hashtag = ""
                    hashtag_began = False
                        
            comment.word_count = len(words)

            try:
                comment.save()
            except IntegrityError as ie:
                # This is okay. Updated csvs are appended, so duplicates happen.
                #print("Comment {} exists already. Skipping ...".format(comment.source_id)) # Uncommenting this line will generates lots of console outputs which slows down execution
                pass

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
                if comment.id and term_id and count:
                    comment_terms.append(CommentTerms(comment_id=comment.id, term_id=term_id, count=count))
            CommentTerms.objects.bulk_create(comment_terms)
            
        ### Delete comments that have been deleted from FL
        deleted_from_FL_nbr = 0
        with connection.cursor() as cursor:
            # Create cascading delete constraint
            try:
                sql = "ALTER TABLE wordcloud_commentterms DROP CONSTRAINT purge_course_run_cascade_ct; ALTER TABLE wordcloud_clicklog DROP CONSTRAINT purge_course_run_cascade_cl;"
                cursor.execute(sql)
            except:
                pass
            sql = "ALTER TABLE wordcloud_commentterms ADD CONSTRAINT purge_course_run_cascade_ct FOREIGN KEY (comment_id) REFERENCES wordcloud_comment (id) ON DELETE CASCADE; ALTER TABLE wordcloud_clicklog ADD CONSTRAINT purge_course_run_cascade_cl FOREIGN KEY (comment_id) REFERENCES wordcloud_comment (id) ON DELETE CASCADE;"
            cursor.execute(sql)
            # Delete all comments for this course/run from wordcloud_comment with cascading effect
            sql = "DELETE FROM wordcloud_comment WHERE course_name = '" + course + "' AND course_run = " + run
            if source_id:
                sql += " AND source_id NOT IN ("
                first = True
                for id in source_id:
                    if first:
                        first = False
                    else:
                        sql += " , "
                    sql += "'" + id + "'"
                sql += ")"
            try:
                cursor.execute(sql)
                deleted_from_FL_nbr = cursor.rowcount
            except:
                pass
            # Removes cascading delete constraint
            sql = "ALTER TABLE wordcloud_commentterms DROP CONSTRAINT purge_course_run_cascade_ct; ALTER TABLE wordcloud_clicklog DROP CONSTRAINT purge_course_run_cascade_cl;"
            cursor.execute(sql)

        pageData = {'uploadstatus': "Comments updated.", 'deleted_from_FL_nbr' : deleted_from_FL_nbr}
        return render(request, 'wordcloud/uploadcomments.html', pageData)
    
    return render(request, 'wordcloud/uploadcomments.html')

@login_required(login_url='/admin/login/')
def uploadtutors(request):
    if request.method == 'POST':
        csvfile = request.FILES['csvfile']
        course,run = csvfile.name[0:csvfile.name.index('_')].rsplit('-', 1) # fails if the CSV isn't named as it should from FutureLearn
        wrapper = TextIOWrapper(csvfile, encoding='utf8')
        reader = DictReader(wrapper)
        
        edited = 0
        inserted = 0
        errors = 0
        sqls = []
        for row in reader:
            with connection.cursor() as cursor:
                # If exist, update, otherwise, insert
                sql = "SELECT tutor_id FROM wordcloud_tutors WHERE tutor_source_id = %s AND tutor_course = %s and tutor_course_run = %s LIMIT 1"
                try:
                    params = [row['id'], course, run]
                    sqls.append(sql.replace("%s", "{}").format(*params))
                    cursor.execute(sql, params)
                    tutor_exists = False
                except:
                    errors += 1
                    continue
                for result in cursor:
                    if result[0]:
                        if result[0] != 0:
                            tutor_exists = True
                if tutor_exists:
                    # Update tutor
                    sql = "UPDATE wordcloud_tutors SET tutor_first_name = %s, tutor_last_name = %s, tutor_team_role = %s, tutor_user_role = %s WHERE tutor_source_id = %s AND tutor_course = %s AND tutor_course_run = %s"
                    try:
                        params = [row['first_name'], row['last_name'], row['team_role'], row['user_role'], row['id'], course, run]
                        sqls.append(sql.replace("%s", "{}").format(*params))
                        cursor.execute(sql, params)
                        edited += 1
                    except:
                        errors += 1
                        continue
                else:
                    # Insert tutor
                    sql = "INSERT INTO wordcloud_tutors (tutor_source_id, tutor_course, tutor_course_run, tutor_first_name, tutor_last_name, tutor_team_role, tutor_user_role) VALUES (%s, %s, %s, %s, %s, %s, %s)"
                    try:
                        params = [row['id'], course, run, row['first_name'], row['last_name'], row['team_role'], row['user_role']]
                        sqls.append(sql.replace("%s", "{}").format(*params))
                        cursor.execute(sql, params)
                        inserted += 1
                    except:
                        errors += 1
                        continue
            
        pageData = {'sqls' : sqls, 'uploadstatus': "Tutors updated. {} inserted, {} edited, {} errors".format(inserted, edited, errors)}
        return render(request, 'wordcloud/uploadtutors.html', pageData)
    
    return render(request, 'wordcloud/uploadtutors.html')

@login_required(login_url='/admin/login/')
def purge(request):
    if request.method == 'POST':
        action = request.POST.get("action", "")
        if action == "purgeCourseRun" or action == "purgeAll":
            courserun = request.POST.get("course_runs", "/")
            course,run = courserun.rsplit('/', 1)
            with connection.cursor() as cursor:
                # Create cascading delete constraint
                try:
                    sql = "ALTER TABLE wordcloud_commentterms DROP CONSTRAINT purge_course_run_cascade_ct; ALTER TABLE wordcloud_clicklogs DROP CONSTRAINT purge_course_run_cascade_cl;"
                    cursor.execute(sql)
                except:
                    pass
                sql = "ALTER TABLE wordcloud_commentterms ADD CONSTRAINT purge_course_run_cascade_ct FOREIGN KEY (comment_id) REFERENCES wordcloud_comment (id) ON DELETE CASCADE; ALTER TABLE wordcloud_clicklog ADD CONSTRAINT purge_course_run_cascade_cl FOREIGN KEY (comment_id) REFERENCES wordcloud_comment (id) ON DELETE CASCADE;"
                cursor.execute(sql)
                if action == "purgeCourseRun":
                    # Delete all comments for this course/run from wordcloud_comment with cascading effect
                    sql = "DELETE FROM wordcloud_comment WHERE course_name = '" + course + "' AND course_run = " + run + ";"
                    pageData = {'message': "Course " + course + " #" + run + " was purged."}
                if action == "purgeAll":
                    # Wipes everything
                    sql = "DELETE FROM wordcloud_comment WHERE 1=1"
                    pageData = {'message': "Everything was purged."}
                cursor.execute(sql)
                # Removes cascading delete constraint
                sql = "ALTER TABLE wordcloud_commentterms DROP CONSTRAINT purge_course_run_cascade_ct; ALTER TABLE wordcloud_clicklog DROP CONSTRAINT purge_course_run_cascade_cl;"
                cursor.execute(sql)
            
            
            return render(request, 'wordcloud/purge.html', pageData)
        else:
            pageData = {'message': "Unknown action. Nothing was done."}
            return render(request, 'wordcloud/purge.html', pageData)
    
    return render(request, 'wordcloud/purge.html')

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
    params = [chosen_topic, course_run]
    
    #print("user_id: " + user_id + " | course_id: " + course_id + " | course_title: " + course_title + " | chosen_topic: " + chosen_topic + " | course_run: " + str(course_run))

    if Comment.objects.filter(course_name=chosen_topic, course_run=course_run).count():
        sql = "SELECT term AS text, sum(count) AS size FROM wordcloud_comment c INNER JOIN wordcloud_commentterms ct ON c.id = ct.comment_id INNER JOIN wordcloud_term t ON t.id = ct.term_id WHERE course_name = %s AND course_run = %s AND term NOT IN (SELECT word from wordcloud_badword)"
        
        # Hashtags (special behaviour)
        if "gethashtags" in request.session:
            sql += " AND t.term LIKE '#%%'"
        else:
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
            
            if "week" in request.session:
                params.append(request.session["week"])
            if 'chosen_words' in request.session:
                params.extend(request.session['chosen_words'])
        
        sql += " AND LENGTH(term) > 2 GROUP BY term ORDER BY size DESC fetch first 200 rows only"
        
        results = []
        with connection.cursor() as cursor:
            cursor.execute(sql, params)
            nbrResults = 0
            lastSize = 0
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
                    size = result[1]
                    if nbrResults == 1 and size == 1:
                        size = 2 # Quick and dirty fix, the wordcloud doesn't work if all words are size == 1
                    results.append({'text': result[0], 'size': result[1]})

        results.append({'text': " ", 'size': 0}) # Quick fix for a wordcloud bug, if all words in list are same size, the wordcloud prints out nothing. This allows to always have something different (size 0)
        
        #print("nbrResults: " + str(nbrResults));
        #results.append({'sql_request': sql})
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
