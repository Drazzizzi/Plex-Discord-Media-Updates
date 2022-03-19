# -*- coding: utf-8 -*-
import re
import sys
from collections import Counter
from datetime import datetime
from dhooks import Webhook, Embed
from plexapi.server import PlexServer

'''
------------------------------------------------------------------------------
PURPOSE

This script is meant to check your plex server, retrieve lists of
shows and movies that are in the Recently Added sections, count and
format them nicely, and then output to a message via discord webhook.

If the lists of media (one for Movies and one for TV) are longer than
discord's max message length (currently set as 4096 chars but can be changed
in the "USER OPTIONS" section below), they will be cut down to size.

i.e: If the sum of the length of both lists is over the
max length, they will each be trimmed down to half of the max size.

The script is meant to be run on a schedule (e.g. via crontab or unraid
user scripts). By default, it should be run every 24 hours, but if you
prefer to run it at a different interval, be sure to change the
lookback_period variable in the "USER OPTIONS" section below.

To get the script working with minimal configuration, you will need to change
these variables (plex_url, plex_token, webhook_url) to match your plex/discord
info; they're in the "USER OPTIONS" section below.

NOTE: Do not set the lookback_period variable to be too far back, or the list
of media may be cut off.

------------------------------------------------------------------------------
DEPENDENCIES

This script requires:
- Python 3 (might work with Python 2 but I haven't done any testing)

Along with the Python modules for:
- PlexAPI
- dhooks
The modules can be installed by executing the command:
pip3 install plexapi dhooks

------------------------------------------------------------------------------
CHANGELOG

~ v1.1 - 2022-03-19
- Made it so that in case there are too many recently added shows/movies,
the list(s) will automatically be trimmed down to a size that can still be
sent via webhook. Before, if one or both lists were too long, the webhook
message would simply fail and not get sent.

~ v1.0 - 2022-03-17
- Initial build
------------------------------------------------------------------------------
'''
start_time = datetime.now()

# BEGIN USER OPTIONS ---------------------------------------------------------

plex_url = ""
plex_token = ""
movie_library = "Movies"
tv_library = "TV Shows"
webhook_url = ""

# Media added since this long ago will be listed.
# FORMAT: "1m", "1h", "1d", "1w" respectively
# correspond to 1 minute, 1 hour, 1 day, 1 week.
lookback_period = "24h"

# Skipped libraries will not be scanned or included in the webhook message
skip_movies = False
skip_tv = False

# Choose whether to show the total number of
# new episodes in the TV Show embed title
show_total_episodes = True

# Choose whether to show the number of new episodes
# for each individual show in the TV Show embed title.
show_individual_episodes = True

# Will be bolded and put on its own line,
# the loockback period will be appended to the end
message_title = "Additions/updates to the media library from the last"

# Thumbnail that will go in all embeds - OPTIONAL
# Set to an empty string ("") to disable it.
# Set to a direct image url string to enable it.
embed_thumbnail = ""

# The symbol to denote each new entry in the lists in the embeds
# Can be replaced with emotes (e.g. :point_right:)
bullet = "•"

# Keep the "0x" and change the last 6 characters
# to the hex codes of your preferred colours.
movie_embed_colour = 0xFB8800
tv_embed_colour = 0xDE4501

# Emotes to be used in the title for each embed - OPTIONAL
# Set these to empty strings ("") to disable
movie_emote = ":clapper:"
tv_emote = ":tv:"

# The max length for discord embed media_lists (it's technically
# 4096, but we need some headroom for max_length_exceeded_msg)
message_max_length = 4000

# The message that will display if a list is too long and needs to be cut
# short. Should be less than 90 characters. Will be bolded and appended with
# two newlines to the end of the list.
max_length_exceeded_msg = "We couldn't fit all of the new media in one message, so check out the library for the rest!"

# END USER OPTIONS -----------------------------------------------------------


# HELPER FUNCTIONS -----------------------------------------------------------
def cleanYear(media):
    """
    Takes a Show/Movie object and returns the title of it with the year
    properly appended. Prevents media with the year already in the title
    from having duplicate years. (e.g., avoids situations like
    "The Flash (2014) (2014)").

    Arguments:
    media -- a Show/Movie object
    """
    title = ""
    # year_regex matches any string ending with a year between 1000-2999 in
    # parentheses. e.g. "The Flash (2014)"
    year_regex = re.compile(".*\([12][0-9]{3}\)$")
    title += media.title
    if not year_regex.match(media.title):
        title += " (" + str(media.year) + ")"
    return title


def trimOnNewlines(long_string, max_length):
    """
    Takes a long multi-line string and a max length, and returns a subsection
    of the string that's the max length or shorter, that ends before a newline.

    Arguments:
    long_string -- string; any string with a newline character
    max_length -- integer; denotes the max length to trim the string down to
    """
    if len(long_string) > max_length:
        end = long_string.rfind("\n", 0, max_length)
        return long_string[:end] + max_length_exceeded_msg
    else:
        return long_string + max_length_exceeded_msg


def createEmbeds(embed_title, embed_description, embed_color, max_length):
    """
    Creates an embed with data from the given arguments, but modifies the
    description of the embed so be below a given amount of characters. Will
    only trim the embed at the end of a line to avoid partial lines, while
    still keeping the description below max_length.

    Arguments:
    embed_title -- title for the embed
    embed_description -- description for the embed
    embed_color -- colour for the embed
    max_length -- integer; the max length for the embed's description
    """
    if len(embed_description) > max_length:
        embed_description = trimOnNewlines(embed_description, max_length)
    embed = Embed(
        title=embed_title,
        description=embed_description,
        color=embed_color)
    webhook_embeds.append(embed)

# Formatting strings from user variables section
bullet += " "
max_length_exceeded_msg = "\n\n**" + max_length_exceeded_msg + "**"
# Checks whether the lookback period should be specified
# in plural and makes the message text look more natural.
period_dict = {
    "m": "minute",
    "h": "hour",
    "d": "day",
    "w": "week",
}
if lookback_period[:-1] == "1":
    lookback_text = period_dict[lookback_period[-1]]
else:
    lookback_text = (lookback_period[:-1] + " " +
                     period_dict[lookback_period[-1]] + "s")
message_title = "_ _\n**" + message_title + " " + lookback_text + ":" "**"

plex = PlexServer(plex_url, plex_token)
webhook = Webhook(webhook_url)
webhook_embeds = []
media_lists = []

# Skips scanning libraries if specified
if not skip_movies:
    movies = plex.library.section(movie_library)
    # Retrieves all movies added since the start of the lookback period
    new_movies = movies.search(filters={"addedAt>>": lookback_period})
    # Raises a flag to skip the movie embed
    # creation/addition if there are no new movies
    if not new_movies:
        skip_movies = True
    else:
        # BUILDING MOVIE LIST ------------------------------------------------
        movies_str = bullet
        new_movies_formatted = [cleanYear(movie) for movie in new_movies]
        total_movies = len(new_movies_formatted)
        movies_str += ("\n" + bullet).join(new_movies_formatted)
        media_lists.append(movies_str)

        # Pluralizes "Movie" title string if appropriate
        movies_title_counted = " Movie"
        if total_movies != 1:
            movies_title_counted += "s"

        # Builds the Movies embed title
        movie_title = str(str(total_movies) + movies_title_counted +
                          "  " + movie_emote)
if not skip_tv:
    shows = plex.library.section(tv_library)
    # Retrieves all TV episodes added since the start of the lookback period
    new_episodes = shows.searchEpisodes(filters={"addedAt>>": lookback_period})
    # Raises a flag to skip the TV show embed
    # creation/addition if there are no new episodes
    if not new_episodes:
        skip_tv = True
    else:
        # BUILDING TV SHOW LIST ----------------------------------------------
        newShows = []
        for episode in new_episodes:
            # Cannot directly retrieve the Show object from the Episode object
            # so I'm using the workaround to search by unique RatingKey instead
            newShows.append(cleanYear(
                            plex.fetchItem(episode.grandparentRatingKey)))

        # Counts the duplicates and builds the
        # properly-formatted list with episode counts
        counted_shows = Counter(newShows)
        show_list = []
        total_episodes = 0

        # Loops through the dictionary of shows with their counts
        for counted_show in counted_shows:
            # Retrieves the number of new episodes for the current show
            episode_count = counted_shows[counted_show]
            total_episodes += episode_count
            episodes_counted = " episode"
            # Pluralizes "episode" string if appropriate
            if episode_count != 1:
                episodes_counted += "s"
            if show_individual_episodes:
                show_list.append(bullet + counted_show + " - " +
                                 "*" + str(episode_count) + episodes_counted +
                                 "*")
            else:
                show_list.append(bullet + counted_show)
        show_list.sort()
        total_shows = len(show_list)
        tv_str = "\n".join(show_list)
        media_lists.append(tv_str)

        # Pluralizes "TV Show" and "Episode" title strings if appropriate
        show_title_counted = " Show"
        episode_title_counted = " Episode"
        if total_shows != 1:
            show_title_counted += "s"
            episode_title_counted += "s"

        if show_total_episodes:
            # Builds the TV Shows embed title with the episode count
            tv_title = (str(total_shows) + show_title_counted + " / " +
                        str(total_episodes) + episode_title_counted + "  " +
                        tv_emote)
        else:
            # Builds the TV Shows embed title
            tv_title = (str(total_shows) + show_title_counted +
                        "  " + tv_emote)

# BUILDING EMBEDS -----------------------------------------------------------
list_count = len(media_lists)
if ((sum([len(descr) for descr in media_lists]) < message_max_length)):
    # Sets to max message length if the sum of both lists is less than it
    embed_length = message_max_length
else:
    # Sets to max message length if there is only one list.
    # Otherwise divides the total embed length by however many lists there are.
    embed_length = message_max_length // list_count

if not skip_movies:
    createEmbeds(movie_title, movies_str, movie_embed_colour, embed_length)
if not skip_tv:
    createEmbeds(tv_title, tv_str, tv_embed_colour, embed_length)

# Adds thumnail image to embeds if specified
[embed.set_thumbnail(embed_thumbnail) for embed in webhook_embeds]

# SENDING WEBHOOK -----------------------------------------------------------
if webhook_embeds:
    try:
        webhook.send(message_title, embeds=webhook_embeds)
        print("Library update message sent.")
    except Exception as err:
        print("There was an error sending the message:", err)
else:
    print("No new/specified media to notify about - message not sent.")

end_time = datetime.now()
curr_date = end_time.isoformat()[0:10]
curr_time = end_time.isoformat()[11:19]
run_time = (end_time - start_time).total_seconds()
print("Script completed at", curr_time, "on", curr_date +
      ". Runtime (in seconds):", str(run_time))
