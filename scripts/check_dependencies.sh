#!/usr/bin/env bash
# Vérifie que tout ce dont ThreatFusion a besoin est installé sur la machine.
# Usage : bash scripts/check_dependencies.sh

set -uo pipefail
FAIL=0

check() {
  local name="$1"
  local cmd="$2"
  if eval "$cmd" > /dev/null 2>&1; then
    echo "[OK]   $name"
  else
    echo "[MANQUANT] $name"
    FAIL=1
  fi
}

echo "== Outils système =="
check "Docker installé"            "docker --version"
check "Docker daemon actif"        "docker info"
check "Docker Compose disponible"  "docker compose version"
check "Python >= 3.12"             "python3 -c 'import sys; exit(0 if sys.version_info >= (3,12) else 1)'"
check "Node.js installé"           "node --version"
check "npm installé"               "npm --version"

echo ""
echo "== Dépendances Python (backend) =="
if [ -f backend/requirements.txt ]; then
  cd backend
  python3 -m pip install --break-system-packages --dry-run -q -r requirements.txt > /tmp/pip_check.log 2>&1
  if [ $? -eq 0 ]; then
    echo "[OK]   requirements.txt installable (dry-run)"
  else
    echo "[ATTENTION] Problème potentiel avec requirements.txt, voir /tmp/pip_check.log"
    FAIL=1
  fi
  cd ..
else
  echo "[MANQUANT] backend/requirements.txt introuvable"
  FAIL=1
fi

echo ""
echo "== Dépendances Node (frontend) =="
if [ -f frontend/package.json ]; then
  echo "[OK]   frontend/package.json trouvé (lance 'npm install' dans frontend/ pour installer)"
else
  echo "[MANQUANT] frontend/package.json introuvable"
  FAIL=1
fi

echo ""
if [ $FAIL -eq 0 ]; then
  echo "Tout est prêt."
else
  echo "Certains éléments manquent — installe-les avant de lancer 'docker compose up'."
fi
exit $FAIL
