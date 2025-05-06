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

        newSport = Sport(
            name = form.name.data,
            coach = form.coach.data,
            description = form.description.data,
            meeting_day = form.meeting_day.data,
            meeting_time1 = form.meeting_time1.data,            
            meeting_time2 = form.meeting_time2.data,
            meeting_place = form.meeting_place.data,
            time_frame = form.time_frame.data,
            author = current_user.id,
            modify_date = dt.datetime.utcnow
        )

        newSport.save()
        return redirect(url_for('sport', sportID=newSport.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at sportform.html to 
    # see how that works.
    return render_template('sportform.html',form=form)

@app.route('/sport/<sportID>')
# This route will only run if the user is logged in.
@login_required
def sport(sportID):
    # retrieve the sport using the sportID
    thisSport = Sport.objects.get(id=sportID)
    # Send the sport object to the 'sport.html' template.
    return render_template('sport.html',sport=thisSport)

# This is the route to list all sports
@app.route('/sport/list')
@app.route('/sports')
# This means the user must be logged in to see this page
@login_required
def sportList():
    # This retrieves all of the 'sports' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'sports'.
    sports = Sport.objects()
    # This renders (shows to the user) the sports.html template. it also sends the sports object 
    # to the template as a variable named sports.  The template uses a for loop to display
    # each sport.
    return render_template('sports.html',sports=sports)

# This route enables a user to edit a sport.  This functions very similar to creating a new 
# sport except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original sport. Read and understand the new sport route 
# before this one. 
@app.route('/sport/edit/<sportID>', methods=['GET', 'POST'])
@login_required
def sportEdit(sportID):
    editSport = Sport.objects.get(id=sportID)
    # if the user that requested to edit this sport is not the author then deny them and
    # send them back to the sport. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editSport.author:
        flash("You can't edit a sport you don't own.")
        return redirect(url_for('sport',sportID=sportID))
    # get the form object
    form = SportForm()
    # If the user has submitted the form then update the sport.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editSport.update(
            name = form.name.data,
            coach = form.coach.data,
            description = form.description.data,
            meeting_day = form.meeting_day.data,
            meeting_time1 = form.meeting_time1.data,
            meeting_time2 = form.meeting_time2.data,
            time_frame = form.time_frame.data,
            meeting_place = form.meeting_place.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated sport using a redirect.
        return redirect(url_for('sport',sportID=sportID))

    # if the form has NOT been submitted then take the data from the editSport object
    # and place it in the form object so it will be displayed to the user on the template.
    form.name.data = editSport.name
    form.coach.data = editSport.coach
    form.description.data = editSport.description
    form.meeting_day.data = editSport.meeting_day
    form.meeting_time1.data = editSport.meeting_time1
    form.meeting_time2.data = editSport.meeting_time2
    form.time_frame.data = editSport.time_frame
    form.meeting_place.data = editSport.meeting_place


    # Send the user to the sport form that is now filled out with the current information
    # from the form.
    return render_template('sportform.html',form=form)

@app.route('/sport/delete/<sportID>')
# Only run this route if the user is logged in.
@login_required
def sportDelete(sportID):
    # retrieve the sport to be deleted using the sportID
    deleteSport = Sport.objects.get(id=sportID)
    # check to see if the user that is making this request is the author of the sport.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteSport.author:
        # delete the sport using the delete() method from Mongoengine
        deleteSport.delete()
        # send a message to the user that the sport was deleted.
        flash('The sport was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a sport you don't own.")
    # Retrieve all of the remaining sports so that they can be listed.
    sports = Sport.objects()  
    # Send the user to the list of remaining sports.
    return render_template('sports.html',sports=sports) 
