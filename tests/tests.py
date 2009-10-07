from django.conf import settings
from django.core.management import call_command
from django.db import models
from django.db.models.loading import load_app
from django.test import TestCase

from usertools.helpers import update_related_fields
from usertools.tests.test_app.models import Author, Book, Chapter, Page


class HelpersTest(TestCase):
    # @@@ If I was really cool I'd put these in here.
    # fixtures = []

    def setUp(self):
        self.old_INSTALLED_APPS = settings.INSTALLED_APPS
        settings.INSTALLED_APPS = (
            'usertools',
            'usertools.tests.test_app',
        )
        load_app('usertools.tests.test_app')
        call_command('syncdb', verbosity=0, interactive=False)

    def tearDown(self):
        settings.INSTALLED_APPS = self.old_INSTALLED_APPS

    def test_update_related_fields(self):
        "usertools.helpers.update_related_fields: Update related object fields."
        user1 = Author.objects.create(name="john")
        user2 = Author.objects.create(name="igor")

        book = Book.objects.create(user=user1, title="Igor le labrador")
        chapter = Chapter.objects.create(user=user1, book=book, number=1)
        
        # update book/chapter for Igor.
        update_related_fields(book, {"user": user2.id})

        updated_book = user2.book_set.all()[0]
        updated_chapter = user2.chapter_set.all()[0]
                
        # page will not be updated because fieldname is different.
        page = Page.objects.create(author=user2, book=book, 
            chapter=updated_chapter, number=1)
        
        # update book/chapter for John.
        update_related_fields(updated_book, {"user": user1.id})
        
        self.assertEquals(user2.book_set.all().count(), 0)        
        self.assertEquals(user1.book_set.all().count(), 1)

        self.assertEquals(user2.chapter_set.all().count(), 0)
        self.assertEquals(user1.chapter_set.all().count(), 1)

        self.assertEquals(user2.page_set.all().count(), 1)
        self.assertEquals(user1.page_set.all().count(), 0)