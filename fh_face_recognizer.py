from deepface import DeepFace
import numpy as np

class FaceRecognizer:
    """Recognizes faces in video frames using FaceNet model via DeepFace."""
    def __init__(self, reference_embedding):
        self.reference_embedding = np.array(reference_embedding)
        self.reference_norm = np.linalg.norm(self.reference_embedding)
        self.model_name = 'Facenet'

    def find_matches(self, frame_generator, threshold=0.4, fps=30, processable_frames=0):
        """ Compare frames with reference embedding using cosine distance. (0.3-0.4 strict, 0.5-0.6 permissive) """
        matches = []
        processed = 0
        skipped = 0

        print("Starting face recognition...")
        print(f"Using threshold: {threshold} (cosine distance)")
        for batch in frame_generator:
            for frame, frame_idx in batch:
                try:
                    result = DeepFace.represent(frame, model_name=self.model_name, enforce_detection=False)

                    if isinstance(result, dict):
                        result = [result]

                    frame_has_match = False

                    for face_data in result:
                        # Calculate cosine distance
                        frame_embedding = np.array(face_data['embedding'])
                        dot_product = np.dot(self.reference_embedding, frame_embedding)
                        frame_norm = np.linalg.norm(frame_embedding)
                        distance = 1 - (dot_product / (self.reference_norm * frame_norm))

                        if distance < threshold:
                            frame_has_match = True
                            break

                    if frame_has_match:
                        timestamp_seconds = frame_idx / fps
                        minutes = int(timestamp_seconds // 60)
                        seconds = int(timestamp_seconds % 60)

                        matches.append({
                            'frame_index': frame_idx,
                            'timestamp': f"{minutes:02d}:{seconds:02d}"
                        })
                        print(f"Match at frame {frame_idx} ({minutes:02d}:{seconds:02d})")

                    processed += 1

                    if processed % 100 == 0:
                        if processable_frames > 0:
                            print(
                                f"Progress: {processed} of {processable_frames} total processable frames | Matches found: {len(matches)}")
                        else:
                            print(f"Progress: {processed} frames | Matches found: {len(matches)}")

                except Exception as e:
                    if skipped == 0:
                        print(f"--> {e}")

                    skipped += 1

        print("=" * 60)
        print(f"Recognition complete: {len(matches)} matches")
        for match in matches:
            print(f"Match at frame {match['frame_index']} ({match['timestamp']})")
        print("=" * 60)

        return matches