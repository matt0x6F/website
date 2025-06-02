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
sudo -u blog bash <<'EOF'
set -euo pipefail

# 4. Pull latest code
git pull

# 5. Run backend migrations and collectstatic
cd /var/lib/blog/api
poetry install
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput

# 6. Change to frontend directory
cd /var/lib/blog/ui

# 7. Set build environment variables and build
export VITE_API_URL="https://ooo-yay.com/api"
export VITE_API_URL_INTERNAL="http://127.0.0.1:8000"
export VITE_PUBLIC_SITE_URL="https://ooo-yay.com"

npm install
npm run build
EOF

# 8. Back to 'matt' user, restart services
sudo systemctl restart nuxt
sudo systemctl restart blog

echo "Deployment complete!" 