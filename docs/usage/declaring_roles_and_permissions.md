# Declaring roles and permissions

## Creating yml file

Respo provides complete and easy way of declaring roles and permissions.

The whole idea is to have all of them in single `yml` file that will be source of truth for the app. (later, we will convert it to pickle format after validation).

For this tutorial, we will work on file `respo_model.yml` that will be used in next sections.

## Content of respo_model.yml

```yml
{!./examples/usage/general_perms.yml!}

{!./examples/usage/general_principles.yml!}

{!./examples/usage/general_roles.yml!}
```

## Permissions

```yml
{!./examples/usage/general_perms.yml!}
```

!!! note

    To avoid issues, every permission must be two lowercase asci alphanumeric strings (at least length of 1), separated by a dot. Full regex is `^[a-z_0-9]{1,}\.[a-z_0-9]{1,}$`

First we need to define **unique** permissions for resources. This could be anything, but suggested convention is "user.read" or "book.list" etc. where first part is named _collection_ or _group_ (many permissions can share the same _collection_) and the second is specific name in this _collection_. The more self-describing names, the better.

Every API endpoint _CAN_ require one or more permissions, ideally the name of endpoint should be similar to required permission (if only one permission will be required).

## Principles

```yml
{!./examples/usage/general_principles.yml!}
```

!!! note

    This section is not obligatory in yml file. If you don't need stronger permissions, just skip it

Permissions may also contain other permissions. For example, in our API `read.read_all` is more powerful than `read.read_basic` so we can write:

```yml
principles:
  - when: read.read_all
    then: [read.read_basic]
```

Consider two endpoints:

- POST /read/read_all
- POST /read/read_basic

Someone with a permission to read every information: `read.read_all` (whatever it is), logically should also be able to read basic informations. By decalring it here in principles part, you can avoid if statements here and there in the app.

## Roles

```yml
{!./examples/usage/general_roles.yml!}
```

!!! note

    Every role name must be a lowercase asci alphanumeric string (at least length of 1). Full regex is `^[a-z_0-9]{1,}$`

The last part of file is a list of roles. Every role has **unique** name, list of permission (that this role has, defined in _permissions_ section) and optionally attribute `include` (list of other role names defined in this section), so role can **extend** other roles.

<br>
<br>
<br>
