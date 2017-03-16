# Better MM

## A better Google Music Manager

### Process

- Recursively search through file structure for files that:
	- End in .mp3 or .flac
	- Have a modification date (maybe import date?) after given timestamp

- Build list of these files with absolute filepaths
- Feed list into gmusicapi from github (music manager api)
