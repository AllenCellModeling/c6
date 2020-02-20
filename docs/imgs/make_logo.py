#!/usr/bin/env python
# coding: utf-8

# Make a logo for c6

import subprocess
import numpy as np
import tqdm
import matplotlib.pyplot as plt


# Define space we work in and track our spots
xylim = 100
centers = []
radii = []


# Create may circles, ensuring they don't overlap each other
def no_overlap(new_xy, new_r):
    """Does a new circle overlap our existing ones?"""
    c2c = [np.linalg.norm(new_xy - other) for other in centers]
    s2s = [dist - new_r - other for dist, other in zip(c2c, radii)]
    return not any(np.array(s2s) < 0)


max_circs, tries = 1000, 10000
for try_i in tqdm.trange(tries, desc="Making circles"):
    new_center = xylim * np.random.random(2)
    new_rad = 1 + np.random.random()
    if no_overlap(new_center, new_rad):
        centers.append(new_center)
        radii.append(new_rad)
centers = np.array(centers)
radii = np.array(radii)


# Expand each circle, one by one
for i, (center, radius) in tqdm.tqdm(
    enumerate(zip(centers, radii)), desc="Embiggening", total=len(centers)
):
    other_centers = centers[np.arange(len(centers)) != i]
    nearest_i = np.argmin([np.linalg.norm(center - other) for other in other_centers])
    nearest_center = other_centers[nearest_i]
    nearest_radius = radii[np.arange(len(radii)) != i][nearest_i]
    radii[i] += np.linalg.norm(center - nearest_center) - radius - nearest_radius


# Set up text
font_props = plt.matplotlib.font_manager.FontProperties(
    family="Helvetica", weight="black", size=98
)
# text_path = plt.matplotlib.text.TextPath((-1, 10), "c6", prop=font_props)
text_path = plt.matplotlib.text.TextPath((-1, 3), "c6", prop=font_props)

# Set up optional colors
monochrome = True
colors = ["tab:blue", "tab:orange", "tab:green", "tab:purple", "tab:olive", "tab:cyan"]

# Plot with clipping
fig, ax = plt.subplots(1, 1, figsize=(6, 6))
for center, radius in zip(centers, radii):
    if monochrome:
        color = colors[0]
    else:
        color = np.random.choice(colors)
    ax.add_patch(plt.matplotlib.patches.Circle(center, radius, fc=color, lw=0))
    ax.patches[-1].set_clip_path(text_path, ax.transData)
ax.set(xlim=(0, xylim), ylim=(0, xylim), aspect=1)
ax.axis("off")
plt.tight_layout(0)
plt.savefig("logo.png", transparent=True, pad_inches=0.0)
try:
    subprocess.run(
        "convert logo.png -gravity South -crop x100%-0-150 logo.png", shell=True
    )
except:
    print("Imagemagick cropping failed")
