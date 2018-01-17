from django.contrib import admin
from .models import Comment, CommentTerms, LTIConsumer, StopWord, Term

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    model = Comment

@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    model = Term

@admin.register(CommentTerms)
class CommentTermsAdmin(admin.ModelAdmin):
    model = CommentTerms

@admin.register(LTIConsumer)
class LTIConsumerAdmin(admin.ModelAdmin):
    model = LTIConsumer

@admin.register(StopWord)
class StopWordAdmin(admin.ModelAdmin):
    model = StopWord
