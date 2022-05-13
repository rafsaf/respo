# FastAPI dependency user_have_permission

## Declare user_have_permission dependency for validating permissions

In this topic we will use fake database and very modest example of user_have_permission dependency for FastAPI, the next ones covers SQLAlchemy integration and more realistic flows.

```python
{!./examples/usage/respo_model_in_fastapi.py!}

```

## Run FastAPI app

Put above code in `main.py` and run

```
uvicorn main:app --reload
```

At the address `localhost:8000/docs` you can test the endpoint.

Click on **Execute** few times in a row to see expected result.

## Expected result

Now, in `user_have_permission` dependency we check using RESPO_MODEL declared in previous chapters if a user have specific permission (or with more precision if a user have at least one role that includes this permission). Since we have only 2 users and we get them by random choice from list, sometimes we get 200 with

```json
[
  {
    "name": "Peter",
    "respo_field": {
      "roles": ["admin"]
    }
  },
  {
    "name": "Sara",
    "respo_field": {
      "roles": []
    }
  }
]
```

and sometimes 403:

```json
{
  "detail": "Forbidden"
}
```

In next section we will get through using real database and SQLAlchemy ORM.
