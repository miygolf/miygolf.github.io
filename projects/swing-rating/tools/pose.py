#!/usr/bin/env python3
# MediaPipe Pose Landmarker (heavy, VIDEO mode) on every source frame (work/f/c<i>_###.jpg, 540x960) -> edit/pose.json
# landmarks in normalised image coords of the upright frame; t = (frame-1)/59.94
import json, glob, sys
import mediapipe as mp
from mediapipe.tasks import python as mpt
from mediapipe.tasks.python import vision
opts = vision.PoseLandmarkerOptions(base_options=mpt.BaseOptions(model_asset_path="work/pose_heavy.task"),
                                    running_mode=vision.RunningMode.VIDEO, num_poses=1,
                                    min_pose_detection_confidence=0.5, min_tracking_confidence=0.5)
out = {}
for i in (1, 2, 3, 4):
    lm = vision.PoseLandmarker.create_from_options(opts)
    fr = []
    for k, p in enumerate(sorted(glob.glob(f"work/f/c{i}_*.jpg"))):
        img = mp.Image.create_from_file(p)
        r = lm.detect_for_video(img, int(k * 1000 / 59.94))
        fr.append([[round(q.x, 4), round(q.y, 4), round(q.visibility, 3)] for q in r.pose_landmarks[0]] if r.pose_landmarks else None)
    out[f"clip{i}"] = fr
    print(i, len(fr), sum(f is None for f in fr), flush=True)
json.dump(out, open("edit/pose.json", "w"))
