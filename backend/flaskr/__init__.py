import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
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
  #Create an endpoint to show question using a question ID
  @app.route('/questions/<int:question_id>')
  def retrieve_question(question_id):
      question = Question.query.filter(
        Question.id == question_id).one_or_none()
      if question is None:
          abort(404)
      else:
          return jsonify({
            'success':True,
            'question':question.format()
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
  def create_question():
        body = request.get_json(request)
        new_question = body.get('question')
        new_answer = body.get('answer')
        new_category = body.get('category')
        new_difficulty = body.get('difficulty')
        if (new_question == '' or new_answer == '' or
            new_category == '' or
                new_difficulty == ''):
            abort(400)
        try:
            question = Question(question=new_question, answer=new_answer,
                                category=new_category,
                                difficulty=new_difficulty)
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })
        except Exception:
            abort(422)

 # Create a POST endpoint to get questions based on a search term.
  @app.route('/questions', methods=['POST'])
  def search_questions():
        body = request.get_json()
        search_term = body.get('searchTerm', None)
        try:
            questions_results = Question.query.order_by(Question.id).filter(
                Question.question.ilike('%{}%'.format(search_term))).all()
            search_questions = [question.format()
                                for question in questions_results]
            return jsonify({
                'success': True,
                'questions': search_questions,
                'total_questions': len(questions_results),
                'current_category': None
            })
        except Exception:
            abort(422)

  #Create an endpoint to show category using a category ID
  @app.route('/categories/<int:category_id>')
  def retrieve_category(category_id):
      category = Category.query.filter(
        Category.id == category_id).one_or_none()
      if category is None:
          abort(404)
      else:
        return jsonify({
          'success':True,
          'category':category.format()
        })

  #Create a GET endpoint to get questions based on category.
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def getByCategory(category_id):
       page = request.args.get('page', 1, type=int)
       start = (page -1)*10
       end = start +10
       questions = Question.query.filter(Question.category == category_id).all()
       formatted_questions = [question.format() for question in questions]
       if formatted_questions is None:
           abort(404)
       else:
           return jsonify({
             'success':True,
             'questions': formatted_questions[start:end],
             'total_questions': len(formatted_questions),
             'current_category': category_id
             })

  #Create a POST endpoint to get questions to play the quiz.
  @app.route('/quizzes', methods=['POST'])
  def get_quiz():
      body = request.get_json()
      previous_questions = body.get('previous_questions', None)
      quizCategory = body.get('quiz_category', None)

      if quizCategory['id'] == 0:
          questions = Question.query.order_by(Question.id).all()
      else:
          questions = Question.query.order_by(Question.id).filter(
              Question.category == quizCategory['id']).all()

          formatted_questions = [question.format() for question in questions]
      # exclude previous questions
      unasked_questions = []
      for question in formatted_questions:
          if question['id'] not in previous_questions:
              unasked_questions.append(question)

      next_question = None
      if len(unasked_questions) > 0:
          next_question = unasked_questions[0]

      return jsonify({
          'success': True,
          'question': next_question
      })

      if len(get_questions) == 0:
          return jsonify(None)
      else:
          questions = list(map(Question.format, get_questions))
          question = random.choice(questions)
          return jsonify(question)


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
      "message": "Resource not found."
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
