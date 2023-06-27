#!/bin/bash

# Check if the argument was provided
if [ "$#" -ne 1 ]; then
    echo "Usage: ./convert_to_aif.sh <directory>"
    exit 1
fi

# Get the directory from the argument
dir="$1"

# Loop over wav files in the directory
for file in "$dir"/*.wav
do
  # Get the filename without the extension
  filename=$(basename "$file" .wav)

  # Convert wav to aif using ffmpeg with specific encoding options and normalize the volume
  ffmpeg -i "$file" -af loudnorm=I=-8:TP=0:LRA=25 -acodec pcm_s8 -ar 32000 -ac 1 "$dir/$filename.aif" -y
done