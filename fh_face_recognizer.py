from deepface import DeepFace
from scipy.spatial.distance import cosine
import numpy as np

class FaceRecognizer:
    """Recognizes faces in video frames using FaceNet model via DeepFace."""
    def __init__(self, reference_embedding):
        self.reference_embedding = np.array(reference_embedding)
        self.model_name = 'FaceNet'

    def find_matches(self, frame_generator, threshold=0.4, fps=30):
        """ Compare frames with reference embedding using cosine distance. (0.3-0.4 strict, 0.5-0.6 permissive) """
        matches = []
        frame_idx = 0
        processed = 0
        skipped = 0

        print("Starting face recognition...")
        print(f"Using threshold: {threshold} (cosine distance)")

        for batch in frame_generator:
            for frame in batch:
                try:
                    result = DeepFace.represent(frame, model_name = self.model_name, enforce_detection = False)

                    frame_has_match = False

                    for face_data in result:
                        frame_embedding = np.array(face_data['embedding'])
                        distance = cosine(self.reference_embedding, frame_embedding)

                        if distance < threshold:
                            frame_has_match = True
                            break

                    if frame_has_match:
                        minutes = int(timestamp_seconds // 60)
                        seconds = int(timestamp_seconds % 60)

                        matches.append({
                            'frame_index': frame_idx,
                            'timestamp': f"{minutes:02d}:{seconds:02d}"
                        })
                        print(f"Match at frame {frame_idx} ({minutes:02d}:{seconds:02d})")

                    processed += 1

                    if processed % 100 == 0:
                        print(f"Progress: {processed} frames, {len(matches)} matches")

                except Exception as e:
                    skipped += 1
                    if skipped % 50 == 0:
                        print(f"Warning: {skipped} frames skipped")

                frame_idx += 1

        print("=" * 60)
        print(f"Recognition complete: {len(matches)} matches")
        print("=" * 60)

        return matches






