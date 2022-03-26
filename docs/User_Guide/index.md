# Declaring roles and permissions

## Creating yml file

Respo provides complete and easy way of declaring roles and permissions.

The whole idea is to have all of them in single `yml` file that will be source of truth for the app. (later, we will convert it to pickle format after validation).

For this tutorial, we will work on file `respo_model.yml` that will be used in next sections.

## Content of respo_model.yml

```yml
{!./examples/user_guide/index/general_perms.yml!}

{!./examples/user_guide/index/general_principles.yml!}

{!./examples/user_guide/index/general_roles.yml!}
```

## Permissions

```yml
{!./examples/user_guide/index/general_perms.yml!}
```

!!! note

    To avoid issues, every permission must be two lowercase asci alphanumeric strings (at least length of 1), separated by a dot. Full regex is `^[a-z_0-9]{1,}\.[a-z_0-9]{1,}$`

First we need to define permissions for resources. This could be anything but suggested convention is "user.read" or "book.list" etc. where first part is named _collection_ or _group_ (many permissions can share the same _collection_) and the second is specific name in this _collection_. The more self-describing names, the better.

Every API endpoint _CAN_ require one or more permissions, ideally the name of endpoint should be similar to required permission (if only one permission will be required).

## Principles

```yml
{!./examples/user_guide/index/general_principles.yml!}
```

!!! note

    This section is not obligatory in yml file. If you don't need stronger permissions, just skip it

Permissions may also contain other permissions. For example `items.update` is traditionaly more powerful than `items.read` so we can write

```yml
principles:
  - when: items.update
    then: [items.read]
```

Consider two endpoints:

- POST /items/update
- POST /items/read

Someone with a permission to update every `item` (whatever it is), logically should also be able to read it.
