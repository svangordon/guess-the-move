from app.api import bp
from app import testing_options_dir

import os

from flask import current_app


# from secrets import password
import datetime
import itertools
from functools import wraps
import os
# import path
import string
import time

from flask_mail import Message
from flask_mail import Mail
from operator import itemgetter 
from flask import Flask, render_template, jsonify, request, session, make_response, send_from_directory
from jinja2 import StrictUndefined
from flask_cors import CORS, cross_origin
from flask_restful import  Api, Resource, reqparse
from werkzeug.security import generate_password_hash, check_password_hash
import uuid
import jwt
from app.models import Student, StudentGroup, Item, Group, GroupNote, StudentItem, StudentTestResult, ReadingLevel, connect_to_db, db, User


# from app import app

# current_app.config.from_object(__name__)
@bp.route('/', defaults={'path': ''})
@bp.route('/<path:path>')
def index(path):
    return render_template('index.html')


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token' in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({'message': 'Token is missing'}), 401

        try:
            data = jwt.decode(token, current_app.config['SECRET_KEY'])
            current_user = User.query.filter_by(
                public_id=data['public_id']).first()
        except:
            return jsonify({'message': 'Token is invalid'})
        return f(current_user, *args, **kwargs)
    return decorated





@bp.route("/item_list/<item_type>")
@token_required
def read_txt_file(current_user, item_type):
    unassigned_items = {'itemType': item_type, 'items': {} }
    # if item_type == "words":
    #     fname = ["other words.txt", "dolch 2.txt", "dolch primer.txt",  "dolch pre primer.txt"]
    # if item_type == "sounds":
    #     fname=["sounds.txt", "digraphs.txt", "r controlled vowels.txt", "vowel patterns.txt", "blends.txt"]
    # if item_type == "letters":
    #     fname = ["capital letters.txt", "lowercase letters.txt"]
    
    fnames = [os.path.join(testing_options_dir, item_type, fname) for fname in os.listdir(os.path.join(testing_options_dir, item_type))]

    for fn in fnames:
            with open(fn) as f:
                content = f.readlines()
                content = [x.strip() for x in content] 
                unassigned_items['items'][fn[0:-4]] = content

    return jsonify(unassigned_items)


@bp.route("/reading-levels")
@token_required
def get_reading_levels(current_user):
    fname = "reading-levels.txt"
    with open(os.path.join(testing_options_dir, fname)) as fn:
        reading_levels = fn.readlines()
        reading_levels = [x.strip() for x in reading_levels] 
    return jsonify(reading_levels)

@bp.route("/students/<student_id>/reading-level", methods=['POST'])
@token_required
def add_reading_level(current_user, student_id):
    user_id = current_user.public_id
    data = request.get_json()
    student_id = data.get('student')[0]
    reading_level = data.get('readingLevel')

    student_reading_level = ReadingLevel.query.filter_by(user_id=user_id, student_id=student_id).first()
    if student_reading_level:
        student_reading_level.reading_level = reading_level
        # student_reading_level.update_date = date.today()
        student_reading_level.update_date = db.func.current_timestamp()
        db.session.commit()
    else:
        db.session.add(ReadingLevel(student_id=student_id, user_id=user_id, reading_level=reading_level))
        db.session.commit()

    return jsonify(data)

@bp.route("/students/reading-levels")
@token_required
def get_student_reading_leels(current_user):
    user_id = current_user.public_id
    reading_levels = ReadingLevel.query.filter_by(user_id=user_id).options(
    db.joinedload('students')).filter_by(user_id=user_id).all()
    reading_level_dict = {}
    for entry in reading_levels:
        if entry.reading_level not in reading_level_dict:
            reading_level_dict[entry.reading_level] = [entry.students.name]
        else:
            reading_level_dict[entry.reading_level].append(entry.students.name)

    return jsonify(reading_level_dict)


def get_item_student_list(item_object):
    student_list = []
    unlearned_student_list =[]
    for item in item_object.studentitems:
        if item.Learned == True:
            student = Student.query.filter_by(student_id=item.student_id).first()
            student_list.append(student.name)
        else:
            student = Student.query.filter_by(student_id=item.student_id).first()
            unlearned_student_list.append(student.name)
    return [student_list, unlearned_student_list]

    
@bp.route("/items/<item_type>")
@token_required
def get_items(current_user, item_type):
    start = time.time()
    user_id = current_user.public_id
    items = StudentItem.query.filter_by(user_id=user_id).filter_by(item_type=item_type).options(
    db.joinedload('items')).filter_by(user_id=user_id).filter_by(item_type=item_type).options(
        db.joinedload('students')).filter_by(user_id=user_id).all()
    item_list =[]
    items_dict = {}
    for item in items:
        if not items_dict.get(item.items.item_id):
            items_dict[item.items.item_id] = {"item": item.items.item, "itemId": item.items.item_id, "itemType": item.item_type, "unlearnedCount": 0, "learnedCount": 0, "unlearnedStudents": [], "learnedStudents": [], "totalCount": 0}
        prefix = "un" if item.Learned == False else ""
        key = "{}learned".format(prefix)
        items_dict[item.items.item_id][key + "Count"] += 1
        items_dict[item.items.item_id]["totalCount"] += 1
        items_dict[item.items.item_id][key + "Students"].append(item.students.name)
    end = time.time()
    elapsed_time = end - start
    return jsonify(items_dict)

# # Expected query params: type
# @bp.route("/items")
# @token_required
# def get_items(current_user):
#     start = time.time()
#     user_id = current_user.public_id
#     item_type = request.args.get('item_type')
#     items = StudentItem.query.filter_by(user_id=user_id).filter_by(item_type=item_type).options(
#     db.joinedload('items')).filter_by(user_id=user_id).filter_by(item_type=item_type).options(
#         db.joinedload('students')).filter_by(user_id=user_id).all()
#     item_list =[]
#     items_dict = {}
#     for item in items:
#         if not items_dict.get(item.items.item_id):
#             items_dict[item.items.item_id] = {"item": item.items.item, "itemId": item.items.item_id, "itemType": item.item_type, "unlearnedCount": 0, "learnedCount": 0, "unlearnedStudents": [], "learnedStudents": [], "totalCount": 0}
#         prefix = "un" if item.Learned == False else ""
#         key = "{}learned".format(prefix)
#         items_dict[item.items.item_id][key + "Count"] += 1
#         items_dict[item.items.item_id]["totalCount"] += 1
#         items_dict[item.items.item_id][key + "Students"].append(item.students.name)
#     end = time.time()
#     elapsed_time = end - start
#     return jsonify(items_dict)
            


    
@bp.route("/items/<item_type>/<item>")
@token_required
def item_detail(current_user, item_type, item):
    """Display item and students who are learning that item"""
    user_id = current_user.public_id
    item_object = Item.query.filter_by(item_id=item, user_id=user_id).first()
    student_items = StudentItem.query.filter_by(
        item_id=item).options(db.joinedload('students')).all()
    learned_student_list = []
    unlearned_student_list =[]
    item_detail = {}

    for student in student_items:
        if student.Learned == False:
            student = {
                'student_id': student.students.student_id,
                'name': student.students.name
                }
            unlearned_student_list.append(student)

        else:
            student = {
                'student_id': student.students.student_id,
                'name': student.students.name
                }
            learned_student_list.append(student)

    item_object = {
        'item_id': item_object.item_id,
        'item': item_object.item,
        'date': item_object.date_added,
        'itemType': item_object.item_type
    }
    item_detail['unlearnedStudentList'] = unlearned_student_list
    item_detail['learnedStudentList'] = learned_student_list
    item_detail['item'] = item_object
    return jsonify(item_detail)

# @bp.route("/unassigned-students/<item>")
@bp.route("/items/<item>")
@token_required
def get_unassigned_students_item(current_user, item):
    """gets students are not assigned to item"""
    user_id = current_user.public_id
    students = StudentItem.query.filter_by(
        item_id=item, user_id=user_id).options(db.joinedload('students')).all()
    student_ids = []
    for student in students:
        student_ids.append(student.student_id)

    unassigned_students = Student.query.filter_by(user_id=user_id).filter(Student.student_id.notin_(student_ids)).all()
    student_list = []

    for student in unassigned_students:
        student = {
            'student_id': student.student_id,
            'student': student.name 
            
        }

        student_list.append(student)
    # student_list = sorted(student_list, key=itemgetter('student'))
    return jsonify([student_list])

@bp.route("/add-student", methods=['POST'])
@token_required
def add_student(current_user):
    user_id = current_user.public_id
    data = request.get_json()

    names = data.get("names")
    names = names.splitlines()
    db.session.bulk_save_objects(
        [
            Student(
                name=name,
                user_id=user_id,
            )
            for name in names
        ]
    )    
    db.session.commit()
    return jsonify(data)

@bp.route("/delete-item", methods=['POST'])
@token_required
def delete_item(current_user):
    data = request.get_json()
    item_id = data.get("item")
    item_type = data.get("itemType")
    user_id = current_user.public_id
    item = Item.query.filter_by(
        item_id=item_id, user_id=user_id).first()
    db.session.delete(item)
    db.session.commit()
    return item_type
  

@bp.route("/add-item", methods=['POST'])
@token_required
def add_item(current_user, ):
    data = request.get_json()
    items = data['item']
    item_type = data['itemType']
    user_id = current_user.public_id
    user_items = Item.query.filter_by(user_id=user_id).filter_by(item_type=item_type).all()
    user_list = [user.item for user in user_items]
    list_to_add = list(set(items).difference(user_list))
    db.session.bulk_save_objects(
        [
            Item(
                item=item,
                user_id=user_id,
                item_type=item_type
            )
            for item in list_to_add
        ]
    )    
    db.session.commit()
    student_data = {'items': list_to_add, 'itemType':item_type}
    return jsonify(student_data)

@bp.route('/add-new-items-to-students', methods=['POST'])
@token_required
def add_new_items_to_students(current_user):
    user_id = current_user.public_id
    data = request.get_json()
    items = data['studentItems'].get('items')
    item_type = data['studentItems'].get('itemType')
    item_list = Item.query.filter(Item.item.in_(items)).filter(Item.user_id == user_id).filter(Item.item_type==item_type).all()
    student_list = Student.query.filter_by(user_id = user_id).all()
    if student_list == []:
        return "no students"
    
    else:
        item_ids = [item.item_id for item in item_list]
        student_ids = [student.student_id for student in student_list]

        db.session.bulk_save_objects(
            [
                StudentItem(
                    item_id=item_id,
                    student_id=student_id,
                    item_type=item_type,
                    user_id=user_id
                )
                for item_id, student_id in itertools.product(item_ids, student_ids)
            ]
        )
        db.session.commit()
        return "items added!"


@bp.route("/add-custom-item", methods=['POST'])
@token_required
def add_custom_item(current_user):
    data = request.get_json()
    items = data['item']
    item_type = data['itemType']
    user_id = current_user.public_id
    table = str.maketrans({key: None for key in string.punctuation})
    new_string = items.translate(table) 
    new_items = new_string.split()
    user_items = Item.query.filter_by(user_id=user_id).filter_by(item_type=item_type).all()
    user_list = [user.item for user in user_items]
    list_to_add = list(set(new_items).difference(user_list))
    db.session.bulk_save_objects(
        [
            Item(
                item=item,
                user_id=user_id,
                item_type=item_type,
                custom= True
            )
            for item in list_to_add
        ]
    )    
    db.session.commit()
    return jsonify(data)

@bp.route('/add-custom-items-to-student', methods=['POST'])
@token_required
def add_custom_items_to_student(current_user):
    user_id = current_user.public_id
    data = request.get_json()
    items = (data['studentItems'].get('item'))
    item_type = data['studentItems'].get('itemType')
    student_id = data.get('studentId')
    items = items.split()
    item_list = Item.query.filter(Item.item.in_(items)).filter(Item.user_id == user_id).filter(Item.item_type==item_type).all()
    item_ids = [item.item_id for item in item_list]
    db.session.bulk_save_objects(
            [
                StudentItem(
                    item_id=item_id,
                    student_id=student_id,
                    item_type=item_type,
                    user_id=user_id
                )
                for item_id in item_ids
            ]
        )
    db.session.commit()
    return "items added!"



@bp.route('/add-items-to-new-students', methods=['POST'])
@token_required
def add_items_to__new_students(current_user):
    data = request.get_json()
    names = data.get("names")
    table = str.maketrans({key: None for key in string.punctuation})
    new_names = names.translate(table)  
    new_names = new_names.splitlines()
    user_id = current_user.public_id
    student_list = Student.query.filter(Student.name.in_(new_names)).filter(Student.user_id == user_id).all()
    item_list = Item.query.filter_by(user_id = user_id).filter_by(custom = False ).all()
    items = [(item.item_id, item.item_type)for item in item_list]
    student_ids = [student.student_id for student in student_list]
    db.session.bulk_save_objects(
        [
            StudentItem(
                item_id=items[0],
                student_id=student_id,
                item_type=items[1],
                user_id=user_id
            )
            for items, student_id in itertools.product(items, student_ids)
        ]
    )
    db.session.commit()
    return "student items added!"


@bp.route("/students/<student_id>", methods=['DELETE'])
@token_required
def delete_student(current_user, student_id):
    # student_id = request.get_json()
    user_id = current_user.public_id
    student = Student.query.filter_by(
        student_id=student_id, user_id=user_id).first()
    db.session.delete(student)
    db.session.commit()
    return 'student deleted!'

@bp.route("/students")
@token_required
def get_students(current_user):
    start = time.time()
    user_id = current_user.public_id
    students = Student.query.filter_by(user_id=user_id).options(
        db.joinedload('studentitems')).options(db.joinedload('studenttestresults')).options(db.joinedload('studentgroups')).options(db.joinedload('readinglevels')).all()
    student_dict = {}
    for student in students:
        student_dict[student.student_id] = {
                'studentId': student.student_id, 
                'name': student.name, 
                'wordCount': 0, 
                'totalWordCount': 0, 
                'unlearnedWordCount': 0, 
                'wordList':[], 
                'unlearnedWordList': [], 
                'lastWordTest': "",
                'letterCount': 0, 
                'unlearnedLetterCount': 0,
                'totalLetterCount': 0, 
                'letterList':[], 
                'unlearnedLetterList': [],
                'lastLetterTest': "",
                'soundCount': 0,
                'unlearnedSoundCount': 0,
                'soundList': [],
                'unlearnedSoundList': [],
                'totalSoundCount': 0,
                'lastSoundTest': "",
                'readingLevel': "",
                'lastReadingLevelUpdate': "",
                'group': ""
                }
        tests = get_student_test_dates(student)
        wordTest = tests.get('lastWordTest')
        if wordTest == None:
            wordTest = ""
        letterTest = tests.get('lastLetterTest')
        if letterTest == None:
            letterTest = ""
        soundTest = tests.get('lastSoundTest')
        if soundTest == None:
            soundTest = ""
        student_dict[student.student_id]['lastWordTest'] = wordTest
        student_dict[student.student_id]['lastLetterTest'] = letterTest
        student_dict[student.student_id]['lastSoundTest'] = soundTest
        student_dict[student.student_id]['group'] = get_student_group(student, user_id)
        student_dict[student.student_id]['readingLevel'] = get_all_student_reading_levels(student)[0]
        student_dict[student.student_id]['lastReadingLevelUpdate'] = get_all_student_reading_levels(student)[1]
        items = StudentItem.query.filter_by(user_id=user_id, student_id=student.student_id).options(db.joinedload('items')).all()
        item_dict = get_student_item_dict(items)
        student_dict[student.student_id]['wordList'] = item_dict.get("wordList")
        student_dict[student.student_id]['letterList'] = item_dict.get("letterList")
        student_dict[student.student_id]['soundList'] = item_dict.get("soundList")
        student_dict[student.student_id]['unlearnedWordList'] = item_dict.get("unlearnedWordList")
        student_dict[student.student_id]['unlearnedLetterList'] = item_dict.get("unlearnedLetterList")
        student_dict[student.student_id]['unlearnedSoundList'] = item_dict.get("unlearnedSoundList")
        student_dict[student.student_id]['wordCount'] = item_dict.get("wordCount")
        student_dict[student.student_id]['letterCount'] = item_dict.get("letterCount")
        student_dict[student.student_id]['soundCount'] = item_dict.get("soundCount")
        student_dict[student.student_id]['unlearnedWordCount'] = item_dict.get("unlearnedWordCount")
        student_dict[student.student_id]['unlearnedLetterCount'] = item_dict.get("unlearnedLetterCount")
        student_dict[student.student_id]['unlearnedSoundCount'] = item_dict.get("unlearnedSoundCount")
        student_dict[student.student_id]['totalWordCount'] = item_dict.get("totalWordCount")
        student_dict[student.student_id]['totalLetterCount'] = item_dict.get("totalLetterCount")
        student_dict[student.student_id]['totalSoundCount'] = item_dict.get("totalSoundCount")
        
    end = time.time()
    elapsed_time = end - start
    print('getting all students took', elapsed_time)

    return jsonify(student_dict)

def get_class_averages(user_id):
    studentitems = StudentItem.query.filter_by(user_id=user_id).filter(StudentItem.Learned.is_(True)).all()
    averages = {}
    for student in studentitems:
        if not averages.get(student.student_id): 
            averages[student.student_id] = {}
        if student.item_type == "words":
            if averages[student.student_id].get("words"):
                averages[student.student_id]["words"].append(student.item_id)
            else:
                averages[student.student_id]["words"] = [student.item_id]

        if student.item_type == "letters":
            if averages[student.student_id].get("letters"):
                averages[student.student_id]["letters"].append(student.item_id)
            else:
                averages[student.student_id]["letters"] = [student.item_id]

        if student.item_type == "sounds":
            if averages[student.student_id].get("sounds"):
                averages[student.student_id]["sounds"].append(student.item_id)
            else:
                averages[student.student_id]["sounds"] = [student.item_id]
        
    averages = averages.values()
    word_list = []
    letter_list = []
    sound_list = []
    for entry in averages:
        if entry.get("words") == None:
            word_list.append([])
        else:
            word_list.append(entry.get("words"))
        if entry.get("letters") == None:
            letter_list.append([])
        else:
            letter_list.append(entry.get("letters"))
        if entry.get("sounds") == None:
            sound_list.append([])
        else:
            sound_list.append(entry.get("sounds"))

    class_averages = {"wordLists": word_list, "letterLists": letter_list, "soundLists": sound_list}
    return class_averages

def get_all_student_reading_levels(student):
        if student.readinglevels == []: 
            reading_level = ""
            last_reading_level_update = ""
        else:
            reading_level = student.readinglevels[0].reading_level
            last_reading_level_update = student.readinglevels[0].update_date
        return [reading_level, last_reading_level_update]
        
def get_student_group(student, user_id):
    if student.studentgroups == []: 
        group_name = ""
    else:
        group = Group.query.filter_by(user_id=user_id, group_id=student.studentgroups[0].group_id).first()
        group_name = group.group_name
    return group_name

def get_student_test_dates(student):
    test_dict = {
        'lastWordTest': "",
        'lastLetterTest': "",
        'lastSoundTest': "",
        }

    for test in student.studenttestresults:
        if test.test_type == "words":
            if test_dict['lastWordTest'] == "":
                test_dict['lastWordTest'] = test.test_date
            else:
                pass
        elif test.test_type == "letters":
            if test_dict['lastLetterTest'] == "":
                test_dict['lastLetterTest'] = test.test_date
            else:
                pass
        elif test.test_type == "sounds":
            if test_dict['lastSoundTest'] == "":
                test_dict['lastSoundTest'] = test.test_date
            else:
                pass
  
    return test_dict

def get_student_item_dict(items):
    item_dict = {
        'wordList': [],
        'letterList':[],
        'soundList':[],
        'unlearnedWordList': [],
        'unlearnedLetterList': [],
        'unlearnedSoundList': [],
        'wordCount': 0,
        'letterCount': 0,
        'soundCount': 0,
        'unlearnedWordCount': 0,
        'unlearnedLetterCount': 0,
        'unlearnedSoundCount': 0,
        'totalWordCount': 0,
        'totalLetterCount': 0,
        'totalSoundCount': 0,

        }
    for item in items:
        if item.item_type == 'words':
            if item.Learned:
          
                item_dict['wordList'].append(item.items.item)
                item_dict['wordCount'] += 1
            else:
                item_dict['unlearnedWordList'].append(item.items.item)
                item_dict['unlearnedWordCount'] +=1
            item_dict['totalWordCount'] += 1
        if item.item_type == 'letters':
            if item.Learned:
                item_dict['letterList'].append(item.items.item)
                item_dict['letterCount'] += 1
            else:
                item_dict['unlearnedLetterList'].append(item.items.item)
                item_dict['unlearnedLetterCount'] +=1
            item_dict['totalLetterCount'] += 1
        if item.item_type == 'sounds':
            if item.Learned:
                item_dict['soundList'].append(item.items.item)
                item_dict['soundCount'] += 1
            else:
                item_dict['unlearnedSoundList'].append(item.items.item)
                item_dict['unlearnedSoundCount'] +=1
            item_dict['totalSoundCount'] += 1

    return item_dict
    


# @bp.route("/details/<student_id>")
@bp.route("/students/<student_id>")
@token_required
def student_detail(current_user, student_id):
    """Show student detail"""
    start = time.time()
    user_id = current_user.public_id
    averages = get_class_averages(user_id)
    student_items = Item.query.filter(Item.custom.is_(False)).all()
    student = Student.query.filter_by(
        student_id=student_id, user_id=user_id).options(db.joinedload('studentgroups')).options(db.joinedload('readinglevels')).all()
    student_items = StudentItem.query.filter_by(
        student_id=student_id).options(db.joinedload('items')).all()
    student_dict = {}

    items = StudentItem.query.filter_by(user_id=user_id, student_id=student_id).options(db.joinedload('items')).all()
    item_dict = get_student_detail_item_dict(items)
    student_dict['classAverages'] = get_class_averages(user_id)
    student_dict['wordList'] = item_dict.get("wordList")
    student_dict['letterList'] = item_dict.get("letterList")
    student_dict['soundList'] = item_dict.get("soundList")
    student_dict['unlearnedWordList'] = item_dict.get("unlearnedWordList")
    student_dict['unlearnedLetterList'] = item_dict.get("unlearnedLetterList")
    student_dict['unlearnedSoundList'] = item_dict.get("unlearnedSoundList")
    student_dict['wordCount'] = item_dict.get("wordCount")
    student_dict['letterCount'] = item_dict.get("letterCount")
    student_dict['soundCount'] = item_dict.get("soundCount")
    student_dict['unlearnedWordCount'] = item_dict.get("unlearnedWordCount")
    student_dict['unlearnedLetterCount'] = item_dict.get("unlearnedLetterCount")
    student_dict['unlearnedSoundCount'] = item_dict.get("unlearnedSoundCount")
    student_dict['totalWordCount'] = item_dict.get("totalWordCount")
    student_dict['totalLetterCount'] = item_dict.get("totalLetterCount")
    student_dict['totalSoundCount'] = item_dict.get("totalSoundCount")
    student_dict['student_id'] = student[0].student_id,
    student_dict['name'] = student[0].name
    student_dict['readingLevel'] = get_all_student_reading_levels(student[0])[0]
    student_dict['lastReadingUpdate'] = get_all_student_reading_levels(student[0])[1]
    student_dict['group'] = get_student_group(student[0], user_id)
    end = time.time()
    elapsed_time = end - start
    print('getting student detail took', elapsed_time)
    return jsonify(student_dict)

def get_student_detail_item_dict(items):
    item_dict = {
        'wordList': [],
        'letterList':[],
        'soundList':[],
        'unlearnedWordList': [],
        'unlearnedLetterList': [],
        'unlearnedSoundList': [],
        'wordCount': 0,
        'letterCount': 0,
        'soundCount': 0,
        'unlearnedWordCount': 0,
        'unlearnedLetterCount': 0,
        'unlearnedSoundCount': 0,
        'totalWordCount': 0,
        'totalLetterCount': 0,
        'totalSoundCount': 0,
        
        }
    for item in items:
        if item.item_type == 'words':
            if item.Learned:
          
                item_dict['wordList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['wordCount'] += 1
            else:
                item_dict['unlearnedWordList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['unlearnedWordCount'] +=1
            item_dict['totalWordCount'] += 1
        if item.item_type == 'letters':
            if item.Learned:
                item_dict['letterList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['letterCount'] += 1
            else:
                item_dict['unlearnedLetterList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['unlearnedLetterCount'] +=1
            item_dict['totalLetterCount'] += 1
        if item.item_type == 'sounds':
            if item.Learned:
                item_dict['soundList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['soundCount'] += 1
            else:
                item_dict['unlearnedSoundList'].append({'item_id': item.items.item_id, 'item': item.items.item})
                item_dict['unlearnedSoundCount'] +=1
            item_dict['totalSoundCount'] += 1

    return item_dict
    
@bp.route("/create-student-test", methods=["POST"])
@token_required
def create_student_test(current_user):
    """creates new student  test row in db, calls update_correct_items
    and update_incorrect_items functions"""
    data = request.get_json()
    student_test = data.get('studentTest')
    test_type = data.get('testType')
    student_id = data.get('studentId')[0]
    user_id = current_user.public_id
    correct_items = []
    incorrect_items = []

    for entry in student_test:

        if entry['answeredCorrectly']:
            correct_items.append(entry.get('testItems'))
        if entry['answeredCorrectly'] == False:
            incorrect_items.append(entry.get('testItems'))
    update_correct_items(student_id, correct_items, test_type, user_id)
    update_incorrect_items(student_id, incorrect_items, test_type, user_id)
    score = calculate_score(correct_items, incorrect_items)
    db.session.add(StudentTestResult(student_id=student_id, user_id=user_id, score=score,
    correct_items=correct_items, incorrect_items=incorrect_items, test_type=test_type))
    db.session.commit()
    return jsonify({'response': 'student test added!'})

def update_correct_items(student_id, correct_items, test_type, user_id):
    """updates correct items in db, called by create_student_test"""
    student_item_list = StudentItem.query.filter_by(student_id=student_id, user_id=user_id, item_type=test_type).options(db.joinedload('items')).filter(
    Item.item.in_(correct_items)).all()
    for item in student_item_list:
        if item.items.item in correct_items:
            item.Learned = True
            item.correct_count = StudentItem.correct_count + 1
            db.session.commit()
    return "correct items"

def update_incorrect_items(student_id, incorrect_items, test_type, user_id):
    """updates incorrect letters in db, called by create_student_test"""
    student_item_list = StudentItem.query.filter_by(student_id=student_id, user_id=user_id, item_type=test_type).options(db.joinedload('items')).filter(
    Item.item.in_(incorrect_items)).all()
    for item in student_item_list:
        if item.items.item in incorrect_items:
            item.incorrect_count = StudentItem.incorrect_count + 1
            db.session.commit()
    return "incorrect items"

def calculate_score(known_items, unknown_items):
    """calculates student test score, called by create_student_test"""
    score = len(known_items) / (len(known_items) + len(unknown_items))
    score = score * 100
    score = int(round(score))
    return score


@bp.route("/get-test-dates")
@token_required
def get_test_dates(current_user, student, test_type):
    user_id = current_user.public_id
    student_id = student 
    test_type = test_type
    test_dates = StudentTestResult.query.filter_by(user_id=user_id, student_id=student_id, test_type=test_type).all()
    if test_dates != []:
        most_recent = test_dates[-1].test_date
        most_recent = most_recent
    else:
        most_recent = ""
    return most_recent


@bp.route("/get-student-item-test/<item_type>/<student>")
@token_required
def get_student_item_test(current_user, item_type, student):
    """get list of student test results, word_counts and chart_data"""

    user_id = current_user.public_id
    student_id = student
    student_items = StudentItem.query.filter_by(
        user_id=user_id, student_id=student_id, item_type=item_type).options(db.joinedload('items')).options(db.joinedload('students')).all()
    student_tests = StudentTestResult.query.filter_by(
        student_id=student_id, user_id=user_id, test_type=item_type).all()
    item_counts = get_item_counts(student_items)
    student_test_list = get_student_item_test_list(student_tests)
    learned_items_list = get_learned_items_list(student_items)
    item_counts = get_item_counts(student_items)
    test_data = {'itemCounts': item_counts, 'studentTestList':student_test_list, 'learnedItemList': learned_items_list
    }
    print("test data", test_data)
    return test_data


@bp.route("/get-all-student-tests/<student_id>")
@token_required
def get_all_student_tests(current_user,  student_id):
    """get list of student test results, word_counts and chart_data"""
    user_id = current_user.public_id
    student_tests = StudentTestResult.query.filter_by(
        student_id=student_id, user_id=user_id).all()
    test_data = {}
    word_test_list = []
    letter_test_list = []
    sound_test_list = []

    for test in student_tests:
        test_date = test.test_date
        student_test_object = {
            'studentId': test.student_id,
            'score': test.score,
            'testDate': test.test_date,
            'correctItems': test.correct_items,
            'incorrectItems': test.incorrect_items,
            'testType': test.test_type
        }
        if test.test_type == "words":
            word_test_list.append(student_test_object)
            test_data['words'] = get_student_item_test("words", test.student_id)
        elif test.test_type == "letters":
             letter_test_list.append(student_test_object)
             test_data['letters'] = get_student_item_test("letters", test.student_id)
        elif test.test_type == "sounds":
             sound_test_list.append(student_test_object)
             test_data['sounds'] = get_student_item_test("sounds", test.student_id)
    if word_test_list != []:
        word_test_list = word_test_list[-1]
    if letter_test_list != []:
        letter_test_list = letter_test_list[-1]
    if sound_test_list != []:
        sound_test_list = sound_test_list[-1]

    test_object = {
        "testData": test_data,
        "wordTest":word_test_list,
        "letterTest": letter_test_list,
        "soundTest": sound_test_list,
    }
    return jsonify(test_object)

def get_item_counts(student_items):
    """is called by get student test, returns item, times read correctly,times read incorrectly """
    item_counts = []
    for student_item in student_items:
        count = {
            "item": student_item.items.item,
            "correctCount": student_item.correct_count,
            "incorrectCount": student_item.incorrect_count
        }
        item_counts.append(count)

    return item_counts

def get_learned_items_list(student_items):
    """is called by get student test, returns list of learned items"""
    learned_items = []
    for student_item in student_items:
        if student_item.Learned == True:
            learned_items.append(student_item.items.item)
    return learned_items


def get_student_item_test_list(student_test):
    """is called by get_student_item_test, returns list of student tests"""
    student_test_list = []
    for student in student_test:
        test_date = student.test_date
        student_test_object = {
            'studentId': student.student_id,
            'score': student.score,
            'testDate': test_date,
            'correctItems': student.correct_items,
            'incorrectItems': student.incorrect_items
        }
        student_test_list.append(student_test_object)
    print("student_test_list", student_test_list)
    return student_test_list

@bp.route("/mark-items-learned", methods=["POST"])
@token_required
def mark_items_learned(current_user):
    data = request.get_json()
    student_id = data.get('studentId')[0]
    item = data.get('item')
    item = item['item_id']
    user_id = current_user.public_id
    student_item = StudentItem.query.filter_by(user_id=user_id, student_id=student_id, item_id=item).first()
    student_item.Learned = True
    db.session.commit()
    return jsonify(student_id)

@bp.route("/mark-items-unlearned", methods=["POST"])
@token_required
def mark_items_unlearned(current_user):
    data = request.get_json()
    student_id = data.get('studentId')[0]
    item = data.get('item')
    item = item['item_id']
    user_id = current_user.public_id
    student_item = StudentItem.query.filter_by(user_id=user_id, student_id=student_id, item_id=item).first()
    student_item.Learned = False
    db.session.commit()
    return jsonify(student_id)



@bp.route("/assign-group", methods=["POST"])
@token_required
def make_student_groups(current_user):
    user_id = current_user.public_id
    data = request.get_json()
    students = data.get('students')
    group_name = data.get('groupName')
    group = Group.query.filter_by(group_name=group_name, user_id=user_id).first()
    existing_student_ids =[]
    student_list = Student.query.filter(Student.name.in_(students)).filter(Student.user_id == user_id).all()

    student_ids = [student.student_id for student in student_list]
    list_to_add = list(set(student_ids).difference(existing_student_ids))
    remove_from_previous_group(list_to_add, user_id)
    db.session.bulk_save_objects(
        [
            StudentGroup(
                student_id=student,
                group_id=group.group_id,
                user_id=user_id
              
            )
            for student in list_to_add
        ]
    )    
    db.session.commit()
    return jsonify(data)

    
def remove_from_previous_group(student_list, user_id):
    students = StudentGroup.query.filter_by(user_id=user_id).filter(StudentGroup.student_id.in_(student_list)).all()
    for student in students:
        db.session.delete(student)
        db.session.commit()
    return "cool"


@bp.route("/add-group", methods=['POST'])
@token_required
def add_group(current_user):
    group_name = request.get_json()
    user_id = current_user.public_id
    existing_group = Group.query.filter_by(user_id=user_id, group_name=group_name).first()
    if existing_group:
        return jsonify({"error": "group already exists"})
    elif not existing_group: 
        if group_name != " " and group_name !="":
            table = str.maketrans({key: None for key in string.punctuation})
            group_name = group_name.translate(table) 
            new_group = Group(user_id=user_id, group_name=group_name)
            db.session.add(new_group)
            db.session.commit()
            return jsonify(group_name)
        else:
            return jsonify({"error": "no group name"})
 


@bp.route("/all-groups")
@token_required
def get_all_groups(current_user):
    user_id = current_user.public_id
    groups = Group.query.filter_by(user_id=user_id).all()
    group_dict = {}
    for group in groups:
        group_dict[group.group_id] = {'name': group.group_name, 'students': []}
    student_groups = StudentGroup.query.filter_by(user_id=user_id).options(db.joinedload('groups')).options(db.joinedload('students')).all()

    for entry in student_groups:
        if entry.groups.group_id in group_dict:
            group_dict[entry.groups.group_id]['students'].append(entry.students.name)
        

    return jsonify(group_dict)


@bp.route("/students/names")
@token_required
def get_all_students(current_user):
    start = time.time()
    user_id = current_user.public_id
    students = Student.query.filter_by(user_id=user_id).all()
    student_list = []
    for student in students:
        student_to_add = {
            'name': student.name,
            'studentId': student.student_id
        }
        student_list.append(student_to_add)

    end = time.time()
    elapsed_time = end - start
    print('getting student list took', elapsed_time)
    return jsonify(student_list)

@bp.route("/delete-group", methods=['POST'])
@token_required
def delete_group(current_user):
    group_name = request.get_json()
    user_id = current_user.public_id
    group = Group.query.filter_by(
        group_name=group_name, user_id=user_id).first()
    db.session.delete(group)
    db.session.commit()
    return "group deleted"

@bp.route("/group-detail/<group>")
@token_required
def group_detail(current_user, group):
    """Display group and students in that group"""
    user_id = current_user.public_id
    group_object = Group.query.filter_by(group_name=group, user_id=user_id).first()
    group_id = group_object.group_id
    group_notes = GroupNote.query.filter_by(group_id=group_id, user_id=user_id).all()
    notes = [note.note for note in group_notes]
    student_group = StudentGroup.query.filter_by(
        group_id=group_id, user_id=user_id).options(db.joinedload('students')).all()
    group_notes = GroupNote.query.filter_by(group_id=group_id, user_id=user_id).all()
    notes = [{'note': note.note, 'date': note.date_added} for note in group_notes]

    if student_group: 
        student_names = []
        student_ids =[]
        for student in student_group:
            student_names.append(student.students.name)
            student_ids.append(student.student_id)
            
        common_words = None
        all_words = set()
        common_letters = None
        all_letters = set()
        common_sounds = None
        all_sounds = set()
        reading_levels ={}
        for student in student_ids:
            student_reading_level = ReadingLevel.query.filter_by(user_id=user_id, student_id=student).options(db.joinedload('students')).first()
            if student_reading_level:
                reading_levels[student_reading_level.students.name] = student_reading_level.reading_level
            student_words = StudentItem.query.filter(StudentItem.Learned.is_(False)).filter_by(user_id=user_id, student_id=student, item_type="words").options(db.joinedload('students')).options(db.joinedload('items')).all()

            student_list = []
            for word in student_words:
                student_list.append(word.items.item)
            student_set = set(student_list)
            all_words = all_words | student_set
            common_words = common_words & student_set if common_words else student_set

            student_letters = StudentItem.query.filter(StudentItem.Learned.is_(False)).filter_by(user_id=user_id, student_id=student, item_type="letters").options(db.joinedload('students')).options(db.joinedload('items')).all()
            student_list = []
            for letter in student_letters:
                student_list.append(letter.items.item)
            student_set = set(student_list)
            all_letters = all_letters | student_set
            common_letters = common_letters & student_set if common_letters else student_set

            student_sounds = StudentItem.query.filter(StudentItem.Learned.is_(False)).filter_by(user_id=user_id, student_id=student, item_type="sounds").options(db.joinedload('students')).options(db.joinedload('items')).all()
            student_list = []
            for sound in student_sounds:
                student_list.append(sound.items.item)
            student_set = set(student_list)
            all_sounds = all_sounds | student_set
            common_sounds = common_sounds & student_set if common_sounds else student_set
        
        
        group_data = {
            'name': group,
            'students': student_names,
            'words' : list(common_words),
            'letters': list(common_letters),
            'sounds': list(common_sounds),
            'readingLevels': reading_levels,
            'notes': notes
        }
        return jsonify(group_data)
    else:
        return jsonify({"message":"no students yet"})

@bp.route("/add-note", methods=['POST'])
@token_required
def add_note(current_user):
    data = request.get_json()
    group_name = data.get('group')
    note = data.get('note')
    user_id = current_user.public_id
    group = Group.query.filter_by(user_id=user_id, group_name=group_name).first()
    group_id = group.group_id
    if note != " " and note !="":
        table = str.maketrans({key: None for key in string.punctuation})
        note = note.translate(table) 
        new_note = GroupNote(user_id=user_id, group_id=group_id, note=note)
        db.session.add(new_note)
        db.session.commit()
        return jsonify(note)
    else:
        return jsonify({"error": "no note"})

@bp.route("/delete-note", methods=['POST'])
@token_required
def delete_note(current_user):
    note = request.get_json()
    user_id = current_user.public_id
    note = GroupNote.query.filter_by(
        note=note, user_id=user_id).first()
    db.session.delete(note)
    db.session.commit()
    return "deleted"

