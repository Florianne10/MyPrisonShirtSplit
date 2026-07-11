# MyPrisonShirtSplit

Script Python qui, à partir d'une image, génère une image par couleur recherchée (`colorsToPaint`) contenant uniquement les pixels qui seraient repeints. La couleur cible (`colorsToSet`) est toujours considérée comme **blanche** ; la luminosité d'origine du pixel est préservée relativement à la couleur recherchée (même logique que le script Lua `GeneratePaintedImage`).

## Prérequis

- Python 3.10+
- Pillow et numpy

```
pip install Pillow numpy
```

## Utilisation

```
python main.py <image> <couleur1> [<couleur2> ...] [-s SENSIBILITÉ] [-o DOSSIER_SORTIE]
```

### Paramètres

| Paramètre | Description |
|---|---|
| `image` | Chemin de l'image source (png, jpg, ...) |
| `colors` | Une ou plusieurs couleurs à rechercher, séparées par des **espaces**. Format `R,G,B` (ex: `255,0,0`) ou hex (ex: `#FF0000`) |
| `-s`, `--sensibility` | Sensibilité entre 0 et 1 (défaut `0.1`). Plus la valeur est élevée, plus la marge de couleur acceptée est large |
| `-o`, `--output-dir` | Dossier de sortie (défaut : même dossier que l'image source) |

### Exemples

Une seule couleur recherchée :

```
python main.py mon_image.png 255,0,0
```

Plusieurs couleurs, sensibilité personnalisée :

```
python main.py mon_image.png 255,0,0 0,255,0 0,0,255 -s 0.15
```

Avec des couleurs en hexadécimal et un dossier de sortie custom :

```
python main.py mon_image.png #FF0000 #00FF00 -o ./resultats
```

## Résultat

Pour chaque couleur passée en paramètre, une image `PNG` est générée :

```
<nom_image>_paint_<index>_<r-g-b>.png
```

- Les pixels qui correspondent à la couleur recherchée (dans la marge de `sensibility`) sont opaques et repeints (nuance de blanc/gris selon la luminosité d'origine).
- Tous les autres pixels sont transparents (alpha = 0).
- L'ordre des couleurs sur la ligne de commande définit la priorité : un pixel déjà capté par une couleur précédente n'est jamais retraité par les couleurs suivantes.
