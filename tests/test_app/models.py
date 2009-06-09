from django.db import models


class Author(models.Model):
    name = models.CharField(max_length=32)
    
    def __unicode__(self):
        return "<Author: %s>" % self.name

class Book(models.Model):
    user = models.ForeignKey(Author)
    title = models.CharField(max_length=32)

    def __unicode__(self):
        return "<Book: %s>" % self.title

class Chapter(models.Model):
    user = models.ForeignKey(Author)
    book = models.ForeignKey(Book)
    number = models.IntegerField()

    def __unicode__(self):
        return "<Chapter: %s>" % self.number
    
class Page(models.Model):
    author = models.ForeignKey(Author)
    book = models.ForeignKey(Book)
    chapter = models.ForeignKey(Chapter)
    number = models.IntegerField()
    
    def __unicode__(self):
        return "<Page: %s>" % self.number
    