import os
import django



def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")


    if 'setup' in dir(django):
        django.setup()

    from books.models import Book

    try:
        with open('./books.csv', 'r') as f:

        # skip the header
            for line in f.readlines()[1:]:
                try:
                    _, title, authors, rating, isbn, isbn13, language, pages, _, _, publication_date, publisher = line.split(',')
                    # format publication_date from to  YYYY-MM-DD
                    publication_date = publication_date.split('/')[2] + '-' + publication_date.split('/')[0] + '-' + publication_date.split('/')[1]


                except ValueError:
                    print('Error parsing line: {}'.format(line))
                    continue

                try:
                    book = Book.objects.create(
                        title=title,
                        authors=authors,
                        rating=rating,
                        isbn=isbn,
                        isbn13=isbn13,
                        language=language,
                        pages=pages,
                        publication_date=publication_date,
                        publisher=publisher
                    )
                    print(book.title + ' created')

                except Exception as e:
                    print('Error creating book: {}'.format(e))
                    continue

            print(f'Created {Book.objects.count()} books')




    except Exception as e:
        print(f"{e!r}")


if __name__ == "__main__":
    main()

