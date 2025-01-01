from django.db import models


class Author(models.Model):
    id = models.AutoField(primary_key=True)
    birth_year = models.SmallIntegerField(null=True, blank=True)
    death_year = models.SmallIntegerField(null=True, blank=True)
    name = models.CharField(max_length=128)

    class Meta:
        db_table = "books_author"
        managed = False  # Django will not manage this table


class Book(models.Model):
    # id = models.AutoField(primary_key=True)
    download_count = models.IntegerField(null=True, blank=True)
    gutenberg_id = models.IntegerField()
    media_type = models.CharField(max_length=16)
    title = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        db_table = "books_book"
        managed = False
        indexes = [
            models.Index(fields=['gutenberg_id']),
        ]


class BookAuthors(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column="book_id")
    author = models.ForeignKey(Author, on_delete=models.CASCADE, db_column="author_id")

    class Meta:
        db_table = "books_book_authors"
        managed = False


class Bookshelf(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=64)

    class Meta:
        db_table = "books_bookshelf"
        managed = False
        indexes = [
            models.Index(fields=['name']),  
        ]


class BookBookshelves(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column="book_id")
    bookshelf = models.ForeignKey(Bookshelf, on_delete=models.CASCADE, db_column="bookshelf_id")

    class Meta:
        db_table = "books_book_bookshelves"
        managed = False


class Language(models.Model):
    id = models.AutoField(primary_key=True)
    code = models.CharField(max_length=4)

    class Meta:
        db_table = "books_language"
        managed = False
        indexes = [
            models.Index(fields=['code']),  
        ]
    def __str__(self) -> str:
        return f"{self.code}"


class BookLanguages(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column="book_id")
    language = models.ForeignKey(Language, on_delete=models.CASCADE, db_column="language_id")

    class Meta:
        db_table = "books_book_languages"
        managed = False


class Subject(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=256)

    class Meta:
        db_table = "books_subject"
        managed = False


class BookSubjects(models.Model):
    id = models.AutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column="book_id")
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, db_column="subject_id")

    class Meta:
        db_table = "books_book_subjects"
        managed = False


class Format(models.Model):
    id = models.AutoField(primary_key=True)
    mime_type = models.CharField(max_length=32)
    url = models.CharField(max_length=256)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, db_column="book_id")

    class Meta:
        db_table = "books_format"
        managed = False
