# For testing.

from django.db import models


class AuthorTest(models.Model):
    name = models.CharField(max_length=32)
    
    def __unicode__(self):
        return "<AuthorTest: %s>" % self.name

class BookTest(models.Model):
    user = models.ForeignKey(AuthorTest)
    title = models.CharField(max_length=32)

    def __unicode__(self):
        return "<BookTest: %s>" % self.title

class ChapterTest(models.Model):
    user = models.ForeignKey(AuthorTest)
    book = models.ForeignKey(BookTest)
    number = models.IntegerField()

    def __unicode__(self):
        return "<ChapterTest: %s>" % self.number
    
class PageTest(models.Model):
    author = models.ForeignKey(AuthorTest)
    book = models.ForeignKey(BookTest)
    chapter = models.ForeignKey(ChapterTest)
    number = models.IntegerField()
    
    def __unicode__(self):
        return "<PageTest: %s>" % self.number
    