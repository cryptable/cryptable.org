#Introduction

Here we explain the blog API design.

## Articles
The articles are written in plain markdown. Which means the text stored in the database is just markdown text.

### Rendering the blog
Rendering of the blog is done in the browser using a SPA written in Angular.

### Handling pictures
Pictures will be uploaded and linked using standard HTML links. Uploading the pictures are another part of the API, 
which don't belong to the article API.

### Data needed to Create an Article

Main data of the API:

1) Markdown text of the article
2) Title of the article
3) Optionally: summary

Indirect information will be:

- Author: person logged on
- Date of last editing

Idea: Use github to store the history article.

#### Data model

| Column | Type | Description |
|--------|------|-------------|
| title | varchar(100) | Title of the article |
| summary | varchar(250) | Small summary or extract of the article |
| article | Text | The article itself |
| author | varchar(128) | Name of the author as known in the Authentication DB |
| updated | Date | Last update on the article |
| created | Date | Date when the article was initially written |
| owner | Foreign Key(auth table) | Author of the Article according to Auth DB |

#### API interface

##### Create articles
POST: /articles
```
{
    "title": <string>,
    "summary": <string>,
    "article": <string>
}
```

##### List articles
GET: /articles

```

```

#### Tests

##### Preparation

```
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
```
##### manual Article model test

Create a user 'david'

```
from django.contrib.auth.models import User
u = User.objects.get(username='david')
from blog.models import Article
article = Article(title='Test', summary='Test Article', article='This is a test Article', owner=u)
article.save()
```