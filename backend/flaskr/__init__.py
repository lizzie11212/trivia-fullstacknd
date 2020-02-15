import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__)
  setup_db(app)
  #Set up CORS. Allow '*' for origins.
  CORS(app, resources={r"/api/*": {"origins": "*"}})

  #Use the after_request decorator to set Access-Control-Allow
  @app.after_request
  def after_request(response):
      response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
      response.headers.add('Access-Control-Allow-Headers', 'GET,POST,PATCH,DELETE,OPTIONS')
      return response

  #Create an endpoint to handle GET requests for all available categories.
  @app.route('/categories', methods=['GET'])
  def all_categories():
      categories = Category.query.all()
      formatted_categories = [category.format() for category in categories]

      return jsonify({
        'success':True,
        'categories': formatted_categories
      })


#Create an endpoint to handle GET requests for questions,including pagination (every 10 questions).
#This endpoint should return a list of questions,number of total questions, current category, categories.
  @app.route('/questions', methods=['GET'])
  def all_questions():
      page = request.args.get('page', 1, type=int)
      start = (page -1)*10
      end = start +10
      questions = Question.query.all()
      formatted_questions = [question.format() for question in questions]
      categories = all_categories().get_json()["categories"]

      return jsonify({
        'success':True,
        'questions': formatted_questions[start:end],
        'total_questions': len(formatted_questions),
        "current_category": None,
        'categories': categories
      })


  #Create an endpoint to DELETE question using a question ID.

  @app.route('/questions/<int:question_id>', methods=["DELETE"])
  def delete_question(question_id):
      question = Question.query.filter(
        Question.id == question_id).one_or_none()
      if question is None:
          abort(404)
      else:
          try:
              question.delete()
          except Exception:
              abort(422)
      return jsonify({'success': True})


#Create an endpoint to POST a new question
  @app.route('/questions', methods=['POST'])
  def add_question():
      data = request.get_json()
      question = Question(
        question = data.get("question"),
        answer = data.get("answer"),
        category=int(body.get("category")),
        difficulty=int(body.get("difficulty"))
      )

      #check if question exists
      existing_question = Question.query.filter_by(question = data.get("question")).first()
      if existing_question:
          return jsonify({
            "message": "Question already exisits."
          }), 200

      #if not exisits, save question to the database_name
      question.insert()
      return jsonify({
        "success": True,
        "question": quetion.format(),
        "message": "Question sucessfully created."
      }), 201

 # Create a POST endpoint to get questions based on a search term.
  @app.route('/questions', methods=['POST'])
  def search():
      search_question_list = []
      search = request.get_json()
      searchTerm = search['searchTerm']
      questions = Question.query.all()
      formatted_questions = [question.format() for question in questions]
      current_questions = formatted_questions[:]
      for item in current_questions:
          if str.lower(searchTerm) in str.lower(item['question']):
              search_question_list.append(item)
          else:
              pass
      return jsonify({'questions': search_question_list,
                      'total_search_questions': len(search_question_list),
                      'current_category': None})

  '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def getByCategory(category_id):
      try:
          questions = getQuestions(category_id).json['questions']
          category = Category.query.get(category_id).type
          return jsonify({'success': True,
                          'questions': questions,
                          'total_questions': len(questions),
                          'current_category': category})
      except Exception:
          abort(404)

  '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
  @app.route('/quizzes', methods=['POST'])
  def play():
      try:
          data = request.get_json()
          previous_questions = data['previous_questions']
          quiz_category = data['quiz_category']
          category = quiz_category['id']
          # return all questions or questions by category
          if quiz_category['type'] == 'click':
              questions = getQuestions().json['questions']
          else:
              questions = getByCategory(category).json['questions']
          # if questions run out force program end
          if len(questions) == len(previous_questions):
              return jsonify({'forceEnd': True})
          else:
              question = random.choice(questions)
          # choose the next random question
          while question['id'] in previous_questions:
              question = random.choice(questions)
          else:
              pass
          return jsonify({'question': question,
                          'guess': data['guess'],
                          'previousQuestions': previous_questions})
      except Exception:
          abort(500)

  #Create error handlers for all expected errors
  @app.errorhandler(400)
  def bad_request(error):
      return jsonify({
          "success": False,
          "error": 400,
          "message": "Bad request"
          }), 400

  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      "success": False,
      "error": 404,
      "message": "Not found."
      }), 404

  @app.errorhandler(405)
  def method_not_allowed(error):
      return jsonify({
          "success": False,
          "error": 405,
          "message": "The method is not allowed for the requested URL."
          }), 405

  @app.errorhandler(422)
  def unprocessable_request(error):
    return jsonify({
      "success": False,
      "error": 422,
      "message": "Unable to process request."
      }), 422

  @app.errorhandler(500)
  def server_error(error):
    return jsonify({
      "success": False,
      "error": 500,
      "message": "Server error."
      }), 500

  return app
