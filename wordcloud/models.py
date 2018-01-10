from django.db import models

class Comment(models.Model):
    author_id = models.CharField(max_length=50)
    parent_id = models.IntegerField()
    step = models.CharField(max_length=6)
    week_number = models.SmallIntegerField()
    step_number = models.SmallIntegerField()
    text = models.TextField()
    timestamp = models.DateTimeField()
    moderated = models.DateTimeField()
    likes = models.SmallIntegerField()
    course_name = models.CharField(max_length=255)
    course_run = models.SmallIntegerField()
    word_count = models.SmallIntegerField()

class Term(models.Model):
    term = models.CharField(max_length=255)
    category = models.CharField(max_length=30)
    score = models.SmallIntegerField()

class CommentTerms(models.Model):
    comment_id = models.ForeignKey('Comment', on_delete=models.CASCADE)
    term_id = models.ForeignKey('Term', on_delete=models.CASCADE)
    count = models.SmallIntegerField
