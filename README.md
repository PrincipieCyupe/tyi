# Tegura Youth Initiative by PRINCIPIE

> **Empowering rural youth in Rwanda with entrepreneurship training, mentorship, and seed funding to build tomorrow's successful businesses.**

[![Python](https://img.shields.io/badge/python-3.11+-green.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-3.0.0-red.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

---

## ��� Table of Contents

1. [What is Tegura Youth Initiative?](#what-is-tegura-youth-initiative)
2. [Why This Platform Exists](#why-this-platform-exists)
3. [Key Features](#key-features)
4. [Technology Stack](#technology-stack)
5. [Getting Started - Local Development](#getting-started---local-development)
6. [Environment Configuration](#environment-configuration)
7. [Database Setup](#database-setup)
8. [Running the Application](#running-the-application)
9. [Production Deployment on Render](#production-deployment-on-render)
10. [Admin Access](#admin-access)
11. [Using the Platform](#using-the-platform)
12. [Troubleshooting](#troubleshooting)
13. [Contributing](#contributing)
14. [License](#license)

---

## ��� What is Tegura Youth Initiative?

Tegura Youth Initiative (TYI) is a comprehensive web platform designed to bridge the gap between rural youth entrepreneurship potential and actual business success in Rwanda. Built with Flask and modern web technologies, it provides a complete ecosystem for:

- **Training**: Access to structured entrepreneurship courses
- **Competition**: Business idea competitions with seed funding prizes
- **Mentorship**: One-on-one guidance from successful entrepreneurs
- **Funding**: 100,000 RWF seed funding for winning projects
- **Community**: Networking with peers and industry leaders basically in-person 

Think of it as a **startup accelerator specifically designed for rural Rwandan youth** - combining education, competition, and real funding opportunities in one platform.

---

## Why This Platform Exists

### The Problem
Rural youth in Rwanda face significant barriers to entrepreneurship:
- Limited access to entrepreneurship education
- No structured mentorship programs
- Difficulty accessing seed funding
- Isolation from entrepreneurial communities
- Lack of business planning resources

### Proposed Solution
Tegura Youth Initiative provides:
- **Free online training** in business fundamentals
- **Competitive framework** that motivates excellence
- **Real seed funding** (100,000 RWF) for winners
- **Digital community** connecting rural youth with mentors
- **Complete ecosystem** from idea to business launch

### Impact Expected in the next 5 years
- 500+ youth trained in entrepreneurship
- 50+ businesses launched and operating
- 100M+ RWF in total funding distributed
- 30+ partner organizations supporting the initiative

---

## Key Features

### For Participants

**Education System**
- Structured course modules (Business Planning, Financial Management, Marketing)
- Progress tracking with completion certificates
- Quiz assessments and practical assignments
- Downloadable resources and templates

**Competition Platform**
- Business idea submission and refinement
- Application tracking dashboard
- Pitch preparation resources
- Real-time leaderboard

**Communication Hub**
- Message inbox for announcements
- Direct contact with program coordinators

**Profile Management**
- Personal dashboard with statistics
- Progress visualization
- Certificate downloads
- Application history

### For Administrators

**Content Management**
- Create and manage courses
- Add/edit course modules
- Upload educational materials
- Manage competition opportunities

**User Management**
- Send targeted messages to users
- Upload leaderboard via CSV
- Track user progress
- Monitor applications

**Competition Administration**
- Review business applications
- Update application statuses
- Announce winners
- Manage prizes and funding

**Analytics Dashboard**
- User engagement metrics
- Course completion rates
- Application statistics
- Platform usage insights

### Public-Facing Features

**Landing Page**
- Animated hero section
- Auto-counting statistics
- Success stories showcase
- Sponsor carousel
- FAQ section
- Contact form with email integration

**Responsive Design**
- Mobile-first approach
- Tablet-optimized layouts
- Desktop full experience
- Cross-browser compatibility

---

## Technology Stack

### Backend
```
Python 3.11+          Core language
Flask 3.0.0           Web framework
SQLAlchemy 3.1.1      Database ORM
Flask-Login 0.6.3     User authentication
Flask-Bcrypt 1.0.1    Password hashing
Flask-WTF 1.2.1       Form handling
```

### Frontend
```
HTML5                 Structure
Tailwind CSS 4.1      Styling (pre-compiled)
JavaScript (Vanilla)  Interactivity
Lucide Icons          Icon system
```

### Database
```
SQLite (Development)  Local development
PostgreSQL (Production) Render deployment
```

### External Services
```
SendGrid              Email notifications
Cloudinary            Image hosting
Render                Production hosting
```

### Development Tools
```
Git                   Version control
Python venv           Virtual environments
pip                   Package management
VS Code               Recommended IDE
```

---

## Getting Started - Local Development

### Prerequisites

Before you begin, make sure you have these installed on your computer:

**1. Python 3.11 or Higher**
```bash
# Check your Python version
python --version
# or
python3 --version

# Should output: Python 3.11.x or higher
```

**Don't have Python?** Download it from [python.org](https://www.python.org/downloads/)

**2. Git**
```bash
# Check if Git is installed
git --version

# Should output: git version x.x.x
```

**Don't have Git?** Download it from [git-scm.com](https://git-scm.com/downloads)

**3. Text Editor or IDE**
- [VS Code](https://code.visualstudio.com/) (Highly recommended)
- [PyCharm](https://www.jetbrains.com/pycharm/)
- [Sublime Text](https://www.sublimetext.com/)
- Any text editor you're comfortable with

### Step 1: Clone the Repository

Open your terminal (Command Prompt on Windows, Terminal on Mac/Linux) and run:
```bash
# Clone the repository
git clone https://github.com/PrincipieCyupe/tyi.git

# Navigate into the project folder
cd tyi
```

**What this does:** Allows you access all the project files locally on you computer.

### Step 2: Create a Virtual Environment

Virtual environments keep your project dependencies isolated from other Python projects.
```bash
# Create virtual environment
python -m venv venv

# Activate it:

# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

**You'll know it worked** when you see `(venv)` at the beginning of your terminal prompt.

### Step 3: Install Dependencies

With your virtual environment activated, install all required packages:
```bash
pip install -r requirements.txt
```

This installs:
- Flask (web framework)
- SQLAlchemy (database)
- SendGrid (emails)
- Cloudinary (images)
- Bcrypt (password security)
- And all other dependencies

**This may take 1-2 minutes** depending on your internet speed.


## Environment Configuration and Steps to Get All Values

### Step 4: Set Up Environment Variables

Create a file named `.env` in the root directory (same level as `app.py`):
```bash
# Create .env file
touch .env  # Mac/Linux
# or
type nul > .env  # Windows
```

Open `.env` in your text editor and add these variables:
```env
# Flask Configuration
SECRET_KEY=your_super_secret_key_here_change_this_in_production
FLASK_ENV=development

# Database (leave as-is for local development)
DATABASE_URL=sqlite:///tegura.db

# SendGrid Email Service (required for email features)
SENDGRID_API_KEY=your_sendgrid_api_key_here_(You will need to set it up yourself from sendgrid.com)
SENDGRID_FROM_EMAIL=your-verified-email@domain.com_(also from sendgrid)

# Cloudinary Image Hosting (required for image uploads)
CLOUDINARY_CLOUD_NAME=your_cloud_name
CLOUDINARY_API_KEY=your_cloudinary_api_key
CLOUDINARY_API_SECRET=your_cloudinary_api_secret
```

### Getting Your API Keys

**SendGrid Setup (for email notifications)**

1. Create free account at [sendgrid.com](https://sendgrid.com/)
2. Go to Settings → API Keys
3. Click "Create API Key"
4. Give it a name (e.g., "Tegura Youth Initiative")
5. Choose "Full Access"
6. Copy the key and paste it in `.env` as `SENDGRID_API_KEY`
7. Go to Settings → Sender Authentication
8. Click "Verify Single Sender"
9. Enter your email and verify it
10. Use this email as `SENDGRID_FROM_EMAIL`

**Cloudinary Setup (for image uploads)**

1. Create free account at [cloudinary.com](https://cloudinary.com/)
2. From your dashboard, find:
   - Cloud Name
   - API Key
   - API Secret
3. Copy these values into your `.env` file

**Secret Key Generation**

For development, you can use any random string. For production, generate a secure key:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Copy the output and use it as your `SECRET_KEY`.

---

## Database Setup

### Step 6: Initialize the Database
MAke sure you have python and inside python environment run
```bash
# This creates the database
from app import app, db
with app.app_context():
   db.create_all()
exit() # to go outside
```

**You'll see:**
```
✅ Cloudinary configured: True
✅ Database tables initialized successfully!
 * Running on http://127.0.0.1:5000
```

**What just happened:**
- SQLite database created at `instance/tegura.db`
- All 14 tables created automatically:
  - `tyi` (users)
  - `course`, `course_module` (education system)
  - `user_course`, `user_module_progress` (progress tracking)
  - `application`, `application_opportunity` (competitions)
  - `message` (user notifications)
  - `leaderboard_entry` (rankings)
  - `event`, `blog_post`, `activity_update` (content)

### Understanding the Database Structure

**Core Tables:**
```
TYI (Users)
├── id, firstname, lastname, email
├── password (hashed with Bcrypt)
├── email_verified, verification_token
├── reset_token, reset_token_expiry
└── created_at

Course
├── id, title, description
├── duration_weeks, level
└── total_modules

Application
├── id, user_id, opportunity_id
├── competition_name, business_name
├── business_idea, status
└── completion_percentage
```

**Relationships:**
- One user → many courses (enrollments)
- One user → many applications
- One user → many messages
- One course → many modules
- One opportunity → many applications

---

## ▶Running the Application

### Step 7: Start the Development Server
```bash
# Make sure your virtual environment is activated
# You should see (venv) in your terminal

python app.py 
# or
flask run
```

**Success Output:**
```
 SENDGRID_API_KEY in environment: True
 API Key starts with: SG.xxxxxxxx...
 API Key length: 69
✅ Cloudinary configured: True
✅ Database tables initialized successfully!
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 8: Access the Application

Open your web browser and visit:
```
http://localhost:5000
```

**or**
```
http://127.0.0.1:5000
```

**You should see:** The Tegura Youth Initiative landing page with:
- Animated hero section
- Statistics counters
- About section
- Competition details
- And more!

### Quick Test Checklist

✅ **Landing Page Loads**: Hero image, animations working
✅ **Registration Works**: Create a new account
✅ **Email Verification**: Check inbox for verification email
✅ **Login Works**: Sign in after verifying email
✅ **Dashboard Loads**: See your user dashboard
✅ **Contact Form**: Submit contact form (check admin email)

---

## Production Deployment on Render

### Why Render?

Render offers:
- Free PostgreSQL database
- Automatic deployments from GitHub
- SSL certificates (HTTPS)
- Easy environment variable management
- Zero DevOps knowledge required

### Prerequisites for Deployment

- GitHub account
- Render account (sign up at [render.com](https://render.com))
- All your API keys (SendGrid, Cloudinary)
- Your code pushed to GitHub

### Step 1: Prepare Your Code for Production

**1.1 Create `requirements.txt`**

Already included in the project, but verify it contains:
```txt
Flask==3.0.0
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Flask-WTF==1.2.1
Flask-Bcrypt==1.0.1
WTForms==3.1.1
python-dotenv==1.0.0
gunicorn==21.2.0
psycopg2-binary==2.9.9
sendgrid==6.11.0
cloudinary==1.36.0
```

**1.2 Create `runtime.txt`**
```txt
python-3.11.0
```

**1.3 Verify `.gitignore`**

Make sure these are in `.gitignore`:
```gitignore
# Environment variables
.env

# Python
__pycache__/
*.pyc
*.pyo
venv/
ENV/

# Database
instance/
*.db
*.sqlite
*.sqlite3

# IDE
.vscode/
.idea/
.DS_Store
```

**1.4 Compile Tailwind CSS**
```bash
npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/main.css --minify
```

### Step 2: Push to GitHub
```bash
# Initialize git (if not already done)
git init

# Add all files
git add .

# Commit
git commit -m "Initial commit - Tegura Youth Initiative"

# Create repository on GitHub, then:
git remote add origin https://github.com/PrincipieCyupe/tyi.git
git branch -M main
git push -u origin main
```

### Step 3: Create PostgreSQL Database on Render

1. Go to [dashboard.render.com](https://dashboard.render.com)
2. Click "**New +**" → "**PostgreSQL**"
3. Configure database:
   - **Name**: `tegura-database`
   - **Database**: `tegura_db`
   - **User**: `tegura_user` (auto-filled)
   - **Region**: Choose closest to your users (e.g., Frankfurt for Europe, Oregon for US)
   - **Plan**: Free ($0/month)
4. Click "**Create Database**"
5. **Wait 2-3 minutes** for database to initialize
6. **Copy the "External Database URL"** - you'll need this soon!

### Step 4: Create Web Service on Render

1. Click "**New +**" → "**Web Service**"
2. Connect your GitHub repository
3. Configure service:

**Basic Settings:**
- **Name**: `tegura-youth-initiative`
- **Region**: **SAME as your database region** (important!)
- **Branch**: `main`
- **Runtime**: Python 3

**Build Settings:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app`

**Plan:**
- Select **Free** ($0/month)

4. Click "**Advanced**" to add environment variables

### Step 5: Configure Environment Variables

Click "**Add Environment Variable**" for each of these:

| Key | Value | Notes |
|-----|-------|-------|
| `DATABASE_URL` | `postgresql://...` | Paste External Database URL from Step 3 |
| `SECRET_KEY` | Generate new key | Run: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `SENDGRID_API_KEY` | `SG.xxx` | From your SendGrid account |
| `SENDGRID_FROM_EMAIL` | `your@email.com` | Your verified SendGrid sender email |
| `CLOUDINARY_CLOUD_NAME` | `your_cloud_name` | From Cloudinary dashboard |
| `CLOUDINARY_API_KEY` | `your_api_key` | From Cloudinary dashboard |
| `CLOUDINARY_API_SECRET` | `your_api_secret` | From Cloudinary dashboard |
| `FLASK_ENV` | `production` | Disables debug mode |
| `PYTHON_VERSION` | `3.11.0` | Matches runtime.txt |

**⚠️ Important:** Never use development secret keys in production!

### Step 6: Deploy

1. Click "**Create Web Service**"
2. Render will:
   - Clone your GitHub repository
   - Install dependencies (takes 3-5 minutes)
   - Start your application
   - Assign a URL: `https://tegura-youth-initiative.onrender.com`

**Monitor the deployment logs:**
```
==> Building...
==> Installing Python 3.11.0
==> Installing dependencies from requirements.txt
==> Starting service...
✅ Cloudinary configured: True
✅ Database tables initialized successfully!
==> Your service is live at https://tegura-youth-initiative.onrender.com
```

### Step 7: Verify Deployment

Visit your live URL and check:

✅ Landing page loads correctly
✅ CSS styles are applied (Tailwind working)
✅ Images load (Cloudinary working)
✅ Registration creates account
✅ Email verification sent (SendGrid working)
✅ Login works after verification
✅ Dashboard loads with data
✅ Contact form sends emails

### Step 8: Set Up Automatic Deployments

Render automatically deploys when you push to GitHub:
```bash
# Make changes locally
git add .
git commit -m "Update feature X"
git push origin main

# Render automatically rebuilds and deploys
```

**Deployment takes 3-5 minutes** each time.

---

## Admin Access

### Default Admin Credentials

**Admin Login URL:**
```
http://localhost:5000/admin
# or production:
https://your-app.onrender.com/admin/
```

**Password:** `Principie@123`

**SECURITY WARNING:**
Change this password in production! Edit in `app.py`:
```python
ADMIN_PASSWORD = "your_new_secure_password_here"
```

### Admin Features

Once logged in, you can:

**Manage Courses**
- Create new courses with modules
- Edit course content
- Delete courses
- Track enrollments

**Manage Users**
- Send messages to specific users
- View user progress
- Monitor applications

**Manage Competition**
- Create application opportunities
- Review submitted applications
- Update application statuses
- Announce winners

**Upload Leaderboard**
- Download CSV template
- Fill in participant data
- Upload CSV to update rankings
- System auto-creates entries

**CSV Format Example:**
```csv
rank,user_email,total_points,project_name,location
1,marie@example.com,1500,Agri-Solutions,Nyagatare
2,jean@example.com,1400,EcoTech,Musanze
3,grace@example.com,1350,Rural Connect,Kamonyi
```

**Manage Events & Content**
- Create events
- Publish blog posts
- Add activity updates
- Manage application opportunities

---

## Using the Platform

### For New Users

**1. Register an Account**
- Visit homepage
- Click "Register" or "Apply Now"
- Fill in personal information
- Submit registration
- **Check your email** for verification link
- Click verification link
- Return to login

**2. Verify Your Email**
- Open verification email from email you used when filling out the register form
- Click "Verify Email Address" button
- You'll be redirected to login page
- Now you can log in!

**3. Log in to dashboard**
- Explore available features

### Navigating the Dashboard

**Home Tab** 
- Overview of your progress:
- Training progress
- Application status
- Leaderboard rank
- Unread messages
- Open opportunities

**Education Tab**
 - Access courses:
- View enrolled courses
- Browse available courses
- Track module completion
- Download certificates

**Application Tab**
- Competition participation:
- View application opportunities
- Submit business ideas
- Track application status
- Days until deadline

**Leaderboard Tab** 
- Rankings:
- Your current rank
- Top 10 participants
- Total participants
- Project details

**Messages Tab** 
- Communications:
- Unread notifications
- Important announcements
- Mark as read/delete options

## Troubleshooting

### Common Issues and Solutions

**Problem: "Module not found" error**
```
ModuleNotFoundError: No module named 'flask'
```

**Solution:**
```bash
# Make sure virtual environment is activated
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Reinstall dependencies
pip install -r requirements.txt
```

---

**Problem: Database tables not created**
```
sqlalchemy.exc.OperationalError: no such table: tyi
```

**Solution:**
```bash
# Delete old database
rm instance/tegura.db

# Restart application (tables auto-create)
python app.py
```

---

**Problem: Email not sending**
```
ERROR sending email: HTTP Error 401: Unauthorized
```

**✅ Solution:**
1. Check SendGrid API key in `.env`
2. Verify sender email is authenticated in SendGrid
3. Check SendGrid dashboard for error details

---

**Problem: Images not uploading**
```
Error uploading to Cloudinary: ...
```

**Solution:**
1. Verify Cloudinary credentials in `.env`
2. Check Cloudinary dashboard for usage limits
3. Ensure file size is under 10MB

---

**Problem: Password reset link expired**
```
Reset link has expired. Please request a new one.
```

**Solution:**
This is normal! Reset tokens expire after 1 hour for security.
1. Go to `/forgot-password`
2. Request new reset link
3. Use link within 1 hour

---

**Problem: CSS styles not loading**
```
GET http://localhost:5000/static/css/main.css 404 (Not Found)
```

**Solution:**
```bash
# Compile Tailwind CSS
npx @tailwindcss/cli -i ./static/css/input.css -o ./static/css/main.css --minify

# Verify file exists
ls static/css/main.css
```

---

**Problem: Port already in use**
```
OSError: [Errno 48] Address already in use
```

**Solution:**
```bash
# Find process using port 5000
lsof -i :5000  # Mac/Linux
netstat -ano | findstr :5000  # Windows

# Kill the process
kill -9 <PID>  # Mac/Linux
taskkill /PID <PID> /F  # Windows

# Or use different port
export PORT=5001
python app.py
```

---

**Problem: Render deployment fails**
```
Build failed: requirements.txt not found
```

**Solution:**
1. Ensure `requirements.txt` is in root directory
2. Commit and push to GitHub:
```bash
git add requirements.txt
git commit -m "Add requirements.txt"
git push origin main
```
3. Trigger manual deploy in Render dashboard

---

**Problem: Database connection error on Render**
```
psycopg2.OperationalError: could not connect to server
```

**Solution:**
1. Check `DATABASE_URL` environment variable
2. Ensure web service and database are in **same region**
3. Use **Internal Database URL**, not External
4. Wait 2-3 minutes after database creation

---

### Getting Help

**Email Support:** admin@principie.tech

** Issues:** [GitHub Issues](https://github.com/PrincipieCyupe/tyi/issues)

**Documentation:** This README

**Bug Reports:** 
Include:
- What you were trying to do
- What happened instead
- Error messages (full text)
- Your operating system
- Python version
- Browser (if relevant)

---

## Contributing

We welcome contributions from the community! Here's how you can help me:

### Types of Contributions

**Bug Reports**
- Found a bug? Open an issue
- Include reproduction steps
- Screenshots help!

**Feature Requests**
- Have an idea? I'd love to hear it
- Explain the use case
- Describe expected behavior

**Code Contributions**
- Fork the repository
- Create a feature branch
- Make your changes
- Write tests if applicable
- Submit a pull request

**Documentation**
- Improve this README
- Add code comments
- Create tutorials
- Translate to other languages

### Development Workflow
```bash
# 1. Fork and clone
git clone https://github.com/PrincipieCyupe/tyi.git

# 2. Create branch
git checkout -b feature/amazing-feature

# 3. Make changes
# ... edit files ...

# 4. Test locally
python app.py

# 5. Commit
git add .
git commit -m "Add amazing feature"

# 6. Push
git push origin feature/amazing-feature

# 7. Open Pull Request on GitHub
```

### Code Style

- Follow PEP 8 for Python code
- Use meaningful variable names
- Comment complex logic
- Keep functions focused and small

### Testing

Before submitting:
- Test registration flow
- Test email sending
- Test image uploads
- Test all user roles (user, admin)
- Check mobile responsiveness

---

## Acknowledgments

### Built by
**Principie Cyubahiro**
- Software Developer & Entrepreneur
- African Leadership University Pre-final Student
- Based in Kigali, Rwanda

### Special Thanks

**Institutions**
- African Leadership University - BSE Faculty

**Technology**
- Flask & Python community
- SendGrid for email infrastructure
- Cloudinary for image hosting
- Render for cloud hosting

**Inspiration**
This platform was inspired by the incredible potential of rural youth in Rwanda who lack access to entrepreneurship resources. Every line of code is written with the goal of creating real economic opportunities and transforming lives.

---

## Contact & Support

### Get In Touch

**Email:** admin@principie.tech

**WhatsApp:** [+250 798 200 584](https://wa.me/250798200584)

**Website:** [Tegura-Youth-Iniative]https://tyi-w843.onrender.com/

**LinkedIn:** [linkedin.com/in/principie](https://www.linkedin.com/in/principie)

**GitHub:** [github.com/PrincipieCyupe](https://www.github.com/PrincipieCyupe)

**Instagram:** [@cyubahiro_principie](https://www.instagram.com/cyubahiro_principie/?hl=en)

**Facebook:** [Principie Cyubahiro](https://www.facebook.com/cyubahiro.principie)

### Book An Office Hours with Me

I'm here to help! Reach out:
- **Monday - Friday:** 9:00 AM - 6:00 PM (CAT/GMT+2)
- **Response Time:** Within 24 hours
- **Emergency Support:** WhatsApp for urgent issues

---

##What's Next?

### Immediate Todos After Setup

- [ ] Change admin password from default
- [ ] Create your first admin account
- [ ] Add sample course content
- [ ] Test email delivery
- [ ] Upload test images to Cloudinary
- [ ] Create sample application opportunity
- [ ] Test complete user flow
- [ ] Invite beta testers

### Future Roadmap

**Q1 2026**
- [ ] Mobile application (iOS & Android)
- [ ] SMS notifications for rural areas
- [ ] Offline course access
- [ ] Video training modules

**Q2 2026**
- [ ] Payment gateway integration
- [ ] Automated certificate generation
- [ ] Alumni network features

**Q3 2026**
- [ ] AI-powered business idea validation
- [ ] Mentor matching algorithm
- [ ] Virtual pitch competitions
- [ ] Investor connection platform

**Q4 2026**
- [ ] Franchise to other African countries
- [ ] Partnership with universities
- [ ] Corporate sponsorship portal
- [ ] Impact measurement dashboard

---

## upport This Project

If this project has helped you or your organization:

**⭐ Star this repository** on GitHub

**Spread the word** - Share with friends and colleagues

**Sponsor** - Support continued development
- Become a corporate sponsor
- Fund scholarships for participants
- Donate to the prize pool

**Partner** - Join as an institutional partner
- Provide mentorship
- Offer internships
- Host workshops

**Contribute** - Help us improve
- Report bugs
- Suggest features
- Submit code
- Improve documentation

---

## Security & Privacy

### Data Protection

**Password Security**
- Bcrypt hashing with salt
- Minimum 4-character requirement (update to 8+ for production)
- Secure password reset flow

**Email Verification**
- Required before account access
- Token expiry (24 hours)
- Prevents spam registrations

**Session Management**
- Secure session cookies
- Automatic timeout
- Login tracking

**File Upload Security**
- File type validation
- Size limits (10MB)
- Secure filename generation

### Privacy Policy

**Data Collection**
- Minimum necessary information
- Explicit consent required
- Clear usage purposes

**Data Usage**
- Training and competition management
- Communication and notifications
- Platform improvement

**Data Sharing**
- Never sold to third parties
- Shared only with explicit permission
- Secure with partners

**User Rights**
- Access your data anytime
- Request data deletion
- Opt-out of communications
- Update information

---

## Success Metrics

Track your impact:

**User Metrics**
- Total registered users
- Active monthly users
- Course completion rates
- Application submission rates

**Engagement Metrics**
- Average session duration
- Pages per session
- Return visitor rate
- Email open rates

**Business Metrics**
- Applications submitted
- Winners selected
- Funding distributed
- Businesses launched

**Impact Metrics**
- Jobs created
- Revenue generated
- Lives impacted
- Communities reached

---

**��� Built By Principie, FOR Underprivileged Rural Youth**

*Turning ideas into reality, one young entrepreneur at a time.*

---

**Last Updated:** November 26, 2025  
**Version:** 1.0.0  
**Status:** Production Ready

---
