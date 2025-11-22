import cv2
import os


def pixelate(in_path, out_path, target_w, target_h, grid_width=64):
    """Pixelate image: downscale to grid_width x grid_height then upscale to target size.

    - in_path: source image path
    - out_path: destination path
    - target_w/target_h: final output size
    - grid_width: how many blocks across (smaller -> larger pixel blocks)
    """
    if not os.path.exists(in_path):
        raise FileNotFoundError(in_path)
    img = cv2.imread(in_path)
    if img is None:
        raise RuntimeError(f"Failed to read image: {in_path}")

    # compute grid height preserving target aspect ratio
    grid_height = max(1, int(grid_width * (target_h / max(1, target_w))))

    # resize down to grid size using INTER_LINEAR for averaging
    small = cv2.resize(img, (grid_width, grid_height), interpolation=cv2.INTER_LINEAR)
    # upscale to target size using nearest neighbor to keep blocky pixels
    pixelated = cv2.resize(small, (target_w, target_h), interpolation=cv2.INTER_NEAREST)

    # ensure output directory exists
    os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)

    # write PNG to preserve quality
    cv2.imwrite(out_path, pixelated)
    return out_path
