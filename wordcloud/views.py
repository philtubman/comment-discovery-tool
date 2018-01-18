from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from csv import DictReader
from ims_lti_py.tool_provider import DjangoToolProvider
from io import TextIOWrapper
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer
from urllib.parse import urlparse

from .models import BadWord, Comment, CommentTerms, CourseLog, LTIConsumer, SearchLog, Term, UserAccess

def index(request):
    return render(request, 'wordcloud/index.html')

@csrf_exempt
@require_POST
def ltilaunch(request):

    consumer_key = request.POST.get('oauth_consumer_key')

    if consumer_key:
        consumer = LTIConsumer.objects.get(consumer_key=consumer_key)
    else:
        return HttpResponse('oauth_consumer_key must be supplied', status=403)

    tool_provider = DjangoToolProvider(consumer_key, consumer.secret, request.POST)

    lti_params = tool_provider.to_params()

    # Set the session stuff in here.
    request.session['user_id'] = lti_params['user_id']
    course_id = str(lti_params['context_id'])
    request.session['course_id'] = course_id

    request.session['course_title'] = lti_params['context_title']

    return_url = lti_params.get('launch_presentation_return_url')

    # This is FutureLearn specific
    if return_url and 'moocs.lancaster.ac.uk' in return_url:
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

    if 'chosen_word' in request.session:
        del request.session['chosen_word']
        request.session.modified = True

    return render(request, 'wordcloud/wordcloud.html')

@require_POST
def onewordresults(request):

    user_id = request.session['user_id']
    course_id = request.session['course_id']
    course_title = request.session['course_title']
    chosen_topic = request.session['chosen_topic']
    course_run = request.session['course_run']
    chosen_word = request.POST['chosenWord']
    request.session['chosen_word'] = chosen_word

    sql = """SELECT author_id, id, text, course_run
            FROM wordcloud_comment AS c
            WHERE text LIKE %s AND c.course_name = %s AND course_run = %s
            ORDER BY timestamp DESC
            fetch first 100 rows only"""

    chosen_word_like = "% {} %".format(chosen_word)
    comments = []
    with connection.cursor() as cursor:
        cursor.execute(sql, [chosen_word_like, chosen_topic, course_run])
        for result in cursor:
            comment_text = result[2].replace(chosen_word, "<mark>{}</mark>".format(chosen_word))
            comments.append({'author_id': result[0], 'id': str(result[1]), 'text': comment_text})
    _log_search(user_id, chosen_word, chosen_topic, course_run)
    return render(request, 'wordcloud/onewordresults.html', {'comments': comments, 'chosen_word': chosen_word, 'chosen_topic': chosen_topic, 'course_run': course_run})

@require_POST
def twowordsresults(request):

    user_id = request.session['user_id']
    chosen_topic = request.session['chosen_topic']
    course_run = request.session['course_run']

    chosen_word_1 = request.session['chosen_word']
    chosen_word_2 = request.POST['chosenWord2']

    sql = """SELECT author_id, id, text, course_run
            FROM wordcloud_comment AS c
            WHERE c.course_name = %s AND course_run = %s
            AND text LIKE %s
            AND text LIKE %s
            ORDER BY timestamp DESC
            fetch first 100 rows only"""

    chosen_word_1_like = "% {} %".format(chosen_word_1)
    chosen_word_2_like = "% {} %".format(chosen_word_2)
    comments = []
    with connection.cursor() as cursor:
        cursor.execute(sql, [chosen_topic, course_run, chosen_word_1_like, chosen_word_2_like])
        for result in cursor:
            comment_text = result[2].replace(chosen_word_1, "<mark>{}</mark>".format(chosen_word_1)).replace(chosen_word_2, "<mark>{}</mark>".format(chosen_word_2))
            comments.append({'author_id': result[0], 'id': str(result[1]), 'text': comment_text})
    _log_search(user_id, "{}+{}".format(chosen_word_1,chosen_word_2), chosen_topic, course_run)

    del request.session['chosen_word']
    request.session.modified = True

    return render(request, 'wordcloud/twowordsresults.html', {'comments': comments, 'chosen_word_1': chosen_word_1, 'chosen_word_2': chosen_word_2, 'chosen_topic': chosen_topic, 'course_run': course_run})

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
        course,run = csvfile.name[0:csvfile.name.index('_')].split('-')
        wrapper = TextIOWrapper(csvfile)
        reader = DictReader(wrapper)
        for row in reader:
            comment = Comment()
            comment.author_id = row['author_id']
            if row['parent_id'] == '':
                row['parent_id'] = None
            comment.parent_id = row['parent_id']
            comment.step = row['step']
            comment.week_number = row['week_number']
            comment.step_number = row['step_number']
            comment.text = row['text']
            comment.timestamp = row['timestamp'][:-4]
            if row['moderated'] == '':
                row['moderated'] = None
            comment.moderated = row['moderated']
            comment.likes = row['likes']
            comment.course_name = course
            comment.course_run = run
            words = tokenizer.tokenize(comment.text)
            # Filter out numbers and stopwords.
            words = [w for w in words if not is_number(w) if w.lower() not in stop]
            comment.word_count = len(words)
            comment.save()

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

        return redirect('wordcloud')
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

    # For the specified course run, select all the terms that occurred in a comment on the course, together
    # with the total occurrences of that term across all the comments in the run.
    sql = """SELECT term AS text, sum(count) AS size
                FROM wordcloud_comment c
                INNER JOIN wordcloud_commentterms ct ON c.id = ct.comment_id
                INNER JOIN wordcloud_term t ON t.id = ct.term_id
                WHERE course_name = %s AND course_run = %s
                AND term NOT IN (SELECT word from wordcloud_badword)"""

    if 'chosen_word' in request.session:
        sql += " AND term != %s"
    
    sql += """ GROUP BY term
                ORDER BY size DESC
                fetch first 200 rows only"""

    params = [chosen_topic, course_run]
    if 'chosen_word' in request.session:
        params.append(request.session['chosen_word'])
    results = []
    with connection.cursor() as cursor:
        cursor.execute(sql, params)
        for result in cursor:
            results.append({'text': result[0], 'size': str(result[1])})

    return JsonResponse(results, safe=False)

def _log_launch(user_id, course_id, return_url):

    user_access, created = UserAccess.objects.get_or_create(user_id=user_id)
    user_access.count += 1
    user_access.save()
    CourseLog.objects.create(user_id=user_id, return_url=return_url, course_id=course_id)

def _log_search(user_id, search, course_name, course_run):
    SearchLog.objects.create(user_id=user_id, search=search, course_name=course_name, course_run=course_run)
