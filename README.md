 # Plex-Discord Media Updates

This is a customizable python script that will send plex library updates to your discord server via webhook. Including listing the titles and release years of all new shows/movies added within a configurable time period, it can also count the amount and includes them in its embed titles, as well as count the episodes of each show and total episodes overall - see the screenshots section for examples. 

Furthermore, if there are too many movies or shows to be listed (discord has a max of ~4000 characters across embeds in a single message), instead of failing to send the message, the script will automatically truncate the lists so that the message can be sent.

*Note: As this is just a python script, you will need to schedule it to run using a scheduler available on your operating system. See the `Running the Script` section for more info.*

# Screenshots

In the screenshots below (media titles and release years are redacted), notice how the title changes to naturally reflect your preferred recently-added search period:

24-hour update:  
![](https://user-images.githubusercontent.com/44678543/159141632-db133f53-7858-4976-ba12-e2a21fe61590.png)

<details><summary>Click to expand preview for 3-day update</summary>

![](https://user-images.githubusercontent.com/44678543/159141135-09863ac3-bf8c-4402-8e23-c51ee8c2c18f.png)

</details>
<details><summary>Click to expand preview for 1-week update</summary>

Notice that lists that are too long will be automatically truncated and an additional message will be appended to let users know. This is to prevent the webhook from failing to send.
  
![](https://user-images.githubusercontent.com/44678543/159141139-b64742eb-0d6a-42a2-92e3-9f2d503e37ea.png)

</details>

# Prerequisites

This script requires Python 3, as well as the python modules outlined in `pip_requirements.txt`. From the same folder as this file, the modules can be installed via the command:

`pip3 install -r pip_requirements.txt`


# Configuration

All configuration and customizations are now done via the configuration file `config.yml` instead of via editing the python script itself.

## Basic Settings

To be able to run this script with minimal configuration, these fields must be set in the configuration file:

`plex`>`url` ~ Your plex URL. Defaults to `https://localhost:32400`.

`plex`>`token` ~ Your plex token.

`plex`>`libraries`>`movies` ~ The name of your Movies library in plex. Defaults to `Movies`.

`plex`>`libraries`>`shows` ~ The name of your TV Show library in plex. Defaults to `TV Shows`. 

`plex_discord_media_updates`>`webhook` ~ Your discord webhook URL.

Once these fields are set, running the script without changing the additional fields below will generate an output similar to the screenshots.

## Advanced Customization

These are additional fields for optional customizations, listed along with their default values. All of these additional settings are in the `plex_discord_media_updates` section of the configuration file.

---

`lookback_period` = `24h`

Media added since this long ago will be listed. It can be configured to be a set amount of minutes, hours, days, or weeks.  
Format/Examples: `4m`, `3h`, `2d`, and `1w` are all separately available options that respectively correspond to 4 minutes, 3 hours, 2 days, and 1 week.

> Note: Don't set this to be too long; if the lists contain enough titles to exceed discord's character limit, they will be truncated.

---

`skip_libraries`>`movies` = `False`  
`skip_libraries`>`shows` = `False`

Skipped libraries (if set to `True`) will not be scanned or included in the webhook message.  

---

`show_total_episode_count` = `True`

Choose whether to show the total number of new episodes in the TV Show embed title

---

`show_episode_count_per_show` = `True`

Choose whether to show the number of new episodes for each individual show in the TV Show embed.

---

`message_options`>`title` = `Additions/updates to the media library from the last`

The overall message caption that will go before the embeds. It will be bolded and put on its own line, and the lookback period will be appended to the end - see the screenshots for examples.  

---

`embed_options`>`thumbnail` = `""`

Optional thumbnail that will go in all embeds. Set to an empty string `""` to disable it. Set to a direct image URL to enable it.

---

`embed_options`>`bullet` = `"•"`

The symbol to denote each new entry in the lists in the embeds. Can be replaced with emotes (e.g. :point_right:)

---

`embed_options`>`movies_colour` = `0xFB8800`  
`embed_options`>`shows_colour` = `0xDE4501`

The colours for the embeds (the coloured line along the left side of each embed - see the screenshots section for examples). Keep the `0x` and change the last 6 characters to the hex codes of your preferred colours.  

---

`movie_emote` = `":clapper:"`  
`shows_emote` = `":tv:"`

Optional emotes that will be appended to the title of each embed - see the screenshots for examples. Set them to empty strings `""` to disable them. 
> NOTE: You MUST encapsulate these in quotes if using emotes (or colons).  

---

`overflow_footer` = `We couldn't fit all of the new media in one message, so check out the library for the rest!`

The message that will display if a list is too long and needs to be truncated. If you change this, ensure that it is less than 90 characters in length. It will automatically be bolded and appended with two newlines to the end of a truncated list. See the embeds in the 1-week screenshot in the `Screenshots` section for an example.  

## Uptime Status Monitoring

The configuration file also includes an *optional* field `uptime_status` to allow the pinging of an uptime status push monitor (e.g. *push monitors* in Uptime Kuma or Healthchecks.io). To ensure the script is actually run on a regular schedule, it will ping a URL given by your instance of one of these services, which will keep the monitor marked as running/up in your service. If the script is not run, it will miss its scheduled check-in and the service can alert you to it.

# Running the Script

The python script is meant to be scheduled and run on a regular basis; its `lookback_time` variable should be set to match that schedule. The default configuration has it scanning your plex library for new media added within the last 24 hours. Therefore, an appropriate schedule would be to run the script every 24 hours. This can be achieved via crontab, systemd timers, or the user scripts plugin if you're on unraid.

