![CI](https://github.com/hoverj/finance-tracker-api/actions/workflows/ci.yml/badge.svg)
# finance-tracker-api

# Project Overview
A RESTful API for tracking income and spending expenses.
Built to demonstrate backend development skills including schema design, JWT authentication, and comprehensive test coverage.

# Tech Stack
- **Language:** Python 3.11
- **Framework:** Django + Django Rest Framework
- **Database:** PostgreSQL
- **Authentication:** JWT via djangorestframework-simplejwt
- **Testing:** pytest and pytest-django
- **Infrastructure:** Docker, Docker Compose
- **CI:** GitHub Actions

# Design Decisions
**Category on Transaction Model**
Instead of linking a transaction directly a user, they are linked indirectly through category ownership. This ensures that each transaction
implicitly checks for a category requirment. This also allows for a single validation check - ensuring on creation that category owner is equal transaction request creation owner and no possible data mutiliation where transaction user attribute does not equal the category ownership.

**Amount Validation**
Ensuring that expense amounts are negative and income amounts are positive allow for much easier, cleaner, and readable code for amount calculation.
With this validation in place, when calculating a user's gross total, there is no need to check the category type on whether to add or subtract.
Plus then there is no confusion of some expense values being negative and some being positive based on how the user types it in. This is a clear
all expenses are negative, all incomes are positive.

**Folder Structure**
Every model has its own folder of - models.py, views.py, serializers.py, and urls.py - which is a strategy based on separation of concerns
and allows for ease of extenability of additional models. Each model folder is responsible its own logic.

This same principle also applies to the testing folder structure. There is a folder for the models, views, and serializers. Each with their own
individual testing file based on the model it aims to test.

# How To Run Locally
1. Clone the repo locally
2. Create a .env file and use .env.template to define the necessary environment variables.
3. Run `docker compose up --build` and let it build
4. Run `docker compose exec web python manage.py migrate`
5. Once successfully built, the API should locally be live on localhost:8000
6. Next run the command `docker compose exec web python manage.py createsuperuser` to create a user with admin credentials and be
   able to use as a user in the next step.
7. In order to interact with it easily, a software like Postman should be installed to easily make API requests

# API Endpoints
** After a listed attribute either (R) for required or (O) for optional will be defined
** Unless otherwise noted JWT authentication is needed for any given API request
## Authentication
   - This API utilizes the JWT authentication the following api can be called with valid username/password credentials 
   - /auth/token/
   - /auth/token/refresh/  

## Category
### /categories/
   - Used for POST and batch GET requests
   - Attributes
     - name (R)
     - category_type (R) : either "income" or "expense"
     - color (O) : defaults to #000000 if not provided 
### /categories/{id}/
   - Used for Update, single gets, or deletes

## Transaction
### /transactions/
   - Used for POST and batch GET requests
   - Attributes
     - category (R) : id of the category
     - amount (R)
     - date (O) : defaults to today if not provided
     - description (O) : is left blank if not provided
### /transactions/{id}/
   - Used for Update, single gets, or deletes

# Testing
Pytest will be used for testing practices
Tests for the Category and Transaction models, serializers, and views were written after they were created. Going forward TDD practices will be followed - tests are written before implementation to ensure code correctness and catch regressions early.

The testing suite currently includes 52 tests spread across the views, serializers, and models of the two models: Category and Transactions.
End to end testing was utilized to test expected behavior in successful and unsuccessful outcomes. 

# Future Improvements
1. Implement an ability for a recurring transaction
   1. Set on the 1st and 16th of each month add a new transaction under the income of Salary.
   2. On the 1st of each month create a new transaction under the expense for a subscription service the user pays for