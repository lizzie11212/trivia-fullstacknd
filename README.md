# Full Stack API Final Project

## Full Stack Trivia

The application will:

1) Display questions - both all questions and by category. Questions should show the question, category and difficulty rating by default and can show/hide the answer.
2) Delete questions.
3) Add questions and require that they include question and answer text.
4) Search for questions based on a text query string.
5) Play the quiz game, randomizing either all questions or within a specific category.

Base URL: At present this app can only be run locally and is not hosted as a base URL.
The backend app is hosted at the default, http://127.0.0.1:5000, which is set as a proxy in the frontend configuration.

## Error Handling:
Errors are returned as JSON objects in the following format:
{
  "success": False,
  "error":400,
  "message": "bad request"
}

## The API will return several error types when requests fail:
400: "Bad request"
404: "Resource not found."
405: "The method is not allowed for the requested URL."
422: "Unable to process request."
500: "Server error."
