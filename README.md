# Turtlebot

SLAM on Turtlebot in ROS2.

## Création du package

Depuis le dossier `src` du workspace :

```bash
cd Turtlebot/src
ros2 pkg create --build-type ament_python final_project_<votre_nom> --dependencies rclpy nav2_simple_commander
```

## Création du dossier `launch`

Créer un dossier `launch` dans le package :

```bash
mkdir Turtlebot/src/final_project_<votre_nom>/launch
```

## Modification du fichier `setup.py`

Ajouter les imports suivants :

```python
from glob import glob
import os
```

Modifier la section `data_files` pour installer les fichiers de lancement :

```python
data_files=[
    ('share/ament_index/resource_index/packages',
        ['resource/' + package_name]),
    ('share/' + package_name, ['package.xml']),
    (os.path.join('share', package_name, 'launch'),
        glob('launch/*.py')),
],
```

Déclarer ensuite le nœud dans `entry_points` :

```python
entry_points={
    'console_scripts': [
        'explorer = final_project_<votre_nom>.explorer:main',
    ],
},
```

où :

* `explorer` est le nom de l'exécutable ROS2 ;
* `explorer.py` est le fichier contenant le nœud ;
* `main` est la fonction principale du programme.

## Compilation du workspace

Depuis la racine du workspace :

```bash
cd Turtlebot
colcon build
source install/setup.bash
```

Après chaque nouvelle ouverture de terminal, il est nécessaire d'exécuter :

```bash
source install/setup.bash
```

Si des modifications sont apportées au package (ajout de fichiers, modification de `setup.py`, nouveaux nœuds, etc.), reconstruire le workspace :

```bash
colcon build
source install/setup.bash
```

## Lancement du projet

Lancer le fichier de lancement :

```bash
ros2 launch final_project_<votre_nom> explorer_turtlebot.launch.py
```

Ou lancer directement le nœud :

```bash
ros2 run final_project_<votre_nom> explorer
```
