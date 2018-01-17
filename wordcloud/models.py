from django.db import models

class Comment(models.Model):
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

class CommentTerms(models.Model):
    comment = models.ForeignKey('Comment', on_delete=models.CASCADE)
    term = models.ForeignKey('Term', on_delete=models.CASCADE)
    count = models.SmallIntegerField()
    class Meta:
        unique_together = (('comment', 'term'),)

class LTIConsumer(models.Model):
    consumer_key = models.CharField(max_length=255, unique=True)
    secret = models.CharField(max_length=36)

class StopWord(models.Model):
    word = models.CharField(max_length=24, unique=True)
