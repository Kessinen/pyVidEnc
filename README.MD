# Video file encoder

## Description

This is a small helper program to encode videos with certain settings:

- Video codec: AV1
- Audio codec: Opus
- Metadata: Title, Release date, IMDB ID
- SAR 1:1
- Filename: Title.Year.mkv

I like to have my video library in a certain format. For video codec I like to use AV1 and for audio Opus. Also metadata should contain certain information. This all sounds pretty straightforward, but a few things complete the job. For example, when coding audio as Opus, FFMPEG has a "bug" when handling side loaded surround audio with libopus. It has to be mapped manually. So every audio stream has to be checked if it is sideloaded and surround. A lot of times there are multiple audio streams. Some sideloaded surround and some stereo. Anamorphic video, that DVDs use, is another problem. I like to have SAR 1:1 so the correct resolution has to be calculated on a videofile basis.

A long time I used HandBrake for this, but I couldn't band it to my prefferred settings so I decided to code one my self. Doing this all by hand is a lot of work and has a high probability of error.

