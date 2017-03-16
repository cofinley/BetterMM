recursively search through file structure for files that:
	end in .mp3 or .flac
	have a modification date (maybe import date?) after given timestamp

build list of these files with absolute filepaths
feed list into gmusicapi from github (music manager api)
