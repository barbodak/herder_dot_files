# Screenshot assets

`mission-control.png` is the screenshot supplied by the maintainer during the setup session (3024 × 1898 pixels). It replaces the earlier screenshots. OpenCode's visible demo conversation title and “just now” recency were temporary screenshot metadata, not installer defaults.

The close-ups are crops of that same screenshot. They preserve its content and are enlarged for readability:

| File | Crop in the original image | Enlargement |
| --- | --- | --- |
| `sidebar-detail.png` | 605 × 730, starting at x=0, y=280 | 125% |
| `top-bar-agents.png` | 925 × 52, starting at x=610, y=0 | 200% |
| `top-bar-terminals.png` | 903 × 52, starting at x=1687, y=0 | 200% |

To reproduce them with ImageMagick:

```sh
magick mission-control.png -crop 605x730+0+280 +repage -filter Lanczos -resize 125% sidebar-detail.png
magick mission-control.png -crop 925x52+610+0 +repage -filter Lanczos -resize 200% top-bar-agents.png
magick mission-control.png -crop 903x52+1687+0 +repage -filter Lanczos -resize 200% top-bar-terminals.png
```
