from django.db import models
from django.contrib.localflavor.us.forms import USPhoneNumberField
from django.forms import ModelForm, Form, CharField


# Create your models here.
class Score(models.Model):
	# This should be team_name for consistency..
	team_name = models.CharField(max_length=255, db_index=True)
	year = models.IntegerField()
	hour = models.IntegerField(db_index=True)
	place = models.IntegerField(db_index=True)
	score = models.IntegerField(db_index=True)

	def __unicode__(self):
		return 'Team: %s, %d Hour %d' % (self.team_name, self.year, self.hour)

class AvailableHours(models.Model):
	year = models.IntegerField()
	hour = models.IntegerField()

class Settings(models.Model):
	lastyear = models.IntegerField()
	lasthour = models.IntegerField()

class EmailSubscriber(models.Model):
	email = models.EmailField(db_index=True)
	team_name = models.CharField(max_length=36,  help_text="(optional)", blank=True, null=True)

	def __unicode__(self):
		if self.team_name:
			return "%s - %s" % (self.email, self.team_name)
		else:
			return self.email
			
	#def __repr__(self):
		#return self.__unicode__()
		
class EmailSubscriberForm(ModelForm):
	class Meta:
		model = EmailSubscriber
		
class EmailUnsubscribeForm(Form):
	pass

class SMSSubscriber(models.Model):
	phone_number = models.CharField(max_length=14, db_index=True)
	team_name = models.CharField(max_length=36, blank=True, null=True)
	
	def __unicode__(self):
		if self.team_name:
			return "%s - %s" % (self.phone_number, self.team_name)
		else:
			return self.phone_number
			
	#def __repr__(self):
		#return self.__unicode__()
		
class SMSUnsubscribeForm(Form):
	pass

class SMSSubscriberForm(Form):
	phone_number = CharField(max_length=14)
	team_name = CharField(max_length=36, help_text="(optional)", required=False)
	#class Meta:
		#model = SMSSubscriber
		
class SearchForm(Form):
	search = CharField(max_length=100)