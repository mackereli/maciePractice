from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Sport
from app.classes.forms import SportForm
from flask_login import login_required
import datetime as dt

@app.route('/sport/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def sportNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = SportForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new sport form. 
        # Sport() is a mongoengine method for creating a new sport. 'newSport' is the variable 
        # that stores the object that is the result of the Sport() method.  
        newSport = Sport(
            # the left side is the name of the field from the data table
            # the right side is the data the user entered which is held in the form object.
            name = form.name.data,
            advisor = form.advisor.data,
            description = form.description.data,
            meeting_day = form.meeting_day.data,
            meeting_time = form.meeting_time.data,
            meeting_place = form.meeting_place.data,

            author = current_user.id,
            # This sets the modifydate to the current datetime.
            modify_date = dt.datetime.utcnow
        )
        # This is a method that saves the data to the mongoDB database.
        newSport.save()

        # Once the new sport is saved, this sends the user to that sport using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a sport so we want 
        # to send them to that sport. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('sport',sportID=newSport.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at sportform.html to 
    # see how that works.
    return render_template('sportform.html',form=form)
