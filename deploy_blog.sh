#!/bin/bash
set -euo pipefail

# 1. Start as privileged user 'matt'
if [[ "$(whoami)" != "matt" ]]; then
  echo "This script must be run as user 'matt'"
  exit 1
fi

# 2. Change to project directory
cd /var/lib/blog

# 3. Change to 'blog' user and run deployment steps
sudo -i -u blog bash <<'EOF'
set -euo pipefail

cd /var/lib/blog

# Ensure poetry is in PATH (adjust if your poetry is elsewhere)
export PATH="$PATH:/home/blog/.local/bin"

# 4. Pull latest code
git pull

# 5. Run backend migrations and collectstatic
cd /var/lib/blog/api
poetry install
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput

# 6. Change to frontend directory
cd /var/lib/blog/ui

# 7. Ensure nvm and npm are available, and use the correct Node version from .nvmrc
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
nvm install
nvm use

# 8. Set build environment variables and build
export VITE_API_URL="https://ooo-yay.com"
export VITE_API_URL_INTERNAL="http://127.0.0.1:8000"
export VITE_PUBLIC_SITE_URL="https://ooo-yay.com"

npm install
npm run build
EOF

# 9. Back to 'matt' user, restart services
sudo systemctl restart nuxt
sudo systemctl restart blog

echo "Deployment complete!" 