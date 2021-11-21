from django.db import models
import re
from datetime import date
from datetime import datetime
from django.db.models.deletion import CASCADE
import bcrypt
EMAIL_REGEX = re.compile('^[_a-z0-9-]+(.[_a-z0-9-]+)@[a-z0-9-]+(.[a-z0-9-]+)(.[a-z]{2,4})$')

class UserManager(models.Manager):
    def registration_validator(self, post_data):
        errors = {}
        #length of the first name
        if len(post_data['first_name']) < 2:
            errors['first_name'] = "First name must be 2 characters or more"
        # length of last NameError
        if len(post_data['last_name']) < 2:
            errors['last_name'] = "Last name must be 2 characters or more"
        # email matches format
        # email_regex = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-z]+$')
        if len(post_data['email'])==0:
            errors['email'] = "You must enter an email"
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Must be a valid email"
        # email is unique
        current_users = User.objects.filter(email = post_data['email'])
        if len(current_users) > 0:
            errors['duplicate'] = "Email already in use"
        # password was entered
        if len(post_data['password']) < 8:
            errors['password'] = "Password must be at least 8 characters long"
        #matches
        if post_data['password'] != post_data['confirm_password']:
            errors['nonmatch'] = "Your password does not match"
        if post_data['dob'] == '':
            errors['date'] = "Please enter your birthday"
        if len(post_data['location']) <= 4:
            errors['location'] = "Please enter your city and state in the required format"
        return errors
    
    def login_validator(self, post_data):
        errors = {}
        existing_user = User.objects.filter(email=post_data['email'])
        if len(existing_user) == None:
            errors['email'] = "Email not registered yet"
            return errors
        if len(post_data['email']) == 0:
            errors['email'] = "Enter email"
        if len(post_data['password']) < 8:
            errors['password'] = "Enter 8 character password"
        if not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Must be a valid email"
        elif bcrypt.checkpw(post_data['password'].encode(), existing_user[0].password.encode()) != True:
            errors['nonmatch'] = "Email and password do not match"
        return errors
    
    def update_validator(self, post_data):
        errors = {}
        if len(post_data['first_name']) == 0:
            errors['first_name'] = "Please enter a first name!"
        if len(post_data['last_name']) == 0:
            errors['last_name'] = "Please enter a last name!"
        if len(post_data['email']) == 0:
            errors['email'] = "Enter email"
        if post_data['dob'] == '':
            errors['date'] = "Please enter your birthday"
        if len(post_data['location']) <= 4:
            errors['location'] = "Please enter your city and state in the required format"
        elif not EMAIL_REGEX.match(post_data['email']):
            errors['email'] = "Must be a valid email"
        return errors

class EventManager(models.Manager):
    def event_validator(self, post_data):
        errors = {}
        existing_event = Event.objects.filter(title=post_data['title'])
        if len(post_data['title']) <= 8:
            errors['title'] = "Please enter a descriptive title"
        if len(post_data['description']) <= 8:
            errors['description'] = "Please enter a better description of your event"
        if len(post_data['sport']) <= 2:
            errors['sport'] = "Please enter the sport"
        if len(post_data['city']) <= 2:
            errors['city'] = "Please enter the City that the event is taking place in"
        if len(post_data['address']) <= 10:
            errors['address'] = "Please enter the address that the event is being held"
        if len(post_data['day']) == "":
            errors['day'] = "Please enter the date of the event"
        if len(existing_event) > 0:
            errors['duplicate'] = "Event title already in use, please check to make sure you have not already created this event"
        return errors
    
    def update_event_validator(self, post_data):
        errors = {}
        existing_event = Event.objects.filter(title=post_data['title'])
        if len(post_data['title']) <= 8:
            errors['title'] = "Please enter a descriptive title"
        if len(post_data['description']) <= 8:
            errors['description'] = "Please enter a better description of your event"
        if len(post_data['sport']) <= 2:
            errors['sport'] = "Please enter the sport"
        if len(post_data['city']) <= 2:
            errors['city'] = "Please enter the City that the event is taking place in"
        if len(post_data['address']) <= 10:
            errors['address'] = "Please enter the address that the event is being held"
        if len(post_data['day']) == "":
            errors['day'] = "Please enter the date of the event"
        if len(existing_event) > 1:
            errors['duplicate'] = "Event title already in use, please check to make sure you have not already created this event"
        return errors

class CommentManager(models.Manager):
    def comment_validator(self, post_data):
        errors = {}
        if len(post_data['message']) <= 1:
            errors['message'] = "Post must be at least 2 characters long"
        return errors

class ReplyManager(models.Manager):
    def reply_validator(self, post_data):
        errors = {}
        if len(post_data['message']) <= 1:
            errors['reply'] = "Reply must be at least 2 characters long"
        return errors


class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    dob = models.DateField()
    location = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = UserManager()
    def __str__(self):
        return '%s %s' % (self.first_name, self.last_name)

class Event(models.Model):
    title = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    sport = models.CharField(max_length=50)
    city = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    day = models.DateField()
    attending = models.ManyToManyField(User, related_name='attendingEvents')
    creator = models.ForeignKey(User, related_name='createdEvents', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = EventManager()
    def __str__(self):
        return '%s %s' % (self.title, self.description)

class Comment_Thread(models.Model):
    message = models.CharField(max_length=500)
    poster = models.ForeignKey(User, related_name='user_messages', on_delete=CASCADE)
    event = models.ForeignKey(Event, related_name='event_messages', on_delete=CASCADE)
    likes = models.ManyToManyField(User, related_name='liked_posts')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = CommentManager()
    def __str__(self):
        return self.message
    
class Reply(models.Model):
    reply = models.CharField(max_length=255)
    poster = models.ForeignKey(User, related_name='user_replies', on_delete=CASCADE)
    original_post = models.ForeignKey(Comment_Thread, related_name='post_comments', on_delete=CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = ReplyManager()
    def __str__(self):
        return self.reply