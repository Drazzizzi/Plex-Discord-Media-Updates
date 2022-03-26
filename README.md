 # PlexDiscordUpdates

This is a customizable python script that will send plex library updates to your discord server via webhook. Including listing the titles and release years of all new shows/movies added within a configurable time period, it can also count the amount and includes them in its embed titles, as well as count the episodes of each show and total episodes overall - see the screenshots section for examples. 

Furthermore, if there are too many movies or shows to be listed (discord has a max of ~4000 characters), instead of faiing to send the message, the script will automatically trim the lists so that the message can be sent.

# Screenshots

In the screenshots below, notice how the title changes to naturally reflect your preferred recently-added search period:

24-hour update:  
![](https://user-images.githubusercontent.com/44678543/159141632-db133f53-7858-4976-ba12-e2a21fe61590.png)

<details><summary>Click to expand preview for 3-day update</summary>

![](https://user-images.githubusercontent.com/44678543/159141135-09863ac3-bf8c-4402-8e23-c51ee8c2c18f.png)

</details>
<details><summary>Click to expand preview for 1-week update</summary>

Notice how for lists that are too long, they get trimmed with an additional message at the bottom of each embed to let users know.
  
![](https://user-images.githubusercontent.com/44678543/159141139-b64742eb-0d6a-42a2-92e3-9f2d503e37ea.png)

</details>

# Pre-Requisites

This script requires the external python modules `PlexAPI` and `dhooks`, which can be installed via pip:

`pip3 install plexapi dhooks`


# Configuration

These settings can all be set/customized in a clearly denoted `USER OPTIONS` section of PlexDiscordUpdates.py, marked by `BEGIN USER OPTIONS` and `END USER OPTIONS` dividers.

## Basic Settings

To be able to run this script with minimal configuration, these variables need to be set:

`plex_url` - Your plex URL

`plex_token` - Your plex token

`movie_library` - The name of your Movies library in plex. Defaults to `Movies`.

`tv_library` - The name of your TV Show library in plex. Defaults to `TV Shows`. 

`webhook_url` - Your discord webhook URL

Running the script without changing the additional variables below will generate an output similar to the screenshots.

## Additional Customization

These are additional variables along with their default values.

`lookback_period = "24h"` - Media added since this long ago will be listed. It can be configured to be a set amount of minutes, hours, days, or weeks.  
Format/Examples: `"4m"`, `"3h"`, `"2d"`, and `"1w"` are all separately available options that respectively correspond to 4 minutes, 3 hours, 2 days, and 1 week.

> Note: Don't set this to be too long or some of the media in these lists will be skipped.

`skip_movies = False` | `skip_tv = False` - Skipped libraries will not be scanned or included in the webhook message

`show_total_episodes = True` - Choose whether to show the total number of new episodes in the TV Show embed title

`show_individual_episodes = True` - Choose whether to show the number of new episodes for each individual show in the TV Show embed title.

`message_title = "Additions/updates to the media library from the last"` - The overall message caption that will go before the embeds. It will be bolded and put on its own line, and the loockback period will be appended to the end - see the screenshots for examples.

`embed_thumbnail = ""` - Optional thumbnail that will go in all embeds. Set to an empty string `""` to disable it. Set to a direct image url string to enable it.

`bullet = "•"` - The symbol to denote each new entry in the lists in the embeds. Can be replaced with emotes (e.g. :point_right:)

`movie_embed_colour = 0xFB8800` | `tv_embed_colour = 0xDE4501` - The colours for the embeds (the coloured line on the left side of each embed - see the screenshots section for examples). Keep the `0x` and change the last 6 characters to the hex codes of your preferred colours.

`movie_emote = ":clapper:"` | `tv_emote = ":tv:"` - Optional emotes that will be appended to the title of each embed - see the screenshots for examples. Set them to empty strings `""` to disable them.

`message_max_length = 4000` - The max length that embeds can reach before they become unsendable (it's technically 4096, but we need some headroom for `max_length_exceeded_msg`)

`max_length_exceeded_msg = "We couldn't fit all of the new media in one message, so check out the library for the rest!"` - The message that will display if a list is too long and needs to be cut short. Should be less than 90 characters. Will be bolded and appended with two newlines to the end of the list. See the bottom of the 1-week screenshot in the `Screenshots` section for an example.

# Running the Script

The python script is meant to be scheduled and run on a regular basis, and to have its `lookback_time` variable be set to match that schedule. The default setting has it scanning your plex library and sending discord messages every 24 hours; if you intend to keep it that way, an appropriate schedule for this would be to have it run every 24 hours. This can be achieved via crontab, systemd timers, or if you're on unraid, you can use the user scripts plugin.

# Uptime Kuma Add-On Script

To ensure the script is actually run on a regular schedule, I have incorporated it into my Uptime Kuma setup via a bash script, and instead of a ping time, I've configured the script to send its execution time in seconds. You can do this too with the `PlexDiscordUpdates.sh` add-on script. Create a `Push` monitor in Uptime Kuma, set the heartbeat interval to 86520 seconds or just over a day (or a couple minutes over your scheduled interval if you're not using 24 hours), copy the Push URL, and then hit save. Then open up `PlexDiscordUpdates.sh` and set the variables as such:

`PlexDiscordUpdates` - The path to the PlexDiscordUpdates.py script
`PingURL` - The Push URL from your Uptime Kuma monitor

Then hit save and you're done. Now instead of calling the python script, you'd call the bash script via your preferred method of scheduling.
