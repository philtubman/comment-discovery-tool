from django.contrib import admin
from .models import *

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    model = Term

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    model = Hashtag

@admin.register(CommentTerms)
class CommentTermsAdmin(admin.ModelAdmin):
    model = CommentTerms

@admin.register(CommentHashtags)
class CommentHashtagsAdmin(admin.ModelAdmin):
    model = CommentHashtags

@admin.register(LTIConsumer)
class LTIConsumerAdmin(admin.ModelAdmin):
    model = LTIConsumer

@admin.register(BadWord)
class BadWordAdmin(admin.ModelAdmin):
    model = BadWord

@admin.register(CourseLog)
class CourseLogAdmin(admin.ModelAdmin):
    model = CourseLog

@admin.register(SearchLog)
class CourseLogAdmin(admin.ModelAdmin):
    model = SearchLog

@admin.register(ClickLog)
class ClickLogAdmin(admin.ModelAdmin):
    model = ClickLog
