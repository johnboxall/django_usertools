from django.db import models
from django.test import TestCase

from usertools.models import AuthorTest, BookTest, ChapterTest, PageTest
from usertools.helpers import update_related_field


class HelpersTest(TestCase):

    def test_update_related_field(self):
        "usertools.helpers.update_related_field: Update related object fields."
        user1 = AuthorTest.objects.create(name="john")
        user2 = AuthorTest.objects.create(name="igor")

        book = BookTest.objects.create(user=user1, title="Igor le labrador")
        chapter = ChapterTest.objects.create(user=user1, book=book, number=1)
        
        # update book/chapter for Igor.
        update_related_field(book, user2.id, "user")

        updated_book = user2.booktest_set.all()[0]
        updated_chapter = user2.chaptertest_set.all()[0]
                
        # page will not be updated because fieldname is different.
        page = PageTest.objects.create(author=user2, book=book, 
            chapter=updated_chapter, number=1)
        
        
        # update book/chapter for John.
        update_related_field(updated_book, user1.id, "user")
        
        self.assertEquals(user2.booktest_set.all().count(), 0)        
        self.assertEquals(user1.booktest_set.all().count(), 1)

        self.assertEquals(user2.chaptertest_set.all().count(), 0)
        self.assertEquals(user1.chaptertest_set.all().count(), 1)

        self.assertEquals(user2.pagetest_set.all().count(), 1)
        self.assertEquals(user1.pagetest_set.all().count(), 0)
