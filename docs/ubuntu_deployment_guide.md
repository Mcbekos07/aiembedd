# Ubuntu Deployment Guide

1. Run `deploy/scripts/install_ubuntu.sh`.
2. Configure `/opt/aiembedd/.env` from `deploy/env/.env.example`.
3. Install systemd unit from `deploy/systemd/aiembedd-backend.service`.
4. Install nginx config from `deploy/nginx/aiembedd.conf`.
