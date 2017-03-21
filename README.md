# Better MM

### A better* Google Music Manager

## Process

1. User feeds in music dr
2. User feeds in date since last added (if any)
3. Program lazy searches through dir recursively for flacs, mp3s
    - Iterator built
4. Program only takes files which are newer (if 'date added' given)
    - Otherwise all files considered
5. Repeat steps 3 and 4 for each dir given
6. Pipe iterator(s) into gmusic music manager upload
    - Happens after oauth with google account


\* says me

