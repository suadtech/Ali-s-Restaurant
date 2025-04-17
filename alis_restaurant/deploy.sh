#!/bin/bash

# Initialize Git repository
git init

# Add all files to Git
git add .

# Create initial commit
git commit -m "Initial commit for Ali's Restaurant booking system"

# Instructions for GitHub setup
echo "=== GitHub Repository Setup ==="
echo "1. Create a new repository on GitHub named 'alis-restaurant'"
echo "2. Run the following commands to push to GitHub:"
echo "   git remote add origin https://github.com/yourusername/alis-restaurant.git"
echo "   git branch -M main"
echo "   git push -u origin main"
echo ""

# Instructions for Heroku setup
echo "=== Heroku Deployment Setup ==="
echo "1. Install Heroku CLI if not already installed"
echo "2. Login to Heroku: heroku login"
echo "3. Create a new Heroku app: heroku create alis-restaurant"
echo "4. Add PostgreSQL addon: heroku addons:create heroku-postgresql:hobby-dev"
echo "5. Configure environment variables:"
echo "   heroku config:set SECRET_KEY=your-secret-key-here"
echo "   heroku config:set DEBUG=False"
echo "   heroku config:set ALLOWED_HOSTS=.herokuapp.com"
echo "6. Push to Heroku: git push heroku main"
echo "7. Run migrations: heroku run python manage.py migrate"
echo "8. Create superuser: heroku run python manage.py createsuperuser"
