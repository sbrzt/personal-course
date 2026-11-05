# Local data

Git ignores everything in this folder except this file. Put here any data you want to use in a notebook without committing it.

The Bibliothecae.it tables do not need to be here: they ship with the course, in `course/resources/bibliothecae/`, and `course.data.bibliothecae()` loads them. To load another version of them instead (for example an updated export), pass its folder or zip to `course.data.bibliothecae(path)`, or set the environment variable `BIBLIOTHECAE_DATA` to it.
