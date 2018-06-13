# Analysis script (Python 2.7) for the [microticks](https://github.com/scriptotek/microticks) package

Generates csv-like aggregated statistics for data gathered with microticks, as well as heatmaps. Comes with sample data.

## Requirements
The script can be used using the command-line terminal, with [Python 2.7](https://www.python.org/download/releases/2.7/) installed. It also requires the Python Imaging Library for heatmap generation [pillow](https://github.com/python-pillow/Pillow). 

## Usage

	processStats.py -i <inputfile> -f <first session id> -l <last session id> -h <name of home screen in ximpel app> [-s <comma separated list of session numbers to skip>]

## Example

### Output in command-line window

Generating statistics (which will be shown in the command-line terminal) with the sample data can be done as follows: 

	python microticks-analysis.py -i sample_stats.json -f 1327 -l 1429 -h main -s 1391,1392

Using the **-i** switch, we select the *sample_stats.json* file, the first (**-f**) session_id in the statistics file we look at is *1327*, and the last (-**l**) session-id is *1429*. The subject name of the initial screen of the application (**-h**) is *main*. Finally, we can optionally specify (**-s**) a comma-separated list of session_ids to skip.

*Output in text file*

We can also choose to output the statistics in a text file (*sample_stats.txt*), instead of in the command-line window (using the standard redirection feature of the terminal). This can be done as follows:

	python microticks-analysis.py -i sample_stats.json -f 1327 -l 1429 -h main -s 1391,1392 > sample_stats.txt

## Output

### Statistics

The script outputs a list of properties, in a space-separated format.

-**total_num_sessions** (total number of sessions)

-**screen_name num_clicks_incl_duplicates** (number of clicks per screen, also counting repeated clicks without subject changes)

-**screen_name num_clicks_excl_duplicates** (number of clicks on subjects, filtering out repeated clicks without subject changes)

-**session num_clicks_incl_duplicates** (number of clicks per session_id, also counting repeated clicks without subject changes)

-**session_id num_subjects_viewed** (number of clicks on subjects, filtering out repeated clicks without subject changes)

-**1st_selected_subj_in_session num_sessions** (first selected subject in a session)

-**2nd_selected_subj_in_session num_sessions** (second selected subject in a session)

-**3rd_selected_subj_in_session num_sessions** (third selected subject in a session)

-**date number_of_sessions** (number of unique sessions per date)

-**hour cumu_clicks_(incl_duplicates) num_sessions mean_clicks_incl_duplicates** (hour of the day, number of clicks (including duplicate clicks), number of unique sessions, mean number of clicks (including duplicate clicks)

-**screen_type clicks_(no_duplicates)** (number of clicks per screen type. The use of this statistic depends on the naming of the subjects - for instance, in *sample_stats.json* the format is *screen-type:content*)

-**day number_of_sessions** (number of unique sessions per day of the week)

-**resource total_num_page_changes total_num_clicks mean_viewed_pages_(2_per_page_change)** (e-book use, specifying the ebook, the number of page changes, the total number of clicks (unfiltered), and the mean number of viewed pages (2 pages are visible on one screen). The use of this statistic depends on the PDFviewer plugin for XIMPEL)

-**session num_page_changes num_viewed_pages** (number of page changes and viewed pages per session_id)

-**screen time_spent min_time_spent max_time_spent total_screen_open_count mean_seconds_in_screen** (the time spent per screen, including minimum and maximum time, mean number of seconds and how many times a screen has been opened)

-**TIME_PER_SCREEN** (the time spent in a screen, for each user - subject indicates the succession of screens opened (space-separated), while dur_sec indicates the number of seconds spent on each screen. Note that we can only measure the time spent on a screen if another screen is selected by a user (the screen before a time-out is indicated by -1).

-**ORDER_CLICKS_IN_SESSIONS** (for each session_id, the succession of opened screens)

### Heatmaps

In a folder with the name of the statistics file in use (e.g. sample_stats/), you'll find a png images with a heatmap for each screen in the application (which has had one or more views). These heatmaps are a visual depiction of the user interactions with each screen of the application (the [X,Y] values), and are projected on a white background.

![Resulting heatmap for the main screen of an application](/images/heatmap-main.png "Resulting heatmap for the main screen of an application")

Using an image editor, e.g. paint.net or the Gimp, it is possible to overlay a heatmap image on a screenshot of an application, to obtain a heatmap such as displayed below.

![Resulting heatmap for the main screen of an application](/images/heatmap-overlay.jpg "Resulting heatmap for the main screen of an application")