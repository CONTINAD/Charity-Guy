# Just a Charity Guy — $CHARITY

Landing site for the **Just a Charity Guy** memecoin. Single static HTML page styled with hand-stamped, sticker-zine aesthetics — chunky Bungee headlines, Caveat marker scribbles, and a cream / forest-green palette built around the mascot.

## Run locally

```bash
python3 -m http.server 8765
```

Then open <http://localhost:8765>.

## Files

| File | Purpose |
|---|---|
| `index.html` | The site — single page, no build step |
| `mascot.png` | Original mascot artwork |
| `mascot_cutout.png` | Mascot with cream backdrop knocked out (transparent) |
| `mascot_card.png` | Square portrait card on halftone bg |
| `mascot_logo.png` / `favicon.png` | Circular badge crops for nav / favicon |
| `mascot_silhouette_*.png` | Single-color silhouettes (used in marquee + watermarks) |
| `coin.png` | Spinning coin asset for tokenomics |
| `pattern_heads.png` | Tileable pattern of mascot heads |
| `make_assets.py` | Pillow script that regenerates all derivatives from `mascot.png` |

## Regenerate assets

```bash
python3 make_assets.py
```

## Customize

Search `index.html` for these placeholders:

- `CHRTYxxx...` — the contract address
- `href="#"` on social cards / receipts — your real social and explorer links
- `@justacharityguy`, `t.me/justacharityguy` — handles
