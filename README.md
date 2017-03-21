# Better MM

A Better* Google Music Manager

## Process

1. User feeds in music dir
2. User feeds in date since last added (if any)
3. Program lazy searches through dir recursively for flacs, mp3s
    i. Iterator built
4. Program only takes files which are newer (if 'date added' given)
    i. Otherwise all files considered
5. Repeat steps 3 and 4 for each dir given
6. Pipe iterator(s) into gmusic music manager upload
    i. Happens after oauth with google account
