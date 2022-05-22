# FastAPI + SQLAlchemy dependency user_have_permission

## Declare user_have_permission dependency for validating permissions

In this topic we will use at first fake database and very modest example of user_have_permission dependency for FastAPI, then write full example, that covers SQLAlchemy integration and more realistic flows.

```python
{!./examples/usage/user_have_permission_I.py!}

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
{
  "name": "Peter"
}
```

when Peter is choosed and sometimes 403:

```json
{
  "detail": "Forbidden"
}
```

when Sara that has no permission.

## Declare user_have_permission dependency with SQLAlchemy user table

```python
{!./examples/usage/user_have_permission_II.py!}

```

## Using SQLAlchemy RespoField

In SQLAlchemy user model we use custom field powered by respo: `SQLAlchemyRespoField`.
It is responsible for serialization and deserialization from `respo.RespoClient` to string in database back and forth. So we write:

```python
respo_field: RespoClient = field(
    default_factory=RespoClient,
    metadata={
        "sa": Column(SQLAlchemyRespoField, nullable=False, server_default="")
    },
)
# or without extra typing support
respo_field = Column(SQLAlchemyRespoField, nullable=False, server_default="")
```

!!! note

    Note, this RespoClient-like field is mutable, so any direct changes to attributes won't trigger SQLAlchemy machinery and changes won't be saved to database. The only methods that trigger so called **has_changed()** event are `add_role` and `remove_role`!

## Scaling

After above setup scaling is very easy using the same dependency factory for any new endpoint (with different permission). For example we can continue with:

```python
@app.get("/buy-book")
def buy_books(
    user=Depends(user_have_permission(RESPO_MODEL.PERMS.BOOK__BUY)),
):
    return None


@app.get("/sell-book")
def sell_books(
    user=Depends(user_have_permission(RESPO_MODEL.PERMS.BOOK__SELL)),
):
    return None

```

## Recap

In this section, we do basicaly two things:

- create field `respo_field` based on custom field `SQLAlchemyRespoField` in our User model in database, so we can store user's roles in database
- create `user_have_permission` dependency factory that is resposible for **additional** checking if user has permission to requested resource. Note, it may differ in certain scenarios and use cases, but basically user should have access either when is **owner/creator** of resource whatever that means, or has role that allow it.

<br>
<br>
<br>
