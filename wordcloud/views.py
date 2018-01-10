from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST
from urllib.parse import urlparse
import pylti

def index(request):
    return render(request, 'wordcloud/index.html')

def ltilaunch(request):
    # Set the session stuff in here.
    request.session['userId'] = 'ltiUserId'
    request.session['courseId'] = 'ltiContextId'
    request.session['courseTitle'] = 'ltiTitle'
    path = urlparse('returnUrl').path
    parts = split(path, '/')
    chosenTopic = parts[2]
    '''
    if (strrpos($_SESSION['courseId'], 'sandpit')) {
	$_SESSION['chosenTopic'] = 'Ebola';
    } else {
	$_SESSION['chosenTopic'] = $chosenTopic;
    }
    $_SESSION['courseRun'] = $parts[3];
    '''
    return redirect('wordcloud')

def wordcloud(request):
    # Pick up the session stuff in here.
    return render(request, 'wordcloud/wordcloud.html')
