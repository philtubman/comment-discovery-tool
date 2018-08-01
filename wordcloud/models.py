from django.db import models

class Comment(models.Model):
    source_id = models.CharField(max_length=255, unique=True)
    author_id = models.CharField(max_length=50)
    parent_id = models.IntegerField(null=True)
    step = models.CharField(max_length=6)
    week_number = models.SmallIntegerField()
    step_number = models.SmallIntegerField()
    text = models.TextField()
    timestamp = models.DateTimeField()
    moderated = models.DateTimeField(null=True)
    likes = models.SmallIntegerField()
    course_name = models.CharField(max_length=255)
    course_run = models.SmallIntegerField()
    word_count = models.SmallIntegerField()

class Term(models.Model):
    term = models.CharField(max_length=255, unique=True)

class Hashtag(models.Model):
    hashtag = models.CharField(max_length=255, unique=True)

class CommentTerms(models.Model):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    term = models.ForeignKey('Term', on_delete=models.CASCADE)
    count = models.SmallIntegerField()
    class Meta:
        unique_together = (('comment', 'term'),)

class CommentHashtags(models.Model):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    hashtag = models.ForeignKey('Hashtag', on_delete=models.CASCADE)
    count = models.SmallIntegerField()
    class Meta:
        unique_together = (('comment', 'hashtag'),)

class LTIConsumer(models.Model):
    consumer_key = models.CharField(max_length=255, unique=True)
    secret = models.CharField(max_length=36)

class BadWord(models.Model):
    word = models.CharField(max_length=24, unique=True)

class UserAccess(models.Model):
    user_id = models.CharField(max_length=36, unique=True)
    count = models.IntegerField(default=0)
    last_access = models.DateTimeField(auto_now=True)

class CourseLog(models.Model):
    user_id = models.CharField(max_length=36)
    return_url = models.CharField(max_length=255)
    course_id = models.CharField(max_length=255)
    access_time = models.DateTimeField(auto_now=True)

class SearchLog(models.Model):
    user_id = models.CharField(max_length=36)
    search = models.CharField(max_length=255)
    course_name = models.CharField(max_length=255)
    course_run = models.SmallIntegerField()

class ClickLog(models.Model):
    user_id = models.CharField(max_length=36)
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    click_time = models.DateTimeField(auto_now=True)
