from app import app
import mongoengine.errors
from flask import render_template, flash, redirect, url_for
from flask_login import current_user
from app.classes.data import Club
from app.classes.forms import ClubForm
from flask_login import login_required
import datetime as dt

@app.route('/club/new', methods=['GET', 'POST'])
# This means the user must be logged in to see this page
@login_required
# This is a function that is run when the user requests this route.
def clubNew():
    # This gets the form object from the form.py classes that can be displayed on the template.
    form = ClubForm()

    # This is a conditional that evaluates to 'True' if the user submitted the form successfully.
    # validate_on_submit() is a method of the form object. 
    if form.validate_on_submit():

        # This stores all the values that the user entered into the new club form. 
        # Club() is a mongoengine method for creating a new club. 'newClub' is the variable 
        # that stores the object that is the result of the Club() method.  
        newClub = Club(
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
        newClub.save()

        # Once the new club is saved, this sends the user to that club using redirect.
        # and url_for. Redirect is used to redirect a user to different route so that 
        # routes code can be run. In this case the user just created a club so we want 
        # to send them to that club. url_for takes as its argument the function name
        # for that route (the part after the def key word). You also need to send any
        # other values that are needed by the route you are redirecting to.
        return redirect(url_for('club',clubID=newClub.id))

    # if form.validate_on_submit() is false then the user either has not yet filled out
    # the form or the form had an error and the user is sent to a blank form. Form errors are 
    # stored in the form object and are displayed on the form. take a look at clubform.html to 
    # see how that works.
    return render_template('clubform.html',form=form)

@app.route('/club/<clubID>')
# This route will only run if the user is logged in.
@login_required
def club(clubID):
    # retrieve the club using the clubID
    thisClub = Club.objects.get(id=clubID)
    # Send the club object to the 'club.html' template.
    return render_template('club.html',club=thisClub)

# This is the route to list all clubs
@app.route('/club/list')
@app.route('/clubs')
# This means the user must be logged in to see this page
@login_required
def clubList():
    # This retrieves all of the 'clubs' that are stored in MongoDB and places them in a
    # mongoengine object as a list of dictionaries name 'clubs'.
    clubs = Club.objects()
    # This renders (shows to the user) the clubs.html template. it also sends the clubs object 
    # to the template as a variable named clubs.  The template uses a for loop to display
    # each club.
    return render_template('clubs.html',clubs=clubs)

# This route enables a user to edit a club.  This functions very similar to creating a new 
# club except you don't give the user a blank form.  You have to present the user with a form
# that includes all the values of the original club. Read and understand the new club route 
# before this one. 
@app.route('/club/edit/<clubID>', methods=['GET', 'POST'])
@login_required
def clubEdit(clubID):
    editClub = Club.objects.get(id=clubID)
    # if the user that requested to edit this club is not the author then deny them and
    # send them back to the club. If True, this will exit the route completely and none
    # of the rest of the route will be run.
    if current_user != editClub.author:
        flash("You can't edit a club you don't own.")
        return redirect(url_for('club',clubID=clubID))
    # get the form object
    form = ClubForm()
    # If the user has submitted the form then update the club.
    if form.validate_on_submit():
        # update() is mongoengine method for updating an existing document with new data.
        editClub.update(
            name = form.name.data,
            advisor = form.advisor.data,
            description = form.description.data,
            meeting_day = form.meeting_day.data,
            meeting_time = form.meeting_time.data,
            meeting_place = form.meeting_place.data,
            modify_date = dt.datetime.utcnow
        )
        # After updating the document, send the user to the updated club using a redirect.
        return redirect(url_for('club',clubID=clubID))

    # if the form has NOT been submitted then take the data from the editClub object
    # and place it in the form object so it will be displayed to the user on the template.
    form.name.data = editClub.name
    form.advisor.data = editClub.advisor
    form.description.data = editClub.description
    form.meeting_day.data = editClub.meeting_day
    form.meeting_time.data = editClub.meeting_time
    form.meeting_place.data = editClub.meeting_place


    # Send the user to the club form that is now filled out with the current information
    # from the form.
    return render_template('clubform.html',form=form)

@app.route('/club/delete/<clubID>')
# Only run this route if the user is logged in.
@login_required
def clubDelete(clubID):
    # retrieve the club to be deleted using the clubID
    deleteClub = Club.objects.get(id=clubID)
    # check to see if the user that is making this request is the author of the club.
    # current_user is a variable provided by the 'flask_login' library.
    if current_user == deleteClub.author:
        # delete the club using the delete() method from Mongoengine
        deleteClub.delete()
        # send a message to the user that the club was deleted.
        flash('The club was deleted.')
    else:
        # if the user is not the author tell them they were denied.
        flash("You can't delete a club you don't own.")
    # Retrieve all of the remaining clubs so that they can be listed.
    clubs = Club.objects()  
    # Send the user to the list of remaining clubs.
    return render_template('clubs.html',clubs=clubs) 

@app.route('/club/join/<clubID>', methods=["POST"])
@login_required
def joinClub(clubID):
    club = Club.objects.get(id=clubID)

    # Prevent duplicate joining
    if current_user not in club.members:
        club.members.append(current_user)
        club.save()
        flash('You have successfully joined the club.')
    else:
        flash('You already joined this club.')

    return redirect(url_for('club', clubID=clubID))
