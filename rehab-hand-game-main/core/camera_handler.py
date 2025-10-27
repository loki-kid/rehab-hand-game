from __future__ import annotations

from typing import Optional, Tuple, Any, List

import cv2
import mediapipe as mp


class CameraHandler:
    """Manage webcam capture and MediaPipe Hands detection.

    - Opens a webcam stream using OpenCV
    - Runs MediaPipe Hands to detect 21 landmarks
    - Provides frame in BGR and a list of normalized landmark coords
    - Convenience: computes index fingertip (landmark 8) in pixel coords
    """

    def __init__(self, camera_index: int = 0, width: int = 640, height: int = 480, flip_horizontal: bool = True) -> None:
        self.camera_index = camera_index
        self.frame_width = width
        self.frame_height = height
        # When True, mirror the output frame as a selfie view and adjust landmarks accordingly
        self.flip_horizontal = flip_horizontal
        self._is_open: bool = False

        self.cap: Optional[cv2.VideoCapture] = None
        self._mp_hands = mp.solutions.hands
        self._hands: Optional[mp.solutions.hands.Hands] = None

    def open(self) -> None:
        """Open camera and initialize detection pipelines.

        Raises:
            RuntimeError: If webcam cannot be opened.
        """
        self.cap = cv2.VideoCapture(self.camera_index)
        # Prefer a consistent resolution for the UI surface
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.frame_height)

        if not self.cap.isOpened():
            self.cap.release()
            self.cap = None
            raise RuntimeError("Cannot open webcam. Please check camera connection and index.")

        # Initialize MediaPipe Hands with reasonable defaults for real-time
        self._hands = self._mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=1,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1,
        )

        self._is_open = True

    def read_frame(self) -> Optional[Tuple[Any, Optional[List[Tuple[int, int]]], Optional[Tuple[int, int]]]]:
        """Read a frame and run detection.

        Returns:
            Tuple of (frame_bgr, landmarks_px, index_fingertip_px) where:
            - frame_bgr: numpy ndarray in BGR color space
            - landmarks_px: list of (x, y) pixel coords for 21 landmarks, or None
            - index_fingertip_px: (x, y) pixel coord of landmark 8, or None

        Returns None if the stream is not open or frame is unavailable.
        """
        if not self._is_open or self.cap is None or self._hands is None:
            return None

        success, frame_bgr = self.cap.read()
        if not success or frame_bgr is None:
            return None

        # MediaPipe expects RGB image (run detection on the raw frame)
        frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        results = self._hands.process(frame_rgb)

        landmarks_px: Optional[List[Tuple[int, int]]] = None
        index_finger_px: Optional[Tuple[int, int]] = None

        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            h, w = frame_bgr.shape[:2]
            landmarks_px = []
            for lm in hand_landmarks.landmark:
                x_px = int(lm.x * w)
                y_px = int(lm.y * h)
                landmarks_px.append((x_px, y_px))

            if len(landmarks_px) >= 9:  # ensure index 8 exists
                index_finger_px = landmarks_px[8]

        # If selfie mirror is requested, flip the frame and adjust landmark X coords
        if self.flip_horizontal:
            h, w = frame_bgr.shape[:2]
            frame_bgr = cv2.flip(frame_bgr, 1)
            if landmarks_px is not None:
                mirrored = []
                for (x, y) in landmarks_px:
                    # Mirror X to match selfie-view frame; keep within [0, w-1]
                    new_x = (w - 1) - x
                    mirrored.append((new_x, y))
                landmarks_px = mirrored
                if index_finger_px is not None:
                    index_finger_px = ((w - 1) - index_finger_px[0], index_finger_px[1])

        return (frame_bgr, landmarks_px, index_finger_px)

    def release(self) -> None:
        """Release camera resources and close pipelines."""
        self._is_open = False
        if self.cap is not None:
            try:
                self.cap.release()
            finally:
                self.cap = None
        if self._hands is not None:
            try:
                self._hands.close()
            finally:
                self._hands = None
