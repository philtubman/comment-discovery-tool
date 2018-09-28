def add_session_key(request):
    if not request.session.session_key:
        request.session.save()

    return {'session_key': request.session.session_key}
