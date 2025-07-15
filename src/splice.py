import csv
from moviepy.editor import VideoFileClip, concatenate_videoclips


csv_file = "HandS_DEMO.csv"
play_timestamps = []
current_state = None
current_count = 0
start_frame = None

with open(csv_file, newline="") as f:
    reader = csv.DictReader(f)
    for idx, row in enumerate(reader):
        state = row["game_state"]
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

# Detect short NO-PLAY segments between PLAY intervals
# Increase threshold here if you want to allow longer gaps (e.g., 90 for 3 seconds)
NOPLAY_THRESHOLD = 150  # frames
PLAY_THRESHOLD = 30  # frames

false_no_play_segments = []
false_play_segments = []

true_play_segments = []

for i in range(len(play_timestamps)):
    start, end = play_timestamps[i]
    length = end - start + 1

    # Calculate gaps before and after this PLAY segment
    gap_before = play_timestamps[i][0] - play_timestamps[i-1][1] - 1 if i > 0 else None
    gap_after = play_timestamps[i+1][0] - play_timestamps[i][1] - 1 if i < len(play_timestamps) - 1 else None

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

FPS = 30  # frames per second
MARGIN = 2 * FPS  # 2 seconds = 60 frames

# Step 1: Adjust each segment
adjusted_segments = []
for start, end, length, gap_before, gap_after in true_play_segments:
    new_start = max(0, start - MARGIN)
    new_end = end + MARGIN + 30 # Extend by 30 frames to ensure we capture the full segment
    adjusted_segments.append((new_start, new_end))

# Step 2: Merge overlapping or adjacent segments
merged_segments = []
adjusted_segments.sort()  # Ensure segments are sorted by start time

for seg in adjusted_segments:
    if not merged_segments:
        merged_segments.append(seg)
    else:
        last_start, last_end = merged_segments[-1]
        current_start, current_end = seg

        if current_start <= last_end + 1:  # Overlapping or adjacent
            merged_segments[-1] = (last_start, max(last_end, current_end))
        else:
            merged_segments.append(seg)

# Step 3: Print final merged segments
print("\nFinal Merged True PLAY Segments (with ±2s margin):")
for start, end in merged_segments:
    duration = end - start + 1
    print(f"Segment from {start/FPS:.2f}s to {end/FPS:.2f}s ({duration} frames)")

# Path to original video
input_video_path = "data/videos/HandS.mp4"
output_video_path = "spliced_output.mp4"
FPS = 30  # Assuming same FPS used earlier

# Your merged_segments list: (start_frame, end_frame)
# Example:
# merged_segments = [(900, 1800), (2500, 3000)]

# Convert frame numbers to seconds
time_segments = [(start / FPS, end / FPS) for start, end in merged_segments]

# Load the video
video = VideoFileClip(input_video_path)

# Extract clips
clips = [video.subclip(start, end) for start, end in time_segments]

# Concatenate and export
final_video = concatenate_videoclips(clips)
final_video.write_videofile(output_video_path, codec="libx264", audio_codec="aac")