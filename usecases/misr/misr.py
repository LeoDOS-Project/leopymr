import math
import os
import cv2
import torch
import numpy as np
from PIL import Image
import torch.nn.functional as F
from torchvision import transforms

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
UPSCALE = 1.0        # set >1.0 for digital zoom (e.g. 2.0)
SIGMA = 1.0          # kernel width


def vectorized_super_resolve_tiled(
    frames,
    upscale=1.0,
    sigma=1.0,
    tile_size=512
):
    """
    frames: (T, 3, H, W)
    returns: (3, H*upscale, W*upscale)
    """
    T, C, H, W = frames.shape
    device = frames.device

    Hh, Wh = int(H * upscale), int(W * upscale)
    out = torch.zeros(C, Hh, Wh, device=device)

    # Precompute kernel
    offsets = torch.tensor(
        [(-1, -1), (-1, 0), (-1, 1),
         (0, -1), (0, 0), (0, 1),
         (1, -1), (1, 0), (1, 1)],
        device=device,
        dtype=torch.float32
    )
    d2 = offsets[:, 0]**2 + offsets[:, 1]**2
    kernel = torch.exp(-d2 / (2 * sigma * sigma)).view(1, 1, 9, 1)
    kernel_sum = kernel.sum() * T

    # Upsample once
    frames_up = F.interpolate(
        frames,
        size=(Hh, Wh),
        mode="bilinear",
        align_corners=False
    )

    # Tile processing
    for y in range(0, Hh, tile_size):
        for x in range(0, Wh, tile_size):
            y0, y1 = y, min(y + tile_size, Hh)
            x0, x1 = x, min(x + tile_size, Wh)

            tile = frames_up[:, :, y0:y1, x0:x1]
            th, tw = tile.shape[-2:]

            patches = F.unfold(
                tile.view(T * C, 1, th, tw),
                kernel_size=3,
                padding=1
            )
            patches = patches.view(T, C, 9, th * tw)

            weighted = patches * kernel
            num = weighted.sum(dim=(0, 2))   # (3, th*tw)

            out[:, y0:y1, x0:x1] = (
                num / (kernel_sum + 1e-6)
            ).view(C, th, tw)

    return out


# ------------------------------------------------------------
# Image loading
# ------------------------------------------------------------

def load_files(files):
    from io import BytesIO
    images = []
    for file in files:
        buffer = BytesIO()
        buffer.write(file.read())
        buffer.seek(0)
        img = Image.open(buffer)
        images.append(transforms.ToTensor()(img))
    return torch.stack(images)  # (T, 3, H, W)

# ------------------------------------------------------------
# Optical flow alignment (OpenCV Farneback)
# ------------------------------------------------------------


def compute_flow(base, img):
    base_gray = cv2.cvtColor(base, cv2.COLOR_RGB2GRAY)
    img_gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    flow = cv2.calcOpticalFlowFarneback(
        base_gray, img_gray,
        None, 0.5, 3, 15, 3, 5, 1.2, 0
    )
    return flow


def warp(img, flow):
    h, w = flow.shape[:2]
    grid_x, grid_y = np.meshgrid(np.arange(w), np.arange(h))
    map_x = (grid_x + flow[..., 0]).astype(np.float32)
    map_y = (grid_y + flow[..., 1]).astype(np.float32)
    return cv2.remap(img, map_x, map_y, cv2.INTER_LINEAR)


# ------------------------------------------------------------
# Kernel-based merge (core SR step)
# ------------------------------------------------------------


def gaussian_kernel(dx, dy, sigma):
    return math.exp(-(dx * dx + dy * dy) / (2 * sigma * sigma))


def super_resolve(frames, upscale=1.0):
    """
    frames: (T, 3, H, W)
    """
    T, C, H, W = frames.shape
    Hh, Wh = int(H * upscale), int(W * upscale)

    device = frames.device
    result = torch.zeros(C, Hh, Wh, device=device)
    weights = torch.zeros_like(result)

    for t in range(T):
        img = frames[t]
        img_up = F.interpolate(
            img.unsqueeze(0),
            size=(Hh, Wh),
            mode="bilinear",
            align_corners=False
        )[0]

        for y in range(Hh):
            for x in range(Wh):
                # local kernel (3x3 neighborhood)
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        yy = min(max(y + dy, 0), Hh - 1)
                        xx = min(max(x + dx, 0), Wh - 1)
                        w = gaussian_kernel(dx, dy, SIGMA)
                        result[:, y, x] += img_up[:, yy, xx] * w
                        weights[:, y, x] += w

    return result / (weights + 1e-6)

# ------------------------------------------------------------
# Main pipeline
# ------------------------------------------------------------


def misr_merge(files):
    burst = load_files(files).to(DEVICE)  # (T,3,H,W)

    # Convert to numpy for OpenCV flow
    burst_np = (burst.permute(0, 2, 3, 1).cpu().numpy() * 255).astype(np.uint8)
    base = burst_np[0]

    aligned = [base]

    for i in range(1, len(burst_np)):
        flow = compute_flow(base, burst_np[i])
        warped = warp(burst_np[i], flow)
        aligned.append(warped)

    aligned = torch.stack([
        transforms.ToTensor()(Image.fromarray(img))
        for img in aligned
    ]).to(DEVICE)

    sr = vectorized_super_resolve_tiled(
        aligned,
        upscale=UPSCALE,
        sigma=SIGMA,
        tile_size=512
    )

    out = (
        sr.clamp(
            0,
            1).permute(
            1,
            2,
            0).cpu().numpy() *
        255).astype(
        np.uint8)
    return Image.fromarray(out)
