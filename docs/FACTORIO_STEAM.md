# Utiliser Factorio Steam avec FLE

## Vérifier ta version Steam

FLE nécessite **Factorio v1.1.110** exactement.

### 1. Vérifier ta version actuelle
```bash
# Lance Factorio Steam
# Menu principal → coin en bas à droite
# Tu verras "Version X.X.XX"
```

### 2. Changer de version sur Steam (si nécessaire)

Steam permet de revenir aux anciennes versions :

1. **Steam → Bibliothèque**
2. **Clic droit sur Factorio → Propriétés**
3. **Betas** (onglet)
4. **Sélectionner dans le menu déroulant:**
   - Cherche `1.1.110` ou `1.1.x - legacy`
5. **Steam téléchargera automatiquement**

### 3. Versions compatibles

**Bonne nouvelle:** Factorio 1.1.x est généralement rétro-compatible.

Si tu as **1.1.100+**, tu peux probablement te connecter au serveur FLE même si ce n'est pas exactement 1.1.110.

**Test rapide:**
```bash
# Lance Factorio Steam
# Multijoueur → Se connecter
# Adresse: localhost
# Port: 34197
```

Si ça refuse la connexion à cause de la version, change via les Betas Steam.

### 4. Alternative: Version standalone

Si Steam ne propose pas 1.1.110:

1. Télécharge depuis https://factorio.com/download/archive
2. Cherche "1.1.110" dans l'archive
3. Télécharge la version macOS
4. Utilise cette version pour te connecter

### 5. Vérification serveur FLE

Le serveur FLE tourne en v1.1.110:

```bash
docker logs fle-factorio_0-1 | grep "Factorio"
# Affichera: "Factorio 1.1.110 (build 62357, linux64, headless)"
```

## Essayer quand même

**Conseil:** Essaye avec ta version Steam actuelle d'abord !

Factorio est plutôt tolérant avec les versions proches. Si c'est 1.1.x (n'importe quel patch), ça marchera probablement.

Si tu as une erreur de version incompatible, on ajustera via les Betas Steam.
