## API flow

This api backend is a simple example of using HATEOAS and a couple other
design patterns. First of all, everything has a unique ID here, even two
(uid set on creation, mid changes on every modification) which can be
considered extremely long timestamps and everything that has name also has a
slug. Thus, whenever slug is present it's used in the urls otherwise uid is
used (it looks like uuid and can be handled by uuid-optimized tools but
doesn't share some standard uuid issues, like this ids aare alphabetically
sortable by creation/modification time). JSON (or otherwise encoded) content
is served raw, without any enveloping, with any metadata required sent in
headers, most notably Link header is used for pagination and other links.

As you have probably already guessed, most of the relations are represented
in the as urls (among other things it could make client-side caching easier).
But only where it makes sense, notably order endpoint uses nested format.

There are not authentication/authorization and almost no validation. Models and
api endpoints structure were the focus of this work. Most of the api code is
default, only a couple things are custom.

## Boring notes

Ok, this project is not made for a real business, rather it's designed based
on my own opinions about what such a project needs.

Many of the things here are stubs to be possibly finished later if I decide to
reuse them, some are ideas I worked on for a long time but never implemented
yet. Feel free to reuse them if you like, however this project might not show
you their final version.

As this was an exercise project I only run this in local shell with runserver
so the things having to do with deployment are not quite polished. However,
even if something doesn't quite work, it can be made to work in little to no
time should the need ever arise.

Yeah, I used cookiecutter-django for scaffolding, it created a few things that
are not currently utilized and I'm lazy to clean them up (besides, I might need
them if I decide to do any further development).
