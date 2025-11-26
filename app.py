from flask import Flask, redirect, url_for, render_template, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timezone, timedelta, datetime
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import ValidationError, Length, InputRequired, DataRequired
from flask_bcrypt import Bcrypt
import cloudinary
import cloudinary.uploader
from werkzeug.utils import secure_filename
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os
from dotenv import load_dotenv

load_dotenv()


app = Flask(__name__)


print(f" SENDGRID_API_KEY in environment: {bool(os.environ.get('SENDGRID_API_KEY'))}")
if os.environ.get('SENDGRID_API_KEY'):
    key = os.environ.get('SENDGRID_API_KEY')
    print(f" API Key starts with: {key[:10]}...")
    print(f" API Key length: {len(key)}")
else:
    print("SENDGRID_API_KEY not found in environment variables!")

app.config['SENDGRID_API_KEY'] = os.environ.get('SENDGRID_API_KEY')
app.config['SENDGRID_FROM_EMAIL'] = os.environ.get('SENDGRID_FROM_EMAIL')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'tegurasecretkey')
SENDGRID_API_KEY = app.config['SENDGRID_API_KEY']
SENDGRID_FROM_EMAIL = app.config['SENDGRID_FROM_EMAIL']
# Cloudinary Configuration
cloudinary.config(
    cloud_name=os.environ.get('CLOUDINARY_CLOUD_NAME'),
    api_key=os.environ.get('CLOUDINARY_API_KEY'),
    api_secret=os.environ.get('CLOUDINARY_API_SECRET')
)

print(f"✅ Cloudinary configured: {bool(os.environ.get('CLOUDINARY_CLOUD_NAME'))}")
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///tegura.db')
if DATABASE_URL and DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
KIGALI_TZ = timezone(timedelta(hours=2))

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' 

@login_manager.user_loader
def load_user(user_id):
    return TYI.query.get(int(user_id))

# Create model to store users (User Auth)
class TYI(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(200), nullable=False)
    lastname = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False, unique=True)
    password = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    reset_token = db.Column(db.String(200), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    # relationships to be defined later
    courses = db.relationship('UserCourse', backref='user', lazy=True)
    applications = db.relationship('Application', backref='user', lazy=True)
    messages = db.relationship('Message', backref='user', lazy=True)

    @property
    def pwd(self):
        raise AttributeError('password is not a readable attribute')

    @pwd.setter
    def pwd(self, plain_text_password):
        self.password = bcrypt.generate_password_hash(plain_text_password).decode('utf-8')

    def check_password(self, plain_text_password):
        return bcrypt.check_password_hash(self.password, plain_text_password)

    def get_initials(self):
        """Get user initials for profile"""
        return f"{self.firstname[0]}{self.lastname[0]}".upper()
    
    def get_full_name(self):
        """Get user's full name"""
        return f"{self.firstname} {self.lastname}"

# Create Courses model
class Course(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    duration_weeks = db.Column(db.Integer, nullable=False)
    level = db.Column(db.String(50), nullable=False)  # Beginner, Intermediate, Advanced
    total_modules = db.Column(db.Integer, nullable=False)
    
    # Relationship with user enrollments
    enrollments = db.relationship('UserCourse', backref='course', lazy=True)

# Create UserCourse model
class UserCourse(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tyi.id'), nullable=False)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    
    # Progress tracking
    current_module = db.Column(db.Integer, default=1)
    completed_modules = db.Column(db.Integer, default=0)
    progress_percentage = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default='in_progress')  # in_progress, completed
    enrolled_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

# Create Application model
# Update Application model
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tyi.id'), nullable=False)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('application_opportunity.id'), nullable=True)
    
    # Application details
    competition_name = db.Column(db.String(200), nullable=False)
    business_name = db.Column(db.String(200), nullable=True)
    business_idea = db.Column(db.Text, nullable=True)
    
    # Status tracking
    status = db.Column(db.String(50), default='draft')  # draft, submitted, under_review, approved, rejected
    completion_percentage = db.Column(db.Integer, default=0)
    documents_uploaded = db.Column(db.Integer, default=0)
    total_documents_required = db.Column(db.Integer, default=4)
    admin_notes = db.Column(db.Text, nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    submitted_at = db.Column(db.DateTime, nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationship
    opportunity = db.relationship('ApplicationOpportunity', backref='applications')


# Create Message model
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tyi.id'), nullable=False)
    
    # Message content
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(50), nullable=False)  # info, success, warning, error
    icon_type = db.Column(db.String(50), nullable=False)  # determines which icon to show
    
    # Status
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create model for leaderboard
class LeaderboardEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tyi.id'), nullable=False)
    
    # Leaderboard data
    total_points = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, nullable=True)
    project_name = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    
    # Relationship
    user = db.relationship('TYI', backref='leaderboard_entry', uselist=False)


# Create CourseModule model
class CourseModule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)
    module_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    content = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer, default=7)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create UserModuleProgress model
class UserModuleProgress(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('tyi.id'), nullable=False)
    module_id = db.Column(db.Integer, db.ForeignKey('course_module.id'), nullable=False)
    status = db.Column(db.String(50), default='not_started')  # not_started, in_progress, completed
    started_at = db.Column(db.DateTime, nullable=True)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    module = db.relationship('CourseModule', backref='user_progress')

# Create ApplicationOpportunity model
class ApplicationOpportunity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    requirements = db.Column(db.Text, nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    prize_amount = db.Column(db.String(100), nullable=True)
    cover_image = db.Column(db.String(500), default='new.png')  # NEW - default to new.png
    status = db.Column(db.String(50), default='open')  # open, closed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
# Create Event model
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    event_date = db.Column(db.DateTime, nullable=False)
    start_time = db.Column(db.String(50), nullable=True)
    end_time = db.Column(db.String(50), nullable=True)
    event_type = db.Column(db.String(50), default='general')  # general, deadline, workshop
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create BlogPost model
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    youtube_url = db.Column(db.String(500), nullable=False)
    cover_image = db.Column(db.String(500), nullable=True)
    publish_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_published = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Create ActivityUpdate model
class ActivityUpdate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    update_type = db.Column(db.String(50), default='general')  # general, success, warning, info
    icon_color = db.Column(db.String(50), default='blue')  # blue, green, yellow, purple, red
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

@app.template_filter('kigali_time')
def kigali_time_filter(dt):
    """Convert UTC datetime to Kigali time for display"""
    if dt is None:
        return "Unknown"
    
    # If datetime is naive (no timezone), assume it's UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    
    # Convert to Kigali time
    kigali_time = dt.astimezone(KIGALI_TZ)
    
    # Calculate time ago
    now = datetime.now(KIGALI_TZ)
    diff = now - kigali_time
    
    if diff.days > 0:
        if diff.days == 1:
            return "1 day ago"
        else:
            return f"{diff.days} days ago"
    elif diff.seconds >= 3600:
        hours = diff.seconds // 3600
        if hours == 1:
            return "1 hour ago"
        else:
            return f"{hours} hours ago"
    elif diff.seconds >= 60:
        minutes = diff.seconds // 60
        if minutes == 1:
            return "1 minute ago"
        else:
            return f"{minutes} minutes ago"
    else:
        return "Just now"

# Create form for signing up
class SignupForm(FlaskForm):
    def validate_email(self, email_to_check):
        email = TYI.query.filter_by(email=email_to_check.data).first()
        if email:
            raise ValidationError('Email Address already exists! Please try a different email.')

    firstname = StringField(label='First Name', validators=[Length(max=100, min=2), DataRequired()])
    lastname = StringField(label='Last Name', validators=[Length(max=100, min=2), DataRequired()])
    email = StringField(label='Email Adress', validators=[Length(max=100, min=2), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(max=10, min=4), DataRequired()])
    submit = SubmitField('Sign up')

# Create form for signing in
class SigninForm(FlaskForm):
    email = StringField(label='Email Adress', validators=[Length(max=100, min=2), DataRequired()])
    password = PasswordField(label='Password', validators=[Length(max=10, min=4), DataRequired()])
    submit = SubmitField('Sign in')

def upload_image_to_cloudinary(file, folder="tegura"):
    """
    Upload an image to Cloudinary and return the secure URL
    
    Args:
        file: FileStorage object from request.files
        folder: Cloudinary folder name (default: 'tegura')
    
    Returns:
        str: Cloudinary secure URL or None if upload fails
    """
    try:
        if file and file.filename:
            # Upload to Cloudinary
            result = cloudinary.uploader.upload(
                file,
                folder=folder,
                resource_type="image",
                overwrite=True,
                transformation=[
                    {'width': 1200, 'height': 800, 'crop': 'limit'},
                    {'quality': 'auto:good'}
                ]
            )
            return result['secure_url']
        return None
    except Exception as e:
        print(f"Error uploading to Cloudinary: {str(e)}")
        return None

def generate_reset_token():
    """Generate a secure random token for password reset"""
    import secrets
    return secrets.token_urlsafe(32)

def send_password_reset_email(user_email, reset_token):
    """Send password reset email via SendGrid"""
    try:
        # Find user
        user = TYI.query.filter_by(email=user_email).first()
        if not user:
            return False
        
        # Generate reset link
        reset_link = url_for('reset_password', token=reset_token, _external=True)
        
        email_subject = "Password Reset Request - Tegura Youth Initiative"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #6366f1; margin: 0;">Tegura Youth Initiative</h1>
                </div>
                
                <div style="background-color: white; padding: 30px; border-radius: 8px;">
                    <h2 style="color: #374151; margin-top: 0;">Password Reset Request</h2>
                    
                    <p>Hello <strong>{user.firstname}</strong>,</p>
                    
                    <p>We received a request to reset your password for your Tegura Youth Initiative account.</p>
                    
                    <p>Click the button below to reset your password. This link will expire in 1 hour.</p>
                    
                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_link}" style="background-color: #6366f1; color: white; padding: 14px 28px; text-decoration: none; border-radius: 8px; font-weight: bold; display: inline-block;">
                            Reset Password
                        </a>
                    </div>
                    
                    <p style="color: #6b7280; font-size: 14px;">Or copy and paste this link into your browser:</p>
                    <p style="background-color: #f3f4f6; padding: 10px; border-radius: 4px; word-break: break-all; font-size: 12px;">
                        {reset_link}
                    </p>
                    
                    <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 30px 0;">
                    
                    <p style="color: #6b7280; font-size: 14px;">
                        <strong>Didn't request a password reset?</strong><br>
                        You can safely ignore this email. Your password will not be changed.
                    </p>
                </div>
                
                <div style="text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px;">
                    <p>© 2025 Tegura Youth Initiative. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Send email via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        email_message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails=user_email,
            subject=email_subject,
            html_content=email_body
        )
        
        response = sg.send(email_message)
        
        if response.status_code in [200, 201, 202]:
            print(f"✅ Password reset email sent to {user_email}")
            return True
        else:
            print(f"⚠️ Failed to send reset email: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error sending reset email: {str(e)}")
        return False

@app.route('/', methods=['POST', 'GET'])
def index_page():
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = SigninForm()
    
    if form.validate_on_submit():
        user = TYI.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Logged in successfully!', 'success')
            return redirect(url_for('home'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = SignupForm()
    if form.validate_on_submit():
        try:
            user = TYI(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                email=form.email.data,
                pwd=form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Account created successfully!', 'success')
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error creating account: {str(e)}', 'danger')
    
    return render_template('register.html', form=form)

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email')
        
        # Find user
        user = TYI.query.filter_by(email=email).first()
        
        if user:
            # Generate reset token
            reset_token = generate_reset_token()
            
            # Set token expiry (1 hour from now) - USE UTC FOR CONSISTENCY
            user.reset_token = reset_token
            user.reset_token_expiry = datetime.utcnow() + timedelta(hours=1)  # Changed to UTC
            
            db.session.commit()
            
            # Send reset email
            if send_password_reset_email(email, reset_token):
                flash('Password reset link sent! Check your email.', 'success')
            else:
                flash('Error sending email. Please try again.', 'danger')
        else:
            # Don't reveal if email exists (security best practice)
            flash('If that email exists, a reset link has been sent.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Find user with this token
    user = TYI.query.filter_by(reset_token=token).first()
    
    # Validate token
    if not user or not user.reset_token_expiry:
        flash('Invalid or expired reset link.', 'danger')
        return redirect(url_for('login'))
    
    # Check if token expired - USE UTC FOR CONSISTENCY
    if datetime.utcnow() > user.reset_token_expiry:  # Changed to UTC
        flash('Reset link has expired. Please request a new one.', 'danger')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        new_password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validate passwords
        if not new_password or len(new_password) < 4:
            flash('Password must be at least 4 characters long.', 'danger')
            return render_template('reset_password.html', token=token)
        
        if new_password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('reset_password.html', token=token)
        
        # Update password
        user.pwd = new_password  # Uses the @pwd.setter which hashes the password
        
        # Clear reset token
        user.reset_token = None
        user.reset_token_expiry = None
        
        db.session.commit()
        
        flash('Password reset successfully! You can now login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token)

@app.route('/home', methods=['POST', 'GET'])
@login_required
def home():
    # Get user's courses
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    
    # Calculate training progress
    if user_courses:
        completed = len([c for c in user_courses if c.status == 'completed'])
        total = len(user_courses)
        overall_progress = sum(c.progress_percentage for c in user_courses) // total if total > 0 else 0
    else:
        completed = 0
        total = 0
        overall_progress = 0
    
    # Get application status
    application = Application.query.filter_by(user_id=current_user.id).first()
    
    # Get leaderboard position
    leaderboard = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()
    
    # Get unread messages count
    unread_messages = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    
    # Get open opportunities
    open_opportunities = ApplicationOpportunity.query.filter_by(status='open').order_by(ApplicationOpportunity.deadline).limit(2).all()
    
    # Get upcoming events (only future events, auto-filter past ones)
    today = datetime.now(KIGALI_TZ)
    upcoming_events = Event.query.filter(Event.event_date >= today).order_by(Event.event_date).limit(3).all()
    
    # Get published blog posts
    blog_posts = BlogPost.query.filter_by(is_published=True).order_by(BlogPost.publish_date.desc()).limit(3).all()
    
    # Get recent activity updates
    recent_activities = ActivityUpdate.query.filter_by(is_active=True).order_by(ActivityUpdate.created_at.desc()).limit(3).all()
    
    return render_template('home.html',
                         completed_courses=completed,
                         total_courses=total,
                         overall_progress=overall_progress,
                         application=application,
                         leaderboard=leaderboard,
                         unread_messages=unread_messages,
                         user_courses=user_courses,
                         opportunities=open_opportunities,
                         events=upcoming_events,
                         blogs=blog_posts,
                         activities=recent_activities)

@app.route('/contact', methods=['POST'])
def contact_form():
    try:
        # Get form data
        first_name = request.form.get('first-name')
        last_name = request.form.get('last-name')
        company = request.form.get('company', 'Not provided')
        email = request.form.get('email')
        phone = request.form.get('phone-number', 'Not provided')
        message = request.form.get('message')
        
        print(f"📧 Contact form submitted by: {first_name} {last_name} ({email})")
        
        # Validate required fields
        if not all([first_name, last_name, email, message]):
            print("❌ Missing required fields")
            flash('Please fill in all required fields.', 'danger')
            return redirect(url_for('index_page') + '#contact')  # Redirect to contact section
        
        # Check if API key exists
        if not SENDGRID_API_KEY:
            print("❌ ERROR: SENDGRID_API_KEY is not set!")
            flash('Email service is not configured. Please contact support.', 'danger')
            return redirect(url_for('index_page') + '#contact')
        
        print(f"✅ API Key is set: {SENDGRID_API_KEY[:15]}...")
        print(f"✅ From email: {SENDGRID_FROM_EMAIL}")
        
        # Create email content
        email_subject = f"New Contact Form Submission from {first_name} {last_name}"
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <h2 style="color: #6366f1; border-bottom: 2px solid #6366f1; padding-bottom: 10px;">
                    New Contact Form Submission
                </h2>
                
                <div style="background-color: white; padding: 20px; border-radius: 8px; margin-top: 20px;">
                    <h3 style="color: #374151; margin-top: 0;">Contact Information</h3>
                    
                    <table style="width: 100%; border-collapse: collapse;">
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: bold; width: 150px;">Name:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{first_name} {last_name}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Email:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">
                                <a href="mailto:{email}" style="color: #6366f1;">{email}</a>
                            </td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Phone:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{phone}</td>
                        </tr>
                        <tr>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb; font-weight: bold;">Company:</td>
                            <td style="padding: 10px; border-bottom: 1px solid #e5e7eb;">{company}</td>
                        </tr>
                    </table>
                    
                    <h3 style="color: #374151; margin-top: 30px;">Message</h3>
                    <div style="background-color: #f3f4f6; padding: 15px; border-radius: 5px; border-left: 4px solid #6366f1;">
                        {message}
                    </div>
                </div>
                
                <div style="margin-top: 20px; padding: 15px; background-color: #e0e7ff; border-radius: 5px; text-align: center;">
                    <p style="margin: 0; color: #4f46e5; font-size: 14px;">
                        📧 Sent from Tegura Youth Initiative Contact Form
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        print("📤 Attempting to send email via SendGrid...")
        
        # Send email via SendGrid
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        
        email_message = Mail(
            from_email=SENDGRID_FROM_EMAIL,
            to_emails='admin@principie.tech',
            subject=email_subject,
            html_content=email_body
        )
        
        # Add reply-to so you can reply directly to the sender
        email_message.reply_to = email
        
        response = sg.send(email_message)
        
        print(f"✅ SendGrid Response Status: {response.status_code}")
        
        if response.status_code in [200, 201, 202]:
            print("✅ Email sent successfully!")
            flash('Thank you for contacting us! We will get back to you soon.', 'success')
        else:
            print(f"⚠️ Unexpected status code: {response.status_code}")
            flash('There was an error sending your message. Please try again.', 'danger')
            
    except Exception as e:
        print(f"❌ ERROR sending email: {str(e)}")
        flash('There was an error sending your message. Please try again.', 'danger')
    
    return redirect(url_for('index_page') + '#contact')  # Redirect back to contact section

@app.route('/course/enroll/<int:course_id>', methods=['POST'])
@login_required
def enroll_course(course_id):
    # Check if course exists
    course = Course.query.get_or_404(course_id)
    
    # Check if user already enrolled
    existing_enrollment = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if existing_enrollment:
        flash('You are already enrolled in this course.', 'info')
    else:
        # Create new enrollment
        new_enrollment = UserCourse(
            user_id=current_user.id,
            course_id=course_id,
            current_module=1,
            completed_modules=0,
            progress_percentage=0,
            status='in_progress',
            enrolled_at=datetime.now(KIGALI_TZ)
        )
        db.session.add(new_enrollment)
        db.session.flush()  # Get the ID
        
        # Auto-create module progress records for all modules in the course
        modules = CourseModule.query.filter_by(course_id=course_id).all()
        for module in modules:
            module_progress = UserModuleProgress(
                user_id=current_user.id,
                module_id=module.id,
                status='not_started'
            )
            db.session.add(module_progress)
        
        db.session.commit()
        flash(f'Successfully enrolled in {course.title}!', 'success')
    
    return redirect(url_for('education'))

@app.route('/home/application')
@login_required
def application():
    # Get user's application (just the first/most recent one)
    user_application = Application.query.filter_by(user_id=current_user.id).order_by(Application.created_at.desc()).first()
    
    # Calculate days until deadline (example: Dec 30, 2025)
    from datetime import datetime
    deadline = datetime(2025, 12, 30)
    days_remaining = (deadline - datetime.now()).days if deadline > datetime.now() else 0
    
    return render_template('application.html',
                         application=user_application,
                         days_remaining=days_remaining)

@app.route('/home/education')
@login_required
def education():
    # Get user's enrolled courses
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    
    # Separate by status
    in_progress = [uc for uc in user_courses if uc.status == 'in_progress']
    completed = [uc for uc in user_courses if uc.status == 'completed']
    
    # Calculate overall stats
    total_courses = len(user_courses)
    completed_count = len(completed)
    in_progress_count = len(in_progress)
    overall_progress = sum(uc.progress_percentage for uc in user_courses) // total_courses if total_courses > 0 else 0
    
    # Get all available courses (courses user hasn't enrolled in yet)
    enrolled_course_ids = [uc.course_id for uc in user_courses]
    available_courses = Course.query.filter(~Course.id.in_(enrolled_course_ids)).all() if enrolled_course_ids else Course.query.all()
    
    return render_template('education.html',
                         in_progress_courses=in_progress,
                         completed_courses=completed,
                         total_courses=total_courses,
                         completed_count=completed_count,
                         in_progress_count=in_progress_count,
                         overall_progress=overall_progress,
                         available_courses=available_courses)

@app.route('/home/leaderboard')
@login_required
def leaderboard():
    # Get all leaderboard entries, ordered by rank
    all_entries = LeaderboardEntry.query.order_by(LeaderboardEntry.rank).all()
    
    # Get current user's leaderboard entry
    user_entry = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()
    
    # Calculate total participants
    total_participants = LeaderboardEntry.query.count()
    
    # Get top 10 entries for display
    top_entries = all_entries[:10] if len(all_entries) >= 10 else all_entries
    
    return render_template('leaderboard.html',
                         user_entry=user_entry,
                         top_entries=top_entries,
                         total_participants=total_participants)

@app.route('/home/messages')
@login_required
def messages():
    # Get all messages for current user
    all_messages = Message.query.filter_by(user_id=current_user.id).order_by(Message.created_at.desc()).all()
    
    # Count unread messages
    unread_count = Message.query.filter_by(user_id=current_user.id, is_read=False).count()
    total_count = len(all_messages)
    
    return render_template('messages.html',
                         messages=all_messages,
                         unread_count=unread_count,
                         total_count=total_count)

@app.route('/message/mark-read/<int:message_id>', methods=['POST'])
@login_required
def mark_message_read(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Security: Make sure message belongs to current user
    if message.user_id == current_user.id:
        message.is_read = True
        db.session.commit()
    
    return redirect(url_for('messages'))

@app.route('/messages/mark-all-read', methods=['POST'])
@login_required
def mark_all_messages_read():
    # Mark all unread messages for current user as read
    Message.query.filter_by(user_id=current_user.id, is_read=False).update({'is_read': True}, synchronize_session=False)
    db.session.commit()
    
    return redirect(url_for('messages'))

@app.route('/message/delete/<int:message_id>', methods=['POST'])
@login_required
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    
    # Security: Make sure message belongs to current user
    if message.user_id == current_user.id:
        db.session.delete(message)
        db.session.commit()
    
    return redirect(url_for('messages'))

@app.route('/home/profile')
@login_required
def profile():
    # Get user's statistics
    total_courses = UserCourse.query.filter_by(user_id=current_user.id).count()
    completed_courses = UserCourse.query.filter_by(user_id=current_user.id, status='completed').count()
    
    # Get leaderboard rank
    leaderboard = LeaderboardEntry.query.filter_by(user_id=current_user.id).first()
    rank = leaderboard.rank if leaderboard else 0
    
    # Get applications count
    applications_count = Application.query.filter_by(user_id=current_user.id).count()
    
    # Calculate overall progress
    user_courses = UserCourse.query.filter_by(user_id=current_user.id).all()
    if user_courses:
        overall_progress = sum(c.progress_percentage for c in user_courses) // len(user_courses)
    else:
        overall_progress = 0
    
    return render_template('profile.html',
                         total_courses=total_courses,
                         completed_courses=completed_courses,
                         rank=rank,
                         applications_count=applications_count,
                         overall_progress=overall_progress)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index_page'))


# Admin Portal Routes
ADMIN_PASSWORD = "Principie@123"

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_portal'))
        else:
            flash('Invalid admin password!', 'danger')
    
    return render_template('admin_login.html')

@app.route('/admin')
def admin_portal():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    # Get all data
    courses = Course.query.all()
    users = TYI.query.all()
    opportunities = ApplicationOpportunity.query.all()
    events = Event.query.order_by(Event.event_date.desc()).all()
    blogs = BlogPost.query.order_by(BlogPost.publish_date.desc()).all()
    activities = ActivityUpdate.query.order_by(ActivityUpdate.created_at.desc()).all()
    
    return render_template('admin.html', 
                         courses=courses, 
                         users=users,
                         opportunities=opportunities,
                         events=events,
                         blogs=blogs,
                         activities=activities,
                         LeaderboardEntry=LeaderboardEntry)


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Admin logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/course/add', methods=['POST'])
def admin_add_course():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    duration_weeks = int(request.form.get('duration_weeks'))
    total_modules = int(request.form.get('total_modules'))
    level = request.form.get('level')
    
    new_course = Course(
        title=title,
        description=description,
        duration_weeks=duration_weeks,
        total_modules=total_modules,
        level=level
    )
    
    db.session.add(new_course)
    db.session.commit()
    flash(f'Course "{title}" added successfully!', 'success')
    
    return redirect(url_for('admin_portal'))

@app.route('/admin/course/delete/<int:course_id>', methods=['POST'])
def admin_delete_course(course_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    course = Course.query.get_or_404(course_id)
    
    # Delete all user enrollments for this course first
    UserCourse.query.filter_by(course_id=course_id).delete()
    
    # Now delete the course
    db.session.delete(course)
    db.session.commit()
    flash('Course and all enrollments deleted successfully!', 'success')
    
    return redirect(url_for('admin_portal'))
@app.route('/admin/message/send', methods=['POST'])
def admin_send_message():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user_id = int(request.form.get('user_id'))
    title = request.form.get('title')
    content = request.form.get('content')
    message_type = request.form.get('message_type')
    icon_type = request.form.get('icon_type')
    
    new_message = Message(
        user_id=user_id,
        title=title,
        content=content,
        message_type=message_type,
        icon_type=icon_type,
        is_read=False,
        created_at=datetime.now(KIGALI_TZ)
    )
    
    db.session.add(new_message)
    db.session.commit()
    flash('Message sent successfully!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Add Module to Course
@app.route('/admin/course/<int:course_id>/add-module', methods=['POST'])
def admin_add_module(course_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    course = Course.query.get_or_404(course_id)
    
    module_number = int(request.form.get('module_number'))
    title = request.form.get('title')
    description = request.form.get('description')
    content = request.form.get('content')
    duration_days = int(request.form.get('duration_days'))
    
    new_module = CourseModule(
        course_id=course_id,
        module_number=module_number,
        title=title,
        description=description,
        content=content,
        duration_days=duration_days
    )
    
    db.session.add(new_module)
    db.session.commit()
    flash(f'Module "{title}" added to {course.title}!', 'success')
    
    return redirect(url_for('admin_manage_course', course_id=course_id))

# Admin - Manage Course (view modules)
@app.route('/admin/course/<int:course_id>/manage')
def admin_manage_course(course_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    course = Course.query.get_or_404(course_id)
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.module_number).all()
    
    return render_template('admin_manage_course.html', course=course, modules=modules)

# Admin - Delete Module
@app.route('/admin/module/delete/<int:module_id>', methods=['POST'])
def admin_delete_module(module_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    module = CourseModule.query.get_or_404(module_id)
    course_id = module.course_id
    
    # Delete user progress for this module
    UserModuleProgress.query.filter_by(module_id=module_id).delete()
    
    db.session.delete(module)
    db.session.commit()
    flash('Module deleted!', 'success')
    
    return redirect(url_for('admin_manage_course', course_id=course_id))

# Admin - Progress Management
@app.route('/admin/progress')
def admin_progress():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    users = TYI.query.all()
    return render_template('admin_progress.html', users=users)

# Admin - View User Progress
@app.route('/admin/progress/user/<int:user_id>')
def admin_user_progress(user_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    user = TYI.query.get_or_404(user_id)
    enrollments = UserCourse.query.filter_by(user_id=user_id).all()
    
    # Get detailed progress for each enrollment
    progress_data = []
    for enrollment in enrollments:
        modules = CourseModule.query.filter_by(course_id=enrollment.course_id).order_by(CourseModule.module_number).all()
        module_progress = []
        
        for module in modules:
            user_module = UserModuleProgress.query.filter_by(
                user_id=user_id,
                module_id=module.id
            ).first()
            
            module_progress.append({
                'module': module,
                'progress': user_module
            })
        
        progress_data.append({
            'enrollment': enrollment,
            'modules': module_progress
        })
    
    return render_template('admin_user_progress.html', user=user, progress_data=progress_data)

# Admin - Update Module Progress
@app.route('/admin/progress/module/<int:progress_id>/update', methods=['POST'])
def admin_update_module_progress(progress_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    progress = UserModuleProgress.query.get_or_404(progress_id)
    new_status = request.form.get('status')
    
    progress.status = new_status
    
    if new_status == 'in_progress' and not progress.started_at:
        progress.started_at = datetime.now(KIGALI_TZ)
    elif new_status == 'completed':
        progress.completed_at = datetime.now(KIGALI_TZ)
    
    db.session.commit()
    
    # Recalculate course progress
    update_course_progress(progress.module.course_id, UserModuleProgress.query.filter_by(module_id=progress.module_id).first().user_id)
    
    flash('Module progress updated!', 'success')
    return redirect(request.referrer)

# Helper function to update course progress
def update_course_progress(course_id, user_id):
    user_course = UserCourse.query.filter_by(user_id=user_id, course_id=course_id).first()
    
    if not user_course:
        return
    
    # Get total modules
    total_modules = CourseModule.query.filter_by(course_id=course_id).count()
    
    # Get completed modules for this user
    completed_modules = db.session.query(UserModuleProgress).join(CourseModule).filter(
        CourseModule.course_id == course_id,
        UserModuleProgress.user_id == user_id,
        UserModuleProgress.status == 'completed'
    ).count()
    
    # Calculate progress
    if total_modules > 0:
        progress_percentage = int((completed_modules / total_modules) * 100)
    else:
        progress_percentage = 0
    
    # Update UserCourse
    user_course.completed_modules = completed_modules
    user_course.progress_percentage = progress_percentage
    
    # Mark as completed if all modules done
    if completed_modules == total_modules and total_modules > 0:
        user_course.status = 'completed'
        user_course.completed_at = datetime.now(KIGALI_TZ)
    else:
        user_course.status = 'in_progress'
    
    db.session.commit()

# Admin - Application Opportunities
@app.route('/admin/opportunity/create', methods=['POST'])
def admin_create_opportunity():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    requirements = request.form.get('requirements')
    deadline_str = request.form.get('deadline')
    prize_amount = request.form.get('prize_amount')
    
    # Handle image upload
    cover_image_url = 'new.png'  # Default fallback
    if 'cover_image' in request.files:
        file = request.files['cover_image']
        if file.filename != '':
            uploaded_url = upload_image_to_cloudinary(file, folder='tegura/opportunities')
            if uploaded_url:
                cover_image_url = uploaded_url
                print(f"✅ Image uploaded: {uploaded_url}")
            else:
                flash('Image upload failed, using default image.', 'warning')
    
    # Parse deadline
    deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    
    new_opportunity = ApplicationOpportunity(
        title=title,
        description=description,
        requirements=requirements,
        deadline=deadline,
        prize_amount=prize_amount,
        cover_image=cover_image_url,  # Store Cloudinary URL
        status='open'
    )
    
    db.session.add(new_opportunity)
    db.session.commit()
    flash(f'Opportunity "{title}" created!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - View Applications
@app.route('/admin/applications')
def admin_applications():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    applications = Application.query.order_by(Application.created_at.desc()).all()
    opportunities = ApplicationOpportunity.query.all()
    
    return render_template('admin_applications.html', applications=applications, opportunities=opportunities)

# Admin - Update Application Status
@app.route('/admin/application/<int:app_id>/update', methods=['POST'])
def admin_update_application(app_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    application = Application.query.get_or_404(app_id)
    new_status = request.form.get('status')
    admin_notes = request.form.get('admin_notes')
    
    application.status = new_status
    if admin_notes:
        application.admin_notes = admin_notes
    
    if new_status in ['approved', 'rejected']:
        application.reviewed_at = datetime.now(KIGALI_TZ)
        application.completion_percentage = 100
    elif new_status == 'under_review':
        application.completion_percentage = 50
    
    db.session.commit()
    
    # Send notification to user
    notification = Message(
        user_id=application.user_id,
        title=f'Application Status Update',
        content=f'Your application for "{application.competition_name}" has been {new_status.replace("_", " ")}.',
        message_type='blue' if new_status == 'under_review' else ('green' if new_status == 'approved' else 'red'),
        icon_type='application',
        is_read=False,
        created_at=datetime.now(KIGALI_TZ)
    )
    db.session.add(notification)
    db.session.commit()
    
    flash('Application status updated and user notified!', 'success')
    return redirect(url_for('admin_applications'))

# User - View Course Details
@app.route('/course/<int:course_id>')
@login_required
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    enrollment = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    
    if not enrollment:
        flash('You need to enroll in this course first.', 'info')
        return redirect(url_for('education'))
    
    # Get modules with user progress
    modules = CourseModule.query.filter_by(course_id=course_id).order_by(CourseModule.module_number).all()
    modules_with_progress = []
    
    for module in modules:
        progress = UserModuleProgress.query.filter_by(
            user_id=current_user.id,
            module_id=module.id
        ).first()
        
        modules_with_progress.append({
            'module': module,
            'progress': progress
        })
    
    return render_template('course_detail.html', course=course, enrollment=enrollment, modules=modules_with_progress)

# User - View Module
@app.route('/course/<int:course_id>/module/<int:module_id>')
@login_required
def view_module(course_id, module_id):
    course = Course.query.get_or_404(course_id)
    module = CourseModule.query.get_or_404(module_id)
    
    # Check enrollment
    enrollment = UserCourse.query.filter_by(user_id=current_user.id, course_id=course_id).first()
    if not enrollment:
        flash('You need to enroll in this course first.', 'info')
        return redirect(url_for('education'))
    
    # Get user's progress for this module
    progress = UserModuleProgress.query.filter_by(
        user_id=current_user.id,
        module_id=module_id
    ).first()
    
    # Mark as in_progress if not started
    if progress and progress.status == 'not_started':
        progress.status = 'in_progress'
        progress.started_at = datetime.now(KIGALI_TZ)
        db.session.commit()
    
    return render_template('module_view.html', course=course, module=module, progress=progress)

# User - Browse Application Opportunities
@app.route('/opportunities')
@login_required
def opportunities():
    open_opportunities = ApplicationOpportunity.query.filter_by(status='open').all()
    user_applications = Application.query.filter_by(user_id=current_user.id).all()
    
    return render_template('opportunities.html', opportunities=open_opportunities, user_applications=user_applications)

# User - Apply to Opportunity
@app.route('/opportunity/<int:opp_id>/apply', methods=['GET', 'POST'])
@login_required
def apply_opportunity(opp_id):
    opportunity = ApplicationOpportunity.query.get_or_404(opp_id)
    
    # Check if already applied
    existing = Application.query.filter_by(
        user_id=current_user.id,
        opportunity_id=opp_id
    ).first()
    
    if existing:
        flash('You have already applied to this opportunity.', 'info')
        return redirect(url_for('opportunities'))
    
    if request.method == 'POST':
        business_name = request.form.get('business_name')
        business_idea = request.form.get('business_idea')
        
        new_application = Application(
            user_id=current_user.id,
            opportunity_id=opp_id,
            competition_name=opportunity.title,
            business_name=business_name,
            business_idea=business_idea,
            status='submitted',
            completion_percentage=25,
            submitted_at=datetime.now(KIGALI_TZ)
        )
        
        db.session.add(new_application)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('opportunities'))
    
    return render_template('apply_form.html', opportunity=opportunity)

# Admin - Create Event
@app.route('/admin/event/create', methods=['POST'])
def admin_create_event():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    event_date_str = request.form.get('event_date')
    start_time = request.form.get('start_time')
    end_time = request.form.get('end_time')
    event_type = request.form.get('event_type')
    
    # Parse date
    event_date = datetime.strptime(event_date_str, '%Y-%m-%d')
    
    new_event = Event(
        title=title,
        description=description,
        event_date=event_date,
        start_time=start_time,
        end_time=end_time,
        event_type=event_type
    )
    
    db.session.add(new_event)
    db.session.commit()
    flash(f'Event "{title}" created!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Delete Event
@app.route('/admin/event/delete/<int:event_id>', methods=['POST'])
def admin_delete_event(event_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    event = Event.query.get_or_404(event_id)
    db.session.delete(event)
    db.session.commit()
    flash('Event deleted!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Create Blog Post
@app.route('/admin/blog/create', methods=['POST'])
def admin_create_blog():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    author = request.form.get('author')
    description = request.form.get('description')
    youtube_url = request.form.get('youtube_url')
    publish_date_str = request.form.get('publish_date')
    
    # Handle image upload
    cover_image_url = '5.jpg'  # Default fallback
    if 'cover_image' in request.files:
        file = request.files['cover_image']
        if file.filename != '':
            uploaded_url = upload_image_to_cloudinary(file, folder='tegura/blogs')
            if uploaded_url:
                cover_image_url = uploaded_url
                print(f"✅ Blog image uploaded: {uploaded_url}")
            else:
                flash('Image upload failed, using default image.', 'warning')
    
    # Parse date
    publish_date = datetime.strptime(publish_date_str, '%Y-%m-%d')
    
    new_blog = BlogPost(
        title=title,
        author=author,
        description=description,
        youtube_url=youtube_url,
        cover_image=cover_image_url,  # Store Cloudinary URL
        publish_date=publish_date
    )
    
    db.session.add(new_blog)
    db.session.commit()
    flash(f'Blog post "{title}" created!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Delete Blog Post
@app.route('/admin/blog/delete/<int:blog_id>', methods=['POST'])
def admin_delete_blog(blog_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    blog = BlogPost.query.get_or_404(blog_id)
    db.session.delete(blog)
    db.session.commit()
    flash('Blog post deleted!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Create Activity Update
@app.route('/admin/activity/create', methods=['POST'])
def admin_create_activity():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    title = request.form.get('title')
    description = request.form.get('description')
    update_type = request.form.get('update_type')
    icon_color = request.form.get('icon_color')
    
    new_activity = ActivityUpdate(
        title=title,
        description=description,
        update_type=update_type,
        icon_color=icon_color
    )
    
    db.session.add(new_activity)
    db.session.commit()
    flash(f'Activity update "{title}" created!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Delete Activity Update
@app.route('/admin/activity/delete/<int:activity_id>', methods=['POST'])
def admin_delete_activity(activity_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    activity = ActivityUpdate.query.get_or_404(activity_id)
    db.session.delete(activity)
    db.session.commit()
    flash('Activity update deleted!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Update Opportunity (add cover image field)
@app.route('/admin/opportunity/update/<int:opp_id>', methods=['POST'])
def admin_update_opportunity(opp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    opportunity = ApplicationOpportunity.query.get_or_404(opp_id)
    opportunity.cover_image = request.form.get('cover_image', 'new.png')
    
    db.session.commit()
    flash('Opportunity updated!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Delete Opportunity
@app.route('/admin/opportunity/delete/<int:opp_id>', methods=['POST'])
def admin_delete_opportunity(opp_id):
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    opportunity = ApplicationOpportunity.query.get_or_404(opp_id)
    
    # Delete all applications for this opportunity
    Application.query.filter_by(opportunity_id=opp_id).delete()
    
    db.session.delete(opportunity)
    db.session.commit()
    flash('Opportunity deleted!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - Upload Leaderboard CSV
@app.route('/admin/leaderboard/upload', methods=['POST'])
def admin_upload_leaderboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    if 'csv_file' not in request.files:
        flash('No file uploaded!', 'danger')
        return redirect(url_for('admin_portal'))
    
    file = request.files['csv_file']
    
    if file.filename == '':
        flash('No file selected!', 'danger')
        return redirect(url_for('admin_portal'))
    
    if not file.filename.endswith('.csv'):
        flash('Please upload a CSV file!', 'danger')
        return redirect(url_for('admin_portal'))
    
    try:
        import csv
        import io
        
        # Read the file content
        content = file.read().decode('utf-8-sig')  # utf-8-sig handles BOM
        
        # Create StringIO object
        csv_file = io.StringIO(content)
        
        # Read CSV
        csv_reader = csv.DictReader(csv_file)
        
        # Verify headers
        expected_headers = {'rank', 'user_email', 'total_points', 'project_name', 'location'}
        if not expected_headers.issubset(set(csv_reader.fieldnames)):
            flash(f'CSV must have headers: rank, user_email, total_points, project_name, location', 'danger')
            return redirect(url_for('admin_portal'))
        
        updated_count = 0
        created_count = 0
        not_found_users = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 because row 1 is header
            try:
                # Get and validate data
                user_email = row['user_email'].strip()
                rank = int(row['rank'].strip())
                total_points = int(row['total_points'].strip())
                project_name = row['project_name'].strip()
                location = row['location'].strip()
                
                # Find user by email
                user = TYI.query.filter_by(email=user_email).first()
                
                if not user:
                    not_found_users.append(user_email)
                    continue
                
                # Check if leaderboard entry exists
                leaderboard_entry = LeaderboardEntry.query.filter_by(user_id=user.id).first()
                
                if leaderboard_entry:
                    # Update existing entry
                    leaderboard_entry.rank = rank
                    leaderboard_entry.total_points = total_points
                    leaderboard_entry.project_name = project_name
                    leaderboard_entry.location = location
                    updated_count += 1
                else:
                    # Create new entry
                    new_entry = LeaderboardEntry(
                        user_id=user.id,
                        rank=rank,
                        total_points=total_points,
                        project_name=project_name,
                        location=location
                    )
                    db.session.add(new_entry)
                    created_count += 1
                    
            except ValueError as e:
                errors.append(f"Row {row_num}: Invalid number format - {str(e)}")
            except KeyError as e:
                errors.append(f"Row {row_num}: Missing column - {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        db.session.commit()
        
        # Build success message
        message = f'✅ Leaderboard updated! {created_count} created, {updated_count} updated.'
        
        if not_found_users:
            message += f' ⚠️ Users not found: {", ".join(not_found_users[:5])}'
            if len(not_found_users) > 5:
                message += f' (and {len(not_found_users) - 5} more)'
        
        if errors:
            message += f' ⚠️ Errors: {"; ".join(errors[:3])}'
            if len(errors) > 3:
                message += f' (and {len(errors) - 3} more)'
        
        flash(message, 'success' if not errors else 'warning')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error processing CSV: {str(e)}', 'danger')
    
    return redirect(url_for('admin_portal'))

# Admin - Clear Leaderboard
@app.route('/admin/leaderboard/clear', methods=['POST'])
def admin_clear_leaderboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    LeaderboardEntry.query.delete()
    db.session.commit()
    flash('Leaderboard cleared!', 'success')
    
    return redirect(url_for('admin_portal'))

# Admin - View Current Leaderboard
@app.route('/admin/leaderboard')
def admin_leaderboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    entries = LeaderboardEntry.query.order_by(LeaderboardEntry.rank).all()
    return render_template('admin_leaderboard.html', entries=entries)

with app.app_context():
    try:
        db.create_all()
        print("✅ Database tables initialized successfully!")
    except Exception as e:
        print(f"⚠️ Database initialization info: {str(e)}")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') != 'production'
    )