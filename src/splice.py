import csv
import subprocess
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

from datetime import timedelta

def seconds_to_hhmmss(seconds):
    return str(timedelta(seconds=int(seconds)))

def splice_long_video_from_seconds(input_path, output_path, segments):
    temp_dir = "temp_ffmpeg_clips"
    os.makedirs(temp_dir, exist_ok=True)

    temp_files = []

    for i, (start_sec, end_sec) in enumerate(segments):
        start = seconds_to_hhmmss(start_sec)
        end = seconds_to_hhmmss(end_sec)
        temp_out = os.path.join(temp_dir, f"clip_{i}.mp4")

        command = [
            "ffmpeg",
            "-ss", start,
            "-to", end,
            "-i", input_path,
            "-c:v", "libx264",
            "-c:a", "aac",
            "-preset", "fast",
            "-crf", "23",
            "-y",
            temp_out
        ]
        subprocess.run(command, check=True)
        temp_files.append(temp_out)

    # Create concat list
    list_path = os.path.join(temp_dir, "file_list.txt")
    with open(list_path, "w") as f:
        for file in temp_files:
            f.write(f"file '{os.path.abspath(file)}'\n")

    # Concatenate with ffmpeg
    concat_cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", list_path,
        "-c", "copy",
        output_path,
        "-y"
    ]
    subprocess.run(concat_cmd, check=True)

    # Cleanup
    for file in temp_files:
        os.remove(file)
    os.remove(list_path)
    os.rmdir(temp_dir)

    print(f"✅ Spliced video saved to: {output_path}")


csv_file = "20250804_100331000_iOS_DEMO.csv"
play_timestamps = []
current_state = None
current_count = 0
start_frame = None
row_count = 0
with open(csv_file, newline="") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader):
        state = row["game_state"]
        row_count+=1
        if state == "PLAY":
            if current_state != "PLAY":
                start_frame = idx
            current_state = "PLAY"
            current_count += 1
        else:
            if current_state == "PLAY" and current_count > 0:
                end_frame = idx - 1
                play_timestamps.append((start_frame, end_frame))
                current_count = 0
            current_state = state
    if current_state == "PLAY" and current_count > 0:
        end_frame = idx
        play_timestamps.append((start_frame, end_frame))
print(play_timestamps)
# Merge adjacent PLAY segments if they are within 6 seconds of each other
# Assuming 30 FPS, 5 seconds = 180 frames
merged_play_timestamps = []
for i in range(len(play_timestamps)):
    start, end = play_timestamps[i]
    length = end - start + 1

    if not merged_play_timestamps:
        merged_play_timestamps.append((start, end))
    else:
        last_start, last_end = merged_play_timestamps[-1]
        # Check if the current segment starts within 5 seconds (150 frames) of the last segment's end
        if start - last_end <= 180+1:
            # Merge them by extending the end of the last segment
            merged_play_timestamps[-1] = (last_start, max(last_end, end))
        else:
            merged_play_timestamps.append((start, end))
print(merged_play_timestamps)

# Detect short NO-PLAY segments between PLAY intervals
# Increase threshold here if you want to allow longer gaps (e.g., 90 for 3 seconds)
NOPLAY_THRESHOLD = 150  # frames
PLAY_THRESHOLD = 30  # frames

false_no_play_segments = []
false_play_segments = []

true_play_segments = []

for i in range(len(merged_play_timestamps)):
    start, end = merged_play_timestamps[i]
    length = end - start + 1

    # Calculate gaps before and after this PLAY segment
    gap_before = merged_play_timestamps[i][0] - merged_play_timestamps[i-1][1] - 1 if i > 0 else None
    gap_after = merged_play_timestamps[i+1][0] - merged_play_timestamps[i][1] - 1 if i < len(merged_play_timestamps) - 1 else None

    # A true PLAY segment must be longer than threshold and have long NO-PLAY gaps before and after
    is_true_play = (
        length >= PLAY_THRESHOLD and
        (gap_before is not None and gap_before > NOPLAY_THRESHOLD) and
        (gap_after is not None and gap_after > NOPLAY_THRESHOLD)
        
        or

        length >= 60
    )
    
    if is_true_play:
        true_play_segments.append((start, end, length, gap_before, gap_after))
    else:
        false_play_segments.append((start, end, length, gap_before, gap_after))

# print true play frame segments in seconds
print("True PLAY Segments (in frames):")
for start, end, length, gap_before, gap_after in true_play_segments:
    print(f"Segment from {start} to {end} ({length} frames), gap before: {gap_before}, gap after: {gap_after}")

print("\nFalse PLAY Segments (in frames):")
for start, end, length, gap_before, gap_after in false_play_segments:
    print(f"Segment from {start} to {end} ({length} frames), gap before: {gap_before}, gap after: {gap_after}")

FPS = 30  # frames per second
MARGIN = 5 * FPS  # 2 seconds = 60 frames

# # for adjacent segments, merge them if they are within 5 seconds of each other
# new_true_play_segments = []
# for i in range(len(true_play_segments) - 1):
#     start1, end1, length1, gap_before1, gap_after1 = true_play_segments[i]
#     start2, end2, length2, gap_before2, gap_after2 = true_play_segments[i + 1]

#     # Check if the segments are within 5 seconds (150 frames) of each other
#     # print(start2, end1)
#     if start2 - end1 <= 10 * FPS:
#         # Merge them by extending the end of the first segment
#         new_end = max(end1, end2)
#         new_true_play_segments.append((start1, new_end, new_end - start1 + 1, gap_before1, gap_after2))
#         # Remove the second segment
#         i+=1
#         # true_play_segments.pop(i + 1)
#     else:
#         new_true_play_segments.append((start1, end1, length1, gap_before1, gap_after1))





# Step 1: Adjust each segment
adjusted_segments = []
for start, end, length, gap_before, gap_after in true_play_segments:
    new_start = max(0, start - MARGIN)
    new_end = min(row_count,end + MARGIN) # Extend by 30 frames to ensure we capture the full segment
    adjusted_segments.append((new_start, new_end))

# Step 2: Merge overlapping or adjacent segments
merged_segments = []
adjusted_segments.sort()  # Ensure segments are sorted by start time

# print adjust segments
print("\nAdjusted True PLAY Segments (with ±2s margin):")
for start, end in adjusted_segments:
    duration = end - start + 1
    print(f"Segment from {start}s to {end}s ({duration} frames)")

for seg in adjusted_segments:
    if not merged_segments:
        merged_segments.append(seg)
    else:
        last_start, last_end = merged_segments[-1]
        current_start, current_end = seg
        print(last_start, last_end, current_start, current_end)
        if (current_start - last_end <= 60):  # Overlapping or adjacent
            print("merged", last_end, current_start)
            merged_segments[-1] = (last_start, max(last_end, current_end))
        else:
            merged_segments.append(seg)

# Step 3: Print final merged segments
print("\nFinal Merged True PLAY Segments (with ±2s margin):")
for start, end in merged_segments:
    duration = end - start + 1
    print(f"Segment from {start}s to {end}s ({duration} frames)")

# Path to original video
input_video_path = "data/videos/20250804_100331000_iOS.MOV"
# converted_video_path = "mp4.mp4"
final_video_path = "final_output.mp4"
FPS = 30  # Assuming same FPS used earlier

# Your merged_segments list: (start_frame, end_frame)
# Example:
# merged_segments = [(900, 1800), (2500, 3000)]

# Convert frame numbers to seconds
time_segments = [(start / FPS, end / FPS) for start, end in merged_segments]
splice_long_video_from_seconds(input_video_path, final_video_path, time_segments)

# Print time segments for debugging
# print("\nTime Segments (in seconds):")
# for start, end in time_segments:
#     print(f"Segment from {start} to {end}")
# Load the video
print(time_segments)
# convert_mov_to_mp4_moviepy(input_video_path,converted_video_path)
# video = VideoFileClip(input_video_path)

# # Extract clips
# # clips = [video.subclip(start, end) for start, end in time_segments]
# first_half_clips = [video.subclip(start, end) for start, end in time_segments[:len(time_segments)//2]]
# second_half_clips = [video.subclip(start, end) for start, end in time_segments[len(time_segments)//2:]]
# # Concatenate and export

# first_half_final_video = concatenate_videoclips(first_half_clips)
# second_half_final_video = concatenate_videoclips(second_half_clips)
# final_video = concatenate_videoclips([first_half_final_video, second_half_final_video])
# safe_duration = duration - 1 if duration else None
# if safe_duration:
#     final_video = final_video.set_duration(safe_duration)
# final_video.write_videofile(final_video_path, codec="libx264", audio_codec="aac")